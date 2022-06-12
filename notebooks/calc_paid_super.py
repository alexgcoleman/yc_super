# %% [markdown]
# # Calculating Actual Paid Super per employee per quarter
# %%
from yc_super.readers import read_combined_file
from yc_super.yearquarter import YearQuarter
import pandas as pd

from typing import List

from pathlib import Path

DATA_PATH = Path('data', 'Sample Super Data.xlsx')
EXAMPLE_PATH = Path('data', 'example.xlsx')

super_file = EXAMPLE_PATH

SUPER_PERC = 0.095

super_data = read_combined_file(super_file)

# %%
withheld = super_data.withheld_super_per_emp_quarter()
withheld
# %%
