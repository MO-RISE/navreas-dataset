import os
import sys
import json
import base64
import logging
import warnings
import argparse
from copy import deepcopy
from typing import List
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import requests
import seaborn as sns
from tqdm import tqdm
from dotenv import load_dotenv
import matplotlib.pyplot as plt

from deepeval.metrics.hallucination_metric import HallucinationMetric
from deepeval.scorer import Scorer
from deepeval.test_case import LLMTestCase

load_dotenv()


def check_prompt(prompt):
    assert isinstance(prompt, list)
    assert len(prompt) == 2
    assert "role" in prompt[0]
    assert "content" in prompt[0]
    assert prompt[0]["role"] == "system"
    assert "role" in prompt[1]
    assert "content" in prompt[1]
    assert prompt[1]["role"] == "user"


def include_image_in_prompt(prompt, image_path):
    with open(image_path, "rb") as image:
        image_b64_encoded = base64.b64encode(image.read())

    user_messages = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64_encoded.decode()}"}},
        {"type": "text", "text": prompt[1]["content"]},
    ]
    prompt[1]["content"] = user_messages

    return prompt

def prepare_prompts(questions, llm):
    prompts = []
    answers = []
    for question in questions:
        prompt = question["prompt"]
        if llm in args.use_images and (image_path := question.get("image", False)):
            prompt = include_image_in_prompt(prompt, image_path)

        if args.alt_system_prompt is not None:
             prompt[0]['content'] = args.alt_system_prompt

        prompts.append(prompt)
        answers.append(question["answers"])

    return prompts, answers

def prompt_llm(prompt, llm_model, temperature, seed):
    check_prompt(prompt)
    response: requests.Response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        },
        data=json.dumps(
            {
                "model": llm_model,
                "messages": prompt,
                "temperature": temperature,
                "seed": seed,
            }
        ),
    )
    response.raise_for_status()
    reply = response.json()
    logging.debug(reply)
    return reply["choices"][0]["message"]["content"]


def match_exact(reply: str, answers: List[str]) -> bool:
    return reply.lower() in answers


def match_includes(reply: str, answers: List[str]) -> bool:
    reply = reply.lower()
    return any([(answer in reply) for answer in answers])


def match_fuzzy(reply: str, answers: List[str]) -> bool:
    reply = reply.lower()
    return any([(reply in answer or answer in reply) for answer in answers])


match_funcs = {
    "exact": match_exact,
    "includes": match_includes,
    "fuzzy": match_fuzzy,
}


