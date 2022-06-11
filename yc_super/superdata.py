from __future__ import annotations
import pandas as pd


class SuperData:
    """Contains payment and super disbursment data frames - contains data for all emps"""

    def __init__(self, payments: pd.DataFrame, disburs: pd.DataFrame):
        self.payments = payments
        self.disburs = disburs

    def __str__(self):
        return f"SuperData({len(self.payments)} payments; {len(self.disburs)} disbursments)"

    def __repr__(self):
        return str(self)

    def get_emp_super_data(self, employee_code) -> EmpSuperData:
        return EmpSuperData(self, employee_code)


class EmpSuperData(SuperData):
    """Contains payment and super disbursement data frames for a single emp"""

    def __init__(self, super_data: SuperData, employee_code: int):
        self.employee_code = employee_code

        payments = super_data.payments
        disburs = super_data.disburs
        super().__init__(
            payments=payments.loc[payments['employee_code'] == employee_code],
            disburs=disburs.loc[disburs['employee_code'] == employee_code]
        )
