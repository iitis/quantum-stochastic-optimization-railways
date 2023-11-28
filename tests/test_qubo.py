import pickle
from QTrains import QuboVars, Parameters, Railway_input, Analyze_qubo, add_update, find_ones, plot_train_diagrams



def test_auxiliary():
    assert find_ones([0,1,1,1,0]) == [1,2,3]

    d1 = {1:1, 2:2, 3:3}
    d2 = {2:2, 4:4}
    add_update(d1, d2)
    assert d1 == {1:1, 2:4, 3:3, 4:4}


def test_qubo_analyze():
    timetable = {"A": {1:0, 3:2}, "B": {1:2 , 3:4}}
    delays = {3:0}

    p = Parameters(timetable, dmax = 2, headways = 1)
    objective_stations = ["B"]
    rail_input = Railway_input(p, objective_stations, delays)
    q = QuboVars(rail_input)

    assert q.sjt_inds['A'] == {1: {0:0, 1:1, 2:2}, 3: {2:3, 3:4, 4:5}}
    q.make_qubo(rail_input)

    assert q.qbit_inds == {0: ['A', 1, 0], 1: ['A', 1, 1], 2: ['A', 1, 2], 3: ['A', 3, 2], 4: ['A', 3, 3],
                                5: ['A', 3, 4], 6: ['B', 1, 2], 7: ['B', 1, 3], 8: ['B', 1, 4], 9: ['B', 3, 4],
                                10: ['B', 3, 5], 11: ['B', 3, 6]}
    assert q.objective == {(6, 6): 0.0, (7, 7): 0.5, (8, 8): 1.0, (9, 9): 0.0, (10, 10): 0.5, (11, 11): 1.0}
    assert q.sum_constrain == {(0, 0): -2, (0, 1): 2, (0, 2): 2, (1, 1): -2, (1, 0): 2, (1, 2): 2,
                               (2, 2): -2, (2, 0): 2, (2, 1): 2, (3, 3): -2, (3, 4): 2, (3, 5): 2,
                               (4, 4): -2, (4, 3): 2, (4, 5): 2, (5, 5): -2, (5, 3): 2, (5, 4): 2,
                               (6, 6): -2, (6, 7): 2, (6, 8): 2, (7, 7): -2, (7, 6): 2, (7, 8): 2,
                               (8, 8): -2, (8, 6): 2, (8, 7): 2, (9, 9): -2, (9, 10): 2, (9, 11): 2,
                               (10, 10): -2, (10, 9): 2, (10, 11): 2, (11, 11): -2, (11, 9): 2, (11, 10): 2}
    assert q.headway_constrain == {(2, 3): 2, (3, 2): 2, (8, 9): 2, (9, 8): 2}
    assert q.passing_time_constrain == {(1, 6): 2, (6, 1): 2, (2, 6): 2, (6, 2): 2, (2, 7): 2, (7, 2): 2,
                                        (4, 9): 2, (9, 4): 2, (5, 9): 2, (9, 5): 2, (5, 10): 2, (10, 5): 2}
    assert not q.circ_constrain
    assert len(q.qubo) == 52
    assert q.noqubits == 12

    assert q.qbit_inds == { 0: ['A', 1, 0], 1: ['A', 1, 1], 2: ['A', 1, 2], 3: ['A', 3, 2], 4: ['A', 3, 3],
                         5: ['A', 3, 4], 6: ['B', 1, 2], 7: ['B', 1, 3], 8: ['B', 1, 4], 9: ['B', 3, 4],
                         10: ['B', 3, 5], 11: ['B', 3, 6]}
    
    dict = q.store_in_dict(rail_input)
    qubo_to_analyze = Analyze_qubo(dict)


    #           0,1,2,3,4,5,6,7,8,9,10,11
    solution = [1,0,0,1,0,0,1,0,0,0,0,1]
    v = qubo_to_analyze.qubo2int_vars(solution)
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 0, ('A',3): 2, ('B',1): 2, ('B',3): 6}
    assert v['t_A_1'].value == 0
    assert v['t_A_3'].value == 2
    assert v['t_B_1'].value == 2
    assert v['t_B_3'].value == 6

    file =  "tests/pics/qubodiagram.pdf"
    plot_train_diagrams(v, qubo_to_analyze.trains_paths, qubo_to_analyze.pass_time, qubo_to_analyze.stay, file)

    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 0, 0,0)  # sum, headway, pass, circ
    assert qubo_to_analyze.objective_val(solution) == 1.0
    assert qubo_to_analyze.broken_MO_conditions(solution) == 0


    solution = [1,0,0,1,0,0,1,0,0,0,0,0]
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 0, ('A',3): 2, ('B',1): 2}
    assert qubo_to_analyze.count_broken_constrains(solution) == (1, 0, 0, 0)

     #          0,1,2,3,4,5,6,7,8,9,10,11
    solution = [0,0,1,1,0,0,0,0,1,0,0,1]
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 2, ('A',3): 2, ('B',1): 4, ('B',3): 6}
    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 1, 0, 0)


    #     0,1,2,3,4,5,6,7,8,9,10,11
    solution = [1,0,0,0,0,1,0,1,0,1,0,0]
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 0, ('A',3): 4, ('B',1): 3, ('B',3): 4}
    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 0, 1, 0)
    assert qubo_to_analyze.broken_MO_conditions(solution) == 0


     #          0,1,2,3,4,5,6,7,8,9,10,11

    timetable = {"A": {1:0, 3:2}, "B": {1:2 , 3:4}}
    p = Parameters(timetable, dmax = 4, headways = 1)
    objective_stations = ["B"]
    delays = {1:2}
    rail_input = Railway_input(p, objective_stations, delays)
    q = QuboVars(rail_input)
    q.make_qubo(rail_input)

    dict = q.store_in_dict(rail_input)
    
    with open('tests/qubo.json', 'wb') as fp:
        pickle.dump(dict, fp)

    with open('tests/qubo.json', 'rb') as fp:
        dict_read = pickle.load(fp)
    
    assert dict == dict_read

    qubo_to_analyze = Analyze_qubo(dict_read)

    solution = [0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1]
    assert qubo_to_analyze.broken_MO_conditions(solution) == 1
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 4, ('A',3): 2, ('B',1):6, ('B',3): 8}
    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 0, 0, 0)





