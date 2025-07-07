
import MetaTrader5 as mt5

def check_mt5_health():
    if not mt5.initialize():
        print("MT5 initialization failed.")
        return False

    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to get account info.")
        return False

    if account_info.balance <= 0:
        print("Account balance is zero.")
        return False

    return True
