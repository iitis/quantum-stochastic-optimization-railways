""" prepare inputs and analyze outputs from quantum annelaing """
import pickle
import os.path
import argparse
import json
import numpy as np


from dimod import utilities

from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import solve_on_LP, prepare_qubo, solve_qubo, analyze_qubo_Dwave ,analyze_chain_strength
from QTrains import display_prec_feasibility, plot_hist_pass_obj, approx_no_physical_qbits, Analyze_qubo
from QTrains import classical_benchmark

from trains_timetable import Input_timetable, Comp_parameters



def prepare_Ising(trains_input, q_pars):
    qubo_file = file_QUBO(trains_input, q_pars)

    with open(qubo_file, 'rb') as fp:
        dict_read = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_read)
    Q = qubo_to_analyze.qubo

    Ising = utilities.qubo_to_ising(Q, offset=0.0)
    print("compute")

    ising_file = qubo_file.replace("qubo_", "ising_").replace("QUBOs", "Ising").replace(".json", ".pkl")

    if not os.path.isfile(ising_file):
        print("save")

        with open(ising_file, 'wb') as fp:
            pickle.dump(Ising, fp)





def process(trains_input, q_pars):
    """ the sequence of calculation  makes computation if results has not been saved already"""


    qubo_file = file_QUBO(trains_input, q_pars)
    lp_file = file_LP_output(trains_input, q_pars)
    qubo_output_file = file_QUBO_comp(trains_input, q_pars)
    hist_file = file_hist(trains_input, q_pars)


    if not os.path.isfile(qubo_file):
        prepare_qubo(trains_input, q_pars, qubo_file)

    if q_pars.compute:

        if not os.path.isfile(lp_file):
            solve_on_LP(trains_input, q_pars, lp_file)

        if not os.path.isfile(qubo_output_file):
            solve_qubo(q_pars, qubo_file, qubo_output_file)

    if q_pars.analyze:
        try:
            if not os.path.isfile(hist_file):
                analyze_qubo_Dwave(trains_input, q_pars, qubo_file, lp_file, qubo_output_file, hist_file)

            file_pass = hist_file.replace(".json", f"{trains_input.objective_stations[0]}_{trains_input.objective_stations[1]}.pdf")
            file_obj = hist_file.replace(".json", "obj.pdf")
            plot_hist_pass_obj(trains_input, q_pars, hist_file, file_pass, file_obj)
            display_prec_feasibility(trains_input, q_pars, hist_file)
        except Exception as e:
            print(" XXXXXXXXXXXXXXXXXXXXXX  ")
            print( f"not working for {qubo_output_file}" )
            print(f"{e}")



def chain_strength(trains_input, q_pars, result):
    """ the sequence of calculation  makes computation if results has not been saved already"""

    qubo_output_file = file_QUBO_comp(trains_input, q_pars)

    broken_fraction = analyze_chain_strength(qubo_output_file)

    hist = np.histogram(broken_fraction)

    result[trains_input.notrains] = {"min": np.min(broken_fraction), "max": np.max(broken_fraction), "histogram": hist}




def get_no_physical_qbits(ret_dict, trains_input, q_pars, trains):
    """ counts no physical q-bits update dict """
    no_logical, no_physical = approx_no_physical_qbits(trains_input, q_pars)

    if trains_input.delays != {}:
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
        help="process mode: 0: prepare only QUBO, 1: make computation (ILP and annealing), 2: analyze outputs, 3: count q-bits, 4: save Ising  5: CPLEX benchmark ^: analyze chain strength",
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

    assert args.mode in [0,1,2,3,4,5,6]
    if args.mode in [1, 3]:
        q_par.compute = True   # make computations / optimisation
    elif args.mode == 2:
        q_par.analyze = True


    our_qubo = Input_timetable()


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

    elif args.mode == 4:

        q_pars = Comp_parameters()
        our_qubo = Input_timetable()

        q_pars.compute = False  # make computations / optimisation
        q_pars.analyze = False
        q_pars.dmax = 6
        q_pars.ppair = 2.0
        q_pars.psum = 4.0

        delays_list = [{}, {1:5, 2:2, 4:5}]
        for delays in delays_list:
        
            our_qubo.qubo_real_2t(delays)
            prepare_Ising(our_qubo, q_pars)

            our_qubo.qubo_real_6t(delays)
            prepare_Ising(our_qubo, q_pars)

            our_qubo.qubo_real_11t(delays)
            prepare_Ising(our_qubo, q_pars)

    elif args.mode == 5:

        q_par = Comp_parameters()
        trains_input = Input_timetable()
        all_results = {}


        for d_max in [2, 6]:
            q_par.dmax = d_max

            
            delays_list = [{}, {1:5, 2:2, 4:5}]
            for delays in delays_list:

                results = {}

                trains_input.qubo_real_1t(delays)
                classical_benchmark(trains_input, q_par, results)

                trains_input.qubo_real_2t(delays)
                classical_benchmark(trains_input, q_par, results)

                trains_input.qubo_real_4t(delays)
                classical_benchmark(trains_input, q_par, results)


                trains_input.qubo_real_6t(delays)
                classical_benchmark(trains_input, q_par, results)

                trains_input.qubo_real_8t(delays)
                classical_benchmark(trains_input, q_par, results)

                trains_input.qubo_real_10t(delays)
                classical_benchmark(trains_input, q_par, results)

                trains_input.qubo_real_11t(delays)
                classical_benchmark(trains_input, q_par, results)

                trains_input.qubo_real_12t(delays)
                classical_benchmark(trains_input, q_par, results)

                if len(delays) == 0:
                    all_results[f"no_delays_dmax{d_max}"] = results
                else:
                    all_results[f"delays_dmax{d_max}"] = results
                
            #print(all_results)
        with open('solutions/cplex_benchmarks.json', 'w') as json_file:
            json.dump(all_results, json_file, indent=4)

    
    if args.mode == 6:
        if not args.simulation:
            

            q_par = Comp_parameters()
            trains_input = Input_timetable()
            q_par.method = "real"

            all_results = {}

            for d_max in [2, 6]:
                q_par.dmax = d_max
                for q_par.annealing_time in [10, 1000]:

                    print(f"###############  annealing time {q_par.annealing_time}")


                    delays_list = [{}, {1:5, 2:2, 4:5}]
                    for delays in delays_list:

                        result = {}

                        trains_input.qubo_real_1t(delays)
                        chain_strength(trains_input, q_par, result)

                        trains_input.qubo_real_2t(delays)
                        chain_strength(trains_input, q_par, result)

                        trains_input.qubo_real_4t(delays)
                        chain_strength(trains_input, q_par, result)


                        trains_input.qubo_real_6t(delays)
                        chain_strength(trains_input, q_par, result)

                        trains_input.qubo_real_8t(delays)
                        chain_strength(trains_input, q_par, result)

                        trains_input.qubo_real_10t(delays)
                        chain_strength(trains_input, q_par, result)

                        trains_input.qubo_real_11t(delays)
                        chain_strength(trains_input, q_par, result)


                        print(result)

                    
                if len(delays) == 0:
                    all_results[f"no_delays_dmax{d_max}_at{q_par.annealing_time}"] = result
                else:
                    all_results[f"delays_dmax{d_max}_at{q_par.annealing_time}"] = result
                
        print(all_results)
        #with open('solutions/chain_strength.json', 'w') as json_file:
            #json.dump(all_results, json_file, indent=4)



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
    