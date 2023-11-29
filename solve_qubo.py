import pickle
import matplotlib.pyplot as plt
import numpy as np
import os.path

from scipy.optimize import linprog
import neal
import dimod
from dwave.system import (
    EmbeddingComposite,
    DWaveSampler
)

from QTrains import QuboVars, Parameters, Railway_input, Analyze_qubo, Variables, LinearPrograming
from QTrains import diff_passing_times



def file_LP_output(q_input, q_pars):
    file = q_input.file
    file = file.replace("qubo", "LP")
    file = f"{file}_{q_pars.dmax}.json"
    file = file.replace("QUBOs", "solutions")
    return file


def file_QUBO(q_input, q_pars):
    file = f"{q_input.file}_{q_pars.dmax}_{q_pars.ppair}_{q_pars.psum}.json"
    return file

def file_QUBO_output(file, q_pars):
    file = file.replace("QUBOs", "solutions")
    if q_pars.method == "sim":
        file = file.replace(".json", f"_{q_pars.method}_{q_pars.num_all_runs}_{q_pars.beta_range}_{q_pars.num_sweeps}.json")
    elif q_pars.method == "real":
        file = file.replace(".json", f"_{q_pars.method}_{q_pars.num_all_runs}_{q_pars.annealing_time}.json")
    return file


def solve_on_LP(q_input, q_pars):
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
    problem = LinearPrograming(v, rail_input, M = 10)
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
    dict = q.store_in_dict(rail_input)

    file = file_QUBO(q_input, q_pars)
    with open(file, 'wb') as fp:
        pickle.dump(dict, fp)



def solve_qubo(q_input, q_pars):

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

    file = file_QUBO_output(file, q_pars)
    with open(file, 'wb') as fp:
        pickle.dump(sampleset, fp)


def analyze_qubo(q_input, q_pars):

    file = file_QUBO(q_input, q_pars)
    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    file1 = file_LP_output(q_input, q_pars)
    with open(file1, 'rb') as fp:
        lp_sol = pickle.load(fp)
        
    qubo_to_analyze = Analyze_qubo(dict_read)
    print(" ......  problem size ......")
    print("no qubits", qubo_to_analyze.noqubits)
    print("no qubo terms", len(qubo_to_analyze.qubo) )
    print(".............................")

    file = file_QUBO_output(file, q_pars)
    with open(file, 'rb') as fp:
        samplesets = pickle.load(fp)

    print("..... LP objective", lp_sol["objective"])
    hist = list([])
    for sampleset in samplesets.values():
        k = 0
        for sample in sampleset.samples():
            sol = [ i for i in sample.values()]
            if qubo_to_analyze.count_broken_constrains(sol) == (0,0,0,0):
                if qubo_to_analyze.broken_MO_conditions(sol) == 0:
                    if k == 0:
                        print("selected objective / energy + ofset",
                            qubo_to_analyze.objective_val(sol),
                            qubo_to_analyze.energy(sol) + qubo_to_analyze.sum_ofset)
                    k = k + 1
                    vq = qubo_to_analyze.qubo2int_vars(sol)
                    h = diff_passing_times(lp_sol["variables"], vq, ["MR", "CS"], qubo_to_analyze.trains_paths) 
                    hist.extend( h )

    file = file.replace("solutions", "histograms")
    with open(file, 'wb') as fp:
        pickle.dump(hist, fp)


def plot_hist(q_input, q_pars):

    file = file_QUBO(q_input, q_pars)
    file = file_QUBO_output(file, q_pars)
    file = file.replace("solutions", "histograms")

    with open(file, 'rb') as fp:
        hist = pickle.load(fp)

        plt.bar(*np.unique(hist, return_counts=True))
        file = file.replace(".json", ".pdf")
        if q_pars.method == "sim":
            plt.title(f"{q_input.file}, {q_pars.method}, dmax={q_pars.dmax}, ppair={q_pars.ppair}, psum={q_pars.psum}")
        else:
            plt.title(f"{q_input.file}, ammeal_time={q_pars.annealing_time}, dmax={q_pars.dmax}, ppair={q_pars.ppair}, psum={q_pars.psum}")
        plt.savefig(file)
        plt.clf()


def process(q_input, q_pars):


    file = file_LP_output(q_input, q_pars)
    if not os.path.isfile(file):
        solve_on_LP(q_input, q_pars)

    file = file_QUBO(q_input, q_pars)
    if not os.path.isfile(file):
        prepare_qubo(q_input, q_pars)
    
    file = file_QUBO_output(file, q_pars)
    if not os.path.isfile(file):
        solve_qubo(q_input, q_pars)

    analyze_qubo(q_input, q_pars)
    plot_hist(q_input, q_pars)



class input_qubo():
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
        self.circ = {}
        self.timetable = {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
        self.objective_stations = ["MR", "CS"]
        self.delays = {3:2}
        self.file = "QUBOs/qubo_1"

    def qubo2(self):
        self.circ = {(3,4): "CS"}
        self.timetable = {"PS": {1: 0, 4:33}, "MR" :{1: 3, 3: 0, 5:5, 4:30}, "CS" : {1: 16 , 3: 13, 4:17, 5:18}}
        self.objective_stations = ["MR", "CS"]
        self.delays = {3:2}
        self.file = "QUBOs/qubo_2"
        


class qubo_parameters():
    def __init__(self):
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


    q_input = input_qubo()
    q_input.qubo1()
    q_pars = qubo_parameters()
    process(q_input, q_pars)

    q_pars.ppair = 250.0
    q_pars.psum = 500.0
    process(q_input, q_pars)

    q_input.qubo2()
    q_pars = qubo_parameters()
    process(q_input, q_pars)

    q_input.qubo1()
    q_pars = qubo_parameters()
    q_pars.method = "real"
    process(q_input, q_pars)
    q_pars.annealing_time = 5
    process(q_input, q_pars)

    q_input.qubo2()
    q_pars = qubo_parameters()
    q_pars.method = "real"
    process(q_input, q_pars)
    q_pars.annealing_time = 50
    process(q_input, q_pars)
    q_pars.annealing_time = 2
    process(q_input, q_pars)

    