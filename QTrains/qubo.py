"encoding problem as QUBO"
import copy
import numpy as np
from .parameters import pairs_same_direction, station_pairs



def find_ones(our_list):
    "find indices of ones in the list"
    return [idx for idx, value in enumerate(our_list) if value == 1]


def add_update(d1, d2):
    """ 
    auxiliary to update the qubo value in the way, 
    that new index value can be added to the previous
    """
    for key in d2:
        if key in d1:
            d1[key] += d2[key]
        else:
            d1[key] = d2[key]
    return d1


class QuboVars:
    """class of constrains and objective in the QUBO form
        - self.ppair - float pair constrain
        - self.psum - float - sum constrain
        - self.sjt_inds - indexing qbits {s:{j: {t: qbit, ...}, ...}, ...}
        - self.qbit_inds - indexing_qbits: {qbit: [s, j, t], ...}
        - self.objective - disct of objective parts {(k,k): p, ....}
        - self.sum_constrain - dict of sum to one part {(k,k): -psum, ... (k,kp): psum, (kp,k): psum  ...}
        - self.sum_ofset - float ofset from sum constrain
        - self.headway_constrain - dict from headway constrain {..., (k,kp): ppair, (kp,k): ppair,  ...}
        - self.passing_time_constrain - dict fram passing tiem constrain {..., (k,kp): ppair, (kp,k): ppair,  ...}
        - self.circ_constrain - dict fram circ constrain {..., (k,kp): ppair, (kp,k): ppair,  ...}

        - self.qubo - whole qubo - sum / concatenate of above
    """
    def __init__(self, Railway_input, ppair = 2., psum = 2.):
        self.ppair = ppair
        self.psum = psum
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

        self.sjt_inds = station_indexing
        self.qbit_inds = vars_index

        self.objective = {}
        self.sum_constrain = {}
        self.sum_ofset = 0
        self.headway_constrain = {}
        self.passing_time_constrain = {}
        self.circ_constrain = {}
        self.qubo = {}
        self.noqubits = 0



    def add_objective(self, Railway_input):
        "add objective to QuboVars class in the form of dict (k,k): objective[k]"
        penalty = {}
        for s in Railway_input.objective_stations:
            for j in self.sjt_inds[s]:
                l_bound = round(Railway_input.timetable[s][j])
                for t in self.sjt_inds[s][j]:
                    k = self.sjt_inds[s][j][t]
                    penalty[(k,k)] = (t - l_bound)/Railway_input.dmax
        self.objective = penalty



    def add_sum_to_one_constrain(self):
        """ add sum to one constrain to QuboVars class in the form of 
        dict {(k,k): -psum, ... (k,kp): psum, (kp,k): psum  ...} """
        sum_constrain = {}
        self.sum_ofset = 0
        for s in self.sjt_inds:
            for j in self.sjt_inds[s]:
                self.sum_ofset += self.psum
                for t in self.sjt_inds[s][j]:
                    k = self.sjt_inds[s][j][t]
                    sum_constrain[(k, k)] = -self.psum
                    for tp in self.sjt_inds[s][j]:
                        kp = self.sjt_inds[s][j][tp]
                        if t != tp:
                            sum_constrain[(k, kp)] = self.psum
        self.sum_constrain = sum_constrain


    def add_headway_constrain(self, Railway_input):
        """ add headway constrain to QuboVars class in the form of 
        dict {..., (k,kp): ppair, (kp,k): ppair,  ...} """
        headway_constrain = {}
        for (j, jp, s) in pairs_same_direction(Railway_input.trains_paths):
            js = self.sjt_inds[s]
            if j in js and jp in js:
                for t in self.sjt_inds[s][j]:
                    k = self.sjt_inds[s][j][t]
                    for tp in self.sjt_inds[s][jp]:
                        kp = self.sjt_inds[s][jp][tp]
                        lb = max([t - Railway_input.headways, Railway_input.tvar_range[s][j][0] - 1 ] )
                        ub = min([t + Railway_input.headways, Railway_input.tvar_range[s][j][1] + 1 ] )
                        if lb < tp < ub:
                            headway_constrain[(k,kp)] = self.ppair
                            headway_constrain[(kp,k)] = self.ppair
        self.headway_constrain = headway_constrain



    def add_passing_time_and_stay_constrain(self, Railway_input):
        """ add minimal passing time + stay to QuboVars class in the form of 
        dict {..., (k,kp): ppair, (kp,k): ppair,  ...} """
        passing_time_constrain = {}
        for (j, s, sp) in station_pairs(Railway_input.trains_paths):
            for t in self.sjt_inds[s][j]:
                for tp in self.sjt_inds[sp][j]:
                    lb = Railway_input.tvar_range[sp][j][0]
                    if (j % 2) == 1:
                        ub = min([t + Railway_input.stay + Railway_input.pass_time[f"{s}_{sp}"], Railway_input.tvar_range[sp][j][1] + 1])
                    else:
                        ub = min([t + Railway_input.stay + Railway_input.pass_time[f"{sp}_{s}"], Railway_input.tvar_range[s][j][1] + 1])
                    if lb <= tp < ub:
                        k = self.sjt_inds[s][j][t]
                        kp = self.sjt_inds[sp][j][tp]
                        passing_time_constrain[(k,kp)] = self.ppair
                        passing_time_constrain[(kp,k)] = self.ppair
        self.passing_time_constrain = passing_time_constrain


    def add_circ_constrain(self, Railway_input):
        """ add rolling stock circulation constrain to QuboVars class in the form of 
        dict {..., (k,kp): ppair, (kp,k): ppair,  ...} """
        circ_constrain = {}
        for _, ((j,jp), s) in enumerate(Railway_input.circulation.items()):
            for t in self.sjt_inds[s][j]:
                for tp in self.sjt_inds[s][jp]:
                    lb = Railway_input.tvar_range[s][jp][0]
                    ub = min([t + Railway_input.stay + Railway_input.preparation_t, Railway_input.tvar_range[s][jp][1] + 1])
                    if lb <= tp < ub:
                        k = self.sjt_inds[s][j][t]
                        kp = self.sjt_inds[s][jp][tp]
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
        add_update( qubo, self.objective )
        add_update( qubo, self.sum_constrain )
        add_update( qubo, self.headway_constrain )
        add_update( qubo, self.passing_time_constrain )
        add_update( qubo, self.circ_constrain)
        self.qubo = dict(sorted(qubo.items()))
        self.noqubits = list(self.qubo.keys())[-1][0]  + 1

    
    def store_in_dict(self, Railway_input):
        d = {}
        d["qubo"] = self.qubo
        d["objective"] = self.objective
        d["sum_constrain"] = self.sum_constrain
        d["sum_ofset"] = self.sum_ofset
        d["headway_constrain"] = self.headway_constrain
        d["passing_time_constrain"] = self.passing_time_constrain
        d["circ_constrain"] = self.circ_constrain
        d["qbit_inds"] = self.qbit_inds
        d["ppair"] = self.ppair
        d["psum"] = self.psum

        d["trains_paths"] = Railway_input.trains_paths
        d["stay_time"] = Railway_input.stay
        d["pass_time"] = Railway_input.pass_time

        return d



