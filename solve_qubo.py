""" main computation script """
import pickle
import os.path
import matplotlib.pyplot as plt
import numpy as np


from trains_timetable import Input_qubo
from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import solve_on_LP, prepare_qubo, solve_qubo, analyze_qubo_Dwave
from QTrains import display_prec_feasibility, make_plots_Dwave, approx_no_physical_qbits

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


def get_no_physical_qbits(ret_dict, q_input, q_pars, p, trains):
    """ counts no physical q-bits update dict """
    no_logical, no_physical = approx_no_physical_qbits(q_input, q_pars, p)

    if q_input.delays != {}:
        ret_dict[f"{trains}_{q_pars.dmax}_disturbed"] = {"no_logical": no_logical, "no_physical": no_physical} 
    else:
        ret_dict[f"{trains}_{q_pars.dmax}_notdisturbed"] = {"no_logical": no_logical, "no_physical": no_physical} 


def count_no_qbits(qubo, parameters, p):
    """ counts no physical q-bits after embedding for 1 - 12 trains """
    delays_list = [{}, {1:5, 2:2, 4:5}]

    ret_dict = {}


    
    for d in [2,6]:
        parameters.dmax = d 

        for delays in delays_list:

            qubo.qubo_real_1t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, p, 1)

            qubo.qubo_real_2t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, p, 2)

            qubo.qubo_real_4t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, p, 4)

            qubo.qubo_real_6t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, p, 6)

            qubo.qubo_real_8t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, p, 8)

            qubo.qubo_real_10t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, p, 10)

            qubo.qubo_real_11t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, p, 11)

            qubo.qubo_real_12t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, p, 12)

    return ret_dict



class Comp_parameters():
    """ stores parameters of QUBO and computaiton """
    def __init__(self):
        self.M = 50
        self.num_all_runs = 25_000

        self.num_reads = 500
        assert self.num_all_runs % self.num_reads == 0

        self.ppair = 2.0
        self.psum = 4.0
        self.dmax = 6

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
    softer_passing_time_constr = True

    p = Process_parameters()

    # these 4 will be from args parse
    p.compute = False   # make computations / optimisation
    p.analyze = True    # Analyze results
    sim = False  # simulation of DWave
    count = False # estimates n.o. physical q-bits
    p.softern_pass = softer_passing_time_constr

    our_qubo = Input_qubo()
    q_par = Comp_parameters()

        
    if sim:
        q_par.method = "sim"
        for d_max in [3]:
            q_par.dmax = d_max

            q_par.ppair = 2.0
            q_par.psum = 4.0
            series_of_computation(our_qubo, q_par, p)

            q_par.ppair = 20.0
            q_par.psum = 40.0
            series_of_computation(our_qubo, q_par, p)
    
    elif count:
        q_par.solver = "Advantage_system4.1"
        no_qbits = count_no_qbits(our_qubo, q_par, p)

        with open("solutions/embedding.json", 'wb') as fp:
            pickle.dump(no_qbits, fp)

    
    else:
        q_par.method = "real"
        q_par.solver = "Advantage_system6.3"
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
    




