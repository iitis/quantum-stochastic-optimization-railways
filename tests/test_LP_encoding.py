""" testing ILP solver"""
import pytest
from scipy.optimize import linprog
from QTrains import Variables, LinearPrograming, Parameters, Railway_input
from QTrains import plot_train_diagrams, train_path_data

def test_variables_class():
    """ test class Variables """
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}

    p = Parameters(timetable, dmax = 5)
    objective_stations = ["MR", "CS"]
    i = Railway_input(p, objective_stations, delays = {3:2})
    assert i.trains_paths == {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    v = Variables(i)
    assert v.variables['t_PS_1'].range == (0, 5)

    our_vars = v.variables
    assert list(our_vars.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert v.indices_objective_vars(i) == [1,2,3,4]
    assert [v.int_id for v in our_vars.values()] == [0,1,2,3,4,5,6]


    assert v.variables['t_PS_1'].int_id == 0
    assert v.variables['t_PS_1'].type == int
    assert v.variables['t_CS_1'].int_id == 2
    assert v.variables['t_PS_1'].type == int

    #problem.add_all_bounds()
    assert [v.range for v in v.variables.values()] == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 7.0), (15.0, 20.0), (0.0, 1.0), (0.0, 1.0)]
    v.set_y_value(('MR', 1, 3), 1)
    assert [v.range for v in v.variables.values()] == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 7.0), (15.0, 20.0), (1,1), (0.0, 1.0)]
    v.reset_y_bonds(('MR', 1, 3))
    assert [v.range for v in v.variables.values()] == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 7.0), (15.0, 20.0), (0.0, 1.0), (0.0, 1.0)]

    v.relax_integer_req()
    assert v.variables['t_PS_1'].type == float
    v.restore_integer_req()
    assert v.variables['t_PS_1'].type == int
    assert list(v.variables.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert v.obj_vars == [1,2,3,4]


def test_LP_class():
    """test LinearPrograming class"""
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable, dmax = 5)

    objective_stations = ["MR", "CS"]
    i = Railway_input(p, objective_stations, delays = {3:2})
    v = Variables(i)
    problem = LinearPrograming(v, i)

    assert problem.obj == [0.0, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0]
    assert problem.obj_ofset == 6.4

def test_constrains():
    """test encoding particular particular constrains"""
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable, dmax = 5)

    objective_stations = ["MR", "CS"]
    r_input = Railway_input(p, objective_stations, delays = {2:3})
    v = Variables(r_input)
    assert v.variables["t_MR_1"].range == (3,8)

    problem = LinearPrograming(v, r_input, M = 10)

    # testing only headways
    problem.lhs_ineq = []
    problem.rhs_ineq = []
    problem.add_headways(v, r_input)
    assert problem.lhs_ineq == [[0, 1, 0, -1, 0, 10, 0], [0, -1, 0, 1, 0, -10, 0], [0, 0, 1, 0, -1, 0, 10], [0, 0, -1, 0, 1, 0, -10]]
    assert problem.rhs_ineq == [8, -2, 8, -2]

    # testing only passing times
    problem.lhs_ineq = []
    problem.rhs_ineq = []
    problem.add_passing_times(v, r_input)

    assert problem.lhs_ineq  == [[1, -1, 0, 0, 0, 0, 0], [0, 1, -1, 0, 0, 0, 0], [0, 0, 0, 1, -1, 0, 0]]
    assert problem.rhs_ineq == [-3, -13, -13]

    timetable = {"A": {1:0, 2:8}, "B": {1:2 , 2:6}}
    par = Parameters(timetable, dmax = 4, headways = 1, circulation = {(1,2): "B"})

    objective_stations = ["A", "B"]
    r_input = Railway_input(par, objective_stations, delays = {1:1})
    assert r_input.trains_paths == {1: ["A", "B"], 2: ["B", "A"]}

    v = Variables(r_input)
    problem = LinearPrograming(v, r_input, M = 10)

    # testing only circ
    problem.lhs_ineq = []
    problem.rhs_ineq = []
    problem.add_circ_constrain(v, r_input)
    assert list(v.variables.keys()) == ['t_A_1', 't_B_1', 't_B_2', 't_A_2']
    assert problem.lhs_ineq  == [[0, 1, -1, 0]]
    assert problem.rhs_ineq == [-4]

    bounds, integrality = v.bonds_and_integrality()
    assert bounds == [(1, 5), (3, 7), (6, 10), (8, 12)]
    assert integrality == [1, 1, 1, 1]


