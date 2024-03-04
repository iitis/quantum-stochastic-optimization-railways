import pickle
import itertools
from scipy.optimize import linprog
import neal
from dwave.system import (
    EmbeddingComposite,
    DWaveSampler
)
from dwave.system.composites import FixedEmbeddingComposite
from minorminer import find_embedding


from .parameters import (Parameters, Railway_input)
from .LP_problem import (Variables, LinearPrograming)
from .make_qubo import (QuboVars, Analyze_qubo, update_hist)


####### make files names and directories, where each step of the solving scheme is saved
def file_LP_output(q_input, q_pars, p):
    """ returns string, the file name and dir to store LP results """
    file = q_input.file
    file = file.replace("qubo", "LP")
    if p.delta == 0:
        file = f"{file}_{q_pars.dmax}.json"
    else:
        file = f"{file}_{q_pars.dmax}_stochastic{p.delta}.json"
    file = file.replace("QUBOs", "solutions")
    return file

def file_QUBO(q_input, q_pars, p):
    """ returns string, the file name and dir to store QUBO and its features """
    if p.delta == 0:
        file = f"{q_input.file}_{q_pars.dmax}_{q_pars.ppair}_{q_pars.psum}.json"
    else:
        file = f"{q_input.file}_{q_pars.dmax}_{q_pars.ppair}_{q_pars.psum}_stochastic{p.delta}.json"
    return file

def file_QUBO_comp(q_input, q_pars, p, replace_pair = ("", "")):
    """ returns string, the file name and dir to store results of computaiton on QUBO """
    file = file_QUBO(q_input, q_pars, p)
    file = file.replace("QUBOs", "solutions")
    if q_pars.method == "sim":
        file = file.replace(".json", f"_{q_pars.method}_{q_pars.num_all_runs}_{q_pars.beta_range[0]}_{q_pars.num_sweeps}.json")
    elif q_pars.method == "real":
        file = file.replace(".json", f"_{q_pars.solver}_{q_pars.num_all_runs}_{q_pars.annealing_time}.json")
    file = file.replace(replace_pair[0], replace_pair[1])
    return file


def file_hist(q_input, q_pars, p, replace_pair = ("", "")):
    """ file for histogram """
    file = file_QUBO_comp(q_input, q_pars, p, replace_pair = replace_pair)
    if not p.softern_pass:
        file = file.replace("solutions", "histograms")
    else:
        file = file.replace("solutions", "histograms_soft")
        file = file.replace("qubo", "qubo_softern")
    return file

#### ILP solver
def solve_on_LP(q_input, q_pars, p):
    """ solve the problem using LP, and save results """
    stay = q_input.stay
    headways = q_input.headways
    preparation_t = q_input.preparation_t

    timetable = q_input.timetable
    objective_stations = q_input.objective_stations
    dmax = q_pars.dmax

    pars = Parameters(timetable, stay=stay, headways=headways,
                   preparation_t=preparation_t, dmax=dmax, circulation=q_input.circ)
    rail_input = Railway_input(pars, objective_stations, delays = q_input.delays)
    v = Variables(rail_input)
    bounds, integrality = v.bonds_and_integrality()
    problem = LinearPrograming(v, rail_input, M = q_pars.M, delta=p.delta)
    opt = linprog(c=problem.obj, A_ub=problem.lhs_ineq,
                  b_ub=problem.rhs_ineq, bounds=bounds, method='highs',
                  integrality = integrality)
    v.linprog2vars(opt)

    v.check_clusters()

    d = {}
    d["variables"] = v.variables
    d["objective"] = problem.compute_objective(v, rail_input)

    file = file_LP_output(q_input, q_pars, p)
    with open(file, 'wb') as fp:
        pickle.dump(d, fp)


#####  QUBO handling ######
def prepare_qubo(q_input, q_pars, p):
    """ create and save QUBO given railway input and parameters 
    
    delta is the parameter that increases passing time, for stochastic purpose
    """
    stay = q_input.stay
    headways = q_input.headways
    preparation_t = q_input.preparation_t

    timetable = q_input.timetable
    objective_stations = q_input.objective_stations

    ppair = q_pars.ppair
    psum = q_pars.psum
    dmax = q_pars.dmax

    par = Parameters(timetable, stay=stay, headways=headways,
                   preparation_t=preparation_t, dmax=dmax, circulation=q_input.circ)
    rail_input = Railway_input(par, objective_stations, delays = q_input.delays)
    q = QuboVars(rail_input, ppair=ppair, psum=psum)
    q.make_qubo(rail_input, p.delta)
    qubo_dict = q.store_in_dict(rail_input)

    file = file_QUBO(q_input, q_pars, p)
    with open(file, 'wb') as fp:
        pickle.dump(qubo_dict, fp)


def approx_no_physical_qbits(q_input, q_pars, p):
    file = file_QUBO(q_input, q_pars, p)
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






