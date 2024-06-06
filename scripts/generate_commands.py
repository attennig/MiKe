for drones in [50, 45, 40, 35, 30, 25]:
    for payload in [50, 45, 40, 35, 30, 25, 20, 15, 10]:
        for seed in range(10):
            print(f"python3 -m src.run_experiment -nu {drones} -nd 200 -filename scenario_L{payload}_50_{seed}.json -algorithm GTSP")