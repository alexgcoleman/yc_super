from pathlib import Path
from yc_super.superdata import SuperData
from yc_super.yearquarter import YearQuarter

import pandas as pd

class UncodedPaySlipWarning(Warning):
    pass

def is_ote(ote_description: str) -> bool:
    ote_description = ote_description.lower()
    if ote_description not in ['ote', 'not ote']:
        raise ValueError(f"Invalid ote_treatment {ote_description}")
    
    return ote_description == 'ote'


def read_combined_file(path: Path) -> SuperData:
    """Reads a combined superannuation file, and returns payslip and disbursment data"""
    excel = pd.ExcelFile(path)

    disbursments = excel.parse('Disbursements')
    pay_codes = excel.parse('PayCodes')
    pay_slips = excel.parse('Payslips')

    # adding pay codes to payslip data
    payments = pay_slips.merge(
        pay_codes.rename(columns={
            'pay_code': 'code'}),
        on='code',
        how='left',
        validate='m:1', # ensure that we don't multiply payslip data
        indicator=True, # 
    )

    if payments['_merge'].value_counts()['left_only'].sum() > 0:
        uncoded_slips = payments[payments['_merge'] == 'left_only']
        raise UncodedPaySlipWarning(f"Detected {len(uncoded_slips)} uncoded payslips!")
        # TODO: output this to an exception file


    payments['is_ote'] = payments['ote_treament'].apply(is_ote)

    payments = payments.drop(columns=['_merge', 'ote_treament'])
    payments['quarter'] = payments['end'].apply(YearQuarter)

    return SuperData(payments=payments, disbursments=disbursments)