def test_optimization_simple_headways():
    """ test simple example with headways """
    # add train number are going one way and even the other way
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable, dmax = 10)

    objective_stations = ["MR", "CS"]
    r_input = Railway_input(p, objective_stations, delays = {3:2})
    v = Variables(r_input)
    bounds, integrality = v.bonds_and_integrality()

    problem = LinearPrograming(v, r_input, M = 10)

    opt = linprog(c=problem.obj, A_ub=problem.lhs_ineq,
                  b_ub=problem.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)

    v.linprog2vars(opt)

    all_vars = ["t_PS_1", "t_MR_1", "t_CS_1", "t_MR_3", "t_CS_3"]
    arr_times = [0, 4, 17, 2, 15]

    for i, var in enumerate( all_vars ):
        assert v.variables[var].value == arr_times[i]

    assert problem.compute_objective(v, r_input) == pytest.approx(0.6)


def test_optimization_simple_circ():
    """ test simple example with circulation """
    # add train number are going one way and even the other way
    timetable = {"A": {1:0, 2:8}, "B": {1:2 , 2:6}}
    par = Parameters(timetable, dmax = 10, headways = 1, circulation = {(1,2): "B"})

    objective_stations = ["A", "B"]
    r_input = Railway_input(par, objective_stations, delays = {1:1})

    v = Variables(r_input)
    bounds, integrality = v.bonds_and_integrality()

    problem = LinearPrograming(v, r_input, M = 10)

    opt = linprog(c=problem.obj, A_ub=problem.lhs_ineq,
                  b_ub=problem.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)

    v.linprog2vars(opt)

    all_vars = ["t_A_1", "t_B_1", "t_B_2", "t_A_2"]
    arr_times = [1,3,7,9]

    for i, var in enumerate( all_vars ):
        assert v.variables[var].value == arr_times[i]

    assert problem.compute_objective(v, r_input) == pytest.approx(0.4)



def test_optimization_larger_headways_circ():
    """ test simple example with headways """
    # add train number are going one way and even the other way
    timetable =  {"PS": {1: 0, 4:33}, "MR" :{1: 3, 3: 0, 5:5, 4:30}, "CS" : {1: 16 , 3: 13, 4:17, 5:18}}
    p = Parameters(timetable, dmax = 10, circulation = {(3,4): "CS"})

    objective_stations = ["MR", "CS"]
    r_input = Railway_input(p, objective_stations, delays = {3:2})
    v = Variables(r_input)
    bounds, integrality = v.bonds_and_integrality()

    problem = LinearPrograming(v, r_input, M = 10)


    opt = linprog(c=problem.obj, A_ub=problem.lhs_ineq,
                  b_ub=problem.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)

    v.linprog2vars(opt)

    all_vars = ["t_PS_1", "t_MR_1", "t_CS_1", "t_MR_3", "t_CS_3", "t_CS_4", "t_MR_4", "t_MR_5", "t_CS_5",
                "y_MR_1_3", "y_CS_1_3", "y_MR_1_5", "y_CS_1_5", "y_MR_3_5", "y_CS_3_5"]
    arr_times = [0, 4, 17, 2, 15, 19, 32, 6, 19, 0, 0, 1,1,1,1]

    for i, var in enumerate( all_vars ):
        assert v.variables[var].value == arr_times[i]

    v.check_clusters()

    assert problem.compute_objective(v, r_input) == pytest.approx(1.2)


def test_train_diagrams():
    """ test plotting of train diagrams """
    timetable =  {"PS": {1: 0, 4:33}, "MR" :{1: 3, 3: 0, 5:5, 4:30}, "CS" : {1: 16 , 3: 13, 4:17, 5:18}}
    p = Parameters(timetable, dmax = 10, circulation = {(3,4): "CS"})
    objective_stations = ["MR", "CS"]
    r_input = Railway_input(p, objective_stations, delays = {3:2})
    v = Variables(r_input)
    bounds, integrality = v.bonds_and_integrality()
    problem = LinearPrograming(v, r_input, M = 10)

    opt = linprog(c=problem.obj, A_ub=problem.lhs_ineq,
                  b_ub=problem.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)

    v.linprog2vars(opt)

    file = "tests/pics/LPdiagram.pdf"
    input_dict = train_path_data(v.variables, p)
    plot_train_diagrams(input_dict, file)
