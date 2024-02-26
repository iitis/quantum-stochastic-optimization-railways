import pickle
import matplotlib.pyplot as plt
import numpy as np

from QTrains import plot_train_diagrams, hist_passing_times, filter_feasible
from QTrains import _ax_hist_passing_times, _ax_objective, plot_title, file_hist
from QTrains import get_solutions_from_dmode, first_ground
from QTrains import file_QUBO_comp, file_QUBO, file_LP_output
from QTrains import Analyze_qubo
from trains_timetable import Input_qubo
from solve_qubo import Comp_parameters, Process_parameters


plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=10)


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

    fig = plt.figure(constrained_layout=True, figsize=(6, 4))

    fig.suptitle(f"DWave results, small instances of 18 qubits")

    (subfig1, subfig2) = fig.subfigures(2,1)

    (ax, ax1) = subfig1.subplots(1, 2, width_ratios=[1.2, 2])
    (ax2, ax3) = subfig2.subplots(1, 2 ,width_ratios=[1.2, 2])

    our_qubo.qubo_real_2t(delays_list[0])
    _ax_hist_passing_times(ax, our_qubo, q_par, p, add_text = False)
    _ax_objective(ax1, our_qubo, q_par, p)
    ax.set_xlabel("Passing time MR-CS")
    our_title = plot_title(our_qubo, q_par)
    print(f"18 qubits top {our_title}")
    ax.text(0.925, 1.1, 'a)', transform=ax.transAxes)
    ax1.text(0.925, 1.1, 'b)', transform=ax1.transAxes)

    our_qubo.qubo_real_2t(delays_list[1])
    _ax_hist_passing_times(ax2, our_qubo, q_par, p, add_text = False)
    _ax_objective(ax3, our_qubo, q_par, p)
    ax2.set_xlabel("Passing time MR-CS")
    our_title = plot_title(our_qubo, q_par)
    print(f"18 qubits botom {our_title}")
    print("..............................")
    ax2.text(0.925, 1.1, 'c)', transform=ax2.transAxes)
    ax3.text(0.925, 1.1, 'd)', transform=ax3.transAxes)


    ax2.set_xlim(left=10, right = 17)
    ax2.set_xticks([10,12,14,16])
    ax.sharex(ax2)    
    ax3.set_xlim(left=-0.2)
    ax1.sharex(ax3)


    fig.savefig("article_plots/2trains_dmax2_DWave.pdf")
    fig.clf()

def plotDWave_6trains():

    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()

    q_par.method = "real"

    delays_list = [{}, {1:5, 2:2, 4:5}]

    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    fig.suptitle("Shaping histograms by varous parameters of QUBO and computation, 6 trains")

    (subfig1, subfig2) = fig.subfigures(2,1)
    (ax, ax1) = subfig1.subplots(1, 2)
    (ax2, ax3) = subfig2.subplots(1, 2)

    q_par.dmax = 2
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10
    our_qubo.qubo_real_6t(delays_list[0])
    _ax_hist_passing_times(ax, our_qubo, q_par, p, add_text = False)
    our_title = plot_title(our_qubo, q_par)
    print(f"6 trains top left {our_title[14:len(our_title)]}, dmax={q_par.dmax}")
    ax.set_xlabel("Passing time MR-CS")

    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10
    our_qubo.qubo_real_6t(delays_list[0])
    _ax_hist_passing_times(ax1, our_qubo, q_par, p, add_text = False)
    our_title = plot_title(our_qubo, q_par)
    print(f"6 trains top fight {our_title[14:len(our_title)]},dm={q_par.dmax}")
    ax1.set_xlabel("Passing time MR-CS")


    q_par.dmax = 6
    q_par.ppair = 20.0
    q_par.psum = 40.0
    q_par.annealing_time = 10
    our_qubo.qubo_real_6t(delays_list[0])
    _ax_hist_passing_times(ax2, our_qubo, q_par, p, add_text = False)
    our_title = plot_title(our_qubo, q_par)
    print(f" 6 trains bottom left {our_title[14:len(our_title)]}, dmax={q_par.dmax}")
    ax2.set_xlabel("Passing time MR-CS")



    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 1000
    our_qubo.qubo_real_6t(delays_list[0])
    _ax_hist_passing_times(ax3, our_qubo, q_par, p, add_text = False)
    our_title = plot_title(our_qubo, q_par)
    print(f"6 train bottom right {our_title[14:len(our_title)]},d={q_par.dmax}")
    print("...............................")
    ax3.set_xlabel("Passing time MR-CS")

    ax3.set_xlim(left=11, right = 21)
    ax3.set_xticks([12,14,16,18,20])

    ax2.set_xlim(left=11, right = 21)
    ax2.set_xticks([12,14,16,18,20])

    ax.sharex(ax2)
    ax1.sharex(ax3)

    ax.text(0.925, 0.9, 'a)', transform=ax.transAxes)
    ax1.text(0.925, 0.9, 'b)', transform=ax1.transAxes)

    ax2.text(0.925, 0.9, 'c)', transform=ax2.transAxes)
    ax3.text(0.925, 0.9, 'd)', transform=ax3.transAxes)

    fig.savefig("article_plots/6trains_DWave.pdf")
    fig.clf()


