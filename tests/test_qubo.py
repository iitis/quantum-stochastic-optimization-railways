""" test creation and analysis of QUBO in qubo.py file """

import pickle
from scipy.optimize import linprog
from QTrains import QuboVars, Parameters, Railway_input, Analyze_qubo, Variables, LinearPrograming
from QTrains import add_update, find_ones, hist_passing_times, plot_train_diagrams, update_hist, train_path_data
from QTrains import filter_feasible, is_feasible, first_with_given_objective, high_excited_state, best_feasible_state, worst_feasible_state



def test_auxiliary():
    """ test auxiliary functions """
    assert find_ones([0,1,1,1,0]) == [1,2,3]

    d1 = {1:1, 2:2, 3:3}
    d2 = {2:2, 4:4}
    add_update(d1, d2)
    assert d1 == {1:1, 2:4, 3:3, 4:4}


def test_qubo_analyze():
    """ test Analyze_qubo() class """
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


    assert q.headway_constrain == {(2, 3): 2.0, (3, 2): 2.0, (8, 9): 2.0, (9, 8): 2.0}

    #  2: ['A', 1, 2], 3: ['A', 3, 2]
    #  8: ['B', 1, 4], 9: ['B', 3, 4]


    assert q.passing_time_constrain == {(1, 6): 2, (6, 1): 2, (2, 6): 2, (6, 2): 2, (2, 7): 2, (7, 2): 2,
                                        (4, 9): 2, (9, 4): 2, (5, 9): 2, (9, 5): 2, (5, 10): 2, (10, 5): 2}
    assert not q.circ_constrain
    assert len(q.qubo) == 52
    assert q.noqubits == 12

    assert q.qbit_inds == { 0: ['A', 1, 0], 1: ['A', 1, 1], 2: ['A', 1, 2], 3: ['A', 3, 2], 4: ['A', 3, 3],
                         5: ['A', 3, 4], 6: ['B', 1, 2], 7: ['B', 1, 3], 8: ['B', 1, 4], 9: ['B', 3, 4],
                         10: ['B', 3, 5], 11: ['B', 3, 6]}

    qubo_dict = q.store_in_dict(rail_input)
    qubo_to_analyze = Analyze_qubo(qubo_dict)

    solutions = []

    #           0,1,2,3,4,5,6,7,8,9,10,11
    solution = [1,0,0,1,0,0,1,0,0,0,0,1]
    solutions.append(solution)
    assert is_feasible(solution, qubo_to_analyze)

    v = qubo_to_analyze.qubo2int_vars(solution)
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 0, ('A',3): 2, ('B',1): 2, ('B',3): 6}
    assert v['t_A_1'].value == 0
    assert v['t_A_3'].value == 2
    assert v['t_B_1'].value == 2
    assert v['t_B_3'].value == 6

    assert qubo_to_analyze.int_vars2qubo(v) == solution

    # we have objective_stations = ["B"]
    assert qubo_to_analyze.heuristics_degenerate(solution, "A") == [[1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
                                                                    [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                                                                    [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1]]
    s1, s2, s3 = qubo_to_analyze.heuristics_degenerate(solution, "A")

    assert qubo_to_analyze.energy(s1) == qubo_to_analyze.energy(s2) == qubo_to_analyze.energy(s3) 

    assert qubo_to_analyze.binary_vars2sjt(s1) == {('A', 1): 0, ('A', 3): 2, ('B', 1): 2, ('B', 3): 6}
    assert qubo_to_analyze.binary_vars2sjt(s2) == {('A', 1): 0, ('A', 3): 3, ('B', 1): 2, ('B', 3): 6}
    assert qubo_to_analyze.binary_vars2sjt(s3) == {('A', 1): 0, ('A', 3): 4, ('B', 1): 2, ('B', 3): 6}

    assert qubo_to_analyze.heuristics_degenerate(solution, "B") == [[1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1]]


    file =  "tests/pics/qubodiagram.pdf"
    input_dict = train_path_data(v, qubo_to_analyze)
    plot_train_diagrams(input_dict, file)

    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 0, 0,0)  # sum, headway, pass, circ
    assert qubo_to_analyze.objective_val(solution) == 1.0
    assert qubo_to_analyze.broken_MO_conditions(solution) == 0
    assert qubo_to_analyze.energy(solution) == qubo_to_analyze.objective_val(solution) - qubo_to_analyze.sum_ofset


    solution = [1,0,0,1,0,0,1,0,0,0,0,0]
    solutions.append(solution)
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 0, ('A',3): 2, ('B',1): 2}
    assert qubo_to_analyze.count_broken_constrains(solution) == (1, 0, 0, 0)
    assert qubo_to_analyze.energy(solution) == qubo_to_analyze.objective_val(solution) - qubo_to_analyze.sum_ofset + qubo_to_analyze.psum

    solution = [1,0,0,1,0,0,0,0,0,0,0,0]
    solutions.append(solution)
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 0, ('A',3): 2}
    assert qubo_to_analyze.count_broken_constrains(solution) == (2, 0, 0, 0)
    assert qubo_to_analyze.energy(solution) == qubo_to_analyze.objective_val(solution) - qubo_to_analyze.sum_ofset + 2*qubo_to_analyze.psum

    solution = [1,0,0,1,0,0,1,0,0,1,1,1]
    solutions.append(solution)
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 0, ('A',3): 2, ('B',1): 2, ('B',3): 4, ('B',3): 5, ('B',3): 6}
    # with to much variables it is more complicated
    assert qubo_to_analyze.count_broken_constrains(solution) == (4, 0, 0, 0)
    assert qubo_to_analyze.energy(solution) == qubo_to_analyze.objective_val(solution) - qubo_to_analyze.sum_ofset + 4*qubo_to_analyze.psum

     #          0,1,2,3,4,5,6,7,8,9,10,11
    solution = [0,0,1,1,0,0,0,0,1,0,0,1]
    solutions.append(solution)
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 2, ('A',3): 2, ('B',1): 4, ('B',3): 6}
    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 1, 0, 0)
    assert qubo_to_analyze.energy(solution) == qubo_to_analyze.objective_val(solution) - qubo_to_analyze.sum_ofset + 2*qubo_to_analyze.ppair

    solution = [0,0,1,1,0,0,0,0,1,0,0,1]
    solutions.append(solution)
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A', 1): 2, ('A', 3): 2, ('B', 1): 4, ('B', 3): 6}
    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 1, 0, 0)
    assert qubo_to_analyze.energy(solution) == qubo_to_analyze.objective_val(solution) - qubo_to_analyze.sum_ofset + 2*qubo_to_analyze.ppair

    #     0,1,2,3,4,5,6,7,8,9,10,11
    solution = [0,1,0,0,1,0,1,0,0,1,0,0]
    assert not is_feasible(solution, qubo_to_analyze)
    solutions.append(solution)
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A',1): 1, ('A',3): 3, ('B',1): 2, ('B',3): 4}
    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 0, 2, 0)
    assert qubo_to_analyze.broken_MO_conditions(solution) == 0
    assert qubo_to_analyze.energy(solution) == qubo_to_analyze.objective_val(solution) - qubo_to_analyze.sum_ofset + 4*qubo_to_analyze.ppair

    assert filter_feasible(solutions, qubo_to_analyze) == [[1,0,0,1,0,0,1,0,0,0,0,1]]
    assert filter_feasible(solutions, qubo_to_analyze, softern_pass_t = True) == [[1,0,0,1,0,0,1,0,0,0,0,1], [0,1,0,0,1,0,1,0,0,1,0,0]]

    ###  filtering test series of feasible states

    solutions = [[1,0,1,0,0,0,1,0,0,0,0,1], [1,0,0,1,0,0,1,0,0,1,0,0], [1,0,0,1,0,0,1,0,0,0,1,0], [1,0,0,1,0,0,1,0,0,0,0,1]]

    assert filter_feasible(solutions, qubo_to_analyze)  == [[1,0,0,1,0,0,1,0,0,1,0,0], [1,0,0,1,0,0,1,0,0,0,1,0], [1,0,0,1,0,0,1,0,0,0,0,1]]
    assert high_excited_state(solutions, qubo_to_analyze, ["A", "B"], 3) == ([1,0,0,1,0,0,1,0,0,0,0,1], 1)
    assert first_with_given_objective(solutions, qubo_to_analyze, 1) == [1,0,0,1,0,0,1,0,0,0,0,1]
    assert best_feasible_state(solutions, qubo_to_analyze) == ([1,0,0,1,0,0,1,0,0,1,0,0], 0)
    assert worst_feasible_state(solutions, qubo_to_analyze) == ([1,0,0,1,0,0,1,0,0,0,0,1], 1)
    


    timetable = {"A": {1:0, 3:2}, "B": {1:2 , 3:4}}
    p = Parameters(timetable, dmax = 2, headways = 1)
    objective_stations = ["B"]
    delays = {1:2}
    rail_input = Railway_input(p, objective_stations, delays)
    q = QuboVars(rail_input)
    q.make_qubo(rail_input)

    qubo_dict = q.store_in_dict(rail_input)

    with open('tests/qubo.json', 'wb') as fp:
        pickle.dump(qubo_dict, fp)

    with open('tests/qubo.json', 'rb') as fp:
        dict_read = pickle.load(fp)

    assert qubo_dict == dict_read

    qubo_to_analyze = Analyze_qubo(dict_read)

    solution = [1,0,0,0,0,1,0,0,1,1,0,0]
    assert qubo_to_analyze.qbit_inds == {0: ['A', 1, 2], 1: ['A', 1, 3], 2: ['A', 1, 4],
                                        3: ['A', 3, 2], 4: ['A', 3, 3], 5: ['A', 3, 4],
                                        6: ['B', 1, 4], 7: ['B', 1, 5], 8: ['B', 1, 6],
                                        9: ['B', 3, 4], 10: ['B', 3, 5], 11: ['B', 3, 6]}

    assert qubo_to_analyze.broken_MO_conditions(solution) == 1
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('A', 1): 2, ('A', 3): 4, ('B', 1): 6, ('B', 3): 4}
    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 0, 1, 0)





