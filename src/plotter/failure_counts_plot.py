import pandas as pd
import matplotlib.pyplot as plt


LABEL_SIZE = 28 #18
LEGEND_SIZE = 28 #16

in_filename = f"data/out/alpha/failure_counts.csv"
df = pd.read_csv(in_filename)
df["successful"] = df["deliveries"] - df["failures"]
#ax = df.groupby("error_rate")["successful"].mean().plot()




fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(9, 6.5))

for n_drones in [20, 25, 30, 35]:
    df_n = df[df["drones"] == n_drones]
    grouped_by_rate = df_n.groupby("error_rate")
    ax.errorbar(
        x=list(grouped_by_rate.groups.keys()),
        y=list(grouped_by_rate.successful.mean()),
        yerr=list(grouped_by_rate.successful.std()),
        label=f"{n_drones} drones",
        color=(n_drones/50, 0, 0),
        marker="o"
    )

ax.set_xlabel(xlabel="alpha max variance", fontsize=LABEL_SIZE)
ax.set_ylabel(ylabel="No. of successful deliveries", fontsize=LABEL_SIZE)

plt.grid(linewidth=0.3)
plt.tight_layout()
plt.legend(
               fancybox=True,
               framealpha=0.5,
               ncol=1,
               handletextpad=0.1,
               columnspacing=0.7,
               prop={'size': LEGEND_SIZE})
plt.show()