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
from QTrains import add_update, find_ones, compare_qubo_and_lp, plot_train_diagrams




def solve_on_LP(timetable, objective_stations, circulation, delays, dmax, file):
    stay = 1
    headways = 2
    preparation_t = 3

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


    

def prepare_qubo(timetable, objective_stations, circulation, delays, dmax, ppair, psum, file):
    stay = 1
    headways = 2
    preparation_t = 3
    p = Parameters(timetable, stay=stay, headways=headways,
                   preparation_t=preparation_t, dmax=dmax, circulation=circulation)
    rail_input = Railway_input(p, objective_stations, delays = delays)
    q = QuboVars(rail_input, ppair=ppair, psum=psum)
    q.make_qubo(rail_input)
    dict = q.store_in_dict(rail_input)

    print(rail_input.tvar_range)

    print( rail_input.pass_time )

    file1 = f"{file}_{dmax}_{ppair}_{psum}.json"
    with open(file1, 'wb') as fp:
        pickle.dump(dict, fp)



def solve_qubo(dmax, ppair, psum, file):
    file = f"{file}_{dmax}_{ppair}_{psum}.json"

    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)
    
    qubo_to_analyze = Analyze_qubo(dict_read)
    Q = qubo_to_analyze.qubo

    file = file.replace("QUBOs", "solutions")

    file = file.replace(".json", "_sim.json")
    s = neal.SimulatedAnnealingSampler()
    sampleset = s.sample_qubo(
        Q, beta_range = (0.001, 50), num_sweeps = 500, num_reads = 10, beta_schedule_type="geometric"
    )

    if False: # real annelaing
        sampler = EmbeddingComposite(DWaveSampler())

        sampleset = sampler.sample(
            bqm,
            num_reads=num_reads,
            auto_scale="true",
            annealing_time=annealing_time,
            chain_strength=chain_strength,
        )

    with open(file, 'wb') as fp:
        pickle.dump(sampleset, fp)



def analyze_qubo(dmax, ppair, psum, file):
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

    file = file.replace(".json", "_sim.json")

    with open(file, 'rb') as fp:
        sampleset = pickle.load(fp)


    print("..... LP objective", lp_sol["objective"])

    hist = {s:list([]) for s in qubo_to_analyze.timetable}

    for sample in sampleset.samples():
        sol = [ i for i in sample.values()]
        if qubo_to_analyze.count_broken_constrains(sol) == (0,0,0,0):
            if qubo_to_analyze.broken_MO_conditions(sol) == 0:
                print("objective", qubo_to_analyze.objective_val(sol) )
                vq = qubo_to_analyze.qubo2int_vars(sol)
                _, over_station = compare_qubo_and_lp(lp_sol["variables"], vq, qubo_to_analyze.trains_paths)
                
                for j in qubo_to_analyze.trains_paths:
                    for s in qubo_to_analyze.trains_paths[j]:
                        v = f"t_{s}_{j}"
                        print("s", s, "j", j)
                        print("qubo", vq[v].value)

                        print("lp", lp_sol["variables"][v].value)

                #print( sol )
                print(over_station)
                #print(qubo_to_analyze.passing_time_constrain)

                for s in over_station:
                    hist[s] = hist[s] + list(over_station[s])

    file = file.replace("solutions", "histograms")

    with open(file, 'wb') as fp:
        pickle.dump(hist, fp)


def plot_hist(dmax, ppair, psum, file):
    file = file.replace("QUBOs", "histograms")
    file = f"{file}_{dmax}_{ppair}_{psum}.json"

    file = file.replace(".json", "_sim.json")

    with open(file, 'rb') as fp:
        histogram = pickle.load(fp)

        k = "CS" 
        hist = histogram[k]
        print(set(hist))   
        plt.bar(*np.unique(hist, return_counts=True))
        file = file.replace(".json", ".pdf")
        plt.savefig(file)
        plt.clf()


if __name__ == "__main__":
    #circulation = {(1,2): "B"}
    circulation = {}
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}}
    objective_stations = ["MR", "CS"]
    delays = {3:2}

    dmax = 5
    ppair = 2.
    psum = 2.

    file = "QUBOs/qubo_1"

    solve_on_LP(timetable, objective_stations, circulation, delays, dmax, file)

    prepare_qubo(timetable, objective_stations, circulation, delays, dmax, ppair, psum, file)

    solve_qubo(dmax, ppair, psum, file)

    analyze_qubo(dmax, ppair, psum, file)

    plot_hist(dmax, ppair, psum, file)