def test_qubo_circ():
    """ test QuboVars class for simple problem of two trains with rolling stock circulation """
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
    """ test QuboVars class for larger problem of two trains heading in the same direction """
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable, dmax = 2)

    objective_stations = ["MR", "CS"]
    i = Railway_input(p, objective_stations, delays = {3:2})
    q = QuboVars(i)


    assert q.sjt_inds == {'PS': {1: {0: 0, 1: 1, 2: 2}},
                          'MR': {1: {3: 3, 4: 4, 5: 5}, 3: {2: 6, 3: 7, 4: 8}},
                          'CS': {1: {16: 9, 17: 10, 18: 11}, 3: {15: 12, 16: 13, 17: 14}}}
    assert q.qbit_inds == {0: ['PS', 1, 0], 1: ['PS', 1, 1], 2: ['PS', 1, 2], 3: ['MR', 1, 3],
                           4: ['MR', 1, 4], 5: ['MR', 1, 5],
                           6: ['MR', 3, 2], 7: ['MR', 3, 3], 8: ['MR', 3, 4],
                           9: ['CS', 1, 16], 10: ['CS', 1, 17], 11: ['CS', 1, 18],
                           12: ['CS', 3, 15], 13: ['CS', 3, 16], 14: ['CS', 3, 17]}


    q.make_qubo(i)

    assert len(q.qubo) == 87
    assert q.noqubits == 15

    print( q.objective )

    print( q.sum_constrain )

    assert q.objective == {(3, 3): 0.0, (4, 4): 0.5, (5, 5): 1.0, (6, 6): 1.0,
                           (7, 7): 1.5, (8, 8): 2.0, (9, 9): 0.0, (10, 10): 0.5,
                           (11, 11): 1.0, (12, 12): 1.0, (13, 13): 1.5, (14, 14): 2.0}

    assert q.sum_constrain == {(0, 0): -2.0, (0, 1): 2.0, (0, 2): 2.0, (1, 1): -2.0,
                               (1, 0): 2.0, (1, 2): 2.0, (2, 2): -2.0, (2, 0): 2.0,
                               (2, 1): 2.0, (3, 3): -2.0, (3, 4): 2.0, (3, 5): 2.0,
                               (4, 4): -2.0, (4, 3): 2.0, (4, 5): 2.0, (5, 5): -2.0,
                               (5, 3): 2.0, (5, 4): 2.0, (6, 6): -2.0, (6, 7): 2.0,
                               (6, 8): 2.0, (7, 7): -2.0, (7, 6): 2.0, (7, 8): 2.0,
                               (8, 8): -2.0, (8, 6): 2.0, (8, 7): 2.0, (9, 9): -2.0,
                               (9, 10): 2.0, (9, 11): 2.0, (10, 10): -2.0, (10, 9): 2.0,
                               (10, 11): 2.0, (11, 11): -2.0, (11, 9): 2.0, (11, 10): 2.0,
                               (12, 12): -2.0, (12, 13): 2.0, (12, 14): 2.0,
                               (13, 13): -2.0, (13, 12): 2.0, (13, 14): 2.0,
                               (14, 14): -2.0, (14, 12): 2.0, (14, 13): 2.0}


    assert len(q.headway_constrain) == 24
    for (k, kp) in q.headway_constrain:
        assert -2 <= q.qbit_inds[k][2] - q.qbit_inds[kp][2] <= 2


    assert len(q.passing_time_constrain) == 18
    for (k, kp) in q.passing_time_constrain:
        if "CS" in [ q.qbit_inds[k][0],  q.qbit_inds[kp][0] ]:
            assert -13 < q.qbit_inds[k][2] - q.qbit_inds[kp][2] < 13
        if "PS" in [ q.qbit_inds[k][0],  q.qbit_inds[kp][0] ]:
            assert -3 < q.qbit_inds[k][2] - q.qbit_inds[kp][2] < 3



