import MetaTrader5 as mt5

def get_candles(symbol, timeframe, count=100):
    """
    Fetch candlestick data for a symbol and timeframe.
    Returns a list of dictionaries containing OHLCV data.
    """
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    return rates if rates is not None else []


def detect_structure_break(symbol, timeframe=mt5.TIMEFRAME_H1):
    """
    Detects:
    - BOS_UP: Break of previous highs (bullish BOS)
    - BOS_DOWN: Break of previous lows (bearish BOS)
    - CHoCH: Lower high and higher low inside a range (change of character)
    - NONE: No meaningful structure change
    """
    candles = get_candles(symbol, timeframe, 30)
    if len(candles) < 5:
        return None

    highs = [candle['high'] for candle in candles]
    lows = [candle['low'] for candle in candles]

    recent_highs = highs[-5:]
    recent_lows = lows[-5:]

    if recent_highs[-1] > max(recent_highs[:-1]):
        return "BOS_UP"
    elif recent_lows[-1] < min(recent_lows[:-1]):
        return "BOS_DOWN"
    elif (
        recent_lows[-1] > min(recent_lows[:-1]) and
        recent_highs[-1] < max(recent_highs[:-1])
    ):
        return "CHoCH"
    else:
        return "NONE"


def detect_mitigation_zone(symbol, direction, timeframe=mt5.TIMEFRAME_H1):
    """
    Detect mitigation zone (unmitigated order block).
    - For "UP": Finds last bearish candle → returns its body (low, high)
    - For "DOWN": Finds last bullish candle → returns its body (low, high)
    """
    candles = get_candles(symbol, timeframe, 20)
    if not candles:
        return None

    if direction.upper() == "UP":
        # Look for last bearish candle (potential demand zone)
        for c in reversed(candles):
            if c['close'] < c['open']:
                return (c['low'], c['high'])

    elif direction.upper() == "DOWN":
        # Look for last bullish candle (potential supply zone)
        for c in reversed(candles):
            if c['close'] > c['open']:
                return (c['low'], c['high'])

    return None
