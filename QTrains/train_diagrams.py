"""plots train diagram for given solutions"""
import matplotlib.pyplot as plt
import matplotlib as mpl



def plot_train_diagrams(v, train_path, pass_time, stay_time, file):
    """plotter of train diagrams"""
    p = train_path[1]
    x = {p[0]: 0}
    time = 0
    for i in range(len(p) - 1):
        s = p[i]
        s1 = p[i+1]
        time += pass_time[f"{s}_{s1}"]
        x[p[i+1]] = time
    time += time

    xs = {j:[] for j in train_path}
    ys = {j:[] for j in train_path}

    for i, j in enumerate( train_path ):
        for s in p:
            for variable in v.variables.values():
                if variable.str_id == f"t_{s}_{j}":
                    ys[j].append(variable.value)
                    if j % 2 == 1:
                        ys[j].append(variable.value+ stay_time)
                    else:
                        ys[j].append(variable.value - stay_time)

                    xs[j].append(x[s])
                    xs[j].append(x[s])

    colors = {0: "black", 1: "red", 2: "green", 3: "blue", 4: "orange", 5: "brown", 6: "cyan"}

    for i, j in enumerate( ys ):
        plt.plot(ys[j], xs[j], "o-", label=f"train {j} ", linewidth=0.85, markersize=2, color = colors[i])
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.45), ncol = 3)

    our_marks = [f"{key}" for key in x ]
    locs = [v for v in x.values() ]
    plt.yticks(locs, our_marks)
    plt.xlabel("time")
    plt.ylabel("stations")
    plt.subplots_adjust(bottom=0.19, top = 0.75)
    plt.savefig(file)