def plotDWave_11trains_dmax6():

    p = Process_parameters()
    our_qubo = Input_qubo()
    q_par = Comp_parameters()

    q_par.method = "real"
    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0

    delays_list = [{}, {1:5, 2:2, 4:5}]

    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    fig.suptitle("DWave large instance 182 qubits, annealing time $10 \mu$s left, $1000 \mu$s right")

    (subfig1, subfig2) = fig.subfigures(2,1)
    (ax, ax1) = subfig1.subplots(1, 2)
    (ax2, ax3) = subfig2.subplots(1, 2)

    q_par.annealing_time = 10
    our_qubo.qubo_real_11t(delays_list[0])
    _ax_hist_passing_times(ax, our_qubo, q_par, p, add_text = False)
    our_title = plot_title(our_qubo, q_par)
    print(f"11 trains top {our_title} annealing time 10 left, 1000 right")
    ax.set_xlabel(f"Passing time MR-CS")

    q_par.annealing_time = 1000
    our_qubo.qubo_real_11t(delays_list[0])
    _ax_hist_passing_times(ax1, our_qubo, q_par, p, add_text = False)
    ax1.set_xlabel(f"Passing time MR-CS")

    q_par.annealing_time = 10
    our_qubo.qubo_real_11t(delays_list[1])
    _ax_hist_passing_times(ax2, our_qubo, q_par, p, add_text = False)
    ax2.set_xlabel(f"Passing time MR-CS")
    our_title = plot_title(our_qubo, q_par)
    print(f"11 trains bottom {our_title} annealing time 10 left, 1000 right")
    print(".............................")

    q_par.annealing_time = 1000
    our_qubo.qubo_real_11t(delays_list[1])
    _ax_hist_passing_times(ax3, our_qubo, q_par, p, add_text = False)
    ax3.set_xlabel(f"Passing time MR-CS")


    ax3.set_xlim(left=11, right = 21)
    ax3.set_xticks([12,14,16,18,20])

    ax2.set_xlim(left=11, right = 21)
    ax2.set_xticks([12,14,16,18,20])

    ax.sharex(ax2)
    ax1.sharex(ax3)
    ax.text(0.925, 0.9, 'a)', transform=ax.transAxes)
    ax1.text(0.925, 0.9, 'b)', transform=ax1.transAxes)

    ax2.text(0.925, 0.9, 'c)', transform=ax2.transAxes)
    ax3.text(0.925, 0.9, 'd)', transform=ax3.transAxes)

    fig.savefig("article_plots/11trains_dmax6_DWave.pdf")
    fig.clf()




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

    fig = plt.figure(constrained_layout=True, figsize=(6, 4))

    if no_trains == 10:
        no_qbits = 168
    elif no_trains == 11:
        no_qbits = 182
    elif no_trains == 12:
        no_qbits = 196
    fig.suptitle(f"DWave without Eq(5) check, {no_qbits} qbits, at= $10 \mu$s left, $1000 \mu$s right")

    (subfig1, subfig2) = fig.subfigures(2,1)
    (ax, ax1) = subfig1.subplots(1, 2)
    (ax2, ax3) = subfig2.subplots(1, 2)

    q_par.annealing_time = 10
    if no_trains == 10:
        our_qubo.qubo_real_10t(delays)
    elif no_trains == 11:
        our_qubo.qubo_real_11t(delays)
    elif no_trains == 12:
        our_qubo.qubo_real_12t(delays)
    _ax_hist_passing_times(ax, our_qubo, q_par, p, add_text = False)
    ax.set_xlabel(f"Passing time MR-CS")
    q_par.annealing_time = 1000
    _ax_hist_passing_times(ax1, our_qubo, q_par, p, add_text = False)
    ax1.set_xlabel(f"Passing time MR-CS")

    our_title = f"{no_trains} trains, Disturbed, ppair={q_par.ppair}, psum={q_par.psum}, dmax={int(q_par.dmax)}"
    print("Soft without passing time constrain check")
    print(f"upper {our_title}, annealing time 10 left, 1000 right")

    ax.text(0.925, 0.9, 'a)', transform=ax.transAxes)
    ax1.text(0.925, 0.9, 'b)', transform=ax1.transAxes)


    q_par.ppair = 20.0
    q_par.psum = 40.0
    q_par.annealing_time = 10
    if no_trains == 10:
        our_qubo.qubo_real_10t(delays)
    elif no_trains == 11:
        our_qubo.qubo_real_11t(delays)
    elif no_trains == 12:
        our_qubo.qubo_real_12t(delays)
    _ax_hist_passing_times(ax2, our_qubo, q_par, p, add_text = False)
    ax2.set_xlabel(f"Passing time MR-CS")
    q_par.annealing_time = 1000
    _ax_hist_passing_times(ax3, our_qubo, q_par, p, add_text = False)
    ax3.set_xlabel(f"Passing time MR-CS")

    our_title = f"{no_trains} trains, Disturbed, ppair={q_par.ppair}, psum={q_par.psum}, dmax={int(q_par.dmax)}"
    print(f"lower {our_title}, annealing time 10 left, 1000 right")
    print("...................")

    ax2.text(0.925, 0.9, 'c)', transform=ax2.transAxes)
    ax3.text(0.925, 0.9, 'd)', transform=ax3.transAxes)


    ax3.set_xlim(left=7, right = 23)
    ax3.set_xticks([8,10,12,14,16,18,20,22])

    ax2.set_xlim(left=7, right = 23)
    ax2.set_xticks([8,10,12,14,16,18,20,22])

    ax.sharex(ax2)
    ax1.sharex(ax3)

    fig.savefig(f"article_plots/{no_trains}trains_DWave_soft.pdf")
    fig.clf()


