import pandas as pd
from yc_super.yearquarter import YearQuarter

WITHHELD_SUPER_CODE = 'P001 - Co. Super 9.5%'


def is_ote(ote_description: str) -> bool:
    ote_description = ote_description.lower()
    if ote_description not in ['ote', 'not ote']:
        raise ValueError(f"Invalid ote_treatment {ote_description}")

    return ote_description == 'ote'


class UncodedPaySlipWarning(Warning):
    pass


def parse(raw_pay_codes: pd.DataFrame, raw_pay_slips: pd.DataFrame) -> pd.DataFrame:
    # TODO add doc string + Define output frame structure

    # adding pay codes to payslip data
    payments = raw_pay_slips.merge(
        raw_pay_codes.rename(columns={
            'pay_code': 'code'}),
        on='code',
        how='left',
        validate='m:1',  # ensure that we don't multiply payslip data
        indicator=True,
    )

    if payments['_merge'].value_counts()['left_only'].sum() > 0:
        uncoded_slips = payments[payments['_merge'] == 'left_only']
        raise UncodedPaySlipWarning(
            f"Detected {len(uncoded_slips)} uncoded payslips!")
        # TODO: output this to an exception file

    payments['is_ote'] = payments['ote_treament'].apply(is_ote)
    payments['is_withheld_super'] = payments['code'] == WITHHELD_SUPER_CODE

    payments = payments.drop(columns=['_merge', 'ote_treament'])
    payments['quarter'] = payments['end'].apply(YearQuarter)
    payments['amount'] = payments['amount'].money.dollars_to_cents

    return payments
