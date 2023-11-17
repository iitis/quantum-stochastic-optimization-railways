from difflib import SequenceMatcher
import itertools




def match_lists(a, b):
    match = SequenceMatcher(None, a, b).find_longest_match()
    return a[match.a:match.a + match.size], match.size

def common_s_same_dir(trains_paths, j, jp):
    stations, size = match_lists(trains_paths[j], trains_paths[jp])
    if size > 1:
        return stations
    return []

def pairs_same_direction(trains_paths):
    trains_station = []
    for [j,jp] in itertools.product(trains_paths, trains_paths):
        if jp > j:
            stations = common_s_same_dir(trains_paths, j,jp)
            for s in stations:
                trains_station.append((j, jp, s))
    return  trains_station

def station_pairs(trains_paths):
    trains_stations = []
    for j in trains_paths:
        stations = trains_paths[j]
        l = len(stations)
        for k in range(l-1):
            s = stations[k]
            sp = stations[k+1]
            trains_stations.append([j,s,sp])
    return trains_stations



class Parameters:
    def __init__(self):
        self.headways = 0
        self.stay = 0
        self.pass_time = {}


class Variables:
    "stores list of variables"

    def __init__(self, trains_paths, penalty_at):
        self.train_paths = trains_paths
        variables = []
        variables += self.make_t_vars(trains_paths)
        variables += self.make_y_vars_same_direction(trains_paths)
        #y_vars_od = 
        self.variables = variables
        self.penalty_vars = self.make_penalty_vars(trains_paths, penalty_at)

    def make_t_vars(self, trains_paths):
        t_vars = []
        for j in trains_paths:
            for s in trains_paths[j]:
                t_vars.append(f"t_{s}_{j}")
        return t_vars

    def make_penalty_vars(self, trains_paths, penalty_at):
        penalty_vars = []
        for j in trains_paths:
            for s in trains_paths[j]:
                if s in penalty_at:
                    penalty_vars.append(f"t_{s}_{j}")
        return penalty_vars


    def make_y_vars_same_direction(self, trains_paths):
        y_vars = []
        for (j, jp, s) in pairs_same_direction(trains_paths):
            y_vars.append(f"y_{s}_{j}_{jp}")
        return y_vars


class Lp:

    def __init__(self, timetable, variables):
        self.obj = []
        self.obj_ofset = 0
        self.lhs_ineq = []
        self.rhs_ineq  = []
        self.lhs_eq = []
        self.rhs_eq = []
        self.bnd = []
        self.dmax = 0
        self.M = 0
        self.timetable = timetable
        self.variables = variables.variables
        self.train_paths = variables.train_paths
        self.penalty_vars = variables.penalty_vars



    def make_objective(self):
        obj = []
        for v in self.variables:
            if v in self.penalty_vars:
                obj.append(1/self.dmax)
            else:
                obj.append(0.0)
        self.obj = obj 

    
    def make_objective_ofset(self, timetable):
        for s in self.timetable:
            for j in self.timetable[s]:
                if f"t_{s}_{j}" in self.penalty_vars:
                    self.obj_ofset += timetable[s][j]/self.dmax

    def add_headways(self, p):
        for (j, jp, s) in pairs_same_direction(self.train_paths):
  
            i = self.variables.index(f"t_{s}_{j}")
            ip = self.variables.index(f"t_{s}_{jp}")
            iy = self.variables.index(f"y_{s}_{j}_{jp}")

            lhs_el_y0 = [0 for _ in self.variables]
            lhs_el_y0[i] = 1
            lhs_el_y0[ip] = -1
            lhs_el_y0[iy] = self.M
            self.lhs_ineq.append(lhs_el_y0)
            self.rhs_ineq.append(-p.headways + self.M)

            lhs_el_y1 = [0 for _ in self.variables]
            lhs_el_y1[i] = -1
            lhs_el_y1[ip] = 1
            lhs_el_y1[iy] = - self.M
            self.lhs_ineq.append(lhs_el_y1)
            self.rhs_ineq.append(-p.headways)

    
    def add_passing_times(self, p, trains_paths):
        for (j, s, sp) in station_pairs(trains_paths):
            lhs_el = [0 for _ in self.variables]
            i = self.variables.index(f"t_{s}_{j}")
            ip = self.variables.index(f"t_{sp}_{j}")
            lhs_el[i] = 1
            lhs_el[ip] = -1
            self.lhs_ineq.append(lhs_el)
            self.rhs_ineq.append(-p.stay -p.pass_time[f"{s}_{sp}"])

    
    def add_all_bounds(self, tvar_range):
        bound = [(0.0,1.0) for _ in self.variables]
        for s in tvar_range:
            for j in tvar_range[s]:
                i = self.variables.index(f"t_{s}_{j}")
                bound[i] = tvar_range[s][j]
        self.bnd = bound

    
    def set_y_value(self, trains_s, new_value):
        (s,j,jp) = trains_s
        i = self.variables.index(f"y_{s}_{j}_{jp}")
        self.bnd[i] = (new_value,new_value)

    def reset_y_bonds(self, trains_s):
        (s,j,jp) = trains_s
        i = self.variables.index(f"y_{s}_{j}_{jp}")
        self.bnd[i] = (0.0, 1.0)





# presentations





