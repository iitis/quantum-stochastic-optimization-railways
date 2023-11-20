from scipy.optimize import linprog
from QTrains import Parameters, Variables, LinearPrograming

def print_calculation(example_problem):
    bounds = [v.range for v in example_problem.variables.values()] 
    opt = linprog(c=example_problem.obj, A_ub=example_problem.lhs_ineq, b_ub=example_problem.rhs_ineq, bounds=bounds, method='highs')
    if opt.success:
        print("var.", "val.", "range", "...................")
        for count, variable in enumerate( example_problem.variables ):
            print(variable, opt["x"][count], example_problem.variables[variable].range)
        print("objective = ", opt["fun"] - example_problem.obj_ofset)
    else:
        print("var.", "range", "...................")
        print("solution not feasible")
        for count, variable in enumerate( example_problem.variables ):
            print(variable, example_problem.variables[variable].range)




if __name__ == "__main__":

    print("make tree")

    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    penalty_at = ["MR", "CS"]
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 16}, "CS" : {1: 0 , 3: 13}}
    tvar_range =  {"PS": {1: (0., 5.)}, "MR" :{1: (3.,8.), 3: (2.,5.)}, "CS" : {1: (16.,21.) , 3: (15., 18.)}}
    p = Parameters()
    p.headways = 2
    p.stay = 1
    p.pass_time = {f"PS_MR": 2, f"MR_CS": 12}

    v = Variables(trains_paths, penalty_at)    
    example_problem = LinearPrograming(v, timetable)
    example_problem.dmax = 5
    example_problem.M = 10
    example_problem.make_objective()
    example_problem.make_objective_ofset()
    example_problem.add_headways(p)
    example_problem.add_passing_times(p)
    example_problem.add_all_bounds(tvar_range)


    print("general LP")
    print_calculation(example_problem)

    example_problem.set_y_value(("MR", 1, 3), 1)
    print_calculation(example_problem)
    example_problem.set_y_value(("CS", 1, 3), 1)
    print_calculation(example_problem)
    example_problem.set_y_value(("CS", 1, 3), 0)
    print_calculation(example_problem)

    example_problem.reset_y_bonds(("CS", 1, 3))
    example_problem.set_y_value(("MR", 1, 3), 0)
    print_calculation(example_problem)
    example_problem.set_y_value(("CS", 1, 3), 1)
    print_calculation(example_problem)
    example_problem.set_y_value(("CS", 1, 3), 0)
    print_calculation(example_problem)




    print("Solve ILP by DOCPLEX")

    example_problem.reset_y_bonds(("CS", 1, 3))
    example_problem.reset_y_bonds(("MR", 1, 3))

    from docplex.mp.model import Model
    from docplex.mp.solution import SolveSolution

    model = Model(name='linear_programing_QTrains')


    lower_bounds = [v.range[0] for v in example_problem.variables.values()] 
    upper_bounds = [v.range[1] for v in example_problem.variables.values()] 

    variables = model.integer_var_dict(example_problem.variables.keys(), lb=lower_bounds, ub=upper_bounds, name=example_problem.variables.keys())

    for index, row in enumerate(example_problem.lhs_ineq):
        model.add_constraint(
            sum([variables[v.label]  * row[v.count] for v in example_problem.variables.values()]) <= example_problem.rhs_ineq[index])
    
    model.minimize(sum([variables[v.label] * example_problem.obj[v.count] for v in example_problem.variables.values()]))
    sol = model.solve()

    for var in model.iter_variables():
        print(var, sol.get_var_value(var))

    print(example_problem.obj_ofset)



    
