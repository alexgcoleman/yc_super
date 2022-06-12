from decimal import Decimal


def d_to_c(dollars: float) -> int:
    """Takes input dollars (as float), and returns the 'cents' value
    as an integer. """
    return int(dollars * 100)


def c_to_d(cents: int) -> Decimal:
    """Takes input cents (int) and returns the 'dollar'
    value as a Decimal (to two decimal places)"""
    return Decimal(f'{cents / 100: .2f}')


def format_c_as_d(cents: int) -> str:
    """Formats cents to a standard dollar representation $34.23"""
    sign = '-' if cents < 0 else ''

    return f'{sign}${abs(cents / 100):.2f}'
