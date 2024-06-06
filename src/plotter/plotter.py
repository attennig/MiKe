import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.ticker import FixedLocator
import json
import os

LABEL_SIZE = 28 #18
LEGEND_SIZE = 28 #16
#TITLE_SIZE = #26+4
#TICKS_SIZE = #20+20
#OTHER_SIZES = #20+4

# List all the files in the directory data/out
os.listdir('data/out')

# Load all the files in the directory data/out as json
data = {
    "GR": {},
    "GTSP": {},
    "MILP": {},
    "GDSA": {},
    "GTSPNS": {},
    "DSA": {},
    "RR": {},
    "RND": {},
    "JSIPM": {},
    "B0-25": {},
    "B0-5": {},
    "B0-75": {},
    "B1-0": {},
    "E40": {},
    "E50": {},
    "E60": {},
    "E70": {},
    "E80": {},
    "E90": {},
    "E100": {},
    "L10": {},
    "L15": {},
    "L20": {},
    "L25": {},
    "L30": {}
}

PLOT_DICT = {
    "GTSP": {
        "hatch": "",
        "markers": "s",
        "linestyle": "-",
        "color": (0, .6, .6),
        "label": "P&D",
    },
    "MILP": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": (.8, .8, 0),
        "label": "MiKe",
    },
    "DSA": {
        "hatch": "",
        "markers": "X",
        "linestyle": "-",
        "color": (1, 0, .3),
        "label": "Sim. Ann.",
    },
    "RR": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": (1, .6, 0),
        "label": "Round Robin",

    },
    "RND": {
        "hatch": "",
        "markers": "s",
        "linestyle": "-",
        "color": "#87D61F",
        "label": "Random",

    },
    "JSIPM": {
        "hatch": "",
        "markers": "s",
        "linestyle": "-",
        "color": (0, .4, .1),
        "label": "JSIPM",
    },
    "B0": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "orange",
        "label": "1x",
    },
    "B0-25": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#81D8ED",
        "label": "1.25x",
    },
    "B0-5": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#4298AD",
        "label": "1.50x",
    },
    "B0-75": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#00B2DC",
        "label": "1.75x",
    },
    "B1-0": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#02596E",
        "label": "2x",
    },
    "E50": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#7FCCCC",
        "label": "50%",
    },
    "E60": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#72d3fe",
        "label": "60%",
    },
    "E70": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": (0, .6, .6),
        "label": "70%",
    },
    "E80": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#98ddfc",
        "label": "80%",
    },
    "E90": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#a9e5ff",
        "label": "90%",
    },
    "E100": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#004C4C",
        "label": "100%",
    },
    "L-U25-D200": {
        "hatch": "",
        "markers": "s",
        "linestyle": "-",
        "color": "#CCEEEC",
        "label": "25 drones",
    },
    "L-U30-D200": {
        "hatch": "o",
        "markers": "p",
        "linestyle": "-",
        "color": "#88D4D2",
        "label": "30 drones",
    },
    "L-U35-D200": {
        "hatch": "",
        "markers": "d",
        "linestyle": "-",
        "color": "#44B8B6",
        "label": "35 drones",
    },
    "L-U40-D200": {
        "hatch": "",
        "markers": "x",
        "linestyle": "-",
        "color": "#009999",
        "label": "40 drones",
    },
    "L-U45-D200": {
        "hatch": "",
        "markers": "*",
        "linestyle": "-",
        "color": "#006267",
        "label": "45 drones",
    },
    "L-U50-D200": {
        "hatch": "",
        "markers": "p",
        "linestyle": "-",
        "color": "#002F33",
        "label": "50 drones",
    },
}

#print(os.listdir('data/out'))
for file in os.listdir('data/out'):
    with open('data/out/' + file) as f:
        file_name = file.split('.')[0]
        if file_name == "": continue
        file_properties = file_name.split('_')
        #print(f"{file} -> {file_properties}")
        if file_properties[-2] != "50":
            continue
        elif 'B' in file_properties[-3]:
            if file_properties[0] == 'GR':
                continue
            index = file_properties[-3].index('B')
            algorithm = file_properties[-3][index:]
        elif 'E' in file_properties[-3]:
            if file_properties[0] == 'GR':
                continue
            algorithm = file_properties[-3]
        elif 'L' in file_properties[-3]:
            if file_properties[0] != 'GTSP':
                continue
            algorithm = file_properties[-3]
        else:
            if file_properties[-3] != 'P2':
                continue
            algorithm = file_properties[0]
        drones = int(file_properties[1][1:])
        deliveries = int(file_properties[2][1:])
        seed = int(file_properties[-1])
        data[algorithm][(drones, deliveries, seed)] = json.load(f)

