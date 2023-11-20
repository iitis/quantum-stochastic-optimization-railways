from scipy.optimize import linprog
from QTrains import Parameters, Variables, LinearPrograming

def print_calculation(our_problem):
    bounds = [v.range for v in our_problem.variables.values()] 
    opt = linprog(c=our_problem.obj, A_ub=our_problem.lhs_ineq, b_ub=our_problem.rhs_ineq, bounds=bounds, method='highs')
    if opt.success:
        print("var.", "val.", "range", "...................")
        for count, variable in enumerate( our_problem.variables ):
            print(variable, opt["x"][count], our_problem.variables[variable].range)
        print("objective = ", opt["fun"] - our_problem.obj_ofset)
    else:
        print("var.", "range", "...................")
        print("solution not feasible")
        for count, variable in enumerate( our_problem.variables ):
            print(variable, our_problem.variables[variable].range)




if __name__ == "__main__":

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
