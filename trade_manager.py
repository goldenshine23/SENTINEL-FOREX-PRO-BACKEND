import MetaTrader5 as mt5
from utils import log
from config import MAX_LOT_SIZE, RISK_SMALL_ACCOUNT, RISK_LARGE_ACCOUNT


def get_open_position(symbol, positions):
    """Return the open position for the symbol, if any."""
    return next((pos for pos in positions if pos.symbol == symbol), None)


def calculate_lot_size(account_balance):
    """
    Dynamically calculate lot size based on account balance and risk rules.

    For small accounts (< $100), it returns a fixed 0.01.
    For large accounts (>= $200), it uses percentage-based risk.
    """
    if account_balance < 100:
        return 0.01
    elif account_balance >= 200:
        risk = RISK_LARGE_ACCOUNT
        lot = round(min((risk * account_balance) / 1000, MAX_LOT_SIZE), 2)
        return lot
    return 0.01  # fallback minimum


def scale_in_position(mt5_manager, position):
    """
    Attempts to scale into an existing position with 1.5x volume increase,
    capped by MAX_LOT_SIZE.
    """
    current_volume = position.volume
    new_volume = min(current_volume * 1.5, MAX_LOT_SIZE)
    add_volume = round(new_volume - current_volume, 2)

    if add_volume <= 0:
        log(f"🟡 No room to scale in further on {position.symbol}")
        return

    tick = mt5.symbol_info_tick(position.symbol)
    if not tick:
        log(f"❌ Tick fetch failed for {position.symbol}")
        return

    price = tick.ask if position.type == mt5.POSITION_TYPE_BUY else tick.bid
    order_type = "buy" if position.type == mt5.POSITION_TYPE_BUY else "sell"

    if not callable(getattr(mt5_manager, "place_order", None)):
        log(f"⚠️ mt5_manager has no callable method 'place_order'. Check your class implementation.")
        return

    success = mt5_manager.place_order(
        symbol=position.symbol,
        lot=add_volume,
        order_type=order_type,
        price=price,
        sl=0,
        tp=0,
    )

    if success:
        log(f"🔄 Scaled in {add_volume} lots on {position.symbol}")
    else:
        log(f"❌ Scale-in failed for {position.symbol}")


def manage_trailing_stop(position, entry_price, strategy_sr):
    """
    Applies a trailing stop when in profit:
    - For BUY: trail SL once price reaches +1%
    - For SELL: trail SL once price drops -1%
    """
    tick = mt5.symbol_info_tick(position.symbol)
    if not tick:
        log(f"⚠️ No tick data for {position.symbol}, cannot trail SL.")
        return

    current_price = tick.bid if position.type == mt5.POSITION_TYPE_SELL else tick.ask

    if position.type == mt5.POSITION_TYPE_BUY and current_price >= entry_price * 1.01:
        new_sl = max(entry_price, strategy_sr)
        update_stop_loss(position, new_sl)
    elif position.type == mt5.POSITION_TYPE_SELL and current_price <= entry_price * 0.99:
        new_sl = min(entry_price, strategy_sr)
        update_stop_loss(position, new_sl)


def update_stop_loss(position, new_sl):
    """
    Update the stop loss for a given MT5 position.
    """
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": position.ticket,
        "sl": new_sl,
        "tp": position.tp,
        "symbol": position.symbol,
        "magic": position.magic,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"✅ SL updated for {position.symbol} → SL = {new_sl}")
    else:
        log(f"❌ SL update failed on {position.symbol} → code {result.retcode} ({result.comment})")


def place_order(symbol, lot, order_type, price, sl, tp):
    """
    Sends a trade order to MT5 with the given parameters.
    """
    order_type_map = {
        "buy": mt5.ORDER_TYPE_BUY,
        "sell": mt5.ORDER_TYPE_SELL,
    }

    if order_type not in order_type_map:
        log(f"❌ Invalid order_type: {order_type}")
        return False

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type_map[order_type],
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "SentinelFXBot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"✅ Order placed: {order_type.upper()} {symbol} at {price}, SL={sl}, TP={tp}")
        return True
    else:
        log(f"❌ Order failed: code={result.retcode}, comment={result.comment}")
        return False
