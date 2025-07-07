import MetaTrader5 as mt5

def check_mt5_health():
    """
    Returns True if MT5 is connected and has a positive balance.
    Ensures MT5 is always shut down to free memory.
    """
    try:
        if not mt5.initialize():
            return False

        account_info = mt5.account_info()
        if account_info is None or account_info.balance <= 0:
            return False

        return True
    finally:
        mt5.shutdown()
