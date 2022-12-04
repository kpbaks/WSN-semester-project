#%%
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import random

#%%
import matplotlib.style
print(matplotlib.style.available)
# pick random style
# matplotlib.style.use(random.choice(matplotlib.style.available))
# matplotlib.style.use('seaborn-whitegrid')
# plt.style.use('fast')
plt.style.use('ggplot')
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

total = 0

# for bytes_used in [
#     bytes_flashed['base'],
#     bytes_flashed['with_software_aes'] - bytes_flashed['base'],
#     bytes_flashed['with_hardware_aes'] - bytes_flashed['base'], 
#     bytes_flashed['with_software_aes_and_8_4_hamming'] - bytes_flashed['with_software_aes'],
#     bytes_flashed['with_hardware_aes_and_8_4_hamming'] - bytes_flashed['with_hardware_aes']
#     ]:
#     xs = np.zeros(5)
#     xs[0] = bytes_used
#     plt.bar(bytes_flashed.keys())


# set figure size
plt.figure(figsize=(10, 5))
plt.title('Memory footprint of the AES implementation')

labels = ['software AES', 'hardware AES']

width = 0.8

print('width', width)
plt.barh(labels, [base, base], label='base')
plt.barh(labels, [bytes_used_for_software_aes, bytes_used_for_hardware_aes], left=[base, base], label='AES')



plt.barh(labels, [bytes_used_for_8_4_hamming, bytes_used_for_8_4_hamming], left=[base + bytes_used_for_software_aes, base + bytes_used_for_hardware_aes], label='Hamming (8,4)')


# plt.bar(bytes_flashed.keys(),s/ bytes_flashed.values(), align='center', alpha=1)
# plt.bar(bytes_flashed.keys(), [0, by])

# plt.ylim(0, MAX_FLASH_MEMORY + kB)
plt.xlim(0, MAX_FLASH_MEMORY + kB)


# draw vertical line at 48 KB
plt.axvline(x=MAX_FLASH_MEMORY, color='red', linestyle='--', label='max flash memory')

# write the max flash memory value on the vertical line
plt.text(MAX_FLASH_MEMORY - kB * 3, 0, '48 kB', color='red', fontsize=12)

plt.xlabel('bytes flashed')

# plt.xticks(rotation=45, fontsize=10, fontweight='bold')
xticks = [x * kB for x in [0, 10, 20, 30, 40, 50]]
plt.xticks(xticks, [f'{int(x/kB)} kB' for x in xticks])
# plt.legend(loc='upper left')
# plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
# plt.legend(fancybox=False, shadow=True, ncol=5)
plt.legend()
plt.tight_layout()
plt.show()

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


# complementary pastel colors
ptgreen = '#b3e2cd'
ptblue = '#a6cee3'
ptred = '#fdcdac'
ptpurple = '#cbd5e8'
ptorange = '#f4cae4'
ptbrown = '#e6f5c9'
ptgray = '#f5f5f5'

ax0.pie(sizes, explode=explode, autopct='%1.1f%%', shadow=True, startangle=90)
ax0.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax0.legend(labels)


labels = ['base', 'hardware AES', '8/4 Hamming', 'free']

sizes = [
    bytes_flashed['base'],
    bytes_flashed['with_hardware_aes'] - bytes_flashed['base'],
    bytes_flashed['with_hardware_aes_and_8_4_hamming'] - bytes_flashed['with_hardware_aes'],
    MAX_FLASH_MEMORY - bytes_flashed['with_hardware_aes_and_8_4_hamming']
]

ax1.pie(sizes, explode=explode,  autopct='%1.1f%%', shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax1.legend(labels)

fig.suptitle('Flash Memory Usage (48 kB)', fontsize=16)

plt.tight_layout()
plt.show()
