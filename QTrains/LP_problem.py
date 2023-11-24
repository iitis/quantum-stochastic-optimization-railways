"encoding the problem into LP / ILP"
from docplex.mp.model import Model
from .parameters import pairs_same_direction, station_pairs

class Variable():
    "stres single variable"
    def __init__(self, count, label):
        self.count = count
        self.label = label
        self.range = (0,1)
        self.value = None
        self.type = int

    def set_value(self, value):
        "set the particular value by the range with the same limits"
        self.range = (value, value)

    def reset_initial_range(self):
        self.range = (0,1)


class Variables():
    "stores list of variables"
    def __init__(self, Railway_input):
        self.trains_paths = Railway_input.trains_paths
        self.tvar_range = Railway_input.tvar_range
        self.y_vars = []
        variables = {}
        self.add_t_vars(Railway_input.trains_paths, variables)
        self.add_y_vars_same_direction(Railway_input, variables)

        self.variables = variables
        self.penalty_vars = self.indices_objective_vars(Railway_input)


    def add_t_vars(self, trains_paths, variables):
        "creates time variables"
        count = len(variables)
        for j in trains_paths:
            for s in trains_paths[j]:
                variables[f"t_{s}_{j}"] =  Variable(count, f"t_{s}_{j}")
                count += 1

    def add_y_vars_same_direction(self, Railway_input, variables):
        "create order variables for trais going the same direction"
        count = len(variables)
        for (j, jp, s) in pairs_same_direction(self.trains_paths):
            v = variables[f"t_{s}_{j}"]
            vp = variables[f"t_{s}_{jp}"]

            p = Railway_input.headways
            if v.range[1] + p >= vp.range[0] and vp.range[1] + p >= v.range[0]:
                # not create redundant variables
                self.y_vars.append(f"y_{s}_{j}_{jp}")
                variables[f"y_{s}_{j}_{jp}"] =  Variable(count, f"y_{s}_{j}_{jp}")
                count += 1


    def indices_objective_vars(self, Railway_input):
        "list index of penalties for which penalties are computed"
        penalty_vars = []
        for j in self.trains_paths:
            for s in self.trains_paths[j]:
                if s in Railway_input.objective_stations:
                    penalty_vars.append(self.variables[f"t_{s}_{j}"].count)
        return penalty_vars



