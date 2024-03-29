import sys
import os
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
sys.path.append(str(parent_dir/'traffic_situations'/'hand_made'))

import json
from trafficgen.read_files import read_situation_files
from utils.questions import *

import fehmarn
        
GENERAL_QUESTION_TEMPLATE = "Marine traffic situation: {} Question: {}"

SYSTEM_PROMPT = """You are an expert mariner and navigator. 
You will be given a marine traffic situation and a multiple choice question about it.
Answer as concisely as possible using the provided choices. For example, if the choices are
(A) starboard, (B) portside, and (C) neither, and the answer is starboard answer '(A) starboard'."""



# SPATIAL REASONING QUESTIONS

NUMBER_OF_SPATIAL_REASONING_QUESTIONS = 40

SPATIAL_REASONING_ENCOUNTER_QUESTIONS = [
    (
        """Is the target ship {} located on starboard or portside of the own ship? 
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

SET_NAME = 'spatial_relationship_and_estimation_of_motion'
copy_question_images(parent_dir/'traffic_situations'/'generated'/'spatial_understanding_set', parent_dir/'questions',SET_NAME + '-')

situations = read_situation_files(parent_dir/'traffic_situations'/'generated'/'spatial_understanding_set')
counter = 0
with open(parent_dir/'questions'/f'{SET_NAME}.jsonl','w') as file:
    for situation in situations:
        situation_description = generate_situation_description(situation)
        encounters = [(situation.own_ship, target_ship) for target_ship in situation.target_ship]
        for specific_question_text_template, answer_function in SPATIAL_REASONING_ENCOUNTER_QUESTIONS:
            for own_ship, target_ship in encounters:
                counter += 1
                if counter > NUMBER_OF_SPATIAL_REASONING_QUESTIONS:
                    break
                question_text = GENERAL_QUESTION_TEMPLATE.format(
                    situation_description,
                    specific_question_text_template.format(target_ship.id))
                answer = answer_function(own_ship, target_ship)
                context_image_path = parent_dir/'questions'/f"{SET_NAME}-{situation.input_file_name[:-5]}.png"
                question = make_question(SYSTEM_PROMPT, question_text, answer, str(context_image_path))
                json.dump(question, file)
                file.write('\n') 
                

# SCENE UNDERSTANDING 
                
NUMBER_OF_SCENE_UNDERSTANDING_QUESTIONS = 40

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

copy_question_images(parent_dir/'traffic_situations'/'generated'/'standard_encounter_set', parent_dir/'questions',SET_NAME + '-')
situations = read_situation_files(parent_dir/'traffic_situations'/'generated'/'standard_encounter_set')
counter = 0
with open(parent_dir/'questions'/f'{SET_NAME}.jsonl','w') as file:
    for situation in situations:
        situation_description = generate_situation_description(situation)
        encounters = [(situation.own_ship, target_ship) for target_ship in situation.target_ship]
        for specific_question_text_template, answer_function in SCENE_UNDERSTANDING_ENCOUNTER_QUESTIONS:
            for own_ship, target_ship in encounters:
                counter += 1
                if counter > NUMBER_OF_SCENE_UNDERSTANDING_QUESTIONS:
                    break
                question_text = GENERAL_QUESTION_TEMPLATE.format(
                    situation_description,
                    specific_question_text_template.format(target_ship.id))
                answer = answer_function(own_ship, target_ship)
                context_image_path = parent_dir/'questions'/f"{SET_NAME}-{situation.input_file_name[:-5]}.png"
                question = make_question(SYSTEM_PROMPT, question_text, answer, str(context_image_path))
                json.dump(question, file)
                file.write('\n')
    


# COLREG AND GOOD SEAMANSHIP 
       

SET_NAME = 'colreg_compliance_and_good_seamanship'

copy_question_images(parent_dir/'traffic_situations'/'hand_made', parent_dir/'questions',SET_NAME + '-')
with open(parent_dir/'questions'/f'{SET_NAME}.jsonl','w') as file:
    for fehmarn_question in fehmarn.questions:
        question_text = GENERAL_QUESTION_TEMPLATE.format(
            fehmarn.situation_description,
            fehmarn_question['text']
        )
        answer = fehmarn_question['correct_answer']
        context_image_path = parent_dir/'questions'/f"{SET_NAME}-fehmarn.png"
        question = make_question(SYSTEM_PROMPT, question_text, answer, str(context_image_path))
        json.dump(question, file)
        file.write('\n')

print("DONE GENERATING QUESTIONS!")

