"module for dispatching parameters and conditions"
from difflib import SequenceMatcher
import itertools
import copy


def match_lists(a, b):
    "helper"
    match = SequenceMatcher(None, a, b).find_longest_match()
    return a[match.a:match.a + match.size], match.size

def common_s_same_dir(trains_paths, j, jp):
    "helper returns the list of series of stations two trains follow going in the same direction"
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
    "class of railway traffic parameters tied to timetable and technical specifics"
    def __init__(self, timetable, stay = 1, headways = 2, preparation_t = 3, dmax = 2):
        self.headways = headways
        self.stay = stay
        self.preparation_t = preparation_t
        self.dmax = dmax
        self.timetable = timetable
        self.trains_paths = self.make_trains_paths()
        self.compute_passing_times()


    def make_trains_paths(self):
        """ return dict of trains and keys and array of subsequent stations"""
        trains_paths = {}
        for s in self.timetable:
            for j in self.timetable[s].keys():
                if j not in trains_paths:
                    trains_paths[j] = [s]
                elif (j % 2) == 1:
                    trains_paths[j].append(s)
                else:
                    trains_paths[j].insert(0, s)
        return trains_paths


    def compute_passing_times(self):
        "compute and add passing time parameter given timetable"
        pass_time = {}
        for (j,s,sp) in station_pairs(self.trains_paths):

            passing_time = abs(self.timetable[sp][j] - self.timetable[s][j]) - self.stay
            if f"{s}_{sp}" in pass_time:
                assert pass_time[f"{s}_{sp}"] == passing_time
            elif f"{sp}_{s}" in pass_time:
                assert pass_time[f"{sp}_{s}"] == passing_time
            else:
                pass_time[f"{s}_{sp}"] = passing_time
        self.pass_time = pass_time



class Railway_input():
    """ class of railway input computed from Parameters class and initial conditions
    such as initial delays """
    def __init__(self, parameters, objective_stations, delays):
        self.headways = parameters.headways
        self.stay = parameters.stay
        self.preparation_t = parameters.preparation_t
        self.dmax = parameters.dmax
        self.timetable = parameters.timetable
        self.trains_paths = parameters.trains_paths
        self.pass_time = parameters.pass_time
        self.objective_stations = objective_stations
        self.add_tvar_ranges(parameters, delays)
        self.circulation = {}


    def add_tvar_ranges(self, parameters, delays):
        """ add the field of ranges of tvar in the form of dict of dict 
            stations -> trains -> rnge tuple """
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
        self.tvar_range = var_range
