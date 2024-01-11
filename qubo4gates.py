""" prepare and analyze small qubos for gate computiong """
import pickle
from QTrains import Analyze_qubo, update_hist
from solve_qubo import Input_qubo, Comp_parameters, file_QUBO, file_LP_output


def dsiplay_analysis(qubo, solution, lp_sol):
    "prints features of the solution"
    print( "..........  QUBO ........   " )
    print("qubo size", len( qubo.qubo ) )
    print("number of Q-bits", len( solution ))
    print("energy", qubo.energy(solution))
    print("ofset", qubo.sum_ofset)
    print("objective", qubo.objective_val(solution))
    
    print("LP objective", lp_sol["objective"] )
    print(" ....... broken constrains   .......")
    print("broken (sum, headway, pass, circ)", qubo.count_broken_constrains(solution))
    print("broken MO", qubo.broken_MO_conditions(solution))

    print(" ........ vars values  ........ ")
    print(" key, qubo, LP ")

    vq = our_qubo.qubo2int_vars(solution)
    for k, v in vq.items():
        print(k, v.value, lp_sol["variables"][k].value)
    print("  ..............................  ")


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


def get_ground(case):
    if case in [1, 5]:
        solution = [1,0,0,1,0,0]
    if case in [2, 6]:
        solution = [1,0,0,0,0,1,0,0,0,0]
    if case in [3, 7]:
        solution = [1,0,0,0,0,0,0,1,0,0,0,0,0,0]
    if case in [4, 8]:
        solution = [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0]
    if case in [9, 10]:
        solution = [1,0,0,0,1,0,1,0,0,0,1,0,1,0,0,0,1,0]
    return solution


def analyze_outputs(our_qubo, solution, lp_sol):
    hist = list([])
    qubo_objectives = list([])
    for solution in solutions:
        dsiplay_analysis(our_qubo, solution, lp_sol)

        feasible = update_hist(our_qubo, solution, ["MR", "CS"], hist, qubo_objectives)
        print("1 for feasible", feasible)
        print(hist)
        print(qubo_objectives)

case = 9
assert case in [1,2,3,4,5,6,7,8, 9, 10]
save = True

q_input = Input_qubo()
q_pars = Comp_parameters()
if case in [1,2,3,4, 9]:
    q_pars.ppair = 2.0
    q_pars.psum = 4.0
if case in [5,6,7,8, 10]:
    q_pars.ppair = 20.0
    q_pars.psum = 40.0

if case in [1, 4, 5, 8,9,10]:
    q_pars.dmax = 2
if case in [2, 6]:
    q_pars.dmax = 4
if case in [3, 7]:
    q_pars.dmax = 6

if case in [1,2,3,4,5,6,7,8]:
    delays = {}
if case in [9,10]:
    delays = {1:5, 2:2, 4:5}

if case in [1,2,3,5,6,7]:
    q_input.qubo_real_1t(delays)
if case in [4, 8,9,10]:
    q_input.qubo_real_2t(delays)

file_q = file_QUBO(q_input, q_pars)
with open(file_q, 'rb') as fp:
    dict_read = pickle.load(fp)

print("qubo file", file_q)

file = file_LP_output(q_input, q_pars)
with open(file, 'rb') as fp:
    lp_sol = pickle.load(fp)

print("lp file", file)

if save:

    solution = get_ground(case)

    save_qubo4gates(dict_read, solution, file_q)


our_qubo = Analyze_qubo(dict_read)
solutions = [solution]

analyze_outputs(our_qubo, solutions, lp_sol)


