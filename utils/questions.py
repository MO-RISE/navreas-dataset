from .encounters import *
from trafficgen.types import Position, Ship, Situation, TargetShip
from trafficgen import calculate_relative_bearing

# {'question': "asfsadfasf 1) ",
#  'answer':1}
# def generate_question()



def make_question(system_prompt, user_prompt, answers):
    question = {}
    question['prompt'] = [
        {"role":"system",
            "content":system_prompt},
        {"role":"user",
            "content": user_prompt}]
    question['answers'] = answers if isinstance(answers,list) else [answers]
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

def generate_spatial_reasoning_questions(situation):
    

    encounters = [(situation.own_ship, target_ship) for target_ship in situation.target_ship]
    
    questions = []

    for own_ship, target_ship in encounters:

        # Starboard or portside
        question = f"""Is the target ship {target_ship.id} to the starboard or portside 
        of the own ship? \n 
        
        """
        side = get_starboard_or_portside(own_ship, target_ship)
        print(side)



# def determine_colreg_type(own_ship: Ship, target_ship: TargetShip):
#     alfa, beta = get_relative_bearing(own_ship, target_ship)
#     theta13_criteria = 67.5,
#     theta14_criteria = 5.0,
#     theta15_criteria = 5.0,
#     theta15 = [
#         112.5,
#         247.5
#     ]
#     colreg_type = determine_colreg(
#         alpha,
#         beta,
#         theta13_criteria,
#         theta14_criteria,
#         theta15_criteria,
#         theta15,
#     )
#     return colreg_type
