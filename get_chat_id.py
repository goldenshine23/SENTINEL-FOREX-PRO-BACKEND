import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve the token safely
token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment.")

# Construct the Telegram API URL
url = f"https://api.telegram.org/bot{token}/getUpdates"

# Send the GET request and handle response
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raise error for non-200 responses
    data = response.json()
    print(data)
except requests.exceptions.RequestException as e:
    print(f"Error communicating with Telegram API: {e}")
