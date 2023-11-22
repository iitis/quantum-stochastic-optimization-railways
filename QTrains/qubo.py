"encoding problem as QUBO"
import copy
try:
    from .parameters import pairs_same_direction, station_pairs
except:
    from parameters import pairs_same_direction, station_pairs



def find_indices(list_to_check, item_to_find):
    return [idx for idx, value in enumerate(list_to_check) if value == item_to_find]


class QuboVars:

    def __init__(self, Railway_input):
        self.tvar_range = Railway_input.var_range
        count = 0
        vars_index = {}
        station_indexing = copy.deepcopy(Railway_input.var_range)
        trains = []
        for s in Railway_input.var_range:
            for j in Railway_input.var_range[s]:
                if j not in trains:
                    trains.append(j)
                by_t = {}
                #TODO ints if rounding may couse problems
                l_bound = int(Railway_input.var_range[s][j][0])
                u_bound = int(Railway_input.var_range[s][j][1])
                for t in range(l_bound, u_bound + 1):
                    by_t[t] = count
                    vars_index[count] = [s,j,t]
                    count += 1
                station_indexing[s][j] = by_t
        
        self.station_indexing = station_indexing
        self.vars_indexing = vars_index
        self.trains_indexing = {key:{k:station_indexing[k][key] for k in station_indexing if key in station_indexing[k]} for key in trains}



    def add_objective(self, Parameters, Railway_input):
        penalty = {}
        for s in Railway_input.penalty_at:
            for j in self.station_indexing[s]:
                l_bound = int(Railway_input.timetable[s][j])
                for t in self.station_indexing[s][j]:
                    k = self.station_indexing[s][j][t]
                    penalty[(k,k)] = (t - l_bound)/Parameters.dmax
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


    def add_headway_constrain(self, Parameters, Railway_input):
        headway_constrain = {}
        for (j, jp, s) in pairs_same_direction(Railway_input.trains_paths):
            js = self.station_indexing[s]
            if j in js and jp in js:
                for t in self.station_indexing[s][j]:
                    k = self.station_indexing[s][j][t]
                    for tp in self.station_indexing[s][jp]:
                        kp = self.station_indexing[s][jp][tp]
                        lb = max([t - Parameters.headways, self.tvar_range[s][j][0] - 1 ] )
                        ub = min([t + Parameters.headways, self.tvar_range[s][j][1] + 1 ] )
                        if lb < tp < ub:
                            headway_constrain[(k,kp)] = self.ppair
                            headway_constrain[(kp,k)] = self.ppair
        self.headway_constrain = headway_constrain



    def add_passing_time_and_stay_constrain(self, Parameters, Railway_input):
        passing_time_constrain = {}
        for (j, s, sp) in station_pairs(Railway_input.trains_paths):
            for t in self.station_indexing[s][j]:
                for tp in self.station_indexing[sp][j]:
                    lb = self.tvar_range[sp][j][0]
                    try:
                        ub = min([t + Parameters.stay + Parameters.pass_time[f"{s}_{sp}"], self.tvar_range[sp][j][1] + 1])
                    except:
                        ub = min([t + Parameters.stay + Parameters.pass_time[f"{sp}_{s}"], self.tvar_range[s][j][1] + 1])
                    if lb <= tp < ub:
                        k = self.station_indexing[s][j][t]
                        kp = self.station_indexing[sp][j][tp]
                        passing_time_constrain[(k,kp)] = self.ppair
                        passing_time_constrain[(kp,k)] = self.ppair
        self.passing_time_constrain = passing_time_constrain

    
    def add_circ_constrain(self, Parameters, Railway_input):
        circ_constrain = {}
        for _, (s, (j,jp)) in enumerate(Railway_input.circulation.items()):
            for t in self.station_indexing[s][j]:
                for tp in self.station_indexing[s][jp]:
                    lb = self.tvar_range[s][jp][0]
                    ub = min([t + Parameters.stay + Parameters.preparation_t, self.tvar_range[s][jp][1] + 1])
                    if lb <= tp < ub:
                        k = self.station_indexing[s][j][t]
                        kp = self.station_indexing[s][jp][tp]
                        circ_constrain[(k,kp)] = self.ppair
                        circ_constrain[(kp,k)] = self.ppair
        self.circ_constrain = circ_constrain
             


    def make_qubo(self, Parameters, Railway_input):
        self.add_objective(Parameters, Railway_input)
        self.add_sum_to_one_constrain()
        self.add_headway_constrain(Parameters, Railway_input)
        self.add_passing_time_and_stay_constrain(Parameters, Railway_input)
        self.add_circ_constrain(Parameters, Railway_input)
        qubo = {}
        qubo.update( self.objective_dict )
        qubo.update( self.sum_constrain_dict )
        qubo.update( self.headway_constrain )
        qubo.update( self.passing_time_constrain )
        qubo.update( self.circ_constrain)
        self.qubo = dict(sorted(qubo.items()))



    def check_broken_constrains(self, var_list):
        broken_sum = 0
        broken_headways = 0
        broken_pass = 0
        for i in find_indices(var_list, 1):
            for j in find_indices(var_list, 1):
                if (i,j) in self.sum_constrain_dict:
                    broken_sum += 1
                if (i,j) in self.headway_constrain:
                    broken_headways += 1
                if (i,j) in self.passing_time_constrain:
                    broken_pass += 1
                # TODO other
        return int(self.sum_ofset/self.psum - broken_sum), int(broken_headways/2), int(broken_pass/2)
    

    def qubo2int(self, var_list):
        print("s,j,t")
        sjt = []
        for i in find_indices(var_list, 1):
            sjt.append(self.vars_indexing[i])
        return sjt
    
    def objective_val(self, var_list):
        objective = 0
        for i in find_indices(var_list, 1):
            if (i,i) in self.objective_dict:
                objective += self.objective_dict[(i,i)]
        return objective








    




