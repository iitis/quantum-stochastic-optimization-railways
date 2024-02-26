""" prepare and analyze small qubos for gate computiong """
import pickle
import json
import matplotlib.pyplot as plt

from QTrains import Analyze_qubo
from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import file_QUBO_comp, file_hist, file_QUBO, file_LP_output
from QTrains import analyze_outputs_gates, plot_hist_gates
from trains_timetable import Input_qubo

from solve_qubo import Comp_parameters, Process_parameters



plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=10)


    
class Cases:
    """ Class for case based modifications """
    def __init__(self, case):
        assert case in [-7, -6, -5, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.case = case
        self.ground = []
        self.comp_specifics_string = ""



    def gate_specifics(self, small_sample, q_pars):
        """ assigns string of specifics of gate computers or its simulators """
        if q_pars.method == "IonQsim":
            if small_sample:
                self.comp_specifics_string = "summary.ionq-sim-aria."
            else:
                if self.case == 4:
                    self.comp_specifics_string = "summary.53."
                if self.case == 8:
                    self.comp_specifics_string =  "summary.51."
                if self.case == 9:
                    self.comp_specifics_string = "summary.51."
            if self.case == 10:
                self.comp_specifics_string = "summary.50."



    def update_problems_parameters(self, input4qubo, q_pars, p):

        if self.case in [-3, -2, -1, 1, 2, 3, 4, 9]:
            q_pars.ppair = 2.0
            q_pars.psum = 4.0
        if self.case in [-7, -6, -5, 5, 6, 7, 8, 10 ]:
            q_pars.ppair = 20.0
            q_pars.psum = 40.0

        if self.case in [-5, -1, 1, 4, 5, 8, 9, 10]:
            q_pars.dmax = 2
        if self.case in [-6, -2, 2, 6]:
            q_pars.dmax = 4
        if self.case in [-7, -3, 3, 7]:
            q_pars.dmax = 6

        if self.case in [-7, -6, -5, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8]:
            delays = {}
        if self.case in [9,10]:
            delays = {1:5, 2:2, 4:5}

        if self.case in [-7, -6, -5, -3, -2, -1, 1, 2, 3, 5, 6, 7]:
            input4qubo.qubo_real_1t(delays)
        if self.case in [4, 8,9,10]:
            input4qubo.qubo_real_2t(delays)

        p.softern_pass = False
        if self.case < 0:
            p.delta = 1

if __name__ == "__main__":

    save_qubo = True
    small_sample_results = False
    
    input4qubo = Input_qubo()
    q_pars = Comp_parameters()
    q_pars.method = "IonQsim"
    p = Process_parameters()

    for case_no in [4,8,9,10]:
    #for case_no in [1,5,2,6]:
        
        case = Cases(case_no)

        case.update_problems_parameters(input4qubo, q_pars, p)


        file_q = file_QUBO(input4qubo, q_pars, p)
        with open(file_q, 'rb') as fp:
            dict_read = pickle.load(fp)


        file = file_LP_output(input4qubo, q_pars, p)
        with open(file, 'rb') as fp:
            lp_sol = pickle.load(fp)

        case.gate_specifics(small_sample_results,  q_pars)
        replace_pair = ("2trains/", f"2trains_IonQSimulatorResults_18_Qubits/{case.comp_specifics_string}")
        file_comp = file_QUBO_comp(input4qubo, q_pars, p, replace_pair)  
        file_h = file_hist(input4qubo, q_pars, p, replace_pair)


        if save_qubo:

            Q = Analyze_qubo(dict_read)


            qubo_solution = Q.int_vars2qubo(lp_sol["variables"])

            all_solutions = Q.heuristics_degenerate(qubo_solution, "PS")

            solutions = all_solutions
            results = analyze_outputs_gates(Q, input4qubo.objective_stations, all_solutions, lp_sol, p.softern_pass)

            #save_qubo_4gates_comp(dict_read, ground_state, file_q)

        else:

            with open(file_comp, 'r') as fp:
                solutions_input = json.load(fp)

            solutions = [sol["vars"] for sol in solutions_input]
            print([sol["energy"] for sol in solutions_input])

            Q = Analyze_qubo(dict_read)
            results = analyze_outputs_gates(Q, input4qubo.objective_stations, solutions, lp_sol, p.softern_pass)

            with open(file_h, 'wb') as fp:
                pickle.dump(results, fp)

            file_pass = f"{file_h}time_hists.pdf"
            file_obj = f"{file_h}obj.pdf"
            
            plot_hist_gates(q_pars, input4qubo, p, file_pass, file_obj, replace_pair)
