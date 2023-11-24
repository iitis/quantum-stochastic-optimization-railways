"encoding problem as QUBO"
import copy
from .parameters import pairs_same_direction, station_pairs



def find_indices(our_list, item):
    "find indices of item in the list"
    return [idx for idx, value in enumerate(our_list) if value == item]


class QuboVars:
    "class of constrains and objective in the QUBO form"
    def __init__(self, Railway_input):
        self.ppair = 2
        self.psum = 2
        self.tvar_range = Railway_input.tvar_range
        count = 0
        vars_index = {}
        station_indexing = copy.deepcopy(Railway_input.tvar_range)
        trains = []
        for s in Railway_input.tvar_range:
            for j in Railway_input.tvar_range[s]:
                if j not in trains:
                    trains.append(j)
                by_t = {}
                l_bound = round(Railway_input.tvar_range[s][j][0])
                u_bound = round(Railway_input.tvar_range[s][j][1])
                for t in range(l_bound, u_bound + 1):
                    by_t[t] = count
                    vars_index[count] = [s,j,t]
                    count += 1
                station_indexing[s][j] = by_t
        self.sum_ofset = 0
        self.station_indexing = station_indexing
        self.vars_indexing = vars_index
        self.objective = {}
        self.sum_constrain = {}
        self.headway_constrain = {}
        self.passing_time_constrain = {}
        self.circ_constrain = {}
        self.qubo = {}



    def add_objective(self, Railway_input):
        "add objective to QuboVars class in the form of dict (k,k): objective[k]"
        penalty = {}
        for s in Railway_input.objective_stations:
            for j in self.station_indexing[s]:
                l_bound = round(Railway_input.timetable[s][j])
                for t in self.station_indexing[s][j]:
                    k = self.station_indexing[s][j][t]
                    penalty[(k,k)] = (t - l_bound)/Railway_input.dmax
        self.objective = penalty



    def add_sum_to_one_constrain(self):
        """ add sum to one constrain to QuboVars class in the form of 
        dict {(k,k): -psum, ... (k,kp): psum, (kp,k): psum  ...} """
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
        self.sum_constrain = sum_constrain


    def add_headway_constrain(self, Railway_input):
        """ add headway constrain to QuboVars class in the form of 
        dict {..., (k,kp): ppair, (kp,k): ppair,  ...} """
        headway_constrain = {}
        for (j, jp, s) in pairs_same_direction(Railway_input.trains_paths):
            js = self.station_indexing[s]
            if j in js and jp in js:
                for t in self.station_indexing[s][j]:
                    k = self.station_indexing[s][j][t]
                    for tp in self.station_indexing[s][jp]:
                        kp = self.station_indexing[s][jp][tp]
                        lb = max([t - Railway_input.headways, self.tvar_range[s][j][0] - 1 ] )
                        ub = min([t + Railway_input.headways, self.tvar_range[s][j][1] + 1 ] )
                        if lb < tp < ub:
                            headway_constrain[(k,kp)] = self.ppair
                            headway_constrain[(kp,k)] = self.ppair
        self.headway_constrain = headway_constrain



    def add_passing_time_and_stay_constrain(self, Railway_input):
        """ add minimal passing time + stay to QuboVars class in the form of 
        dict {..., (k,kp): ppair, (kp,k): ppair,  ...} """
        passing_time_constrain = {}
        for (j, s, sp) in station_pairs(Railway_input.trains_paths):
            for t in self.station_indexing[s][j]:
                for tp in self.station_indexing[sp][j]:
                    lb = self.tvar_range[sp][j][0]
                    if (j % 2) == 1:
                        ub = min([t + Railway_input.stay + Railway_input.pass_time[f"{s}_{sp}"], self.tvar_range[sp][j][1] + 1])
                    else:
                        ub = min([t + Railway_input.stay + Railway_input.pass_time[f"{sp}_{s}"], self.tvar_range[s][j][1] + 1])
                    if lb <= tp < ub:
                        k = self.station_indexing[s][j][t]
                        kp = self.station_indexing[sp][j][tp]
                        passing_time_constrain[(k,kp)] = self.ppair
                        passing_time_constrain[(kp,k)] = self.ppair
        self.passing_time_constrain = passing_time_constrain


    def add_circ_constrain(self, Railway_input):
        """ add rolling stock circulation constrain to QuboVars class in the form of 
        dict {..., (k,kp): ppair, (kp,k): ppair,  ...} """
        circ_constrain = {}
        for _, (s, (j,jp)) in enumerate(Railway_input.circulation.items()):
            for t in self.station_indexing[s][j]:
                for tp in self.station_indexing[s][jp]:
                    lb = self.tvar_range[s][jp][0]
                    ub = min([t + Railway_input.stay + Railway_input.preparation_t, self.tvar_range[s][jp][1] + 1])
                    if lb <= tp < ub:
                        k = self.station_indexing[s][j][t]
                        kp = self.station_indexing[s][jp][tp]
                        circ_constrain[(k,kp)] = self.ppair
                        circ_constrain[(kp,k)] = self.ppair
        self.circ_constrain = circ_constrain


    def make_qubo(self, Railway_input):
        """create sorted QUBO dict with all constrains """
        self.add_objective(Railway_input)
        self.add_sum_to_one_constrain()
        self.add_headway_constrain(Railway_input)
        self.add_passing_time_and_stay_constrain( Railway_input)
        self.add_circ_constrain( Railway_input)
        qubo = {}
        qubo.update( self.objective )
        qubo.update( self.sum_constrain )
        qubo.update( self.headway_constrain )
        qubo.update( self.passing_time_constrain )
        qubo.update( self.circ_constrain)
        self.qubo = dict(sorted(qubo.items()))
        self.noqubits = list(self.qubo.keys())[-1][0]  + 1



    def count_broken_constrains(self, var_list):
        """ given QUBO and solution ccount number of broken constrains """
        broken_sum = 0
        broken_headways = 0
        broken_pass = 0
        broken_circ = 0
        for i in find_indices(var_list, 1):
            for j in find_indices(var_list, 1):
                if (i,j) in self.sum_constrain:
                    broken_sum += 1
                if (i,j) in self.headway_constrain:
                    broken_headways += 1
                if (i,j) in self.passing_time_constrain:
                    broken_pass += 1
                if (i,j) in self.circ_constrain:
                    broken_circ += 1
        return round(self.sum_ofset/self.psum - broken_sum), round(broken_headways/2), round(broken_pass/2), round(broken_circ/2)


    def binary_vars2sjt(self, var_list):
        """returns particular integer sjt (train j enters s at time t)
        given QUBO variables
        """
        sjt = []
        for i in find_indices(var_list, 1):
            sjt.append(self.vars_indexing[i])
        return sjt


    def objective_val(self, var_list):
        """ returns int, the particular objective value, given QUBO variables """
        objective = 0
        for i in find_indices(var_list, 1):
            if (i,i) in self.objective:
                objective += self.objective[(i,i)]
        return objective
