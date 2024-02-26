""" prepare and analyze small qubos for gate computiong """
import pickle
import copy
import json
import matplotlib.pyplot as plt
import itertools

from QTrains import Analyze_qubo, update_hist
from QTrains import file_LP_output, file_QUBO, file_QUBO_comp, file_hist
from QTrains import file_QUBO_comp, file_hist, file_QUBO, file_LP_output
from QTrains import _ax_hist_passing_times, _ax_objective, plot_title
from trains_timetable import Input_qubo

from solve_qubo import Comp_parameters, Process_parameters



plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rc('font', size=10)


def dsiplay_analysis_gates(q_input, our_solution, lp_solution, timetable = False):
    "prints features of the solution fram gate computer"
    print( "..........  QUBO ........   " )
    #print("qubo size=", len( q_input.qubo ), " number of Q-bits=", len( our_solution ))
    print("energy=", q_input.energy( our_solution ))
    print("energy + ofset=", q_input.energy( our_solution ) + q_input.sum_ofset)
    print("QUBO objective=", q_input.objective_val( our_solution ), "  ILP objective=", lp_solution["objective"] )

    print("broken (sum, headway, pass, circ)", q_input.count_broken_constrains( our_solution ))
    print("broken MO", q_input.broken_MO_conditions( our_solution ))

    if timetable:
        print(" ........ vars values  ........ ")
        print(" key, qubo, LP ")

        vq = q_input.qubo2int_vars( our_solution )
        for k, v in vq.items():
            print(k, v.value, lp_solution["variables"][k].value)
        print("  ..............................  ")


def save_qubo_gates(dict_qubo, ground_sols, input_file):
    "creates and seves file with ground oslution and small qubo for gate computing"
    our_qubo = Analyze_qubo(dict_qubo)
    qubo4gates = {}
    qubo4gates["qubo"] = dict_qubo["qubo"]
    qubo4gates["ground_solutions"] = ground_sols
    E = our_qubo.energy(ground_sols[0])
    for ground_sol in ground_sols:
        assert E == our_qubo.energy(ground_sol)
    qubo4gates["ground_energy"] = E
    
    new_file = input_file.replace("LR_timetable/", "gates/")
    with open(new_file, 'wb') as fp_w:
        pickle.dump(qubo4gates, fp_w)




def analyze_outputs_gates(qubo, q_input, our_solutions, lp_solution, p):
    """  returns histogram of passing times between selected stations and objective 
         outputs of gate computer
    """
    hist = list([])
    qubo_objectives = list([])

    count = 0
    no_feasible = 0
    stations = q_input.objective_stations

    for solution in our_solutions:
        dsiplay_analysis_gates(qubo, solution, lp_solution)

        count += 1
        no_feasible += update_hist(qubo, solution, stations, hist, qubo_objectives, p.softern_pass)
        print("feasible", bool(no_feasible))
        print(hist)
        print(qubo_objectives)
    
    perc_feasible = no_feasible/count

    results = {"perc feasible": perc_feasible, f"{stations[0]}_{stations[1]}": hist}
    results["no qubits"] = qubo.noqubits
    results["no qubo terms"] = len(qubo.qubo)
    results["lp objective"] = lp_sol["objective"]
    results["q ofset"] = qubo.sum_ofset
    results["qubo objectives"] = qubo_objectives
    return results



def plot_gate_gates(q_pars, input4qubo, p, file_pass, file_obj, replace_pair):
    """ plots histrogram from gate computers output """

    fig, ax = plt.subplots(figsize=(4, 3))
    _ax_hist_passing_times(ax, input4qubo, q_pars, p, replace_string = replace_pair)
    our_title = plot_title(input4qubo, q_pars)

    fig.subplots_adjust(bottom=0.2, left = 0.15)

    plt.title(our_title)

    plt.savefig(file_pass)
    plt.clf()


    fig, ax = plt.subplots(figsize=(4, 3))

    _ax_objective(ax, input4qubo, q_pars, p, replace_string = replace_pair)
    our_title= f"{plot_title(input4qubo, q_pars)}, dmax={int(q_pars.dmax)}"

    fig.subplots_adjust(bottom=0.2, left = 0.15)
    
    plt.title(our_title)

    plt.savefig(file_obj)
    plt.clf()


    
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


    def get_ground(self):
        """ returns ground state solution given case number """
        if self.case in [1, 5]:
            ground_solution = [1,0,0,1,0,0]
        if self.case in [-1, -5]:
            ground_solution = [1,0,0,0,1,0]
        if self.case in [2, 6]:
            ground_solution = [1,0,0,0,0,1,0,0,0,0]
        if self.case in [-2, -6]:
            ground_solution = [1,0,0,0,0,0,1,0,0,0]
        if self.case in [3, 7]:
            ground_solution = [1,0,0,0,0,0,0,1,0,0,0,0,0,0]
        if self.case in [-3, -7]:
            ground_solution = [1,0,0,0,0,0,0,0,1,0,0,0,0,0]
        if self.case in [4, 8]:
            ground_solution = [1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0]
        if self.case in [9, 10]:
            ground_solution = [1,0,0,0,1,0,1,0,0,0,1,0,1,0,0,0,1,0]
        self.ground = ground_solution


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
            results = analyze_outputs_gates(Q, input4qubo, all_solutions, lp_sol, p)

            #save_qubo_gates(dict_read, ground_state, file_q)

        else:

            with open(file_comp, 'r') as fp:
                solutions_input = json.load(fp)

            solutions = [sol["vars"] for sol in solutions_input]
            print([sol["energy"] for sol in solutions_input])

            Q = Analyze_qubo(dict_read)
            results = analyze_outputs_gates(Q, input4qubo, solutions, lp_sol, p)

            with open(file_h, 'wb') as fp:
                pickle.dump(results, fp)

            file_pass = f"{file_h}time_hists.pdf"
            file_obj = f"{file_h}obj.pdf"
            
            plot_gate_gates(q_pars, input4qubo, p, file_pass, file_obj, replace_pair)
