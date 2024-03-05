import pickle
import numpy as np
import csv

from QTrains import high_excited_state
from QTrains import plot_title, file_hist, objective_histograms, energies_histograms, passing_time_histigrams, train_path_data
from QTrains import get_solutions_from_dmode, best_feasible_state
from QTrains import file_QUBO_comp, file_QUBO, file_LP_output
from QTrains import Analyze_qubo
from trains_timetable import Input_qubo
from solve_qubo import Comp_parameters, Process_parameters




def csv_write_hist(file_name, hist, key1 = "value", key2 = "count"):
    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = [key1, key2]
        value = hist[key1]
        count = hist[key2]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(value):
            writer.writerow({key1: v, key2: count[i]})



def file4csv(our_qubo, q_par, p):
    write_file = file_hist(our_qubo, q_par, p)
    write_file = write_file.replace("histograms/LR_timetable/", "article_plots/")
    write_file = write_file.replace("histograms_soft/LR_timetable/", "article_plots/")
    write_file = write_file.replace(".json", ".csv")
    return write_file


############# DWave #########



def plotDWave_2trains_dmax2():

    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()

    q_par.method = "real"
    q_par.dmax = 2
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10
    delays_list = [{}, {1:5, 2:2, 4:5}]

    our_qubo.qubo_real_2t(delays_list[0])

    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)

    hist = objective_histograms(our_qubo, q_par, p)
    write_file = write_file.replace("qubo", "objective")
    csv_write_hist(write_file, hist)

    our_title = plot_title(our_qubo, q_par)
    print(f"2 trains, 18 qubits passing time / objective, top {our_title}")


    our_qubo.qubo_real_2t(delays_list[1])

    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)

    hist = objective_histograms(our_qubo, q_par, p)
    write_file = write_file.replace("qubo", "objective")
    csv_write_hist(write_file, hist)

    our_title = plot_title(our_qubo, q_par)
    print(f"2 trains, 18 qubits passing time / objective, botom {our_title}")
    print("..............................")


    energies = energies_histograms(our_qubo, q_par, p)
    write_file = write_file.replace("objective", "energies/energies_feasible")
    csv_write_hist(write_file, energies, key1 = "feasible_value", key2 = "feasible_count")
    write_file = write_file.replace("energies/energies_feasible", "energies/energies_notfeasible")
    csv_write_hist(write_file, energies, key1 = "notfeasible_value", key2 = "notfeasible_count")

    q_par.ppair = 20.0
    q_par.psum = 40.0

    write_file = file4csv(our_qubo, q_par, p)
    energies = energies_histograms(our_qubo, q_par, p)
    write_file = write_file.replace("qubo", "energies/energies_feasible")
    print(write_file)
    csv_write_hist(write_file, energies, key1 = "feasible_value", key2 = "feasible_count")
    write_file = write_file.replace("energies/energies_feasible", "energies/energies_notfeasible")
    csv_write_hist(write_file, energies, key1 = "notfeasible_value", key2 = "notfeasible_count")



def plotDWave_6trains():

    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()
    q_par.method = "real"
    delays_list = [{}, {1:5, 2:2, 4:5}]

    q_par.dmax = 2
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10
    our_qubo.qubo_real_6t(delays_list[0])
    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)
    our_title = plot_title(our_qubo, q_par)
    print(f"6 trains top left {our_title[14:len(our_title)]}, dmax={q_par.dmax}")


    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10
    our_qubo.qubo_real_6t(delays_list[0])
    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)
    our_title = plot_title(our_qubo, q_par)
    print(f"6 trains top fight {our_title[14:len(our_title)]},dm={q_par.dmax}")


    q_par.dmax = 6
    q_par.ppair = 20.0
    q_par.psum = 40.0
    q_par.annealing_time = 10
    our_qubo.qubo_real_6t(delays_list[0])
    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)
    our_title = plot_title(our_qubo, q_par)
    print(f"6 trains bottom left {our_title[14:len(our_title)]}, dmax={q_par.dmax}")


    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 1000
    our_qubo.qubo_real_6t(delays_list[0])
    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)
    our_title = plot_title(our_qubo, q_par)
    print(f"6 train bottom right {our_title[14:len(our_title)]},d={q_par.dmax}")
    print("...............................")



