from pathlib import Path
from yc_super.superdata import SuperData
from yc_super.yearquarter import YearQuarter

from typing import Tuple

import pandas as pd

WITHHELD_SUPER_CODE = 'P001 - Co. Super 9.5%'


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
    payments['is_withheld_super'] = payments['code'] == WITHHELD_SUPER_CODE

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
        columns=['pay_period_from', 'pay_period_to']).rename(columns={
            'sgc_amount': 'amount'
        })

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


@pd.api.extensions.register_series_accessor("interval")
class IntervalAccessor:
    """Implementing custom accessor as using a lot of interval methods"""

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    @property
    def left(self):
        return self._obj.apply(lambda x: x.left)

    @property
    def right(self):
        return self._obj.apply(lambda x: x.right)

    @property
    def length(self):
        return self._obj.apply(lambda x: x.length)


def can_absorb(interval_1, interval_2: pd.Series) -> bool:
    """Returns True if disbur_1 can absorb disbur_2"""
    return ((interval_1.left <= interval_2.left)
            and (interval_1.right >= interval_2.right))


def absorb_disburs_for_emp(emp_disburs_df: pd.DataFrame) -> pd.DataFrame:
    """"""
    emp_disburs = emp_disburs_df
    emp_disburs['_period_length'] = emp_disburs['pay_period'].interval.length

    # sort descending payment_made date and period_length
    # now we only need to consider if a row absorbs the next row
    emp_disburs = emp_disburs.sort_values(
        ['payment_made', '_period_length'], ascending=False)

    # finding what to absorb
    # TODO: below line seems to be a bug in this pandas? unable to shift
    # series that contains intervals, seems to try and concat?
    # bypassing by reconstructin interval from next row
    #emp_disburs['_next_period'] = emp_disburs['pay_period'].shift(-1)
    emp_disburs['_next_left'] = emp_disburs['pay_period'].interval.left.shift(
        -1).fillna(emp_disburs['pay_period'].interval.left) + pd.DateOffset(1)
    emp_disburs['_next_right'] = emp_disburs['pay_period'].interval.right.shift(
        -1).fillna(emp_disburs['pay_period'].interval.right)
    emp_disburs['_next_period'] = emp_disburs.apply(
        lambda row: pd.Interval(row['_next_left'], row['_next_right'], closed='both'), axis=1)

    emp_disburs['_next_amount'] = emp_disburs['amount'].shift(-1, fill_value=0)

    emp_disburs['_absorb_next'] = emp_disburs.apply(
        lambda row: can_absorb(row['pay_period'], row['_next_period']), axis=1)

    emp_disburs['_was_absorbed'] = emp_disburs['_absorb_next'].shift(
        1, fill_value=False)

    # absorbing
    # TODO: below technique doesn't work if there are multiple concurrent absorbtions! just raise error for now
    emp_disburs['_absorb_next_next'] = emp_disburs['_absorb_next'].shift(1)
    if sum(emp_disburs['_absorb_next'] & emp_disburs['_absorb_next_next']) > 0:
        raise ValueError('detected multiple concurrent absorptions!')

    # adding totals from absorbees
    rows_arbsorbers = emp_disburs['_absorb_next']
    emp_disburs.loc[rows_arbsorbers,
                    'amount'] += emp_disburs.loc[rows_arbsorbers, '_next_amount']

    # returnign unabsorbed rows, with original columns
    return emp_disburs.loc[~emp_disburs['_was_absorbed'], list(emp_disburs_df)]


def absorb_disburs(disburs_df: pd.DataFrame) -> pd.DataFrame:
    """Makes disbursements with a pay_period that entirely encompass 
    other disbursements' pay_periods "absorb" the smaller disbursements,
    adding their total to its own.

    Returns disbursements DataFrame
    """
    return pd.concat([
        disburs_df.loc[disburs_df['employee_code'] == emp]
        .copy()
        .pipe(absorb_disburs_for_emp)
        for emp in disburs_df['employee_code'].unique()
    ])


def combine_disburse_payments(disburs_df: pd.DataFrame, payments_df: pd.DataFrame) -> pd.DataFrame:
    """Returns disburments, with matching payments data added as a nested series"""
    disburs = disburs_df.copy()
    payments = payments_df.copy()

    payments['_disbur_idx'] = payments.apply(
        get_disbur_idx_for_payslip, axis=1, disburs=disburs).astype("Int64")

    # getting payment data for disbursments
    disburs_payment_data = (
        pd.DataFrame({'_disbur_idx': disburs.index})
        .merge(payments.fillna(-1), on='_disbur_idx', how='left')
        .groupby('_disbur_idx')
        .agg(
            payslip_ids=('payslip_id', 'unique'),
            payslip_quarters=('quarter', 'unique'),
            payslip_num_quarters=('quarter', 'nunique')
        )
    )

    return disburs.join(disburs_payment_data)


def read_combined_file(path: Path) -> SuperData:
    """Reads a combined superannuation file, and returns payslip and disbursement data"""
    excel = pd.ExcelFile(path)

    payments = parse_payments(
        raw_pay_codes=excel.parse('PayCodes'),
        raw_pay_slips=excel.parse('Payslips')
    )

    disburs = (
        excel
        .parse('Disbursements')
        .pipe(parse_disburs)
        .pipe(absorb_disburs)
        .pipe(combine_disburse_payments, payments_df=payments)
    )

    return SuperData(payments=payments, disburs=disburs)
