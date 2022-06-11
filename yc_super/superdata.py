import pandas as pd

class SuperData:
    """Contains payment and super disbursment data frames"""
    def __init__(self, payments: pd.DataFrame, disbursments: pd.DataFrame):
        self.payments = payments
        self.disbursments = disbursments

    # TODO: str and repr methods
