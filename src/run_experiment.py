from src.Problem import ProblemInstance
from src.solvers.MILP import MILP
from src.solvers.Greedy import Greedy
from src.solvers.GreedyTSP import GreedyTSP
from src.solvers.Baseline import Baseline
from time import process_time
import json
import argparse

parser = argparse.ArgumentParser(description='Solve Drone Delivery problem.')

parser.add_argument('-nu', type=int, help='Number of drones')
parser.add_argument('-nd', type=int, help='Number of deliveries')

parser.add_argument('-filename', type=str, help='name of json file storing the input instance')
parser.add_argument('-seed', type=int, help='seed for random number generator')
parser.add_argument('-parameters', type=str, help='parameters for the algorithm')
parser.add_argument('-algorithm', type=str, help='List of algorithms in ["MILP", "GR", "RR", "RND", "GTSP"]')


args = parser.parse_args()


if __name__ == '__main__':

    print(f"Running {args.algorithm} on {args.filename} with {args.nu} drones and {args.nd} deliveries")
    problem = ProblemInstance(f"data/scenarios/{args.filename}", args.nu, args.nd,
                              param_file=f"data/parameters/parameters_{args.parameters}.json")
    print(f"Problem instance loaded. {len(problem.U)} drones and {len(problem.P)} deliveries")
    seed = int(args.filename.split('.')[0].split("_")[-1])
    if args.algorithm == "MILP":
        solver = MILP(problem)
    elif args.algorithm == "GR":
        solver = Greedy(problem)
    elif args.algorithm == "GTSP":
        solver = GreedyTSP(problem, args=args)
    elif args.algorithm in ["RR", "RND", "JSIPM"]:
        solver = Baseline(problem, args.algorithm, seed=seed)
    else:
        raise Exception(f"{args.algorithm} is not a supported algorithm")
    print(f"Running {args.algorithm} solver")
    start = process_time()
    schedule, makespan, approximate = solver.solve()
    stop = process_time()
    process_time_var = stop - start
    print(f"proc time: {process_time_var}")

    print(f"Algorithm's makespan: {makespan}")
    print(f"Computed makespan: {problem.makespan(schedule)}")
    #problem.debug_schedule(schedule)
    solution = {'algorithm': args.algorithm, 'makespan': makespan, 'schedule': schedule, 'approximation': approximate}
    with open(f"data/out/{args.algorithm}_U{args.nu}_D{args.nd}_{args.filename}", 'w') as out:
        json.dump(solution, out)

