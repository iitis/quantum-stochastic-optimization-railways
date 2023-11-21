from QTrains import Variables, LinearPrograming, Parameters

def test_var_class():
    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    penalty_at = ["MR", "CS"]
    v = Variables(trains_paths, penalty_at) 
    assert v.y_vars == ['y_MR_1_3', 'y_CS_1_3']
    assert v.trains_paths == trains_paths
    vars = {}
    v.make_t_vars(trains_paths, vars)
    assert list(vars.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3']
    vars = {}
    v.make_y_vars_same_direction(trains_paths, vars)
    assert list(vars.keys()) == ['y_MR_1_3', 'y_CS_1_3']
    assert v.make_penalty_vars(trains_paths, penalty_at) == [1,2,3,4]


def test_LP_class():
    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    penalty_at = ["MR", "CS"]
    v = Variables(trains_paths, penalty_at)
    assert v.variables['t_PS_1'].count == 0
    assert v.variables['t_PS_1'].type == int
    assert v.variables['t_CS_1'].count == 2
    assert v.variables['t_PS_1'].type == int
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 16}, "CS" : {1: 0 , 3: 13}}    
    example_problem = LinearPrograming(v, timetable)
    assert example_problem.timetable == timetable
    assert example_problem.trains_paths == trains_paths
    assert list(example_problem.variables.keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert example_problem.penalty_vars == [1,2,3,4]
    example_problem.dmax = 5
    example_problem.make_objective()
    assert example_problem.obj == [0.0, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0]
    example_problem.make_objective_ofset()
    assert example_problem.obj_ofset == 6.4
    tvar_range =  {"PS": {1: (0., 5.)}, "MR" :{1: (3.,8.), 3: (2.,5.)}, "CS" : {1: (16.,21.) , 3: (15., 18.)}}
    example_problem.add_all_bounds(tvar_range)
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
    p = Parameters()
    p.headways = 2
    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    penalty_at = ["MR", "CS"]
    v = Variables(trains_paths, penalty_at)
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 16}, "CS" : {1: 0 , 3: 13}} 
    example_problem = LinearPrograming(v, timetable)
    example_problem.add_headways(p)
    assert example_problem.lhs_ineq == [[0, 1, 0, -1, 0, 0, 0], [0, -1, 0, 1, 0, 0, 0], [0, 0, 1, 0, -1, 0, 0], [0, 0, -1, 0, 1, 0, 0]]
    assert example_problem.rhs_ineq == [-2, -2, -2, -2]
    tvar_range =  {"PS": {1: (0., 5.)}, "MR" :{1: (3.,8.), 3: (2.,5.)}, "CS" : {1: (16.,21.) , 3: (15., 18.)}}
    example_problem.add_all_bounds(tvar_range)
    assert example_problem.variables["t_MR_1"].range == (3,8)

    p = Parameters()
    p.stay = 1
    p.pass_time = {f"PS_MR": 2, f"MR_CS": 12}
    example_problem = LinearPrograming(v, timetable)
    example_problem.add_passing_times(p)
    assert example_problem.lhs_ineq  == [[1, -1, 0, 0, 0, 0, 0], [0, 1, -1, 0, 0, 0, 0], [0, 0, 0, 1, -1, 0, 0]]
    assert example_problem.rhs_ineq == [-3, -13, -13]

