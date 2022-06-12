from decimal import Decimal


def dollars_to_cents(dollars: float) -> int:
    """Takes input dollars (as float), and returns the 'cents' value
    as an integer. """
    return int(dollars * 100)


def cents_to_dollars(cents: int) -> Decimal:
    """Takes input cents (int) and returns the 'dollar'
    value as a Decimal (to two decimal places)"""
    return Decimal(f'{cents / 100: .2f}')


def cents_to_dollar_str(cents: int) -> str:
    """Formats cents to a standard dollar representation $34.23"""
    sign = '-' if cents < 0 else ''

    return f'{sign}${abs(cents / 100):.2f}'
