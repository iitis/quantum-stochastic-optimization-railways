""" testing ILP solver"""
import pytest
from scipy.optimize import linprog
from QTrains import Variables, LinearPrograming, Parameters, Railway_input

def test_variables_class():
    """ test class Variables """
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    objective_stations = ["MR", "CS"]

    p = Parameters(timetable, dmax = 5)
    i = Railway_input(p, objective_stations, delays = {3:2})
    v = Variables(i)
    assert v.y_vars == ['y_MR_1_3', 'y_CS_1_3']
    assert v.trains_paths == {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    out_vars = {}

    v.add_t_vars(v, out_vars)
    assert list(out_vars.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3']

    v.add_y_vars_same_direction(i, out_vars)
    assert list(out_vars.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert v.indices_objective_vars(i) == [1,2,3,4]


def test_LP_class():
    """test LinearPrograming class"""
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    objective_stations = ["MR", "CS"]
    p = Parameters(timetable, dmax = 5)
    i = Railway_input(p, objective_stations, delays = {3:2})
    v = Variables(i)

    assert v.variables['t_PS_1'].count == 0
    assert v.variables['t_PS_1'].type == int
    assert v.variables['t_CS_1'].count == 2
    assert v.variables['t_PS_1'].type == int

    example_problem = LinearPrograming(v, i)


    assert list(example_problem.variables.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert example_problem.penalty_vars == [1,2,3,4]
    assert example_problem.obj == [0.0, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0]
    assert example_problem.obj_ofset == 6.4


    example_problem.add_all_bounds()
    assert [v.range for v in example_problem.variables.values()] == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 5.0), (15.0, 18.0), (0.0, 1.0), (0.0, 1.0)]
    example_problem.set_y_value(('MR', 1, 3), 1)
    assert [v.range for v in example_problem.variables.values()] == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 5.0), (15.0, 18.0), (1,1), (0.0, 1.0)]
    example_problem.reset_y_bonds(('MR', 1, 3))
    assert [v.range for v in example_problem.variables.values()] == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 5.0), (15.0, 18.0), (0.0, 1.0), (0.0, 1.0)]

    example_problem.relax_integer_req()
    assert example_problem.variables['t_PS_1'].type == float
    example_problem.restore_integer_req()
    assert example_problem.variables['t_PS_1'].type == int

def test_constrains():
    """test encoding particular particular constrains"""
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    objective_stations = ["MR", "CS"]

    p = Parameters(timetable, dmax = 5)
    r_input = Railway_input(p, objective_stations, delays = {2:3})
    v = Variables(r_input)
    example_problem = LinearPrograming(v, r_input, M = 10)

    assert example_problem.variables["t_MR_1"].range == (3,8)

    # testing only headways
    example_problem.lhs_ineq = []
    example_problem.rhs_ineq = []
    example_problem.add_headways(p)
    assert example_problem.lhs_ineq == [[0, 1, 0, -1, 0, 10, 0], [0, -1, 0, 1, 0, -10, 0], [0, 0, 1, 0, -1, 0, 10], [0, 0, -1, 0, 1, 0, -10]]
    assert example_problem.rhs_ineq == [8, -2, 8, -2]

    # testing only passing times
    example_problem.lhs_ineq = []
    example_problem.rhs_ineq = []
    example_problem.add_passing_times(p)

    assert example_problem.lhs_ineq  == [[1, -1, 0, 0, 0, 0, 0], [0, 1, -1, 0, 0, 0, 0], [0, 0, 0, 1, -1, 0, 0]]
    assert example_problem.rhs_ineq == [-3, -13, -13]

    objective_stations = ["A", "B"]
    timetable = {"A": {1:0, 2:8}, "B": {1:2 , 2:6}}
    par = Parameters(timetable, dmax = 4, headways = 1)
    r_input = Railway_input(par, objective_stations, delays = {1:1})
    r_input.circulation = {"B": (1,2)}
    v = Variables(r_input)
    assert v.trains_paths == {1: ["A", "B"], 2: ["B", "A"]}
    example_problem = LinearPrograming(v, r_input, M = 10)

    # testing only circ
    example_problem.lhs_ineq = []
    example_problem.rhs_ineq = []
    example_problem.add_circ_constrain(r_input)
    assert list(v.variables.keys()) == ['t_A_1', 't_B_1', 't_B_2', 't_A_2']
    assert example_problem.lhs_ineq  == [[0, 1, -1, 0]]
    assert example_problem.rhs_ineq == [-4]

    bounds, integrality = example_problem.bonds_and_integrality()
    assert bounds == [(1, 4), (3, 6), (6, 10), (8, 12)]
    assert integrality == [1, 1, 1, 1]


