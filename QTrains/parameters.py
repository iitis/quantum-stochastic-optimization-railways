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
    return trains_station

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
    """class of railway traffic parameters tied to timetable and technical specifics
    IMPORTANT in timetable odd train numbers are going one way and even train numbers 
    are going the other ways
    
    - self.headways - int minimal headway between trians,
    - self.stay - int (minimal) stay on the station
    - self.preparation_t -in minimal preparation time when "going around"
    - self.dmax - maximal delay
    - self timetable of trains arriving stations in the dict of dict form:
        e.g. {s1 : {j1:t1, j2:t2...}, s2 : {j1:t1, j2:t2...}, ... } 
    - self.trains_paths:: stores dict where trains are kays and seqience (vector of stations) are values
            e.g. {j1 : [s1, s2, s3] ...}
    - self pass_time - passing time between stations in the dict form {"s1_s1": t12, "s2_s3": t23, ...}
    - self: circulation - dict {(j,jp): s, ... }  where j ands at s and then starts back as jp
    """

    def __init__(self, timetable, stay = 1, headways = 2, preparation_t = 3, dmax = 2, circulation = None):
        self.headways = headways
        self.stay = stay
        self.preparation_t = preparation_t
        self.dmax = dmax
        self.timetable = timetable
        self.trains_paths = self.make_trains_paths()
        self.pass_time = self.compute_passing_times()
        if circulation:
            self.circulation = circulation
        else:
            self.circulation = {}


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
                assert pass_time[f"{s}_{sp}"] == passing_time, f"train {j}, {s} => {sp}"
            elif f"{sp}_{s}" in pass_time:
                assert pass_time[f"{sp}_{s}"] == passing_time, f"train {j}, {sp} => {s}"
            else:
                pass_time[f"{s}_{sp}"] = passing_time
        return pass_time



class Railway_input():
    """ class of railway input computed from Parameters class and initial conditions
    such as initial delays 
    - fields as in Parameters
    additional field is initial condition dependent:
    - self.tvar_range - dict: {s: {j: (tmin, tmax), j1: (t1min, t1max), ...}, s1: ...}
    - self.bojective_station - vec of stations on which objective is computed

            """
    def __init__(self, parameters, objective_stations, delays):
        # form parameters
        self.headways = parameters.headways
        self.stay = parameters.stay
        self.preparation_t = parameters.preparation_t
        self.dmax = parameters.dmax
        self.timetable = parameters.timetable
        self.trains_paths = parameters.trains_paths
        self.pass_time = parameters.pass_time
        self.circulation = parameters.circulation

        # additinal fields
        self.objective_stations = objective_stations
        self.add_tvar_ranges(parameters, delays)


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
                b = a+parameters.dmax
                assert a <= b
                var_range[s][j] = (a,b)
        self.tvar_range = var_range
