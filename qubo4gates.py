""" prepare and analyze small qubos for gate computiong """
import pickle
import os
import json
from QTrains import Analyze_qubo, update_hist
from solve_qubo import Input_qubo, Comp_parameters, file_QUBO, file_LP_output, make_plots


def dsiplay_analysis(input, our_solution, lp_solution, timetable = False):
    "prints features of the solution"
    print( "..........  QUBO ........   " )
    print("qubo size=", len( input.qubo ), " number of Q-bits=", len( our_solution ))
    print("energy=", input.energy( our_solution ))
    print("energy + ofset=", input.energy( our_solution ) + input.sum_ofset)
    print("QUBO objective=", input.objective_val( our_solution ), "  ILP objective=", lp_solution["objective"] )

    print("broken (sum, headway, pass, circ)", input.count_broken_constrains( our_solution ))
    print("broken MO", input.broken_MO_conditions( our_solution ))

    if timetable:
        print(" ........ vars values  ........ ")
        print(" key, qubo, LP ")

        vq = input.qubo2int_vars( our_solution )
        for k, v in vq.items():
            print(k, v.value, lp_solution["variables"][k].value)
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


def analyze_outputs(input, our_solutions, lp_solution, softern_constr):
    """  returns histogram of passing times between selected stations and objective """
    hist = list([])
    qubo_objectives = list([])
    for solution in our_solutions:
        dsiplay_analysis(input, solution, lp_solution)

        feasible = update_hist(input, solution, ["MR", "CS"], hist, qubo_objectives, softern_constr)
        print("feasible", bool(feasible))
        print(hist)
        print(qubo_objectives)
    return hist, qubo_objectives

case = 8
assert case in [1,2,3,4,5,6,7,8, 9, 10]
save = False

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

    solutions = [solution]

else:
    folder = "solutions/LR_timetable/2trains_IonQSimulatorResults_18_Qubits/"
    print( os.path.isdir(folder) )
    if case == 4:
        data = f"{folder}summary.ionq-sim-aria.qubo_2t_delays_no_2_2.0_4.0.json"
    if case == 8:
        data = f"{folder}summary.ionq-sim-aria.qubo_2t_delays_no_2_20.0_40.0.json"
    if case == 9:
        data = f"{folder}summary.ionq-sim-aria.qubo_2t_delays_124_525_2_2.0_4.0.json"
    if case == 10:
        data = f"{folder}summary.ionq-sim-aria.qubo_2t_delays_124_525_2_20.0_40.0.json"

    with open(data, 'r') as fp:
        solutions_input = json.load(fp)

    solutions = [sol["vars"] for sol in solutions_input]
    print([sol["energy"] for sol in solutions_input])



our_qubo = Analyze_qubo(dict_read)
softern = False
p_times, objs = analyze_outputs(our_qubo, solutions, lp_sol, softern)
print(objs)

ground_sol = get_ground(case)
ground = lp_sol["objective"]
folder = folder.replace("solutions", "histograms")
if softern:
    soft = "soft"
else:
    soft = ""
file_pass = f"{folder}pass_IonQsim{case}{soft}.pdf"
file_obj = f"{folder}obj_IonQsim{case}{soft}.pdf"
q_pars.method = "IonQsim"
make_plots(p_times, objs, ground, q_pars, q_input, file_pass, file_obj)
