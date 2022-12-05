#%%
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import random
import glob
from pathlib import Path

plt.style.use('ggplot')
#%%


csvs: list[str] = glob.glob('../data/*.csv')
csvs_with_energy_usage: list[Path] = [Path(csv) for csv in csvs if 'energest' in csv]

print(csvs_with_energy_usage)

#%%

ITERATIONS_PER_ROW = 10

fig, ax = plt.subplots(figsize=(10, 8))

for csv in csvs_with_energy_usage:
    df = pl.read_csv(csv).slice(1, -1)
    # skip the first row, as it is not measured correctly
    # df = df.drop(0)
    # df.slice(1, -1)
    # find the median of the total_charge_mHa column
    median = df['total_charge_mHa'].median()
    label = csv.stem
    ax.bar(label, median, label=label)

ax.set_ylabel('median total charge [mHa]')
ax.set_xlabel('configuration')
ax.set_title('Median total charge per configuration')
ax.legend()

plt.tight_layout()
plt.show()


