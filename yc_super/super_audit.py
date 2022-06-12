import pandas as pd
from yc_super.super_data import SuperData

SUPER_PERC = 0.095  # TODO: add this to a config file


def withheld_per_emp_qtr(super_data: SuperData) -> pd.DataFrame:
    """Returns a multi-indexed dataframe containing the amount
    of withheld super for each employee for each quarter"""
    return (
        super_data.payments
        .loc[super_data.payments['is_withheld_super']]
        .groupby(['employee_code', 'quarter'])
        .agg(withheld=('amount', 'sum'))
    )


def disbursed_per_emp_qtr(super_data: SuperData) -> pd.DataFrame:
    """Amount of disbursed super for each employee for each quarter"""
    return (
        super_data.disburs
        .groupby(['employee_code', 'quarter'])
        .agg(disbursed=('amount', 'sum'))
    )


def ote_and_payable_per_emp_qtr(super_data: SuperData) -> pd.DataFrame:
    """Sum of the OTE earned per employee per quarter"""
    ote = (
        super_data.payments
        .loc[super_data.payments['is_ote']]
        .groupby(['employee_code', 'quarter'])
        .agg(ote=('amount', 'sum'))
    )
    ote['payable'] = ote['ote'] * SUPER_PERC

    return ote


def audit_super_emp_qtr(super_data: SuperData) -> pd.DataFrame:
    """
    Audits the super values for an employee for a quarter.

    MultiIndexed on employee_code, quarter

    All calculations done at 'quarter' level, i.e OTE payments are
    summed for the quarter, and super calculated from the total.

    Fields:
        - ote : total Ordinary time earnings
        - payable: total payable super (ote * super_perc)
        - withheld: total withheld super
        - disbursed: total disbursed super

    Additional fields for auditing:
        - payable-withheld: +'ve = payable more than withheld
        - payable-disbursed : +'ve = payable more than disbursed
        - withheld-disbursed: +'ve = withheld more than disbursed 
    """
    audit = (
        ote_and_payable_per_emp_qtr(super_data)
        .join(disbursed_per_emp_qtr(super_data), how='outer')
        .join(withheld_per_emp_qtr(super_data), how='outer')
        .fillna(0).astype(int)
    )

    audit['payable-withheld'] = audit['payable'] - audit['withheld']
    audit['payable-disbursed'] = audit['payable'] - audit['disbursed']
    audit['withheld-disbursed'] = audit['withheld'] - audit['disbursed']

    return audit
