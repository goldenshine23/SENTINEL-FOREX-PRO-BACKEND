import time
import logging
from datetime import datetime, timezone

import MetaTrader5 as mt5

from backend.mt5_manager import MT5Manager
from backend.strategy import decide_trade
from backend.ai_memory import AIMemory
from backend.news_sentiment import get_news_sentiment, is_strong_news_event
from backend.journal import TradeJournal
from backend.risk_manager import calculate_risk_percent, calculate_lot
from backend.telegram_alerts import send_telegram_message
from backend.trade_filter import is_spread_acceptable
from backend.watchdog import check_mt5_health
import backend.bot_runner as bot_runner
from backend.config import MAX_TRADES_AT_ONCE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

BASE_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD",
    "AUDUSD", "NZDUSD", "XAUUSD", "USOIL", "US30",
    "NAS100", "BTCUSD", "GBPJPY", "EURJPY", "AUDJPY"
]

def resolve_symbols():
    """Dynamically detect available MT5 symbols based on BASE_SYMBOLS."""
    resolved = []
    if mt5.initialize():
        try:
            all_symbols = mt5.symbols_get()
            for base in BASE_SYMBOLS:
                match = next((s.name for s in all_symbols if s.name.startswith(base)), None)
                if match:
                    resolved.append(match)
        finally:
            mt5.shutdown()
    return resolved

def main_loop(user_email):
    mt5_api = MT5Manager()
    ai_memory = AIMemory()
    journal = TradeJournal()
    last_export_day = None

    if not mt5_api.connect():
        logging.error(f"[{user_email}] ❌ Failed to connect to MT5.")
        send_telegram_message(f"[{user_email}] ❌ Failed to connect to MT5.")
        return

    symbols_to_trade = resolve_symbols()
    if not symbols_to_trade:
        logging.error(f"[{user_email}] ❌ No valid symbols found.")
        send_telegram_message(f"[{user_email}] ❌ No valid symbols found.")
        return

    logging.info(f"[{user_email}] ✅ Symbols: {symbols_to_trade}")
    send_telegram_message(f"[{user_email}] ✅ MT5 Bot started. Symbols: {', '.join(symbols_to_trade)}")

    try:
        while bot_runner.bot_states.get(user_email, False):
            now = datetime.now(timezone.utc)

            # 🗓 Export daily report at 22:00 UTC
            if now.hour == 22 and (last_export_day is None or now.date() != last_export_day):
                report_path = journal.export_daily_report()
                logging.info(f"[{user_email}] 📄 Report exported: {report_path}")
                send_telegram_message(f"[{user_email}] 📄 Daily Report:\n{report_path}")
                last_export_day = now.date()

            # 🩺 MT5 health check
            if not check_mt5_health():
                logging.warning(f"[{user_email}] ⚠️ MT5 health check failed.")
                send_telegram_message(f"[{user_email}] ⚠️ Health check failed. Retrying...")
                time.sleep(5)
                continue

            open_positions = mt5.positions_get()
            if open_positions and len(open_positions) >= MAX_TRADES_AT_ONCE:
                logging.info(f"[{user_email}] ⏳ Max trade limit reached. Waiting...")
                time.sleep(3)
                continue

            candidates = []

            for symbol in symbols_to_trade:
                if not mt5.symbol_select(symbol, True):
                    continue
                if mt5_api.has_open_position(symbol):
                    continue
                if is_strong_news_event(symbol):
                    continue
                if not is_spread_acceptable(symbol):
                    continue

                sentiment = get_news_sentiment(symbol)
                strategy_feedback = ai_memory.update_strategy(symbol)
                trade = decide_trade(symbol, sentiment, strategy_feedback)

                if trade:
                    reward = abs(trade['tp'] - trade['entry_price'])
                    candidates.append((symbol, trade, strategy_feedback, reward))

            if candidates:
                symbol, trade, strategy_feedback, _ = max(candidates, key=lambda x: x[3])
                account_info = mt5.account_info()
                symbol_info = mt5.symbol_info(symbol)
                risk_percent = calculate_risk_percent(account_info.balance, strategy_feedback)
                trade["lot"] = calculate_lot(symbol_info, account_info.balance, risk_percent)

                logging.info(f"[{user_email}] 🚨 Attempting trade on {symbol}...")
                success = mt5_api.place_order(
                    symbol=symbol,
                    lot=trade['lot'],
                    order_type=trade['type'],
                    price=trade['entry_price'],
                    sl=trade['sl'],
                    tp=trade['tp']
                )

                if success:
                    journal.log_trade(
                        symbol=symbol,
                        entry_price=trade['entry_price'],
                        exit_price=None,
                        profit=None,
                        direction=trade['type'].upper()
                    )
                    send_telegram_message(
                        f"✅ Trade Executed for {user_email}\n"
                        f"Symbol: {symbol}\nType: {trade['type'].upper()}\nLot: {trade['lot']}\n"
                        f"Entry: {trade['entry_price']}\nSL: {trade['sl']} | TP: {trade['tp']}"
                    )
                else:
                    logging.warning(f"[{user_email}] ❌ Failed to place trade on {symbol}")
                    send_telegram_message(f"[{user_email}] ❌ Trade failed on {symbol}")
            else:
                logging.debug(f"[{user_email}] 🔍 No valid trade setup right now.")

            time.sleep(1)

    except Exception as e:
        logging.exception(f"[{user_email}] ❗ Crash occurred:")
        send_telegram_message(f"[{user_email}] ❗ Bot Error: {e}")

    finally:
        mt5_api.disconnect()
        send_telegram_message(f"[{user_email}] 🔌 MT5 Bot stopped.")
if __name__ == "__main__":
    user_email = "chinedudazi@gmail.com"  # ✅ Or dynamically load
    bot_runner.bot_states[user_email] = True
    main_loop(user_email)
