import matplotlib.pyplot as plt
import pickle
import numpy as np
import copy

from .solve_sched_problems import file_hist



def passing_time_histigrams(trains_input, q_pars, replace_string = ("", "")):
    """ returs dict histogram of passing times between staitons in trains_input (objectvive stations) """
    file = file_hist(trains_input, q_pars, replace_string)
    with open(file, 'rb') as fp:
        results = pickle.load(fp)
    hist_pass = results[f"{trains_input.objective_stations[0]}_{trains_input.objective_stations[1]}"]

    xs = list( range(np.max(hist_pass) + 1) )
    ys = [hist_pass.count(x) for x in xs]

    hist = {"value":xs, "count":ys, "stations":trains_input.objective_stations, "no_trains":trains_input.notrains, "dmax":q_pars.dmax,
             "softern":q_pars.softern_pass}

    return hist


def objective_histograms(trains_input, q_pars, replace_string = ("", "")):
    """ returns dict histogram of objectives"""
    file = file_hist(trains_input, q_pars, replace_string)
    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    hist_obj = results["qubo objectives"]
    ground = results["lp objective"]

    xs = list(set(hist_obj))
    xs = np.sort(xs)
    ys = [hist_obj.count(x) for x in xs]

    hist = {"value":list(xs), "count":ys, "ground_state":ground}

    return hist


def energies_histograms(trains_input, q_pars, replace_string = ("", "")):
    """ returns dict histogram of energies, feasible and not feasible"""
    file = file_hist(trains_input, q_pars, replace_string)
    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    hist_feas = results["energies feasible"]
    hist_notfeas = results["energies notfeasible"]
    ground = results["lp objective"] - results["q ofset"]

    xs_f = list(set(hist_feas))
    xs_f = np.sort(xs_f)
    ys_f = [hist_feas.count(x) for x in xs_f]

    xs_nf = list(set(hist_notfeas))
    xs_nf = np.sort(xs_nf)
    ys_nf = [hist_notfeas.count(x) for x in xs_nf]

    hist = {"feasible_value":list(xs_f), "feasible_count":ys_f, "notfeasible_value":list(xs_nf), "notfeasible_count":ys_nf, "ground_state":ground}

    return hist


##### plots

def plot_title(trains_input, q_pars):
    """ title for plot of passing times """
    if trains_input.delays == {}:
        disturbed = "Not disturbed"
    else:
        disturbed = "Disturbed"
    if q_pars.method == "real":
        tit = f"{disturbed}, at={q_pars.annealing_time} mili seconds, ppair={round(q_pars.ppair)}, psum={round(q_pars.psum)}"
    else:
        tit = f"{disturbed}, {q_pars.method}, ppair={round(q_pars.ppair)}, psum={round(q_pars.psum)}"
    return tit



def _ax_hist_passing_times(ax, hist, add_text = True):
    """ axes for the passing time plots """
    
    xs = hist["value"]
    ys = hist["count"]
    ax.bar(xs,ys)

    stations = hist["stations"]
    ax.set_xlabel(f"Passing times {stations}")
    ax.set_ylabel("counts")
    if add_text:
        k = np.max(ys)/12
        no_trains = hist["no_trains"]
        dmax = int(hist["dmax"])
        ax.text(1,k, f"{no_trains} trains, dmax={dmax}", fontsize=10)

    ax.set_xlim(left=0)
    xx = [i for i in xs if i % 2 == 0]
    ax.set_xticks(xx)


def _ax_objective(ax, hist):
    """ axes for the objective plot """

    xs = hist["value"]
    ys = hist["count"]
    ground = hist["ground_state"]
    
    ax.bar(list(xs),ys, width = 0.3, color = "gray", label = "QUBO")
    ax.axvline(x = ground, lw = 2, color = 'red', linestyle = 'dashed', label = 'ground state')

    ax.legend()
    ax.set_xlabel("Objective")
    ax.set_ylabel("counts")


