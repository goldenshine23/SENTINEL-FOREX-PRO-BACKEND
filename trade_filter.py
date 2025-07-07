import MetaTrader5 as mt5
from backend.config import MAX_SPREAD_PIPS  # Set this in config, e.g., MAX_SPREAD_PIPS = 3

def is_spread_acceptable(symbol, max_spread_pips=None):
    """
    Check if the spread for the given symbol is within the acceptable limit.

    Args:
        symbol (str): The trading symbol, e.g., 'EURUSD'
        max_spread_pips (float, optional): Maximum acceptable spread in pips. Uses default if None.

    Returns:
        bool: True if spread is acceptable, False otherwise
    """
    max_spread_pips = max_spread_pips or MAX_SPREAD_PIPS

    # Fetch current market data
    tick = mt5.symbol_info_tick(symbol)
    info = mt5.symbol_info(symbol)

    if not tick or not info:
        return False  # Cannot verify spread without data

    point = info.point
    spread_in_pips = (tick.ask - tick.bid) / point

    return spread_in_pips <= max_spread_pips
