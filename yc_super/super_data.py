from __future__ import annotations
from typing import Callable
from yc_super.yearquarter import YearQuarter
import pandas as pd


class SuperData:
    """Contains payment and super disbursment data frames - contains data for all emps"""
    payments: pd.DataFrame
    disburs: pd.DataFrame
    employees: pd.Series
    quarters: pd.Series

    def __init__(self, payments: pd.DataFrame, disburs: pd.DataFrame):
        self.payments = payments
        self.disburs = disburs

        self.employees = self._get_unique_values('employee_code')
        self.quarters = self._get_unique_values('quarter')

    def __str__(self):
        return f"SuperData({len(self.payments)} payments; {len(self.disburs)} disbursments)"

    def __repr__(self):
        return str(self)

    def get_payments_for_quarter(self, quarter: YearQuarter) -> pd.DataFrame:
        return self.payments.loc[self.payments['quarter'] == quarter].copy()

    def _get_unique_values(self, column_name: str) -> pd.Series:
        """Returns series of all unique values in payments and disburs for
        column name"""
        dfs = [df for df in [self.payments, self.disburs] if column_name in df]

        return pd.concat([
            pd.Series(df['quarter'].unique())
            for df in dfs
        ])
