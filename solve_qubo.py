""" main computation script """
import pickle
import os.path
import matplotlib.pyplot as plt
import numpy as np
import pytest

from scipy.optimize import linprog
import neal
from dwave.system import (
    EmbeddingComposite,
    DWaveSampler
)

from QTrains import QuboVars, Parameters, Railway_input, Analyze_qubo, Variables, LinearPrograming
from QTrains import diff_passing_times



def file_LP_output(q_input, q_pars):
    """ returns string, the file name and dir to store LP results """
    file = q_input.file
    file = file.replace("qubo", "LP")
    file = f"{file}_{q_pars.dmax}.json"
    file = file.replace("QUBOs", "solutions")
    return file


def file_QUBO(q_input, q_pars):
    """ returns string, the file name and dir to store QUBO and its features """
    file = f"{q_input.file}_{q_pars.dmax}_{q_pars.ppair}_{q_pars.psum}.json"
    return file

def file_QUBO_comp(file, q_pars):
    """ returns string, the file name and dir to store results of computaiton on QUBO """
    file = file.replace("QUBOs", "solutions")
    if q_pars.method == "sim":
        file = file.replace(".json", f"_{q_pars.method}_{q_pars.num_all_runs}_{q_pars.beta_range[0]}_{q_pars.num_sweeps}.json")
    elif q_pars.method == "real":
        file = file.replace(".json", f"_{q_pars.method}_{q_pars.num_all_runs}_{q_pars.annealing_time}.json")
    return file


def solve_on_LP(q_input, q_pars):
    """ solve the problem using LP, and save results """
    stay = q_input.stay
    headways = q_input.headways
    preparation_t = q_input.preparation_t

    timetable = q_input.timetable
    objective_stations = q_input.objective_stations
    circulation = q_input.circ
    delays = q_input.delays
    file = q_input.file

    dmax = q_pars.dmax

    file = file.replace("QUBOs", "solutions")
    p = Parameters(timetable, stay=stay, headways=headways,
                   preparation_t=preparation_t, dmax=dmax, circulation=circulation)
    rail_input = Railway_input(p, objective_stations, delays = delays)
    v = Variables(rail_input)
    bounds, integrality = v.bonds_and_integrality()
    problem = LinearPrograming(v, rail_input, M = q_pars.M)
    opt = linprog(c=problem.obj, A_ub=problem.lhs_ineq,
                  b_ub=problem.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)
    v.linprog2vars(opt)

    v.check_clusters()

    d = {}
    d["variables"] = v.variables
    d["objective"] = problem.compute_objective(v, rail_input)

    file = file_LP_output(q_input, q_pars)
    with open(file, 'wb') as fp:
        pickle.dump(d, fp)



def prepare_qubo(q_input, q_pars):
    """ create and save QUBO given railway input and parameters """
    stay = q_input.stay
    headways = q_input.headways
    preparation_t = q_input.preparation_t

    timetable = q_input.timetable
    objective_stations = q_input.objective_stations
    circulation = q_input.circ
    delays = q_input.delays
    file = q_input.file

    ppair = q_pars.ppair
    psum = q_pars.psum
    dmax = q_pars.dmax

    p = Parameters(timetable, stay=stay, headways=headways,
                   preparation_t=preparation_t, dmax=dmax, circulation=circulation)
    rail_input = Railway_input(p, objective_stations, delays = delays)
    q = QuboVars(rail_input, ppair=ppair, psum=psum)
    q.make_qubo(rail_input)
    qubo_dict = q.store_in_dict(rail_input)

    file = file_QUBO(q_input, q_pars)
    with open(file, 'wb') as fp:
        pickle.dump(qubo_dict, fp)


def solve_qubo(q_input, q_pars):
    """ solve the problem given by QUBO and store results """
    file = file_QUBO(q_input, q_pars)

    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_read)
    Q = qubo_to_analyze.qubo

    sampleset = {}
    loops = q_pars.num_all_runs // q_pars.num_reads
    if q_pars.method == "sim":
        for k in range(loops):
            s = neal.SimulatedAnnealingSampler()
            sampleset[k] = s.sample_qubo(
                Q, beta_range = q_pars.beta_range, num_sweeps = q_pars.num_sweeps,
                num_reads = q_pars.num_reads, beta_schedule_type="geometric"
            )

    elif q_pars.method == "real":
        sampler = EmbeddingComposite(DWaveSampler())

        for k in range(loops):

            sampleset[k] = sampler.sample_qubo(
                Q,
                num_reads=q_pars.num_reads,
                annealing_time=q_pars.annealing_time
        )

    file = file_QUBO_comp(file, q_pars)
    with open(file, 'wb') as fp:
        pickle.dump(sampleset, fp)


