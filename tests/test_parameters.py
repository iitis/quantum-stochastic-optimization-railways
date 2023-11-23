from QTrains import match_lists, common_s_same_dir, pairs_same_direction, station_pairs, Parameters, Railway_input

def test_helpers():
    a = [1,2,3]
    b = [2,3]
    assert match_lists(a, b) == ([2, 3], 2)

    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    assert common_s_same_dir(trains_paths, 1, 3) == ["MR", "CS"]
    assert pairs_same_direction(trains_paths)  == [(1, 3, 'MR'), (1, 3, 'CS')]
    assert station_pairs(trains_paths) == [[1, 'PS', 'MR'], [1, 'MR', 'CS'], [3, 'MR', 'CS']]

    trains_paths = {1: ["PS", "MR", "CS"], 2: ["CS", "MR"]}
    assert common_s_same_dir(trains_paths, 1, 2) == []
    assert pairs_same_direction(trains_paths)  == []

def test_par_class():
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable)
    assert p.headways == 2
    assert p.stay == 1


def test_initial_conditions():

    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    objective_stations = ["MR", "CS"]
    delays = {3:2}  # train:delay
    p = Parameters(timetable, dmax = 5)


    assert p.pass_time == {"PS_MR": 2, "MR_CS": 12}

    i = Railway_input(p, objective_stations, delays)
    assert i.trains_paths == {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]} 
    assert i.tvar_range ==  {"PS": {1: (0., 5.)}, "MR" :{1: (3.,8.), 3: (2.,5.)}, "CS" : {1: (16.,21.) , 3: (15., 18.)}}





