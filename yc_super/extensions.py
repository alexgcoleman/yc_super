import pandas as pd


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
