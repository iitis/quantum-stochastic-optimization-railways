""" prepare and analyze small qubos for gate computiong """
import pickle
import os
import json
from QTrains import Analyze_qubo, update_hist
from solve_qubo import Input_qubo, Comp_parameters, Process_parameters, file_QUBO, file_LP_output, make_plots


def dsiplay_analysis(q_input, our_solution, lp_solution, timetable = False):
    "prints features of the solution"
    print( "..........  QUBO ........   " )
    print("qubo size=", len( q_input.qubo ), " number of Q-bits=", len( our_solution ))
    print("energy=", q_input.energy( our_solution ))
    print("energy + ofset=", q_input.energy( our_solution ) + q_input.sum_ofset)
    print("QUBO objective=", q_input.objective_val( our_solution ), "  ILP objective=", lp_solution["objective"] )

    print("broken (sum, headway, pass, circ)", q_input.count_broken_constrains( our_solution ))
    print("broken MO", q_input.broken_MO_conditions( our_solution ))

    if timetable:
        print(" ........ vars values  ........ ")
        print(" key, qubo, LP ")

        vq = q_input.qubo2int_vars( our_solution )
        for k, v in vq.items():
            print(k, v.value, lp_solution["variables"][k].value)
        print("  ..............................  ")


def save_qubo4gates(dict_qubo, qround_sol, input_file):
    "creates and seves file with ground oslution and small qubo for gate computing"
    our_qubo = Analyze_qubo(dict_qubo)
    qubo4gates = {}
    qubo4gates["qubo"] = dict_qubo["qubo"]
    qubo4gates["ground_solution"] = qround_sol
    qubo4gates["ground_energy"] = our_qubo.energy(qround_sol)
    new_file = input_file.replace("LR_timetable/", "gates/")
    with open(new_file, 'wb') as fp_w:
        pickle.dump(qubo4gates, fp_w)


def get_ground(case_no):
    """ returns ground state solution given case number """
    if case_no in [1, 5]:
        ground_solution = [1,0,0,1,0,0]
    if case in [-1, -5]:
        ground_solution = [1,0,0,0,1,0]
    if case_no in [2, 6]:
        ground_solution = [1,0,0,0,0,1,0,0,0,0]
    if case_no in [-2, -6]:
        ground_solution = [1,0,0,0,0,0,1,0,0,0]
    if case_no in [3, 7]:
        ground_solution = [1,0,0,0,0,0,0,1,0,0,0,0,0,0]
    if case_no in [-3, -7]:
        ground_solution = [1,0,0,0,0,0,0,0,1,0,0,0,0,0]
    if case_no in [4, 8]:
        ground_solution = [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0]
    if case_no in [9, 10]:
        ground_solution = [1,0,0,0,1,0,1,0,0,0,1,0,1,0,0,0,1,0]
    return ground_solution


def analyze_outputs(qubo_input, our_solutions, lp_solution, softern_constr):
    """  returns histogram of passing times between selected stations and objective """
    hist = list([])
    qubo_objectives = list([])
    for solution in our_solutions:
        dsiplay_analysis(qubo_input, solution, lp_solution)

        feasible = update_hist(qubo_input, solution, ["MR", "CS"], hist, qubo_objectives, softern_constr)
        print("feasible", bool(feasible))
        print(hist)
        print(qubo_objectives)
    return hist, qubo_objectives

def results_file_dir(d_folder, problem_case, small_sample, ionq_sim = True):
    """ rerurns string of the name and dir of file with results on gate computers or its simulators """
    if ionq_sim:
        if problem_case == 4:
            if small_sample:
                data_file = f"{d_folder}summary.ionq-sim-aria.qubo_2t_delays_no_2_2.0_4.0.json"
            else:
                data_file = f"{d_folder}summary.53.qubo_2t_delays_no_2_2.0_4.0.json"
        if problem_case == 8:
            if small_sample:
                data_file = f"{d_folder}summary.ionq-sim-aria.qubo_2t_delays_no_2_20.0_40.0.json"
            else:
                data_file = f"{d_folder}summary.51.qubo_2t_delays_no_2_20.0_40.0.json"
        if problem_case == 9:
            if small_sample:
                data_file = f"{d_folder}summary.ionq-sim-aria.qubo_2t_delays_124_525_2_2.0_4.0.json"
            else:
                data_file = f"{d_folder}summary.51.qubo_2t_delays_124_525_2_2.0_4.0.json"
        if problem_case == 10:
            if small_sample:
                data_file = f"{d_folder}summary.ionq-sim-aria.qubo_2t_delays_124_525_2_20.0_40.0.json"
            else:
                data_file = f"{d_folder}summary.50.qubo_2t_delays_124_525_2_20.0_40.0.json"
    else:
        data_file = ""
    return data_file

case = -6
save = True
small_sample_results = False


if __name__ == "__main__":

    assert case in [-7, -6, -5, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    input4qubo = Input_qubo()
    q_pars = Comp_parameters()
    if case in [-3, -2, -1, 1, 2, 3, 4, 9]:
        q_pars.ppair = 2.0
        q_pars.psum = 4.0
    if case in [-7, -6, -5, 5, 6, 7, 8, 10 ]:
        q_pars.ppair = 20.0
        q_pars.psum = 40.0

    if case in [-5, -1, 1, 4, 5, 8, 9, 10]:
        q_pars.dmax = 2
    if case in [-6, -2, 2, 6]:
        q_pars.dmax = 4
    if case in [-7, -3, 3, 7]:
        q_pars.dmax = 6

    if case in [-7, -6, -5, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8]:
        delays = {}
    if case in [9,10]:
        delays = {1:5, 2:2, 4:5}

    if case in [-7, -6, -5, -3, -2, -1, 1, 2, 3, 5, 6, 7]:
        input4qubo.qubo_real_1t(delays)
    if case in [4, 8,9,10]:
        input4qubo.qubo_real_2t(delays)


    p = Process_parameters()
    if case < 0:
        p.delta = 1

    file_q = file_QUBO(input4qubo, q_pars, p)
    with open(file_q, 'rb') as fp:
        dict_read = pickle.load(fp)

    print("qubo file", file_q)

    file = file_LP_output(input4qubo, q_pars, p)
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)

    print("lp file", file)

    if save:

        ground_state = get_ground(case)

        save_qubo4gates(dict_read, ground_state, file_q)

        solutions = [ground_state]

    else:
        folder = "solutions/LR_timetable/2trains_IonQSimulatorResults_18_Qubits/"
        print( os.path.isdir(folder) )
        data_f = results_file_dir(folder, case, small_sample_results)
        

        with open(data_f, 'r') as fp:
            solutions_input = json.load(fp)

        solutions = [sol["vars"] for sol in solutions_input]
        print([sol["energy"] for sol in solutions_input])


    Q = Analyze_qubo(dict_read)
    softern = False
    p_times, objs = analyze_outputs(Q, solutions, lp_sol, softern)
    print(objs)

    ground_sol = get_ground(case)
    ground = lp_sol["objective"]

    if not save:
        folder = folder.replace("solutions", "histograms")
        if softern:
            soft = "soft"
        else:
            soft = ""
        file_pass = f"{folder}pass_IonQsim{case}{soft}.pdf"
        file_obj = f"{folder}obj_IonQsim{case}{soft}.pdf"
        q_pars.method = "IonQsim"
        make_plots(p_times, objs, ground, q_pars, input4qubo, file_pass, file_obj)
