import datetime
from backend.config import CRYPTO_SYMBOLS, ALLOW_WEEKEND_CRYPTO, TRADING_SESSIONS

def is_weekend():
    """Check if current UTC day is Saturday or Sunday"""
    now = datetime.datetime.utcnow()
    return now.weekday() in (5, 6)

def is_crypto(symbol: str) -> bool:
    """Determine if the symbol is a crypto asset"""
    return symbol.upper() in CRYPTO_SYMBOLS

def should_trade(symbol: str) -> bool:
    """
    Decide if a symbol is tradable now based on:
    - Weekend rule for crypto
    - Active forex sessions for fiat pairs
    """
    if is_weekend():
        return is_crypto(symbol) and ALLOW_WEEKEND_CRYPTO
    return in_trade_sessions()

def current_gmt_time():
    """Return current UTC time"""
    return datetime.datetime.utcnow()

def in_trade_sessions() -> bool:
    """Check if current time falls within any configured session"""
    now = datetime.datetime.utcnow()
    hour = now.hour

    for session in TRADING_SESSIONS.values():
        start = session['start']
        end = session['end']
        if start < end:
            if start <= hour < end:
                return True
        else:
            # Handles sessions crossing midnight (e.g., 22–5)
            if hour >= start or hour < end:
                return True
    return False

def log(message: str):
    """Standardized logging to console with UTC timestamp"""
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
