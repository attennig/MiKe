from src.solvers.BASE_Solver import Solver
from src.solvers.Greedy import Greedy
import json


class GreedyTSP(Solver):
    def __init__(self, problem, args=None):
        super().__init__(problem)
        self.args = args

    def solve(self):
        greedy = Greedy(self.problem)
        clusters, initial_makespan, approximate = greedy.solve()
        if self.args is not None:
            solution = {'algorithm': "GR", 'makespan': initial_makespan, 'schedule': clusters, 'approximation': approximate}
            with open(f"data/out/GR_U{self.args.nu}_D{self.args.nd}_{self.args.filename}", 'w') as out:
                json.dump(solution, out)
        print(f"Greedy solution --- Makespan: {initial_makespan}")
        self.problem.debug_schedule(clusters)
        print("--------------------")
        return self.schedule_clusters_inorder(clusters)
