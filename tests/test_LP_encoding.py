from scipy.optimize import linprog


from QTrains import Variables, LinearPrograming, Parameters, Railway_input, make_ilp_docplex

def test_var_class():
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}} 
    objective_stations = ["MR", "CS"]

    p = Parameters(timetable, dmax = 5)
    i = Railway_input(p, objective_stations, delays = {3:2})
    v = Variables(i) 
    assert v.y_vars == ['y_MR_1_3', 'y_CS_1_3']
    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    assert v.trains_paths == trains_paths
    vars = {}
    v.add_t_vars(trains_paths, vars)
    assert list(vars.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3']

    v.add_y_vars_same_direction(i, vars)
    assert list(vars.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert v.indices_objective_vars(i) == [1,2,3,4]


def test_LP_class():
    
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}  
    objective_stations = ["MR", "CS"]
    p = Parameters(timetable, dmax = 5)
    i = Railway_input(p, objective_stations, delays = {3:2})
    v = Variables(i)
    
    assert v.variables['t_PS_1'].count == 0
    assert v.variables['t_PS_1'].type == int
    assert v.variables['t_CS_1'].count == 2
    assert v.variables['t_PS_1'].type == int
      
    example_problem = LinearPrograming(v, p)


    assert list(example_problem.variables.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert example_problem.penalty_vars == [1,2,3,4]
    
    assert example_problem.obj == [0.0, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0]
    assert example_problem.obj_ofset == 6.4


    example_problem.add_all_bounds()
    assert [v.range for v in example_problem.variables.values()]  == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 5.0), (15.0, 18.0), (0.0, 1.0), (0.0, 1.0)]
    example_problem.set_y_value(('MR', 1, 3), 1)
    assert [v.range for v in example_problem.variables.values()]  == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 5.0), (15.0, 18.0), (1,1), (0.0, 1.0)]
    example_problem.reset_y_bonds(('MR', 1, 3))
    assert [v.range for v in example_problem.variables.values()]  == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 5.0), (15.0, 18.0), (0.0, 1.0), (0.0, 1.0)]

    example_problem.relax_integer_req()
    assert example_problem.variables['t_PS_1'].type == float
    example_problem.restore_integer_req()
    assert example_problem.variables['t_PS_1'].type == int

def test_parametrised_constrains():
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}  
    objective_stations = ["MR", "CS"]

    p = Parameters(timetable, dmax = 5)
    input = Railway_input(p, objective_stations, delays = {2:3})
    v = Variables(input)
    
    example_problem = LinearPrograming(v, p, M = 10)
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
    input = Railway_input(par, objective_stations, delays = {1:1})
    input.circulation = {"B": (1,2)}
    v = Variables(input)
    assert v.trains_paths == {1: ["A", "B"], 2: ["B", "A"]}
    example_problem = LinearPrograming(v, par, M = 10)
    example_problem.lhs_ineq = []
    example_problem.rhs_ineq = []
    example_problem.add_circ_constrain(par, input)
    assert  example_problem.lhs_ineq  == [[0, 1, -1, 0]]  #TODO chck these
    assert example_problem.rhs_ineq == [-4]

    example_problem = LinearPrograming(v, par, M = 10)
    example_problem.add_circ_constrain(par, input)

    bounds = [(0,0) for _ in example_problem.variables]
    integrality = [1 for _ in example_problem.variables]
    for v in example_problem .variables.values():
        bounds[v.count] = v.range
        integrality[v.count] = int(v.type == int)

    opt = linprog(c=example_problem.obj, A_ub=example_problem.lhs_ineq, b_ub=example_problem.rhs_ineq, bounds=bounds, method='highs', integrality = integrality)


    print("var.", "val.", "range", "...................")

    for key in example_problem.variables.keys():
        variable  = example_problem.variables[key]
        variable.value = opt["x"][variable.count]

    variable  = example_problem.variables["t_A_1"]
    assert opt["x"][variable.count] == 1.0

    variable  = example_problem.variables["t_B_1"]
    assert opt["x"][variable.count] == 3.0

    variable  = example_problem.variables["t_B_2"]
    assert opt["x"][variable.count] == 7.0

    variable  = example_problem.variables["t_A_2"]
    assert opt["x"][variable.count] == 9.0

    assert example_problem.compute_objective() == 1.0






