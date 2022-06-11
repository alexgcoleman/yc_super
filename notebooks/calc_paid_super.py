# %% [markdown]
# # Calculating Actual Paid Super per employee per quarter
# %%
from yc_super.readers import read_combined_file
from yc_super.yearquarter import YearQuarter
import pandas as pd

from pathlib import Path

super_file = Path('data', 'Sample Super Data.xlsx')

SUPER_PERC = 0.095

super_data = read_combined_file(super_file)

disburs = super_data.disburs

# %% [markdown]
# ## Do timestamp columns represent same quarter for each row?
# No!
# %%
ts_cols = ['payment_made', 'pay_period_from', 'pay_period_to']
for col in ts_cols:
    disburs[f'qtr_{col}'] = disburs[col].apply(YearQuarter)

disburs['qrt_same_made_from'] = disburs['qtr_payment_made'] == disburs['qtr_pay_period_from']
disburs['qrt_same_made_to'] = disburs['qtr_payment_made'] == disburs['qtr_pay_period_to']
disburs['qrt_same_to_from'] = disburs['qtr_pay_period_to'] == disburs['qtr_pay_period_from']

# %%
disburs['qrt_same_made_from'].value_counts()

# %%
disburs['qrt_same_made_to'].value_counts()

# %%
disburs['qrt_same_to_from'].value_counts()

# %% [markdown]
# ## Building Timespan for Disbupsments


def get_pay_period(disbur_row: pd.Series) -> pd.Interval:
    return pd.Interval(
        left=disbur_row['pay_period_from'],
        right=disbur_row['pay_period_to'],
        closed='both')


disburs['pay_period'] = disburs.apply(get_pay_period, axis=1)
disburs
# %%
payments = super_data.payments

payments
