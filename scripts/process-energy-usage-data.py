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

# set figure size
plt.figure(figsize=(10, 7))
plt.barh(labels, df['mAh'].to_list(), color=hex_codes)
plt.xlabel('median current draw for one whole iteration (mAh)')
plt.ylabel('configuration')
plt.title('Median current draw of different configurations')
plt.tight_layout()
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

plt.figure(figsize=(10, 7))

plt.barh(labels, mAhs[1:], color=hex_codes[1:5])
plt.xlabel('percentage of current draw compared to base configuration')
plt.ylabel('configuration')
plt.title('Percentage of current draw of different configurations')
plt.tight_layout()
plt.savefig('../charts/percentage-current-draw-each-configuration.pdf', format='pdf')
plt.savefig('../charts/percentage-current-draw-each-configuration.png', dpi=300)

plt.show()


#%%


indices = [i for i in range(128)]


# NO INTERLEAVE
# 0, 1, 2, 3, 4, 5, 6, 7,   | 8, 9, 10, 11, 12, 13, 14, 15
# 16, 17, 18, 19, 20, 21,   | 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
# 32, 33, 34, 35, 36, 37,   | 38, 39, 40, 41, 42, 43, 44, 45, 46, 47
# 48, 49, 50, 51, 52, 53,   | 54, 55, 56, 57, 58, 59, 60, 61, 62, 63
# 64, 65, 66, 67, 68, 69,   | 70, 71, 72, 73, 74, 75, 76, 77, 78, 79
# 80, 81, 82, 83, 84, 85,   | 86, 87, 88, 89, 90, 91, 92, 93, 94, 95
# 96, 97, 98, 99, 100, 101, | 102, 103, 104, 105, 106, 107, 108, 109, 110, 111
# 112, 113, 114, 115, 116,  | 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127


# WITH INTERLEAVE
# 0, 8, 16, 24, 32, 40, 48, 56,  | 64, 72, 80, 88, 96, 104, 112, 120
# 1, 9, 17, 25, 33, 41, 49, 57,  | 65, 73, 81, 89, 97, 105, 113, 121
# 2, 10, 18, 26, 34, 42, 50, 58, | 66, 74, 82, 90, 98, 106, 114, 122
# 3, 11, 19, 27, 35, 43, 51, 59, | 67, 75, 83, 91, 99, 107, 115, 123
# 4, 12, 20, 28, 36, 44, 52, 60, | 68, 76, 84, 92, 100, 108, 116, 124
# 5, 13, 21, 29, 37, 45, 53, 61, | 69, 77, 85, 93, 101, 109, 117, 125
# 6, 14, 22, 30, 38, 46, 54, 62, | 70, 78, 86, 94, 102, 110, 118, 126
# 7, 15, 23, 31, 39, 47, 55, 63, | 71, 79, 87, 95, 103, 111, 119, 127








# interleave the indices
indices_interleaved = [indices[i] for i in range(0, len(indices), 2)] + [indices[i] for i in range(1, len(indices), 2)]


