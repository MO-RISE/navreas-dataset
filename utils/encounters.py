"""
Functions to analyse encouters in marine traffic situations
"""

from typing import Tuple  
import numpy as np
from trafficgen import calculate_relative_bearing, determine_colreg
from trafficgen.types import Ship, TargetShip

TO_KNOTS = 3600 / 1852
TO_MS = 1852 / 3600

THETA13_CRITERIA= 67.5,
THETA14_CRITERIA= 5.0,
THETA15_CRITERIA= 5.0,
THETA15 = [
    112.5,
    247.5
]
    
def _get_velocity_vector(ship: Ship):
    speed = ship.start_pose.speed * TO_MS
    course = np.radians(ship.start_pose.course)
    v_x = speed* np.round(np.sin(course), decimals=10)
    v_y = speed* np.round(np.cos(course), decimals=10)
    return np.array([v_x, v_y])

def _get_position_vector(ship):
    return np.array([ship.start_pose.position.east, ship.start_pose.position.north])

def get_relative_position(own_ship: Ship, target_ship: TargetShip):
    target_pos = _get_position_vector(target_ship)
    own_pos = _get_position_vector(own_ship)
    return target_pos - own_pos

def get_relative_bearing(own_ship: Ship, target_ship: TargetShip)-> float:
    alpha, _ = calculate_relative_bearing(
        own_ship.start_pose.position,
        own_ship.start_pose.course,
        target_ship.start_pose.position,
        target_ship.start_pose.course
    )
    if alpha > 360:
        alpha %= 360
    return np.round(alpha,1)

def get_range(own_ship: Ship, target_ship: Ship):
    return np.round(np.linalg.norm(get_relative_position(own_ship, target_ship)) / 1852, 1)

def get_cpa(own_ship: Ship, target_ship: Ship) -> Tuple[float, float]:
    """Get the distance and time to Closest Point of Approach (CPA) between two vessels
    (own and target)

    The formulas assume that the velocity vectors of the vessels remain consant (i.e.
    costant speed and course).

    Source: http://geomalgorithms.com/a07-_distance.html#cpa_time()
    """

    own_velocity = _get_velocity_vector(own_ship)
    target_velocity = _get_velocity_vector(target_ship)

    # Calculation of Time to Closest Point of Approach
    velocity_diff = target_velocity - own_velocity
    velocity_diff_2 = np.dot(velocity_diff, velocity_diff)
    if velocity_diff_2 < 0.01:
        tcpa = 0
    else:
        relative_position = get_relative_position(own_ship, target_ship)
        tcpa = -np.dot(relative_position, velocity_diff) / velocity_diff_2

    # Calculation of Distance to Closest Point of Approach
    movement_own = tcpa * own_velocity
    movement_target = tcpa * target_velocity
    relative_movement_target = (
        get_relative_position(own_ship, target_ship) + movement_target
    )
    dcpa = np.linalg.norm(relative_movement_target - movement_own)

    return dcpa, tcpa


def get_starboard_or_portside_location(own_ship: Ship, target_ship: TargetShip):
    """Get if the Target ship is on the starboard or portside of the own ship
    """
    alfa = get_relative_bearing(own_ship, target_ship)
    if alfa == 0.0 or alfa == 180:
        return 'neither'
    if alfa > 0.0 and alfa < 180:
        return 'starboard'
    return 'portside'


def get_ahead_or_astern_location(own_ship: Ship, target_ship: TargetShip):
    """Get if the Target ship is on the ahead or astern of the own ship
    """
    alfa = get_relative_bearing(own_ship, target_ship)
    if alfa == 270 or alfa == 90:
        return 'neither'
    if alfa > 270.0 or alfa < 90:
        return 'ahead'
    return 'astern'

def get_approaching_or_receding(own_ship: Ship, target_ship: TargetShip):
    """Get if a the Target ship is approaching the own ship or receding"""
    _ , tcpa = get_cpa(own_ship,target_ship)
    if tcpa <= 0.0:
        return 'receding'
    return 'approaching'

def get_bow_crossing_range(own_ship: Ship, target_ship: TargetShip):
    """
    Based on the algorithm described in:
    https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect

    """
    p = _get_position_vector(own_ship)
    q = _get_position_vector(target_ship)
    r = _get_velocity_vector(own_ship)
    s = _get_velocity_vector(target_ship)
    rxs = np.cross(r, s)
    if np.round(rxs,2) == 0.0: 
        # The courses are parallel. 
        return None
    t = np.cross(q - p, s)/rxs # time it takes the own ship to reach the intersection point
    u = np.cross(q - p, r)/rxs # time it takes the target ship to reach the intersection point
    if t < 0.0 or u < 0.0:
        # The ships are diverging
        return None
    i = q + u*s # Intersection point
    k = p + u*r # Position of own ship when the target ship reaches the intersection point
    if np.round(t) == np.round(u):
        # Collision
        return 0.0
    sign = 1 if u < t else -1
    return sign*np.round(np.linalg.norm(i - k),2)
    
def get_ahead_or_astern_crossing(own_ship: Ship, target_ship: TargetShip):
    
    bcr = get_bow_crossing_range(own_ship, target_ship)

    if bcr == None or bcr == 0.0:
        return 'neither'
    if bcr > 0.0:
        return 'ahead'
    return 'astern'


def get_risk_of_collision(own_ship: Ship, target_ship: TargetShip):
    dcpa, tcpa = get_cpa(own_ship, target_ship)
    if tcpa < 0.0:
        return 'no'
    if dcpa >= own_ship.static.length*10:
        return 'no'
    return 'yes'


def get_colreg_encounter_type(own_ship, target_ship):
    beta, alpha = calculate_relative_bearing(
        own_ship.start_pose.position,
        own_ship.start_pose.course,
        target_ship.start_pose.position,
        target_ship.start_pose.course
    )
    encounter_type = determine_colreg(
        alpha,
        beta,
        THETA13_CRITERIA,
        THETA14_CRITERIA,
        THETA15_CRITERIA,
        THETA15
    )
   
    if 'overtaking' in encounter_type.value:
        return 'overtaking'
    if 'crossing' in encounter_type.value:
        return 'crossing'
    if 'head-on' in encounter_type.value:
        return 'head-on'
    return 'neither'
    
def get_stand_on_ship(own_ship, target_ship):
    beta, alpha = calculate_relative_bearing(
        own_ship.start_pose.position,
        own_ship.start_pose.course,
        target_ship.start_pose.position,
        target_ship.start_pose.course
    )
    encounter_type = determine_colreg(
        alpha,
        beta,
        THETA13_CRITERIA,
        THETA14_CRITERIA,
        THETA15_CRITERIA,
        THETA15
    )
    if 'give-way' in encounter_type.value: 
        return 'target ship'
    if 'stand-on' in encounter_type.value:
        return 'own ship'
    return 'neither'
    
   