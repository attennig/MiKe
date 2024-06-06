import argparse
import random
from math import floor, radians, cos, sin, sqrt
import json

parser = argparse.ArgumentParser(description='Generate instances for Drone Delivery problem.')
parser.add_argument('-n', type=int, help='Number of stations')
parser.add_argument('-s', type=int, help='Seed')
parser.add_argument('-p', type=str, help='Parameter file code')
parser.add_argument('-beta', type=float, help='Station increase factor', default=0)
parser.add_argument('-batt', type=bool, help='Battery case', default=False)

args = parser.parse_args()

AoI_size = 60000

random.seed(args.s)


def load_parameters():
    with open(f"data/parameters/parameters_{args.p}.json", 'r') as f:
        parameters = json.load(f)["parameters"]
    alpha= float(parameters["alpha"])
    B = float(parameters["B"])
    v = float(parameters["drone_speed"])
    max_dist = floor(B * v / alpha)
    min_dist = max_dist * 0.7#0.2
    return min_dist, max_dist


def station_placement(n: int, min_dist: float, max_dist: float):
    stations = []
    j = 1

    x, y = random.uniform(0, AoI_size), random.uniform(0, AoI_size)
    stations.append({'id': j, 'x': x, 'y': y})
    j += 1

    while len(stations) < n:
        add_station(stations, j)
        j += 1
    return stations


def add_station(stations, id):
    while True:
        i = random.randint(0, len(stations) - 1)
        d, theta = random.uniform(min_dist, max_dist), radians(random.uniform(0, 360))
        x = stations[i]['x'] + d * cos(theta)
        y = stations[i]['y'] + d * sin(theta)
        if is_location_available(stations, x, y, min_dist):
            print(f"positioning {id} as neighbour of {i}")
            stations.append({'id': id, 'x': x, 'y': y})
            return


def is_location_available(stations, x: float, y: float, min_dist: float) -> bool:
    if not (0 < x < AoI_size and 0 < y < AoI_size): return False
    for s in stations:
        if sqrt((s['x'] - x) ** 2 + (s['y'] - y) ** 2) <= min_dist:
            print(f"location ({x}, {y}) not available")
            return False
    return True


def drone_placement(stations):
    drones = []
    for u in range(1, len(stations) + 1):
        home_u = random.choice(stations)
        drones.append({'id': u, 'home': home_u['id']})
    return drones


def delivery_generation(stations):
    deliveries = []
    for d in range(1, 10*len(stations) + 1):
        rnd_src, rnd_dst = random.sample(stations, 2)
        deliveries.append({'id': d, 'src': rnd_src['id'], 'dst': rnd_dst['id']})
    return deliveries


if __name__ == "__main__":
    min_dist, max_dist = load_parameters()
    stations = station_placement(args.n, min_dist, max_dist)
    drones = drone_placement(stations)
    deliveries = delivery_generation(stations)
    if args.beta > 0:
        add = int(args.beta * len(stations))
        for i in range(add):
            add_station(stations, len(stations) + 1)
        output = f"data/scenarios/scenario_{args.p}B{str(args.beta).replace('.', '-')}_{args.n}_{args.s}.json"
    else:
        output = f"data/scenarios/scenario_{args.p}_{args.n}_{args.s}.json"

    if args.batt:
        add = int(1 * len(stations))
        for i in range(add):
            add_station(stations, len(stations) + 1)
        for i in range(10):
            random.seed(i)
            drones = drone_placement(stations)
            deliveries = delivery_generation(stations)
            instance = {'stations': stations, 'drones': drones, 'deliveries': deliveries}
            instance = {'entities': instance}
            for b in [10, 15, 20, 25, 30]:
                output = f"data/scenarios/scenario_L{b}_{args.n}_{i}.json"
                with open(output, 'w') as f:
                    json.dump(instance, f)
        exit(0)

    instance = {'stations': stations, 'drones': drones, 'deliveries': deliveries}
    instance = {'entities': instance}
    with open(output, 'w') as f:
        json.dump(instance, f)
