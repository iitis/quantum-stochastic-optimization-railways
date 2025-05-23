""" test solving trains problems """
import pickle
import numpy as np
import matplotlib.pyplot as plt

from QTrains import Analyze_qubo
from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import solve_on_LP, prepare_qubo, solve_qubo, analyze_qubo_Dwave
from QTrains import display_prec_feasibility, plot_hist_pass_obj
from QTrains import plot_title, _ax_hist_passing_times, _ax_objective, passing_time_histigrams, objective_histograms, energies_histograms
from QTrains import analyze_QUBO_outputs, get_solutions_from_dmode, save_qubo_4gates_comp, first_with_given_objective



# input

class Input_timetable():
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


class Comp_parameters():
    """ stores parameters of QUBO and computaiton """
    def __init__(self):
        self.M = 50
        self.num_all_runs = 1_000

        self.num_reads = 500
        assert self.num_all_runs % self.num_reads == 0

        self.ppair = 2.0
        self.psum = 4.0
        self.dmax = 5

        # for simulated annelaing
        self.method = "sim"
        self.beta_range = (0.001, 50)
        self.num_sweeps = 500

        self.softern_pass = False
        self.delta = 0


def test_file_names():
    """ 
    test file name strings for saving results in subsequent steps of 
    solving process
    """

    trains_input = Input_timetable()
    trains_input.qubo1()
    q_pars = Comp_parameters()

    file = file_LP_output(trains_input, q_pars)
    assert file == "solutions/LP_1_5.json"

    file = file_QUBO(trains_input, q_pars)
    assert file == "QUBOs/qubo_1_5_2.0_4.0.json"

    file = file_QUBO_comp(trains_input, q_pars)
    assert file ==  "solutions/qubo_1_5_2.0_4.0_sim_1000_0.001_500.json"

    file = file_hist(trains_input, q_pars)
    assert file == "histograms/qubo_1_5_2.0_4.0_sim_1000_0.001_500.json"


def test_solving_process():
    """
    test solving process via ILP 
    and steps of QUBO creation
    """
    trains_input = Input_timetable()
    trains_input.qubo1()
    q_pars = Comp_parameters()

    # LP solving
    file = "tests/files/test_LP.json"
    solve_on_LP(trains_input, q_pars, file)

    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)


    assert list(lp_sol["variables"].keys()) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert lp_sol["objective"] == 0

    assert lp_sol["variables"]['t_PS_1'].value == 0
    assert lp_sol["variables"]['t_MR_1'].value == 3
    assert lp_sol["variables"]['t_CS_1'].value == 16
    assert lp_sol["variables"]['t_MR_3'].value == 0
    assert lp_sol["variables"]['t_CS_3'].value == 13
    assert lp_sol["variables"]['y_MR_1_3'].value == 0
    assert lp_sol["variables"]['y_CS_1_3'].value == 0


    file = "tests/files/test_QUBO.json"
    prepare_qubo(trains_input, q_pars, file)

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

def test_solving_QUBO():
    """ test solving QUBO """
    trains_input = Input_timetable()
    trains_input.qubo1()
    q_pars = Comp_parameters()

    input_file = "tests/files/test_QUBO.json"
    output_file = "tests/files/test_QUBO_output.json"

    solve_qubo(q_pars, input_file, output_file)

    with open(input_file, 'rb') as fp:
        dict_read = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_read)

    with open(output_file, 'rb') as fp:
        samplesets = pickle.load(fp)

    assert list(samplesets.keys()) == [0, 1]

    assert len(samplesets[0]) == 500

    energies = []
    for (sol, energy, _) in samplesets[0].record:
        energies.append(energy)
        assert len(sol) == 30

    objective = 0
    assert np.min(energies) + qubo_to_analyze.sum_ofset == objective


    sols = get_solutions_from_dmode(samplesets, q_pars)
    assert len(sols) == 1000

    file = file = "tests/files/test_LP.json"
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)

    sol = first_with_given_objective(sols, qubo_to_analyze, lp_sol["objective"])
    assert qubo_to_analyze.objective_val(sol) == objective


