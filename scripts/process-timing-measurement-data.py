#%%
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import os
import sys
import random
import glob
from pathlib import Path
import matplotlib.font_manager


plt.style.use('ggplot')

# choose a great looking serif font
plt.rcParams['font.family'] = 'sans-serif'

figsize = (10, 7)


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
hex_codes = [to_hex(c) for c in rgba_colors[0::48]]

labels = [
    'No AES\nNo Hamming',
    'Hardware AES',
    'Software AES',
    'Hardware AES\n8/4 Hamming',
    'Software AES\n8/4 Hamming',
]

RTIMER_SECOND = 32768

# I forgot to measure the time it takes to sample the light sensor
# so I subtracted the time it takes to sample the light sensor from the total time
# I got in no-aes-no-hamming configuration.
# I assume that the time it takes to sample the light sensor is the same for all configurations
TICKS_TO_SAMPLE_4_LIGHT_MEASUREMENTS = 95 - 43 # 52

timing_values = (np.array([
    43,
    57,
    66,
    157,
    166,
]) + TICKS_TO_SAMPLE_4_LIGHT_MEASUREMENTS) / RTIMER_SECOND

# # see our google sheet for the values
# timing_values = [
#     43 / RTIMER_SECOND, # seconds
#     57 / RTIMER_SECOND, # seconds
#     66 / RTIMER_SECOND, # seconds
#     157 / RTIMER_SECOND, # seconds
#     166 / RTIMER_SECOND, # seconds
# ]

# set figure size
plt.figure(figsize=figsize)
title: str = 'Average time per payload generation and transmission'
plt.title(title, fontsize=20, pad=10, fontweight='normal')
plt.bar(labels, timing_values, color=hex_codes)

plt.xlabel('configuration', color='black', fontsize=18)


# show the y-axis in milliseconds
plt.ylabel('time (ms)', color='black', fontsize=18)
# Convert the tick labels to milliseconds
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x*1000:.3f}"))

# for each bar, show the value in the middle of bar of it in milliseconds
# for i, v in enumerate(timing_values):
#     half_up = v / 2
#     plt.text(i, half_up, f"{v*1000:.3f} ms", ha='center', fontsize=12)

# Show each measurement as a tick on the y-axis
plt.yticks(timing_values, fontsize=12)
plt.xticks(fontsize=13)

# Create a list of colors for the y-axis ticks
plt.tick_params(axis='y', which='major', colors='black')
plt.tick_params(axis='x', which='major', colors='black')

plt.tight_layout()
plt.savefig('../charts/average-time-per-payload-generation-and-transmission.png', dpi=300, bbox_inches='tight')
plt.savefig('../charts/average-time-per-payload-generation-and-transmission.pdf', format='pdf', bbox_inches='tight')
plt.show()


#%%

timing_value_of_base_configuration: float = timing_values[0]
timing_values_as_percentage_of_base_configuration = [
    (t - timing_value_of_base_configuration) / timing_value_of_base_configuration * 100.0
    for t in timing_values[1:]
]

print(timing_values_as_percentage_of_base_configuration)

plt.figure(figsize=figsize)

plt.bar(labels[1:], timing_values_as_percentage_of_base_configuration, color=hex_codes[1:5])

title: str = 'Percentage of time compared to base configuration'

plt.title(title, fontsize=20, pad=10, fontweight='normal')

plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:.2f} %"))


ylabel: str = 'percentage of time'
plt.ylabel(ylabel, color='black', fontsize=18)
plt.xlabel('configuration', color='black', fontsize=18)
plt.tick_params(axis='y', which='major', colors='black')
plt.tick_params(axis='x', which='major', colors='black')

plt.yticks(timing_values_as_percentage_of_base_configuration, fontsize=12)
plt.xticks(fontsize=13)




plt.tight_layout()
plt.savefig('../charts/percentage-of-time-compared-to-base-configuration.png', dpi=300)
plt.savefig('../charts/percentage-of-time-compared-to-base-configuration.pdf', format='pdf')
plt.show()