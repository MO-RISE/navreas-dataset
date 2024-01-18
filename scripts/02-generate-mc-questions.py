import sys
import os
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import json
from trafficgen.read_files import read_situation_files
from utils.questions import *

        
GENERAL_QUESTION_TEMPLATE = "Marine traffic situation: {} Question: {}"

SYSTEM_PROMPT = "You are an expert mariner and navigator."

# SPATIAL REASONING QUESTIONS


SPATIAL_REASONING_ENCOUNTER_QUESTIONS = [
    (
        """Is the target_ship {} located on starboard or portside of the own ship? 
        Please select the appropriate option:
        (A) starboard
        (B) portside
        (C) neither.""",
        get_starboard_or_portside_location
    ),
    (
        """Is the target ship {} located ahead or astern of the own ship? 
        Please select the appropriate option:
        (A) ahead
        (B) astern
        (C) neither.""",
        get_ahead_or_astern_location
    ),
    (
        """Is the target ship {} approaching or receding the own ship? 
        Please select the appropriate option:
        (A) approacing or (B) receding.""",
        get_approaching_or_receding
    ),
    (
        """Is the target ship {} crossing ahead or astern of the own ship? 
        Please select the appropriate option:
        (A) ahead
        (B) astern
        (C) neither.""",
        get_ahead_or_astern_crossing
    )
]

SET_NAME = 'spatial_reasoning'
copy_question_images(parent_dir/'traffic_situations'/'generated'/'spatial_understanding_set', parent_dir/'questions',SET_NAME + '-')

situations = read_situation_files(parent_dir/'traffic_situations'/'generated'/'spatial_understanding_set')
with open(parent_dir/'questions'/f'{SET_NAME}.jsonl','w') as file:
    for situation in situations:
        situation_description = generate_situation_description(situation)
        encounters = [(situation.own_ship, target_ship) for target_ship in situation.target_ship]
        for specific_question_text_template, answer_function in SPATIAL_REASONING_ENCOUNTER_QUESTIONS:
            for own_ship, target_ship in encounters:
                question_text = GENERAL_QUESTION_TEMPLATE.format(
                    situation_description,
                    specific_question_text_template.format(target_ship.id))
                answer = answer_function(own_ship, target_ship)
                context_image_path = SET_NAME + '-' + situation.input_file_name[:-5] + '.png'
                question = make_question(SYSTEM_PROMPT, question_text, answer, context_image_path)
                json.dump(question, file)
                file.write('\n')

# SCENE UDNERSSTANDING 
                
SET_NAME = 'scene_understanding'

SCENE_UNDERSTANDING_ENCOUNTER_QUESTIONS = [
    (
        """Is there any risk of collision between the target ship {} and the own ship?
        Please select the appropriate option:
        (A) yes
        (B) no.""", 
        get_risk_of_collision
    ),
    (
        """What is the type of the encounter according to the International Regulations for Preventing Collisions at Sea (COLREGs)
        between the own ship and the target ship {}, as perceived from the own ship's perspective?
        Please select the appropriate option:
        (A) overtaking 
        (B) head-on
        (C) crossing 
        (E) neither 
  
        """,
        get_colreg_encounter_type
    ),
    (
        """In the encounter between the own ship and th target ship {}, which of them is the stand on ship
        according to the International Regulations for Preventing Collisions at Sea (COLREGs)?
        Please select the appropriate option;
        (A) own ship
        (B) target ship
        (C) neither
        """,
        get_stand_on_ship
    )
]

situations = read_situation_files(parent_dir/'traffic_situations'/'generated'/'standard_encounter_set')
with open(parent_dir/'questions'/f'{SET_NAME}.jsonl','w') as file:
    for situation in situations:
        situation_description = generate_situation_description(situation)
        encounters = [(situation.own_ship, target_ship) for target_ship in situation.target_ship]
        for specific_question_text_template, answer_function in SCENE_UNDERSTANDING_ENCOUNTER_QUESTIONS:
            for own_ship, target_ship in encounters:
                question_text = GENERAL_QUESTION_TEMPLATE.format(
                    situation_description,
                    specific_question_text_template.format(target_ship.id))
                answer = answer_function(own_ship, target_ship)
                context_image_path = SET_NAME + '-' + situation.input_file_name[:-5] + '.png'
                question = make_question(SYSTEM_PROMPT, question_text, answer, context_image_path)
                json.dump(question, file)
                file.write('\n')