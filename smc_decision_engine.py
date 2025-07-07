import MetaTrader5 as mt5
from config import MAX_STOPLOSS_PIPS
from utils import log

from technicals import (
    detect_order_block,
    detect_support_resistance,
    confirm_candle_entry,
    is_market_ranging,
    get_trend_direction,
    get_volatility  # ✅ Make sure this function exists in your technicals
)

def get_sl_tp_by_smc(symbol, direction, entry_price):
    symbol_info = mt5.symbol_info(symbol)
    point = symbol_info.point if symbol_info and symbol_info.point else 0.0001

    sl_zone = detect_order_block(symbol, direction)
    sl = sl_zone if sl_zone else (
        entry_price - MAX_STOPLOSS_PIPS * point if direction == "UP"
        else entry_price + MAX_STOPLOSS_PIPS * point
    )

    tp_zone = detect_support_resistance(symbol, direction)
    tp = tp_zone if tp_zone else (
        entry_price + MAX_STOPLOSS_PIPS * 2 * point if direction == "UP"
        else entry_price - MAX_STOPLOSS_PIPS * 2 * point
    )

    return round(sl, 5), round(tp, 5)

def decide_trade(symbol, news_sentiment=None, strategy_feedback=None):
    log(f"🔍 Scanning {symbol}...")

    if is_market_ranging(symbol):
        log(f"⚠️ {symbol} is ranging. Skipping.")
        return None

    trend = get_trend_direction(symbol)
    if trend not in ["UP", "DOWN"]:
        log(f"⚠️ No clear trend on {symbol}. Skipping.")
        return None

    if news_sentiment is not None:
        if (news_sentiment < 0 and trend == "UP") or (news_sentiment > 0 and trend == "DOWN"):
            log(f"⚠️ Sentiment contradicts trend on {symbol}. Skipping.")
            return None

    if not confirm_candle_entry(symbol):
        log(f"⚠️ No entry candle confirmed for {symbol}. Skipping.")
        return None

    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        log(f"❌ No tick data for {symbol}.")
        return None

    entry_price = tick.ask if trend == "UP" else tick.bid
    sl, tp = get_sl_tp_by_smc(symbol, trend, entry_price)

    lot_size = 0.01
    if strategy_feedback and strategy_feedback.get("risk_reduction"):
        lot_size = 0.01

    # ✅ Scoring logic
    base_score = abs(tp - sl)
    score = base_score

    # 🔸 Add Volatility Factor (scaled)
    volatility = get_volatility(symbol)
    if volatility:
        score += volatility * 0.5  # Weight volatility moderately

    # 🔸 News Sentiment Boost
    if news_sentiment is not None and (
        (trend == "UP" and news_sentiment > 0) or (trend == "DOWN" and news_sentiment < 0)
    ):
        score += abs(news_sentiment) * 0.3

    # 🔸 Order Block Confidence
    if detect_order_block(symbol, trend):
        score += 0.2

    # 🔸 Trend Strength Bonus
    if strategy_feedback:
        trend_strength = strategy_feedback.get("trend_strength", 0)
        score += trend_strength * 0.4

    decision = {
        "symbol": symbol,
        "type": "buy" if trend == "UP" else "sell",
        "entry_price": entry_price,
        "sl": sl,
        "tp": tp,
        "lot": lot_size,
        "score": round(score, 5)
    }

    log(f"✅ Signal for {symbol} → {decision['type'].upper()} @ {entry_price} | "
        f"SL: {sl} | TP: {tp} | Score: {decision['score']}")
    return decision
