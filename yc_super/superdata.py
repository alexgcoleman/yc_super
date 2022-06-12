from __future__ import annotations
from yc_super.yearquarter import YearQuarter
import pandas as pd


SUPER_PERC = 0.095


class SuperData:
    """Contains payment and super disbursment data frames - contains data for all emps"""

    payments: pd.DataFrame
    disburs: pd.DataFrame
    employees: pd.Series
    quarters: pd.Series
    super_perc: float

    def __init__(self, payments: pd.DataFrame, disburs: pd.DataFrame, super_perc: float = SUPER_PERC):
        self.payments = payments
        self.disburs = disburs

        self.employees = self._get_unique_values('employee_code')
        self.quarters = self._get_unique_values('quarter')
        self.super_perc = super_perc

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

    def withheld_per_emp_quarter(self) -> pd.DataFrame:
        """Returns a multi-indexed dataframe containing the amount
        of withheld super for each employee for each quarter"""
        return (
            self.payments
            .loc[self.payments['is_withheld_super']]
            .groupby(['employee_code', 'quarter'])
            .agg(withheld=('amount', 'sum'))
        )

    def disbursed_per_emp_quarter(self) -> pd.DataFrame:
        """Amount of disbursed super for each employee for each quarter"""
        return (
            self.disburs
            .groupby(['employee_code', 'quarter'])
            .agg(disbursed=('amount', 'sum'))
        )

    def ote_and_entitled_super_per_emp_quarter(self) -> pd.DataFrame:
        """Sum of the OTE earned per employee per quarter"""
        ote = (
            self.payments
            .loc[self.payments['is_ote']]
            .groupby(['employee_code', 'quarter'])
            .agg(ote=('amount', 'sum'))
        )

        ote['entitled'] = ote['ote'] * self.super_perc

        return ote

    def audit_super_emp_quarter(self) -> pd.DataFrame:
        """
        Audits the super values for an employee for a quarter.

        MultiIndexed on employee_code, quarter

        Fields:
          - ote : total Ordinary time earnings
          - entitled: total entitled super (ote * super_perc)
          - withheld: total withheld super
          - disbursed: total disbursed super

        Additional Delta fields for auditing:
          - entitled-withheld: +'ve = entitled more than withheld
          - entitled-disbursed : +'ve = entitled more than disbursed
          - withheld-disbursed: +'ve = withheld more than disbursed 
        """
        audit = (self.ote_and_entitled_super_per_emp_quarter()
                 .join(self.disbursed_per_emp_quarter(), how='outer')
                 .join(self.withheld_per_emp_quarter(), how='outer')
                 .fillna(0)
                 )

        audit['entitled-withheld'] = audit['entitled'] - audit['withheld']
        audit['entitled-disbursed'] = audit['entitled'] - audit['disbursed']
        audit['withheld-disbursed'] = audit['withheld'] - audit['disbursed']
        return audit
