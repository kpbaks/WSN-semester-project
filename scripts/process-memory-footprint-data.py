#%%
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# import seaborn as sns
import os
import sys
import random

plt.style.use('ggplot')

# choose a great looking serif font
plt.rcParams['font.family'] = 'sans-serif'

figsize = (10, 7)


#%%
import matplotlib.style
print(matplotlib.style.available)
# pick random style
# matplotlib.style.use(random.choice(matplotlib.style.available))
# matplotlib.style.use('seaborn-whitegrid')
# plt.style.use('fast')
plt.style.use('ggplot')

# create a gradient palette of colors starting from orange to red
# from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import ListedColormap
from matplotlib.colors import to_hex

# Create a colormap
cmap = plt.get_cmap('viridis')

# Get the list of RGBA values from the colormap
rgba_colors = cmap.colors

# Convert the list of RGBA values to a list of hex codes
hex_codes = [to_hex(c) for c in rgba_colors[48::48]]

# aes_color = '#1f77b4'
# hamming_color = '#ff7f0e'
# base_color = '#2ca02c'

aes_color = hex_codes[2]
hamming_color = hex_codes[1]
base_color = hex_codes[3]


#%%

df = pl.scan_csv("../data/memory-footprint.csv")

#%%

kB = 1000
MAX_FLASH_MEMORY = 48 * kB # 48 KB


df: pl.DataFrame = \
    pl.scan_csv("../data/memory-footprint.csv") \
        .with_column((pl.col('bytes flashed') / MAX_FLASH_MEMORY * 100).alias('percentage flashed')) \
        .collect()

df.head()

#%%

df['configuration'].to_list()

#%%
# create at stacked bar chart with the memory footprint of the different configurations

configurations = df['configuration'].to_list()
bytes_flashed = df['bytes flashed'].to_list()
base_cost_in_bytes = bytes_flashed[0]

#%%

bytes_flashed: dict[str, int] = {
    'base': 18821,
    'with_software_aes': 21556,
    'with_hardware_aes': 20614,
    'with_software_aes_and_8_4_hamming': 21634,
    'with_hardware_aes_and_8_4_hamming': 20692,
}

base = bytes_flashed['base']
bytes_used_for_software_aes: int = bytes_flashed['with_software_aes'] - base
bytes_used_for_hardware_aes: int = bytes_flashed['with_hardware_aes'] - base
bytes_used_for_8_4_hamming: int = bytes_flashed['with_software_aes_and_8_4_hamming'] - bytes_flashed['with_software_aes']

fig, ax = plt.subplots(figsize=(6, 8))
fig.suptitle('Memory footprint of each AES implementation', fontsize=14)

labels = ['Software AES', 'Hardware AES']

# plt.barh(labels, [base, base], label='base')
ax.bar(labels, [base, base], label='base', color=base_color)
# ax.barh(labels, [bytes_used_for_software_aes, bytes_used_for_hardware_aes], left=[base, base], label='AES')
ax.bar(labels, [bytes_used_for_software_aes, bytes_used_for_hardware_aes], bottom=[base, base], label='AES', color=aes_color)

# ax.barh(labels, [bytes_used_for_8_4_hamming, bytes_used_for_8_4_hamming], left=[base + bytes_used_for_software_aes, base + bytes_used_for_hardware_aes], label='Hamming (8,4)')
ax.bar(labels, [bytes_used_for_8_4_hamming, bytes_used_for_8_4_hamming], bottom=[base + bytes_used_for_software_aes, base + bytes_used_for_hardware_aes], label='Hamming (8,4)', color=hamming_color)

# ax.set_gca().xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x/1000:.0f} kB"))
# ax.set_

# ax.set_xticks(labels, color='black', fontsize=12, fontweight='bold')
ax.set_xticklabels(labels, color='black', fontsize=12)

ax.set_ylim(0, MAX_FLASH_MEMORY + 2 * kB)
# draw vertical line at 48 KB
ax.axhline(y=MAX_FLASH_MEMORY, color='red', linestyle='--', label='max flash memory', linewidth=2)


# write the max flash memory value on the vertical line]
# ax.text(0, MAX_FLASH_MEMORY - kB * 3, '48 kB', color='red', fontsize=12)

twin_ax = ax.twinx()
twin_ax.set_ylim(ax.get_ylim())
twin_ax.set_yticks([MAX_FLASH_MEMORY])
twin_ax.set_yticklabels(['48 kB'], color='red', fontsize=12)

yticks = [x * kB for x in [0, 10, 20, 30, 40, 50]]
ax.set_yticks(yticks, [f'{int(x/kB)} kB' for x in yticks],  color='black')

ax.legend(fancybox=False, shadow=False, ncol=5, loc='upper center', bbox_to_anchor=(0.5, -0.05))
fig.tight_layout()

fig.savefig('../charts/memory-footprint.png', dpi=300, bbox_inches='tight')
fig.savefig('../charts/memory-footprint.pdf', bbox_inches='tight', format='pdf')

fig.show()

#%%

fig, (ax0, ax1) = plt.subplots(1, 2, sharex=False, figsize=(10, 5))

labels = ['base', 'software AES', '8/4 Hamming', 'free']

explode = (0, 0.3, 0.1, 0)  # only "explode" the 2nd slice (i.e. '{software, hardware} AES' and '8/4 Hamming')

sizes = [
    bytes_flashed['base'],
    bytes_flashed['with_software_aes'] - bytes_flashed['base'],
    bytes_flashed['with_software_aes_and_8_4_hamming'] - bytes_flashed['with_software_aes'],
    MAX_FLASH_MEMORY - bytes_flashed['with_software_aes_and_8_4_hamming']
]


shadow = False

# complementary pastel colors
ptgreen = '#b3e2cd'
ptblue = '#a6cee3'
ptred = '#fdcdac'
ptpurple = '#cbd5e8'
ptorange = '#f4cae4'
ptbrown = '#e6f5c9'
ptgray = '#f5f5f5'

ax0.pie(sizes, explode=explode, autopct='%1.1f%%', shadow=shadow, startangle=90)
ax0.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax0.legend(labels)


labels = ['base', 'hardware AES', '8/4 Hamming', 'free']

sizes = [
    bytes_flashed['base'],
    bytes_flashed['with_hardware_aes'] - bytes_flashed['base'],
    bytes_flashed['with_hardware_aes_and_8_4_hamming'] - bytes_flashed['with_hardware_aes'],
    MAX_FLASH_MEMORY - bytes_flashed['with_hardware_aes_and_8_4_hamming']
]

ax1.pie(sizes, explode=explode,  autopct='%1.1f%%', shadow=shadow, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax1.legend(labels)

fig.suptitle('Flash Memory Usage (48 kB)', fontsize=16)

plt.tight_layout()
plt.savefig('../charts/pie_chart_of_memory_usage.png', dpi=300)
plt.savefig('../charts/pie_chart_of_memory_usage.pdf', format='pdf')

plt.show()
