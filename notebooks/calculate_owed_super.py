# %% [markdown]
# # Calculating Owed Superannuation
# %%
from __future__ import annotations

from yc_super.readers import read_combined_file
from yc_super.owed import calculate_owed
import pandas as pd

from pathlib import Path

super_file = Path('data', 'Sample Super Data.xlsx')

SUPER_PERC = 0.095

# %%
super_data = read_combined_file(super_file)
payments = super_data.payments
# %% [markdown]
# ## Categorising payments into quarters
# %%
owed = calculate_owed(super_data)
owed
