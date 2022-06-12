""" Pandas Extensions """
import pandas as pd
import yc_super.converters as converters
from typing import Iterable


@pd.api.extensions.register_series_accessor("interval")
class IntervalSeriesAccessor:
    """Custom Pandas Series accessor .interval to allow
    access to interval periods"""

    def __init__(self, pandas_obj: pd.Series):
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


@pd.api.extensions.register_series_accessor("money")
class MoneySeriesAccessor:
    """Custom Pandas Series accessor .money

    Holds methods to handle currency, heavily uses yc_super.converters"""

    def __init__(self, pandas_obj: pd.Series):
        self._obj = pandas_obj

    @property
    def d_to_c(self):
        """Takes input dollars (as float), and returns the 'cents' value
        as an integer. """
        return self._obj.apply(converters.d_to_c)

    @property
    def c_to_d(self):
        """Takes input cents (int) and returns the 'dollar'
        value as a Decimal (to two decimal places)"""
        return self._obj.apply(converters.c_to_d)

    @property
    def format_c_as_d(self):
        """Formats cents to a standard dollar representation $34.23"""
        return self._obj.apply(converters.format_c_as_d)

    @property
    def round_c(self):
        """Rounds Cents and converts to an integer"""
        return self._obj.round().astype('Int64')


@pd.api.extensions.register_dataframe_accessor("money")
class MoneyFrameAccessor:
    """Custom Pandas DataFrame accessor .money"""

    def __init__(self, pandas_obj: pd.DataFrame):
        self._obj = pandas_obj

    def format_c_as_d(self, columns: Iterable = None):
        """Formats cents to a standard dollar representation $34.23

        If no columns are given, formats all integer columns"""
        df = self._obj.copy()

        if columns is not None:
            to_format = columns
        else:
            to_format = df.select_dtypes(include=['int', 'Int64']).columns

        df[to_format] = df[to_format].apply(
            lambda col: col.money.format_c_as_d)

        return df


@pd.api.extensions.register_series_accessor("yq")
class YearQuarterSeriesAccessor:
    """Custom Pandas Series accessor .yq to allow
    access to interval periods"""

    def __init__(self, pandas_obj: pd.Series):
        self._obj = pandas_obj

    @property
    def year(self):
        """Returns the calandar year of the YearQuarter"""
        return self._obj.apply(lambda x: x.year)

    @property
    def quarter(self):
        """Returns the Quarter as an integer (1-4)"""
        return self._obj.apply(lambda x: x.quarter)

    @property
    def start(self):
        """Returns the timestamp of the start of the YearQuarter"""
        return self._obj.apply(lambda x: x.start)

    @property
    def end(self):
        """Returns the timestamp of the end of the YearQuarter"""
        return self._obj.apply(lambda x: x.end)

    @property
    def interval(self):
        """Returns the YearQuarter as an interval"""
        return self._obj.apply(lambda x: x.interval)