def test_smallest_qubo():
    """  test comparison of QUBO output vs LP output """
    timetable = {"MR" :{1: 3}, "CS" : {1: 16}}
    objective_stations = ["MR", "CS"]
    delays = {1:1}
    p = Parameters(timetable, dmax = 3, headways = 1)
    rail_input = Railway_input(p, objective_stations, delays)
    q = QuboVars(rail_input, psum = 4, ppair = 2)
    q.make_qubo(rail_input)

    assert q.noqubits == 8
    assert len(q.qubo) == 44

    solution = [1,0,0,0,1,0,0,0]
    qubo_dict = q.store_in_dict(rail_input)
    qubo_to_analyze = Analyze_qubo(qubo_dict)
    assert qubo_to_analyze.broken_MO_conditions(solution) == 0
    assert qubo_to_analyze.count_broken_constrains(solution) == (0, 0, 0, 0)
    assert qubo_to_analyze.binary_vars2sjt(solution) == {('MR', 1): 4, ('CS', 1): 17}
    assert qubo_to_analyze.objective_val(solution) == (1/3+1/3)


def test_qubo_vs_LP():
    """  test comparison of QUBO output vs LP output """
    timetable = {"A": {1:0, 3:2}, "B": {1:2 , 3:4}}
    delays = {3:0}

    p = Parameters(timetable, dmax = 2, headways = 1)
    objective_stations = ["B"]
    rail_input = Railway_input(p, objective_stations, delays)

    #QUBO
    q = QuboVars(rail_input)
    q.make_qubo(rail_input)
    qubo_dict = q.store_in_dict(rail_input)
    qubo_to_analyze = Analyze_qubo(qubo_dict)
    solution = [1,0,0,1,0,0,1,0,0,0,0,1]
    vq = qubo_to_analyze.qubo2int_vars(solution)
    assert vq['t_A_1'].value == 0
    assert vq['t_A_3'].value == 2
    assert vq['t_B_1'].value == 2
    assert vq['t_B_3'].value == 6
    assert qubo_to_analyze.objective_val(solution) == 1.0


    hist = hist_passing_times(vq, ["A", "B"], qubo_to_analyze)
    assert hist == [1.0, 3.0]

    hist_list = list([])
    qubo_objective = list([1.0])
    feasible = update_hist(qubo_to_analyze, solution, ["A", "B"], hist_list, qubo_objective)

    assert hist_list == [1.0, 3.0]
    assert qubo_objective == [1.0, 1.0]
    assert bool(feasible)

    hist_list = list([])
    qubo_objective = list([])
    feasible = update_hist(qubo_to_analyze, solution, ["A", "B"], hist_list, qubo_objective, softern_pass_t = True)

    assert hist_list == [1.0, 3.0]
    assert qubo_objective == [1.0]
    assert bool(feasible)

    solution = [0,1,0,1,0,0,1,0,0,0,0,1]
    hist_list = list([])
    qubo_objective = list([])
    feasible = update_hist(qubo_to_analyze, solution, ["A", "B"], hist_list, qubo_objective, softern_pass_t = True)

    assert hist_list == [0.0, 3.0]
    assert qubo_objective == [1.0]
    assert bool(feasible)


    # LP
    v = Variables(rail_input)
    bounds, integrality = v.bonds_and_integrality()
    prob = LinearPrograming(v, rail_input, M = 15)
    opt = linprog(c=prob.obj, A_ub=prob.lhs_ineq,
                  b_ub=prob.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)
    v.linprog2vars(opt)
    vl = v.variables
    assert vl['t_A_1'].value == 0
    assert vl['t_A_3'].value == 2
    assert vl['t_B_1'].value == 2
    assert vl['t_B_3'].value == 4
    assert prob.compute_objective(v, rail_input) == 0.0


    #stochastic  LP
    v = Variables(rail_input)
    bounds, integrality = v.bonds_and_integrality()
    prob = LinearPrograming(v, rail_input, M = 15, delta = 1)
    opt = linprog(c=prob.obj, A_ub=prob.lhs_ineq,
                  b_ub=prob.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)
    v.linprog2vars(opt)
    vl = v.variables
    assert vl['t_A_1'].value == 0
    assert vl['t_A_3'].value == 2
    assert vl['t_B_1'].value == 3
    assert vl['t_B_3'].value == 5
    assert prob.compute_objective(v, rail_input) == 1.0

    # QUBO
    hist_list = list([])
    qubo_objective = list([])
    q = QuboVars(rail_input)
    q.make_qubo(rail_input, delta = 1)
    qubo_dict = q.store_in_dict(rail_input)
    qubo_to_analyze = Analyze_qubo(qubo_dict)

    solution = [1,0,0,1,0,0,0,1,0,0,1,0]
    vq = qubo_to_analyze.qubo2int_vars(solution)
    assert vq['t_A_1'].value == 0
    assert vq['t_A_3'].value == 2
    assert vq['t_B_1'].value == 3
    assert vq['t_B_3'].value == 5

    feasible = update_hist(qubo_to_analyze, solution, ["A", "B"], hist_list, qubo_objective)

    assert hist_list == [2.0, 2.0]
    assert qubo_objective == [1.0]
    assert bool(feasible)



