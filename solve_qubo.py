""" main computation script """
import pickle
import os.path
import matplotlib.pyplot as plt
import numpy as np


from trains_timetable import Input_qubo
from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import solve_on_LP, prepare_qubo, solve_qubo, analyze_qubo_Dwave
from QTrains import display_prec_feasibility, make_plots_Dwave

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=10)





def plot_hist(q_input, q_pars, p):
    """ plot histograms of trains passing time from results from QUBO """

    make_plots_Dwave(q_input, q_pars, p)
    display_prec_feasibility(q_input, q_pars, p)



def process(q_input, q_pars, p):
    """ the sequence of calculation  makes computation if results has not been saved already"""

    file = file_LP_output(q_input, q_pars, p)
    if not os.path.isfile(file):
        solve_on_LP(q_input, q_pars, p)

    file = file_QUBO(q_input, q_pars, p)
    if not os.path.isfile(file):
        prepare_qubo(q_input, q_pars, p)

    if p.compute:
        file = file_QUBO_comp(q_input, q_pars, p)
        if not os.path.isfile(file):
            solve_qubo(q_input, q_pars, p)

    if p.analyze:
        try:
            file = file_hist(q_input, q_pars, p)
            if not os.path.isfile(file):
                analyze_qubo_Dwave(q_input, q_pars, p)

            plot_hist(q_input, q_pars, p)
        except:
            file = file_QUBO_comp(q_input, q_pars, p)
            print(" XXXXXXXXXXXXXXXXXXXXXX  ")
            print( f"not working for {file}" )




class Comp_parameters():
    """ stores parameters of QUBO and computaiton """
    def __init__(self):
        self.M = 50
        self.num_all_runs = 25_000

        self.num_reads = 500
        assert self.num_all_runs % self.num_reads == 0

        self.ppair = 2.0
        self.psum = 4.0
        self.dmax = 10

        self.method = "sim"
        # for simulated annelaing
        self.beta_range = (0.001, 50)
        self.num_sweeps = 500
        # for real annealing
        self.annealing_time = 1000
        self.solver = "Advantage_system6.3"
        self.token = ""
        assert self.annealing_time * self.num_reads < 1_000_000


class Process_parameters():
    def __init__(self):
        self.compute = False
        self.analyze = False
        self.softern_pass = False
        self.delta = 0


def series_of_computation(qubo, parameters, p):
    """ performs series of computation for 1 - 12 trains """
    delays_list = [{}, {1:5, 2:2, 4:5}]

    for delays in delays_list:

        qubo.qubo_real_1t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_2t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_4t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_6t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_8t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_10t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_11t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_12t(delays)
        process(qubo, parameters,p)


if __name__ == "__main__":
    softer_passing_time_constr = False

    p = Process_parameters()

    # these 4 will be from args parse
    p.compute = False   # make computations / optimisation
    p.analyze = True    # Analyze results
    sim = False  # simulation of DWave
    p.softern_pass = softer_passing_time_constr

    our_qubo = Input_qubo()
    q_par = Comp_parameters()

        
    if sim:
        q_par.method = "sim"
        for d_max in [2,6]:
            q_par.dmax = d_max

            q_par.ppair = 2.0
            q_par.psum = 4.0
            series_of_computation(our_qubo, q_par, p)

            q_par.ppair = 20.0
            q_par.psum = 40.0
            series_of_computation(our_qubo, q_par, p)
    else:
        q_par.method = "real"
        for d_max in [2,6]:
            q_par.dmax = d_max
            for at in [10, 1000]:
                q_par.annealing_time = at

                q_par.ppair = 2.0
                q_par.psum = 4.0
                series_of_computation(our_qubo, q_par, p)

                q_par.ppair = 20.0
                q_par.psum = 40.0
                series_of_computation(our_qubo, q_par, p)
    




