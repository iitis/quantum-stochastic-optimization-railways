""" reads json file with QUBOs - 1 train """
import pickle

# add file name
file_q = 'qubo_1t_delays_no_2_2.0_4.0.json'


with open(file_q, 'rb') as fp:
    dict_read = pickle.load(fp)


print( dict_read  )
