import argparse
from src.Problem import ProblemInstance
import json
import random
import copy

#python3 -m src.variable_energy_consumption -nu 3 -nd 12 -filename scenario_P2_50_2.json -algorithm GTSP

parser = argparse.ArgumentParser(description='Rerouting considering variable energy consumption rate.')

parser.add_argument('-nu', type=int, help='Number of drones')
parser.add_argument('-nd', type=int, help='Number of deliveries')
parser.add_argument('-seed', type=int, help='Seed')


parser.add_argument('-filename', type=str, help='name of json file storing the input instance')
parser.add_argument('-algorithm', type=str, help='List of algorithms in ["MILP", "GR", "CTSP", "DSA", "RR", "RND", "JSIPM"]')
parser.add_argument('-error_rate', type=float, help='alpha error rate, positive number to increase, negative to decrease')


args = parser.parse_args()

if __name__ == '__main__':
    random.seed(args.seed)
    print(f"Considering the following solution: obtained with algorithm {args.algorithm} runned on {args.filename} with {args.nu} drones and {args.nd} deliveries")
    problem = ProblemInstance(f"data/scenarios/{args.filename}", args.nu, args.nd)
    sol_filename = f"data/out/{args.algorithm}_U{args.nu}_D{args.nd}_{args.filename}"
    out_filename = f"data/out/alpha/{args.error_rate}_U{args.nu}_D{args.nd}_{args.filename}"

    with open(sol_filename, 'r') as sol_file:
        solution = json.load(sol_file)

    schedule = solution['schedule']
    makespan = solution['makespan']
    alpha_init = problem.alpha

    # estrazione rotte da schedule con arrival time per ogni hop
    for u in problem.U:
        curr_time = 0
        schedule_u = schedule[f"{u['id']}"]
        curr_station_id = u['home']
        path = []
        for delivery in schedule_u:
            delivery['to_src'] = copy.deepcopy(problem.LCP[(curr_station_id, delivery['src'])])
            hop_index = -1
            for hop_index in range(len(delivery['to_src'])-1):
                hop = (delivery['to_src'][hop_index], delivery['to_src'][hop_index+1])
                delivery['to_src'][hop_index] = {'station': delivery['to_src'][hop_index], 'arrival_time': curr_time, 'alpha': alpha_init}
                curr_time += problem.DELTA[hop]

            if len(delivery['to_src']) > 0:
                delivery['to_src'][hop_index+1] = {'station': delivery['to_src'][hop_index+1], 'arrival_time': curr_time, 'alpha': alpha_init}


            delivery['to_dst'] = copy.deepcopy(problem.LCP[(delivery['src'], delivery['dst'])])
            hop_index = -1
            for hop_index in range(len(delivery['to_dst'])-1):
                hop = (delivery['to_dst'][hop_index], delivery['to_dst'][hop_index + 1])
                delivery['to_dst'][hop_index] = {'station': delivery['to_dst'][hop_index], 'arrival_time': curr_time, 'alpha': alpha_init}
                curr_time += problem.DELTA[hop]
                # in the first station we load the parcel, thus we need to add delta_l to curr_time before the drone arrives to the second station_
                if hop_index == 0:
                    curr_time += problem.delta_l

            # before arrived at destination we need to unload the parcel
            curr_time += problem.delta_u
            delivery['to_dst'][hop_index+1] = {'station': delivery['to_dst'][hop_index+1], 'arrival_time': curr_time, 'alpha': alpha_init}

            curr_station_id = delivery['dst']

    DATA_OUT_SCHEDULE_INIT = copy.deepcopy(schedule)

    # generazione perturbazioni di alpha
    step = 1000 # seconds
    probability = 0.5
    error_rate = args.error_rate

    snapshot = {}
    for u in problem.U:
        t = 500
        schedule_u = schedule[f"{u['id']}"]
        schedule_time_u = schedule_u[-1]['to_dst'][-1]['arrival_time']
        print(f"for {u['id']} up to {schedule_time_u}")
        snapshot[u['id']] = []
        while t < schedule_time_u:
            dice = random.uniform(0.0,1.0)
            if dice <= probability:
                # variation = random.uniform(-alpha_init*error_rate, alpha_init*error_rate) # mixed
                #if t <= makespan * 0.5:
                variation = random.uniform(0, alpha_init * error_rate) # solo peggiorativo
                #else:
                #    variation = random.uniform(0, -alpha_init * 0.5) # solo migliorativo
                new_alpha = alpha_init + variation
                problem.alpha = new_alpha
                problem.precompute_parameters()
                snapshot[u['id']] += [{"time": t, "alpha": new_alpha, "variation": variation, "DELTA": copy.deepcopy(problem.DELTA), "LCP": copy.deepcopy(problem.LCP)}]
                print(f"time:{t}, alpha:{new_alpha}, {len(problem.edges)}")
            t = t + step


    for u in problem.U:
        print(f"____________________________________\n drone {u['id']}")
        curr_time = 0
        schedule_u = schedule[f"{u['id']}"]
        #last_station = u['home']
        for param in snapshot[u['id']]:
            FOUND = False
            END = False
            print(f"updating for {param['time']}, {param['alpha']}")

            while not FOUND and not END:
                for delivery_idx, delivery in enumerate(schedule_u):
                    if delivery['to_src'][-1]['arrival_time'] >= param['time']:
                        FOUND = True
                        found_delivery_idx = delivery_idx
                        found_delivery = delivery
                        found_piece_of_route = 'to_src'
                        break
                    if delivery['to_dst'][-1]['arrival_time'] >= param['time']:
                        FOUND = True
                        found_delivery_idx = delivery_idx
                        found_delivery = delivery
                        found_piece_of_route = 'to_dst'
                        break
                if not FOUND:
                    END = True
                    break
                for station_idx, station in enumerate(found_delivery[found_piece_of_route]):
                    if station['arrival_time'] >= param['time']:
                        found_station_idx = station_idx
                        found_station = station
                        break
            if not FOUND: break

            new_LCP_found_delivery = {}


            if found_piece_of_route == 'to_src':
                # Recompute path to_src
                new_LCP_found_delivery['to_src'] = schedule_u[found_delivery_idx]['to_src'][:found_station_idx]
                new_LCP_found_delivery['to_src'] += [{'station': found_station['station'],
                                                     'arrival_time': found_station['arrival_time'],
                                                     'alpha': param['alpha'],
                                                     'variation': param['variation']}]

                curr_time = found_station['arrival_time']

                new_LCP = param['LCP'][(found_station['station'], found_delivery['src'])]

                for hop_idx in range(1,len(new_LCP)):
                    hop = (new_LCP[hop_idx-1], new_LCP[hop_idx])
                    curr_time += param['DELTA'][hop]
                    new_LCP_found_delivery['to_src'] += [{'station': new_LCP[hop_idx],
                                                         'arrival_time': curr_time,
                                                         'alpha': param['alpha'],
                                                         'variation': param['variation']}]

                found_station = new_LCP_found_delivery['to_src'][-1]
                #print(found_station)
                found_station_idx = 0

                schedule_u[found_delivery_idx]['to_src'] = copy.deepcopy(new_LCP_found_delivery['to_src'])


            new_LCP = param['LCP'][(found_station['station'], found_delivery['dst'])]

            new_LCP_found_delivery['to_dst'] = schedule_u[found_delivery_idx]['to_dst'][:found_station_idx]
            new_LCP_found_delivery['to_dst'] += [{'station': found_station['station'],
                                                 'arrival_time': found_station['arrival_time'],
                                                 'alpha': param['alpha'],
                                                 'variation': param['variation']}]
            curr_time = found_station['arrival_time']
            for hop_idx in range(1, len(new_LCP)):
                hop = (new_LCP[hop_idx - 1], new_LCP[hop_idx])
                curr_time += param['DELTA'][hop]
                if new_LCP[hop_idx-1] == found_delivery['src']:
                    curr_time += problem.delta_l
                if new_LCP[hop_idx] == found_delivery['dst']:
                    curr_time += problem.delta_u

                new_LCP_found_delivery['to_dst'] += [{'station': new_LCP[hop_idx],
                                                     'arrival_time': curr_time,
                                                     'alpha': param['alpha'],
                                                     'variation': param['variation']}]

            schedule_u[found_delivery_idx]['to_dst'] = copy.deepcopy(new_LCP_found_delivery['to_dst'])

            prev_station = schedule_u[found_delivery_idx]['to_dst'][-1]
            for delivery in schedule_u[found_delivery_idx+1:]:
                # recompute for all successive deliveries

                new_LCP_delivery = {}

                new_LCP = param['LCP'][(prev_station['station'], delivery['src'])]
                new_LCP_delivery['to_src'] = [prev_station]
                curr_time = prev_station['arrival_time']
                for hop_idx in range(1,len(new_LCP)):
                    hop = (new_LCP[hop_idx-1], new_LCP[hop_idx])
                    curr_time += param['DELTA'][hop]
                    new_LCP_delivery['to_src'] += [{'station': new_LCP[hop_idx],
                                                    'arrival_time': curr_time,
                                                    'alpha': param['alpha'],
                                                    'variation': param['variation']}]

                new_LCP = param['LCP'][(delivery['src'], delivery['dst'])]
                new_LCP_delivery['to_dst'] = [new_LCP_delivery['to_src'][-1]]
                for hop_idx in range(1, len(new_LCP)):
                    hop = (new_LCP[hop_idx - 1], new_LCP[hop_idx])
                    curr_time += param['DELTA'][hop]
                    if new_LCP[hop_idx - 1] == delivery['src']:
                        curr_time += problem.delta_l
                    if new_LCP[hop_idx] == delivery['dst']:
                        curr_time += problem.delta_u

                    new_LCP_delivery['to_dst'] += [{'station': new_LCP[hop_idx],
                                                          'arrival_time': curr_time,
                                                          'alpha': param['alpha'],
                                                          'variation': param['variation']}]

                prev_station = new_LCP_delivery['to_dst'][-1]


                delivery['to_src'] = copy.deepcopy(new_LCP_delivery['to_src'])

                delivery['to_dst'] = copy.deepcopy(new_LCP_delivery['to_dst'])


    DATA_OUT_SCHEDULE_RESILIENT = copy.deepcopy(schedule)

    # plotting data
    data = {
        "basic_schedule": DATA_OUT_SCHEDULE_INIT,
        "resilient_schedule": DATA_OUT_SCHEDULE_RESILIENT
    }

    with open(out_filename, 'w') as out:
        json.dump(data, out)
