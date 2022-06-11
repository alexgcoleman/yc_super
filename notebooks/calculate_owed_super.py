# %% [markdown]
# # Calculating Owed Superannuation
# %%
from yc_super.superdata import SuperData
from yc_super.readers import read_combined_file

import pandas as pd

from pathlib import Path

super_file = Path('data', 'Sample Super Data.xlsx')

# %%
super_data = read_combined_file(super_file)

# %%
super_data.payments