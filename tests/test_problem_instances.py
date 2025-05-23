""" tests trains timetable instances """
import pickle
from trains_timetable import Input_timetable, Comp_parameters
from QTrains import prepare_qubo


def test_1train_qubo():
    """tests one train instance"""
    q_par = Comp_parameters()
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.dmax = 2
    trains_input = Input_timetable()
    delays = {}
    trains_input.qubo_real_1t(delays)

    file_input = "tests/files/1train_QUBO.json"

    prepare_qubo(trains_input, q_par, file_input)

    with open(file_input, 'rb') as fp:
        created_qubo = pickle.load(fp)

    file_input = "tests/files/sols4comparison/qubo_1t_delays_no_2_2.0_4.0.json"

    with open(file_input, 'rb') as fp:
        compare_qubo = pickle.load(fp)

    for k, value in created_qubo.items():
        assert value == compare_qubo[k]


def test_2train_qubo():
    """ test 2 trains instance """
    q_par = Comp_parameters()
    q_par.ppair = 2.0
    q_par.psum = 4.0
    trains_input = Input_timetable()
    delays = {}
    trains_input.qubo_real_2t(delays)

    file_input = "tests/files/2train_QUBO.json"

    q_par.dmax = 2

    prepare_qubo(trains_input, q_par, file_input)

    with open(file_input, 'rb') as fp:
        created_qubo = pickle.load(fp)

    file_input = "tests/files/sols4comparison/qubo_2t_delays_no_2_2.0_4.0.json"

    with open(file_input, 'rb') as fp:
        compare_qubo = pickle.load(fp)

    for k, value in created_qubo.items():
        assert value == compare_qubo[k]


def test_4train_qubo():
    """ test 4 trains instance """
    q_par = Comp_parameters()
    q_par.ppair = 2.0
    q_par.psum = 4.0
    q_par.dmax = 2
    trains_input = Input_timetable()
    delays = {}
    trains_input.qubo_real_4t(delays)

    file_input = "tests/files/4train_QUBO.json"

    prepare_qubo(trains_input, q_par, file_input)

    with open(file_input, 'rb') as fp:
        created_qubo = pickle.load(fp)

    file_input = "tests/files/sols4comparison/qubo_4t_delays_no_2_2.0_4.0.json"

    with open(file_input, 'rb') as fp:
        compare_qubo = pickle.load(fp)

    for k, value in created_qubo.items():
        assert value == compare_qubo[k]