def plotDWave_11trains_hist(dmax = 6):

    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()
    q_par.method = "real"
    q_par.dmax = dmax
    q_par.ppair = 2.0
    q_par.psum = 4.0
    delays_list = [{}, {1:5, 2:2, 4:5}]


    q_par.annealing_time = 10
    our_qubo.qubo_real_11t(delays_list[0])
    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)
    our_title = plot_title(our_qubo, q_par)
    print(f"11 trains top left, {our_title}")


    q_par.annealing_time = 1000
    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)
    our_title = plot_title(our_qubo, q_par)
    print(f"11 trains top right, {our_title}")

    q_par.annealing_time = 10
    our_qubo.qubo_real_11t(delays_list[1])

    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)
    our_title = plot_title(our_qubo, q_par)
    print(f"11 trains bottom left, {our_title}")

    energies = energies_histograms(our_qubo, q_par, p)
    write_file = write_file.replace("qubo", "energies/energies_feasible")
    csv_write_hist(write_file, energies, key1 = "feasible_value", key2 = "feasible_count")
    write_file = write_file.replace("energies/energies_feasible", "energies/energies_notfeasible")
    csv_write_hist(write_file, energies, key1 = "notfeasible_value", key2 = "notfeasible_count")


    q_par.annealing_time = 1000
    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)
    print(f"11 trains bottom right, {our_title}")
    print(".............................")

    energies = energies_histograms(our_qubo, q_par, p)
    write_file = write_file.replace("qubo", "energies/energies_feasible")
    csv_write_hist(write_file, energies, key1 = "feasible_value", key2 = "feasible_count")
    write_file = write_file.replace("energies/energies_feasible", "energies/energies_notfeasible")
    csv_write_hist(write_file, energies, key1 = "notfeasible_value", key2 = "notfeasible_count")


    q_par.ppair = 20.0
    q_par.psum = 40.0
    q_par.annealing_time = 10
    energies = energies_histograms(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    write_file = write_file.replace("qubo", "energies/energies_feasible")
    csv_write_hist(write_file, energies, key1 = "feasible_value", key2 = "feasible_count")
    write_file = write_file.replace("energies/energies_feasible", "energies/energies_notfeasible")
    csv_write_hist(write_file, energies, key1 = "notfeasible_value", key2 = "notfeasible_count")

    q_par.annealing_time = 1000
    energies = energies_histograms(our_qubo, q_par, p)
    write_file = write_file.replace("qubo", "energies/energies_feasible")
    csv_write_hist(write_file, energies, key1 = "feasible_value", key2 = "feasible_count")
    write_file = write_file.replace("energies/energies_feasible", "energies/energies_notfeasible")
    csv_write_hist(write_file, energies, key1 = "notfeasible_value", key2 = "notfeasible_count")







def plot_DWave_soft_dmax6(no_trains = 11):

    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()
    q_par.method = "real"
    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    p.softern_pass = True

    delays_list = [{}, {1:5, 2:2, 4:5}]
    delays = delays_list[1]

    #fig = plt.figure(constrained_layout=True, figsize=(6, 4))

    if no_trains == 10:
        no_qbits = 168
        our_qubo.qubo_real_10t(delays)
    elif no_trains == 11:
        no_qbits = 182
        our_qubo.qubo_real_11t(delays)
    elif no_trains == 12:
        no_qbits = 196
        our_qubo.qubo_real_12t(delays)
    
    print(f"DWave without Eq(5) check, {no_qbits} qbits, at= $10 \mu$s left, $1000 \mu$s right")


    q_par.annealing_time = 10

    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)

    q_par.annealing_time = 1000
    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)

    our_title = f"{no_trains} trains, upper, disturbed, ppair={q_par.ppair}, psum={q_par.psum}, dmax={int(q_par.dmax)}"
    print(f"{our_title}, annealing time 10 left, 1000 right")

    q_par.ppair = 20.0
    q_par.psum = 40.0
    q_par.annealing_time = 10

    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)
    q_par.annealing_time = 1000

    hist = passing_time_histigrams(our_qubo, q_par, p)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)

    our_title = f"{no_trains} trains, lower, disturbed, ppair={q_par.ppair}, psum={q_par.psum}, dmax={int(q_par.dmax)}"
    print(f"{our_title}, annealing time 10 left, 1000 right")
    print("...................")



