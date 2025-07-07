from .utils import log
import MetaTrader5 as mt5
from backend.config import MAX_STOPLOSS_PIPS
from .technicals import (
    detect_order_block,
    detect_support_resistance,
    confirm_candle_entry,
    is_market_ranging,
    get_trend_direction
)

def get_sl_tp_by_smc(symbol, direction, entry_price):
    """
    Determine Stop Loss and Take Profit based on SMC zones:
    - SL: Use recent Order Block or fallback to max SL
    - TP: Use opposite Support/Resistance
    """
    symbol_info = mt5.symbol_info(symbol)
    point = symbol_info.point if symbol_info and symbol_info.point else 0.0001

    # SL logic
    sl_zone = detect_order_block(symbol, direction)
    sl = sl_zone if sl_zone else (
        entry_price - MAX_STOPLOSS_PIPS * point if direction == "UP"
        else entry_price + MAX_STOPLOSS_PIPS * point
    )

    # TP logic
    tp_zone = detect_support_resistance(symbol, direction)
    tp = tp_zone if tp_zone else (
        entry_price + MAX_STOPLOSS_PIPS * 2 * point if direction == "UP"
        else entry_price - MAX_STOPLOSS_PIPS * 2 * point
    )

    return round(sl, 5), round(tp, 5)

def decide_trade(symbol, news_sentiment=None, strategy_feedback=None):
    """
    Main SMC Trade Decision Engine
    Applies market structure, sentiment, and candle logic
    """
    # 1️⃣ Market Structure Filter
    if is_market_ranging(symbol):
        log(f"⚠️ {symbol} is ranging. Skipping.")
        return None

    # 2️⃣ Trend Filter
    trend = get_trend_direction(symbol)
    if trend not in ["UP", "DOWN"]:
        log(f"⚠️ No trend direction detected for {symbol}. Skipping.")
        return None

    # 3️⃣ Sentiment Filter (optional override logic)
    if news_sentiment is not None:
        if news_sentiment < 0 and trend == "UP":
            log(f"⚠️ Bearish sentiment contradicts bullish trend on {symbol}. Skipping.")
            return None
        if news_sentiment > 0 and trend == "DOWN":
            log(f"⚠️ Bullish sentiment contradicts bearish trend on {symbol}. Skipping.")
            return None

    # 4️⃣ Entry Candle Confirmation
    if not confirm_candle_entry(symbol):
        log(f"⚠️ Entry candle not confirmed for {symbol}. Skipping.")
        return None

    # 5️⃣ Trade Construction
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        log(f"❌ No tick data for {symbol}. Skipping.")
        return None

    entry_price = tick.ask if trend == "UP" else tick.bid
    sl, tp = get_sl_tp_by_smc(symbol, trend, entry_price)

    # Risk management (can be improved with account data)
    lot_size = 0.01
    if strategy_feedback and strategy_feedback.get("risk_reduction"):
        lot_size = 0.01  # already conservative — placeholder for scaling

    decision = {
        "symbol": symbol,
        "type": "buy" if trend == "UP" else "sell",
        "entry_price": entry_price,
        "sl": sl,
        "tp": tp,
        "lot": lot_size
    }

    log(f"✅ SMC Trade Signal [{symbol}] | {decision['type'].upper()} @ {entry_price} | SL: {sl} | TP: {tp}")
    return decision
