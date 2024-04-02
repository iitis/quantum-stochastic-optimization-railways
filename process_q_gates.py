""" prepare inputs and analyze outputs from gate computing """
import pickle
import json
import argparse

from QTrains import Analyze_qubo
from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import analyze_QUBO_outputs, plot_hist_pass_obj
from QTrains import save_qubo_4gates_comp

from trains_timetable import Input_timetable, Comp_parameters



def gate_specifics_str(q_pars, trains_input, nolayers=1):
    """ assigns string of specifics of gate computers or its simulators """
    if q_pars.method == "IonQsim":
        if nolayers == 2:
            if trains_input.notrains == 1:
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

        if trains_input.notrains == 2:
            if q_pars.ppair == 2.0 and q_pars.psum == 4.0 and trains_input.delays == {}:
                return "summary.53."
            if q_pars.ppair == 20.0 and q_pars.psum == 40.0 and trains_input.delays == {}:
                return "summary.51."
            if q_pars.ppair == 2.0 and q_pars.psum == 4.0 and trains_input.delays != {}:
                return "summary.51."
        return "summary.50."

    if q_pars.method == "IonQreal":
        if nolayers == 2:
            return "2layers_"
        if nolayers == 1:
            return "1layer_"
    if q_pars.method == "IBMsim":
        return "summary.IBM.5."
    if q_pars.method == "IBMreal":
        return ""

    return ""


def get_files_dirs(trains_input, q_pars, data_file, nolayers):
    """returns the pair of the string to be replaced in the file reader for gates computing"""
    notrains = trains_input.notrains
    comp_specifics_string = gate_specifics_str(q_pars, trains_input, nolayers)
    if notrains == 1:
        trains_folder = "1train/"
    else:
        trains_folder =f"{notrains}trains/"

    replace_pair = (f"solutions/LR_timetable/{trains_folder}", f"{data_file}{comp_specifics_string}")
    replace_pairh = (trains_folder, f"{data_file}{trains_folder}{comp_specifics_string}")

    return replace_pair, replace_pairh



def read_aria_summary(args, our_key):

    datafile = args.datafile

    if args.nolayers == 1:
        file_comp = f"{datafile}expt.ionq-qpu-aria.all.json"
    elif args.nolayers == 2:
        file_comp = f"{datafile}expt.two-layers.ionq-qpu-aria.all.json"

    with open(file_comp) as f:
        expt_results = json.load(f)

    for result in expt_results:
        if result['qubo_name'] == our_key:
            return result
    return {}



def save_QUBO(trains_input, q_pars, lp_file, qubo_file, output_file):
    """ saves the QUBO in the file for given instance """
    with open(lp_file, 'rb') as fp:
        lp_sol = pickle.load(fp)

    with open(qubo_file, 'rb') as fp:
        dict_read = pickle.load(fp)

    Q = Analyze_qubo(dict_read)
    qubo_solution = Q.int_vars2qubo(lp_sol["variables"])
    ground_solutions = Q.heuristics_degenerate(qubo_solution, "PS")

    save_qubo_4gates_comp(dict_read, ground_solutions, output_file)

    results = analyze_QUBO_outputs(Q, trains_input.objective_stations, ground_solutions, lp_sol, q_pars.softern_pass)
    print("no qbits", results["no qubits"])
    print("objective optimal", results["lp objective"])



def analyze_and_plot_hists(args, trains_input, q_pars):
    """ analyze experiments outputs, save histograms as .json as well as plot histograms """
    replace_pair, replace_pairh = get_files_dirs(trains_input, q_pars, args.datafile, args.nolayers)

    file_comp = file_QUBO_comp(trains_input, q_pars)
    file_comp = file_comp.replace(replace_pair[0], replace_pair[1])
    file_h = file_hist(trains_input, q_pars)
    file_h = file_h.replace(replace_pairh[0], replace_pairh[1])

    if "IonQ" in args.datafile and "Aria" in args.datafile and "Experiments" in args.datafile:
        our_key = file_comp.replace(replace_pair[1], "")
        our_key = our_key.replace(".json", "")
        solutions_input = [read_aria_summary(args, our_key)]

    else:
        with open(file_comp, 'r') as fp:
            solutions_input = json.load(fp)


    file = file_LP_output(trains_input, q_pars)
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)

    file_q = file_QUBO(trains_input, q_pars)
    with open(file_q, 'rb') as fp:
        dict_read = pickle.load(fp)
    Q = Analyze_qubo(dict_read)

    solutions = [sol["vars"] for sol in solutions_input]

    results = analyze_QUBO_outputs(Q, trains_input.objective_stations, solutions, lp_sol, q_pars.softern_pass)

    with open(file_h, 'wb') as fp:
        pickle.dump(results, fp)

    file_temp = file_h.replace(".json", "_")
    file_pass = f"{file_temp}time_hists.pdf"
    file_obj = f"{file_temp}obj.pdf"

    plot_hist_pass_obj(trains_input, q_pars, file_h, file_pass, file_obj)


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

    trains_input = Input_timetable()
    q_pars = Comp_parameters()

    if "IonQ Simulations" in args.datafile:
        q_pars.method = "IonQsim"
    elif "IonQ Aria Experiments" in args.datafile:
        q_pars.method = "IonQreal"
    elif "IBM Simulations" in args.datafile:
        q_pars.method = "IBMsim"


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
                    trains_input.qubo_real_1t(delay)
                elif no_trains == 2:
                    trains_input.qubo_real_2t(delay)
                elif no_trains == 4:
                    trains_input.qubo_real_4t(delay)

                if args.savequbo:

                    lp_file = file_LP_output(trains_input, q_pars)
                    qubo_file = file_QUBO(trains_input, q_pars)
                    output_file = qubo_file.replace("LR_timetable/", "gates/")
                    save_QUBO(trains_input, q_pars, lp_file, qubo_file, output_file)
                else:
                    try:
                        analyze_and_plot_hists(args, trains_input, q_pars)
                    except:
                        print(f" does not work {q_pars.method}_notrains={trains_input.notrains}_ppair={q_pars.ppair}_psum={q_pars.psum}_dmax={q_pars.dmax}_delay={trains_input.delays}")