def analyze_qubo(q_input, q_pars):
    """ analyze results of computation on QUBO and comparison with LP """
    show_var_vals = False
    file = file_QUBO(q_input, q_pars)
    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    file1 = file_LP_output(q_input, q_pars)
    with open(file1, 'rb') as fp:
        lp_sol = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_read)

    file = file_QUBO_comp(file, q_pars)
    with open(file, 'rb') as fp:
        samplesets = pickle.load(fp)
    
    hist = list([])
    qubo_objectives = list([])
    count = 0
    no_feasible = 0
    for sampleset in samplesets.values():
        for sample in sampleset.samples():
            sol = list(sample.values())
            count += 1
            if qubo_to_analyze.count_broken_constrains(sol) == (0,0,0,0):
                if qubo_to_analyze.broken_MO_conditions(sol) == 0:
                    no_feasible += 1
                    q_objective = qubo_to_analyze.objective_val(sol)

                    assert q_objective == pytest.approx( qubo_to_analyze.energy(sol) + qubo_to_analyze.sum_ofset )

                    vq = qubo_to_analyze.qubo2int_vars(sol)
                    h = diff_passing_times(lp_sol["variables"], vq, q_input.objective_stations, qubo_to_analyze.trains_paths)
                    hist.extend( h )
                    qubo_objectives.append( q_objective )
    perc_feasible = no_feasible/count

    if show_var_vals:
        for v in lp_sol["variables"]:
            print(v, lp_sol["variables"][v].value, lp_sol["variables"][v].range )

    results = {"perc feasible": perc_feasible, f"{q_input.objective_stations[0]}_{q_input.objective_stations[1]}": hist}
    results["no qubits"] = qubo_to_analyze.noqubits
    results["no qubo terms"] = len(qubo_to_analyze.qubo)
    results["lp objective"] = lp_sol["objective"]
    results["qubo objectives"] = qubo_objectives

    file = file.replace("solutions", "histograms")
    with open(file, 'wb') as fp:
        pickle.dump(results, fp)


def display_results(res_dict, q_pars, q_input):
    """ print results of computation """
    print("xxxxxxxxx    RESULTS     xxxxxx ", q_input.file,  "xxxxx")
    print(  )
    print("method", q_pars.method)
    print("psum", q_pars.psum)
    print("ppair", q_pars.ppair)
    print("LP objective", res_dict["lp objective"])

    if q_pars.method == "real":
        print("annealing time", q_pars.annealing_time)
    print("no qubits", res_dict["no qubits"])
    print("no qubo terms", res_dict["no qubo terms"])
    print("percentage of feasible", res_dict["perc feasible"])


def plot_hist(q_input, q_pars):
    """ plot histograms of trains passing time from results from QUBO """
    file = file_QUBO(q_input, q_pars)
    file = file_QUBO_comp(file, q_pars)
    file = file.replace("solutions", "histograms")

    with open(file, 'rb') as fp:
        results = pickle.load(fp)

        hist_pass = results[f"{q_input.objective_stations[0]}_{q_input.objective_stations[1]}"]

        plt.bar(*np.unique(hist_pass, return_counts=True))
        file_pass = file.replace(".json", f"{q_input.objective_stations[0]}_{q_input.objective_stations[1]}.pdf")
        if q_pars.method == "sim":
            plt.title(f"{q_input.file}, {q_pars.method}, dmax={q_pars.dmax}, ppair={q_pars.ppair}, psum={q_pars.psum}")
        else:
            plt.title(f"{q_input.file}, ammeal_time={q_pars.annealing_time}, dmax={q_pars.dmax}, ppair={q_pars.ppair}, psum={q_pars.psum}")
        plt.xlabel(f"Passing times between {q_input.objective_stations[0]} and {q_input.objective_stations[1]} comparing with ILP")
        plt.ylabel("number of solutions")
        plt.savefig(file_pass)
        plt.clf()

        hist_obj = results["qubo objectives"]


        file_pass = file.replace(".json", "obj.pdf")
        plt.hist(hist_obj, color = "gray", label = "QUBO")
        plt.axvline(x = results["lp objective"], lw = 3, color = 'red', label = 'ILP')
        if q_pars.method == "sim":
            plt.title(f"{q_input.file}, {q_pars.method}, dmax={q_pars.dmax}, ppair={q_pars.ppair}, psum={q_pars.psum}")
        else:
            plt.title(f"{q_input.file}, ammeal_time={q_pars.annealing_time}, dmax={q_pars.dmax}, ppair={q_pars.ppair}, psum={q_pars.psum}")
        plt.legend()
        plt.xlabel("Objective")
        plt.ylabel("density")
        plt.savefig(file_pass)
        plt.clf()

        display_results(results, q_pars, q_input)



