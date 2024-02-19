import pickle
import os.path
import matplotlib.pyplot as plt
import numpy as np
import sys
 


from solve_qubo import Input_qubo, Comp_parameters, Process_parameters, file_QUBO, file_LP_output, make_plots
from solve_qubo import plot_title, _ax_hist_passing_times, _ax_objective




def plot2trains_dmax2_DWave():

    p = Process_parameters()
    p.analyze = True
    our_qubo = Input_qubo()
    q_par = Comp_parameters()

    q_par.method = "real"
    q_par.dmax = 2
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10

    delays_list = [{}, {1:5, 2:2, 4:5}]

    fig = plt.figure(constrained_layout=True, figsize=(6, 4))

    fig.suptitle(f"DWave results, small instances dmax={int(q_par.dmax)} and 2 trains", size = 16)

    (subfig1, subfig2) = fig.subfigures(2,1)

    (ax, ax1) = subfig1.subplots(1, 2, width_ratios=[1.2, 2])
    (ax2, ax3) = subfig2.subplots(1, 2 ,width_ratios=[1.2, 2])

    our_qubo.qubo_real_2t(delays_list[0])
    _ax_hist_passing_times(ax, our_qubo, q_par, p, add_text = False, dir="")
    _ax_objective(ax1, our_qubo, q_par, p)
    our_title = plot_title(our_qubo, q_par)
    subfig1.suptitle(our_title)

    our_qubo.qubo_real_2t(delays_list[1])
    _ax_hist_passing_times(ax2, our_qubo, q_par, p, add_text = False, dir="")
    _ax_objective(ax3, our_qubo, q_par, p)
    subfig2.suptitle("Disturbed, parameters as above")

    ax2.set_xlim(left=10, right = 17)
    ax2.set_xticks([10,12,14,16])
    ax.sharex(ax2)


    
    ax3.set_xlim(left=-0.2)
    ax1.sharex(ax3)


    fig.savefig("article_plots/2trains_dmax2_DWave.pdf")
    fig.clf()


def plot10_11trains_dmax6_DWave():

    p = Process_parameters()
    p.analyze = True
    our_qubo = Input_qubo()
    q_par = Comp_parameters()

    q_par.method = "real"
    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10

    delays_list = [{}, {1:5, 2:2, 4:5}]

    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    fig.suptitle("DWave results, passing times MR - CS both ways", size = 16)

    (subfig1, subfig2) = fig.subfigures(2,1)
    (ax, ax1) = subfig1.subplots(1, 2)
    (ax2, ax3) = subfig2.subplots(1, 2)

    our_qubo.qubo_real_10t(delays_list[0])
    _ax_hist_passing_times(ax, our_qubo, q_par, p, add_text = False, dir="")
    our_title = f"{plot_title(our_qubo, q_par)} dmax={int(q_par.dmax)}"
    ax.set_xlabel("passing time MR-CS, 10 trains")
    our_qubo.qubo_real_11t(delays_list[0])
    _ax_hist_passing_times(ax1, our_qubo, q_par, p, add_text = False, dir="")
    subfig1.suptitle(our_title)
    ax1.set_xlabel("passing time MR-CS, 11 trains")

    our_qubo.qubo_real_10t(delays_list[1])
    _ax_hist_passing_times(ax2, our_qubo, q_par, p, add_text = False, dir="")
    ax2.set_xlabel("passing time MR-CS, 10 trains")
    our_title = "Disturbed, other parameters as above"
    our_qubo.qubo_real_11t(delays_list[1])
    _ax_hist_passing_times(ax3, our_qubo, q_par, p, add_text = False, dir="")
    ax3.set_xlabel("passing time MR-CS, 11 trains")
    subfig2.suptitle(our_title)


    ax3.set_xlim(left=11, right = 21)
    ax3.set_xticks([12,14,16,18,20])

    ax2.set_xlim(left=11, right = 21)
    ax2.set_xticks([12,14,16,18,20])

    ax.sharex(ax2)
    ax1.sharex(ax3)

    fig.savefig("article_plots/10_11trains_dmax6_DWave.pdf")
    fig.clf()


def plot6trains_intermediate():

    p = Process_parameters()
    p.analyze = True
    our_qubo = Input_qubo()
    q_par = Comp_parameters()

    q_par.method = "real"

    delays_list = [{}, {1:5, 2:2, 4:5}]

    fig = plt.figure(constrained_layout=True, figsize=(6, 4))
    fig.suptitle("DWave results, intermediate case of 6 trains", size = 16)

    (subfig1, subfig2) = fig.subfigures(2,1)
    (ax, ax1) = subfig1.subplots(1, 2)
    (ax2, ax3) = subfig2.subplots(1, 2)

    q_par.dmax = 2
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10
    our_qubo.qubo_real_6t(delays_list[0])
    _ax_hist_passing_times(ax, our_qubo, q_par, p, add_text = False, dir="")
    our_title = plot_title(our_qubo, q_par)
    ax.set_title(f"{our_title[14:len(our_title)]}, dmax={q_par.dmax}")
    ax.set_xlabel("passing time, MR-CS")

    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 10
    our_qubo.qubo_real_6t(delays_list[0])
    _ax_hist_passing_times(ax1, our_qubo, q_par, p, add_text = False, dir="")
    our_title = plot_title(our_qubo, q_par)
    ax1.set_title(f"{our_title[14:len(our_title)]},dm={q_par.dmax}")
    ax1.set_xlabel("passing time, MR-CS")


    q_par.dmax = 6
    q_par.ppair = 20.0
    q_par.psum = 40.0
    q_par.annealing_time = 10
    our_qubo.qubo_real_6t(delays_list[0])
    _ax_hist_passing_times(ax2, our_qubo, q_par, p, add_text = False, dir="")
    our_title = plot_title(our_qubo, q_par)
    ax2.set_title(f"{our_title[14:len(our_title)]}, dmax={q_par.dmax}")
    ax2.set_xlabel("passing time, MR-CS")



    q_par.dmax = 6
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.annealing_time = 1000
    our_qubo.qubo_real_6t(delays_list[0])
    _ax_hist_passing_times(ax3, our_qubo, q_par, p, add_text = False, dir="")
    our_title = plot_title(our_qubo, q_par)
    ax3.set_title(f"{our_title[14:len(our_title)]},d={q_par.dmax}")
    ax3.set_xlabel("passing time, MR-CS")


    ax3.set_xlim(left=11, right = 21)
    ax3.set_xticks([12,14,16,18,20])

    ax2.set_xlim(left=11, right = 21)
    ax2.set_xticks([12,14,16,18,20])

    ax.sharex(ax2)
    ax1.sharex(ax3)

    fig.savefig("article_plots/6trains_DWave.pdf")
    fig.clf()



if __name__ == "__main__":
    plot2trains_dmax2_DWave()
    plot10_11trains_dmax6_DWave()
    plot6trains_intermediate()