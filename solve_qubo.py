import pickle
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

    file = f"{file}_{dmax}_{ppair}_{psum}.json"
    with open(file, 'wb') as fp:
        pickle.dump(dict, fp)



def solve_qubo(dmax, ppair, psum, file):
    file = f"{file}_{dmax}_{ppair}_{psum}.json"

    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)
    
    qubo_to_analyze = Analyze_qubo(dict_read)
    Q = qubo_to_analyze.qubo

    file = file.replace("QUBOs", "solutions")

    file = file.replace(".pickle", "_sim.pickle")
    s = neal.SimulatedAnnealingSampler()
    sampleset = s.sample_qubo(
        Q, beta_range = (0.1, 10), num_sweeps = 10, num_reads = 10, beta_schedule_type="geometric"
    )

    if False:
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
    file = f"{file}_{dmax}_{ppair}_{psum}.json"
    file = file.replace("QUBOs", "solutions")

    file = file.replace(".pickle", "_sim.pickle")

    with open(file, 'rb') as fp:
        sampleset = pickle.load(fp)


    print(sampleset.info)
    print(sampleset.variables)

    print(sampleset.samples)

    sols = []
    for sample in sampleset.samples():
        print([ i for i in sample.values()])

    if False:
        sampler = EmbeddingComposite(DWaveSampler())

        sampleset = sampler.sample(
            bqm,
            num_reads=num_reads,
            auto_scale="true",
            annealing_time=annealing_time,
            chain_strength=chain_strength,
        )



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

    prepare_qubo(timetable, objective_stations, circulation, delays, dmax, ppair, psum, file)

    solve_qubo(dmax, ppair, psum, file)

    analyze_qubo(dmax, ppair, psum, file)