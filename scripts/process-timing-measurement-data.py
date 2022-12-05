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

CLOCK_SECOND = 128

timing_values = [
    0.02 / 128, # seconds
    0.02 / 128, # seconds
    0.007, # seconds
    0.02 / 128, # seconds
    0.007, # seconds
]

# set figure size
plt.figure(figsize=(10, 7))
plt.barh(labels, timing_values, color=hex_codes)
plt.title('Average time per payload')
plt.xlabel('Time (s)')
plt.ylabel('Configuration')

plt.tight_layout()
plt.savefig('../charts/average-time-per-payload.png', dpi=300)
plt.savefig('../charts/average-time-per-payload.pdf', format='pdf')
plt.show()


#%%

labels = [
    'Hardware AES',
    'Software AES',
    'Hardware AES, 8/4 Hamming',
    'Software AES, 8/4 Hamming',
]

timing_values0 = timing_values[0]

timing_values = [(timing_value - timing_values0) / timing_values0 * 100.0 for timing_value in timing_values]

plt.figure(figsize=(10, 7))

plt.barh(labels, timing_values[1:], color=hex_codes[1:5])
plt.title('Average time per payload compared to base configuration')
plt.xlabel('percentage of time compared to base configuration')
plt.ylabel('configuration')


plt.tight_layout()
# plt.savefig('../charts/percentage-current-draw-each-configuration.pdf', format='pdf')
# plt.savefig('../charts/percentage-current-draw-each-configuration.png', dpi=300)

plt.show()