#########################  Scaling ####################
    
def add_elemet(our_qubo, q_par, p, no_qubits, no_physical_qbits, no_qubo_terms, feasibility_perc):

    file = file_hist(our_qubo, q_par, p)
    with open(file, 'rb') as fp:
        res_dict = pickle.load(fp)
    
    no_qubits.append(res_dict["no qubits"])
    no_qubo_terms.append(res_dict["no qubo terms"])
    feasibility_perc.append(res_dict["perc feasible"])

    with open("solutions/embedding.json", 'rb') as fp:
        embeddinq_dict = pickle.load(fp)

    if our_qubo.delays == {}:
        disturbed = "notdisturbed"
    else:
        disturbed = "disturbed"

    phys_qbits = embeddinq_dict[f"{our_qubo.notrains}_{q_par.dmax}_{disturbed}"]

    assert phys_qbits['no_logical'] == res_dict["no qubits"]

    no_physical_qbits.append(phys_qbits['no_physical'])


def log_linear_fit(x, y, rmax):
    
    x_lin = list(range(0,rmax, 50))
    if rmax > 0:
        if 0 in y:
            x = x[0:-1]
            y = y[0:-1]
        a, b = np.polyfit(x, np.log(y), 1)

    y_lin = np.exp(a*np.array(x_lin)+b)

    return x_lin, y_lin


def get_series(q_par, p, delays, rmax):

    no_qubits = []
    no_physical_qubits = []
    no_qubo_terms = []
    feasibility_perc = []

    for d in [2,6]:
        q_par.dmax = d
        our_qubo = Input_qubo()
        our_qubo.qubo_real_1t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_2t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_4t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()    
        our_qubo.qubo_real_6t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_8t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_10t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_11t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_12t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_physical_qubits, no_qubo_terms, feasibility_perc)

    x_lin, y_lin = log_linear_fit(no_physical_qubits, feasibility_perc, rmax)

    d = {"no_qubits":no_qubits, "no_physical":no_physical_qubits, "no_qubo_terms":no_qubo_terms, "feasibility_perc":feasibility_perc, "x_lin":x_lin, "y_lin":y_lin}

    return d


def csv_file_scaling(q_par, delay):
    if delay == {}:
        disturbed = "no"
    else:
        disturbed = "disturbed"
    file = f"article_plots/scaling/qubo{q_par.annealing_time}_{q_par.ppair}_{q_par.psum}_{disturbed}.csv"
    file_fit_small = f"article_plots/scaling/fitsmall{q_par.annealing_time}_{q_par.ppair}_{q_par.psum}_{disturbed}.csv"
    file_fit = f"article_plots/scaling/fit{q_par.annealing_time}_{q_par.ppair}_{q_par.psum}_{disturbed}.csv"

    return file, file_fit_small, file_fit



