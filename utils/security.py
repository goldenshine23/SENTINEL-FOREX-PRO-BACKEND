import json
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

USERS_FILE = "users.json"

# Load users from JSON
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Save users to JSON
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Password strength checker
def is_strong_password(password):
    return (
        len(password) >= 6 and
        re.search(r"[a-zA-Z]", password) and
        re.search(r"\d", password) and
        re.search(r"[^\w\s]", password)
    )

# Register user with email, password and telegram username
def register_user(email, password, telegram_username):
    users = load_users()
    email = email.lower()

    if email in users:
        return False, "User already exists."

    if not is_strong_password(password):
        return False, "Password must be at least 6 characters, include a digit and special character."

    users[email] = {
        "password": generate_password_hash(password),
        "telegram_username": telegram_username.strip("@"),
        "approved": False,
        "is_admin": False,
        "chat_id": ""
    }

    save_users(users)
    return True, "Registration successful. Await admin approval."

# Validate login credentials
def validate_user(email, password):
    users = load_users()
    email = email.lower()

    if email not in users:
        return "unregistered"

    user = users[email]
    if not user.get("approved", False):
        return "not_approved"

    if not check_password_hash(user["password"], password):
        return "wrong_password"

    return "valid"

# Change password securely
def change_user_password(email, old_password, new_password):
    users = load_users()
    email = email.lower()

    if email not in users:
        return False, "User not found."

    user = users[email]

    if not check_password_hash(user["password"], old_password):
        return False, "Old password is incorrect."

    if not is_strong_password(new_password):
        return False, "New password is not strong enough."

    user["password"] = generate_password_hash(new_password)
    save_users(users)
    return True, "Password updated successfully."
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_token(email):
    """Generate a timed token for a user's email"""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt="reset")

def confirm_token(token, expiration=3600):
    """Confirm a timed token (default expires in 1 hour)"""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, salt="reset", max_age=expiration)
    except Exception:
        return None
