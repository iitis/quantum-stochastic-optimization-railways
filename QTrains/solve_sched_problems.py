""" execution module for solving trains scheduling problem  """
import pickle
import itertools
import time
import pytest
import numpy as np
try:
    import cplex
except:
    print("no CPLEX")

from scipy.optimize import linprog
import neal
from dwave.system import (
    EmbeddingComposite,
    DWaveSampler
)
from dwave.system.composites import FixedEmbeddingComposite
from minorminer import find_embedding


from .parameters import (Parameters, Railway_input)
from .LP_problem import (Variables, LinearPrograming, make_ilp_docplex)
from .make_qubo import (QuboVars, Analyze_qubo, update_hist, is_feasible)


####### make files names and directories, where each step of the solving scheme is saved
def file_LP_output(trains_input, q_pars):
    """ returns string, the file name and dir to store LP results """
    file = trains_input.file
    file = file.replace("qubo", "LP")
    file = f"{file}_{q_pars.dmax}.json"

    file = file.replace("QUBOs", "solutions")
    return file

def file_QUBO(trains_input, q_pars):
    """ returns string, the file name and dir to store QUBO and its features """
    return f"{trains_input.file}_{q_pars.dmax}_{q_pars.ppair}_{q_pars.psum}.json"


def file_QUBO_comp(trains_input, q_pars):
    """ returns string, the file name and dir to store results of computaiton on QUBO """
    file = file_QUBO(trains_input, q_pars)
    file = file.replace("QUBOs", "solutions")
    if q_pars.method == "sim":
        file = file.replace(".json", f"_{q_pars.method}_{q_pars.num_all_runs}_{q_pars.beta_range[0]}_{q_pars.num_sweeps}.json")
    elif q_pars.method == "real":
        file = file.replace(".json", f"_{q_pars.solver}_{q_pars.num_all_runs}_{q_pars.annealing_time}.json")

    return file


def file_hist(trains_input, q_pars):
    """ file for histogram """
    file = file_QUBO_comp(trains_input, q_pars)
    if not q_pars.softern_pass:
        file = file.replace("solutions", "histograms")
    else:
        file = file.replace("solutions", "histograms_soft")
        file = file.replace("qubo", "qubo_softern")
    return file

#### ILP solver
def solve_on_LP(trains_input, q_pars, output_file):
    """ solve the problem using LP, and save results """
    stay = trains_input.stay
    headways = trains_input.headways
    preparation_t = trains_input.preparation_t

    timetable = trains_input.timetable
    objective_stations = trains_input.objective_stations
    dmax = q_pars.dmax

    pars = Parameters(timetable, stay=stay, headways=headways,
                   preparation_t=preparation_t, dmax=dmax, circulation=trains_input.circ)
    rail_input = Railway_input(pars, objective_stations, delays = trains_input.delays)
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

    with open(output_file, 'wb') as fp:
        pickle.dump(d, fp)


def classical_benchmark(trains_input, q_pars, results:dict):

    """ solve the problem using LP, and save results """
    stay = trains_input.stay
    headways = trains_input.headways
    preparation_t = trains_input.preparation_t

    timetable = trains_input.timetable
    objective_stations = trains_input.objective_stations
    dmax = q_pars.dmax

    pars = Parameters(timetable, stay=stay, headways=headways,
                   preparation_t=preparation_t, dmax=dmax, circulation=trains_input.circ)
    rail_input = Railway_input(pars, objective_stations, delays = trains_input.delays)
    v = Variables(rail_input)
    bounds, integrality = v.bonds_and_integrality()
    problem = LinearPrograming(v, rail_input, M = q_pars.M)
    model = make_ilp_docplex(problem, v)

    start = time.time()
    solution = model.solve()
    end = time.time()


    v.docplex2vars(model, solution)
    v.check_clusters()

    cplex_obj = problem.compute_objective(v, rail_input)


    assert pytest.approx( solution.objective_value - problem.obj_ofset) == cplex_obj

    results[trains_input.notrains] = {"model engine": model.get_engine().name, 
                                      "CPLEX Python API version": cplex.__version__,
                                      "Comp time [seconds]": end - start,
                                      "Objective value":  cplex_obj
                                      }

    check = True

    if check:

        v = Variables(rail_input)
        bounds, integrality = v.bonds_and_integrality()
        problem = LinearPrograming(v, rail_input, M = q_pars.M)

        opt = linprog(c=problem.obj, A_ub=problem.lhs_ineq,
                    b_ub=problem.rhs_ineq, bounds=bounds, method='highs',
                    integrality = integrality)
        v.linprog2vars(opt)
        v.check_clusters()

        assert  cplex_obj == problem.compute_objective(v, rail_input) 


