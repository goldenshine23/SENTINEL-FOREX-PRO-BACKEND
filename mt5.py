import MetaTrader5 as mt5

def connect_mt5(login=None, password=None, server=None):
    """
    Connects to MetaTrader 5 terminal using given credentials.
    Returns (True, None) on success or (False, error) on failure.
    """
    try:
        if login is not None:
            login = int(login)  # MT5 API requires login as integer
        connected = mt5.initialize(login=login, password=password, server=server)
        if not connected:
            return False, mt5.last_error()
        return True, None
    except Exception as e:
        return False, str(e)

def disconnect_mt5():
    """
    Gracefully disconnects from MetaTrader 5 terminal.
    """
    try:
        return mt5.shutdown()
    except Exception:
        return False

def get_account_info():
    """
    Returns account info dictionary or None if not connected.
    Ensures a connection before querying.
    """
    try:
        if not mt5.initialize():
            return None
        info = mt5.account_info()
        mt5.shutdown()
        return info
    except Exception:
        return None
