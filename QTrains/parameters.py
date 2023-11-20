from difflib import SequenceMatcher
import itertools


def match_lists(a, b):
    match = SequenceMatcher(None, a, b).find_longest_match()
    return a[match.a:match.a + match.size], match.size

def common_s_same_dir(trains_paths, j, jp):
    stations, size = match_lists(trains_paths[j], trains_paths[jp])
    if size > 1:
        return stations
    return []

def pairs_same_direction(trains_paths):
    trains_station = []
    for [j,jp] in itertools.product(trains_paths, trains_paths):
        if jp > j:
            stations = common_s_same_dir(trains_paths, j,jp)
            for s in stations:
                trains_station.append((j, jp, s))
    return  trains_station

def station_pairs(trains_paths):
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
    def __init__(self):
        self.headways = 0
        self.stay = 0
        self.pass_time = {}


