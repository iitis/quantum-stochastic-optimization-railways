import numpy as np
import matplotlib.pyplot as plt
import pickle
from scipy.optimize import linprog
import neal
from dwave.system import (
    EmbeddingComposite,
    DWaveSampler
)


from .parameters import (Parameters, Railway_input)
from .LP_problem import (Variables, LinearPrograming)
from .make_qubo import (QuboVars, Analyze_qubo, update_hist)



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

# make files names and directories, where each step of the solving scheme is saved
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

#### solvers and data analysis
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




def analyze_qubo(q_input, q_pars, p):
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

    hist = list([])
    qubo_objectives = list([])
    count = 0
    no_feasible = 0

    for sampleset in samplesets.values():
        if q_pars.method == "sim":
            for (sol, energy, occ) in sampleset.record:
                for _ in range(occ):

                    count += 1
                    no_feasible += update_hist(qubo_to_analyze, sol, stations, hist, qubo_objectives, softern_pass_t = p.softern_pass)
        elif q_pars.method == "real":
            for (sol, energy, occ, other) in sampleset.record:
                for _ in range(occ):

                    count += 1
                    no_feasible += update_hist(qubo_to_analyze, sol, stations, hist, qubo_objectives, softern_pass_t = p.softern_pass)

    assert count == q_pars.num_all_runs

    perc_feasible = no_feasible/count

    if show_var_vals:
        for v in lp_sol["variables"]:
            print(v, lp_sol["variables"][v].value, lp_sol["variables"][v].range )

    results = {"perc feasible": perc_feasible, f"{stations[0]}_{stations[1]}": hist}
    results["no qubits"] = qubo_to_analyze.noqubits
    results["no qubo terms"] = len(qubo_to_analyze.qubo)
    results["lp objective"] = lp_sol["objective"]
    results["q ofset"] = qubo_to_analyze.sum_ofset
    results["qubo objectives"] = qubo_objectives


    file =  file_hist(q_input, q_pars, p)
    with open(file, 'wb') as fp:
        pickle.dump(results, fp)


##### results presentation 
        
def display_results(q_input, q_pars, p):
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


##### plots

def plot_title(q_input, q_pars):
    if q_input.delays == {}:
        disturbed = "Not disturbed"
    else:
        disturbed = "Disturbed"
    if q_pars.method == "real":
        tit = f"{disturbed}, at={q_pars.annealing_time}$\mu$s, ppair={round(q_pars.ppair)}, psum={round(q_pars.psum)}"
    else:
        tit = f"{disturbed}, {q_pars.method}, ppair={round(q_pars.ppair)}, psum={round(q_pars.psum)}"
    return tit


def _ax_hist_passing_times(ax, q_input, q_pars, p, add_text = True, replace_string = ("", "")):
    """ axes for the passing time plots """
    file = file_hist(q_input, q_pars, p, replace_string)
    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    hist_pass = results[f"{q_input.objective_stations[0]}_{q_input.objective_stations[1]}"]

    xs = list( range(np.max(hist_pass) + 1) )
    ys = [hist_pass.count(x) for x in xs]
    ax.bar(xs,ys)

    ax.set_xlabel(f"Passing times between {q_input.objective_stations[0]} and {q_input.objective_stations[1]} - both ways")
    ax.set_ylabel("counts")
    if add_text:
        k = np.max(ys)/12
        ax.text(1,k, f"{q_input.notrains} trains, dmax={int(q_pars.dmax)}", fontsize=10)

    if "softern" in file:
        ax.set_xlim(left=0, right = 30)
        ax.set_xticks(range(0, 30, 2))
    else:
        ax.set_xlim(left=0)
        xx = [i for i in xs if i % 2 == 0]
        ax.set_xticks(xx)



def _ax_objective(ax, q_input, q_pars, p, replace_string = ("", "")):
    """ axes for the objective plot """
    file = file_hist(q_input, q_pars, p, replace_string)
    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    hist_obj = results["qubo objectives"]
    ground = results["lp objective"]

    xs = set(hist_obj)
    ys = [hist_obj.count(x) for x in set(hist_obj)]
    
    ax.bar(list(xs),ys, width = 0.3, color = "gray", label = "QUBO")
    ax.axvline(x = ground, lw = 2, color = 'red', linestyle = 'dashed', label = 'ground state')

    ax.legend()
    ax.set_xlabel("Objective")
    ax.set_ylabel("counts")

    

def make_plots(q_input, q_pars, p):
    """ ferform plotting on DWave results """

    fig, ax = plt.subplots(figsize=(4, 3))

    _ax_hist_passing_times(ax, q_input, q_pars, p)
    our_title = plot_title(q_input, q_pars)

    fig.subplots_adjust(bottom=0.2, left = 0.15)

    plt.title(our_title)

    file = file_hist(q_input, q_pars, p)
    file_pass = file.replace(".json", f"{q_input.objective_stations[0]}_{q_input.objective_stations[1]}.pdf")
    plt.savefig(file_pass)
    plt.clf()


    fig, ax = plt.subplots(figsize=(4, 3))

    _ax_objective(ax, q_input, q_pars, p)
    our_title= f"{plot_title(q_input, q_pars)}, dmax={int(q_pars.dmax)}"

    fig.subplots_adjust(bottom=0.2, left = 0.15)
    
    plt.title(our_title)

    file = file_hist(q_input, q_pars, p)
    file_obj = file.replace(".json", "obj.pdf")
    plt.savefig(file_obj)
    plt.clf()