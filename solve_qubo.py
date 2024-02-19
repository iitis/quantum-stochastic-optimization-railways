""" main computation script """
import pickle
import os.path
import matplotlib.pyplot as plt
import numpy as np


from scipy.optimize import linprog
import neal
from dwave.system import (
    EmbeddingComposite,
    DWaveSampler
)

from QTrains import QuboVars, Parameters, Railway_input, Analyze_qubo, Variables, LinearPrograming
from QTrains import update_hist

plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=10)

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

def file_QUBO_comp(q_input, q_pars, p):
    """ returns string, the file name and dir to store results of computaiton on QUBO """
    file = file_QUBO(q_input, q_pars, p)
    file = file.replace("QUBOs", "solutions")
    if q_pars.method == "sim":
        file = file.replace(".json", f"_{q_pars.method}_{q_pars.num_all_runs}_{q_pars.beta_range[0]}_{q_pars.num_sweeps}.json")
    elif q_pars.method == "real":
        file = file.replace(".json", f"_{q_pars.solver}_{q_pars.num_all_runs}_{q_pars.annealing_time}.json")
    return file


def file_hist(q_input, q_pars, p):
    """ file for histogram """
    file = file_QUBO_comp(q_input, q_pars, p)
    if not p.softern_pass:
        file = file.replace("solutions", "histograms")
    else:
        file = file.replace("solutions", "histograms_soft")
        file = file.replace("qubo", "qubo_softern")
    return file

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

    print(f"start {file}")

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
        for sample in sampleset.samples():
            sol = list(sample.values())
            count += 1
            no_feasible += update_hist(qubo_to_analyze, sol, stations, hist, qubo_objectives, softern_pass_t = p.softern_pass)

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


def _ax_hist_passing_times(ax, q_input, q_pars, p, add_text = True, dir=""):

    file = f"{dir}{file_hist(q_input, q_pars, p)}"
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



def _ax_objective(ax, q_input, q_pars, p, dir = ""):

    file = f"{dir}{file_hist(q_input, q_pars, p)}"
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


def plot_hist(q_input, q_pars, p):
    """ plot histograms of trains passing time from results from QUBO """


    make_plots(q_input, q_pars, p)

    display_results(q_input, q_pars, p)



def process(q_input, q_pars, p):
    """ the sequence of calculation  makes computation if results has not been saved already"""

    file = file_LP_output(q_input, q_pars, p)
    if not os.path.isfile(file):
        solve_on_LP(q_input, q_pars, p)

    file = file_QUBO(q_input, q_pars, p)
    if not os.path.isfile(file):
        prepare_qubo(q_input, q_pars, p)

    if p.compute:
        file = file_QUBO_comp(q_input, q_pars, p)
        if not os.path.isfile(file):
            solve_qubo(q_input, q_pars, p)

    if p.analyze:
        #if True:
        try:
            file = file_hist(q_input, q_pars, p)
            if not os.path.isfile(file):
                analyze_qubo(q_input, q_pars, p)

            plot_hist(q_input, q_pars, p)
        #else:
        except:
            file = file_QUBO_comp(q_input, q_pars, p)
            print(" XXXXXXXXXXXXXXXXXXXXXX  ")
            print( f"not working for {file}" )




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


    # real live problems plus PS - CS and back


    def instance_delay_string(self):
        k = self.delays.keys()
        s1 = ''.join(map(str, k))
        v = self.delays.values()
        s2 = ''.join(map(str, v))
        return f"delays_{s1}_{s2}".replace("__", "_no")

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
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/12trains/qubo_12t_{s_del}"
        self.notrains = 12


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
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/11trains/qubo_11t_{s_del}"
        self.notrains = 11

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
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/10trains/qubo_10t_{s_del}"
        self.notrains = 10

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
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/8trains/qubo_8t_{s_del}"
        self.notrains = 8


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
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/6trains/qubo_6t_{s_del}"
        self.notrains = 6



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
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/4trains/qubo_4t_{s_del}"
        self.notrains = 4


    def qubo_real_2t(self, d):
        """
        2 trains 1 pair PS - CS - PS
        
        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(1,14): "CS"}
        self.timetable = {"PS":{1:14, 14:58}, "MR":{1:17, 14:55},
                          "CS":{1:32, 14:40}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/2trains/qubo_2t_{s_del}"
        self.notrains = 2

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
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/1train/qubo_1t_{s_del}"
        self.notrains = 1



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
        self.solver = "Advantage_system6.3"
        self.token = ""
        assert self.annealing_time * self.num_reads < 1_000_000


class Process_parameters():
    def __init__(self):
        self.compute = False
        self.analyze = False
        self.softern_pass = False
        self.delta = 0


def series_of_computation(qubo, parameters, p):
    """ performs series of computation for 1 - 12 trains """
    delays_list = [{}, {1:5, 2:2, 4:5}]

    for delays in delays_list:

        qubo.qubo_real_1t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_2t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_4t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_6t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_8t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_10t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_11t(delays)
        process(qubo, parameters,p)

        qubo.qubo_real_12t(delays)
        process(qubo, parameters,p)


if __name__ == "__main__":

    real_problem = True
    make_stochatic_qubos = False

    p = Process_parameters()

    if real_problem:
        #p.compute = True
        p.analyze = True
        #p.softern_pass = True
        sim = False
        our_qubo = Input_qubo()
        q_par = Comp_parameters()

        if sim:
            q_par.method = "sim"
            for d_max in [2,6]:
                q_par.dmax = d_max

                q_par.ppair = 2.0
                q_par.psum = 4.0
                series_of_computation(our_qubo, q_par, p)

                q_par.ppair = 20.0
                q_par.psum = 40.0
                series_of_computation(our_qubo, q_par, p)
        else:
            q_par.method = "real"
            for d_max in [2,6]:
                q_par.dmax = d_max
                for at in [10, 1000]:
                    q_par.annealing_time = at

                    q_par.ppair = 2.0
                    q_par.psum = 4.0
                    series_of_computation(our_qubo, q_par, p)

                    q_par.ppair = 20.0
                    q_par.psum = 40.0
                    series_of_computation(our_qubo, q_par, p)
    
    elif make_stochatic_qubos:

        p.delta = 1
        our_qubo = Input_qubo()
        q_par = Comp_parameters()
        delays_list = [{}, {1:5, 2:2, 4:5}]

        for delays in delays_list:

            for d_max in [2,4, 6]:
                q_par.dmax = d_max

                our_qubo.qubo_real_1t(delays)
                q_par.ppair = 2.0
                q_par.psum = 4.0
                process(our_qubo, q_par, p)

                q_par.ppair = 20.0
                q_par.psum = 40.0
                process(our_qubo, q_par, p)


    else:
        # testing
        p.compute = True
        p.analyze = True
        #p.softern_pass = True
        p.delta = 0

        our_qubo = Input_qubo()
        our_qubo.qubo1()
        q_par = Comp_parameters()
        q_par.dmax = 5
        q_par.method = "sim"
        process(our_qubo, q_par, p)

        our_qubo.qubo2()
        process(our_qubo, q_par, p)