def test_qubo_circ():
    timetable = {"A": {1:0, 2:8}, "B": {1:2 , 2:6}}
    par = Parameters(timetable, dmax = 2, headways = 1, circulation = {(1,2): "B"})

    objective_stations = ["B"]
    r_input = Railway_input(par, objective_stations, delays = {1:0})
    q = QuboVars(r_input, ppair = 4)

    assert q.ppair == 4
    q.add_circ_constrain(r_input)
    assert q.qbit_inds == {0: ['A', 1, 0], 1: ['A', 1, 1], 2: ['A', 1, 2],
                               3: ['A', 2, 8], 4: ['A', 2, 9], 5: ['A', 2, 10],
                               6: ['B', 1, 2], 7: ['B', 1, 3], 8: ['B', 1, 4],
                               9: ['B', 2, 6], 10: ['B', 2, 7], 11: ['B', 2, 8]}
    assert q.circ_constrain == {(7, 9): 4, (9, 7): 4, (8, 9): 4, (9, 8): 4, (8, 10): 4, (10, 8): 4}


def test_qubo_larger():
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable, dmax = 5)

    objective_stations = ["MR", "CS"]
    i = Railway_input(p, objective_stations, delays = {3:2})
    q = QuboVars(i)

    assert q.sjt_inds == {'PS': {1: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}},
                                  'MR': {1: {3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11}, 3: {2: 12, 3: 13, 4: 14, 5: 15}},
                                  'CS': {1: {16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21}, 3: {15: 22, 16: 23, 17: 24, 18: 25}}}
    assert q.qbit_inds == {0: ['PS', 1, 0], 1: ['PS', 1, 1], 2: ['PS', 1, 2], 3: ['PS', 1, 3],
                               4: ['PS', 1, 4], 5: ['PS', 1, 5], 6: ['MR', 1, 3], 7: ['MR', 1, 4],
                               8: ['MR', 1, 5], 9: ['MR', 1, 6], 10: ['MR', 1, 7], 11: ['MR', 1, 8],
                               12: ['MR', 3, 2], 13: ['MR', 3, 3], 14: ['MR', 3, 4], 15: ['MR', 3, 5],
                               16: ['CS', 1, 16], 17: ['CS', 1, 17], 18: ['CS', 1, 18], 19: ['CS', 1, 19],
                               20: ['CS', 1, 20], 21: ['CS', 1, 21], 22: ['CS', 3, 15], 23: ['CS', 3, 16],
                               24: ['CS', 3, 17], 25: ['CS', 3, 18]}


    q.make_qubo(i)

    assert len(q.qubo) == 244
    assert q.noqubits == 26

    assert q.objective == {(6, 6): 0.0, (7, 7): 0.2, (8, 8): 0.4, (9, 9): 0.6,
                           (10, 10): 0.8, (11, 11): 1.0, (12, 12): 0.4, (13, 13): 0.6,
                           (14, 14): 0.8, (15, 15): 1.0, (16, 16): 0.0, (17, 17): 0.2,
                           (18, 18): 0.4, (19, 19): 0.6, (20, 20): 0.8, (21, 21): 1.0,
                           (22, 22): 0.4, (23, 23): 0.6, (24, 24): 0.8, (25, 25): 1.0}
    assert q.sum_constrain == {(0, 0): -2, (0, 1): 2, (0, 2): 2, (0, 3): 2, (0, 4): 2,
                               (0, 5): 2, (1, 1): -2, (1, 0): 2, (1, 2): 2, (1, 3): 2,
                               (1, 4): 2, (1, 5): 2, (2, 2): -2, (2, 0): 2, (2, 1): 2,
                               (2, 3): 2, (2, 4): 2, (2, 5): 2, (3, 3): -2, (3, 0): 2,
                               (3, 1): 2, (3, 2): 2, (3, 4): 2, (3, 5): 2, (4, 4): -2,
                               (4, 0): 2, (4, 1): 2, (4, 2): 2, (4, 3): 2, (4, 5): 2,
                               (5, 5): -2, (5, 0): 2, (5, 1): 2, (5, 2): 2, (5, 3): 2,
                               (5, 4): 2, (6, 6): -2, (6, 7): 2, (6, 8): 2, (6, 9): 2,
                               (6, 10): 2, (6, 11): 2, (7, 7): -2, (7, 6): 2, (7, 8): 2,
                               (7, 9): 2, (7, 10): 2, (7, 11): 2, (8, 8): -2, (8, 6): 2,
                               (8, 7): 2, (8, 9): 2, (8, 10): 2, (8, 11): 2, (9, 9): -2,
                               (9, 6): 2, (9, 7): 2, (9, 8): 2, (9, 10): 2, (9, 11): 2,
                               (10, 10): -2, (10, 6): 2, (10, 7): 2, (10, 8): 2, (10, 9): 2,
                               (10, 11): 2, (11, 11): -2, (11, 6): 2, (11, 7): 2, (11, 8): 2,
                               (11, 9): 2, (11, 10): 2, (12, 12): -2, (12, 13): 2, (12, 14): 2,
                               (12, 15): 2, (13, 13): -2, (13, 12): 2, (13, 14): 2, (13, 15): 2,
                               (14, 14): -2, (14, 12): 2, (14, 13): 2, (14, 15): 2, (15, 15): -2,
                               (15, 12): 2, (15, 13): 2, (15, 14): 2, (16, 16): -2, (16, 17): 2,
                               (16, 18): 2, (16, 19): 2, (16, 20): 2, (16, 21): 2, (17, 17): -2,
                               (17, 16): 2, (17, 18): 2, (17, 19): 2, (17, 20): 2, (17, 21): 2,
                               (18, 18): -2, (18, 16): 2, (18, 17): 2, (18, 19): 2, (18, 20): 2,
                               (18, 21): 2, (19, 19): -2, (19, 16): 2, (19, 17): 2, (19, 18): 2,
                               (19, 20): 2, (19, 21): 2, (20, 20): -2, (20, 16): 2, (20, 17): 2,
                               (20, 18): 2, (20, 19): 2, (20, 21): 2, (21, 21): -2, (21, 16): 2,
                               (21, 17): 2, (21, 18): 2, (21, 19): 2, (21, 20): 2, (22, 22): -2,
                               (22, 23): 2, (22, 24): 2, (22, 25): 2, (23, 23): -2, (23, 22): 2,
                               (23, 24): 2, (23, 25): 2, (24, 24): -2, (24, 22): 2, (24, 23): 2,
                               (24, 25): 2, (25, 25): -2, (25, 22): 2, (25, 23): 2, (25, 24): 2}

    assert len(q.headway_constrain) == 32
    for (k, kp) in q.headway_constrain:
        assert -2 < q.qbit_inds[k][2] - q.qbit_inds[kp][2] < 2

    assert len(q.passing_time_constrain) == 72
    for (k, kp) in q.passing_time_constrain:
        if "CS" in [ q.qbit_inds[k][0],  q.qbit_inds[kp][0] ]:
            assert -13 < q.qbit_inds[k][2] - q.qbit_inds[kp][2] < 13
        if "PS" in [ q.qbit_inds[k][0],  q.qbit_inds[kp][0] ]:
            assert -3 < q.qbit_inds[k][2] - q.qbit_inds[kp][2] < 3



