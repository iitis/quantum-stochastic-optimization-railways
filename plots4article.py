import pickle
import os.path
import matplotlib.pyplot as plt
import numpy as np
import sys
 


from solve_qubo import Input_qubo, Comp_parameters, Process_parameters, file_QUBO, file_LP_output, make_plots
from solve_qubo import plot_title, _ax_hist_passing_times, _ax_objective



print("1")

real_problem = True
make_stochatic_qubos = False

p = Process_parameters()
p.analyze = True
#p.softern_pass = True
our_qubo = Input_qubo()
q_par = Comp_parameters()

q_par.method = "real"
q_par.dmax = 2
q_par.ppair = 2.0
q_par.psum = 4.0
q_par.annealing_time = 10

delays_list = [{}, {1:5, 2:2, 4:5}]
our_qubo.qubo_real_2t(delays_list[0])


fig, ax = plt.subplots(figsize=(4, 3))

_ax_hist_passing_times(ax, our_qubo, q_par, p, dir="")
our_title = plot_title(our_qubo, q_par)
fig.subplots_adjust(bottom=0.2, left = 0.15)
plt.title(our_title)

fig.savefig("article_plots/test.pdf")
fig.clf()