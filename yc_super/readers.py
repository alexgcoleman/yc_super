from pathlib import Path
from yc_super.super_data import SuperData
from yc_super.parsers import parse_disburs, parse_payments
import pandas as pd


def read_combined_file(path: Path) -> SuperData:
    """Reads a combined superannuation file, and returns payslip and disbursement data"""
    excel = pd.ExcelFile(path)

    payments = parse_payments.parse(
        raw_pay_codes=excel.parse('PayCodes'),
        raw_pay_slips=excel.parse('Payslips')
    )

    disburs = (excel.parse('Disbursements')
               .pipe(parse_disburs.parse))

    return SuperData(payments=payments, disburs=disburs)