#########################  Scaling ####################
    
def add_elemet(our_qubo, q_par, p, no_qubits, no_qubo_terms, feasibility_perc):


    file = file_hist(our_qubo, q_par, p)
    
    with open(file, 'rb') as fp:
        res_dict = pickle.load(fp)
    

    no_qubits.append(res_dict["no qubits"])
    no_qubo_terms.append(res_dict["no qubo terms"])
    feasibility_perc.append(res_dict["perc feasible"])


def get_series(q_par, p, delays):

    no_qubits = []
    no_qubo_terms = []
    feasibility_perc = []

    for d in [2,6]:
        q_par.dmax = d

        our_qubo = Input_qubo()
        our_qubo.qubo_real_1t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_2t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_4t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()    
        our_qubo.qubo_real_6t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_8t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_10t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_11t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_qubo_terms, feasibility_perc)
        our_qubo = Input_qubo()
        our_qubo.qubo_real_12t(delays)
        add_elemet(our_qubo, q_par, p, no_qubits, no_qubo_terms, feasibility_perc)


    return no_qubits, no_qubo_terms, feasibility_perc


def plot_realisation_fit(ax, x, y, rmax, color, marker, label):
    
    ax.plot(x, y, marker, color = color, label = label)
    x_art = list(range(50,rmax, 50))

    if rmax > 0:
        if 0 in y:
            x = x[0:-1]
            y = y[0:-1]
        a, b = np.polyfit(x, np.log(y), 1)
        ax.plot(x_art, np.exp(a*np.array(x_art)+b), "--", color = color, label = f"{label} log linear fit")



    
