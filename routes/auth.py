from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from models.user import User
from utils.security import validate_password_strength, hash_password
from user_utils import (
    register_user,
    validate_user,
    approve_user
)

auth = Blueprint("auth", __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    telegram = data.get("telegram_username")

    if not email or not password or not telegram:
        return jsonify({"message": "Missing fields"}), 400

    success, message = register_user(email, password, telegram)
    return jsonify({"message": message}), 201 if success else 400


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    status = validate_user(email, password)

    if status == "valid":
        token = create_access_token(identity=email)
        return jsonify({"token": token, "message": "Login successful"}), 200
    elif status == "not_approved":
        return jsonify({"message": "Account not approved yet"}), 403
    elif status == "wrong_password":
        return jsonify({"message": "Incorrect password"}), 401
    else:
        return jsonify({"message": "User not registered"}), 404


@auth.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_email = get_jwt_identity()
    data = request.get_json()

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'message': 'Missing password fields'}), 400

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not check_password_hash(user.password, old_password):
        return jsonify({'message': 'Old password is incorrect'}), 401

    if not validate_password_strength(new_password):
        return jsonify({
            'message': 'Password must be at least 6 characters long, contain one uppercase letter, one number, and one special character.'
        }), 400

    user.password = hash_password(new_password)
    user.save()  # assumes your User model has a .save() method

    return jsonify({'message': 'Password updated successfully'}), 200


@auth.route('/approve-user', methods=['POST'])
@jwt_required()
def approve():
    current_user = get_jwt_identity()
    data = request.get_json()
    email_to_approve = data.get("email")

    if current_user != "chinedudazi@gmail.com":
        return jsonify({"message": "Only admin can approve users"}), 403

    success, message = approve_user(email_to_approve)
    return jsonify({"message": message}), 200 if success else 404
