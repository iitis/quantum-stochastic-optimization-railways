""" computation of single problem, create the tree for B & B with int var relaxation """
from scipy.optimize import linprog
from QTrains import Parameters, Variables, LinearPrograming, Railway_input, make_ilp_docplex

def print_calculation_LP(prob):
    bounds = [(0,0) for _ in prob.variables]
    integrality = [1 for _ in prob.variables]
    for v in prob.variables.values():
        bounds[v.count] = v.range
        integrality[v.count] = int(v.type == int)

    opt = linprog(c=prob.obj, A_ub=prob.lhs_ineq, b_ub=prob.rhs_ineq, bounds=bounds, method='highs', integrality = integrality)
    if opt.success:
        print("var.", "val.", "range", "...................")
        for key in prob.variables.keys():
            variable  = prob.variables[key]
            print(key, opt["x"][variable.count], variable.range)
            variable.value = opt["x"][variable.count]
        print("objective", prob.compute_objective())
    else:
        print("var.", "range", "...................")
        print("solution not feasible")
        for variable in prob.variables:
            print(variable, prob.variables[variable].range)



if __name__ == "__main__":

    print("make tree")

    penalty_at = ["MR", "CS"]
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable, dmax = 5)
    i = Railway_input(p, penalty_at, delays = {3:2})
    r_var = Variables(i)

    example_problem = LinearPrograming(r_var, p, M = 10)
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

    model = make_ilp_docplex(example_problem)
    sol = model.solve()

    print("xxxxxxxxxxxxxxxxxx")

    for var in model.iter_variables():
        print(var, sol.get_var_value(var))

    for var in model.iter_variables():
        example_problem.variables[str(var)].value = sol.get_var_value(var)

    print ("objective", example_problem.compute_objective()  )