def test_2trains():
    """ test QUBO from article """

    circ = {(1,14): "CS"}
    timetable = {"PS":{1:14, 14:58}, "MR":{1:17, 14:55},
                          "CS":{1:32, 14:40}
                        }
    objective_stations = ["MR", "CS"]
    delays = {1:5}
    par = Parameters(timetable, dmax = 2, headways = 1, circulation = circ)
    rail_input = Railway_input(par, objective_stations, delays)
    q = QuboVars(rail_input, psum = 4, ppair = 2)
    q.make_qubo(rail_input)

    assert q.qbit_inds == {0: ['PS', 1, 19], 1: ['PS', 1, 20], 2: ['PS', 1, 21], 3: ['PS', 14, 58],
                           4: ['PS', 14, 59], 5: ['PS', 14, 60], 6: ['MR', 1, 22], 7: ['MR', 1, 23],
                           8: ['MR', 1, 24], 9: ['MR', 14, 55], 10: ['MR', 14, 56], 11: ['MR', 14, 57],
                           12: ['CS', 1, 37], 13: ['CS', 1, 38], 14: ['CS', 1, 39], 15: ['CS', 14, 40],
                           16: ['CS', 14, 41], 17: ['CS', 14, 42]}

    circ_constr = {(12, 15): 2, (15, 12): 2, (13, 15): 2, (15, 13): 2, (13, 16): 2,
                   (16, 13): 2, (14, 15): 2, (15, 14): 2, (14, 16): 2, (16, 14): 2,
                   (14, 17): 2, (17, 14): 2}


    for k, el in circ_constr.items():
        assert el == q.qubo[k]

    pt_constrain = {(1, 6): 2, (6, 1): 2, (2, 6): 2, (6, 2): 2, (2, 7): 2, (7, 2): 2,
                    (7, 12): 2, (12, 7): 2, (8, 12): 2, (12, 8): 2, (8, 13): 2, (13, 8): 2,
                    (16, 9): 2, (9, 16): 2, (17, 9): 2, (9, 17): 2, (17, 10): 2, (10, 17): 2,
                    (10, 3): 2, (3, 10): 2, (11, 3): 2, (3, 11): 2, (11, 4): 2, (4, 11): 2}


    for k, el in pt_constrain.items():
        assert el == q.qubo[k]

    sum_constr = {(0, 0): -4, (0, 1): 4, (0, 2): 4, (1, 1): -4, (1, 0): 4,
                  (1, 2): 4, (2, 2): -4, (2, 0): 4, (2, 1): 4, (3, 3): -4,
                  (3, 4): 4, (3, 5): 4, (4, 4): -4, (4, 3): 4, (4, 5): 4,
                  (5, 5): -4, (5, 3): 4, (5, 4): 4, (6, 6): -4, (6, 7): 4, (6, 8): 4,
                  (7, 7): -4, (7, 6): 4, (7, 8): 4, (8, 8): -4, (8, 6): 4, (8, 7): 4,
                  (9, 9): -4, (9, 10): 4, (9, 11): 4, (10, 10): -4, (10, 9): 4,
                  (10, 11): 4, (11, 11): -4, (11, 9): 4, (11, 10): 4,
                  (12, 12): -4, (12, 13): 4, (12, 14): 4, (13, 13): -4,
                  (13, 12): 4, (13, 14): 4, (14, 14): -4, (14, 12): 4,
                  (14, 13): 4, (15, 15): -4, (15, 16): 4, (15, 17): 4,
                  (16, 16): -4, (16, 15): 4, (16, 17): 4, (17, 17): -4,
                  (17, 15): 4, (17, 16): 4}

    objective = {(6, 6): 2.5, (7, 7): 3.0, (8, 8): 3.5, (9, 9): 0.0,
                (10, 10): 0.5, (11, 11): 1.0, (12, 12): 2.5,
                (13, 13): 3.0, (14, 14): 3.5, (15, 15): 0.0,
                (16, 16): 0.5, (17, 17): 1.0}


    assert len( q.qubo )  == len( circ_constr ) + len(pt_constrain) + len(sum_constr)

    for k, el in sum_constr.items():
        if k not in objective:
            assert el == q.qubo[k]
        else:
            assert el + objective[k] == q.qubo[k]





