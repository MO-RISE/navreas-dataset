import sys
import numpy as np
from pathlib import Path
from pytest import approx

current_dir = Path(__file__).parent.resolve()
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from trafficgen.read_files import read_situation_files
from utils.encounters import *

situation = read_situation_files(current_dir)[0]

def test_relative_position():
    rel_pos = get_relative_position(situation.own_ship, situation.target_ship[0])
    assert rel_pos[0] == 300
    assert rel_pos[1] == 1000

def test_get_relative_bearing():
    assert get_relative_bearing(situation.own_ship, situation.target_ship[0]) == approx(np.rad2deg(np.arctan2(300,1000)))
    assert get_relative_bearing(situation.own_ship, situation.target_ship[1]) == 270


def test_get_cpa():
    dcpa, tcpa = get_cpa(situation.own_ship, situation.target_ship[0])
    assert tcpa != 0.0
    assert dcpa == 300.0
    dcpa, tcpa = get_cpa(situation.own_ship, situation.target_ship[1])
    assert tcpa == 0.0
    assert dcpa == 300.0

def test_get_starboard_or_portside():
    assert get_starboard_or_portside(situation.own_ship, situation.target_ship[0]) == 'starboard'
    assert get_starboard_or_portside(situation.own_ship, situation.target_ship[1]) == 'portside'
    assert get_starboard_or_portside(situation.own_ship, situation.target_ship[2]) == 'neither'

def test_get_ahead_or_astern():
    assert get_ahead_or_astern(situation.own_ship, situation.target_ship[0]) == 'ahead'
    assert get_ahead_or_astern(situation.own_ship, situation.target_ship[1]) == 'neither'
    assert get_ahead_or_astern(situation.own_ship, situation.target_ship[2]) == 'astern'

def test_get_approaching_or_receding():
    assert get_approaching_or_receding(situation.own_ship, situation.target_ship[0]) == 'approaching'
    assert get_approaching_or_receding(situation.own_ship, situation.target_ship[1]) == 'receding'
    assert get_approaching_or_receding(situation.own_ship, situation.target_ship[2]) == 'receding'

def test_get_bow_crossing_range():
    assert None == get_bow_crossing_range(situation.own_ship, situation.target_ship[2])
    assert -500 == get_bow_crossing_range(situation.own_ship, situation.target_ship[3]) 
    assert None == get_bow_crossing_range(situation.own_ship, situation.target_ship[4])
    assert 0.0 == get_bow_crossing_range(situation.own_ship, situation.target_ship[5])
 
def test_get_bow_or_stern_crossing():
    assert 'neither' == get_bow_or_stern_crossing(situation.own_ship, situation.target_ship[2])
    assert 'stern' == get_bow_or_stern_crossing(situation.own_ship, situation.target_ship[3]) 
    assert 'neither' == get_bow_or_stern_crossing(situation.own_ship, situation.target_ship[4])
    assert 'neither' == get_bow_or_stern_crossing(situation.own_ship, situation.target_ship[5])