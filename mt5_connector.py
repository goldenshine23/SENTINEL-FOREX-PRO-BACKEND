import threading
import time
import logging

# Adjust import based on your folder structure
from .mt5_manager import MT5Manager  # If inside `bot/`

# ✅ Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# ✅ Track running bots globally
running_bots = {}  # user_id -> UserBotRunner instance

# ----------------------------------------
# 🧠 UserBotRunner: Handles one user's MT5 bot
# ----------------------------------------
class UserBotRunner:
    def __init__(self, user_id, config):
        self.user_id = user_id
        self.config = config or {}
        self.manager = MT5Manager()
        self.thread = None
        self.running = False

    def start(self):
        if self.running:
            logging.warning(f"[{self.user_id}] Bot already running.")
            return
        self.running = True
        self.thread = threading.Thread(target=self.run_bot, daemon=True)
        self.thread.start()
        logging.info(f"[{self.user_id}] Bot thread started.")

    def stop(self):
        self.running = False
        self.manager.disconnect()
        logging.info(f"[{self.user_id}] Bot stopped and MT5 disconnected.")

    def run_bot(self):
        if not self.manager.connect():
            logging.error(f"[{self.user_id}] Failed to connect to MT5.")
            return

        logging.info(f"[{self.user_id}] Bot connected and running.")

        while self.running:
            try:
                for symbol in self.config.get("symbols", []):
                    if self.manager.has_open_position(symbol):
                        continue

                    price = self.manager.get_current_price(symbol, "buy")
                    if price:
                        self.manager.place_order(
                            symbol=symbol,
                            lot=0.01,
                            order_type="buy",
                            price=price,
                            sl=0.0,
                            tp=0.0
                        )

                time.sleep(10)

            except Exception as e:
                logging.error(f"[{self.user_id}] Bot loop error: {e}")
                self.running = False
                break

# ----------------------------------------
# 🔌 Public API for GUI / Controller
# ----------------------------------------

def start_user_bot(user_id, config):
    if user_id in running_bots:
        logging.warning(f"[{user_id}] Bot already running.")
        return False
    bot_runner = UserBotRunner(user_id, config)
    running_bots[user_id] = bot_runner
    bot_runner.start()
    return True

def stop_user_bot(user_id):
    if user_id not in running_bots:
        logging.warning(f"[{user_id}] No bot to stop.")
        return False
    running_bots[user_id].stop()
    del running_bots[user_id]
    return True

def get_bot_status(user_id):
    bot = running_bots.get(user_id)
    return bot.running if bot else False