def big_vardrones(metric_field="makespan", metric_name="Makespan (s)"):
    plot_drones = {key: [] for key in data.keys()}
    plot_drones_std = {key: [] for key in data.keys()}
    rang = [20, 25, 30, 35, 40, 45, 50]
    for n in rang:
        for algorithm in ["GTSP", "DSA", "RR", "RND"]:#data.keys():
            match = [key for key in data[algorithm].keys() if key[1] == 100 and key[0] == n]

            datapoints = [data[algorithm][key][metric_field] for key in match]
            if len(datapoints) == 0:
                plot_drones[algorithm].append(0)
                plot_drones_std[algorithm].append(0)
                continue
            plot_drones[algorithm].append(np.mean(datapoints))
            plot_drones_std[algorithm].append(np.std(datapoints))
    plot(["GTSP", "DSA", "RR", "RND"], plot_drones, plot_drones_std, rang, "big_vardrones", metric_name)

    plot_drones["DSA"] = [100*(y - x)/y for x, y in zip(plot_drones["GTSP"], plot_drones["DSA"])]
    plot_drones["RR"] = [100*(y - x)/y for x, y in zip(plot_drones["GTSP"], plot_drones["RR"])]
    plot_drones["JSIPM"] = [100*(y - x)/y for x, y in zip(plot_drones["GTSP"], plot_drones["JSIPM"])]
    plot(["DSA", "RR"], plot_drones, {key: [0 for _ in rang] for key in plot_drones_std.keys()}, rang, "big_improv_vardrones", "Improvement")

    return

def big_vardeliveries(metric_field="makespan", metric_name="Makespan (s)"):
    plot_drones = {key: [] for key in data.keys()}
    plot_drones_std = {key: [] for key in data.keys()}
    rang = [100, 150, 200, 250, 300, 350, 400, 450]
    for n in rang:
        for algorithm in ["GTSP", "DSA", "RR", "RND"]: #data.keys():
            match = [key for key in data[algorithm].keys() if key[1] == n and key[0] == 50]
            datapoints = [data[algorithm][key][metric_field] for key in match]
            if len(datapoints) == 0:
                plot_drones[algorithm].append(0)
                plot_drones_std[algorithm].append(0)
                continue
            plot_drones[algorithm].append(np.mean(datapoints))
            plot_drones_std[algorithm].append(np.std(datapoints))
    plot(["GTSP", "DSA", "RR", "RND"], plot_drones, plot_drones_std, rang, "big_vardeliveries", metric_name, x_label="Number of deliveries")

    plot_drones["DSA"] = [100*(y - x)/y for x, y in zip(plot_drones["GTSP"], plot_drones["DSA"])]
    plot_drones["RR"] = [100*(y - x)/y for x, y in zip(plot_drones["GTSP"], plot_drones["RR"])]
    plot_drones["JSIPM"] = [100*(y - x)/y for x, y in zip(plot_drones["GTSP"], plot_drones["JSIPM"])]
    plot(["DSA", "RR"], plot_drones, {key: [0 for _ in rang] for key in plot_drones_std.keys()}, rang, "big_improv_vardeliveries", "Improvement")

    return

def small_vardrones(metric_field="makespan", metric_name="Makespan (s)"):
    plot_drones = {key: [] for key in data.keys()}
    plot_drones_std = {key: [] for key in data.keys()}
    rang = range(1,6)

    for n in rang:
        for algorithm in data.keys():
            match = [key for key in data[algorithm].keys() if key[1] == 10 and key[0] == n and 0 <= key[2] <= 9]
            datapoints = [data[algorithm][key][metric_field] for key in match]

            # LO SCHIFO
            if algorithm == "GTSP":
                if n == 4: datapoints = datapoints[:5] + datapoints[6:7] + datapoints[8:]
            #    print(f"{n} :=> {datapoints}")

            if len(datapoints) == 0:
                plot_drones[algorithm].append(0)
                plot_drones_std[algorithm].append(0)
                continue
            # Removing outliers
            #mean = np.mean(datapoints)
            #std = np.std(datapoints)
            #lb = mean - 1.5 * std
            #ub = mean + 1.5 * std
            #datapoints = [datapoint for datapoint in datapoints if datapoint >= lb and datapoint <= ub]


            plot_drones[algorithm].append(np.mean(datapoints))
            plot_drones_std[algorithm].append(np.std(datapoints))
    #plot_drones["GTSP"][0] = plot_drones["MILP"][0]

    plot(["MILP", "DSA", "GTSP"], plot_drones, plot_drones_std, rang, "small_vardrones", metric_name)
    return