def feasibility_percentage():
    p = Process_parameters()
    q_par = Comp_parameters()

    q_par.method = "real"
    delays_list = [{}, {1:5, 2:2, 4:5}]
    rmax = 10_000

    q_par.annealing_time = 10

    no_qubits_nd, Qsize_nd, feas_perc_nd = get_series(q_par, p, delays_list[0])
    no_qubits_d, Qsize_d, feas_perc_d = get_series(q_par, p, delays_list[1])

    
    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    fig.suptitle("DWave output - Scaling of precentage of feasible solutions")
    (subfig1, subfig2) = fig.subfigures(2,1)
    (ax, ax1) = subfig1.subplots(1, 2)
    (ax2, ax3) = subfig2.subplots(1, 2)

    plot_realisation_fit(ax, Qsize_nd, feas_perc_nd, 2500, color="green", marker="x", label="2,4 Not disturbed")
    plot_realisation_fit(ax, Qsize_d, feas_perc_d, 2500, color="red", marker="d", label="2,4 Disturbed")

    plot_realisation_fit(ax1, Qsize_nd, feas_perc_nd, rmax, color="green", marker="x", label="2,4 Not disturbed")
    plot_realisation_fit(ax1, Qsize_d, feas_perc_d, rmax, color="red", marker="d", label="2,4 Disturbed")

    q_par.ppair = 20.0
    q_par.psum = 40.0

    no_qubits_nd, Qsize_nd, feas_perc_nd = get_series(q_par, p, delays_list[0])
    no_qubits_d, Qsize_d, feas_perc_d = get_series(q_par, p, delays_list[1])

    plot_realisation_fit(ax, Qsize_nd, feas_perc_nd, 2500, color="blue", marker="1", label="20,40 Not disturbed")
    plot_realisation_fit(ax, Qsize_d, feas_perc_d, 2500, color="orange", marker="o", label="20,40 Disturbed")

    plot_realisation_fit(ax1, Qsize_nd, feas_perc_nd, rmax, color="blue", marker="1", label="20,40 Not disturbed")
    plot_realisation_fit(ax1, Qsize_d, feas_perc_d, rmax, color="orange", marker="o", label="20,40 Disturbed")


    ax.set_ylabel("perc. of feasible solutions")
    ax.set_xlabel("n.o. non zero QUBO elements")
    ax.set_yscale('log')
    ax.text(0.925, 0.9, 'a)', transform=ax.transAxes)


    ax1.text(0.925, 0.9, 'b)', transform=ax1.transAxes)
    ax1.set_ylabel("perc. of feasible solutions")
    ax1.set_xlabel("n.o. non zero QUBO elements")
    ax1.set_yscale('log')
    
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 1000

    no_qubits_nd, Qsize_nd, feas_perc_nd = get_series(q_par, p, delays_list[0])
    no_qubits_d, Qsize_d, feas_perc_d = get_series(q_par, p, delays_list[1])


    plot_realisation_fit(ax2, Qsize_nd, feas_perc_nd, 2500, color="green", marker="x", label="2,4 Not disturbed")
    plot_realisation_fit(ax2, Qsize_d, feas_perc_d, 2500, color="red", marker="d", label="2,4 Disturbed")

    plot_realisation_fit(ax3, Qsize_nd, feas_perc_nd, rmax, color="green", marker="x", label="2,4 Not disturbed")
    plot_realisation_fit(ax3, Qsize_d, feas_perc_d, rmax, color="red", marker="d", label="2,4 Disturbed")


    ax2.set_ylabel("perc. of feasible solutions")
    ax2.set_xlabel("n.o. non zero QUBO elements")
    ax2.set_yscale('log')
    ax2.text(0.925, 0.9, 'c)', transform=ax2.transAxes)


    q_par.ppair = 20.0
    q_par.psum = 40.0

    no_qubits_nd, Qsize_nd, feas_perc_nd = get_series(q_par, p, delays_list[0])
    no_qubits_d, Qsize_d, feas_perc_d = get_series(q_par, p, delays_list[1])


    plot_realisation_fit(ax2, Qsize_nd, feas_perc_nd, 2500, color="blue", marker="1", label="20,40 Not disturbed")
    plot_realisation_fit(ax2, Qsize_d, feas_perc_d, 2500, color="orange", marker="o", label="20,40 Disturbed")

    plot_realisation_fit(ax3, Qsize_nd, feas_perc_nd, rmax, color="blue", marker="1", label="20,40 Not disturbed")
    plot_realisation_fit(ax3, Qsize_d, feas_perc_d, rmax, color="orange", marker="o", label="20,40 Disturbed")
    ax3.text(0.925, 0.9, 'd)', transform=ax3.transAxes)


    ax3.set_ylabel("perc. of feasible solutions")
    ax3.set_xlabel("n.o. non zero QUBO elements")
    ax3.set_yscale('log')


    fig.savefig(f"article_plots/feasibility_percentage.pdf")
    plt.clf()


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


    fig = plt.figure(constrained_layout=True, figsize=(6, 4))

    (subfig1, subfig2) = fig.subfigures(2,1)
    (ax, ax1) = subfig1.subplots(1, 2, width_ratios=[1.2, 2])
    (ax2, ax3) = subfig2.subplots(1, 2, width_ratios=[1.2, 2])

    q_par.method = "IonQsim"
    q_par.dmax = 2
    q_par.ppair = ppair
    q_par.psum = psum
    q_par.annealing_time = 10

    fig.suptitle(f"{q_par.method} small instances of 18 qubits", size = 16)

    delays_list = [{}, {1:5, 2:2, 4:5}]

    delays = delays_list[0]
    our_qubo.qubo_real_2t(delays)
    comp_specifics_string = data_string_gates(q_par, delays)
    replace_pair = ("2trains/", f"2trains_IonQSimulatorResults_18_Qubits/{comp_specifics_string}")

    _ax_hist_passing_times(ax, our_qubo, q_par, p, add_text = False, replace_string = replace_pair)
    _ax_objective(ax1, our_qubo, q_par, p, replace_string = replace_pair)
    our_title = plot_title(our_qubo, q_par)
    print(f"Upper panel {our_title}")
    ax.set_xlabel("Passing time MR-CS")


    delays = delays_list[1]
    our_qubo.qubo_real_2t(delays)
    comp_specifics_string = data_string_gates(q_par, delays)
    replace_pair = ("2trains/", f"2trains_IonQSimulatorResults_18_Qubits/{comp_specifics_string}")
    _ax_hist_passing_times(ax2, our_qubo, q_par, p, add_text = False, replace_string = replace_pair)
    _ax_objective(ax3, our_qubo, q_par, p, replace_string = replace_pair)
    ax.set_xlabel("Passing time MR-CS")

    ax.text(0.925, 1.1, 'a)', transform=ax.transAxes)
    ax1.text(0.925, 1.1, 'b)', transform=ax1.transAxes)
    ax2.text(0.925, 1.1, 'a)', transform=ax2.transAxes)
    ax3.text(0.925, 1.1, 'b)', transform=ax3.transAxes)


    our_title = plot_title(our_qubo, q_par)
    print(f"Lower panel {our_title}")
    print("..........................")

    ax2.set_xlim(left=10, right = 17)
    ax2.set_xticks([10,12,14,16])
    ax.sharex(ax2)

    ax3.set_xlim(left=-0.2, right = 8.2)
    ax1.sharex(ax3)

    file_output = f"article_plots/2trains_{q_par.ppair}{q_par.psum}_IonQsim.pdf"
    file_output = file_output.replace(".0", "")


    plt.savefig(file_output)
    plt.clf()