def csv_write_scaling(file, file_fit_small, file_fit, d):
    with open(file, 'w', newline='') as csvfile:
        fieldnames = ["size", "perc"]
        size = d["no_physical"]
        perc = d["feasibility_perc"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(size):
            writer.writerow({'size': v, 'perc': perc[i]})
    with open(file_fit_small, 'w', newline='') as csvfile:
        fieldnames = ["x_lin", "y_lin"]
        size = d["x_lin"][0:11]
        perc = d["y_lin"][0:11]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(size):
            writer.writerow({'x_lin': v, 'y_lin': perc[i]})
    with open(file_fit, 'w', newline='') as csvfile:
        fieldnames = ["x_lin", "y_lin"]
        size = d["x_lin"]
        perc = d["y_lin"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(size):
            writer.writerow({'x_lin': v, 'y_lin': perc[i]})

    
def feasibility_percentage():
    p = Process_parameters()
    q_par = Comp_parameters()
    q_par.method = "real"
    delays_list = [{}, {1:5, 2:2, 4:5}]
    rmax = 150_000

    print("feasibility percentage")

    q_par.annealing_time = 10

    q_par.ppair = 2.0
    q_par.psum = 4.0

    delay = delays_list[0]
    d = get_series(q_par, p, delay, rmax)
    file, file_fit_small, file_fit = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit_small, file_fit, d)

    delay = delays_list[1]
    d = get_series(q_par, p, delay, rmax)
    file, file_fit_small, file_fit = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit_small, file_fit, d)

    q_par.ppair = 20.0
    q_par.psum = 40.0

    delay = delays_list[0]
    d = get_series(q_par, p, delay, rmax)
    file, file_fit_small, file_fit = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit_small, file_fit, d)

    delay = delays_list[1]
    d = get_series(q_par, p, delay, rmax)
    file, file_fit_small, file_fit = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit_small, file_fit, d)

    q_par.annealing_time = 1000

    q_par.ppair = 2.0
    q_par.psum = 4.0

    delay = delays_list[0]
    d = get_series(q_par, p, delay, rmax)
    file, file_fit_small, file_fit = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit_small, file_fit, d)

    delay = delays_list[1]
    d = get_series(q_par, p, delay, rmax)
    file, file_fit_small, file_fit = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit_small, file_fit, d)

    q_par.ppair = 20.0
    q_par.psum = 40.0

    delay = delays_list[0]
    d = get_series(q_par, p, delay, rmax)
    file, file_fit_small, file_fit = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit_small, file_fit, d)

    delay = delays_list[1]
    d = get_series(q_par, p, delay, rmax)
    file, file_fit_small, file_fit = csv_file_scaling(q_par, delay)
    csv_write_scaling(file, file_fit_small, file_fit, d)

    print("..........................................")
    



def csv_write_embedding(embeddinq_dict, q_par, delay):
    if delay == {}:
        disturbed = "notdisturbed"
    else:
        disturbed = "disturbed"

    file_name = f"article_plots/noqbits/embedding{q_par.dmax}_{disturbed}.csv"

    with open(file_name, 'w', newline='') as csvfile:
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
    x_fit, y_fit = fit(logical, physical, 15000, order = order)

    file_name = f"article_plots/noqbits/smallfit_order{order}_{q_par.dmax}_{disturbed}.csv"
    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = ['no_logical', 'no_physical']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i, lqbits in enumerate(x_fit[0:9]):
            writer.writerow({'no_logical': lqbits, 'no_physical': y_fit[i]})

    
    file_name = f"article_plots/noqbits/fit_order{order}_{q_par.dmax}_{disturbed}.csv"
    with open(file_name, 'w', newline='') as csvfile:
        fieldnames = ['no_logical', 'no_physical']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i, lqbits in enumerate(x_fit):
            writer.writerow({'no_logical': lqbits, 'no_physical': y_fit[i]})





def fit(x, y, rmax, order = 1):
    
    x_lin = np.array(list(range(0,rmax, 50)))
    if order == 1:
        a, b = np.polyfit(x, y, 1)
        y_lin = np.array(a*x_lin+b)
    if order == 2:
        a, b,c = np.polyfit(x, y, 2)
        y_lin = np.array(a*x_lin**2+b*x_lin+c)


    return x_lin, y_lin

def embedding():

    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()
    q_par.method = "real"
    q_par.ppair = 2.0
    q_par.psum = 4.0
    p.softern_pass = True

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


