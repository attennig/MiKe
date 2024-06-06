from src.solvers.BASE_Solver import Solver
import random
import math

import networkx as nx


class LocalSearch(Solver):
    def __init__(self, problem, metaheuristic: str, init_solution=[], seed=None):
        super().__init__(problem)
        if seed is not None:
            random.seed(seed)
        self.metaheuristic = metaheuristic
        self.init_solution = init_solution
        if self.init_solution == []:
            # generates random solution
            elements = self.problem.P + [0 for _ in range(len(self.problem.U) - 1)]
            random.shuffle(elements)
            self.init_solution = [0] + elements + [0]
            assert self.init_solution.count(0) == len(self.problem.U) + 1




    def solve(self):
        if self.metaheuristic == "simulated_annealing_dorling":
            return self.simulated_annealing_dorling(self.init_solution)

    def simulated_annealing_dorling(self, init_solution):
        #----------- adding single depot as centroid of stations ---------
        depot = {
            'id': -1,
            'x': sum([s['x'] for s in self.problem.S])/len(self.problem.S),
            'y': sum([s['y'] for s in self.problem.S])/len(self.problem.S)
                 } # centroid of stations
        edges = []
        for s in self.problem.S:
            time = (math.sqrt((s["x"] - depot["x"]) ** 2 + (s["y"] - depot["y"]) ** 2) / self.problem.v) + self.problem.delta_r
            edges += [(s["id"], depot["id"], {"weight": time})]

        edges = [e for e in edges if e[2]["weight"] <= self.problem.delta_max + self.problem.delta_r]
        self.problem.edges += edges


        G = nx.Graph()
        G.add_edges_from(self.problem.edges)

        for s in self.problem.S:
            self.problem.LCP[(s['id'], depot['id'])], self.problem.DELTA[(s['id'], depot['id'])] = self.problem.lcp(G, s['id'], depot['id'])
            self.problem.LCP[(depot['id'],s['id'])], self.problem.DELTA[(depot['id'], s['id'])] = self.problem.lcp(G, depot['id'], s['id'])

        #-------------------------------

        temperature = 1
        final_temperature = 0.001
        mu = 0.9
        exchanges_per_iteration = 1000
        solution = init_solution
        schedule, makespan = self.evaluate_solution_dorling(solution, depot)

        while temperature > final_temperature:
            temperature = temperature*mu
            for k in range(exchanges_per_iteration):
                i, j = random.sample(range(1, len(solution)-1), 2)
                r = random.sample([1, 2, 3], 1)
                # i must always be < j
                if i > j:
                    app = j
                    j = i
                    i = app
                assert i < j
                # exchanging rules
                if r == 1:
                    new_solution = solution[:i] + [solution[j]] + solution[i+1:j] + [solution[i]] + solution[j+1:]
                elif r == 2:
                    new_solution = solution[:i] + solution[i+1:j+1] + [solution[i]] + solution[j+1:]
                else:
                    rev = solution[i:j + 1]
                    rev.reverse()
                    new_solution = solution[:i] + rev + solution[j+1:]
                new_schedule, new_makespan = self.evaluate_solution_dorling(new_solution, depot)

                try:
                    criterion = math.exp(-(new_makespan - makespan)/temperature)
                except OverflowError:
                    criterion = math.inf

                if criterion >= random.uniform(0, 1):
                    solution = new_solution
                    schedule = new_schedule
                    makespan = new_makespan

        return schedule, makespan, True

    def evaluate_solution(self, solution):
        trips = {}
        zeros_indices = [i for i in range(len(solution)) if solution[i] == 0]

        for i in range(len(zeros_indices)-1):
            trips[i] = solution[zeros_indices[i]+1:zeros_indices[i+1]]

        return self.schedule(trips)

    def evaluate_solution_dorling(self, solution, depot):
        trips = {}
        zeros_indices = [i for i in range(len(solution)) if solution[i] == 0]

        for i in range(len(zeros_indices)-1):
            trips[i] = solution[zeros_indices[i]+1:zeros_indices[i+1]]

        schedule = {u['id']: [] for u in self.problem.U}
        costs = {}

        for u in self.problem.U:
            for i, trip in trips.items():
                if trip:
                    time = self.problem.DELTA[(u['home'], depot['id'])]
                    time += self.problem.DELTA[(depot['id'], trip[0]['src'])]
                    time += self.problem.DELTA[(trip[0]['src'], trip[0]['dst'])]
                    time += self.problem.delta_l + self.problem.delta_u
                    for j in range(1, len(trip)):
                        p = trip[j]
                        q = trip[j - 1]
                        time += self.problem.DELTA[(q['dst'], p['src'])]
                        time += self.problem.DELTA[(p['src'], p['dst'])]
                        time += self.problem.delta_l + self.problem.delta_u
                    costs[(u['id'], i)] = time

        completion_times = []
        while len(costs) > 0:
            # Select the trip with minimal cost
            u, i = min(costs, key=costs.get)
            cost = costs[(u, i)]

            # Remove all trips incompatible with the selected one from the costs dictionary
            to_remove = []
            for _u, _i in costs.keys():
                if _u == u or _i == i:
                    to_remove.append((_u, _i))
            for key in to_remove:
                del costs[key]

            schedule[u] = trips[i]
            completion_times.append(cost)

        return schedule, max(completion_times)

        #return self.schedule(trips)