def make_plots_Dwave(trains_input, q_pars):
    """ plotting of DWave results """

    fig, ax = plt.subplots(figsize=(4, 3))
    
    hist = passing_time_histigrams(trains_input, q_pars)
    _ax_hist_passing_times(ax, hist)
    our_title = plot_title(trains_input, q_pars)

    fig.subplots_adjust(bottom=0.2, left = 0.15)

    plt.title(our_title)

    file = file_hist(trains_input, q_pars)
    file_pass = file.replace(".json", f"{trains_input.objective_stations[0]}_{trains_input.objective_stations[1]}.pdf")
    plt.savefig(file_pass)
    plt.clf()


    fig, ax = plt.subplots(figsize=(4, 3))

    hist = objective_histograms(trains_input, q_pars)
    _ax_objective(ax, hist)
    our_title= f"{plot_title(trains_input, q_pars)}, dmax={int(q_pars.dmax)}"

    fig.subplots_adjust(bottom=0.2, left = 0.15)
    
    plt.title(our_title)

    file = file_hist(trains_input, q_pars)
    file_obj = file.replace(".json", "obj.pdf")
    plt.savefig(file_obj)
    plt.clf()


def plot_hist_gates(q_pars, input4qubo, file_pass, file_obj, replace_pair):
    """ plots histrogram from gate computers output """

    fig, ax = plt.subplots(figsize=(4, 3))
    hist = passing_time_histigrams(input4qubo, q_pars, replace_string = replace_pair)
    _ax_hist_passing_times(ax, hist)
    our_title = plot_title(input4qubo, q_pars)

    fig.subplots_adjust(bottom=0.2, left = 0.15)

    plt.title(our_title)

    plt.savefig(file_pass)
    plt.clf()


    fig, ax = plt.subplots(figsize=(4, 3))

    hist = objective_histograms(input4qubo, q_pars, replace_string = replace_pair)
    _ax_objective(ax, hist)
    our_title= f"{plot_title(input4qubo, q_pars)}, dmax={int(q_pars.dmax)}"

    fig.subplots_adjust(bottom=0.2, left = 0.15)
    
    plt.title(our_title)

    plt.savefig(file_obj)
    plt.clf()


# train diagrams
    

def train_path_data(v, p, exclude_st = "", initial_tt = False):
    paths = p.trains_paths
    tp = list(paths.values())[0]
    tp = copy.deepcopy(tp)

    if exclude_st != "":
        tp.remove(exclude_st)

    stations_loc = {tp[0]: 0}
    time = 0
    for i in range(len(tp) - 1):
        s = tp[i]
        s1 = tp[i+1]
        time += p.pass_time[f"{s}_{s1}"]
        stations_loc[tp[i+1]] = time
    time += time

    xs = {j:[] for j in paths}
    ys = {j:[] for j in paths}

    for i, j in enumerate( paths ):
        for s in tp:
            for variable in v.values():
                if variable.str_id == f"t_{s}_{j}":
                    if initial_tt:
                        time = variable.range[0]
                    else:
                        time = variable.value
                    ys[j].append(time)
                    if j % 2 == 1:
                        ys[j].append(time + p.stay)
                    else:
                        ys[j].append(time - p.stay)

                    xs[j].append(stations_loc[s])
                    xs[j].append(stations_loc[s])
                    

    return {"space": xs, "time":ys, "stations_loc": stations_loc}
    


def plot_train_diagrams(input_dict, file):
    "plotter of train diagrams"

    xs = input_dict["space"]
    ys = input_dict["time"]
    stations_loc = input_dict["stations_loc"]


    colors = {0: "black", 1: "red", 2: "green", 3: "blue", 4: "orange", 5: "brown", 6: "cyan"}

    for j in ys.keys():
        plt.plot(ys[j], xs[j], "o-", label=f"train {j} ", linewidth=0.85, markersize=2)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.45), ncol = 3)

    our_marks = [f"{key}" for key in stations_loc]
    locs = list(stations_loc.values())
    plt.yticks(locs, our_marks)
    plt.xlabel("time")
    plt.ylabel("stations")
    plt.subplots_adjust(bottom=0.19, top = 0.75)
    plt.savefig(file)
    plt.clf()
