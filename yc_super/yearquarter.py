from __future__ import annotations
import pandas as pd
from functools import total_ordering

@total_ordering
class YearQuarter:
    year: int
    quarter: int

    def __init__(self, dt: pd.Timestamp):
        self.year = dt.year
        self.quarter = dt.quarter

    def __str__(self):
        return f'{self.year}-Q{self.quarter}'
    
    def __repr__(self):
        return f'YearQuarter({self})'

    def __eq__(self, other: YearQuarter) -> bool:
        return (self.year == other.year) and (self.quarter == other.quarter)

    def __gt__(self, other: YearQuarter) -> bool:
        if self.year > other.year:
            return True
        
        elif self.year < other.year:
            return False

        else:
            return self.quarter > other.quarter

    @property
    def start(self) -> pd.Timestamp:
        return pd.Timestamp(
            year=self.year,
            month={
                1: 1,
                2: 4,
                3: 7,
                4: 10}[self.quarter],
            day=1)

    @property
    def end(self) -> pd.Timestamp:
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