# this should be new class using the sbove dict

class Analyze_qubo():
    def __init__(self, d):
        self.qubo = d["qubo"]
        self.objective = d["objective"]
        self.sum_constrain = d["sum_constrain"]
        self.sum_ofset = d["sum_ofset"]
        self.headway_constrain = d["headway_constrain"]
        self.passing_time_constrain =d["passing_time_constrain"]
        self.circ_constrain= d["circ_constrain"]
        self.qbit_inds = d["qbit_inds"]
        self.ppair = d["ppair"]
        self.psum = d["psum"]

        self.trains_paths = d["trains_paths"]
        self.stay = d["stay_time"]
        self.pass_time = d["pass_time"]




    def binary_vars2sjt(self, var_list):
        """returns particular integer sjt (train j enters s at time t)
        given QUBO variables
        use if sum constrains are fulfilled
        """
        assert len(var_list) == len(self.qbit_inds)
        sjt = {}
        for i in find_ones(var_list):
            s,j,t = self.qbit_inds[i]
            sjt[(s,j)] = t
        return sjt

    def count_broken_constrains(self, var_list):
        """ given QUBO and solution ccount number of broken constrains """
        broken_sum = 0
        broken_headways = 0
        broken_pass = 0
        broken_circ = 0
        for i in find_ones(var_list):
            for j in find_ones(var_list):
                if (i,j) in self.sum_constrain:
                    broken_sum += 1
                if (i,j) in self.headway_constrain:
                    broken_headways += 1
                if (i,j) in self.passing_time_constrain:
                    broken_pass += 1
                if (i,j) in self.circ_constrain:
                    broken_circ += 1
        return round(self.sum_ofset/self.psum - broken_sum), round(broken_headways/2), round(broken_pass/2), round(broken_circ/2)


    def broken_MO_conditions(self, var_list):
        """ checks MO situations that are problematic """
        no_MO = 0
        solution = self.binary_vars2sjt(var_list)
        pair = (0,0)
        our_sign = 0
        for (j, jp, s) in pairs_same_direction(self.trains_paths):
            t1 = solution[(s,j)]
            t2 = solution[(s,jp)]
            if pair == (j,jp):
                if our_sign != np.sign(t1 - t2):
                    no_MO +=1
            else:
                pair = (j,jp)
                our_sign = np.sign(t1 - t2)
        return no_MO



    def objective_val(self, var_list):
        """ returns int, the particular objective value, given QUBO variables """
        objective = 0
        for i in find_ones(var_list):
            if (i,i) in self.objective:
                objective += self.objective[(i,i)]
        return objective
