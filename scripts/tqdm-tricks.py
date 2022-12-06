#%%
from tqdm import tqdm
import time

# Create two progress bar instances
pbar1 = tqdm(
    total=100,
    desc="pbar1",
    bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
    # bar_prefix="prefix",
    # bar_suffix="suffix",
)
pbar2 = tqdm(total=100, ascii=' #')

# Update the first progress bar
for i in range(100):
    pbar1.update(1)
    time.sleep(0.1)

pbar1.close()
print('', end='\r')


# Update the second progress bar
for i in range(100):
    pbar2.update(1)
    time.sleep(0.1)

pbar2.close()
print('', end='\r')



time.sleep(5)