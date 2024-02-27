import matplotlib.pyplot as plt
import pickle
import numpy as np

from .solve_sched_problems import file_hist


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



def passing_time_histigrams(q_input, q_pars, p, replace_string = ("", "")):

    file = file_hist(q_input, q_pars, p, replace_string)
    with open(file, 'rb') as fp:
        results = pickle.load(fp)

    hist_pass = results[f"{q_input.objective_stations[0]}_{q_input.objective_stations[1]}"]

    xs = list( range(np.max(hist_pass) + 1) )
    ys = [hist_pass.count(x) for x in xs]

    hist = {"x":xs, "y":ys, "stations":q_input.objective_stations, "no_trains":q_input.notrains, "dmax":q_pars.dmax,
            "ppair":q_pars.ppair, "psum":q_pars.psum, "softern":p.softern_pass, "method": q_pars.method}

    return hist


def _ax_hist_passing_times(ax, hist, add_text = True):
    """ axes for the passing time plots """
    
    xs = hist["x"]
    ys = hist["y"]
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

    

def make_plots_Dwave(q_input, q_pars, p):
    """ plotting of DWave results """

    fig, ax = plt.subplots(figsize=(4, 3))
    
    hist = passing_time_histigrams(q_input, q_pars, p)
    _ax_hist_passing_times(ax, hist)
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


def plot_hist_gates(q_pars, input4qubo, p, file_pass, file_obj, replace_pair):
    """ plots histrogram from gate computers output """

    fig, ax = plt.subplots(figsize=(4, 3))
    hist = passing_time_histigrams(input4qubo, q_pars, p, replace_string = replace_pair)
    _ax_hist_passing_times(ax, hist)
    our_title = plot_title(input4qubo, q_pars)

    fig.subplots_adjust(bottom=0.2, left = 0.15)

    plt.title(our_title)

    plt.savefig(file_pass)
    plt.clf()


    fig, ax = plt.subplots(figsize=(4, 3))

    _ax_objective(ax, input4qubo, q_pars, p, replace_string = replace_pair)
    our_title= f"{plot_title(input4qubo, q_pars)}, dmax={int(q_pars.dmax)}"

    fig.subplots_adjust(bottom=0.2, left = 0.15)
    
    plt.title(our_title)

    plt.savefig(file_obj)
    plt.clf()


# make plots

def plot_train_diagrams(v, p, file):
    "plotter of train diagrams"

    tp = list(p.trains_paths.values())[0]
    x = {tp[0]: 0}
    time = 0
    for i in range(len(tp) - 1):
        s = tp[i]
        s1 = tp[i+1]
        time += p.pass_time[f"{s}_{s1}"]
        x[tp[i+1]] = time
    time += time

    xs = {j:[] for j in p.trains_paths}
    ys = {j:[] for j in p.trains_paths}

    for i, j in enumerate( p.trains_paths ):
        for s in tp:
            for variable in v.values():
                if variable.str_id == f"t_{s}_{j}":
                    ys[j].append(variable.value)
                    if j % 2 == 1:
                        ys[j].append(variable.value+ p.stay)
                    else:
                        ys[j].append(variable.value - p.stay)

                    xs[j].append(x[s])
                    xs[j].append(x[s])

    colors = {0: "black", 1: "red", 2: "green", 3: "blue", 4: "orange", 5: "brown", 6: "cyan"}

    for i, j in enumerate( ys ):
        plt.plot(ys[j], xs[j], "o-", label=f"train {j} ", linewidth=0.85, markersize=2)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.45), ncol = 3)

    our_marks = [f"{key}" for key in x ]
    locs = list(x.values())
    plt.yticks(locs, our_marks)
    plt.xlabel("time")
    plt.ylabel("stations")
    plt.subplots_adjust(bottom=0.19, top = 0.75)
    plt.savefig(file)
    plt.clf()
