"encoding problem as QUBO"
import copy
try:
    from .parameters import pairs_same_direction, station_pairs, Parameters
except:
    from parameters import pairs_same_direction, station_pairs, Parameters

class QuboVars:

    def __init__(self, tvar_range):
        self.tvar_range = tvar_range
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



    def add_objective(self, penalty_at, timetable):
        penalty = {}
        for s in penalty_at:
            for j in self.station_indexing[s]:
                print(s)
                print(j)
                l_bound = int(timetable[s][j])
                print(l_bound)
                for t in self.station_indexing[s][j]:
                    k = self.station_indexing[s][j][t]
                    penalty[(k,k)] = (t - l_bound)/self.dmax
        self.objective_dict = penalty



    def add_sum_to_one_constrain(self):
        sum_constrain = {}
        self.sum_ofset = 0
        for s in self.station_indexing:
            for j in self.station_indexing[s]:
    
                self.sum_ofset += self.psum
                for t in self.station_indexing[s][j]:
                    k = self.station_indexing[s][j][t]
                    sum_constrain[(k, k)] = -self.psum
                    for tp in self.station_indexing[s][j]:
                        kp = self.station_indexing[s][j][tp]
                        if t != tp:
                            sum_constrain[(k, kp)] = self.psum
        
        self.sum_constrain_dict = sum_constrain


    def add_headway_constrain(self, p, trains_paths):
        headway_constrain = {}
        for (j, jp, s) in pairs_same_direction(trains_paths):
            js = self.station_indexing[s]
            if j in js and jp in js:
                for t in self.station_indexing[s][j]:
                    k = self.station_indexing[s][j][t]
                    for tp in self.station_indexing[s][jp]:
                        kp = self.station_indexing[s][jp][tp]
                        lb = max([t - p.headways, self.tvar_range[s][j][0]])
                        ub = min([t + p.headways, self.tvar_range[s][j][1]])
                        if lb < tp < ub:
                            headway_constrain[(k,kp)] = self.ppair
                            headway_constrain[(kp,k)] = self.ppair
        self.headway_constrain = headway_constrain



    def add_passing_time_and_stay_constrain(self, p, trains_paths):
        passing_time_constrain = {}
        for (j, s, sp) in station_pairs(trains_paths):
            for t in self.station_indexing[s][j]:
                for tp in self.station_indexing[sp][j]:
                    lb = self.tvar_range[sp][j][0]
                    ub = min([t + p.stay + p.pass_time[f"{s}_{sp}"], self.tvar_range[sp][j][1]])
                    if lb <= tp < ub:
                        k = self.station_indexing[s][j][t]
                        kp = self.station_indexing[sp][j][tp]
                        passing_time_constrain[(k,kp)] = self.ppair
                        passing_time_constrain[(kp,k)] = self.ppair
        self.passing_time_constrain = passing_time_constrain









    


        




def mulit_indexing_variables():
    0

if __name__ == "__main__":

    tvar_range =  {"PS": {1: (0., 5.)}, "MR" :{1: (3.,8.), 3: (2.,5.)}, "CS" : {1: (16.,21.) , 3: (15., 18.)}}

    q = QuboVars(tvar_range)

    q.dmax = 5
    q.psum = 2
    q.ppair = 2

    penalty_at = ["MR", "CS"]

    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 0}, "CS" : {1: 16 , 3: 13}} 


    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}

    p = Parameters()
    p.stay = 1
    p.headways = 2
    p.pass_time = {f"PS_MR": 2, f"MR_CS": 12}

    q.add_passing_time_and_stay_constrain(p, trains_paths)

    assert len(q.passing_time_constrain) == 72

    for (k, kp) in q.passing_time_constrain:
        if "CS" in [ q.vars_indexing[k][0],  q.vars_indexing[kp][0] ]:
           assert -13 < q.vars_indexing[k][2] - q.vars_indexing[kp][2] < 13 



