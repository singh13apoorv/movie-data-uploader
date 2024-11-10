from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from backend.app import mongo
from backend.app.auth.utils import create_jwt_token
from backend.app.models import User

auth_bp = Blueprint("auth", __name__)


# Signup route
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Validate required fields
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Check if the user already exists
    existing_user = User.find_by_email(email)
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Hash the password and create a new user document
    hashed_password = generate_password_hash(password)
    new_user = User(
        email=email,
        password_hash=hashed_password,
        full_name=data.get("full_name"),
        date_joined=datetime.now(timezone.utc),  # Ensure we set the date_joined field
        is_active=True,
    )

    # Save the new user to MongoDB
    mongo.db.users.insert_one(new_user.to_dict())  # Insert user into MongoDB

    return jsonify({"message": "User registered successfully"}), 201


# Login route
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Retrieve the user from MongoDB
    user = User.find_by_email(email)  # Make sure `find_by_email` is defined
    if user and check_password_hash(user.password_hash, password):
        token = create_jwt_token(user.email)  # Create token on successful login
        return jsonify({"token": token}), 200
    return jsonify({"message": "Invalid credentials"}), 401
