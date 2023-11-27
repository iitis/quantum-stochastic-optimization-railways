"encoding the problem into LP / ILP"
from docplex.mp.model import Model
from .parameters import pairs_same_direction, station_pairs

class Variable():
    """single variable
        - self.int_id:: unique integer id
        - self.str_id:: unique string id (includeing stations and trains)
        - self.cluster::  id of the cluster, all variables in the cluster are supossed to be equal
    """
    def __init__(self, count, label, cluster = None):
        self.int_id = count
        self.str_id = label
        self.range = None
        self.value = None
        self.type = int
        self.cluster = cluster

    def set_value(self, value):
        "set the particular value by the range with the same limits"
        self.range = (value, value)

    def reset_initial_range_y(self):
        "reset initial range of y variable"
        self.range = (0,1)


class Variables():
    """stores all variables
        - self. tvar_range - ranges of t variables dict  
        - self.variables dict where keys are string identifier (inclyding trains and stations) and values are Variable objects:
            {"t_s_j": Variable(...) ....., "y_s_j_jp": Variable (...), }
        - self.obj_vars vector of int_id if variables that are in the objective
    """
    def __init__(self, Railway_input):
        #self.trains_paths = Railway_input.trains_paths
        self.variables = {}
        self.add_t_vars(Railway_input)
        self.add_y_vars_same_direction(Railway_input)
        self.obj_vars = self.indices_objective_vars(Railway_input)


    def add_t_vars(self, Railway_input):
        "create time variables"
        count = len(self.variables)
        for j in Railway_input.trains_paths:
            for s in Railway_input.trains_paths[j]:
                self.variables[f"t_{s}_{j}"] =  Variable(count, f"t_{s}_{j}")
                count += 1
                self.variables[f"t_{s}_{j}"].range = Railway_input.tvar_range[s][j]

    def add_y_vars_same_direction(self, Railway_input):
        "create order variables for trais going in the same direction"
        count = len(self.variables)
        for (j, jp, s) in pairs_same_direction(Railway_input.trains_paths):
            v = self.variables[f"t_{s}_{j}"]
            vp = self.variables[f"t_{s}_{jp}"]

            p = Railway_input.headways
            if v.range[1] + p >= vp.range[0] and vp.range[1] + p >= v.range[0]:
                # do not create redundant variables
                #self.y_vars.append(f"y_{s}_{j}_{jp}")
                self.variables[f"y_{s}_{j}_{jp}"] =  Variable(count, f"y_{s}_{j}_{jp}", (j,jp))
                self.variables[f"y_{s}_{j}_{jp}"].range = (0,1)
                count += 1


    def indices_objective_vars(self, Railway_input):
        "list index of penalties for which penalties are computed"
        penalty_vars = []
        for j in Railway_input.trains_paths:
            for s in Railway_input.trains_paths[j]:
                if s in Railway_input.objective_stations:
                    penalty_vars.append(self.variables[f"t_{s}_{j}"].int_id)
        return penalty_vars
    

    def set_y_value(self, trains_s, new_value):
        "set particular value for y variable"
        (s,j,jp) = trains_s
        self.variables[f"y_{s}_{j}_{jp}"].set_value(new_value)
        print(f"setting y_{s}_{j}_{jp} to {new_value}")


    def reset_y_bonds(self, trains_s):
        "reset range of y variable to (0,1)"
        (s,j,jp) = trains_s
        self.variables[f"y_{s}_{j}_{jp}"].reset_initial_range_y()
        print(f"reseting y_{s}_{j}_{jp} to (0,1)")

    def relax_integer_req(self):
        "relax integer requirements for all variables"
        for v in self.variables.values():
            v.type = float

    def restore_integer_req(self):
        "reset integer requirements for all variables"
        for v in self.variables.values():
            v.type = int

    def bonds_and_integrality(self):
        """ partial input for linprog return a range of variables
         and the type 0 - float, 1 - int """
        bounds = [(0,0) for _ in self.variables]
        integrality = [1 for _ in self.variables]
        for v in self.variables.values():
            bounds[v.int_id] = v.range
            integrality[v.int_id] = int(v.type == int)
        return bounds, integrality
    
    def check_clusters(self):
        "check if all variables in givem cluster are the same"
        clusters = {}
        for var in self.variables.values():
            if var.cluster:
                if var.cluster in clusters:
                    assert var.value == clusters[var.cluster], f"Error Message: {var.str_id} not in cluster"
                else:
                    clusters[var.cluster] = var.value




    def linprog2vars(self, linprogopt):
        """ write results of linprog optimization 
        to values of variables """
        for key in self.variables.keys():
            variable  = self.variables[key]
            variable.value = linprogopt["x"][variable.int_id]

    def docplex2vars(self, model, sol):
        """ write doclpex (model, sol) output to variables """
        for var in model.iter_variables():
            self.variables[str(var)].value = sol.get_var_value(var)



