import MetaTrader5 as mt5
from statistics import mean

def get_candles(symbol, timeframe, count=50):
    """Fetch recent OHLC candles for the given symbol and timeframe."""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    return rates if rates else []

def get_trend_direction(symbol):
    """
    Top-down trend check: W1, D1, H4
    - Use 5/15 SMA crossover voting
    - 2 out of 3 agreement confirms trend
    """
    timeframes = [mt5.TIMEFRAME_W1, mt5.TIMEFRAME_D1, mt5.TIMEFRAME_H4]
    trend_votes = []

    for tf in timeframes:
        candles = get_candles(symbol, tf, 20)
        if not candles:
            continue

        closes = [c['close'] for c in candles]
        ma_fast = mean(closes[-5:])
        ma_slow = mean(closes[-15:])

        if ma_fast > ma_slow:
            trend_votes.append("UP")
        elif ma_fast < ma_slow:
            trend_votes.append("DOWN")

    if trend_votes.count("UP") >= 2:
        return "UP"
    elif trend_votes.count("DOWN") >= 2:
        return "DOWN"
    return "NONE"

def is_market_ranging(symbol):
    """
    Detect sideways market using MA compression on H4.
    - Range if MA distance is small relative to average candle range.
    """
    candles = get_candles(symbol, mt5.TIMEFRAME_H4, 50)
    if not candles:
        return True

    closes = [c['close'] for c in candles]
    ma_fast = mean(closes[-10:])
    ma_slow = mean(closes[-30:])
    distance = abs(ma_fast - ma_slow)
    avg_range = mean([c['high'] - c['low'] for c in candles])

    return distance < 0.25 * avg_range

def confirm_candle_entry(symbol):
    """
    Confirm entry using M15 engulfing or pin bar pattern.
    - Looks at last 2 full candles (ignore current forming)
    """
    candles = get_candles(symbol, mt5.TIMEFRAME_M15, 3)
    if len(candles) < 3:
        return False

    prev = candles[-2]
    curr = candles[-1]

    # Bullish Engulfing
    if (
        prev['close'] < prev['open'] and curr['close'] > curr['open'] and
        curr['close'] > prev['open'] and curr['open'] < prev['close']
    ):
        return True

    # Bearish Engulfing
    if (
        prev['close'] > prev['open'] and curr['close'] < curr['open'] and
        curr['close'] < prev['open'] and curr['open'] > prev['close']
    ):
        return True

    # Pin Bar (small body, long wick)
    body = abs(curr['close'] - curr['open'])
    wick = curr['high'] - curr['low']
    if body < 0.25 * wick:
        return True

    return False

def detect_order_block(symbol, direction):
    """
    Detect recent high/low as proxy OB zone.
    - Could later use imbalance detection, CHoCH, mitigation
    """
    candles = get_candles(symbol, mt5.TIMEFRAME_H1, 20)
    if not candles:
        return None

    if direction == "UP":
        return min(c['low'] for c in candles[-5:])
    else:
        return max(c['high'] for c in candles[-5:])

def detect_support_resistance(symbol, direction):
    """
    Detect TP zone using recent S/R
    - Uses H1 last 10-bar highs/lows
    """
    candles = get_candles(symbol, mt5.TIMEFRAME_H1, 50)
    if not candles:
        return None

    highs = [c['high'] for c in candles]
    lows = [c['low'] for c in candles]

    return max(highs[-10:]) if direction == "UP" else min(lows[-10:])

def get_volatility(symbol, period=14, timeframe=mt5.TIMEFRAME_H1):
    """
    Estimate volatility using ATR-like logic:
    - Calculates average high-low range over `period` candles
    """
    candles = get_candles(symbol, timeframe, period + 1)
    if len(candles) < period:
        return 0

    ranges = [c['high'] - c['low'] for c in candles[-period:]]
    return round(mean(ranges), 5)