def test_optimization_simple_headways():
    """ test simple example with headways """
    # add train number are going one way and even the other way
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    objective_stations = ["MR", "CS"]
    p = Parameters(timetable, dmax = 5)
    r_input = Railway_input(p, objective_stations, delays = {3:2})
    v = Variables(r_input)
    example_problem = LinearPrograming(v, r_input, M = 10)
    bounds, integrality = example_problem.bonds_and_integrality()

    opt = linprog(c=example_problem.obj, A_ub=example_problem.lhs_ineq, 
                  b_ub=example_problem.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)

    example_problem.linprog2vars(opt)

    all_vars = ["t_PS_1", "t_MR_1", "t_CS_1", "t_MR_3", "t_CS_3"]
    arr_times = [0, 4, 17, 2, 15]

    for i, var in enumerate( all_vars ):
        assert example_problem.variables[var].value == arr_times[i]

    assert example_problem.compute_objective() == pytest.approx(1.2)


def test_optimization_simple_circ():
    """ test simple example with circulation """
    # add train number are going one way and even the other way
    objective_stations = ["A", "B"]
    timetable = {"A": {1:0, 2:8}, "B": {1:2 , 2:6}}
    par = Parameters(timetable, dmax = 4, headways = 1)
    r_input = Railway_input(par, objective_stations, delays = {1:1})
    r_input.circulation = {"B": (1,2)}
    v = Variables(r_input)
    example_problem = LinearPrograming(v, r_input, M = 10)

    bounds, integrality = example_problem.bonds_and_integrality()
    opt = linprog(c=example_problem.obj, A_ub=example_problem.lhs_ineq, 
                  b_ub=example_problem.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)

    example_problem.linprog2vars(opt)

    all_vars = ["t_A_1", "t_B_1", "t_B_2", "t_A_2"]
    arr_times = [1,3,7,9]

    for i, var in enumerate( all_vars ):
        assert example_problem.variables[var].value == arr_times[i]

    assert example_problem.compute_objective() == pytest.approx(1.0)



def test_optimization_larger_headways_circ():
    """ test simple example with headways """
    # add train number are going one way and even the other way
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0, 5:5, 4:30}, "CS" : {1: 16 , 3: 13, 4:17, 5:18}}
    objective_stations = ["MR", "CS"]
    p = Parameters(timetable, dmax = 2)
    r_input = Railway_input(p, objective_stations, delays = {3:2})
    r_input.circulation = {"CS": (3,4)}
    v = Variables(r_input)
    example_problem = LinearPrograming(v, r_input, M = 10)
    bounds, integrality = example_problem.bonds_and_integrality()

    opt = linprog(c=example_problem.obj, A_ub=example_problem.lhs_ineq, 
                  b_ub=example_problem.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)

    example_problem.linprog2vars(opt)

    all_vars = ["t_PS_1", "t_MR_1", "t_CS_1", "t_MR_3", "t_CS_3", "t_CS_4", "t_MR_4", "t_MR_5", "t_CS_5",
                "y_MR_1_3", "y_CS_1_3", "y_MR_1_5", "y_CS_1_5", "y_MR_3_5", "y_CS_3_5"]
    arr_times = [0, 4, 17, 2, 15, 19, 32, 6, 19, 0, 0, 1,1,1,1]

    for i, var in enumerate( all_vars ):
        assert example_problem.variables[var].value == arr_times[i]

    assert example_problem.compute_objective() == pytest.approx(6.0)

