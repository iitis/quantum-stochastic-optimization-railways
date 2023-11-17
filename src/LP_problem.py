from parameters import pairs_same_direction, station_pairs


class Variables:
    "stores list of variables"

    def __init__(self, trains_paths, penalty_at):
        self.trains_paths = trains_paths
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


class LinearPrograming:

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
        self.trains_paths = variables.trains_paths
        self.penalty_vars = variables.penalty_vars



    def make_objective(self):
        obj = []
        for v in self.variables:
            if v in self.penalty_vars:
                obj.append(1/self.dmax)
            else:
                obj.append(0.0)
        self.obj = obj 

    
    def make_objective_ofset(self):
        for s in self.timetable:
            for j in self.timetable[s]:
                if f"t_{s}_{j}" in self.penalty_vars:
                    self.obj_ofset += self.timetable[s][j]/self.dmax

    def add_headways(self, p):
        for (j, jp, s) in pairs_same_direction(self.trains_paths):
  
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

    
    def add_passing_times(self, p):
        for (j, s, sp) in station_pairs(self.trains_paths):
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




# tests for now here


def test_var_class():
    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    penalty_at = ["MR", "CS"]
    v = Variables(trains_paths, penalty_at)  
    assert v.trains_paths == trains_paths
    assert v.make_t_vars(trains_paths) == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3']
    assert v.make_y_vars_same_direction(trains_paths) == ['y_MR_1_3', 'y_CS_1_3']
    assert v.make_penalty_vars(trains_paths, penalty_at) == ['t_MR_1', 't_CS_1', 't_MR_3', 't_CS_3']


def test_LP_class():
    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    penalty_at = ["MR", "CS"]
    v = Variables(trains_paths, penalty_at)
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 16}, "CS" : {1: 0 , 3: 13}}    
    example_problem = LinearPrograming(timetable, v)
    assert example_problem.timetable == timetable
    assert example_problem.trains_paths == trains_paths
    assert example_problem.variables == ['t_PS_1', 't_MR_1', 't_CS_1', 't_MR_3', 't_CS_3', 'y_MR_1_3', 'y_CS_1_3']
    assert example_problem.penalty_vars == ['t_MR_1', 't_CS_1', 't_MR_3', 't_CS_3']
    example_problem.dmax = 5
    example_problem.make_objective()
    assert example_problem.obj == [0.0, 0.2, 0.2, 0.2, 0.2, 0.0, 0.0]
    example_problem.make_objective_ofset()
    assert example_problem.obj_ofset == 6.4
    tvar_range =  {"PS": {1: (0., 5.)}, "MR" :{1: (3.,8.), 3: (2.,5.)}, "CS" : {1: (16.,21.) , 3: (15., 18.)}}
    example_problem.add_all_bounds(tvar_range)
    assert example_problem.bnd == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 5.0), (15.0, 18.0), (0.0, 1.0), (0.0, 1.0)]
    example_problem.set_y_value(('MR', 1, 3), 1)
    assert example_problem.bnd == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 5.0), (15.0, 18.0), (1,1), (0.0, 1.0)]
    example_problem.reset_y_bonds(('MR', 1, 3))
    assert example_problem.bnd == [(0.0, 5.0), (3.0, 8.0), (16.0, 21.0), (2.0, 5.0), (15.0, 18.0), (0.0, 1.0), (0.0, 1.0)]


def test_parametrised_constrains():
    from parameters import Parameters
    p = Parameters()
    p.headways = 2
    trains_paths = {1: ["PS", "MR", "CS"], 3: ["MR", "CS"]}
    penalty_at = ["MR", "CS"]
    v = Variables(trains_paths, penalty_at)
    timetable =  {"PS": {1: 0}, "MR" :{1: 3, 3: 16}, "CS" : {1: 0 , 3: 13}} 
    example_problem = LinearPrograming(timetable, v)
    example_problem.add_headways(p)
    assert example_problem.lhs_ineq == [[0, 1, 0, -1, 0, 0, 0], [0, -1, 0, 1, 0, 0, 0], [0, 0, 1, 0, -1, 0, 0], [0, 0, -1, 0, 1, 0, 0]]
    assert example_problem.rhs_ineq == [-2, -2, -2, -2]

    p = Parameters()
    p.stay = 1
    p.pass_time = {f"PS_MR": 2, f"MR_CS": 12}
    example_problem = LinearPrograming(timetable, v)
    example_problem.add_passing_times(p)
    assert example_problem.lhs_ineq  == [[1, -1, 0, 0, 0, 0, 0], [0, 1, -1, 0, 0, 0, 0], [0, 0, 0, 1, -1, 0, 0]]
    assert example_problem.rhs_ineq == [-3, -13, -13]



if __name__ == "__main__":
    test_var_class()
    test_LP_class()
    test_parametrised_constrains()