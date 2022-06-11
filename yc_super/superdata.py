import pandas as pd


class SuperData:
    """Contains payment and super disbursment data frames"""

    def __init__(self, payments: pd.DataFrame, disburs: pd.DataFrame):
        self.payments = payments
        self.disburs = disburs

    # TODO: str and repr methods