def test_qubo_1():
    timetable = {"A": {1:0, 2:8}, "B": {1:2 , 2:6}}
    par = Parameters(timetable, dmax = 10, headways = 1, circulation = {(1,2): "B"})

    objective_stations = ["B"]
    r_input = Railway_input(par, objective_stations, delays = {1:0})
    q = QuboVars(r_input)
    q.make_qubo(r_input)

    assert len(q.qubo) == 812
    assert q.noqubits == 44


def test_qubo_2():
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable, dmax = 10)

    objective_stations = ["MR", "CS"]
    r_input = Railway_input(p, objective_stations, delays = {3:2})
    q = QuboVars(r_input)
    q.make_qubo(r_input)

    assert len(q.qubo) == 909
    assert q.noqubits == 51

def test_qubo_3():
    timetable =  {"PS": {1: 0, 4:33}, "MR" :{1: 3, 3: 0, 5:5, 4:30}, "CS" : {1: 16 , 3: 13, 4:17, 5:18}}
    p = Parameters(timetable, dmax = 10, circulation = {(3,4): "CS"})

    objective_stations = ["MR", "CS"]
    r_input = Railway_input(p, objective_stations, delays = {3:2})
    q = QuboVars(r_input)
    q.make_qubo(r_input)

    assert len(q.qubo) == 2008
    assert q.noqubits == 106