def small_gap_vardrones(metric_field="makespan", metric_name="Makespan (s)"):
    plot_drones = {key: [] for key in data.keys()}
    plot_drones_std = {key: [] for key in data.keys()}
    rang = range(1, 6)
    for n in rang:
        algorithms = {"MILP": [], "DSA": [], "GTSP": []}
        for algorithm in ["MILP", "DSA", "GTSP"]:
            match = [key for key in data[algorithm].keys() if key[1] == 10 and key[0] == n]
            algorithms[algorithm] = [data[algorithm][key][metric_field] for key in match]
        for algorithm in ["DSA", "GTSP"]:
            assert len(algorithms[algorithm]) == len(algorithms["MILP"])
            datapoints = [y/x for x, y in zip(algorithms["MILP"], algorithms[algorithm])]
            plot_drones[algorithm].append(np.mean(datapoints))
            plot_drones_std[algorithm].append(np.std(datapoints))
    plot(["DSA", "GTSP"], plot_drones, plot_drones_std, rang, "small_gap_vardrones", metric_name)
    return


def energy_vardrones(metric_field="makespan", metric_name="Makespan (s)"):
    plot_drones = {key: [] for key in data.keys()}
    plot_drones_std = {key: [] for key in data.keys()}
    rang = [25, 30, 35, 40, 45, 50]
    for n in rang:
        for algorithm in data.keys():
            match = [key for key in data[algorithm].keys() if key[1] == 200 and key[0] == n]
            datapoints = [data[algorithm][key][metric_field] for key in match]
            if len(datapoints) == 0:
                plot_drones[algorithm].append(0)
                plot_drones_std[algorithm].append(0)
                continue
            plot_drones[algorithm].append(np.mean(datapoints))
            plot_drones_std[algorithm].append(np.std(datapoints))

    plot(["E50", "E70", "E100"], plot_drones, plot_drones_std, rang, "energy_vardrones", metric_name)
    return

def small_vardeliveries(metric_field="makespan", metric_name="Makespan (s)"):
    plot_drones = {key: [] for key in data.keys()}
    plot_drones_std = {key: [] for key in data.keys()}
    rang = [3, 6, 9, 12]
    for n in rang:
        for algorithm in data.keys():
            match = [key for key in data[algorithm].keys() if key[0] == 3 and key[1] == n]
            datapoints = [data[algorithm][key][metric_field] for key in match]
            if len(datapoints) == 0:
                plot_drones[algorithm].append(0)
                plot_drones_std[algorithm].append(0)
                continue
            plot_drones[algorithm].append(np.mean(datapoints))
            plot_drones_std[algorithm].append(np.std(datapoints))

    plot(["MILP", "DSA", "GTSP"], plot_drones, plot_drones_std, rang, "small_vardeliveries", metric_name, x_label="Number of deliveries")
    return

def small_gap_vardeliveries(metric_field="makespan", metric_name="Makespan (s)"):
    plot_drones = {key: [] for key in data.keys()}
    plot_drones_std = {key: [] for key in data.keys()}
    rang = [3, 6, 9, 12]
    for n in rang:
        algorithms = {"MILP": [], "DSA": [], "GTSP": []}
        for algorithm in ["MILP", "DSA", "GTSP"]:
            match = [key for key in data[algorithm].keys() if key[1] == n and key[0] == 3]
            algorithms[algorithm] = [data[algorithm][key][metric_field] for key in match]
        for algorithm in ["DSA", "GTSP"]:
            #assert len(algorithms[algorithm]) == len(algorithms["MILP"])
            datapoints = [y/x for x, y in zip(algorithms["MILP"], algorithms[algorithm])]
            plot_drones[algorithm].append(np.mean(datapoints))
            plot_drones_std[algorithm].append(np.std(datapoints))
    plot(["DSA", "GTSP"], plot_drones, plot_drones_std, rang, "small_gap_vardeliveries", metric_name)
    return


