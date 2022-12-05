#%%
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

median_energy_usage: dict[str, float] = {}

for csv in csvs_with_energy_usage:
    total_current_mAhs = pl.scan_csv(csv) \
        .select(pl.col('total_charge_mAh')) \
        .collect() \
        .to_numpy() / ITERATIONS_PER_ROW

    median = np.median(total_current_mAhs)
    median_energy_usage[csv.name] = median


df = pl.DataFrame({'configuration': list(median_energy_usage.keys()), 'mAh': list(median_energy_usage.values())})
df = df.sort('mAh')
df['mAh']

for x in df['mAh']:
    print(f'{x:.10f}', end='\n')

#%%

# create a vertical bar chart with the median energy usage of the different configurations

# create a gradient palette of colors starting from orange to red
# from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import ListedColormap
from matplotlib.colors import to_hex

# Create a colormap
cmap = plt.get_cmap('viridis')

# Get the list of RGBA values from the colormap
rgba_colors = cmap.colors

# Convert the list of RGBA values to a list of hex codes
hex_codes = [to_hex(c) for c in rgba_colors[100::12]]

labels = [
    'No AES, No Hamming',
    'Hardware AES',
    'Software AES',
    'Hardware AES, 8/4 Hamming',
    'Software AES, 8/4 Hamming',
]

plt.barh(labels, df['mAh'].to_list(), color=hex_codes)
plt.xlabel('median current draw for one whole iteration (mAh)')
plt.ylabel('configuration')
plt.title('Median current draw of different configurations')

plt.savefig('../charts/median-current-draw-each-configuration.png', dpi=300)
plt.savefig('../charts/median-current-draw-each-configuration.pdf', format='pdf')
plt.show()


#%%

labels = [
    'Hardware AES',
    'Software AES',
    'Hardware AES, 8/4 Hamming',
    'Software AES, 8/4 Hamming',
]

mAhs = df['mAh'].to_list()

mAhs0 = mAhs[0]

# calculate the percentage of the current draw of each configuration compared to the base configuration
mAhs = [(mAh - mAhs0) / mAhs0 * 100.0 for mAh in mAhs]

plt.barh(labels, mAhs[1:], color=hex_codes)
plt.xlabel('percentage of current draw compared to base configuration')
plt.ylabel('configuration')
plt.title('Percentage of current draw of different configurations')
plt.savefig('../charts/percentage-current-draw-each-configuration.pdf', format='pdf')
plt.savefig('../charts/percentage-current-draw-each-configuration.png', dpi=300)

plt.show()