def evaluate_llms():
    match_func = match_funcs[args.match]

    results = defaultdict(dict)

    for path in args.paths:
        logging.info("Processing prompts from: %s", path)

        # Read questions from file
        with path.open() as f_handle:
            questions = [json.loads(line) for line in f_handle.readlines()]

        logging.info("...found %d questions", len(questions))

        for llm in args.llms:
            logging.info("...evaluating LLM: %s", llm)

            prompts, answers = prepare_prompts(deepcopy(questions), llm)

            def _mapper_func(prompt, expected_answer):
                reply = prompt_llm(prompt, llm_model=llm, temperature=args.temperature, seed=args.seed)
                prompt_context = prompt[0]['content'] #system
                prompt_input = prompt[1]['content']  #user
               
                test_case = LLMTestCase(
                    input=prompt_input,
                    actual_output=reply,
                    expected_output=expected_answer,
                    context=[prompt_context]
                )
                print(prompt_input)
                print(reply)
                print(expected_answer)
                
                # LLM (gpt4) - based metrics, TODO: make an option 
                hallucination_metric = HallucinationMetric(threshold=0.5)
                hallucination_score = hallucination_metric.measure(test_case) 

                quazi_exact_score = Scorer.quasi_exact_match_score(expected_answer, reply)
                bleu_score = Scorer.sentence_bleu_score([expected_answer], reply, "bleu1")
                faithfulness_score = Scorer.faithfulness_score(expected_answer, reply)
                return reply, hallucination_score, quazi_exact_score, bleu_score, faithfulness_score


            with ThreadPoolExecutor(args.threads) as executor:
                logging.info("...with %d threads", args.threads)
                replies = []
                hallucination_scores = []
                quazi_exact_scores = []
                bleu_scores = []
                faithfulness_scores = []
                for prompt, answer in tqdm(zip(prompts, answers), total=len(prompts)):
                     reply, hallucination_score, quazi_score, bleu_score, faithfulness_score = _mapper_func(prompt, answer[0])
                     replies.append(reply)
                     hallucination_scores.append(hallucination_score)
                     quazi_exact_scores.append(quazi_score)
                     bleu_scores.append(bleu_score)
                     faithfulness_scores.append(faithfulness_score)
            
            did_pass = list(map(match_func, replies, answers))
            score = did_pass.count(True) / len(did_pass)  # In percent
            hallucination_average = sum(hallucination_scores) / len(hallucination_scores) * 100
            quazi_exact_score_average = sum(quazi_exact_scores) / len(quazi_exact_scores) * 100
            
            common_score = 0.4 * score + 0.4 * quazi_exact_score_average + 0.2 * (1 - hallucination_average)
            print(score)
            print(common_score)
            logging.info("...got score: %d %%", common_score)

            details = dict(
                zip(
                    ["questions", "replies", "did_pass", "hallucination_score", "quazi_exact_score",
                     "bleu_scores", "faithfulness_scores"],
                    [questions, replies, did_pass, str(hallucination_scores),
                     str(quazi_exact_scores), str(bleu_scores), str(faithfulness_scores)]
                )
            )

            results[path.stem].update({llm: {"score": common_score, "details": details}})

        results_file = args.output_path/'results.json'
        with results_file.open("w") as f_handle:
            print(results)
            json.dump(results, f_handle, sort_keys=True, indent=4)

    scopes = list(results.keys())
    llms = args.llms

    data = [[results[scope][llm]["score"] for scope in scopes] for llm in llms]
    
    ax = sns.heatmap(
        data,
        vmin=0,
        vmax=100,
        annot=True,
        fmt=".1f",
        xticklabels=scopes,
        yticklabels=llms,
    )
    #ax.set(xlabel="Scope", ylabel="LLM", title="Percentage of correct answers")

    # Save the plot to a file
    # plot_file_path = args.plot_file  # Get the file path from command-line arguments
    results_file = args.output_path/'results.png'
    plt.savefig(results_file)
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="evaluate-llms",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "paths", type=Path, nargs="+", help="Paths to files containing prompts."
    )

    parser.add_argument(
        "--llms",
        required=True,
        nargs="+",
        type=str,
        help="Which LLM(s) to use. Refer to https://openrouter.ai/docs#models",
    )

    parser.add_argument(
        "--match",
        type=str,
        choices=["exact", "includes", "fuzzy"],
        default="includes",
        help="Logic for evaluating respones from the LLM(s) agains the ideal answer(s)",
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=20,
        help="Number of threads to use when processing the prompts towards the LLM(s)",
    )

    parser.add_argument(
        "--use-images",
        type=str,
        nargs='+',
        default=[],
        help="Include any images that are referenced in the input files for these specific LLMs",
    )

    parser.add_argument(
        "--alt-system-prompt",
        type=str,
        help="Give an alternative system prompt for setting the scene of the conversation. Will replace the ones in the input .jsonl files"
    )

    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path('./'),
        help="Path to output details about the evaluation in json format to. Defaults to current directory.",
    )

    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=154544424155)

    parser.add_argument("--log-level", type=int, default=logging.INFO)

    ## Parse arguments and start doing our thing
    args = parser.parse_args()

    # Setup logger
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s", level=args.log_level
    )
    logging.captureWarnings(True)
    warnings.filterwarnings("once")

    # Run evaluation
    try:
        evaluate_llms()
    except KeyboardInterrupt:
        sys.exit(0)
