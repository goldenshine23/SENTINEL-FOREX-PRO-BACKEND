import threading
import time
import MetaTrader5 as mt5
from smc_decision_engine import decide_trade
from trade_manager import place_order

try:
    from log import log_user_event
    from config import (
        MAGIC_NUMBER,
        MAX_TRADES_AT_ONCE,
        MAX_STOPLOSS_PIPS,
        MAX_LOT_SIZE,
        RISK_TIERS
    )
except ImportError:
    from .log import log_user_event
    from backend.config import (
        MAGIC_NUMBER,
        MAX_TRADES_AT_ONCE,
        MAX_STOPLOSS_PIPS,
        MAX_LOT_SIZE,
        RISK_TIERS
    )

from smc_decision_engine import decide_trade
from trade_manager import place_order
from symbol_utils import SYMBOLS_TO_TRADE

bot_states = {}
user_threads = {}
stop_flags = {}

def get_risk_percent(balance):
    for tier in RISK_TIERS:
        if balance <= tier["balance_max"]:
            return tier["risk_percent"]
    return 0.02

def bot_loop(user_email):
    if not mt5.initialize():
        log_user_event(user_email, "❌ MT5 initialization failed.")
        return

    account_info = mt5.account_info()
    if account_info is None or account_info.balance <= 0:
        log_user_event(user_email, "❌ Invalid or zero account balance.")
        mt5.shutdown()
        return

    risk = get_risk_percent(account_info.balance)
    log_user_event(user_email, f"✅ Bot started on account {account_info.login} "
                               f"(Balance: {account_info.balance}, Risk: {risk * 100}%)")

    try:
        while not stop_flags.get(user_email, False):
            positions = mt5.positions_get()
            open_trade_count = len(positions) if positions else 0

            if open_trade_count >= MAX_TRADES_AT_ONCE:
                log_user_event(user_email, "🔒 Max trades reached. Skipping this cycle.")
                time.sleep(30)
                continue

            best_signal = None
            best_score = -float("inf")

            for symbol in SYMBOLS_TO_TRADE:
                signal = decide_trade(symbol)

                if signal:
                    score = signal.get("score", 1)  # use .get("score") or default to 1
                    if score > best_score:
                        best_signal = signal
                        best_score = score
                    log_user_event(user_email, f"📡 Signal for {symbol}: {signal}")
                else:
                    log_user_event(user_email, f"⏳ No valid setup for {symbol}")
                time.sleep(1)

            if best_signal:
                log_user_event(user_email, f"🎯 Best trade selected: {best_signal}")
                success = place_order(
                    symbol=best_signal["symbol"],
                    order_type=best_signal["type"],
                    price=best_signal["entry_price"],
                    sl=best_signal["sl"],
                    tp=best_signal["tp"],
                    lot=best_signal["lot"]
                )
                if success:
                    log_user_event(user_email, f"✅ Trade placed: {best_signal}")
                else:
                    log_user_event(user_email, f"❌ Failed to place trade for {best_signal['symbol']}")
            else:
                log_user_event(user_email, "🟡 No trade placed. No valid signal detected.")

            log_user_event(user_email, "🔁 Scan complete. Waiting before next scan...")
            time.sleep(30)

    except Exception as e:
        log_user_event(user_email, f"⚠️ Bot error: {e}")
    finally:
        try:
            mt5.shutdown()
        except Exception:
            pass
        log_user_event(user_email, "🛑 Bot stopped.")
        stop_flags[user_email] = False
        bot_states[user_email] = False

def start_bot_for_user(user_email):
    if user_email in user_threads and user_threads[user_email].is_alive():
        log_user_event(user_email, "⚠️ Bot is already running.")
        return False

    stop_flags[user_email] = False
    bot_states[user_email] = True
    t = threading.Thread(target=bot_loop, args=(user_email,), daemon=True)
    user_threads[user_email] = t
    t.start()
    return True

def stop_bot_for_user(user_email):
    if user_email in user_threads:
        stop_flags[user_email] = True
        log_user_event(user_email, "⛔ Stop requested. Bot will stop shortly.")
        return True
    return False

def get_open_trades(user_email=None):
    trades = []
    if not mt5.initialize():
        log_user_event(user_email or "System", "⚠️ Failed to initialize MT5 to fetch trades.")
        return trades

    positions = mt5.positions_get()
    if positions:
        for pos in positions:
            trades.append({
                "symbol": pos.symbol,
                "type": "BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL",
                "lot": pos.volume,
                "profit": round(pos.profit, 2)
            })

    mt5.shutdown()
    return trades

def start_bot():
    print("📈 Bot is running in standalone mode ✅")
    email = "admin@sentinel.com"
    start_bot_for_user(email)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("🛑 Bot interrupted manually. Exiting...")

if __name__ == "__main__":
    start_bot()
