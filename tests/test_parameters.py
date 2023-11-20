from QTrains import match_lists, common_s_same_dir, pairs_same_direction, station_pairs, Parameters

def test_helpers():
    a = [1,2,3]
    b = [2,3]
    assert match_lists(a, b) == ([2, 3], 2)

    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    assert common_s_same_dir(trains_paths, 1, 3) == ["MR", "CS"]
    assert pairs_same_direction(trains_paths)  == [(1, 3, 'MR'), (1, 3, 'CS')]
    assert station_pairs(trains_paths) == [[1, 'PS', 'MR'], [1, 'MR', 'CS'], [3, 'MR', 'CS']]

def test_par_class():
    p = Parameters()
    assert p.headways == 0
    assert p.stay == 0

