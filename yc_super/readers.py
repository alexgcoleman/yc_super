from pathlib import Path
from yc_super.superdata import SuperData
from yc_super.yearquarter import YearQuarter

from typing import Tuple

import pandas as pd


class UncodedPaySlipWarning(Warning):
    pass


def is_ote(ote_description: str) -> bool:
    ote_description = ote_description.lower()
    if ote_description not in ['ote', 'not ote']:
        raise ValueError(f"Invalid ote_treatment {ote_description}")

    return ote_description == 'ote'


def parse_payments(raw_pay_codes: pd.DataFrame, raw_pay_slips: pd.DataFrame) -> pd.DataFrame:
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

    payments = payments.drop(columns=['_merge', 'ote_treament'])
    payments['quarter'] = payments['end'].apply(YearQuarter)

    return payments


def parse_disburs(raw_disburs: pd.DataFrame) -> pd.DataFrame:
    # TODO: add docstring + define output frame structure
    ts_cols = ['payment_made', 'pay_period_from', 'pay_period_to']

    disburs = raw_disburs.copy()
    disburs[ts_cols] = disburs[ts_cols].apply(pd.to_datetime)

    # pay period defines the interval of dates for which payslips are captured from
    disburs['pay_period'] = disburs.apply(
        lambda row: pd.Interval(
            left=row['pay_period_from'],
            right=row['pay_period_to'],
            closed='both'), axis=1)

    disburs = disburs.drop(
        columns=['pay_period_from', 'pay_period_to'])

    return disburs


def idx_of_containing_interval(x: object, interval_series: pd.Series, on_multiple: str = 'raise') -> object:
    """Returns the index from interval_series that contains x

    Returns None if no interval contains x

    on_multiple: how to handle instances where multiple intervals contain x
        - 'raise' (default): raise ValueError
        - 'first': return first interval's idx
    """

    valid_on_multiple = ['raise', 'first']
    if on_multiple not in valid_on_multiple:
        raise ValueError(
            f"on_multiple can only be one of {valid_on_multiple} (got {on_multiple}).")

    # intervals that contain x
    contains = interval_series[
        interval_series.apply(lambda interval: x in interval)]

    if len(contains) == 0:
        return None

    if (on_multiple == 'raise') and (len(contains) > 1):
        raise ValueError(
            f"{len(contains)} intervals contained {x}, and on_multiple={on_multiple}")

    return contains.index[0]


def get_disbur_idx_for_payslip(payslip_row: pd.Series, disburs: pd.DataFrame) -> object:
    return idx_of_containing_interval(
        x=payslip_row['end'],
        interval_series=disburs.loc[
            disburs['employee_code'] == payslip_row['employee_code'], 'pay_period'
        ]
    )


def filter_future_disburs(disburs_df: pd.DataFrame, payments: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Filters disbursements that cover a period after the latest payment)

    Returns Tuple (past, future), representing past and future (excluded) disbursements"""
    disburs = disburs_df.copy()

    emp_payment_ranges = payments.groupby('employee_code').agg(
        _payment_max_date=('end', 'max'))

    disburs = disburs.merge(
        emp_payment_ranges, on='employee_code', how='left')

    rows_future_disburs = disburs['pay_period'].apply(
        lambda x: x.right) > disburs['_payment_max_date']

    # can return input df, as indexes will be aligned - ensures we don't mutate it accidentally
    return (
        disburs_df[~rows_future_disburs],
        disburs_df[rows_future_disburs]
    )


def read_combined_file(path: Path) -> SuperData:
    """Reads a combined superannuation file, and returns payslip and disbursement data"""
    excel = pd.ExcelFile(path)

    payments = parse_payments(
        raw_pay_codes=excel.parse('PayCodes'),
        raw_pay_slips=excel.parse('Payslips')
    )

    # TODO: do something with future_disburs! log, save in SuperData for rainy day?
    disburs, future_disburs = (
        excel
        .parse('Disbursements')
        .pipe(parse_disburs)
        .pipe(filter_future_disburs, payments))

    # adding disbursement_id to payments
    payments['_disbur_idx'] = payments.apply(
        get_disbur_idx_for_payslip, axis=1, disburs=disburs)

    return SuperData(payments=payments, disburs=disburs)
