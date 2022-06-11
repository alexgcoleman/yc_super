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
        return f'YearQuater({self})'

    def __eq__(self, other: YearQuarter) -> bool:
        return (self.year == other.year) and (self.quarter == other.quarter)

    def __gt__(self, other: YearQuarter) -> bool:
        if self.year > other.year:
            return True
        
        elif self.year < other.year:
            return False

        else:
            return self.quarter > other.quarter

    def __hash__(self):
        return hash(repr(self))