def solve_qubo(q_input, q_pars, p):
    """ solve the problem given by QUBO and store results """
    file = file_QUBO(q_input, q_pars, p)
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
        sampler = EmbeddingComposite(DWaveSampler(solver=q_pars.solver, token=q_pars.token))

        for k in range(loops):

            sampleset[k] = sampler.sample_qubo(
                Q,
                num_reads=q_pars.num_reads,
                annealing_time=q_pars.annealing_time
        )

    file = file_QUBO_comp(q_input, q_pars, p)
    with open(file, 'wb') as fp:
        pickle.dump(sampleset, fp)

    print(f"solved qubo method {q_pars.method}")



def get_solutions_from_dmode(samplesets, q_pars):
    """ from dmode imput return a series of QUBO solutions as [sol1, sol2, ...] """
    solutions = []
    for sampleset in samplesets.values():
        if q_pars.method == "sim":
            for (sol, energy, occ) in sampleset.record:
                for _ in range(occ):
                    solutions.append(sol)
        elif q_pars.method == "real":
            for (sol, energy, occ, other) in sampleset.record:
                for _ in range(occ):
                    solutions.append(sol)
    assert len(solutions) == q_pars.num_all_runs
    return solutions

                    


def analyze_qubo_Dwave(q_input, q_pars, p):
    """ analyze results of computation on QUBO and comparison with LP """
    show_var_vals = False

    file = file_QUBO(q_input, q_pars, p)
    with open(file, 'rb') as fp:
        dict_read = pickle.load(fp)

    file = file_LP_output(q_input, q_pars, p)
    with open(file, 'rb') as fp:
        lp_sol = pickle.load(fp)

    qubo_to_analyze = Analyze_qubo(dict_read)
    file = file_QUBO_comp(q_input, q_pars, p)
    print( file )
    with open(file, 'rb') as fp:
        samplesets = pickle.load(fp)

    stations = q_input.objective_stations

    our_solutions = get_solutions_from_dmode(samplesets, q_pars)

    results = analyze_QUBO_outputs(qubo_to_analyze, stations, our_solutions, lp_sol, softernpass = False)


    file =  file_hist(q_input, q_pars, p)
    with open(file, 'wb') as fp:
        pickle.dump(results, fp)



def analyze_QUBO_outputs(qubo, stations, our_solutions, lp_solution, softernpass = False):
    """  returns histogram of passing times between selected stations and objective 
         outputs of gate computer
    """
    hist = list([])
    qubo_objectives = list([])

    count = 0
    no_feasible = 0

    display = len(our_solutions) < 100

    for solution in our_solutions:
        if display:
            dsiplay_solution_analysis(qubo, solution, lp_solution)

        count += 1
        no_feasible += update_hist(qubo, solution, stations, hist, qubo_objectives, softernpass)

    
    perc_feasible = no_feasible/count

    results = {"perc feasible": perc_feasible, f"{stations[0]}_{stations[1]}": hist}
    results["no qubits"] = qubo.noqubits
    results["no qubo terms"] = len(qubo.qubo)
    results["lp objective"] = lp_solution["objective"]
    results["q ofset"] = qubo.sum_ofset
    results["qubo objectives"] = qubo_objectives
    return results

######## gates  #######
        

def save_qubo_4gates_comp(dict_qubo, ground_sols, input_file):
    "creates and seves file with ground oslution and small qubo for gate computing"
    our_qubo = Analyze_qubo(dict_qubo)
    qubo4gates = {}
    qubo4gates["qubo"] = dict_qubo["qubo"]
    qubo4gates["ground_solutions"] = ground_sols
    E = our_qubo.energy(ground_sols[0])
    for ground_sol in ground_sols:
        assert E == our_qubo.energy(ground_sol)
    qubo4gates["ground_energy"] = E

    new_file = input_file.replace("LR_timetable/", "gates/")
    with open(new_file, 'wb') as fp_w:
        pickle.dump(qubo4gates, fp_w)


##### results presentation

        
def dsiplay_solution_analysis(q_input, our_solution, lp_solution, timetable = False):
    "prints features of the solution fram gate computer"
    print( "..........  QUBO ........   " )
    print("qubo size=", len( q_input.qubo ), " number of Q-bits=", len( our_solution ))
    print("energy=", q_input.energy( our_solution ))
    print("energy + ofset=", q_input.energy( our_solution ) + q_input.sum_ofset)
    print("QUBO objective=", q_input.objective_val( our_solution ), "  ILP objective=", lp_solution["objective"] )

    print("broken (sum, headway, pass, circ)", q_input.count_broken_constrains( our_solution ))
    print("broken MO", q_input.broken_MO_conditions( our_solution ))

    if timetable:
        print(" ........ vars values  ........ ")
        print(" key, qubo, LP ")

        vq = q_input.qubo2int_vars( our_solution )
        for k, v in vq.items():
            print(k, v.value, lp_solution["variables"][k].value)
        print("  ..............................  ")


def display_prec_feasibility(q_input, q_pars, p):
    """ print results of computation """

    file = file_hist(q_input, q_pars, p)
    with open(file, 'rb') as fp:
        res_dict = pickle.load(fp)

    
    print("xxxxxxxxx    RESULTS     xxxxxx ", q_input.file,  "xxxxx")
    print("delays", q_input.delays )
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