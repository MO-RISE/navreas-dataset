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

from deepeval import evaluate
from deepeval.metrics.answer_relevancy import AnswerRelevancyMetric
from deepeval.metrics.hallucination_metric import HallucinationMetric
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

            def _mapper_func(prompt):
                reply = prompt_llm(prompt, llm_model=llm, temperature=args.temperature, seed=args.seed)
                prompt_context = prompt[0]['content'] #system
                prompt_input = prompt[1]['content']  #user
               
                test_case = LLMTestCase(
                    input=prompt_input,
                    actual_output=reply,
                    context=[prompt_context],
                    retrieval_context=[prompt_context]
                )
                print(prompt_input)
                print(reply)
                print(prompt_context)
                answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5)
                hallucination_metric = HallucinationMetric(threshold=0.5)
               
                hallucination_score = evaluate([test_case], [hallucination_metric])[0].metrics[0].score
                relevance_score = evaluate([test_case], [answer_relevancy_metric])[0].metrics[0].score

                return reply, relevance_score, hallucination_score


            with ThreadPoolExecutor(args.threads) as executor:
                logging.info("...with %d threads", args.threads)
                replies = []
                factual_scores = []
                relevance_scores = []
                hallucination_scores = []

                for prompt in tqdm(prompts):
                        reply, relevance_score, hallucination_score = _mapper_func(prompt)
                        replies.append(reply)
                         
                        relevance_scores.append(relevance_score)
                        hallucination_scores.append(hallucination_score)
            
            relevance_average = sum(relevance_scores) / len(relevance_scores) * 100
            hallucination_average = sum(hallucination_scores) / len(hallucination_scores) * 100

            final_score = (relevance_average + hallucination_average) / 2

            did_pass = list(map(match_func, replies, answers))
            score = did_pass.count(True) / len(did_pass) * 100  # In percent

            logging.info("...got score: %d %%", score)

            details = dict(
                zip(
                    ["questions", "replies", "did_pass", "deepeval_score"], [questions, replies, did_pass, final_score]
                )
            )

            results[path.stem].update({llm: {"score": score, "details": details}})

        results_file = args.output_path/'results.json'
        with results_file.open("w") as f_handle:
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
    ax.set(xlabel="Scope", ylabel="LLM", title="Percentage of correct answers")

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
