from src.solvers.BASE_Solver import Solver
import copy
import random


class Baseline(Solver):

    def __init__(self, problem, method=None, seed=None):
        super().__init__(problem)
        self.method = method
        self.seed = seed

    def random_baseline(self):
        random.seed(self.seed)
        P = copy.deepcopy(self.problem.P)
        random.shuffle(P)
        schedule = {u['id']: [] for u in self.problem.U}
        for p in P:
            u = random.choice(self.problem.U)
            schedule[u['id']] += [p]
        return schedule, self.problem.makespan(schedule), True

    def round_robin(self):
        schedule = {u['id']: [] for u in self.problem.S}
        for i in range(len(self.problem.P)):
            u_id = 1 + i % len(self.problem.U)
            schedule[u_id] += [self.problem.P[i]]
        return schedule, self.problem.makespan(schedule), True

    def solve(self):
        if self.method == "RND":
            return self.random_baseline()
        elif self.method == "RR":
            return self.round_robin()
        else:
            assert self.method == "JSIPM"
            return self.JSIPM_best_approx()
