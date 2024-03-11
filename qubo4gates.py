""" prepare and analyze small qubos for gate computiong """
import pickle
import json
import matplotlib.pyplot as plt
import argparse

from QTrains import Analyze_qubo
from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import file_QUBO_comp, file_hist, file_QUBO, file_LP_output
from QTrains import analyze_QUBO_outputs, plot_hist_gates
from QTrains import save_qubo_4gates_comp

from trains_timetable import Input_qubo, Comp_parameters, Process_parameters



plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=10)



def gate_specifics_str(q_pars, input4qubo, nolayers=1):
    """ assigns string of specifics of gate computers or its simulators """
    if q_pars.method == "IonQsim":
        if nolayers == 2:
            if input4qubo.notrains == 1:
                if q_pars.ppair == 20.0 and q_pars.psum == 40.0 and q_pars.dmax == 4:
                    return "summary.two-layer.51."
                if q_pars.ppair == 2.0 and q_pars.psum == 4.0 and q_pars.dmax == 6:
                    return "summary.two-layer.51."
                if q_pars.ppair == 2.0 and q_pars.psum == 4.0 and q_pars.dmax == 2:
                    return "summary.two-layer.53."
                if q_pars.ppair == 20.0 and q_pars.psum == 40.0 and q_pars.dmax == 2:
                    return "summary.two-layer.53."
                if q_pars.ppair == 2.0 and q_pars.psum == 4.0 and q_pars.dmax == 4:
                    return "summary.two-layer.53."
            return "summary.two-layer.50."

        elif input4qubo.notrains == 2:
            if q_pars.ppair == 2.0 and q_pars.psum == 4.0 and input4qubo.delays == {}:
                return "summary.53."
            if q_pars.ppair == 20.0 and q_pars.psum == 40.0 and input4qubo.delays == {}:
                return "summary.51."
            if q_pars.ppair == 2.0 and q_pars.psum == 4.0 and input4qubo.delays != {}:
                return "summary.51."
            
        return "summary.50."
    
    if q_pars.method == "IonQreal":
        return ""
    if q_pars.method == "IBMsim":
        return "summary.IBM.5."
    if q_pars.method == "IBMreal":
        return ""


def get_files_dirs(input4qubo, q_pars, data_file, nolayers):
    """returns the pair of the string to be replaced in the file reader for gates computing"""
    notrains = input4qubo.notrains
    comp_specifics_string = gate_specifics_str(q_pars, input4qubo, nolayers)
    if notrains == 1:
        trains_folder = "1train/"
    else:
        trains_folder =f"{notrains}trains/"

    replace_pair = (f"solutions/LR_timetable/{trains_folder}", f"{data_file}{comp_specifics_string}")
    replace_pairh = (trains_folder, f"{data_file}{trains_folder}{comp_specifics_string}")
    
    return replace_pair, replace_pairh



def read_aria_summary(input4qubo, q_pars, p, datafile, replace_string):
    our_key = file_QUBO_comp(input4qubo, q_pars, p, (replace_string, ""))
    our_key = our_key.replace(".json", "")

    file_comp = f"{datafile}expt.ionq-qpu-aria.all.json"

    with open(file_comp) as f:
        expt_results = json.load(f)

    for result in expt_results:
        if result['qubo_name'] == our_key:
            return result
    return {}



def save_QUBO(input4qubo, q_pars, p):
    """ saves the QUBO in the file for given instance """
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
    results = analyze_QUBO_outputs(Q, input4qubo.objective_stations, ground_solutions, lp_sol, p.softern_pass)
    print("no qbits", results["no qubits"])
    print("objective optimal", results["lp objective"])
    


def analyze_and_plot_hists(args, input4qubo, q_pars, p):
    """ analyze experiments outputs, save histograms as .json as well as plot histograms """
    replace_pair, replace_pairh = get_files_dirs(input4qubo, q_pars, args.datafile, args.nolayers)

    file_comp = file_QUBO_comp(input4qubo, q_pars, p, replace_pair)  
    file_h = file_hist(input4qubo, q_pars, p, replace_pairh)

    if "IonQ Aria Experiments" in args.datafile:
        solutions_input = [read_aria_summary(input4qubo, q_pars, p, args.datafile, replace_pair[0])]

    else:

        with open(file_comp, 'r') as fp:
            solutions_input = json.load(fp)


    file = file_LP_output(input4qubo, q_pars, p)
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)
                    
    file_q = file_QUBO(input4qubo, q_pars, p)
    with open(file_q, 'rb') as fp:
        dict_read = pickle.load(fp)
    Q = Analyze_qubo(dict_read)

    solutions = [sol["vars"] for sol in solutions_input]
    print([sol["energy"] for sol in solutions_input])

    results = analyze_QUBO_outputs(Q, input4qubo.objective_stations, solutions, lp_sol, p.softern_pass)

    with open(file_h, 'wb') as fp:
        pickle.dump(results, fp)

    file_h = file_h.replace(".json", "_")
    file_pass = f"{file_h}time_hists.pdf"
    file_obj = f"{file_h}obj.pdf"            
    plot_hist_gates(q_pars, input4qubo, p, file_pass, file_obj, replace_pairh)


if __name__ == "__main__":


    parser = argparse.ArgumentParser("number of trains, mode of analysis")

    parser.add_argument(
        "--notrains",
        type=int,
        help="number of trains, 1,2,4 are supported",
        default=2,
    )

    parser.add_argument(
        "--savequbo",
        type=bool,
        help="if True prepare qubo else analyze outputs",
        default=False,
    )

    parser.add_argument(
        "--nolayers",
        type=int,
        help="number of layers of QAOA in analyzed data",
        default=1,
    )

    parser.add_argument(
        "--datafile",
        type =str,
        help = "file with data",
        default = "QAOA Results/IonQ Simulations/",
    )

    args = parser.parse_args()

    input4qubo = Input_qubo()
    q_pars = Comp_parameters()

    if "IonQ Simulations" in args.datafile:
        q_pars.method = "IonQsim"
    elif "IonQ Aria Experiments" in args.datafile:
        q_pars.method = "IonQreal"
    elif "IBM Simulations" in args.datafile:
        q_pars.method = "IBMsim"
    p = Process_parameters()

    
    no_trains = args.notrains
    if no_trains == 1:
        delays = [{}]
        all_dmax = [2,4,6]
    elif no_trains == 2:
        delays = [{}, {1:5, 2:2, 4:5}]
        all_dmax = [2] # TODO 3 can be added it there are these data 
    elif no_trains == 4:
        delays = [{}, {1:5, 2:2, 4:5}]
        all_dmax = [2]

    for delay in delays:
        for (q_pars.ppair, q_pars.psum) in [(2.0, 4.0), (20.0, 40.0)]:
            for q_pars.dmax in all_dmax:

                if no_trains == 1:
                    input4qubo.qubo_real_1t(delay)
                elif no_trains == 2:
                    input4qubo.qubo_real_2t(delay)
                elif no_trains == 4:
                    input4qubo.qubo_real_4t(delay)

                if args.savequbo:
                    save_QUBO(input4qubo, q_pars, p)
                else:
                    try:
                        analyze_and_plot_hists(args, input4qubo, q_pars, p)
                    except:
                        print(f" does not work {q_pars.method}_notrains={input4qubo.notrains}_ppair={q_pars.ppair}_psum={q_pars.psum}_dmax={q_pars.dmax}_delay={input4qubo.delays}")



            