# Real live data  from MRL

def real_data_dirs(part_of_day, direction):

    assert part_of_day in ["morning ", "afternoon", "morning afternoon"]
    assert direction in ["north", "south"]
    days = "11-31"

    file = f"histograms/real_data/Realdata_{part_of_day}_{days}012024{direction}.json"
    return file

def _ax_hist_real_data(ax, file):

    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    h = results["hist"]

    r1 = np.ceil(max(h))
    bins = np.arange(- 0.5, r1 + 1.5, 1.)

    ax.hist( h, bins = bins, color = "gray",  ec="darkblue")

    ax.set_xlabel(f"measured passing time CS -- MR")
    ax.set_xlim(left=6, right = 24)
    ax.set_xticks(range(6, 24, 2))
    ax.set_ylabel("counts")


def plot_real_live_MLR_4():


    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    fig.suptitle("Real data from MLR, pick hours", size = 16)
    (subfig1, subfig2) = fig.subfigures(2,1)
    (ax, ax1) = subfig1.subplots(1, 2)
    (ax2, ax3) = subfig2.subplots(1, 2)

    print("real MLR")

    part_of_day = "morning "
    direction = "north"

    print(f"up left {part_of_day} {direction}")

    file = real_data_dirs(part_of_day, direction)
    _ax_hist_real_data(ax, file)

    direction = "south"

    print(f"up right {part_of_day} {direction}")

    file = real_data_dirs(part_of_day, direction)
    _ax_hist_real_data(ax1, file)


    part_of_day = "afternoon"
    direction = "north"

    file = real_data_dirs(part_of_day, direction)
    _ax_hist_real_data(ax2, file)

    print(f"down left {part_of_day} {direction}")

    direction = "south"

    print(f"down righr {part_of_day} {direction}")

    file = real_data_dirs(part_of_day, direction)
    _ax_hist_real_data(ax3, file)

    print("...................")

    ax.text(0.925, 0.9, 'a)', transform=ax.transAxes)
    ax1.text(0.925, 0.9, 'b)', transform=ax1.transAxes)
    ax2.text(0.925, 0.9, 'c)', transform=ax2.transAxes)
    ax3.text(0.925, 0.9, 'd)', transform=ax3.transAxes)

    fig.savefig("article_plots/real_data4.pdf")
    fig.clf()