class LinearPrograming():
    """
    linera programing (perhaps integer) functions are implemented there
    - self.obj:: a vector which elements are weights to objective of corresponding variables
    - self.obj_ofset:: float - ofset due to constant term in the objective
    - self.lhs_ineq - vector of vectors of the lhs of inequality problem
    - self.rhs_ineq - vector of rhs part of ineqiality problem
    we use scipy.optimize.linprog encoding  
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
    for_k sum_i v_i lhs_{i,k} <= rhs_k
    - self.lhs_eq  / self.rhs_eq - similar but with equality
    - M - parameter of LP

    """
    def __init__(self, Variables, Railway_input, M = 10):
        self.obj = []
        self.obj_ofset = 0
        self.lhs_ineq = []
        self.rhs_ineq  = []
        self.lhs_eq = []
        self.rhs_eq = []
        self.M = M

        self.make_objective(Variables, Railway_input)
        self.make_objective_ofset(Variables, Railway_input)
        self.add_headways(Variables, Railway_input)
        self.add_passing_times(Variables, Railway_input)
        self.add_circ_constrain(Variables, Railway_input)



    def make_objective(self, Variables, Railway_input):
        "create the vector for objective"
        obj = []
        for v in Variables.variables.values():
            if v.int_id in Variables.obj_vars:
                obj.append(1/Railway_input.dmax)
            else:
                obj.append(0.0)
        self.obj = obj


    def make_objective_ofset(self, Variables, Railway_input):
        "returns float the ofset for objective"
        for s in Railway_input.timetable:
            for j in Railway_input.timetable[s]:
                if Variables.variables[f"t_{s}_{j}"].int_id in Variables.obj_vars:
                    self.obj_ofset += Railway_input.timetable[s][j]/Railway_input.dmax


    def add_headways(self, Variables, Railway_input):
        "add headway constrain to the inequality matrix"
        for (j, jp, s) in pairs_same_direction(Railway_input.trains_paths):
            v = Variables.variables[f"t_{s}_{j}"]
            vp = Variables.variables[f"t_{s}_{jp}"]
            vy = Variables.variables[f"y_{s}_{j}_{jp}"]
            i = v.int_id
            ip = vp.int_id
            iy = vy.int_id

            p = Railway_input.headways
            if v.range[1] + p >= vp.range[0] and vp.range[1] + p >= v.range[0]:
                # do not count trains with no dependencies

                lhs_el_y0 = [0 for _ in Variables.variables]
                lhs_el_y0[i] = 1
                lhs_el_y0[ip] = -1
                lhs_el_y0[iy] = self.M
                self.lhs_ineq.append(lhs_el_y0)
                self.rhs_ineq.append(-p + self.M)

                lhs_el_y1 = [0 for _ in Variables.variables]
                lhs_el_y1[i] = -1
                lhs_el_y1[ip] = 1
                lhs_el_y1[iy] = - self.M
                self.lhs_ineq.append(lhs_el_y1)
                self.rhs_ineq.append(-p)


    def add_passing_times(self, Variables, Railway_input):
        "ad passing time constrain to inequality matrix"
        for (j, s, sp) in station_pairs(Railway_input.trains_paths):
            lhs_el = [0 for _ in Variables.variables]
            i = Variables.variables[f"t_{s}_{j}"].int_id
            ip = Variables.variables[f"t_{sp}_{j}"].int_id
            lhs_el[i] = 1
            lhs_el[ip] = -1
            self.lhs_ineq.append(lhs_el)
            if (j % 2) == 1:
                self.rhs_ineq.append(-Railway_input.stay -Railway_input.pass_time[f"{s}_{sp}"])
            else:
                self.rhs_ineq.append(-Railway_input.stay -Railway_input.pass_time[f"{sp}_{s}"])

    def add_circ_constrain(self, Variables, Railway_input):
        "ass rolling stock circulation constrain into the inequality matrix"
        for _, ((j,jp), s) in enumerate(Railway_input.circulation.items()):
            lhs_el = [0 for _ in Variables.variables]
            i = Variables.variables[f"t_{s}_{j}"].int_id
            ip = Variables.variables[f"t_{s}_{jp}"].int_id
            lhs_el[i] = 1
            lhs_el[ip] = -1
            self.lhs_ineq.append(lhs_el)
            self.rhs_ineq.append(-Railway_input.stay -Railway_input.preparation_t)

    # these requires values of variables
    
    def compute_objective(self, Variables, Railway_input):
        "given the values of variables, returns the objective"
        obj = 0
        for s in Railway_input.timetable:
            for j in Railway_input.timetable[s]:
                v = Variables.variables[f"t_{s}_{j}"]
                if v.int_id in Variables.obj_vars:
                    obj += v.value/Railway_input.dmax
        return obj - self.obj_ofset
    


def make_ilp_docplex(prob, var):
    "create the docplex model return the docplex model object"
    model = Model(name='linear_programing_QTrains')

    lower_bounds = [0 for _ in var.variables]
    upper_bounds = [0 for _ in var.variables]

    for v in var.variables.values():
        lower_bounds[v.int_id] = v.range[0]
        upper_bounds[v.int_id] = v.range[1]

    variables = model.integer_var_dict(var.variables.keys(), lb=lower_bounds, ub=upper_bounds, name=var.variables.keys())

    for index, row in enumerate(prob.lhs_ineq):
        model.add_constraint(
            sum(variables[v.str_id] * row[v.int_id] for v in var.variables.values()) <= prob.rhs_ineq[index])

    for index, row in enumerate(prob.lhs_eq):
        model.add_constraint(
            sum(variables[v.str_id] * row[v.int_id] for v in var.variables.values()) == prob.rhs_eq[index])

    model.minimize(sum(variables[v.str_id] * prob.obj[v.int_id] for v in var.variables.values()))

    return model

