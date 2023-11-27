""" computation of single problem, create the tree for B & B with int var relaxation """
from scipy.optimize import linprog
from QTrains import Parameters, Variables, LinearPrograming, Railway_input, make_ilp_docplex

def print_calculation_LP(r_var, i, prob):
    "make the LP / ILP optimisation and print results"
    bounds, integrality = r_var.bonds_and_integrality()
    opt = linprog(c=prob.obj, A_ub=prob.lhs_ineq, b_ub=prob.rhs_ineq, 
                  bounds=bounds, method='highs', integrality = integrality)
    if opt.success:
        r_var.linprog2vars(opt)
        for var in r_var.variables.values():
            print(var.str_id, var.value, var.range)
        print(" xxxxxxxxxxxxx  objective =  ", prob.compute_objective(r_var, i))
    else:
        print("!!!! NOT FEASIBLE !!!!!")



if __name__ == "__main__":
    print("make tree")
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    p = Parameters(timetable, dmax = 5)

    objective_stations = ["MR", "CS"]
    i = Railway_input(p, objective_stations, delays = {3:2})
    r_var = Variables(i)
    problem = LinearPrograming(r_var, i, M = 10)
   
    print("general LP")
    r_var.relax_integer_req()
    print_calculation_LP(r_var, i,problem)

    r_var.set_y_value(("MR", 1, 3), 1)
    print_calculation_LP(r_var, i,problem)

    r_var.set_y_value(("CS", 1, 3), 1)
    print_calculation_LP(r_var, i,problem)

    r_var.set_y_value(("CS", 1, 3), 0)
    print_calculation_LP(r_var, i,problem)

    r_var.reset_y_bonds(("CS", 1, 3))
    r_var.set_y_value(("MR", 1, 3), 0)
    print_calculation_LP(r_var, i,problem)

    r_var.set_y_value(("CS", 1, 3), 1)
    print_calculation_LP(r_var, i,problem)

    r_var.set_y_value(("CS", 1, 3), 0)
    print_calculation_LP(r_var, i,problem)


    print("xxxx Solve ILP by DOCPLEX  xxxxxx")

    r_var = Variables(i)
    problem = LinearPrograming(r_var, i, M = 10)

    model = make_ilp_docplex(problem, r_var)
    sol = model.solve()
    r_var.docplex2vars(model, sol)

    for var in r_var.variables.values():
        print(var.str_id, var.value, var.range)
    print ("objective", problem.compute_objective(r_var, i)  )