def plot_real_live_MLR_2():


    fig = plt.figure(constrained_layout=True, figsize=(6, 2.2))
    fig.suptitle("Real data measured from MLR left northbound, right southbound")
    (ax, ax1) = fig.subplots(1,2)

    print("real MLR")


    part_of_day = "morning afternoon"
    direction = "north"


    file = real_data_dirs(part_of_day, direction)

    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    days = results["days"]
    month = results["month"]
    year = results["year"]
    period = results["period"]
    print(f"{period} {days}  {month}  {year}")


    print(f"left {direction}")

    _ax_hist_real_data(ax, file)

    direction = "south"
    print(f"right {direction}")

    print("..................")

    file = real_data_dirs(part_of_day, direction)
    _ax_hist_real_data(ax1, file)

    ax.text(0.925, 0.9, 'a)', transform=ax.transAxes)
    ax1.text(0.925, 0.9, 'b)', transform=ax1.transAxes)


    fig.savefig("article_plots/real_data2.pdf")
    fig.clf()

def high_excited(solutions, qubo_to_analyze, our_qubo):
    for solution in solutions:
        vq = qubo_to_analyze.qubo2int_vars(solution)
        h = hist_passing_times(vq, our_qubo.objective_stations, qubo_to_analyze)
        if (20 in h):
            return solution, qubo_to_analyze.objective(solution)
    return 0, 0

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

    our_qubo.qubo_real_11t(delays_list[1])    
    file = file_QUBO_comp(our_qubo, q_par, p)
    print( file )
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

    solution = first_ground(solutions, qubo_to_analyze, lp_sol)
    v = qubo_to_analyze.qubo2int_vars(solution)

    file =  "article_plots/Gtrain_diagram.pdf"
    plot_train_diagrams(v, qubo_to_analyze, file)


    feas_sols = filter_feasible(solutions, qubo_to_analyze)

    solution, energy = high_excited(feas_sols, qubo_to_analyze, our_qubo)
    v = qubo_to_analyze.qubo2int_vars(solution)

    file =  "article_plots/Etrain_diagram.pdf"
    plot_train_diagrams(v, qubo_to_analyze, file)





if __name__ == "__main__":
    train_diagrams()

    #plotDWave_2trains_dmax2()
    #plotDWave_11trains_dmax6()
    #plotDWave_6trains()
    #plot_DWave_soft_dmax6(no_trains = 11)
    #plot_DWave_soft_dmax6(no_trains = 10)

    #plot2trains_gates_simulations(2.0,4.0)
    #plot2trains_gates_simulations(20.0,40.0)

    #plot_real_live_MLR_4()
    #plot_real_live_MLR_2()

    feasibility_percentage()