""" computation of single problem, create the tree for B & B with int var relaxation """
from scipy.optimize import linprog
from QTrains import Parameters, Variables, LinearPrograming, Railway_input, make_ilp_docplex

def print_calculation_LP(prob):
    "make the LP / ILP optimisation and print results"
    bounds, integrality = prob.bonds_and_integrality()
    opt = linprog(c=prob.obj, A_ub=prob.lhs_ineq, b_ub=prob.rhs_ineq, 
                  bounds=bounds, method='highs', integrality = integrality)
    if opt.success:
        prob.linprog2vars(opt)
        for var in prob.variables.values():
            print(var.label, var.value, var.range)
        print("objective", prob.compute_objective())
    else:
        print("!!!! NOT FEASIBLE !!!!!")



if __name__ == "__main__":
    print("make tree")
    penalty_at = ["MR", "CS"]
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable, dmax = 5)
    i = Railway_input(p, penalty_at, delays = {3:2})
    r_var = Variables(i)
    example_problem = LinearPrograming(r_var, i, M = 10)
   
    print("general LP")
    example_problem.relax_integer_req()
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


    print("xxxx Solve ILP by DOCPLEX  xxxxxx")

    example_problem = LinearPrograming(r_var, i, M = 10)

    model = make_ilp_docplex(example_problem)
    sol = model.solve()
    example_problem.docplex2vars(model, sol)

    for var in example_problem.variables.values():
        print(var.label, var.value, var.range)
    print ("objective", example_problem.compute_objective()  )
