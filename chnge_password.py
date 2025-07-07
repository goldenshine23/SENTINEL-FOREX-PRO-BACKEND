from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from bot.auth import load_users, save_users, is_strong_password
from backend.config import TELEGRAM_BOT_TOKEN
import requests

change_password_bp = Blueprint("change_password", __name__)

@change_password_bp.route("/change-password", methods=["POST"])
def change_password():
    # Ensure user is logged in
    email = session.get("user_email")
    if not email:
        return jsonify({"message": "❌ Unauthorized. Please log in."}), 401

    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    users = load_users()
    user = users.get(email)

    if not user:
        return jsonify({"message": "❌ User not found."}), 404

    if not check_password_hash(user["password"], old_password):
        return jsonify({"message": "❌ Old password is incorrect."}), 400

    if not is_strong_password(new_password):
        return jsonify({"message": "❌ Weak password. Must contain 6+ letters, 1 number, and 1 special character."}), 400

    # Update password
    user["password"] = generate_password_hash(new_password)
    save_users(users)

    # ✅ Send Telegram confirmation
    chat_id = user.get("chat_id")
    if TELEGRAM_BOT_TOKEN and chat_id:
        message = "🔐 Your password was successfully changed."
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        try:
            requests.post(telegram_url, data=payload, timeout=10)
        except Exception as e:
            print(f"Telegram error: {e}")

    return jsonify({"message": "✅ Password changed successfully."}), 200
