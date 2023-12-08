""" prepare and analyze small qubos for gate computiong """
import pickle
from QTrains import Analyze_qubo, update_hist
from solve_qubo import Input_qubo, Comp_parameters, file_QUBO, file_LP_output


def dsiplay_analysis(qubo, solution):
    "prints features of the solution"
    print("solution", solution)
    print("energy", qubo.energy(solution))
    print("objective", qubo.objective_val(solution))
    print("ofset", -qubo.sum_ofset)
    print(" ....... broken constrains   .......")
    print("broken (sum, headway, pass, circ)", qubo.count_broken_constrains(solution))
    print("broken MO", qubo.broken_MO_conditions(solution))


def save_qubo4gates(dict_qubo, qround_sol, file):
    "creates and seves file with ground oslution and small qubo for gate computing"
    our_qubo = Analyze_qubo(dict_qubo)
    qubo4gates = {}
    qubo4gates["qubo"] = dict_qubo["qubo"]
    qubo4gates["ground_solution"] = qround_sol
    qubo4gates["ground_energy"] = our_qubo.energy(qround_sol)
    new_file = file.replace("LR_timetable/", "gates/")
    with open(new_file, 'wb') as fp:
        pickle.dump(qubo4gates, fp)

q_input = Input_qubo()
q_pars = Comp_parameters()
q_pars.ppair = 2.0
q_pars.psum = 4.0
q_pars.dmax = 2
delays = {}
q_input.qubo_real_1t(delays)

file_q = file_QUBO(q_input, q_pars)
with open(file_q, 'rb') as fp:
    dict_read = pickle.load(fp)

print("qubo file", file_q)

file = file_LP_output(q_input, q_pars)
with open(file, 'rb') as fp:
    lp_sol = pickle.load(fp)

print("lp file", file)

qubo_smallest = Analyze_qubo(dict_read)
qround_solution = [1,0,0,1,0,0]

save_qubo4gates(dict_read, qround_solution, file_q)


dsiplay_analysis(qubo_smallest, qround_solution)


print(" more advances analysis for future")
# this makes the histogram of differences (lp ground vs qubo) of passing times between given stations
hist = list([])
qubo_objectives = list([])
feasible = update_hist(qubo_smallest, qround_solution, lp_sol["variables"], ["MR", "CS"], hist, qubo_objectives)
print("1 for feasible", feasible)
print(hist)
print(qubo_objectives)
