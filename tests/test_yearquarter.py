from yc_super.yearquarter import YearQuarter
import pytest
import pandas as pd
from itertools import product
from typing import List, Tuple
TEST_START_YEAR = 1980
TEST_END_YEAR = 2200
QUARTERS = [1, 2, 3, 4]


def all_year_quarter_ints() -> List[Tuple[int, int]]:
    return list(
        product(
            range(TEST_START_YEAR, TEST_END_YEAR+1),
            QUARTERS))


def all_timestamps() -> List[pd.Timestamp]:
    return list(pd.date_range(
        start=str(TEST_START_YEAR),
        end=str(TEST_END_YEAR),
        freq="D"))


def boundary_timestamps():
    """Only timestamps near the beginning (1-3) and end (26+) 
    of each month"""
    all_ts = all_timestamps()
    return [
        ts for ts in all_ts
        if ts.day <= 4
        and ts.day >= 26]


def yq_str(y: int, q: int) -> str:
    return f"{y}-Q{q}"


def all_yqs() -> List[YearQuarter]:
    return [YearQuarter(year=y, quarter=q)
            for (y, q) in all_year_quarter_ints()]


def test_int_init():
    """Tests initilisation using integer year, quarter method"""
    for (year, quarter) in all_year_quarter_ints():
        yq = YearQuarter(year=year, quarter=quarter)
        print(yq)
        assert str(yq) == yq_str(year, quarter)


def test_timestamp_init():
    """Tests initialisation using timestamp method"""
    for ts in all_timestamps():
        yq = YearQuarter(ts)
        assert str(yq) == yq_str(ts.year, ts.quarter)


@pytest.mark.slow
def test_interval_coverage_exhaustive():
    """Tests that the YearQuarter intervals cover all days (i.e. no day
    falls outside of every year quarter interval)"""
    yqs = [YearQuarter(year=y, quarter=q)
           for (y, q) in all_year_quarter_ints()]

    for ts in all_timestamps():
        assert any([(ts in yq.interval) for yq in yqs])


def test_interval_coverage_quick():
    """Tests that the YearQuarter intervals cover all days (i.e. no day
    falls outside of every year quarter interval)

    Quick version, so we only test around the start and end of every month
    (days 1-3, days 27+) of each month"""
    yqs = all_yqs()

    for ts in boundary_timestamps():
        assert any([(ts in yq.interval) for yq in yqs])


def test_no_interval_overlap():
    """Tests that no YearQuarter interval overlaps with another"""
    yq_intervals = [yq.interval for yq in all_yqs()]

    for interval in yq_intervals:
        # should only overlap with itself
        assert sum([interval.overlaps(other) for other in yq_intervals]) == 1
