from src.Problem import ProblemInstance


import json
import argparse

parser = argparse.ArgumentParser(description='Extraction of battery consumption.')

parser.add_argument('-nu', type=int, help='Number of drones')
parser.add_argument('-nd', type=int, help='Number of deliveries')

parser.add_argument('-filename', type=str, help='name of json file storing the input instance')
parser.add_argument('-algorithm', type=str, help='List of algorithms in ["MILP", "GR", "CTSP", "DSA", "RR", "RND", "JSIPM"]')


args = parser.parse_args()


if __name__ == '__main__':

    print(f"Extracting energy consumption from results of algorithm {args.algorithm} runned on {args.filename} with {args.nu} drones and {args.nd} deliveries")
    problem = ProblemInstance(f"data/scenarios/{args.filename}", args.nu, args.nd)
    #exit()
    #print(f"Problem instance loaded. {len(problem.U)} drones and {len(problem.P)} deliveries")
    #seed = int(args.filename.split('.')[0].split("_")[-1])

    sol_filename = f"data/out_old/{args.algorithm}_U{args.nu}_D{args.nd}_{args.filename}"
    out_filename = f"data/out/{args.algorithm}_U{args.nu}_D{args.nd}_{args.filename}"


    with open(sol_filename, 'r') as sol_file:
        solution = json.load(sol_file)

    schedule = solution['schedule']
    tot_energy_consumption = 0
    for u in problem.U:
        energy_consumption_u = 0
        #print(f"Drone {str(u['id'])} starts from station {u['home']}")
        prev = u['home']
        #print(f"having assigned deliveries: {schedule[str(u['id'])]}")
        for delivery in schedule[str(u['id'])]:
            #print(f"from {prev} go to {delivery['src']}")
            energy_consumption_u += problem.ENERGY[(prev, delivery['src'])]
            #print(f"and then go to {delivery['dst']}")
            energy_consumption_u += problem.ENERGY[(delivery['src'], delivery['dst'])]
            prev = delivery['dst']

        #print(f"consuming {energy_consumption_u} energy units")
        tot_energy_consumption += energy_consumption_u

    mean_energy_consumption = tot_energy_consumption/len(problem.U)

    print(f"Total energy consumption: {tot_energy_consumption}")
    print(f"Mean energy consumption: {mean_energy_consumption}")

    solution["tot_energy_cons"] = tot_energy_consumption
    solution["mean_energy_cons"] = mean_energy_consumption


    #print(solution)
    with open(out_filename, 'w') as out:
        json.dump(solution, out)

