import MetaTrader5 as mt5

BASE_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
    "XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD", "US30", "NAS100", "SPX500",
    "GBPJPY", "EURJPY", "AUDJPY", "NZDJPY", "CADJPY", "CHFJPY", "EURGBP"
]

def detect_broker_symbols():
    """
    Detects tradable, visible symbols matching the common base pairs.
    Useful for adapting to brokers with suffixes like '.m', '.r', etc.
    """
    if not mt5.initialize():
        print(f"❌ MT5 initialization failed: {mt5.last_error()}")
        return []

    all_symbols = mt5.symbols_get()
    matched_symbols = []

    for base in BASE_SYMBOLS:
        for sym in all_symbols:
            if (
                sym.name.startswith(base)
                and sym.visible
                and sym.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL
            ):
                matched_symbols.append(sym.name)
                break  # Only pick one variation per base (e.g., 'EURUSD.m')

    mt5.shutdown()
    return matched_symbols
