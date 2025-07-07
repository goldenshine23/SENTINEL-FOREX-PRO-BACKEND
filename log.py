import datetime
import os

LOG_DIR = "logs"

def log_user_event(user_email, message):
    """
    Write a user-specific log entry to a dedicated log file.
    """
    safe_email = user_email.replace("@", "_").replace(".", "_")
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    log_path = os.path.join(LOG_DIR, f"{safe_email}.log")
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def log(message):
    """
    General console log with timestamp.
    """
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{timestamp}] {message}")


def get_user_logs(email):
    """
    Retrieve logs for a specific user based on their email.
    """
    safe_email = email.replace("@", "_").replace(".", "_")
    log_path = os.path.join(LOG_DIR, f"{safe_email}.log")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            return f.readlines()
    return []