#####  QUBO handling ######
def prepare_qubo(trains_input, q_pars, output_file):
    """ create and save QUBO given railway input and parameters 
    
    """
    stay = trains_input.stay
    headways = trains_input.headways
    preparation_t = trains_input.preparation_t

    timetable = trains_input.timetable
    objective_stations = trains_input.objective_stations

    ppair = q_pars.ppair
    psum = q_pars.psum
    dmax = q_pars.dmax

    par = Parameters(timetable, stay=stay, headways=headways,
                   preparation_t=preparation_t, dmax=dmax, circulation=trains_input.circ)

    rail_input = Railway_input(par, objective_stations, delays = trains_input.delays)
    q = QuboVars(rail_input, ppair=ppair, psum=psum)
    q.make_qubo(rail_input)
    qubo_dict = q.store_in_dict(rail_input)

    with open(output_file, 'wb') as fp:
        pickle.dump(qubo_dict, fp)


def approx_no_physical_qbits(trains_input, q_pars):
    """ returns number of logical qbits and approximates number of physical qubits using embeder """
    file = file_QUBO(trains_input, q_pars)
    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_read)
    Q = qubo_to_analyze.qubo

    solver = DWaveSampler(solver=q_pars.solver)

    __, target_edgelist, _ = solver.structure

    emb = find_embedding(Q, target_edgelist, verbose=1)

    no_logical = len(emb.keys())
    physical_qbits_lists = list(emb.values())
    physical_qbits_list = list(itertools.chain(*physical_qbits_lists))
    no_physical =  len( set(physical_qbits_list) )

    return no_logical, no_physical



def solve_qubo(q_pars, input_file, output_file):
    """ solve the problem given by QUBO and store results """

    with open(input_file, 'rb') as fp:
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
        sampler = EmbeddingComposite(DWaveSampler(solver=q_pars.solver, token=q_pars.token))

        for k in range(loops):

            sampleset[k] = sampler.sample_qubo(
                Q,
                num_reads=q_pars.num_reads,
                annealing_time=q_pars.annealing_time
        )

    with open(output_file, 'wb') as fp:
        pickle.dump(sampleset, fp)

    print(f"solved qubo method {q_pars.method}")



def get_solutions_from_dmode(samplesets, q_pars):
    """ from dmode imput return a series of QUBO solutions as [sol1, sol2, ...] """
    solutions = []
    broken_chains = []
    for sampleset in samplesets.values():
        if q_pars.method == "sim":
            for (sol, _, occ) in sampleset.record:  # not used energy in the middle
                for _ in range(occ):
                    solutions.append(sol)
        elif q_pars.method == "real":
            for (sol, _, occ, _) in sampleset.record:
                for _ in range(occ):
                    solutions.append(sol)
    assert len(solutions) == q_pars.num_all_runs

    return solutions




def analyze_qubo_Dwave(trains_input, q_pars, qubo_file, lp_file, qubo_output_file, hist_file):
    """ analyze results of computation on QUBO and comparison with LP """

    with open(qubo_file, 'rb') as fp:
        dict_qubo = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_qubo)

    with open(lp_file, 'rb') as fp:
        lp_sol = pickle.load(fp)

    with open(qubo_output_file, 'rb') as fp:
        samplesets = pickle.load(fp)

    stations = trains_input.objective_stations

    our_solutions = get_solutions_from_dmode(samplesets, q_pars)

    results = analyze_QUBO_outputs(qubo_to_analyze, stations, our_solutions, lp_sol, softernpass = q_pars.softern_pass)

    with open(hist_file, 'wb') as fp:
        pickle.dump(results, fp)



