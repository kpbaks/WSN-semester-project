#%%
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path
import matplotlib.font_manager


# plt.style.use('ggplot')

# choose a great looking serif font
plt.rcParams['font.family'] = 'sans-serif'

figsize = (10, 7)


FIGSIZE: tuple[int,int] = (10, 7)

AXIS_LABEL_FONT_SIZE = 18
XAXIS_LABEL_FONT_SIZE = AXIS_LABEL_FONT_SIZE
YAXIS_LABEL_FONT_SIZE = AXIS_LABEL_FONT_SIZE

YTICKS_LABEL_FONT_SIZE = 14
XTICKS_LABEL_FONT_SIZE = 14


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


fix, ax = plt.subplots(figsize=FIGSIZE)

ax.bar(labels, timing_values, color=hex_codes)

title: str = 'Average time per payload generation and transmission'
# ax.set_title(title, fontsize=20, pad=10, fontweight='normal')

ax.set_xlabel('configuration', color='black', fontsize=XAXIS_LABEL_FONT_SIZE, labelpad=10)
ax.set_xticklabels(labels, fontsize=XTICKS_LABEL_FONT_SIZE)
# ax.tick_params(axis='x', which='major', colors='black', fontsize=XTICKS_LABEL_FONT_SIZE)

ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x*1000:.3f}"))
ax.set_yticks(timing_values, fontsize=YTICKS_LABEL_FONT_SIZE)
ax.set_yticklabels([f'{x*1000:.3f}' for x in timing_values], fontsize=YTICKS_LABEL_FONT_SIZE)
xmaxs = [0.05, 0.24, 0.42, 0.61, 0.8]

for x, xmax in zip(ax.get_yticks(), xmaxs):
    # draw a line at starting at the left y-axis, and ending at the start of its bar
    # center_of_bar = x - (x - axis.get_ylim()[0]) / 2
    ax.axhline(x, xmin=0, xmax=xmax, color='black', linewidth=0.8, alpha=0.75, linestyle='--')    

twinx = ax.twinx()
twinx.set_ylim(ax.get_ylim())
twinx.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x*1000:.3f}"))
twinx.set_ylabel('time (ms)', color='black', fontsize=YAXIS_LABEL_FONT_SIZE, labelpad=10)

twinx_xticks = np.arange(0, 8, 1)
twinx.set_yticklabels([f'{x:.1f}' for x in twinx_xticks], fontsize=YTICKS_LABEL_FONT_SIZE)

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

plt.figure(figsize=FIGSIZE)
plt.bar(labels[1:], timing_values_as_percentage_of_base_configuration, color=hex_codes[1:5])

title: str = 'Percentage of time compared to base configuration'

# plt.title(title, fontsize=20, pad=10, fontweight='normal')

# plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:.2f} %"))


ylabel: str = 'Percentage of time'
# plt.ylabel(ylabel, color='black', fontsize=YAXIS_LABEL_FONT_SIZE, labelpad=10)
plt.xlabel('Configuration', color='black', fontsize=XAXIS_LABEL_FONT_SIZE, labelpad=10)

# plt.tick_params(axis='y', which='major', colors='black')
# plt.tick_params(axis='x', which='major', colors='black')

plt.yticks(timing_values_as_percentage_of_base_configuration, fontsize=YTICKS_LABEL_FONT_SIZE)
plt.xticks(fontsize=XTICKS_LABEL_FONT_SIZE)

axis = plt.gca()

# axis.yaxis.set_major_formatter('{x:.2f}%')
axis.set_yticks(timing_values_as_percentage_of_base_configuration, fontsize=YTICKS_LABEL_FONT_SIZE)
axis.set_yticklabels([f'{x:.2f}%' for x in timing_values_as_percentage_of_base_configuration], fontsize=YTICKS_LABEL_FONT_SIZE)

xmaxs = [0.05, 0.29, 0.52, 0.76]

for x, xmax in zip(axis.get_yticks(), xmaxs):
    # draw a line at starting at the left y-axis, and ending at the start of its bar
    # center_of_bar = x - (x - axis.get_ylim()[0]) / 2
    axis.axhline(x, xmin=0, xmax=xmax, color='black', linewidth=0.8, alpha=0.75, linestyle='--')    
    # axis.line


twinx = axis.twinx()
# twinx.yaxis.set_major_formatter('{x:.2f}')
twinx.set_ylim(axis.get_ylim())

# 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0
xticks = np.arange(0, 140, 10)
twinx.set_yticks(xticks)
twinx.set_yticklabels([f'{x}%' for x in xticks], fontsize=YTICKS_LABEL_FONT_SIZE)

twinx.set_ylabel(ylabel, color='black', fontsize=YAXIS_LABEL_FONT_SIZE, labelpad=15)




plt.tight_layout()
plt.savefig('../charts/percentage-of-time-compared-to-base-configuration.png', dpi=300)
plt.savefig('../charts/percentage-of-time-compared-to-base-configuration.pdf', format='pdf')
plt.show()
# %%
