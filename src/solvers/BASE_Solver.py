import random
import itertools
import numpy as np
from src.Problem import ProblemInstance
import networkx as nx


class Solver:

    def __init__(self, problem_instance: ProblemInstance):
        self.problem = problem_instance

    def solve(self):
        pass

    def delta(self, x, y, payload=False):
        if payload:
            return self.problem.DELTA_P[(x, y)]
        else:
            return self.problem.DELTA[(x, y)]

    def tau(self, p: dict, q: dict):
        # Time of performing p after q
        x = p['src']
        y = p['dst']
        # s = q['src']
        z = q['dst']
        return self.delta(z, x) + self.problem.delta_l + self.delta(x, y, True) + self.problem.delta_u

    def schedule(self, trips):
        schedule = {u['id']: [] for u in self.problem.U}
        costs = {}

        for u in self.problem.U:
            for i, trip in trips.items():
                if trip:
                    costs[(u['id'], i)] = self.problem.completion_time(u, trip)

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

    def build_delivery_graph(self, deliveries=None, home=None):

        # 1) Build a graph with deliveries as nodes
        delivery_graph = self.build_directed_delivery_graph(deliveries, home=home)

        # 2) Create undirected graph for the TSP
        delivery_graph = self.build_undirected_graph(delivery_graph)

        # 3) Make the graph metric
        delivery_graph = self.build_metric_graph(delivery_graph)

        '''
        if deliveries is None:
            deliveries = self.problem.P
        if M is None:
            if home is None:
                M = sum([self.delta(p['dst'], q['src']) + 1000 for p in deliveries for q in deliveries if p != q])
            else:
                M = sum([self.delta(p['dst'], q['src']) + 1000 for p in deliveries for q in deliveries if p != q]) + \
                    sum([self.delta(home, p['src']) + 1000 for p in deliveries])
        G = nx.Graph()
        n = len(self.problem.P)
        G.add_nodes_from([p['id'] for p in deliveries])
        G.add_nodes_from([p['id'] + n for p in deliveries])
        G.add_node(0)
        if home is not None:
            G.add_node(-1)
            G.add_edge(0, -1, weight=M)
        for p in deliveries:
            G.add_edge(p['id'], p['id'] + n, weight=M)
            if home is None:
                G.add_edge(p['id'], 0, weight=0)
                G.add_edge(p['id'] + n, 0, weight=0)
            else:
                G.add_edge(0, p['id'], weight=self.delta(home, p['src']) + 1000 + M)
                G.add_edge(-1, p['id'], weight=M ** 2)
                G.add_edge(0, p['id'] + n, weight=M ** 2)
                G.add_edge(p['id'] + n, -1, weight=1000 + M)
                G.add_edge(p['id'], -1, weight=M ** 2)
                G.add_edge(p['id'] + n, 0, weight=M ** 2)
        for p in deliveries:
            for q in deliveries:
                if p != q:
                    G.add_edge(p['id'] + n, q['id'], weight=self.delta(p['dst'], q['src']) + 1000 + M)
                    G.add_edge(p['id'], q['id'], weight=M ** 2)
                    G.add_edge(p['id'] + n, q['id'] + n, weight=M ** 2)
        return G
        '''
        return delivery_graph

    def build_undirected_graph(self, G):
        assert type(G) == nx.DiGraph
        H = nx.Graph()
        n = len(self.problem.P) + 1
        H.add_nodes_from(G.nodes)
        H.add_nodes_from([node + n for node in G.nodes])
        for u in G.nodes:
            H.add_edge(u, u + n, weight=0)
        M = max([G[u][v]['weight'] for u in G.nodes for v in G.nodes if u != v])
        for u in G.nodes:
            for v in G.nodes:
                if u != v:
                    H.add_edge(u + n, v, weight=G[u][v]['weight'] + M)
                    H.add_edge(u, v, weight=M * 2)
                    H.add_edge(u + n, v + n, weight=M * 2)
        return H

    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.approximation.traveling_salesman.greedy_tsp.html#networkx.algorithms.approximation.traveling_salesman.greedy_tsp
    def build_metric_graph(self, G):
        assert type(G) == nx.Graph
        h = max([G[u][v]['weight'] for u in G.nodes for v in G.nodes if u != v])
        for u in G.nodes:
            for v in G.nodes:
                if u != v:
                    G[u][v]['weight'] = h + G[u][v]['weight']
        return G

    def build_directed_delivery_graph(self, deliveries, home=None):
        G = nx.DiGraph()
        G.add_nodes_from([p['id'] for p in deliveries])
        G.add_node(0)
        for p in deliveries:
            G.add_edge(p['id'], 0, weight=0)
            if home is None:
                G.add_edge(0, p['id'], weight=0)
            else:
                G.add_edge(0, p['id'], weight=self.delta(home, p['src']) + self.delta(p['src'], p['dst'], True))
        for p in deliveries:
            for q in deliveries:
                if p != q:
                    G.add_edge(p['id'], q['id'],
                               weight=self.delta(p['dst'], q['src']) + self.delta(q['src'], q['dst'], True))
        assert len(G.nodes) == len(deliveries) + 1
        assert len(G.edges) == len(G.nodes) ** 2 - len(G.nodes)
        # ogni nodo in una clique diretta di n nodi ha n-1 archi entranti e n-1 archi uscenti
        # allora |E| = n * (n-1) =  n**2 - n
        return G

    def repeated_assignment_heuristic(self, G: nx.DiGraph):
        T = set()
        V = set()
        D = nx.adjacency_matrix(G).todense()
        k = 2
        while k != 0:
            # P = self.rah_assign(D) # A list of lists of nodes
            P = [[0, 1], [2]]
            for p in P:
                v = random.sample(p, 1)
                V.add(v)
                T.update([(u, v) for u in p if u != v])

        pass

    def atsp(self, G, home=None):
        G = self.build_directed_delivery_graph(G, home=home)
        n = len(G.nodes) - 1
        D = np.matrix(np.zeros((n + 1, n + 1)))
        P = list(G.nodes)
        for i, u in enumerate(P):
            for j, v in enumerate(P):
                if u != v:
                    D[i, j] = G[u][v]['weight']
        assert home is not None
        best_time = np.inf
        best_path = None
        counter = 0
        center = P.index(0)
        for p in itertools.permutations(np.array([i for i, u in enumerate(P) if u != 0])):
            flag = 0
            counter += 1
            time = 0
            for i in range(len(p) - 1):
                time += D[p[i], p[i + 1]]
                if time > best_time:
                    flag = 1
                    break
            if flag == 1:
                continue
            time += D[center, p[0]]
            if time < best_time:
                best_time = time
                best_path = p
        # start_index = best_path.index(center)
        # best_path = best_path[start_index + 1:] + best_path[:start_index]
        print(f"Brute force: {counter} permutations")
        best_path = [P[i] for i in best_path]
        print(f"Best path: {best_path}")
        return [[delivery for delivery in self.problem.P if delivery['id'] == best_path[i]][0] for i in
                range(len(best_path))]

    def schedule_clusters(self, clusters):
        schedule = {u['id']: [] for u in self.problem.U}
        trips = {}
        costs = {}

        for i, cluster in clusters.items():
            for u in self.problem.U:
                trips[(u['id'], i)] = self.atsp(self.build_delivery_graph(cluster, home=u['home']))
                costs[(u['id'], i)] = self.problem.completion_time(u, trips[(u['id'], i)])

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

            schedule[u] = trips[(u, i)]
            print(f"Drone {u} assigned to cluster {i} with completion time {cost}.")
            completion_times.append(cost)

        return schedule, max(completion_times)

    def cluster_lengths(self, clusters):
        costs = {}
        for i, cluster in clusters.items():
            costs[i] = np.sum(
                [self.delta(p['src'], p['dst']) + self.problem.delta_l + self.problem.delta_u for p in cluster])
            print(f"Cluster {i} has {len(clusters[i])} elements and cost {costs[i]}")
        return costs

    def schedule_clusters_inorder(self, clusters):
        schedule = {u['id']: [] for u in self.problem.U}
        trips = {}
        costs = {}

        processing_times = {}
        for i, cluster in clusters.items():
            processing_times[i] = np.sum([self.delta(p['src'], p['dst'], True) for p in cluster])
        order = list(sorted(processing_times, key=processing_times.get, reverse=True))

        completion_times = []
        drones = {u['id']: u for u in self.problem.U}
        while len(order) > 0:
            i = order.pop(0)

            # Compute the costs for all drones
            for u_id, u in drones.items():
                if len(clusters[i]) < 2:
                    if len(clusters[i]) == 0:
                        trips[u_id] = [clusters[i]]
                    else:
                        trips[u_id] = [clusters[i][0]]
                else:
                    trips[u_id] = self.atsp(clusters[i], home=u['home'])
                costs[u_id] = self.problem.completion_time(u, trips[u_id])

            # Select the trip with minimal cost
            min_u = min(costs.keys(), key=costs.get)
            cost = costs[min_u]
            trip = trips[min_u]

            costs = {}
            trips = {}

            schedule[min_u] = trip
            print(f"Drone {min_u} assigned to cluster {i} with completion time {cost}.")
            completion_times.append(cost)
            drones.pop(min_u)

        return schedule, max(completion_times), True
