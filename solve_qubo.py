import pickle
import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import linprog
import neal
import dimod
from dwave.system import (
    EmbeddingComposite,
    DWaveSampler,
    LeapHybridSampler,
    LeapHybridCQMSampler,
)

from QTrains import QuboVars, Parameters, Railway_input, Analyze_qubo, Variables, LinearPrograming
from QTrains import add_update, find_ones, diff_passing_times, plot_train_diagrams




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

    file1 = file.replace("qubo", "LP")
    file1 = f"{file1}_{dmax}.json"

    with open(file1, 'wb') as fp:
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

    file1 = f"{file}_{dmax}_{ppair}_{psum}.json"
    with open(file1, 'wb') as fp:
        pickle.dump(dict, fp)



def solve_qubo(q_input, q_pars):

    loops = 10
    file = q_input.file

    ppair = q_pars.ppair
    psum = q_pars.psum
    dmax = q_pars.dmax

    file = f"{file}_{dmax}_{ppair}_{psum}.json"

    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_read)
    Q = qubo_to_analyze.qubo

    file = file.replace("QUBOs", "solutions")
    file = file.replace(".json", f"_{q_pars.method}.json")


    sampleset = {}

    if q_pars.method == "sim":
        for k in range(loops):
            s = neal.SimulatedAnnealingSampler()
            sampleset[k] = s.sample_qubo(
                Q, beta_range = (0.001, 50), num_sweeps = 500, num_reads = q_pars.num_reads, beta_schedule_type="geometric"
            )

    elif q_pars.method == "real":
        sampler = EmbeddingComposite(DWaveSampler())

        for k in range(loops):

            num_reads = q_pars.num_reads
            annealing_time = 2
            chain_strength = 1

            sampleset[k] = sampler.sample_qubo(
                Q,
                num_reads=num_reads,
                auto_scale="true",
                annealing_time=annealing_time,
                chain_strength=chain_strength,
        )

    with open(file, 'wb') as fp:
        pickle.dump(sampleset, fp)



def analyze_qubo(q_input, q_pars):

    file = q_input.file

    ppair = q_pars.ppair
    psum = q_pars.psum
    dmax = q_pars.dmax

    file1 = f"{file}_{dmax}.json"
    file1 = file1.replace("qubo", "LP")
    file1 = file1.replace("QUBOs", "solutions")
    file = f"{file}_{dmax}_{ppair}_{psum}.json"

    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    with open(file1, 'rb') as fp:
        lp_sol = pickle.load(fp)
        
    qubo_to_analyze = Analyze_qubo(dict_read)

    file = file.replace("QUBOs", "solutions")

    file = file.replace(".json", f"_{q_pars.method}.json")

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
                        print("selected objective", qubo_to_analyze.objective_val(sol) )
                    k = k + 1
                    vq = qubo_to_analyze.qubo2int_vars(sol)
                    h = diff_passing_times(lp_sol["variables"], vq, ["MR", "CS"], qubo_to_analyze.trains_paths) 
                    hist.extend( h )


    file = file.replace("solutions", "histograms")

    with open(file, 'wb') as fp:
        pickle.dump(hist, fp)


def plot_hist(q_input, q_pars):

    ppair = q_pars.ppair
    psum = q_pars.psum
    dmax = q_pars.dmax

    file = q_input.file

    file = file.replace("QUBOs", "histograms")
    file = f"{file}_{dmax}_{ppair}_{psum}.json"

    file = file.replace(".json", f"_{q_pars.method}.json")

    with open(file, 'rb') as fp:
        hist = pickle.load(fp)

        plt.bar(*np.unique(hist, return_counts=True))
        file = file.replace(".json", ".pdf")
        plt.title(f"sim, dmax={dmax}, ppair={ppair}, psum={psum}")
        plt.savefig(file)
        plt.clf()



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


class qubo_parameters():
    def __init__(self):
        self.num_reads = 500
        self.ppair = 2.0
        self.psum = 2.0
        self.dmax = 10
        self.method = "sim"


if __name__ == "__main__":


    q_input = input_qubo()
    q_input.qubo1()
    q_pars = qubo_parameters()


    solve_on_LP(q_input, q_pars)

    prepare_qubo(q_input, q_pars)


    solve_qubo(q_input, q_pars)

    analyze_qubo(q_input, q_pars)

    plot_hist(q_input, q_pars)