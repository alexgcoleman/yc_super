# %% [markdown]
# # Calculating Actual Paid Super per employee per quarter
# %%
from yc_super.readers import read_combined_file
from yc_super.yearquarter import YearQuarter
import pandas as pd

from typing import List

from pathlib import Path

super_file = Path('data', 'Sample Super Data.xlsx')

SUPER_PERC = 0.095

super_data = read_combined_file(super_file)

disburs = super_data.disburs
payments = super_data.payments


# %%
disburs