def data_string_gates(q_par, delays):
    """  this ir rough encodung, will be expanded """
    if q_par.ppair == 2.0 and q_par.psum == 4.0 and delays == {}:
        return "summary.53."
    if q_par.ppair == 20.0 and q_par.psum == 40.0 and delays == {}:
        return "summary.51."
    if q_par.ppair == 2.0 and q_par.psum == 4.0 and delays == {1:5, 2:2, 4:5}:
        return "summary.51."
    if q_par.ppair == 20.0 and q_par.psum == 40.0 and delays == {1:5, 2:2, 4:5}:
        return "summary.50."
    


def plot2trains_gates_simulations(ppair, psum):
    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()

    print("IonQ simulation, 2 trains 18 qbits")


    q_par.method = "IonQsim"
    q_par.dmax = 2
    q_par.ppair = ppair
    q_par.psum = psum
    q_par.annealing_time = 10


    delays_list = [{}, {1:5, 2:2, 4:5}]

    delays = delays_list[0]
    our_qubo.qubo_real_2t(delays)
    comp_specifics_string = data_string_gates(q_par, delays)
    replace_pair = ("2trains/", f"2trains_IonQSimulatorResults_18_Qubits/{comp_specifics_string}")
    
    hist = passing_time_histigrams(our_qubo, q_par, p, replace_string = replace_pair)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)

    hist = objective_histograms(our_qubo, q_par, p, replace_string = replace_pair)
    write_file = write_file.replace("qubo", "objective")
    csv_write_hist(write_file, hist)

    our_title = plot_title(our_qubo, q_par)
    print(f"Upper panel, left passing time, right objective, {our_title}")


    delays = delays_list[1]
    our_qubo.qubo_real_2t(delays)
    comp_specifics_string = data_string_gates(q_par, delays)
    replace_pair = ("2trains/", f"2trains_IonQSimulatorResults_18_Qubits/{comp_specifics_string}")

    hist = passing_time_histigrams(our_qubo, q_par, p, replace_string = replace_pair)
    write_file = file4csv(our_qubo, q_par, p)
    csv_write_hist(write_file, hist)

    hist = objective_histograms(our_qubo, q_par, p, replace_string = replace_pair)
    write_file = write_file.replace("qubo", "objective")
    csv_write_hist(write_file, hist)

    energies = energies_histograms(our_qubo, q_par, p, replace_string = replace_pair)
    write_file = write_file.replace("objective", "energies/energies_feasible")
    csv_write_hist(write_file, energies, key1 = "feasible_value", key2 = "feasible_count")
    write_file = write_file.replace("energies/energies_feasible", "energies/energies_notfeasible")
    csv_write_hist(write_file, energies, key1 = "notfeasible_value", key2 = "notfeasible_count")


    our_title = plot_title(our_qubo, q_par)
    print(f"Lower panel, eft passing time, right objective, {our_title}")
    print("..........................")



def csv_file_scaling(q_par, delay):
    if delay == {}:
        disturbed = "no"
    else:
        disturbed = "disturbed"
    file = f"article_plots/gates_scaling/qubo_{q_par.method}_{q_par.ppair}_{q_par.psum}_{disturbed}.csv"

    return file

