import matplotlib.pyplot as plt
import json
import os
from matplotlib.ticker import MaxNLocator
import matplotlib.patches as mpatches
import csv

LABEL_SIZE = 28 #18
LEGEND_SIZE = 24 #16
ANNOTATION_SIZE = 20
arrow_width = 0.2
line_width = 0.015
vspace = 0.6


SUCC_EXP = True
SCHED_EXP = False

def plot_arrows(A, file_name_out, H):
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 7))
    #ax.set_xlabel("Time (s)")
    #ax.set_ylabel("Drones (id)")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    for a in A:
        plt.arrow(x=a['x'],
                  y=a['y'],
                  dx=a['dx'],
                  dy=a['dy'],
                  color=a['color'],
                  hatch=a['hatch'],
                  width=a['width'],
                  linestyle=a['linestyle'])
        plt.annotate(a['text'], (a['x'],a['y']-0.08), fontsize=ANNOTATION_SIZE)
        #plt.annotate("X", ((a['x'] + 0.5*a['dx']), a['y']-0.07), fontsize=20, color=(1, 0, .3))

    plt.legend(handles=H, fontsize=LEGEND_SIZE)

    #plt.grid()
    ax.axhline(3, linestyle='--', color=(.5,.5,.5))
    ax.axhline(5, linestyle='--', color=(.5,.5,.5))
    ax.set_xlabel(xlabel="Time (s)", fontsize=LABEL_SIZE)
    ax.tick_params(axis='both', which='major', labelsize=LABEL_SIZE)
    ax.set_yticks([2,4,6],["Drone 1", "Drone 2", "Drone 3"])
    plt.tight_layout()

    plt.savefig(f"data/plot/alpha_{file_name_out}.pdf", format='pdf')




if SUCC_EXP: folder = "data/out/alpha"
if SCHED_EXP: folder = "data/out/alpha_old"
data = {}
keys = []
out_filename = f"data/out/alpha/failure_counts.csv"



for file in os.listdir(folder):
    print(file)
    with open(f"{folder}/" + file) as f:
        file_name = '.'.join(file.split('.')[:-1])
        print(file_name)
        file_properties = file_name.split('_')
        print(file_properties)
        i=0
        error_rate = float(file_properties[i])
        print(error_rate)
        i+=1
        if SCHED_EXP: i+=1
        drones = int(file_properties[i][1:])
        print(drones)
        i+=1
        deliveries = int(file_properties[i][1:])
        print(deliveries)

        seed = int(file_properties[-1])
        print(seed)
        keys += [(error_rate, drones, deliveries, seed)]
        data[(error_rate, drones, deliveries, seed)] = json.load(f)


if SUCC_EXP:
    csvfile = open(out_filename, 'w', newline='')
    fieldnames = ['error_rate', 'drones', 'deliveries', 'seed', 'failures']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

for key in keys:
    print(key)
    drones = key[0]
    deliveries = key[1]
    seed = key[2]
    arrows = []
    lengths = {}



    for drone_id, drone_schedule in data[key]['resilient_schedule'].items():
        for delivery in drone_schedule:

            arrows += [{
                "x": delivery['to_src'][0]['arrival_time'],
                "y": 2*int(drone_id) + vspace,
                "dx": delivery['to_src'][-1]['arrival_time'] - delivery['to_src'][0]['arrival_time'],
                "dy": 0,
                "color": (.8, .8, 0),
                "hatch":"",
                "width": line_width,
                "text": "",
                "linestyle": ":",
                "failed": False
            }]

            arrows += [{
                "x": delivery['to_dst'][0]['arrival_time'],
                "y": 2*int(drone_id) + vspace,
                "dx": delivery['to_dst'][-1]['arrival_time'] - delivery['to_dst'][0]['arrival_time'],
                "dy": 0,
                "color": (.8, .8, 0),
                "hatch":"",
                "width": arrow_width,
                "text": delivery['id'],
                "linestyle": "-",
                "failed": False
            }]
            lengths[delivery['id']] = {}
            lengths[delivery['id']]["pickup"] = delivery['to_src'][-1]['arrival_time'] - delivery['to_src'][0][
                'arrival_time']
            lengths[delivery['id']]["delivery"] = delivery['to_dst'][-1]['arrival_time'] - delivery['to_dst'][0][
                'arrival_time']

    count_failures = 0
    for drone_id, drone_schedule in data[key]['basic_schedule'].items():
        no_fail = {'color': (1, 0, .3)}
        NO_FAIL = True
        for delivery in drone_schedule:
            failed_pick = False
            if lengths[delivery['id']]["pickup"] > delivery['to_src'][-1]['arrival_time'] - delivery['to_src'][0][
                'arrival_time']:
                failed_pick = True
                no_fail = {'color': (.8, .6, .6)}
                NO_FAIL = False


            arrows += [{
                "x": delivery['to_src'][0]['arrival_time'],
                "y": 2*int(drone_id),
                "dx": delivery['to_src'][-1]['arrival_time'] - delivery['to_src'][0]['arrival_time'],
                "dy": 0,
                "color": (0, .6, .6),
                "hatch":"",
                "width": line_width,
                "text": "",
                "linestyle": ":",
                "failed": failed_pick
            }]
            if NO_FAIL:
                arrows += [{
                    "x": delivery['to_src'][0]['arrival_time'],
                    "y": 2 * int(drone_id) - vspace,
                    "dx": delivery['to_src'][-1]['arrival_time'] - delivery['to_src'][0]['arrival_time'],
                    "dy": 0,
                    "color": no_fail['color'],
                    "hatch": "/",
                    "width": line_width,
                    "text": "",
                    "linestyle": ":",
                    "failed": failed_pick
                }]
            failed_del = False
            if lengths[delivery['id']]["delivery"] > delivery['to_dst'][-1]['arrival_time'] - delivery['to_dst'][0][
                'arrival_time']:
                failed_del = True
                no_fail = {'color': (.8, .6, .6)}
                NO_FAIL = False
            arrows += [{
                "x": delivery['to_dst'][0]['arrival_time'],
                "y": 2*int(drone_id),
                "dx": delivery['to_dst'][-1]['arrival_time'] - delivery['to_dst'][0]['arrival_time'],
                "dy": 0,
                "color": (0, .6, .6),
                "hatch":"",
                "width": arrow_width,
                "text": delivery['id'],
                "linestyle": "-",
                "failed": failed_del
            }]
            if NO_FAIL:
                arrows += [{
                    "x": delivery['to_dst'][0]['arrival_time'],
                    "y": 2 * int(drone_id) - vspace,
                    "dx": delivery['to_dst'][-1]['arrival_time'] - delivery['to_dst'][0]['arrival_time'],
                    "dy": 0,
                    "color": no_fail['color'],
                    "hatch": "//",
                    "width": arrow_width,
                    "text": delivery['id'],
                    "linestyle": "-",
                    "failed": failed_del
                }]
            if failed_del or failed_pick:
                count_failures += 1

    if SCHED_EXP:
        legend_handles = [mpatches.Patch(color=(.8, .8, 0), label='resilient'), mpatches.Patch(color=(0, .6, .6), label='base w/o variation'), mpatches.Patch(color=(1, 0, .3), label='base with variation')]
        print(legend_handles)
        plot_arrows(arrows, str(key[1:])+"_new",legend_handles)

    if SUCC_EXP:
        error_rate, drones, deliveries, seed = key
        writer.writerow({
            'error_rate': error_rate,
            'drones': drones,
            'deliveries': deliveries,
            'seed': seed,
            'failures': count_failures
        })


if SUCC_EXP: csvfile.close()
