"encoding the problem into LP / ILP"

from .parameters import pairs_same_direction, station_pairs

class Variable():
    "stres single variable"
    def __init__(self, count, label):
        self.count = count
        self.label = label
        self.range = (0,1)
        self.value = None
        self.type = None

    def set_value(self, value):
        "set the particular value by the range with the same limits"
        self.range = (value, value)

    def reset_initial_range(self):
        self.range = (0,1)


class Variables():
    "stores list of variables"

    def __init__(self, trains_paths, penalty_at):
        self.trains_paths = trains_paths
        self.count_y_vars = 0
        variables1 = {}
        self.make_t_vars(trains_paths, variables1)
        self.make_y_vars_same_direction(trains_paths, variables1)
        #y_vars_od =
        self.variables = variables1
        self.penalty_vars = self.make_penalty_vars(trains_paths, penalty_at)


    def make_t_vars(self, trains_paths, variables):
        "creates time variables"
        count = len(variables)
        for j in trains_paths:
            for s in trains_paths[j]:
                variables[f"t_{s}_{j}"] =  Variable(count, f"t_{s}_{j}")
                count += 1


    def make_penalty_vars(self, trains_paths, penalty_at):
        "list index of penalties for which penalties are computed"
        penalty_vars = []
        for j in trains_paths:
            for s in trains_paths[j]:
                if s in penalty_at:
                    penalty_vars.append(self.variables[f"t_{s}_{j}"].count)
        return penalty_vars


    def make_y_vars_same_direction(self, trains_paths, variables):
        "create order variables for trais going the same direction"
        count = len(variables)
        for (j, jp, s) in pairs_same_direction(trains_paths):
            self.count_y_vars += 1
            variables[f"y_{s}_{j}_{jp}"] =  Variable(count, f"y_{s}_{j}_{jp}")
            count += 1



class LinearPrograming(Variables):
    "linera programing (perhaps integer) functions are implemented there"
    def __init__(self, Variables, timetable):
        self.obj = []
        self.obj_ofset = 0
        self.lhs_ineq = []
        self.rhs_ineq  = []
        self.lhs_eq = []
        self.rhs_eq = []
        self.dmax = 0
        self.M = 0
        self.timetable = timetable
        self.variables = Variables.variables
        self.trains_paths = Variables.trains_paths
        self.penalty_vars = Variables.penalty_vars



    def make_objective(self):
        "create the vector for objective"
        obj = []
        for v in self.variables.values():
            if v.count in self.penalty_vars:
                obj.append(1/self.dmax)
            else:
                obj.append(0.0)
        self.obj = obj


    def make_objective_ofset(self):
        "returns float the ofset for objective"
        for s in self.timetable:
            for j in self.timetable[s]:
                if self.variables[f"t_{s}_{j}"].count in self.penalty_vars:
                    self.obj_ofset += self.timetable[s][j]/self.dmax

    def add_headways(self, p):
        "add headway constrain to the inequality matrix"
        for (j, jp, s) in pairs_same_direction(self.trains_paths):
            i = self.variables[f"t_{s}_{j}"].count
            ip = self.variables[f"t_{s}_{jp}"].count
            iy = self.variables[f"y_{s}_{j}_{jp}"].count

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


    def add_passing_times(self, p):
        "ad passing time constrain to inequality matrix"
        for (j, s, sp) in station_pairs(self.trains_paths):
            lhs_el = [0 for _ in self.variables]
            i = self.variables[f"t_{s}_{j}"].count
            ip = self.variables[f"t_{sp}_{j}"].count
            lhs_el[i] = 1
            lhs_el[ip] = -1
            self.lhs_ineq.append(lhs_el)
            self.rhs_ineq.append(-p.stay -p.pass_time[f"{s}_{sp}"])


    def add_all_bounds(self, tvar_range):
        "add bonds to all t variables"
        for s in tvar_range:
            for j in tvar_range[s]:
                self.variables[f"t_{s}_{j}"].range = tvar_range[s][j]


    def set_y_value(self, trains_s, new_value):
        "set particular value for y variable"
        (s,j,jp) = trains_s
        self.variables[f"y_{s}_{j}_{jp}"].set_value(new_value)

    def reset_y_bonds(self, trains_s):
        "reset bonds for y variable to (0,1)"
        (s,j,jp) = trains_s
        self.variables[f"y_{s}_{j}_{jp}"].reset_initial_range()
