""" main computation script """
import pickle
import os.path
#import matplotlib.pyplot as plt
import argparse

from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import solve_on_LP, prepare_qubo, solve_qubo, analyze_qubo_Dwave
from QTrains import display_prec_feasibility, make_plots_Dwave, approx_no_physical_qbits

from trains_timetable import Input_qubo, Comp_parameters



def plot_hist(q_input, q_pars):
    """ plot histograms of trains passing time from results from QUBO """

    make_plots_Dwave(q_input, q_pars)
    display_prec_feasibility(q_input, q_pars)



def process(q_input, q_pars):
    """ the sequence of calculation  makes computation if results has not been saved already"""


    file = file_QUBO(q_input, q_pars)
    if not os.path.isfile(file):
        prepare_qubo(q_input, q_pars)

    if q_pars.compute:

        file = file_LP_output(q_input, q_pars)
        if not os.path.isfile(file):
            solve_on_LP(q_input, q_pars)

        file = file_QUBO_comp(q_input, q_pars)
        if not os.path.isfile(file):
            solve_qubo(q_input, q_pars)

    if q_pars.analyze:
        try:
            file = file_hist(q_input, q_pars)
            if not os.path.isfile(file):
                analyze_qubo_Dwave(q_input, q_pars)

            plot_hist(q_input, q_pars)
        except:
            file = file_QUBO_comp(q_input, q_pars)
            print(" XXXXXXXXXXXXXXXXXXXXXX  ")
            print( f"not working for {file}" )


def get_no_physical_qbits(ret_dict, q_input, q_pars, trains):
    """ counts no physical q-bits update dict """
    no_logical, no_physical = approx_no_physical_qbits(q_input, q_pars)

    if q_input.delays != {}:
        ret_dict[f"{trains}_{q_pars.dmax}_disturbed"] = {"no_logical": no_logical, "no_physical": no_physical} 
    else:
        ret_dict[f"{trains}_{q_pars.dmax}_notdisturbed"] = {"no_logical": no_logical, "no_physical": no_physical} 


def count_no_qbits(qubo, parameters):
    """ counts no physical q-bits after embedding for 1 - 12 trains """
    delays_list = [{}, {1:5, 2:2, 4:5}]

    ret_dict = {}
    
    for d in [2,6]:
        parameters.dmax = d 

        for delays in delays_list:

            qubo.qubo_real_1t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, 1)

            qubo.qubo_real_2t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, 2)

            qubo.qubo_real_4t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, 4)

            qubo.qubo_real_6t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, 6)

            qubo.qubo_real_8t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, 8)

            qubo.qubo_real_10t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, 10)

            qubo.qubo_real_11t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, 11)

            qubo.qubo_real_12t(delays)
            get_no_physical_qbits(ret_dict, qubo, parameters, 12)

    return ret_dict



def series_of_computation(qubo, parameters):
    """ performs series of computation for 1 - 12 trains """
    delays_list = [{}, {1:5, 2:2, 4:5}]

    for delays in delays_list:

        qubo.qubo_real_1t(delays)
        process(qubo, parameters)

        qubo.qubo_real_2t(delays)
        process(qubo, parameters)

        qubo.qubo_real_4t(delays)
        process(qubo, parameters)

        qubo.qubo_real_6t(delays)
        process(qubo, parameters)

        qubo.qubo_real_8t(delays)
        process(qubo, parameters)

        qubo.qubo_real_10t(delays)
        process(qubo, parameters)

        qubo.qubo_real_11t(delays)
        process(qubo, parameters)

        qubo.qubo_real_12t(delays)
        process(qubo, parameters)


if __name__ == "__main__":


    parser = argparse.ArgumentParser("mode of problem solving: computation /  output analysis")

    parser.add_argument(
        "--mode",
        type=int,
        help="process mode: 0: prepare only QUBO, 1: make computation (ILP and annealing), 2: analyze outputs, 3: count q-bits ",
        default=2,
    )

    parser.add_argument(
        "--simulation",
        type=bool,
        help="if True solve / analyze output of simulated annealing (via DWave software), if False real annealing",
        default=False,
    )

    parser.add_argument(
        "--softern_pass",
        type=bool,
        help="if true analyze output without feasibility check on minimal passing time constrain",
        default=False,
    )


    args = parser.parse_args()


    q_par = Comp_parameters()
    q_par.softern_pass = args.softern_pass

    q_par.compute = False  # make computations / optimisation
    q_par.analyze = False  # Analyze results

    assert args.mode in [0,1,2,3]
    if args.mode in [1, 3]:
        q_par.compute = True   # make computations / optimisation
    elif args.mode == 2:
        q_par.analyze = True


    our_qubo = Input_qubo()
    

        
    if args.simulation:
        q_par.method = "sim"
        for d_max in [2]:
            q_par.dmax = d_max

            q_par.ppair = 2.0
            q_par.psum = 4.0
            series_of_computation(our_qubo, q_par)

            q_par.ppair = 20.0
            q_par.psum = 40.0
            series_of_computation(our_qubo, q_par)
    
    elif args.mode == 3:
        q_par.solver = "Advantage_system4.1"
        no_qbits = count_no_qbits(our_qubo, q_par)

        with open("solutions/embedding.json", 'wb') as fp:
            pickle.dump(no_qbits, fp)

    else:
        q_par.method = "real"
        q_par.solver = "Advantage_system6.3"
        for d_max in [2,6]:
            q_par.dmax = d_max
            for q_par.annealing_time in [10, 1000]:

                q_par.ppair = 2.0
                q_par.psum = 4.0
                series_of_computation(our_qubo, q_par)

                q_par.ppair = 20.0
                q_par.psum = 40.0
                series_of_computation(our_qubo, q_par)
    