def process(q_input, q_pars):
    """ the sequence of calculation  makes computation if results has not been saved already"""
    file = file_LP_output(q_input, q_pars)
    if not os.path.isfile(file):
        solve_on_LP(q_input, q_pars)

    file = file_QUBO(q_input, q_pars)
    if not os.path.isfile(file):
        prepare_qubo(q_input, q_pars)

    file = file_QUBO_comp(file, q_pars)
    if not os.path.isfile(file):
        solve_qubo(q_input, q_pars)

    analyze_qubo(q_input, q_pars)
    plot_hist(q_input, q_pars)



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

    def qubo1(self):
        """
        two trains one following other
        """
        self.circ = {}
        self.timetable = {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
        self.objective_stations = ["MR", "CS"]
        self.delays = {3:2}
        self.file = "QUBOs/qubo_1"

    def qubo2(self):
        """ 
        four - trains  3 going one direction and one going around at "CS"
        """
        self.circ = {(3,4): "CS"}
        self.timetable = {"PS": {1: 0, 4:33}, "MR" :{1: 3, 3: 0, 5:5, 4:30}, "CS" : {1: 16 , 3: 13, 4:17, 5:18}}
        self.objective_stations = ["MR", "CS"]
        self.delays = {3:2}
        self.file = "QUBOs/qubo_2"

    # real live problems plus PS - CS and back

    def qubo_real_12t(self, d):
        """
        12 trains

        8 trains from real live timetable
        added 2 pairs PS - CS - PS  number (11, 13, 12, 14)

        https://www.mta.maryland.gov/schedule/lightrail?origin=7640&destination=7646&direction=0&trip=3447009&schedule_date=12%2F06%2F2023&show_all=yes
        
        starts from 8 a.m.  0 -> 8:00  arr a minute before dep

        """
        self.circ = {(11,14): "CS", (12,13): "PS"}
        self.timetable = {"PS":{11:14, 12:40, 13:44, 14:58}, "MR":{1:12, 11:17, 3:22, 5:32, 7:42, 13:47, 0:20, 2:35, 12:37,  4:50, 14:55, 6:60}, 
                          "CS":{1:27, 11:32, 3:37, 5:47, 7:57, 13:62, 0:5, 2:20, 12:22, 4:35, 14:40, 6:45}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        self.file = f"QUBOs/LR_timetable/12trains/qubo_{d}_12t"


    def qubo_real_11t(self, d):
        """
        11 trains 
        
        7 trains from real live timetable
        added 2 pairs PS - CS - PS  number (11, 13, 12, 14)

        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS", (12,13): "PS"}
        self.timetable = {"PS":{11:14, 12:40, 13:44, 14:58}, "MR":{1:12, 11:17, 3:22, 5:32, 7:42, 13:47, 2:35, 12:37,  4:50, 14:55, 6:60}, 
                          "CS":{1:27, 11:32, 3:37, 5:47, 7:57, 13:62, 2:20, 12:22, 4:35, 14:40, 6:45}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        self.file = f"QUBOs/LR_timetable/11trains/qubo_{d}_11t"

    def qubo_real_10t(self, d):
        """
        10 trains 
        
        6 trains from real live timetable
        added 2 pairs PS - CS - PS  number (11, 13, 12, 14)

        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS", (12,13): "PS"}
        self.timetable = {"PS":{11:14, 12:40, 13:44, 14:58}, "MR":{1:12, 11:17, 3:22, 5:32, 7:42, 13:47, 2:35, 12:37, 4:50, 14:55}, 
                          "CS":{1:27, 11:32, 3:37, 5:47, 7:57, 13:62, 2:20, 12:22, 4:35, 14:40}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        self.file = f"QUBOs/LR_timetable/10trains/qubo_{d}_10t"

    def qubo_real_8t(self, d):
        """
        8 trains

        6 trains from real live timetable
        added 1 pair PS - CS - PS

        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS"}
        self.timetable = {"PS":{11:14, 14:58}, "MR":{1:12, 11:17, 3:22, 5:32, 2:35, 4:50, 14:55, 6:60}, 
                          "CS":{1:27, 11:32, 3:37, 5:47, 2:20, 4:35, 14:40, 6:45}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        self.file = f"QUBOs/LR_timetable/8trains/qubo_{d}_8t"


    def qubo_real_6t(self, d):
        """
        6 trains

        5 trains from real live timetable
        added 1 pair PS - CS - PS
        
        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS"}
        self.timetable = {"PS":{11:14, 14:58}, "MR":{1:12, 11:17, 3:22, 4:50, 14:55, 6:60}, 
                          "CS":{1:27, 11:32, 3:37, 4:35, 14:40, 6:45}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        self.file = f"QUBOs/LR_timetable/6trains/qubo_{d}_6t"

    


    def qubo_real_4t(self, d):
        """
        4 trains

        3 trains from real live timetable
        added 1 pair PS - CS - PS
        
        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS"}
        self.timetable = {"PS":{11:14, 14:58}, "MR":{1:12, 11:17, 4:50, 14:55}, 
                          "CS":{1:27, 11:32, 4:35, 14:40}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        self.file = f"QUBOs/LR_timetable/4trains/qubo_{d}_4t"


    def qubo_real_2t(self, d):
        """
        2 trains 1 pair PS - CS - PS
        
        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS"}
        self.timetable = {"PS":{11:14, 14:58}, "MR":{11:17, 14:55}, 
                          "CS":{11:32, 14:40}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        self.file = f"QUBOs/LR_timetable/2trains/qubo_{d}_2t"

    def qubo_real_1t(self, d):
        """
        smallest possible 1 train according to real live timetable
        """
        self.circ = {}
        self.timetable = {"MR":{1:12}, 
                          "CS":{1:27}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        self.file = f"QUBOs/LR_timetable/1train/qubo_{d}_1t"



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
        assert self.annealing_time * self.num_reads < 1_000_000


if __name__ == "__main__":

    real_problem = True

    if real_problem:

        our_qubo = Input_qubo()
        q_par = Comp_parameters()
        q_par.method = "sim"
        q_par.dmax = 10

        delays_list = [{}, {1:5}, {1:5, 4:5}, {1:5, 2:2, 4:5}]

        for delays in delays_list:

            our_qubo.qubo_real_1t(delays)
            process(our_qubo, q_par)

            our_qubo.qubo_real_2t(delays)
            process(our_qubo, q_par)

            our_qubo.qubo_real_4t(delays)
            process(our_qubo, q_par)

            our_qubo.qubo_real_6t(delays)
            process(our_qubo, q_par)

            our_qubo.qubo_real_8t(delays)
            process(our_qubo, q_par)

            our_qubo.qubo_real_10t(delays)
            process(our_qubo, q_par)

            our_qubo.qubo_real_11t(delays)
            process(our_qubo, q_par)

            our_qubo.qubo_real_12t(delays)
            process(our_qubo, q_par)



    else:

        our_qubo = Input_qubo()
        our_qubo.qubo1()
        q_par = Comp_parameters()
        process(our_qubo, q_par)

        q_par.ppair = 250.0
        q_par.psum = 500.0
        process(our_qubo, q_par)

        q_par.ppair = 2.0
        q_par.psum = 4.0
        q_par.method = "real"
        process(our_qubo, q_par)
        q_par.annealing_time = 5
        process(our_qubo, q_par)

        our_qubo.qubo2()
        q_par.method = "sim"
        process(our_qubo, q_par)

        our_qubo.qubo2()
        q_par.method = "real"
        q_par.annealing_time = 1000
        process(our_qubo, q_par)
        q_par.annealing_time = 50
        process(our_qubo, q_par)
        q_par.annealing_time = 2
        process(our_qubo, q_par)
