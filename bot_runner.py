import threading
import time
import MetaTrader5 as mt5

from .log import log_user_event  # ✅ Correct relative import

from backend.config import (
    MAGIC_NUMBER,
    MAX_TRADES_AT_ONCE,
    MAX_STOPLOSS_PIPS,
    MAX_LOT_SIZE,
    RISK_TIERS  # ✅ Use RISK_TIERS instead of removed constants
)

# ✅ Fix: Add bot_states so it can be accessed from main.py
bot_states = {}

# Dictionary to track running threads per user
user_threads = {}

# Optional stop flags for future graceful shutdowns
stop_flags = {}

def get_risk_percent(balance):
    """
    Dynamically determine risk % based on balance using tiers from config.
    """
    for tier in RISK_TIERS:
        if balance <= tier["balance_max"]:
            return tier["risk_percent"]
    return 0.02  # Fallback risk

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
            # ✅ TODO: Add real strategy logic here
            log_user_event(user_email, "🟢 Bot heartbeat - running.")
            time.sleep(10)
    except Exception as e:
        log_user_event(user_email, f"⚠️ Bot error: {e}")
    finally:
        mt5.shutdown()
        log_user_event(user_email, "🛑 Bot stopped.")
        stop_flags[user_email] = False
        bot_states[user_email] = False  # Update state when stopped

def start_bot_for_user(user_email):
    if user_email in user_threads and user_threads[user_email].is_alive():
        log_user_event(user_email, "⚠️ Bot is already running.")
        return False

    stop_flags[user_email] = False
    bot_states[user_email] = True  # ✅ Ensure state is tracked
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
