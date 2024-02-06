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

from retry import retry
import requests
import seaborn as sns
from tqdm import tqdm
from dotenv import load_dotenv
import matplotlib.pyplot as plt

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

@retry(tries=3, delay=5)
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
    if 'error' in reply:
        raise Exception(f"API error \n code: {reply['error']['code']} \n message: {reply['error']['message']} \n prompt: {prompt}")
    return reply["choices"][0]["message"]["content"]
   


def match_exact(reply: str, answers: List[str]) -> bool:
    return reply.lower() in answers


def match_includes(reply: str, answers: List[str]) -> bool:
    reply = reply.lower()
    return any([(answer.lower() in reply) for answer in answers])


def match_fuzzy(reply: str, answers: List[str]) -> bool:
    reply = reply.lower()
    return any([(reply in answer or answer in reply) for answer in answers])


match_funcs = {
    "exact": match_exact,
    "includes": match_includes,
    "fuzzy": match_fuzzy,
}

def format_string(input_string, max_line_length=20):
    # Replace underscores with spaces
    formatted_string = input_string.replace("_", " ")
    
    # Split the string into words
    words = formatted_string.split()
    
    # Initialize an empty string and a temporary line string
    result_string = ""
    temp_line = ""
    
    # Iterate over the words
    for word in words:
        # Check if adding the next word exceeds the max line length
        if len(temp_line + word) > max_line_length:
            # If so, append the temp line to the result string and reset it
            result_string += temp_line.strip() + "\n"
            temp_line = word + " "  # Start a new line with the current word
        else:
            # If not, continue adding words to the temp line
            temp_line += word + " "
    
    # Add the last line to the result string
    result_string += temp_line.strip()
    
    return result_string

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
                return prompt_llm(
                    prompt, llm_model=llm, temperature=args.temperature, seed=args.seed
                )

            with ThreadPoolExecutor(args.threads) as executor:
                logging.info("...with %d threads", args.threads)
                replies = list(
                    tqdm(
                        executor.map(_mapper_func, prompts),
                        total=len(prompts),
                    )
                )

            did_pass = list(map(match_func, replies, answers))
            summary = list(zip(answers,replies,did_pass))
            questions_replies = [{'question':question, 'reply':reply} for question, reply in zip(questions, replies)]
            score = did_pass.count(True) / len(did_pass) * 100  # In percent

            logging.info("...got score: %d %%", score)

            details = dict(
                zip(
                    ["questions_replies","summary"], [questions_replies, summary]
                )
            )

            results[path.stem].update({llm: {"score": score, "details": details}})

        results_name = 'results.json' if args.output_name == None else args.output_name + '.json' 
        results_file = args.output_path/results_name
        with results_file.open("w") as f_handle:
            json.dump(results, f_handle, sort_keys=True, indent=4)

    scopes = list(results.keys())

    llms = args.llms

    data = [[results[scope][llm]["score"] for scope in scopes] for llm in llms]

    plt.figure(figsize=(10, 8)) 

    ax = sns.heatmap(
        data,
        vmin=0,
        vmax=100,
        annot=True, 
        fmt=".1f",
        xticklabels=[format_string(scope) for scope in scopes],
        yticklabels=llms,
    )
    ax.set(xlabel="Scope", ylabel="LLM", title="Percentage of correct answers")

    # Adjust layout to prevent labels from being cropped
    plt.tight_layout()      

    # Save the plot to a file
    # plot_file_path = args.plot_file  # Get the file path from command-line arguments
    results_name = 'results.png' if args.output_name == None else args.output_name + '.png' 
    results_file = args.output_path/results_name
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

    parser.add_argument(
        "--output_name",
        type=str,
        help="Give a name to the output files."
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