def analyze_QUBO_outputs(qubo, stations, our_solutions, lp_solution, softernpass = False):
    """  returns histogram of passing times between selected stations and objective 
         outputs of gate computer
    """
    hist = list([])
    qubo_objectives = list([])

    energy_feasible = list([])
    energy_notfeasible = list([])

    count = 0
    no_feasible = 0

    display = len(our_solutions) < 100

    for solution in our_solutions:
        if display:
            dsiplay_solution_analysis(qubo, solution, lp_solution)

        count += 1

        if is_feasible(solution, qubo, softernpass):
            no_feasible += 1
            qubo_objectives.append(qubo.objective_val(solution))
            energy_feasible.append(qubo.energy(solution))

            update_hist(qubo, solution, stations, hist, softernpass)
        else:
            energy_notfeasible.append(qubo.energy(solution))

    perc_feasible = no_feasible/count

    results = {"perc feasible": perc_feasible, f"{stations[0]}_{stations[1]}": hist}
    results["no qubits"] = qubo.noqubits
    results["no qubo terms"] = len(qubo.qubo)
    results["lp objective"] = lp_solution["objective"]
    results["q ofset"] = qubo.sum_ofset
    results["qubo objectives"] = qubo_objectives
    results["energies feasible"] = energy_feasible
    results["energies notfeasible"] = energy_notfeasible
    return results



def analyze_chain_strength(qubo_output_file):
    """ analyze results of computation on QUBO and comparison with LP """


    with open(qubo_output_file, 'rb') as fp:
        samplesets = pickle.load(fp)


    solutions = []
    broken_fraction = []
    for sampleset in samplesets.values():
        for (sol,energy, occ, chain_break_fraction) in sampleset.record:
            for _ in range(occ):
                solutions.append(sol)
                broken_fraction.append(chain_break_fraction)

    return broken_fraction




######## gates  #######


def save_qubo_4gates_comp(dict_qubo, ground_sols, output_file):
    "creates and seves file with ground oslution and small qubo for gate computing"
    our_qubo = Analyze_qubo(dict_qubo)
    qubo4gates = {}
    qubo4gates["qubo"] = dict_qubo["qubo"]
    qubo4gates["ground_solutions"] = ground_sols
    E = our_qubo.energy(ground_sols[0])
    for ground_sol in ground_sols:
        assert E == our_qubo.energy(ground_sol)
    qubo4gates["ground_energy"] = E

    with open(output_file, 'wb') as fp_w:
        pickle.dump(qubo4gates, fp_w)


##### results presentation


def dsiplay_solution_analysis(trains_input, our_solution, lp_solution, timetable = False):
    "prints features of the solution fram gate computer"
    print( "..........  QUBO ........   " )
    print("qubo size=", len( trains_input.qubo ), " number of Q-bits=", len( our_solution ))
    print("energy=", trains_input.energy( our_solution ))
    print("energy + ofset=", trains_input.energy( our_solution ) + trains_input.sum_ofset)
    print("QUBO objective=", trains_input.objective_val( our_solution ), "  ILP objective=", lp_solution["objective"] )

    print("broken (sum, headway, pass, circ)", trains_input.count_broken_constrains( our_solution ))
    print("broken MO", trains_input.broken_MO_conditions( our_solution ))

    if timetable:
        print(" ........ vars values  ........ ")
        print(" key, qubo, LP ")

        vq = trains_input.qubo2int_vars( our_solution )
        for k, v in vq.items():
            print(k, v.value, lp_solution["variables"][k].value)
        print("  ..............................  ")


def display_prec_feasibility(trains_input, q_pars, file_h):
    """ print results of computation """

    with open(file_h, 'rb') as fp:
        res_dict = pickle.load(fp)


    print("xxxxxxxxx    RESULTS     xxxxxx ", trains_input.file,  "xxxxx")
    print("delays", trains_input.delays )
    print("method", q_pars.method)
    print("psum", q_pars.psum)
    print("ppair", q_pars.ppair)
    print("dmax", q_pars.dmax)
    print("LP objective", res_dict["lp objective"])
    print("qubo ofset", res_dict["q ofset"])

    if q_pars.method == "real":
        print("annealing time", q_pars.annealing_time)
    print("no qubits", res_dict["no qubits"])
    print("no qubo terms", res_dict["no qubo terms"])
    print("percentage of feasible", res_dict["perc feasible"])
