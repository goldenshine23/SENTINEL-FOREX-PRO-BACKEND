from backend.config import RISK_TIERS, MAX_LOT_SIZE

def calculate_risk_percent(balance, feedback=None):
    """
    Dynamically determines risk % based on balance tiers and optional AI feedback.
    """
    for tier in RISK_TIERS:
        if balance <= tier["balance_max"]:
            base_risk = tier["risk_percent"]
            if feedback and feedback.get("adjust_risk"):
                return max(base_risk / 2, 0.005)  # Reduce risk if needed
            return base_risk
    return 0.01  # Safe fallback

def calculate_lot(symbol_info, balance, risk_percent):
    """
    Calculates lot size with proper risk management and fallback.
    """
    try:
        base_lot = (risk_percent / 100) * balance / 1000
        safe_lot = max(base_lot, 0.01)
        return round(min(safe_lot, MAX_LOT_SIZE), 2)
    except Exception as e:
        from backend.telegram_alerts import send_telegram_message
        send_telegram_message(f"[ERROR] Lot calculation failed: {e}")
        return 0.01
