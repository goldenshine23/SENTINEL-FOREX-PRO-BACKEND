import json
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

# File that stores user data
USERS_FILE = "users.json"

def load_users():
    """Load user data from JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    """Save user data to JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def is_strong_password(password):
    """
    Validate password strength:
    - At least 6 characters
    - At least one letter (a-z or A-Z)
    - At least one digit
    - At least one special character
    - At least one uppercase letter
    """
    return (
        len(password) >= 6 and
        re.search(r"[A-Z]", password) and
        re.search(r"\d", password) and
        re.search(r"[^a-zA-Z0-9]", password)
    )

def register_user(email, password, telegram_username):
    """
    Register a new user securely.
    Returns (True, message) or (False, error)
    """
    users = load_users()

    if email in users:
        return False, "User already exists."

    if not is_strong_password(password):
        return False, "Password is not strong enough. Must include an uppercase letter, number, and special character."

    users[email] = {
        "password": generate_password_hash(password),
        "approved": False,
        "telegram_username": telegram_username
    }

    save_users(users)
    return True, "Registration successful. Awaiting admin approval."

def validate_user(email, password):
    """
    Validate login credentials.
    Returns:
      - 'valid'
      - 'wrong_password'
      - 'not_approved'
      - 'unregistered'
    """
    users = load_users()

    if email not in users:
        return "unregistered"

    user = users[email]

    if not user.get("approved", False):
        return "not_approved"

    if not check_password_hash(user["password"], password):
        return "wrong_password"

    return "valid"

def change_user_password(email, old_password, new_password):
    """
    Change a user's password securely.
    Verifies old password and validates new one.
    """
    users = load_users()

    if email not in users:
        return False, "User not found."

    user = users[email]

    if not check_password_hash(user["password"], old_password):
        return False, "Old password is incorrect."

    if not is_strong_password(new_password):
        return False, "New password is not strong enough. Must include an uppercase letter, number, and special character."

    user["password"] = generate_password_hash(new_password)
    save_users(users)
    return True, "Password updated successfully."

def approve_user(email):
    """
    Admin approves a registered user.
    """
    users = load_users()

    if email not in users:
        return False, "User not found."

    users[email]["approved"] = True
    save_users(users)
    return True, f"User {email} approved successfully."
