import shutil
from pathlib import Path
from .encounters import *


def make_question(system_prompt, user_prompt, answers, context_image_path):
    question = {}
    question['prompt'] = [
        {"role":"system",
            "content":system_prompt},
        {"role":"user",
            "content": user_prompt}]
    question['answers'] = answers if isinstance(answers,list) else [answers]
    question['image'] = context_image_path
    return question

def generate_situation_description(situation, nautical_phrasing=True):

    # Description with the own ship's information
    own_ship = situation.own_ship
    own_name = own_ship.static.name
    own_type = own_ship.static.ship_type.value
    own_length = own_ship.static.length
    own_speed = own_ship.start_pose.speed
    own_course = own_ship.start_pose.course
    description = f"The own ship, called '{own_name}', is a {own_length} meters long {own_type} moving at a speed of {own_speed} knots on a course of {own_course} degrees. "

    # Description of the total number of targets in the situation
    no_target_ships = len(situation.target_ship)
    if no_target_ships == 1:
        description += f"Around the own ship there is 1 target ship. "
    else:
        description += f"Around the own ship there are {no_target_ships} target ships. "

    # Extracting and adding information about each target ship
    for target_ship in situation.target_ship:
        target_id = target_ship.id
        target_name = target_ship.static.name
        target_type = target_ship.static.ship_type.value
        target_length = target_ship.static.length
        target_speed = target_ship.start_pose.speed
        target_course = target_ship.start_pose.course
        target_relative_bearing = get_relative_bearing(own_ship, target_ship)
        target_range = get_range(own_ship, target_ship)
        
        if nautical_phrasing:
            description += f"Target {target_id}, '{target_name}', a {target_type} of {target_length} meters, making {target_speed} knots on a course of {target_course}°. Target ship {target_id} lies {target_range} nautical miles off, bearing {target_relative_bearing}° relative. "
        else:
            description += f" Target ship {target_id}, called '{target_name}', is a {target_length} meters long {target_type} moving at a speed of {target_speed} knots on a course of {target_course} degrees.  This target ship {target_id} has a range of {target_range} nautical miles and relative bearing of {target_relative_bearing} degrees with respect to the own ship."
    return description.strip()


def copy_question_images(source_directory, target_directory, prefix):

    source = Path(source_directory)
    target = Path(target_directory)
    
    # Create the target directory if it doesn't exist
    target.mkdir(parents=True, exist_ok=True)

    # Define image file extensions
    image_extensions = ['.jpg', '.png', '.jpeg']

    # Iterate over image files in the source directory
    for file_path in source.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            # Construct new filename with suffix
            new_filename = prefix + file_path.stem + file_path.suffix
            new_file_path = target / new_filename

            # Copy the file
            shutil.copy(file_path, new_file_path)

