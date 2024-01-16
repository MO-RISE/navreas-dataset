import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import json
from trafficgen.read_files import read_situation_files
from utils.questions import *

situations = read_situation_files(parent_dir/'tests')

system_prompt = "You are an expert mariner and navigator."
question_prompt_template = "Nautical situation: {} Question: On which side of the own ship is the target ship {}? Answer only either 'starboard', 'portside', or 'neither'."

# Writing each dictionary to a new line in the file
with open('foo.jsonl', 'w') as file:

    for situation in situations:
        situation_description = generate_situation_description(situation)
        encounters = [(situation.own_ship, target_ship) for target_ship in situation.target_ship]
        for own_ship, target_ship in encounters:
            question = question_prompt_template.format(situation_description, target_ship.id)
            ideal_answer = get_starboard_or_portside(own_ship, target_ship)
            chat_prompt  = make_chat_prompt(system_prompt, question, ideal_answer)
            print(chat_prompt)
            json.dump(chat_prompt, file)
            file.write('\n')
