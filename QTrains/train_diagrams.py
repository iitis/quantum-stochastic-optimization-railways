"plots train diagram for given solutions"
import matplotlib.pyplot as plt

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
