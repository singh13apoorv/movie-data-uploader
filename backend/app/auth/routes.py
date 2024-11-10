from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from backend.app import mongo
from backend.app.auth.utils import create_jwt_token, token_required
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
    mongo.insert_document("users", new_user.to_dict())  # Insert user into MongoDB

    return jsonify({"message": "User registered successfully"}), 201


# Login route
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Retrieve the user from MongoDB
    user = User.find_by_email(email)  # Ensure `find_by_email` is defined properly
    if user and user.check_password(password):
        token = create_jwt_token(user.email)  # Create token on successful login
        return jsonify({"token": token}), 200

    return jsonify({"message": "Invalid credentials"}), 401


@auth_bp.route("/movies", methods=["GET"])
@token_required  # Protect this route with authentication
def list_movies():
    # Access the authenticated user's email from g
    user_email = g.current_user_email
    user = User.find_by_email(user_email)

    if user:
        # Assuming you have a method to fetch movies uploaded by the user
        user_movies = mongo.find_documents("movies", {"user_email": user_email})
        return jsonify({"movies": user_movies}), 200

    return jsonify({"message": "User not found"}), 404
