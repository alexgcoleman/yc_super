import pandas as pd
from yc_super.superdata import SuperData

# TODO: read this from config/env?
SUPER_PERC = 0.095


def calculate_owed(super_data: SuperData) -> pd.DataFrame:
    """Takes a SuperData object and returns a dataframe 
    representing the total amount of super owed per-employee, per-quarter

    Only sums payments where `is_ote` is True

    Output dataframe structure
    index:
        employee_code,
        quarter: yc_super.yearquarter.YearQuarter

    values:
        payslip_total: float -> Total amount of OTE for payslips
        owed_super: -> Total amount of super owed in that quarter

    """
    payments = super_data.payments

    ote_per_quarter = (
        payments[payments['is_ote']]
        .groupby(['employee_code', 'quarter'])
        .agg(payslip_total=('amount', 'sum')))

    ote_per_quarter['owed_super'] = ote_per_quarter['payslip_total'] * SUPER_PERC

    return ote_per_quarter
