import pandas as pd
import numpy as np
import math
import networkx as nx
import scipy
import copy
import matplotlib.pyplot as plt


class ProblemInstance:
    def __init__(self, instance_file=None, n_drones=None, n_deliveries=None,
                 param_file="data/parameters/parameters_P2.json"):
        self.S = []  # Stations
        self.U = []  # Drones
        self.P = []  # Deliveries
        self.alpha = 0  # Battery discharge rate
        self.alpha_P = 0  # Battery discharge rate when carrying a delivery
        self.B = 0  # Battery capacity
        self.v = 0  # Drone speed
        self.K = 0  # Maximum number of task per drone

        self.delta_u, self.delta_l, self.delta_r = 0, 0, 0  # Unload, Load and Battery swap times

        self.load_instance(instance_file, n_drones, n_deliveries, param_file)

        # Precomputed parameters
        # Maximum distance between two stations
        self.delta_max = self.B / self.alpha
        self.delta_max_P = self.B / self.alpha_P  # When carrying a delivery
        # Shortest paths between all stations, distance between all stations (in terms of time) and energy consumed
        self.LCP, self.DELTA, self.ENERGY = self.precompute_parameters(self.delta_max, self.alpha)
        self.LCP_P, self.DELTA_P, self.ENERGY_P = self.precompute_parameters(self.delta_max_P, self.alpha_P)

    def load_instance(self, entities_file_path: str, n_drones: int, n_deliveries: int, param_file_path):

        # Load parameters
        parameters = pd.read_json(param_file_path)["parameters"]
        self.alpha = float(parameters["alpha"])
        if "alpha_P" in parameters:
            self.alpha_P = float(parameters["alpha_P"])
        else:
            self.alpha_P = self.alpha
        self.B = float(parameters["B"])
        self.v = float(parameters["drone_speed"])
        self.delta_u = float(parameters["delta_u"])
        self.delta_l = float(parameters["delta_l"])
        self.delta_r = float(parameters["delta_r"])
        self.K = n_deliveries

        # Load entities
        entities = pd.read_json(entities_file_path)["entities"]
        self.S = entities["stations"]
        self.U = entities["drones"][:n_drones]
        self.P = entities["deliveries"][:n_deliveries]

    def print_problem_instance(self):
        print(f"Stations: {self.S}")
        print(f"Drones: {self.U}")
        print(f"Deliveries: {self.P}")

    def precompute_parameters(self, delta_max, alpha):
        edges = []
        LCP = {}
        DELTA = {}
        ENERGY = {}

        for x in self.S:
            for y in self.S:
                x_id, y_id = x["id"], y["id"]
                if x_id == y_id:
                    continue
                flight_time = (math.sqrt((x["x"] - y["x"]) ** 2 + (x["y"] - y["y"]) ** 2) / self.v)
                if flight_time > delta_max:
                    continue
                time = flight_time + self.delta_r
                energy_consumption = flight_time * alpha
                edges += [(x_id, y_id, {"weight": time, "energy_consumption": energy_consumption})]
        G = nx.Graph()
        G.add_nodes_from([s['id'] for s in self.S])
        G.add_edges_from(edges)

        assert nx.is_connected(G)
        for j in self.S:
            for k in self.S:
                x, y = j['id'], k['id']
                if x == y:
                    lcp = [x]
                    delta = 0
                else:
                    lcp, delta = self.lcp(G, x, y)
                LCP[(x, y)], DELTA[(x, y)] = lcp, delta
                ENERGY[(x, y)] = 0
                if len(lcp) >= 2:
                    for i in range(len(lcp) - 1):
                        ENERGY[(x, y)] += G.get_edge_data(lcp[i], lcp[i + 1])['energy_consumption']

        return LCP, DELTA, ENERGY

    @staticmethod
    def lcp(G, x, y):
        try:
            path = nx.shortest_path(G, source=x, target=y, weight='weight')
            cost = nx.path_weight(G, path, "weight")
            return path, cost
        except nx.NetworkXNoPath:
            return [], 0

    def completion_time(self, u, trip):
        time = 0
        if (not trip) or (trip == [[]]):
            return 0
        time += self.DELTA[(u['home'], trip[0]['src'])]
        time += self.DELTA_P[(trip[0]['src'], trip[0]['dst'])]
        time += self.delta_l + self.delta_u
        for i in range(1, len(trip)):
            p = trip[i]
            q = trip[i - 1]
            time += self.DELTA[(q['dst'], p['src'])]
            time += self.DELTA_P[(p['src'], p['dst'])]
            time += self.delta_l + self.delta_u
        return time

    def makespan(self, schedule):
        times = []
        for u in self.U:
            times.append(self.completion_time(u, schedule[u['id']]))
        return max(times)

    def debug_schedule(self, schedule):
        for u in self.U:
            print(f"Drone {u['id']} [Home: {u['home']}] -> {schedule[u['id']]}")
            print(f"---> Completion time: {self.completion_time(u, schedule[u['id']])}")