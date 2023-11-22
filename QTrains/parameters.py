"module for dispatching parameters and conditions"
from difflib import SequenceMatcher
import itertools, copy


def match_lists(a, b):
    "helper"
    match = SequenceMatcher(None, a, b).find_longest_match()
    return a[match.a:match.a + match.size], match.size

def common_s_same_dir(trains_paths, j, jp):
    "helper teritns the series of stations two trains follow going in the same direction"
    stations, size = match_lists(trains_paths[j], trains_paths[jp])
    if size > 1:
        return stations
    return []

def pairs_same_direction(trains_paths):
    "list of tripples, in each pair of trains going the same direction and station they pass"
    trains_station = []
    for [j,jp] in itertools.product(trains_paths, trains_paths):
        if jp > j:
            stations = common_s_same_dir(trains_paths, j,jp)
            for s in stations:
                trains_station.append((j, jp, s))
    return  trains_station

def station_pairs(trains_paths):
    "list of tripples, in each train and the pair of two subsequent stations"
    trains_stations = []
    for j in trains_paths:
        stations = trains_paths[j]
        l = len(stations)
        for k in range(l-1):
            s = stations[k]
            sp = stations[k+1]
            trains_stations.append([j,s,sp])
    return trains_stations

class Parameters:
    def __init__(self, timetable, stay = 1, headways = 2, preparation_t = 3, dmax = 2):
        self.headways = headways
        self.stay = stay
        self.preparation_t = preparation_t
        self.dmax = dmax
        self.timetable = timetable
        self.make_passing_times()

    
    def make_passing_times(self):
        pass_time = {}
        stations = [el for el in self.timetable]
        for i in range(len(stations) - 1):
            a = stations[i]
            b = stations[i+1]
            for j in self.timetable[a]:
                if j in self.timetable[b]:
                    passing_time = abs(self.timetable[b][j] - self.timetable[a][j]) - self.stay
                    if f"{a}_{b}" in pass_time:
                        assert pass_time[f"{a}_{b}"] == passing_time
                    elif "{a}_{b}" in pass_time:
                        assert pass_time[f"{b}_{a}"] == passing_time
                    else:
                     pass_time[f"{a}_{b}"] = passing_time
       
        self.pass_time = pass_time



class Railway_input:
    def __init__(self, parameters, penalty_at, delays):
        self.timetable = parameters.timetable
        self.penalty_at = penalty_at
        self.trains_paths = self.make_trains_paths()
        self.add_initial_delays(parameters, delays)
        self.circulation = {}


    def make_trains_paths(self):
        trains_paths = {}
        for s in self.timetable:
            for j in self.timetable[s].keys():
                if j not in trains_paths:
                    trains_paths[j] = [s]
                else:
                    if (j % 2) == 1:
                        trains_paths[j].append(s)
                    else:
                        trains_paths[j].insert(0, s)
                    # TODO sorting is necessary here
        return trains_paths
    

    def add_initial_delays(self, parameters, delays):
        var_range = copy.deepcopy(self.timetable) 
        for s in var_range:
            for j in var_range[s]:
                a = var_range[s][j]
                if j in delays:
                    if s in self.trains_paths[j]:
                        a = a + delays[j]
                b = var_range[s][j]+parameters.dmax
                assert a <= b
                var_range[s][j] = (a,b)
        self.var_range = var_range





 
