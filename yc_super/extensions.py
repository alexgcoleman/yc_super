import pandas as pd
import yc_super.converters as converters


@pd.api.extensions.register_series_accessor("interval")
class IntervalAccessor:
    """Custom Pandas Series accessor .interval to allow
    access to interval periods"""

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


@pd.api.extensions.register_series_accessor("money")
class MoneyAccessor:
    """Custom Pandas Series accessor .money

    Holds methods to handle currency, heavily uses yc_super.converters"""

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    @property
    def dollars_to_cents(self):
        """Takes input dollars (as float), and returns the 'cents' value
        as an integer. """
        return self._obj.apply(converters.dollars_to_cents)

    @property
    def cents_to_dollars(self):
        """Takes input cents (int) and returns the 'dollar'
        value as a Decimal (to two decimal places)"""
        return self._obj.apply(converters.cents_to_dollars)

    @property
    def cents_to_dollar_str(self):
        """Formats cents to a standard dollar representation $34.23"""
        return self._obj.apply(converters.cents_to_dollar_str)

    @property
    def round_cents(self):
        """Rounds Cents back to an integer"""
        return self._obj.round().astype('Int64')
