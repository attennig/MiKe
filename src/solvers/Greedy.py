from src.solvers.BASE_Solver import Solver
import copy
import math


class Greedy(Solver):

    def __int__(self, problem):
        super().__init__(problem)

    def solve(self):
        P = copy.deepcopy(self.problem.P)
        U_ids = [_u["id"] for _u in self.problem.U]

        d = {}
        a = {}
        t = {}
        C = {}
        k = {}

        schedule = {}

        for u in self.problem.U:
            d[f"{u['id']},{0}"] = u['home']
            a[f"{u['id']},{0}"] = u['home']
            C[u['id']] = 0
            k[u['id']] = 0
            schedule[u['id']] = []
        while P:
            min_val = math.inf
            min_p = None
            min_u = None
            for drone in self.problem.U:
                u = drone['id']
                for p in P:
                    if k[u] == 0:
                        last_delivery = {
                            'id': u,
                            'src': drone['home'],
                            'dst': drone['home']
                        }
                    else:
                        last_delivery = schedule[u][-1]
                    tau_u_p = self.tau(p, last_delivery)
                    if min_val > C[u] + tau_u_p:

                        min_u = u
                        min_p = {
                            'id': p['id'],
                            'src': p['src'],
                            'dst': p['dst']
                        }
                        min_val = C[u] + tau_u_p
            k[min_u] = k[min_u] + 1
            C[min_u] = min_val
            d[f"{min_u},{k[min_u]}"] = min_p['src']  # departure
            a[f"{min_u},{k[min_u]}"] = min_p['dst']  # arrival
            t[f"{min_u},{k[min_u]}"] = min_p['id']
            #print(f"{min_p} assigned to {min_u}")
            schedule[min_u] += [min_p]
            P.remove(min_p)
        return schedule, max(C.values()), True
