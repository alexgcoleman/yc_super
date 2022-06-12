from __future__ import annotations
import pandas as pd
from functools import total_ordering


@total_ordering
class YearQuarter:
    """Class which defines a financial quarter.

    Can be initialised using either:
        timestamp=pd.Timestamp
        or
        year=int
        quarter=int (1-4)"""
    year: int
    quarter: int
    start: pd.Timestamp
    end: pd.Timestamp
    interval: pd.Interval

    def __init__(self, ts: pd.Timestamp | None = None, year=None, quarter=None):
        if ts is not None:
            self.year = ts.year
            self.quarter = ts.quarter

        elif year is not None and quarter is not None:
            if quarter not in range(1, 5):
                raise ValueError(f'Invalid quarter: {quarter}')
            self.year = year
            self.quarter = quarter

        else:
            raise ValueError(
                'Must construct with either timestamp argument, or year and quarter keywords')

        self.start = self._get_start()
        self.end = self._get_end()
        self.interval = pd.Interval(self.start, self.end, closed='both')

    def __str__(self) -> str:
        return f'{self.year}-Q{self.quarter}'

    def __repr__(self) -> str:
        return f'YearQuarter({self})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, YearQuarter):
            raise NotImplementedError

        return (self.year == other.year) and (self.quarter == other.quarter)

    def __gt__(self, other: YearQuarter) -> bool:
        if self.year > other.year:
            return True

        elif self.year < other.year:
            return False

        else:
            return self.quarter > other.quarter

    def __contains__(self, other: object):
        if not isinstance(other, pd.Timestamp):
            raise NotImplementedError

        return other in self.interval

    def _get_start(self) -> pd.Timestamp:
        """Gets the timestamp representing the first day of the quarter"""
        return pd.Timestamp(
            year=self.year,
            month={
                1: 1,
                2: 4,
                3: 7,
                4: 10}[self.quarter],
            day=1)

    def _get_end(self) -> pd.Timestamp:
        """Gets the timestamp representing the last day of the quarter"""
        return pd.Timestamp(
            year=self.year,
            month={
                1: 3,
                2: 6,
                3: 9,
                4: 12}[self.quarter],
            day={
                1: 31,
                2: 30,
                3: 30,
                4: 31}[self.quarter])

    def __hash__(self):
        return hash(repr(self))


@pd.api.extensions.register_series_accessor("yq")
class YearQuarterAccessor:
    """Custom Pandas Series accessor .yq to allow
    access to interval periods"""

    def __init__(self, pandas_obj):
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
