#%%
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import glob
from pathlib import Path

# plt.style.use('ggplot')
#%%
csvs: list[str] = glob.glob('../data/*.csv')
csvs_with_energy_usage: list[Path] = [Path(csv) for csv in csvs if 'energest' in csv]

print(csvs_with_energy_usage)

#%%
ITERATIONS_PER_ROW = 10

FIGSIZE: tuple[int,int] = (10, 7)

AXIS_LABEL_FONT_SIZE = 18
XAXIS_LABEL_FONT_SIZE = AXIS_LABEL_FONT_SIZE
YAXIS_LABEL_FONT_SIZE = AXIS_LABEL_FONT_SIZE

YTICKS_LABEL_FONT_SIZE = 14
XTICKS_LABEL_FONT_SIZE = 14

#%%

median_energy_usage: dict[str, float] = {}

for csv in csvs_with_energy_usage:
    total_energy_mJs = pl.scan_csv(csv) \
        .select(pl.col('total_energy_mJ')) \
        .collect() \
        .to_numpy() / ITERATIONS_PER_ROW
        # .select(pl.col('total_charge_mAh')) \

    median = np.mean(total_energy_mJs[1:]) # ignore the first row because it is not a full iteration
    median_energy_usage[csv.name] = median

key: str = 'total_energy_mJ'

df = pl.DataFrame({'configuration': list(median_energy_usage.keys()), key: list(median_energy_usage.values())})
df = df.sort(key)
# df[key]

for x in df[key]:
    print(f'{x:.10f}', end='\n')

#%%
df

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
# hex_codes = [to_hex(c) for c in rgba_colors[100::12]]
hex_codes = [to_hex(c) for c in rgba_colors[0::48]]


#%%


fontsize_yticks = 12

labels = [
    'No AES\nNo Hamming',
    'Hardware AES',
    'Software AES',
    'Hardware AES\n8/4 Hamming',
    'Software AES\n8/4 Hamming',
]
plt.figure(figsize=FIGSIZE)
plt.bar(labels, df[key].to_list(), color=hex_codes)
# plt.title('Average energy usage per payload generation and transmission (mJ)', color='black', fontsize=18,y=1.03)
plt.xlabel('Configuration', color='black', fontsize=XAXIS_LABEL_FONT_SIZE, labelpad=15)
# plt.ylabel('Average energy usage (mJ)', color='black', fontsize=16, labelpad=15)
plt.xticks(color='black', fontsize=XTICKS_LABEL_FONT_SIZE, rotation=0)
plt.yticks(color='black', fontsize=YTICKS_LABEL_FONT_SIZE)

plt.ylim(0.92, 1.0)

axis = plt.gca()
axis.yaxis.set_major_formatter('{x:.2f}')
axis.set_yticks(df[key].to_list(), fontsize=YTICKS_LABEL_FONT_SIZE)
# for each tick in the y-axis, add a horizontal line, to the start of the bar

xmaxs = [0.05, 0.24, 0.42, 0.61, 0.8]

for x, xmax in zip(axis.get_yticks(), xmaxs):
    # draw a line at starting at the left y-axis, and ending at the start of its bar
    # center_of_bar = x - (x - axis.get_ylim()[0]) / 2
    axis.axhline(x, xmin=0, xmax=xmax, color='black', linewidth=0.8, alpha=0.75, linestyle='--')    
    # axis.line
    # axis.axhline(x, color='black', linewidth=0.5, alpha=0.3)

# for tick in axis.gset_yticklabels():

    # tick.set_horizontalalignment('left')
    # tick.set_verticalalignment('center')
    # tick.set_x(-0.1)s




twinx = axis.twinx()
# twinx.yaxis.set_major_formatter('{x:.2f}')
twinx.set_ylim(axis.get_ylim())

# 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 1.0
xticks = np.arange(0.92, 1.01, 0.01)
twinx.set_yticks(xticks)
twinx.set_yticklabels([f'{x:.2f}' for x in xticks], fontsize=YTICKS_LABEL_FONT_SIZE)
twinx.set_ylabel('Average energy usage (mJ)', color='black', fontsize=YAXIS_LABEL_FONT_SIZE, labelpad=15)


plt.tight_layout()
plt.savefig('../charts/average-energy-usage-each-configuration.png', dpi=300)
plt.savefig('../charts/average-energy-usage-each-configuration.pdf', format='pdf')
plt.show()


#%%

mJs = df[key].to_list()

# calculate the percentage of the current draw of each configuration compared to the base configuration
mJs = [(mJ - mJs[0]) / mJs[0] * 100.0 for mJ in mJs]

plt.figure(figsize=FIGSIZE)

plt.bar(labels[1:], mJs[1:], color=hex_codes[1:5])

# plt.title('Percentage of extra energy usage compared to the base configuration (mJ)', color='black', fontsize=18,y=1.02)
plt.xlabel('Configuration', color='black', fontsize=XAXIS_LABEL_FONT_SIZE, labelpad=15)
ylabel: str = 'Percentage (%)'
# plt.ylabel(ylabel, color='black', fontsize=16)
plt.xticks(color='black', fontsize=XTICKS_LABEL_FONT_SIZE, rotation=0)
plt.yticks(color='black', fontsize=YTICKS_LABEL_FONT_SIZE)

axis = plt.gca()

axis.yaxis.set_major_formatter('{x:.2f}%')
axis.set_yticks(mJs[1:], fontsize=YTICKS_LABEL_FONT_SIZE)


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
xticks = np.arange(0, 6, 1)
twinx.set_yticks(xticks)
twinx.set_yticklabels([f'{x}%' for x in xticks], fontsize=YTICKS_LABEL_FONT_SIZE)

twinx.set_ylabel(ylabel, color='black', fontsize=YAXIS_LABEL_FONT_SIZE, labelpad=15)

plt.tight_layout()
plt.savefig('../charts/percentage-energy-usage-configuration.pdf', format='pdf')
plt.savefig('../charts/percentage-energy-usage-configuration.png', dpi=300)
plt.show()



# %%
