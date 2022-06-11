from __future__ import annotations
from yc_super.yearquarter import YearQuarter
import pandas as pd

WINDOW_TO_PAY = pd.Timedelta(days=28)


class SuperData:
    """Contains payment and super disbursment data frames - contains data for all emps"""

    def __init__(self, payments: pd.DataFrame, disburs: pd.DataFrame):
        self.payments = payments
        self.disburs = disburs

        self.employees = self._get_employees()

    def __str__(self):
        return f"SuperData({len(self.payments)} payments; {len(self.disburs)} disbursments)"

    def __repr__(self):
        return str(self)

    def get_emp_super_data(self, employee_code) -> EmpSuperData:
        return EmpSuperData(self, employee_code)

    def get_payments_for_quarter(self, quarter: YearQuarter) -> pd.DataFrame:
        return self.payments.loc[self.payments['quarter'] == quarter].copy()

    def get_disbursments_for_quarter(self, quarter: YearQuarter) -> pd.DataFrame:
        return self.disburs[
            (self.disburs['payment_made'] -
             WINDOW_TO_PAY).apply(lambda ts: ts in quarter)
        ]

    def _get_employees(self):
        return pd.concat([
            pd.Series(df['employee_code'].unique()) for df in (self.payments, self.disburs)]).unique()


class EmpSuperData(SuperData):
    """Contains payment and super disbursement data frames for a single emp"""

    def __init__(self, super_data: SuperData, employee_code: int):
        self.employee_code = employee_code

        payments = super_data.payments.copy()
        disburs = super_data.disburs.copy()

        super().__init__(
            payments=payments.loc[payments['employee_code'] == employee_code],
            disburs=disburs.loc[disburs['employee_code'] == employee_code]
        )

    def __str__(self):
        return f"EmpSuperData:{self.employee_code}:({len(self.payments)} payments; {len(self.disburs)} disbursments)"
