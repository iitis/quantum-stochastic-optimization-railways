from scipy.optimize import linprog
from docplex.mp.model import Model
from docplex.mp.solution import SolveSolution
from QTrains import Parameters, Variables, LinearPrograming

def print_calculation_LP(prob):
    bounds = [(0,0) for _ in prob.variables]
    integrality = [1 for _ in prob.variables]
    for v in prob.variables.values():
        bounds[v.count] = v.range
        integrality[v.count] = int(v.type == int)

    opt = linprog(c=prob.obj, A_ub=prob.lhs_ineq, b_ub=prob.rhs_ineq, bounds=bounds, method='highs', integrality = integrality)
    if opt.success:
        print("var.", "val.", "range", "...................")
        for count, variable in enumerate( prob.variables ):
            print(variable, opt["x"][count], prob.variables[variable].range)
        print("objective = ", opt["fun"] - prob.obj_ofset)
    else:
        print("var.", "range", "...................")
        print("solution not feasible")
        for count, variable in enumerate( prob.variables ):
            print(variable, prob.variables[variable].range)



def make_ILP_DOCPLEX(prob):
    model = Model(name='linear_programing_QTrains')

    lower_bounds = [0 for _ in prob.variables]
    upper_bounds = [0 for _ in prob.variables]

    for v in prob.variables.values():
        lower_bounds[v.count] = v.range[0]
        upper_bounds[v.count] = v.range[1] 

    variables = model.integer_var_dict(prob.variables.keys(), lb=lower_bounds, ub=upper_bounds, name=prob.variables.keys())

    for index, row in enumerate(prob.lhs_ineq):
        model.add_constraint(
            sum([variables[v.label]  * row[v.count] for v in prob.variables.values()]) <= prob.rhs_ineq[index])
     
    for index, row in enumerate(prob.lhs_eq):
        model.add_constraint(
            sum([variables[v.label]  * row[v.count] for v in prob.variables.values()]) == prob.rhs_eq[index])
    
    model.minimize(sum([variables[v.label] * prob.obj[v.count] for v in prob.variables.values()]))

    return model


if __name__ == "__main__":

    print("make tree")

    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    penalty_at = ["MR", "CS"]
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}} 
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
    example_problem.relax_integer_req()
    

    print("general LP")

    print_calculation_LP(example_problem)

    example_problem.set_y_value(("MR", 1, 3), 1)
    print_calculation_LP(example_problem)
    example_problem.set_y_value(("CS", 1, 3), 1)
    print_calculation_LP(example_problem)
    example_problem.set_y_value(("CS", 1, 3), 0)
    print_calculation_LP(example_problem)

    example_problem.reset_y_bonds(("CS", 1, 3))
    example_problem.set_y_value(("MR", 1, 3), 0)
    print_calculation_LP(example_problem)
    example_problem.set_y_value(("CS", 1, 3), 1)
    print_calculation_LP(example_problem)
    example_problem.set_y_value(("CS", 1, 3), 0)
    print_calculation_LP(example_problem)




    print("Solve ILP by DOCPLEX")

    example_problem.restore_integer_req()
    example_problem.reset_y_bonds(("CS", 1, 3))
    example_problem.reset_y_bonds(("MR", 1, 3))

    model = make_ILP_DOCPLEX(example_problem)


    sol = model.solve()

    print(example_problem.obj_ofset)
    print(sol)
    
    
    for var in model.iter_variables():
        print(var, sol.get_var_value(var))

    



    