class LinearPrograming():
    "linera programing (perhaps integer) functions are implemented there"
    def __init__(self, variables, railway_input, M = 10):
        self.obj = []
        self.obj_ofset = 0
        self.lhs_ineq = []
        self.rhs_ineq  = []
        self.lhs_eq = []
        self.rhs_eq = []
        self.dmax = railway_input.dmax
        self.M = M
        self.tvar_range = variables.tvar_range
        self.timetable = railway_input.timetable
        self.variables = variables.variables
        self.trains_paths = variables.trains_paths
        self.penalty_vars = variables.penalty_vars

        self.make_objective()
        self.make_objective_ofset()
        self.add_headways(railway_input)
        self.add_passing_times(railway_input)
        self.add_all_bounds()
        self.add_circ_constrain(railway_input)



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

    def compute_objective(self):
        "given the values of variables, returns the objective"
        obj = 0
        for s in self.timetable:
            for j in self.timetable[s]:
                v = self.variables[f"t_{s}_{j}"]
                if v.count in self.penalty_vars:
                    obj += v.value/self.dmax
        return obj - self.obj_ofset


    def add_headways(self, railway_input):
        "add headway constrain to the inequality matrix"
        for (j, jp, s) in pairs_same_direction(self.trains_paths):
            v = self.variables[f"t_{s}_{j}"]
            vp = self.variables[f"t_{s}_{jp}"]
            vy =self.variables[f"y_{s}_{j}_{jp}"]
            i = v.count
            ip = vp.count
            iy = vy.count

            p = railway_input.headways
            if v.range[1] + p >= vp.range[0] and vp.range[1] + p >= v.range[0]:
                # do not count trains with no dependencies

                lhs_el_y0 = [0 for _ in self.variables]
                lhs_el_y0[i] = 1
                lhs_el_y0[ip] = -1
                lhs_el_y0[iy] = self.M
                self.lhs_ineq.append(lhs_el_y0)
                self.rhs_ineq.append(-p + self.M)

                lhs_el_y1 = [0 for _ in self.variables]
                lhs_el_y1[i] = -1
                lhs_el_y1[ip] = 1
                lhs_el_y1[iy] = - self.M
                self.lhs_ineq.append(lhs_el_y1)
                self.rhs_ineq.append(-p)


    def add_passing_times(self, railway_input):
        "ad passing time constrain to inequality matrix"
        for (j, s, sp) in station_pairs(self.trains_paths):
            lhs_el = [0 for _ in self.variables]
            i = self.variables[f"t_{s}_{j}"].count
            ip = self.variables[f"t_{sp}_{j}"].count
            lhs_el[i] = 1
            lhs_el[ip] = -1
            self.lhs_ineq.append(lhs_el)
            if (j % 2) == 1:
                self.rhs_ineq.append(-railway_input.stay -railway_input.pass_time[f"{s}_{sp}"])
            else:
                self.rhs_ineq.append(-railway_input.stay -railway_input.pass_time[f"{sp}_{s}"])

    def add_circ_constrain(self, rail_input):
        "ass rolling stock circulation constrain into the inequality matrix"
        for _, (s, (j,jp)) in enumerate(rail_input.circulation.items()):
            lhs_el = [0 for _ in self.variables]
            i = self.variables[f"t_{s}_{j}"].count
            ip = self.variables[f"t_{s}_{jp}"].count
            lhs_el[i] = 1
            lhs_el[ip] = -1
            self.lhs_ineq.append(lhs_el)
            self.rhs_ineq.append(-rail_input.stay -rail_input.preparation_t)



    def add_all_bounds(self):
        "add ranges to  t variables"
        for s in self.tvar_range:
            for j in self.tvar_range[s]:
                self.variables[f"t_{s}_{j}"].range = self.tvar_range[s][j]


    def set_y_value(self, trains_s, new_value):
        "set particular value for y variable"
        (s,j,jp) = trains_s
        self.variables[f"y_{s}_{j}_{jp}"].set_value(new_value)


    def reset_y_bonds(self, trains_s):
        "reset range of y variable to (0,1)"
        (s,j,jp) = trains_s
        self.variables[f"y_{s}_{j}_{jp}"].reset_initial_range()

    def relax_integer_req(self):
        "relax integer requirements for all variables"
        for v in self.variables.values():
            v.type = float

    def restore_integer_req(self):
        "reset integer requirements for all variables"
        for v in self.variables.values():
            v.type = int


def make_ilp_docplex(prob):
    "create the docplex model return the docplex model object"
    model = Model(name='linear_programing_QTrains')

    lower_bounds = [0 for _ in prob.variables]
    upper_bounds = [0 for _ in prob.variables]

    for v in prob.variables.values():
        lower_bounds[v.count] = v.range[0]
        upper_bounds[v.count] = v.range[1]

    variables = model.integer_var_dict(prob.variables.keys(), lb=lower_bounds, ub=upper_bounds, name=prob.variables.keys())

    for index, row in enumerate(prob.lhs_ineq):
        model.add_constraint(
            sum(variables[v.label] * row[v.count] for v in prob.variables.values()) <= prob.rhs_ineq[index])

    for index, row in enumerate(prob.lhs_eq):
        model.add_constraint(
            sum(variables[v.label] * row[v.count] for v in prob.variables.values()) == prob.rhs_eq[index])

    model.minimize(sum(variables[v.label] * prob.obj[v.count] for v in prob.variables.values()))

    return model
