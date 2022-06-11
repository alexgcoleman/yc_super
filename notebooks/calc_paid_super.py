# %% [markdown]
# # Calculating Actual Paid Super per employee per quarter
# %%
from yc_super.readers import read_combined_file
import pandas as pd

from pathlib import Path

super_file = Path('data', 'Sample Super Data.xlsx')

SUPER_PERC = 0.095

super_data = read_combined_file(super_file)

disbursments = super_data.disbursments

# %% [markdonw]
# ## Determining Correct Quarter for Disbursement
# %%
