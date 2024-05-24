""" reads json file with Ising - 6 train """
import pickle

# add file name
file_q = 'ising_6t_delays_no_6_2.0_4.0.pkl'


with open(file_q, 'rb') as fp:
    dict_read = pickle.load(fp)


print( dict_read  )
