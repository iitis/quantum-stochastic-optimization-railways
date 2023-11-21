"encoding problem as QUBO"
import copy

class QuboVars:

    def __init__(self, tvar_range):
        self.tvar_range = tvar_range
        print(tvar_range)
        count = 0
        vars_index = {}
        station_indexing = copy.deepcopy(tvar_range)
        trains = []
        for s in tvar_range:
            for j in tvar_range[s]:
                if j not in trains:
                    trains.append(j)
                by_t = {}
                #TODO ints if rounding may couse problems
                l_bound = int(tvar_range[s][j][0])
                u_bound = int(tvar_range[s][j][1])
                for t in range(l_bound, u_bound + 1):
                    by_t[t] = count
                    vars_index[count] = [s,j,t]
                    count += 1
                station_indexing[s][j] = by_t
        
        self.station_indexing = station_indexing
        self.vars_indexing = vars_index
        self.trains_indexing = {key:{k:station_indexing[k][key] for k in station_indexing if key in station_indexing[k]} for key in trains}



    def add_objective(self, penalty_at):
        penalty = {}
        for s in penalty_at:
            for j in self.station_indexing[s]:
                print(s)
                print(j)
                print(self.tvar_range[s][j])
                l_bound = int(self.tvar_range[s][j][0])
                for t in self.station_indexing[s][j]:
                    k = self.station_indexing[s][j][t]
                    penalty[(k,k)] = (t - l_bound)/self.dmax
        self.objective_dict = penalty



    


        




def mulit_indexing_variables():
    0

if __name__ == "__main__":

    tvar_range =  {"PS": {1: (0., 5.)}, "MR" :{1: (3.,8.), 3: (2.,5.)}, "CS" : {1: (16.,21.) , 3: (15., 18.)}}

    q = QuboVars(tvar_range)

    q.dmax = 5

    penalty_at = ["MR", "CS"]

    q.add_objective(penalty_at)

    print(q.objective_dict)

