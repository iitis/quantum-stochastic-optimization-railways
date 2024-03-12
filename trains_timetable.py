

class Input_timetable():
    """ store railway parameters """
    def __init__(self):
        self.stay = 1
        self.headways = 2
        self.preparation_t = 3
        self.circ = {}
        self.timetable = {}
        self.objective_stations = []
        self.delays = {}
        self.file = ""
        self.notrains = 0


    # real live problems plus PS - CS and back


    def instance_delay_string(self):
        k = self.delays.keys()
        s1 = ''.join(map(str, k))
        v = self.delays.values()
        s2 = ''.join(map(str, v))
        return f"delays_{s1}_{s2}".replace("__", "_no")

    def qubo_real_12t(self, d):
        """
        12 trains

        8 trains from real live timetable
        added 2 pairs PS - CS - PS  number (11, 13, 12, 14)

        https://www.mta.maryland.gov/schedule/lightrail?origin=7640&destination=7646&direction=0&trip=3447009&schedule_date=12%2F06%2F2023&show_all=yes
        
        starts from 8 a.m.  0 -> 8:00  arr a minute before dep

        """
        self.circ = {(11,14): "CS", (12,13): "PS"}
        self.timetable = {"PS":{11:14, 12:40, 13:44, 14:58}, "MR":{1:12, 11:17, 3:22, 5:32, 7:42, 13:47, 0:20, 2:35, 12:37,  4:50, 14:55, 6:60},
                          "CS":{1:27, 11:32, 3:37, 5:47, 7:57, 13:62, 0:5, 2:20, 12:22, 4:35, 14:40, 6:45}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/12trains/qubo_12t_{s_del}"
        self.notrains = 12


    def qubo_real_11t(self, d):
        """
        11 trains 
        
        7 trains from real live timetable
        added 2 pairs PS - CS - PS  number (11, 13, 12, 14)

        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS", (12,13): "PS"}
        self.timetable = {"PS":{11:14, 12:40, 13:44, 14:58}, "MR":{1:12, 11:17, 3:22, 5:32, 7:42, 13:47, 2:35, 12:37,  4:50, 14:55, 6:60},
                          "CS":{1:27, 11:32, 3:37, 5:47, 7:57, 13:62, 2:20, 12:22, 4:35, 14:40, 6:45}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/11trains/qubo_11t_{s_del}"
        self.notrains = 11

    def qubo_real_10t(self, d):
        """
        10 trains 
        
        6 trains from real live timetable
        added 2 pairs PS - CS - PS  number (11, 13, 12, 14)

        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS", (12,13): "PS"}
        self.timetable = {"PS":{11:14, 12:40, 13:44, 14:58}, "MR":{1:12, 11:17, 3:22, 5:32, 7:42, 13:47, 2:35, 12:37, 4:50, 14:55},
                          "CS":{1:27, 11:32, 3:37, 5:47, 7:57, 13:62, 2:20, 12:22, 4:35, 14:40}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/10trains/qubo_10t_{s_del}"
        self.notrains = 10

    def qubo_real_8t(self, d):
        """
        8 trains

        6 trains from real live timetable
        added 1 pair PS - CS - PS

        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS"}
        self.timetable = {"PS":{11:14, 14:58}, "MR":{1:12, 11:17, 3:22, 5:32, 2:35, 4:50, 14:55, 6:60},
                          "CS":{1:27, 11:32, 3:37, 5:47, 2:20, 4:35, 14:40, 6:45}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/8trains/qubo_8t_{s_del}"
        self.notrains = 8


    def qubo_real_6t(self, d):
        """
        6 trains

        5 trains from real live timetable
        added 1 pair PS - CS - PS
        
        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS"}
        self.timetable = {"PS":{11:14, 14:58}, "MR":{1:12, 11:17, 3:22, 4:50, 14:55, 6:60},
                          "CS":{1:27, 11:32, 3:37, 4:35, 14:40, 6:45}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/6trains/qubo_6t_{s_del}"
        self.notrains = 6



    def qubo_real_4t(self, d):
        """
        4 trains

        3 trains from real live timetable
        added 1 pair PS - CS - PS
        
        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(11,14): "CS"}
        self.timetable = {"PS":{11:14, 14:58}, "MR":{1:12, 11:17, 4:50, 14:55},
                          "CS":{1:27, 11:32, 4:35, 14:40}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/4trains/qubo_4t_{s_del}"
        self.notrains = 4


    def qubo_real_2t(self, d):
        """
        2 trains 1 pair PS - CS - PS
        
        starts from 8 a.m.  0 -> 8:00

        """
        self.circ = {(1,14): "CS"}
        self.timetable = {"PS":{1:14, 14:58}, "MR":{1:17, 14:55},
                          "CS":{1:32, 14:40}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/2trains/qubo_2t_{s_del}"
        self.notrains = 2

    def qubo_real_1t(self, d):
        """
        smallest possible 1 train according to real live timetable
        """
        self.circ = {}
        self.timetable = {"MR":{1:12},
                          "CS":{1:27}
                        }
        self.objective_stations = ["MR", "CS"]
        self.delays = d
        s_del = self.instance_delay_string()
        self.file = f"QUBOs/LR_timetable/1train/qubo_1t_{s_del}"
        self.notrains = 1




class Comp_parameters():
    """ stores parameters of QUBO and computaiton """
    def __init__(self):
        self.M = 50
        self.num_all_runs = 25_000

        self.num_reads = 500
        assert self.num_all_runs % self.num_reads == 0

        self.ppair = 2.0
        self.psum = 4.0
        self.dmax = 6

        self.method = "sim"
        # for simulated annelaing
        self.beta_range = (0.001, 50)
        self.num_sweeps = 500
        # for real annealing
        self.annealing_time = 1000
        self.solver = "Advantage_system6.3"
        self.token = ""
        assert self.annealing_time * self.num_reads < 1_000_000

        self.compute = False
        self.analyze = False
        self.softern_pass = False
        self.delta = 0
