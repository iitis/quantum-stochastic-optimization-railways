""" saves data in .csv files for plots """
import pickle
import csv
import numpy as np

from QTrains import high_excited_state
from QTrains import plot_title, file_hist, objective_histograms, energies_histograms, passing_time_histigrams, train_path_data
from QTrains import get_solutions_from_dmode, best_feasible_state
from QTrains import file_QUBO_comp, file_QUBO, file_LP_output
from QTrains import Analyze_qubo
from trains_timetable import Input_timetable, Comp_parameters

from process_q_gates import get_files_dirs




def csv_write_hist(file_name, hist, key1 = "value", key2 = "count"):
    """ 
    write histogram to csv 

    input:
    - file_name: string - csv file name
    - hist: dict - containing histogram
    - key1: string - key for value in histogram
    - key2: string - key for counts in histogram
    """
    with open(file_name, 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = [key1, key2]
        value = hist[key1]
        count = hist[key2]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(value):
            writer.writerow({key1: v, key2: count[i]})



def file4csv(trains_input, q_par, layers = 1):
    """
    returns string, the file name (and dir) for the cvs file
    input:
    - trains_input - object of Input_timetable class
    - q_par - object of Comp_parameters class
    """
    write_file = file_hist(trains_input, q_par)
    write_file = write_file.replace("histograms/LR_timetable/", "article_plots/")
    write_file = write_file.replace("histograms_soft/LR_timetable/", "article_plots/")
    if q_par.method == "real":
        write_file = write_file.replace(".json", ".csv")
    else:
        write_file = write_file.replace(".json", f"_{q_par.method}_{layers}layers.csv")
    return write_file


############# DWave #########


def dWave_hist(no_trains = 2, dmax = 2, at = 10, soft = False):
    """
    write csv files of analysis of dWave outputs for given instance size and parameters:

    input:
    - no_trains: int
    - dmax: int,
    - at: int (annealing time)
    - soft: bool - if True does not check minimal passing time constrain for feasibility check
    """

    trains_input = Input_timetable()
    q_par = Comp_parameters()

    q_par.method = "real"
    q_par.dmax = dmax
    q_par.annealing_time = at
    q_par.softern_pass = soft

    delays_list = [{}, {1:5, 2:2, 4:5}]

    for delays in delays_list:

        for (ppair, psum) in [(2.0, 4.0), (20.0, 40.0)]:

            q_par.ppair = ppair
            q_par.psum = psum

            if no_trains == 2:
                trains_input.qubo_real_2t(delays)
            if no_trains == 11:
                trains_input.qubo_real_11t(delays)

            file_h = file_hist(trains_input, q_par)
            hist = passing_time_histigrams(trains_input, q_par, file_h)
            write_file = file4csv(trains_input, q_par, file_h)
            csv_write_hist(write_file, hist)

            hist = objective_histograms(file_h)
            write_file = write_file.replace("qubo", "objective")
            csv_write_hist(write_file, hist)

            our_title = plot_title(trains_input, q_par)
            print(our_title, f"soft{soft}")

            energies = energies_histograms(file_h)
            write_file = write_file.replace("objective", "energies/energies_feasible")
            csv_write_hist(write_file, energies, key1 = "feasible_value", key2 = "feasible_count")
            write_file = write_file.replace("energies/energies_feasible", "energies/energies_notfeasible")
            csv_write_hist(write_file, energies, key1 = "notfeasible_value", key2 = "notfeasible_count")


def series_DWave_hist():
    """
    performs series of computations concerning DWave 
    saves series of csv files
    """
    dWave_hist(no_trains = 2, at = 10, dmax = 2)
    dWave_hist(no_trains = 2, at = 1000, dmax = 2)
    dWave_hist(no_trains = 11, dmax = 2)
    dWave_hist(no_trains = 11, at = 10, dmax = 6)
    dWave_hist(no_trains = 11, at = 1000, dmax = 6)

    dWave_hist(no_trains = 11, dmax = 6, at = 10, soft = True)
    dWave_hist(no_trains = 11, dmax = 6, at = 1000, soft = True)


#########################  Scaling ####################

def add_elemet(trains_input, q_par, no_qubits, no_physical_qbits, no_qubo_terms, feasibility_perc):
    """
    updates following lists:
    no_qubits, no_qubo_terms, feasibility_perc, no_physical_qbits

    for instance determined by
    - trains_input - object of Input_timetable class
    - q_par - object of Comp_parameters class
    """

    file = file_hist(trains_input, q_par)
    with open(file, 'rb') as fp:
        res_dict = pickle.load(fp)

    no_qubits.append(res_dict["no qubits"])
    no_qubo_terms.append(res_dict["no qubo terms"])
    feasibility_perc.append(res_dict["perc feasible"])

    with open("solutions/embedding.json", 'rb') as fp:
        embeddinq_dict = pickle.load(fp)

    if trains_input.delays == {}:
        disturbed = "notdisturbed"
    else:
        disturbed = "disturbed"

    phys_qbits = embeddinq_dict[f"{trains_input.notrains}_{q_par.dmax}_{disturbed}"]

    assert phys_qbits['no_logical'] == res_dict["no qubits"]

    no_physical_qbits.append(phys_qbits['no_physical'])


def log_linear_fit(x, y, rmax):
    """
    fites line to log(y) = ax + b
    then extrapoltation the fit to range rmax
    returns 2 arrays of such extrapolation: x_lin, y_lin
    """

    x_lin = list(range(0,rmax, 50))
    if rmax > 0:
        if 0 in y:
            x = x[0:-1]
            y = y[0:-1]
        a, b = np.polyfit(x, np.log(y), 1)

    y_lin = np.exp(a*np.array(x_lin)+b)

    return x_lin, y_lin


def DWave_series(q_par, delays, rmax):
    """
    returns a dict, of the output of DWave
    "no_qubits" - list of the sizes of problems (logical qubits)
    "no_physical" - list of the sizes of problems (physical qubits)
    "no_qubo_terms"  - qubo size (n.o. terms / couplings)
    "feasibility_perc" - pergentage of feasibility form DWave solutions
    "x_lin"
    "y_lin"  - linear fit to feasibility percentage vs. number of physical q-bits
    """
    no_qubits = []
    no_physical_qubits = []
    no_qubo_terms = []
    feasibility_perc = []

    for d in [2,6]:
        q_par.dmax = d
        trains_input = Input_timetable()
        trains_input.qubo_real_1t(delays)
        add_elemet(trains_input, q_par, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        trains_input = Input_timetable()
        trains_input.qubo_real_2t(delays)
        add_elemet(trains_input, q_par, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        trains_input = Input_timetable()
        trains_input.qubo_real_4t(delays)
        add_elemet(trains_input, q_par, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        trains_input = Input_timetable()
        trains_input.qubo_real_6t(delays)
        add_elemet(trains_input, q_par, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        trains_input = Input_timetable()
        trains_input.qubo_real_8t(delays)
        add_elemet(trains_input, q_par, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        trains_input = Input_timetable()
        trains_input.qubo_real_10t(delays)
        add_elemet(trains_input, q_par, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        trains_input = Input_timetable()
        trains_input.qubo_real_11t(delays)
        add_elemet(trains_input, q_par, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        trains_input = Input_timetable()
        trains_input.qubo_real_12t(delays)
        add_elemet(trains_input, q_par, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)

    x_lin, y_lin = log_linear_fit(no_physical_qubits, feasibility_perc, rmax)

    d = {"no_qubits":no_qubits, "no_physical":no_physical_qubits, "no_qubo_terms":no_qubo_terms, "feasibility_perc":feasibility_perc, "x_lin":x_lin, "y_lin":y_lin}
    return d


def csv_file_scaling(q_par, delay):
    """ returns strings: names and directories for 3 files (real data, linear fit, linear extrapolation)
    where results of scaling of number of q-bits and feasibility percentage will be saved 
    """
    if delay == {}:
        disturbed = "no"
    else:
        disturbed = "disturbed"
    file = f"article_plots/scaling/qubo{q_par.annealing_time}_{q_par.ppair}_{q_par.psum}_{disturbed}.csv"
    file_fit = f"article_plots/scaling/fitsmall{q_par.annealing_time}_{q_par.ppair}_{q_par.psum}_{disturbed}.csv"
    file_extrapolation = f"article_plots/scaling/fit{q_par.annealing_time}_{q_par.ppair}_{q_par.psum}_{disturbed}.csv"

    return file, file_fit, file_extrapolation



def csv_write_scaling(file, file_fit, file_extrapolation, d):
    """
    write to .csv a result for single instance on DWave scalling: 
    feasibility percentage vs. number of physical q-bits.
    In particular:
        - actual data
        - linear fit and extrapolation
    """
    with open(file, 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ["size", "perc"]
        size = d["no_physical"]
        perc = d["feasibility_perc"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(size):
            writer.writerow({'size': v, 'perc': perc[i]})
    with open(file_fit, 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ["x_lin", "y_lin"]
        size = d["x_lin"][0:11]
        perc = d["y_lin"][0:11]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(size):
            writer.writerow({'x_lin': v, 'y_lin': perc[i]})
    with open(file_extrapolation, 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ["x_lin", "y_lin"]
        size = d["x_lin"]
        perc = d["y_lin"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(size):
            writer.writerow({'x_lin': v, 'y_lin': perc[i]})


def feasibility_percentage():
    """
    saves to .csv results from the series of instances on DWave scalling: 
    feasibility percentage vs. number of physical q-bits.
    """
    q_par = Comp_parameters()
    q_par.method = "real"
    delays_list = [{}, {1:5, 2:2, 4:5}]
    rmax = 150_000

    print("feasibility percentage")

    q_par.annealing_time = 10

    q_par.ppair = 2.0
    q_par.psum = 4.0

    delay = delays_list[0]
    d = DWave_series(q_par, delay, rmax)
    file, file_fit, file_e = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit, file_e, d)

    delay = delays_list[1]
    d = DWave_series(q_par, delay, rmax)
    file, file_fit, file_e = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit, file_e, d)

    q_par.ppair = 20.0
    q_par.psum = 40.0

    delay = delays_list[0]
    d = DWave_series(q_par, delay, rmax)
    file, file_fit, file_e = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit, file_e, d)

    delay = delays_list[1]
    d = DWave_series(q_par, delay, rmax)
    file, file_fit, file_e = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit, file_e, d)

    q_par.annealing_time = 1000

    q_par.ppair = 2.0
    q_par.psum = 4.0

    delay = delays_list[0]
    d = DWave_series(q_par, delay, rmax)
    file, file_fit, file_e = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit, file_e, d)

    delay = delays_list[1]
    d = DWave_series(q_par, delay, rmax)
    file, file_fit, file_e = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit, file_e, d)

    q_par.ppair = 20.0
    q_par.psum = 40.0

    delay = delays_list[0]
    d = DWave_series(q_par, delay, rmax)
    file, file_fit, file_e = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit, file_e, d)

    delay = delays_list[1]
    d = DWave_series(q_par, delay, rmax)
    file, file_fit, file_e = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit, file_e, d)

    print("..........................................")


def csv_write_embedding(embeddinq_dict, q_par, delay):
    """
    write to .csv the number of logical and physical (DWave) qubits 
    """
    if delay == {}:
        disturbed = "notdisturbed"
    else:
        disturbed = "disturbed"

    file_name = f"article_plots/noqbits/embedding{q_par.dmax}_{disturbed}.csv"

    with open(file_name, 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ['no_logical', 'no_physical']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        logical = []
        physical = []
        for trains in [1,2,4,6,8,10,11,12]:
            l = embeddinq_dict[f"{trains}_{q_par.dmax}_{disturbed}"]["no_logical"]
            ph = embeddinq_dict[f"{trains}_{q_par.dmax}_{disturbed}"]["no_physical"]

            writer.writerow({'no_logical': l, 'no_physical': ph})
            logical.append(l)
            physical.append(ph)

    order = 1
    x_fit, y_fit = fit_polynomial(logical, physical, 15000, order = order)

    file_name = f"article_plots/noqbits/smallfit_order{order}_{q_par.dmax}_{disturbed}.csv"
    with open(file_name, 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ['no_logical', 'no_physical']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i, lqbits in enumerate(x_fit[0:9]):
            writer.writerow({'no_logical': lqbits, 'no_physical': y_fit[i]})


    file_name = f"article_plots/noqbits/fit_order{order}_{q_par.dmax}_{disturbed}.csv"
    with open(file_name, 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ['no_logical', 'no_physical']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i, lqbits in enumerate(x_fit):
            writer.writerow({'no_logical': lqbits, 'no_physical': y_fit[i]})





def fit_polynomial(x, y, rmax, order = 1):
    """
    returns the array of the points in linear (or quadratic) fit 
    given initial data in x,y, tle limit of the output and the fitting order
    """
    x_lin = np.array(list(range(0,rmax, 50)))
    if order == 1:
        a, b = np.polyfit(x, y, 1)
        y_lin = np.array(a*x_lin+b)
    if order == 2:
        a, b,c = np.polyfit(x, y, 2)
        y_lin = np.array(a*x_lin**2+b*x_lin+c)

    return x_lin, y_lin


def embedding_statistics():
    """" write down to .csv logical and physical (DWave) problem sizes from the series of computation """
    q_par = Comp_parameters()
    q_par.method = "real"
    q_par.ppair = 2.0
    q_par.psum = 4.0

    delays_list = [{}, {1:5, 2:2, 4:5}]

    with open("solutions/embedding.json", 'rb') as fp:
        embeddinq_dict = pickle.load(fp)

    q_par.dmax = 2
    delay = delays_list[0]
    csv_write_embedding(embeddinq_dict, q_par, delay)

    q_par.dmax = 6
    delay = delays_list[0]
    csv_write_embedding(embeddinq_dict, q_par, delay)

    q_par.dmax = 2
    delay = delays_list[1]
    csv_write_embedding(embeddinq_dict, q_par, delay)

    q_par.dmax = 6
    delay = delays_list[1]
    csv_write_embedding(embeddinq_dict, q_par, delay)


####################  GATES  ########################


def series_gates_simulations():
    """ series of computation for IonQ simulator """

    for (ppair,psum) in[(2.0, 4.0), (20.0,40.0)]:
        for dmax in [2,4,6]:
            save_results_gates(ppair,psum, nolayers=1,dmax=dmax, notrains = 1)
            save_results_gates(ppair,psum, nolayers=2,dmax=dmax, notrains = 1)

    for (ppair,psum) in[(2.0, 4.0), (20.0,40.0)]:
        save_results_gates(ppair,psum, nolayers=1,dmax=2, notrains = 2)
        save_results_gates(ppair,psum, nolayers=2,dmax=2, notrains = 2)



def series_gates_real():
    """ write down series of results for real Quantum Gates device """
    for (ppair,psum) in[(2.0, 4.0), (20.0,40.0)]:
        for dmax in [2,4,6]:
            save_results_gates(ppair,psum, nolayers=1,dmax=dmax, notrains = 1, real = True)
            save_results_gates(ppair,psum, nolayers=2,dmax=dmax, notrains = 1, real = True)

    for (ppair,psum) in[(2.0, 4.0), (20.0,40.0)]:
        save_results_gates(ppair,psum, nolayers=1,dmax=2, notrains = 2, real = True)
        save_results_gates(ppair,psum, nolayers=2,dmax=2, notrains = 2, real = True)




def series_gates_simulations_ibm():
    """ series of computation for IBM simulator """

    for (ppair,psum) in[(2.0, 4.0), (20.0,40.0)]:
        for dmax in [2,4,6]:
            save_results_gates(ppair,psum, nolayers=1,dmax=dmax, notrains = 1, device = "IBM")



def save_results_gates(ppair, psum, nolayers, dmax=2, notrains = 2, real = False,  device = "Aria"):
    """ save to .csv result from real or simulated Quantum Gates device """
    trains_input = Input_timetable()
    q_par = Comp_parameters()


    q_par.dmax = dmax
    q_par.ppair = ppair
    q_par.psum = psum

    if device == "Aria":
        if real:
            data_file = "QAOA Results/IonQ Aria Experiments/"
            q_par.method = "IonQreal"
        else:
            data_file = "QAOA Results/IonQ Simulations/"
            q_par.method = "IonQsim"
    if device == "IBM":
        q_par.method = "IBMsim"
        data_file = "QAOA Results/IBM Simulations/"


    delays_list = [{}, {1:5, 2:2, 4:5}]
    if notrains == 1 or real:
        delays_list = [{}]


    for delays in delays_list:
        if notrains == 1:
            trains_input.qubo_real_1t(delays)
        if notrains == 2:
            trains_input.qubo_real_2t(delays)

        _, csh = get_files_dirs(trains_input, q_par, data_file, nolayers)

        file_histogram = file_hist(trains_input, q_par)
        file_histogram = file_histogram.replace(csh[0], csh[1])
        hist = passing_time_histigrams(trains_input, q_par, file_histogram)
        write_file = file4csv(trains_input, q_par, nolayers)
        csv_write_hist(write_file, hist)

        hist = objective_histograms(file_histogram)
        write_file = write_file.replace("qubo", "objective")
        csv_write_hist(write_file, hist)

        our_title = plot_title(trains_input, q_par)
        print(our_title)

        energies = energies_histograms(file_histogram)
        write_file = write_file.replace("objective", "energies/energies_feasible")
        csv_write_hist(write_file, energies, key1 = "feasible_value", key2 = "feasible_count")
        write_file = write_file.replace("energies/energies_feasible", "energies/energies_notfeasible")
        csv_write_hist(write_file, energies, key1 = "notfeasible_value", key2 = "notfeasible_count")




def csv_file_scaling_gates(q_par, delay, layers):
    """ 
    returns the string of csv file and directory of scaling of feasibility percentage on (simulated) gates computing
    """
    if delay == {}:
        disturbed = "no"
    else:
        disturbed = "disturbed"

    file = f"article_plots/gates_scaling/qubo_{layers}layer_{q_par.method}_{q_par.ppair}_{q_par.psum}_{disturbed}.csv"

    return file

def csv_write_gates_scaling(file, d):
    """
    saves to csv results of scaling of feasibility percentage on (simulated) gates computing
    """
    with open(file, 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ['size', "perc"]
        size = d['no qubits']
        perc = d["perc_feasible"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(size):
            writer.writerow({'size': v, 'perc': perc[i]})


def gates_scalling_update(d, trains_input, q_par, data_file, nolayers):
    """
    updates list of number of qubits and feasibility percentage, for quantum gates results 
    """
    _, csh = get_files_dirs(trains_input, q_par, data_file, nolayers)
    file_histogram = file_hist(trains_input, q_par)
    file_histogram = file_histogram.replace(csh[0], csh[1])

    with open(file_histogram, 'rb') as fp:
        results = pickle.load(fp)
    d["no qubits"].append(results['no qubits'])
    d["perc_feasible"].append(results['perc feasible'])


def gates_scaling_IonQ(delays, ppair, psum, nolayers):
    """
    write down results from IonQ simulations: # qubits vs. feasibility percentage
    """
    trains_input = Input_timetable()
    q_par = Comp_parameters()

    print("IonQ simulation")

    q_par.ppair = ppair
    q_par.psum = psum
    q_par.method = "IonQsim"
    data_file = "QAOA Results/IonQ Simulations/"

    d = {"no qubits": [], "perc_feasible": []}

    if delays == {}:

        q_par.dmax = 2
        trains_input.qubo_real_1t(delays)
        gates_scalling_update(d, trains_input, q_par, data_file, nolayers)

        q_par.dmax = 4
        trains_input.qubo_real_1t(delays)
        gates_scalling_update(d, trains_input, q_par, data_file, nolayers)

        q_par.dmax = 6
        trains_input.qubo_real_1t(delays)
        gates_scalling_update(d, trains_input, q_par, data_file, nolayers)

    q_par.dmax = 2
    trains_input.qubo_real_2t(delays)
    gates_scalling_update(d, trains_input, q_par, data_file, nolayers)

    # TODO for larger ...

    file = csv_file_scaling_gates(q_par, delays, nolayers)
    csv_write_gates_scaling(file, d)


def gates_scaling_IBM(ppair, psum, nolayers):
    """
    write down results from IBM simulations: # qubits vs. feasibility percentage
    """
    trains_input = Input_timetable()
    q_par = Comp_parameters()

    print("IBM simulation")

    q_par.ppair = ppair
    q_par.psum = psum
    q_par.method = "IBMsim"
    data_file = "QAOA Results/IBM Simulations/"

    d = {"no qubits": [], "perc_feasible": []}
    delays = {}

    q_par.dmax = 2
    trains_input.qubo_real_1t(delays)
    gates_scalling_update(d, trains_input, q_par, data_file, nolayers)

    q_par.dmax = 4
    trains_input.qubo_real_1t(delays)
    gates_scalling_update(d, trains_input, q_par, data_file, nolayers)

    q_par.dmax = 6
    trains_input.qubo_real_1t(delays)
    gates_scalling_update(d, trains_input, q_par, data_file, nolayers)

    # TODO for larger ...

    file = csv_file_scaling_gates(q_par, delays, nolayers)
    csv_write_gates_scaling(file, d)


def gates_scaling_IonQ_seq(layers=1):
    """ write down series of results from IonQ simulations """
    delays_list = [{}, {1:5, 2:2, 4:5}]

    gates_scaling_IonQ(delays_list[0], 2.0, 4.0, layers)
    gates_scaling_IonQ(delays_list[1], 2.0, 4.0, layers)

    gates_scaling_IonQ(delays_list[0], 20.0, 40.0, layers)
    gates_scaling_IonQ(delays_list[1], 20.0, 40.0, layers)



################## Real life data from MRL  ################################

def real_data_dirs(part_of_day, direction):
    """ returs string: file name and directory where real live data are saved """
    assert part_of_day in ["morning ", "afternoon", "morning afternoon"]
    assert direction in ["north", "south"]
    days = "11-31"
    file = f"histograms/real_data/Realdata_{part_of_day}_{days}012024{direction}.json"
    return file


def MLR_data(file):
    """ returns dict, histogram of passing time of real trains' scenario """
    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    h = results["hist"]
    r1 = np.ceil(max(h))
    bins = np.arange(- 0.5, r1 + 1.5, 1.)
    our_h, our_b = np.histogram(h, bins = bins)
    b_middle = [(our_b[i] + our_b[i+1])/2 for i in range(len(our_b) - 1)]

    return{"count":our_h, "value":b_middle}


def plot_real_life_MLR_2():
    """ writes data from recorded real life trains passing time """
    print("real MLR")

    part_of_day = "morning afternoon"

    direction = "north"
    print(f"left {direction}")
    file = real_data_dirs(part_of_day, direction)
    hist = MLR_data(file)
    write_file = f"article_plots/MLR_real/{direction}_histogram.csv"
    csv_write_hist(write_file, hist)


    direction = "south"
    print(f"right {direction}")
    file = real_data_dirs(part_of_day, direction)
    hist = MLR_data(file)
    write_file = f"article_plots/MLR_real/{direction}_histogram.csv"
    csv_write_hist(write_file, hist)


    print("..... time  and data .....")
    with open(file, 'rb') as fp:
        results = pickle.load(fp)
    days = results["days"]
    month = results["month"]
    year = results["year"]
    period = results["period"]
    print(f"{period} {days}  {month}  {year}")

    print("..................")


#####################   Train diagrams ###########################


def csv_write_train_diagram(file, train_d):
    """ saves data for one train diagram """
    space = train_d["space"]
    time = train_d["time"]
    for j, route in space.items():
        with open(f"{file}{j}.csv", 'w', newline='', encoding="utf-8") as csvfile:
            fieldnames = ["loc", "t"]
            ts = time[j]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for i,loc in enumerate(route):
                writer.writerow({'loc': loc, 't': ts[i]})


def train_diagrams():
    """ generates and saves data for sequence of train diagrams """
    trains_input = Input_timetable()
    q_par = Comp_parameters()

    q_par.method = "real"
    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10

    delays_list = [{}, {1:5, 2:2, 4:5}]

    print("train diagram")

    trains_input.qubo_real_11t(delays_list[1])
    file = file_QUBO_comp(trains_input, q_par)
    with open(file, 'rb') as fp:
        samplesets = pickle.load(fp)

    solutions = get_solutions_from_dmode(samplesets, q_par)

    file = file_QUBO(trains_input, q_par)
    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    file = file_LP_output(trains_input, q_par)
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_read)
    exclude_st = ""

    v = lp_sol["variables"]

    file =  "article_plots/Conflicted_train_diagram.pdf"
    input_dict = train_path_data(v, qubo_to_analyze, exclude_st = exclude_st, initial_tt=True)
    #plot_train_diagrams(input_dict, file)
    file =  "article_plots/train_diagrams/conflicted/train"
    csv_write_train_diagram(file, input_dict)


    file =  "article_plots/ILPtrain_diagram.pdf"
    input_dict = train_path_data(v, qubo_to_analyze, exclude_st = exclude_st)
    file =  "article_plots/train_diagrams/ILP/train"
    csv_write_train_diagram(file, input_dict)


    solution, _ = best_feasible_state(solutions, qubo_to_analyze)
    v = qubo_to_analyze.qubo2int_vars(solution)

    file =  "article_plots/Btrain_diagram.pdf"
    input_dict = train_path_data(v, qubo_to_analyze, exclude_st = exclude_st)
    file =  "article_plots/train_diagrams/QUBObest/train"
    csv_write_train_diagram(file, input_dict)


    solution, _ = high_excited_state(solutions, qubo_to_analyze, trains_input.objective_stations, increased_pt=20)
    v = qubo_to_analyze.qubo2int_vars(solution)

    file =  "article_plots/Etrain_diagram.pdf"
    input_dict = train_path_data(v, qubo_to_analyze, exclude_st = exclude_st)
    file =  "article_plots/train_diagrams/QUBOexcited20/train"
    csv_write_train_diagram(file, input_dict)

    print("......................")


if __name__ == "__main__":
    series_DWave_hist()
    embedding_statistics()
    series_gates_real()
    series_gates_simulations()
    series_gates_simulations_ibm()
    gates_scaling_IonQ_seq()
    gates_scaling_IBM(2.0,4.0, 1)
    gates_scaling_IBM(20.0,40.0, 1)
    plot_real_life_MLR_2()
    feasibility_percentage()
    train_diagrams()
