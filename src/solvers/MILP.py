from src.solvers.BASE_Solver import Solver
import gurobipy as gp
from gurobipy import GRB


# GUROBI OPT PARAMETERS #
OPT_TIME_LIMIT = 24*60  # [minutes]
OPT_MEM_LIMIT = 125  # [GB]


class MILP(Solver):
    def __init__(self, problem):
        super().__init__(problem)

        # Gurobi solver
        env = gp.Env(empty=True)
        env.setParam('TimeLimit', OPT_TIME_LIMIT * 60)
        env.setParam('SoftMemLimit', OPT_MEM_LIMIT)
        env.setParam('Method', 0)  # primal 0, dual 1, barrier 2, concurrent 3
        env.start()
        self.model = gp.Model(env=env)
        self.setup()

    def solve(self):
        self.model.optimize()
        print(f"Gurobi status: {self.model.Status}")

        #self.print_vars()
        return self.extract_solution(self.model.Status)

    def setup(self):

        # Constants
        M = 10 ** 5

        # Variables
        P_ids = [_p["id"] for _p in self.problem.P]
        P_u = [{'id': u['id'] + len(self.problem.P), 'src': u['home'], 'dst': u['home']} for u in self.problem.U] # dummy tasks
        P_u_ids = [_u['id'] + len(self.problem.P) for _u in self.problem.U]
        U_ids = [_u["id"] for _u in self.problem.U]
        t = {}  # t_{u},{p},{x},{y},{k}
        tau = {}  # tau_{u},{k}
        for u in U_ids:
            for k in range(self.problem.K + 1):
                tau[f"{u},{k}"] = self.model.addVar(vtype=GRB.CONTINUOUS, name=f"tau_{u},{k}")
                for p in P_ids + P_u_ids:
                    t[f"{u},{p},{k}"] = self.model.addVar(vtype=GRB.BINARY, name=f"t_{u},{p},{k}")

        maxC = self.model.addVar(vtype=GRB.CONTINUOUS, name=f"maxC")

        # Constraints

        #  Each drone task is related to at most one delivery
        #         \sum_{p \in P + 0}  t^{u,p}(k) \le 1, \quad \forall u \in U, k \in [0, K]
        for u in U_ids:
            for k in range(self.problem.K + 1):
                self.model.addConstr(gp.LinExpr([(1.0, t[f"{u},{p},{k}"]) for p in P_ids + P_u_ids]) <= 1, f"C1_{u},{k}")

        #  Dummy task
        #         t^{u,0}(0) = 1, \quad \forall u \in U
        for u in U_ids:
            self.model.addConstr(t[f"{u},{u + len(self.problem.P)},{0}"] == 1, f"C2_{u}")

        # For each drone tasks must be assigned sequentially
        #         \sum_{p \in P}  t^{u,p}(k) \le \sum_{p \in P}  t^{u,p}(k-1) , \quad \forall u \in U, k \in [1, K]
        for u in U_ids:
            for k in range(1, self.problem.K + 1):
                self.model.addConstr(gp.LinExpr([(1.0, t[f"{u},{p},{k}"]) for p in P_ids + P_u_ids]) <=
                                     gp.LinExpr([(1.0, t[f"{u},{p},{k-1}"]) for p in P_ids + P_u_ids]), f"C3_{u},{k}")

        # Each delivery is assigned to exactly one drone task
        #         \sum_{u \in U} \sum_{k} t^{u,p}(k) = 1, \quad \forall p \in P
        for p in P_ids + P_u_ids:
            self.model.addConstr(
                gp.LinExpr([(1.0, t[f"{u},{p},{k}"]) for u in U_ids for k in range(self.problem.K+1)]) == 1, f"C4_{p}")

        #  Dummy task cannot be assigned to a drone task different from the first one
        #for u in U_ids:
        #    self.model.addConstr(
        #        gp.LinExpr([(1.0, t[f"{u},{0},{k}"]) for k in range(1, self.problem.K+1)]) == 0, f"C4bis_0_{u}")

        #  Task processing time:
        for u in U_ids:
            for k in range(1, self.problem.K+1):
                for p in self.problem.P:
                    for q in self.problem.P + P_u:
                        if p != q:
                            tau_u_p = self.tau(p, q)
                            self.model.addConstr(tau[f"{u},{k}"] >= tau_u_p
                                                 - M * (2 - t[f"{u},{q['id']},{k-1}"] - t[f"{u},{p['id']},{k}"]),
                                                 f"C5_{u},{k},{p['id']},{q['id']}")

        # maxC >= \max_{u \in U} \sum_{k} tau^u(k)
        for u in U_ids:
            self.model.addConstr(maxC >= gp.LinExpr(
                                [(1.0, tau[f"{u},{k}"]) for k in range(1, self.problem.K+1)]
                                ), f"makespan_{u}")

        # Objective function
        self.model.setObjective(maxC, GRB.MINIMIZE)
        self.model.write(f"data/log/modelP2.lp")

    def extract_solution(self, status_code):
        approximate = False
        if status_code in [GRB.TIME_LIMIT, GRB.MEM_LIMIT]:
            approximate = True

        schedule = {}
        for u in self.problem.U:
            T_u = []
            for k in range(1, self.problem.K+1):
                for p in self.problem.P:
                    if self.model.getVarByName(f"t_{u['id']},{p['id']},{k}").x >= 0.5:
                        T_u += [p]
            schedule[u['id']] = T_u
        return schedule, self.model.getVarByName(f"maxC").x, approximate

    def print_vars(self):
        for var in self.model.getVars():
            print(f"{var.VarName} = {var.x}")