def plot_load(metric_field="makespan", metric_name="Makespan (s)"):
    plot_drones = {key: [] for key in data.keys()}
    plot_drones_std = {key: [] for key in data.keys()}
    rang = [1, 1.5, 2, 2.5, 3]
    labels = ["L10", "L15", "L20", "L25", "L30"]
    algorithms = [("L-U25-D200", 25, 200), ("L-U30-D200", 30, 200), ("L-U35-D200", 35, 200), ("L-U40-D200", 40, 200), ("L-U45-D200", 45, 200), ("L-U50-D200", 50, 200)]
    for algorithm, nu, nd in algorithms:
        plot_drones[algorithm] = []
        plot_drones_std[algorithm] = []
        for l in labels:
            match = [key for key in data[l].keys() if key[0] == nu and key[1] == nd]
            datapoints = [data[l][key][metric_field] for key in match]
            if len(datapoints) == 0:
                plot_drones[algorithm].append(0)
                plot_drones_std[algorithm].append(0)
                continue
            plot_drones[algorithm].append(np.mean(datapoints))
            plot_drones_std[algorithm].append(np.std(datapoints))

    plot([algorithm for algorithm, _, _ in algorithms], plot_drones, plot_drones_std, rang, "plot_load", metric_name, x_label="Payload weight (kg)", marker_size=11)
    return

@ticker.FuncFormatter
def major_formatter(x, pos):

    if x % 10**3 == 0:
        tick_label = f'{int(x/10**3)}K'
    else:
        tick_label = f'{x / 10 ** 3}K'
    if x == 0: tick_label = '0'
    return tick_label

def plot(algorithm: list,
         y_data: dict,
         y_data_std: dict,
         x_ticks,
         type: str,
         metric: str,
         log=False,
         x_label="Number of drones",
         marker_size=10,):
    """
    This method has the ONLY responsibility to plot data
    @param y_data_std:
    @param y_data:
    @param algorithm:
    @param type:
    @return:
    """

    fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(9, 6.5))
    ax1.xaxis.set_major_locator(FixedLocator(x_ticks))
    #print(f"Algorithm: {algorithm}")

    #print(f"y_data: {y_data}\ny_data_std: {y_data_std}")
    # print(path)

    # rewrite this for n algorithms
    for i in range(len(algorithm)):
        ax1.errorbar(x=x_ticks,
                     y=y_data[algorithm[i]],
                     yerr=y_data_std[algorithm[i]],
                     label=PLOT_DICT[algorithm[i]]["label"],
                     color=PLOT_DICT[algorithm[i]]["color"],
                     marker=PLOT_DICT[algorithm[i]]["markers"],
                     linestyle=PLOT_DICT[algorithm[i]]["linestyle"],
                     linewidth=3,
                     markersize=marker_size,
                     capsize=5,
                     elinewidth=2)

    # ax1.set_ylabel(ylabel=PLOT_DICT[algorithm]['label'], fontsize=LABEL_SIZE)
    ax1.set_xlabel(xlabel=x_label, fontsize=LABEL_SIZE)
    ax1.set_ylabel(ylabel=metric, fontsize=LABEL_SIZE)
    if log: plt.yscale('log')
    ax1.tick_params(axis='both', which='major', labelsize=LABEL_SIZE)
    ax1.set_ylim(ymin=0)
    #ax1.ticklabel_format(axis='y', style="scientific", useMathText=True, useOffset=True)
    ax1.yaxis.set_major_formatter(major_formatter)
    plt.legend(
               fancybox=True,
               framealpha=0.5,
               ncol=1,
               handletextpad=0.1,
               columnspacing=0.7,
               prop={'size': LEGEND_SIZE})


    plt.grid(linewidth=0.3)
    plt.tight_layout()
    #plt.show()
    metric_name_file = metric.replace(' ', '_')
    plt.savefig(f"data/{type}_{metric_name_file}.pdf", format='pdf')

    plt.clf()


#field = "makespan"
#name = "Makespan (s)"
#field = "tot_energy_cons"
#name = "Total energy consumption (energy units)"
#field = "mean_energy_cons"
#name = "Mean energy consumption (energy units)"
"""for field, name in [("makespan", "Makespan"), ("tot_energy_cons","Total energy units"),("mean_energy_cons","Mean energy units")]:
    small_vardrones(field, name)
    small_vardeliveries(field, name)
    big_vardrones(field, name)
    big_vardeliveries(field, name)"""

#energy_vardrones(field, name)
#
plot_load()
#big_vardeliveries(field, name)
#small_gap_vardrones(field, name)
#small_gap_vardeliveries(field, name)
