""" reads json file with QUBOs - 4 trains """
import pickle

# add file name
file_q = 'qubo_4t_delays_124_525_2_20.0_40.0.json'


with open(file_q, 'rb') as fp:
    dict_read = pickle.load(fp)


print( dict_read  )
