""" testing module parameters """
from QTrains import match_lists, common_s_same_dir, pairs_same_direction, station_pairs, Parameters, Railway_input

def test_helpers():
    """ test helpers in parameters """
    a = [1,2,3]
    b = [2,3]
    assert match_lists(a, b) == ([2, 3], 2)

    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    assert common_s_same_dir(trains_paths, 1, 3) == ["MR", "CS"]
    assert pairs_same_direction(trains_paths)  == [(1, 3, 'MR'), (1, 3, 'CS')]
    assert station_pairs(trains_paths) == [[1, 'PS', 'MR'], [1, 'MR', 'CS'], [3, 'MR', 'CS']]

    trains_paths = {1: ["PS", "MR", "CS"], 2: ["CS", "MR"]}
    assert not common_s_same_dir(trains_paths, 1, 2)
    assert not pairs_same_direction(trains_paths)

def test_parameter_class():
    """ test class Parameters()  """
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable)
    assert p.headways == 2
    assert p.stay == 1
    assert p.pass_time == {"PS_MR": 2, "MR_CS": 12}
    assert p.trains_paths == {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}


def test_initial_conditions():
    """ test class Railway_input() """
    timetable = {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    delays = {3:2} # train:delay
    p = Parameters(timetable, dmax = 5)

    objective_stations = ["MR", "CS"]
    i = Railway_input(p, objective_stations, delays)
    assert i.tvar_range ==  {"PS": {1: (0., 5.)}, "MR" :{1: (3.,8.), 3: (2.,7.)}, "CS" : {1: (16.,21.) , 3: (15., 20.)}}
    assert i.objective_stations == ['MR', 'CS']
