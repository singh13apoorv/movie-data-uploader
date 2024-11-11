from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from app import mongo
from app.auth.utils import create_jwt_token, token_required
from app.models import User

auth_bp = Blueprint("auth", __name__)


# Signup route
@auth_bp.route("/signup", methods=["GET", "POST"])
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
    g.mongo.insert_document("users", new_user.to_dict())  # Insert user into MongoDB

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


# Movies list with pagination and sorting
@auth_bp.route("/movies", methods=["GET"])
@token_required
def list_movies():
    # Pagination and sorting logic
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    sort_by = request.args.get(
        "sort_by", "date_added"
    )  # Default to sorting by date_added
    sort_order = request.args.get("sort_order", "asc")  # Default to ascending order

    # Build sort criteria
    sort_direction = 1 if sort_order == "asc" else -1
    sort_criteria = [(sort_by, sort_direction)]

    # Fetch movies from MongoDB with pagination and sorting
    skip = (page - 1) * per_page
    movies = g.mongo.find_documents(
        "movies", query={}, sort=sort_criteria, skip=skip, limit=per_page
    )

    return jsonify([movie for movie in movies]), 200