def csv_write_gates_scaling(file, d):
    with open(file, 'w', newline='') as csvfile:
        fieldnames = ['size', "perc"]
        size = d['no qubits']
        perc = d["perc_feasible"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i,v in enumerate(size):
            writer.writerow({'size': v, 'perc': perc[i]})


def gates_scaling(delays, ppair, psum):
    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()

    print("IonQ simulation, 2 trains 18 qbits")


    q_par.method = "IonQsim"
    q_par.dmax = 2
    q_par.ppair = ppair
    q_par.psum = psum

    our_qubo.qubo_real_2t(delays)
    comp_specifics_string = data_string_gates(q_par, delays)
    replace_pair = ("2trains/", f"2trains_IonQSimulatorResults_18_Qubits/{comp_specifics_string}")

    file = file_hist(our_qubo, q_par, p, replace_pair = replace_pair)
    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    d = {"no qubits": [results['no qubits']], "perc_feasible": [results['perc feasible']]}
    file = csv_file_scaling(q_par, delays)
    csv_write_gates_scaling(file, d)


def gates_scaling_seq():

    delays_list = [{}, {1:5, 2:2, 4:5}]

    gates_scaling(delays_list[0], 2.0, 4.0)
    gates_scaling(delays_list[1], 2.0, 4.0)

    gates_scaling(delays_list[0], 20.0, 40.0)
    gates_scaling(delays_list[1], 20.0, 40.0)



################## Real live data from MRL  ################################

def real_data_dirs(part_of_day, direction):

    assert part_of_day in ["morning ", "afternoon", "morning afternoon"]
    assert direction in ["north", "south"]
    days = "11-31"
    file = f"histograms/real_data/Realdata_{part_of_day}_{days}012024{direction}.json"
    return file


def MLR_data(file):
    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    h = results["hist"]
    r1 = np.ceil(max(h))
    bins = np.arange(- 0.5, r1 + 1.5, 1.)
    our_h, our_b = np.histogram(h, bins = bins)
    b_middle = [(our_b[i] + our_b[i+1])/2 for i in range(len(our_b) - 1)]

    return{"count":our_h, "value":b_middle}


def _ax_hist_real_data(ax, hist):

    xs = hist["value"]
    ys = hist["count"]
    ax.bar(xs,ys, color = "gray",  ec="darkblue")
    ax.set_xlabel(f"measured passing time CS -- MR")
    ax.set_xlim(left=6, right = 24)
    ax.set_xticks(range(6, 24, 2))
    ax.set_ylabel("counts")




def plot_real_live_MLR_2():

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
    space = train_d["space"]
    time = train_d["time"]
    for j, route in space.items():
        with open(f"{file}{j}.csv", 'w', newline='') as csvfile:
            fieldnames = ["loc", "t"]
            ts = time[j]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for i,loc in enumerate(route):
                writer.writerow({'loc': loc, 't': ts[i]})




def train_diagrams():

    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()

    q_par.method = "real"
    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10

    delays_list = [{}, {1:5, 2:2, 4:5}]

    print("train diagram")

    our_qubo.qubo_real_11t(delays_list[1])    
    file = file_QUBO_comp(our_qubo, q_par, p)
    with open(file, 'rb') as fp:
        samplesets = pickle.load(fp)

    solutions = get_solutions_from_dmode(samplesets, q_par)

    file = file_QUBO(our_qubo, q_par, p)
    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    file = file_LP_output(our_qubo, q_par, p)
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
    

    solution, energy = best_feasible_state(solutions, qubo_to_analyze)
    v = qubo_to_analyze.qubo2int_vars(solution)

    file =  "article_plots/Btrain_diagram.pdf"
    input_dict = train_path_data(v, qubo_to_analyze, exclude_st = exclude_st)
    file =  "article_plots/train_diagrams/QUBObest/train"
    csv_write_train_diagram(file, input_dict)


    solution, energy = high_excited_state(solutions, qubo_to_analyze, our_qubo.objective_stations, increased_pt=20)
    v = qubo_to_analyze.qubo2int_vars(solution)

    file =  "article_plots/Etrain_diagram.pdf"
    input_dict = train_path_data(v, qubo_to_analyze, exclude_st = exclude_st)
    file =  "article_plots/train_diagrams/QUBOexcited20/train"
    csv_write_train_diagram(file, input_dict)

    print("......................")



if __name__ == "__main__":
    plotDWave_2trains_dmax2()
    #plotDWave_6trains()
    plotDWave_11trains_hist(dmax = 2)
    plotDWave_11trains_hist(dmax = 6)
    #plot_DWave_soft_dmax6(no_trains = 11)

    plot2trains_gates_simulations(2.0,4.0)
    plot2trains_gates_simulations(20.0,40.0)

    gates_scaling_seq()


    #plot_real_live_MLR_2()

    #embedding()

    #feasibility_percentage()

    #train_diagrams()