def test_qubo_analysis():
    """ test the analysis of the QUBO opimisation results """
    trains_input = Input_timetable()
    trains_input.qubo1()
    q_pars = Comp_parameters()

    qubo_file = "tests/files/test_QUBO.json"
    lp_file = "tests/files/test_LP.json"
    qubo_output_file = "tests/files/test_QUBO_output.json"
    hist_file = "tests/files/test_hist.json"

    analyze_qubo_Dwave(trains_input, q_pars, qubo_file, lp_file, qubo_output_file, hist_file)

    with open(hist_file, 'rb') as fp:
        results = pickle.load(fp)

    hist_obj = results["qubo objectives"]
    ground = results["lp objective"]
    assert results["perc feasible"] > 0.95
    assert results["no qubits"] == 30
    assert results["no qubo terms"] == 306

    assert ground == 0.0
    assert np.min(hist_obj) == 0.0
    histogram_obj = [hist_obj.count(x) for x in set(hist_obj)]
    assert np.sum(histogram_obj) == 1000*results["perc feasible"]
    for i in range(5):
        assert histogram_obj[i] > 2


    hist_pass = results[f"{trains_input.objective_stations[0]}_{trains_input.objective_stations[1]}"]

    xs = list( range(np.max(hist_pass) + 1) )
    histogram_pass = [hist_pass.count(x) for x in xs]


    assert np.sum(histogram_pass) == 2*1000*results["perc feasible"]  # there are 2 trains
    assert histogram_pass[0:12] == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    test_list = histogram_pass[12:17]
    test_list.sort(reverse=True)
    assert histogram_pass[12:17]==test_list  # decreasing histogram

    hist_e = energies_histograms(hist_file)
    hist_o = objective_histograms(hist_file)
    hist_p = passing_time_histigrams(trains_input, q_pars, hist_file)

    assert hist_e["ground_state"] == -20
    assert np.min(hist_e["feasible_value"]) == -20
    assert sum(hist_e["feasible_count"]) + sum(hist_e["notfeasible_count"]) == 1000
    assert hist_o["ground_state"] == 0
    assert sum(hist_e["feasible_count"]) == sum(hist_o["count"])
    assert sum(hist_p["count"]) == 2*sum(hist_o["count"])

    # plotting auxiliary
    plot_tit = plot_title(trains_input, q_pars)
    assert plot_tit == "Not disturbed, sim, ppair=2, psum=4"
    _, ax = plt.subplots(figsize=(4, 3))
    _ax_objective(ax, hist_o)
    _ax_hist_passing_times(ax, hist_p)
    plt.clf()


def test_plotting():
    """ test trains plots """
    trains_input = Input_timetable()
    trains_input.qubo1()
    q_pars = Comp_parameters()
    q_pars.method = "sim"

    hist_file = "tests/files/test_hist.json"

    file_pass = hist_file.replace(".json", f"{trains_input.objective_stations[0]}_{trains_input.objective_stations[1]}.pdf")
    file_obj = hist_file.replace(".json", "obj.pdf")

    plot_hist_pass_obj(trains_input, q_pars, hist_file, file_pass, file_obj)
    display_prec_feasibility(trains_input, q_pars, hist_file)



def test_gates():
    """ 
    test auxiliary functions for quantum gates and 
    analysis of quantum gate outputs 
    """
    trains_input = Input_timetable()
    trains_input.qubo1()
    q_pars = Comp_parameters()
    q_pars.method = "IonQsim"

    file = "tests/files/test_LP.json"
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)

    file = "tests/files/test_QUBO.json"
    with open(file, 'rb') as fp:
        dict_qubo = pickle.load(fp)

    Q = Analyze_qubo(dict_qubo)
    qubo_solution = Q.int_vars2qubo(lp_sol["variables"])
    all_solutions = Q.heuristics_degenerate(qubo_solution, "PS")
    ret = analyze_QUBO_outputs(Q, trains_input.objective_stations, all_solutions, lp_sol, q_pars.softern_pass)

    assert ret == {'perc feasible': 1.0, 'MR_CS': [12, 12], 'no qubits': 30,
                   'no qubo terms': 306, 'lp objective': 0.0,
                   'q ofset': 20.0, 'qubo objectives': [0.0],
                   'energies feasible': [-Q.sum_ofset], 'energies notfeasible': []}


    test_f = "tests/files/qubo_and_ground.json"
    save_qubo_4gates_comp(dict_qubo, all_solutions, test_f)

    with open(test_f, 'rb') as fp:
        dict_read = pickle.load(fp)

    assert dict_read["ground_solutions"] == all_solutions
    assert dict_read["ground_energy"] == Q.energy(qubo_solution)
