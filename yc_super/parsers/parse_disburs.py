from yc_super.yearquarter import YearQuarter
from typing import Callable
import pandas as pd

# TODO: put this in a config
WINDOW_TO_PAY = pd.Timedelta(days=28)


def get_quarter_from_payment_window(disburs_df: pd.DataFrame, window_days: int = WINDOW_TO_PAY) -> pd.Series:
    """Determine disbursement quarter (the quarter the disbursement applied to)
    using the Payment Window technique."""
    return (disburs_df['payment_made'] - window_days).apply(YearQuarter)


def consolidate_pay_period(disburs_df: pd.DataFrame) -> pd.DataFrame:
    """Converts pay_period_from, pay_period_to into a pandas Interval

    Removes columns:
      - pay_period_from
      - pay_period_to

    Adds columns:
      - pay_period : Interval
    """
    disburs = disburs_df.copy()

    disburs['pay_period'] = disburs.apply(
        lambda row: pd.Interval(
            left=row['pay_period_from'],
            right=row['pay_period_to'],
            closed='both'), axis=1)

    disburs = disburs.drop(
        columns=['pay_period_from', 'pay_period_to'])

    return disburs


def parse(raw_disburs: pd.DataFrame, quarter_fn: Callable = get_quarter_from_payment_window) -> pd.DataFrame:
    """Parse a raw disbursment dataframe"""
    ts_cols = ['payment_made', 'pay_period_from', 'pay_period_to']

    disburs = raw_disburs.copy().rename(columns={'sgc_amount': 'amount'})
    disburs[ts_cols] = disburs[ts_cols].apply(pd.to_datetime)

    disburs['quarter'] = disburs.pipe(quarter_fn)
    disburs['amount'] = disburs['amount'].money.d_to_c

    return disburs
