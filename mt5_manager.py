import MetaTrader5 as mt5
import logging
from config import MAGIC_NUMBER  # ✅ Use relative or direct import based on your structure


class MT5Manager:
    def __init__(self):
        self.connected = False

    def connect(self, login=None, password=None, server=None):
        """
        Connect to MetaTrader 5 using optional credentials.
        """
        try:
            success = (
                mt5.initialize(login=int(login), password=password, server=server)
                if login else mt5.initialize()
            )

            if not success:
                logging.error(f"❌ MT5 initialization failed: {mt5.last_error()}")
                return False

            self.connected = True
            logging.info("🔗 Connected to MetaTrader 5.")
            return True

        except Exception as e:
            logging.exception(f"❌ Exception during MT5 connection: {e}")
            return False

    def disconnect(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logging.info("🔌 Disconnected from MT5.")

    def has_open_position(self, symbol):
        try:
            positions = mt5.positions_get(symbol=symbol)
            if positions is None:
                logging.warning(f"⚠️ Could not retrieve positions for {symbol} (Error: {mt5.last_error()})")
                return False
            return len(positions) > 0
        except Exception as e:
            logging.exception(f"❌ Error checking open positions for {symbol}: {e}")
            return False

    def get_current_price(self, symbol, order_type):
        try:
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                logging.error(f"❌ Failed to fetch price for {symbol}")
                return None
            return tick.ask if order_type.lower() == "buy" else tick.bid
        except Exception as e:
            logging.exception(f"❌ Error getting current price for {symbol}: {e}")
            return None

    def place_order(self, symbol, lot, order_type, price=None, sl=0.0, tp=0.0):
        try:
            if not mt5.symbol_select(symbol, True):
                logging.error(f"❌ Could not select symbol {symbol} in Market Watch.")
                return False

            if price is None:
                price = self.get_current_price(symbol, order_type)
                if price is None:
                    return False

            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logging.error(f"❌ Could not retrieve symbol info for {symbol}")
                return False

            filling_mode = symbol_info.filling_mode
            if filling_mode not in (
                mt5.ORDER_FILLING_IOC,
                mt5.ORDER_FILLING_RETURN,
                mt5.ORDER_FILLING_FOK
            ):
                logging.warning(f"⚠️ Unknown or unsupported filling mode for {symbol}: {filling_mode}")

            order = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": mt5.ORDER_TYPE_BUY if order_type.lower() == "buy" else mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": sl,
                "tp": tp,
                "magic": MAGIC_NUMBER,
                "deviation": 10,
                "type_filling": filling_mode,
                "type_time": mt5.ORDER_TIME_GTC,  # ✅ Always include time type
            }

            result = mt5.order_send(order)

            if result is None:
                logging.error("❌ order_send() returned None.")
                return False

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(
                    f"❌ Order failed: {symbol} [{order_type.upper()}] | RetCode: {result.retcode} | "
                    f"Msg: {result.comment} | Volume: {lot} | Price: {price}"
                )
                return False

            logging.info(
                f"✅ Order Placed: {symbol} {order_type.upper()} {lot} lots @ {price} "
                f"| SL: {sl} | TP: {tp} | Ticket: {result.order}"
            )
            return True

        except Exception as e:
            logging.exception(f"❌ Exception placing order on {symbol}: {e}")
            return False
