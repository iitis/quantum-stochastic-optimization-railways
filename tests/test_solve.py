import pickle
import os.path
import matplotlib.pyplot as plt
import numpy as np


#from scipy.optimize import linprog
#import neal
#from dwave.system import (    EmbeddingComposite,    DWaveSampler)

from QTrains import QuboVars, Parameters, Railway_input, Analyze_qubo, Variables, LinearPrograming
#from QTrains import update_hist
from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import solve_on_LP, prepare_qubo, solve_qubo, analyze_qubo
from QTrains import display_results


# input

class Input_qubo():
    """ store railway parameters """
    def __init__(self):
        self.stay = 1
        self.headways = 2
        self.preparation_t = 3
        self.circ = {}
        self.timetable = {}
        self.objective_stations = []
        self.delays = {}
        self.file = ""
        self.notrains = 0

    # these are test instances

    def qubo1(self):
        """
        two trains one following other not disturbed
        """
        self.circ = {}
        self.timetable = {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
        self.objective_stations = ["MR", "CS"]
        self.delays = {}
        self.file = "QUBOs/qubo_1"
        self.notrains = 2

    def qubo2(self):
        """ 
        two trains one following other disturbed
        """
        self.circ = {}
        self.timetable = {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
        self.objective_stations = ["MR", "CS"]
        self.delays = {3:2}
        self.file = "QUBOs/qubo_2"
        self.notrains = 2


class Comp_parameters():
    """ stores parameters of QUBO and computaiton """
    def __init__(self):
        self.M = 50
        self.num_all_runs = 1_000

        self.num_reads = 500
        assert self.num_all_runs % self.num_reads == 0

        self.ppair = 2.0
        self.psum = 4.0
        self.dmax = 6

        # for simulated annelaing
        self.method = "sim"
        self.beta_range = (0.001, 50)
        self.num_sweeps = 500


class Process_parameters():
    def __init__(self):
        self.softern_pass = False
        self.delta = 0


def test_file_names():
     # testing

    q_input = Input_qubo()
    q_input.qubo1()
    #q_input.qubo2()
    q_pars = Comp_parameters()
    q_pars.dmax = 5
    q_pars.method = "sim"
    p = Process_parameters()

    file = file_LP_output(q_input, q_pars, p)
    assert file == "solutions/LP_1_5.json"

    file = file_QUBO(q_input, q_pars, p)
    assert file == "QUBOs/qubo_1_5_2.0_4.0.json"

    file = file_QUBO_comp(q_input, q_pars, p)
    assert file ==  "solutions/qubo_1_5_2.0_4.0_sim_1000_0.001_500.json"

    file = file_hist(q_input, q_pars, p)
    assert file == "histograms/qubo_1_5_2.0_4.0_sim_1000_0.001_500.json"


def test_solving_process():
     # testing

    q_input = Input_qubo()
    q_input.qubo1()
    #q_input.qubo2()
    q_pars = Comp_parameters()
    q_pars.dmax = 5
    q_pars.method = "sim"
    p = Process_parameters()


    solve_on_LP(q_input, q_pars, p)

    file = file_LP_output(q_input, q_pars, p)
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)

    print(lp_sol)

    assert list(lp_sol["variables"].keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert lp_sol["objective"] == 0

    assert lp_sol["variables"]['t_PS_1'].value == 0
    assert lp_sol["variables"]['t_MR_1'].value == 3
    assert lp_sol["variables"]['t_CS_1'].value == 16
    assert lp_sol["variables"]['t_MR_3'].value == 0
    assert lp_sol["variables"]['t_CS_3'].value == 13
    assert lp_sol["variables"]['y_MR_1_3'].value == 0
    assert lp_sol["variables"]['y_CS_1_3'].value == 0


    prepare_qubo(q_input, q_pars, p)
    
    file = file_QUBO(q_input, q_pars, p)
    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_read)
    assert  qubo_to_analyze.objective  == {(6, 6): 0.0, (7, 7): 0.2, (8, 8): 0.4, (9, 9): 0.6, (10, 10): 0.8, (11, 11): 1.0,
                                           (12, 12): 0.0, (13, 13): 0.2, (14, 14): 0.4, (15, 15): 0.6, (16, 16): 0.8,
                                            (17, 17): 1.0, (18, 18): 0.0, (19, 19): 0.2, (20, 20): 0.4, (21, 21): 0.6,
                                            (22, 22): 0.8, (23, 23): 1.0, (24, 24): 0.0, (25, 25): 0.2, (26, 26): 0.4,
                                            (27, 27): 0.6, (28, 28): 0.8, (29, 29): 1.0}

    assert qubo_to_analyze.sum_ofset == 20.0
    assert qubo_to_analyze.headway_constrain == {(6, 14): 2.0, (14, 6): 2.0, (6, 15): 2.0, (15, 6): 2.0, (6, 16): 2.0,
                                                (16, 6): 2.0, (7, 15): 2.0, (15, 7): 2.0, (7, 16): 2.0, (16, 7): 2.0,
                                                (7, 17): 2.0, (17, 7): 2.0, (8, 16): 2.0, (16, 8): 2.0, (8, 17): 2.0,
                                                (17, 8): 2.0, (9, 17): 2.0, (17, 9): 2.0, (18, 26): 2.0, (26, 18): 2.0,
                                                (18, 27): 2.0, (27, 18): 2.0, (18, 28): 2.0, (28, 18): 2.0,
                                                (19, 27): 2.0, (27, 19): 2.0, (19, 28): 2.0, (28, 19): 2.0,
                                                (19, 29): 2.0, (29, 19): 2.0, (20, 28): 2.0, (28, 20): 2.0,
                                                (20, 29): 2.0, (29, 20): 2.0, (21, 29): 2.0, (29, 21): 2.0}


    assert qubo_to_analyze.circ_constrain == {}
    assert qubo_to_analyze.noqubits == 30
    Q = qubo_to_analyze.qubo
    assert len(Q.keys()) == 306  # Number of non-zero couplings

    solve_qubo(q_input, q_pars, p)

    qubo_to_analyze = Analyze_qubo(dict_read)
    file = file_QUBO_comp(q_input, q_pars, p)
    print( file )
    with open(file, 'rb') as fp:
        samplesets = pickle.load(fp)

    assert list(samplesets.keys()) == [0, 1]

    assert len(samplesets[0]) == 500

    energies = []
    for (sol, energy, occ) in samplesets[0].record:
        energies.append(energy)
        assert len(sol) == 30
    
    objective = 0
    assert np.min(energies) + qubo_to_analyze.sum_ofset == objective


    analyze_qubo(q_input, q_pars, p)

            #plot_hist(q_input, q_pars, p)
        #else: