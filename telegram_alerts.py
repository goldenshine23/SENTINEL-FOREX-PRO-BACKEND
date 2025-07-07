import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file (default fallback)
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str, chat_id: str = None):
    """
    Sends a Telegram message to a specific user's chat_id.
    If no chat_id is provided, it falls back to default CHAT_ID.
    Requires TELEGRAM_BOT_TOKEN to be set in .env
    """
    if not BOT_TOKEN:
        print("❌ Telegram bot token missing. Check .env file.")
        return

    chat_id = chat_id or DEFAULT_CHAT_ID  # fallback if not provided
    if not chat_id:
        print("❌ No chat_id provided or found. Cannot send message.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"  # optional: allows bold, italics, etc.
    }

    try:
        response = requests.post(url, data=payload, timeout=5)
        if not response.ok:
            print(f"⚠️ Telegram message failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {e}")
