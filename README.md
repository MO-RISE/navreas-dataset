# NAVigation REASoning dataset

A dataset for evaluating the navigation reasoning of Large Language Models (LLMs).

The dataset consists of sets of questions about marine traffic situations in a JSONL format and a number of images describing the situations. The questions and images are located in the `questions` directory. The dataset includes the following sets of questions:

**`spatial_relationship_and_estimation_of_motion.jsonl`**

Includes the following type of questions:

- At starboard or at portside?
- A ahead or astern?
- Approaching or receding?
- Will cross ahead or astern?

**`scene_understanding.jsonl`**

Includes the following type of questions:

- Is there a risk of collision, yes or no?
- What is the type of CORLEG encounter between the own ship and a target ship?
- In the encounter, which ship is the stand-on ship according to the COLREGS?

**`colreg_compliance_and_good_seamanship.jsonl`**

Includes the following type of questions:

- If the situation was to be soved in X manner, which COLREG rule would be broken?
- Of the given possible solutions, which is the safest one?

The generation and usage of these dataset is done through three scripts locate in the `scripts` directory:

**`01-generate-traffic-situations.py`**

Generates traffic situations using [Traffic Generator](https://github.com/dnv-opensource/ship-traffic-generator). The situations are described with json files and images. Configuration files and generated files are found in the `traffic_situations` directory.

**`02-generate-mc-questions.py`**

Generates the sets of questions based on the traffic situations using the functions in the `utils` directory. The generated questions are found in the `questions` directory.

**`03-evaluate-llms.py`**

Evaluates LLMs through a command line interface. See "Usage" below for more details.

## Installation

Clone the repository locally and add a `.env` in the main directory with following content:

```
OPENROUTER_API_KEY=<your OPEN Router key here>
```

### Devcontainer in VSCode.

The repository includes the configuration necessary to use a devcontainer in VS Code. For more information on how to use a devcontainer see [here](https://code.visualstudio.com/docs/devcontainers/tutorial).

### Virutal environment

Within a virtual environment (such as conda) install all the dependencies by running:

```bash
pip install -r requirements.txt
```

## Usage

### Modify the questions

Edit and run the script `02-generate-mc-questions.py`

### Evaluation

The evaluation is made through the `03-evaluate-llms.py` script/program. To obtain info on its use run:

```bash
python 03-evaluate-llms.py --help
```

The LLMs to be evaluted must be declared with the [model names used by Open Router](https://openrouter.ai/docs#models). For example, to evaluate OpenAI's GPT-3.5-turbo and Mistral 7B Instruct models with respect to both of the sets, the following command could be run:

```bash
python 03-evaluate-llms.py ../questions/spatial_relationship_and_estimation_of_motion.jsonl ../questions/scene_understanding.jsonl --llms  openai/gpt-3.5-turbo mistralai/mistral-7b-instruct
```

The results are saved as two files `results.json` and `results.png`. By default these images are saved to the current directory. To change the output path the flag `--output-path` can be used.

The flag `--use-images` specifies which models should include the images describing the marine traffic situations in the questions. For example to compare OpenAI's GPT-3.5-turbo, Mistral 7B Instruct models and OpenAI's GPT4 Vision the followin could should be run:

```bash
 python 03-evaluate-llms.py ../questions/scene_understanding.jsonl --llms openai/gpt-4-vision-preview mistralai/mistral-7b-instruct openai/gpt-3.5-turbo --use-images openai/gpt-4-vision-preview
```

## Roadmap

The following questions describe the roadmap of this dataset. Some of this questions are implemented other not.

**Spatial relationship and estimation of motion**

- At starboard or at portside?
- A ahead or astern?
- Moving or standing still?
- Approaching or receding?
- Starboard turn or portside turn\*?
- CPA? TCPA?
- Will cross ahead or astern?
- Bow and stern crossing distance?

**Scene understanding**

- Determine if there is risk of collision (Yes or No, following Rule 8)
- If yes, determine the type of COLREG situation (head-on, crossing, overtaking).
- Determine which vessel should give way.

**Actions to be taken according to COLREG and good seamanship (Rule 2, 8, 13, 14, and 15)**

- Stand-on or give-way?
- Alteration of course or speed.
- Well-defined (i.e. readily apparent visually or by radar)\*
- Timely.\*
- Reduce the risk of collision (plan for everyone’s safety)
- Consider maneuvering capabilities.\*
- Consider uncertainties.\*
- Consider the restrictions and limitations of surrounding vessels.

\*Missing at the moment

# Prompts used in the report

```
python 03-evaluate-llms.py ../questions/spatial_relationship_and_estimation_of_motion.jsonl ../questions/scene_understanding.jsonl ../questions/colreg_compliance_and_good_seamanship.jsonl --llms  mistralai/mistral-7b-instruct open-orca/mistral-7b-openorca openai/gpt-3.5-turbo openai/gpt-4-turbo-preview google/gemini-pro anthropic/claude-2 --output_name base-results
```

```
python 03-evaluate-llms.py ../questions/spatial_relationship_and_estimation_of_motion.jsonl ../questions/scene_understanding.jsonl ../questions/colreg_compliance_and_good_seamanship.jsonl --llms openai/gpt-4-turbo-preview openai/gpt-4-vision-preview google/gemini-pro google/gemini-pro-vision --output_name base-results-vision  --use-images  openai/gpt-4-vision-preview google/gemini-pro-vision
```
