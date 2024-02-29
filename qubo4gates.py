""" prepare and analyze small qubos for gate computiong """
import pickle
import json
import matplotlib.pyplot as plt

from QTrains import Analyze_qubo
from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import file_QUBO_comp, file_hist, file_QUBO, file_LP_output
from QTrains import analyze_QUBO_outputs, plot_hist_gates
from QTrains import save_qubo_4gates_comp
from trains_timetable import Input_qubo

from solve_qubo import Comp_parameters, Process_parameters



plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=10)


    

def gate_specifics(small_sample, q_pars, input4qubo):
    """ assigns string of specifics of gate computers or its simulators """
    if q_pars.method == "IonQsim":
        if small_sample:
            return "summary.ionq-sim-aria."
        else:
            if q_pars.ppair == 2.0 and q_pars.psum == 4.0 and input4qubo.delays == {}:
                return "summary.53."
            if q_pars.ppair == 20.0 and q_pars.psum == 40.0 and input4qubo.delays == {}:
                return "summary.51."
            if q_pars.ppair == 2.0 and q_pars.psum == 4.0 and input4qubo.delays != {}:
                return "summary.51."
            if q_pars.ppair == 20.0 and q_pars.psum == 40.0 and input4qubo.delays != {}:
                return "summary.50."


def save_QUBO(input4qubo, q_pars, p):
    file = file_LP_output(input4qubo, q_pars, p)
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)
            
    file_q = file_QUBO(input4qubo, q_pars, p)
    print(file_q)
    with open(file_q, 'rb') as fp:
        dict_read = pickle.load(fp)

    Q = Analyze_qubo(dict_read)
    qubo_solution = Q.int_vars2qubo(lp_sol["variables"])
    ground_solutions = Q.heuristics_degenerate(qubo_solution, "PS")
    save_qubo_4gates_comp(dict_read, ground_solutions, file_q)
    _ = analyze_QUBO_outputs(Q, input4qubo.objective_stations, ground_solutions, lp_sol, p.softern_pass)
    


def analyze_and_plot_hists(small_sample, input4qubo, q_pars, p):
    comp_specifics_string = gate_specifics(small_sample, q_pars, input4qubo)
    replace_pair = ("2trains/", f"2trains_IonQSimulatorResults_18_Qubits/{comp_specifics_string}")
    file_comp = file_QUBO_comp(input4qubo, q_pars, p, replace_pair)  
    file_h = file_hist(input4qubo, q_pars, p, replace_pair)

    with open(file_comp, 'r') as fp:
        solutions_input = json.load(fp)

    file = file_LP_output(input4qubo, q_pars, p)
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)
            
    file_q = file_QUBO(input4qubo, q_pars, p)
    print(file_q)
    with open(file_q, 'rb') as fp:
        dict_read = pickle.load(fp)
    Q = Analyze_qubo(dict_read)

    solutions = [sol["vars"] for sol in solutions_input]
    print([sol["energy"] for sol in solutions_input])

    results = analyze_QUBO_outputs(Q, input4qubo.objective_stations, solutions, lp_sol, p.softern_pass)

    with open(file_h, 'wb') as fp:
        pickle.dump(results, fp)

    file_pass = f"{file_h}time_hists.pdf"
    file_obj = f"{file_h}obj.pdf"            
    plot_hist_gates(q_pars, input4qubo, p, file_pass, file_obj, replace_pair)


if __name__ == "__main__":

    input4qubo = Input_qubo()
    q_pars = Comp_parameters()
    q_pars.method = "IonQsim"
    q_pars.dmax = 2
    p = Process_parameters()
    p.softern_pass = False

    # these are tunable
    small_sample = False
    save_qubo = False
    no_trains = 2

    for delays in ({}, {1:5, 2:2, 4:5}):
        for (q_pars.ppair, q_pars.psum) in [(2.0, 4.0), (20.0, 40.0)]:

            if no_trains == 1:
                input4qubo.qubo_real_1t(delays)
            else:
                input4qubo.qubo_real_2t(delays)

            if save_qubo:
                save_QUBO(input4qubo, q_pars, p)
            else:
                analyze_and_plot_hists(small_sample, input4qubo, q_pars, p)

            
