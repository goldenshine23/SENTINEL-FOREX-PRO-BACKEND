import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === Core Bot Constants ===
MAGIC_NUMBER = 123456
MAX_TRADES_AT_ONCE = 1
MAX_STOPLOSS_PIPS = 30
MAX_SPREAD_PIPS = 3
MAX_LOT_SIZE = 1.0

# === Risk Tier System ===
RISK_TIERS = [
    {"balance_max": 100, "risk_percent": 0.10},
    {"balance_max": 1000, "risk_percent": 0.03},
    {"balance_max": float("inf"), "risk_percent": 0.02}
]

# === Risk Constants ===
RISK_SMALL_ACCOUNT = 0.1   # 10% risk for accounts < $100
RISK_LARGE_ACCOUNT = 0.02  # 2% risk for accounts >= $100

# === Secure Keys and API Tokens ===
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your-telegram-bot-token")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "fallback-api-key")

# === Admin and Founder ===
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123")
FOUNDER_EMAIL = os.getenv("FOUNDER_EMAIL", "chinedudazi@gmail.com")
FOUNDER_TELEGRAM_USERNAME = os.getenv("FOUNDER_TELEGRAM_USERNAME", "Chinedudazi")

# === Trading Symbols and Sessions ===
CRYPTO_SYMBOLS = ["BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD"]
ALLOW_WEEKEND_CRYPTO = True

TRADING_SESSIONS = {
    "London": {"start": 7, "end": 16},
    "NewYork": {"start": 13, "end": 22},
    "Asia": {"start": 23, "end": 6}
}

# === Flags ===
IGNORE_SPREAD_CHECK = os.getenv("IGNORE_SPREAD_CHECK", "false").strip().lower() == "true"

# === Debug Output (Optional) ===
if __name__ == "__main__":
    print("🔑 SECRET_KEY:", SECRET_KEY)
    print("📨 TELEGRAM_BOT_TOKEN:", TELEGRAM_BOT_TOKEN)
    print("📊 FINNHUB_API_KEY:", FINNHUB_API_KEY)
    print("👤 ADMIN_EMAIL:", ADMIN_EMAIL)
    print("🔐 ADMIN_PASSWORD:", ADMIN_PASSWORD)
    print("👑 FOUNDER_EMAIL:", FOUNDER_EMAIL)
    print("💬 FOUNDER_TELEGRAM_USERNAME:", FOUNDER_TELEGRAM_USERNAME)
    print("⚙️ IGNORE_SPREAD_CHECK:", IGNORE_SPREAD_CHECK)
