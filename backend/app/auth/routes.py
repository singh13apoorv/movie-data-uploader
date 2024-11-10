from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from backend.app import mongo
from backend.app.auth.utils import create_jwt_token, token_required
from backend.app.models import Movie, User

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


@auth_bp.route("/movies", methods=["POST"])
@token_required
def create_movie():
    data = request.get_json()  # Expecting a JSON body with movie details

    # Validate required fields
    required_fields = [
        "show_id",
        "movie_type",
        "title",
        "director",
        "cast",
        "country",
        "date_added",
        "release_year",
        "rating",
        "duration",
        "listed_in",
        "description",
    ]
    if not all(field in data for field in required_fields):
        return (
            jsonify(
                {
                    "error": f"Missing one or more required fields: {', '.join(required_fields)}"
                }
            ),
            400,
        )

    # Create a new Movie instance
    new_movie = Movie(
        show_id=data["show_id"],
        movie_type=data["movie_type"],
        title=data["title"],
        director=data["director"],
        cast=data["cast"],
        country=data["country"],
        date_added=datetime.strptime(data["date_added"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        release_year=data["release_year"],
        rating=data["rating"],
        duration=data["duration"],
        listed_in=data["listed_in"],
        description=data["description"],
    )

    # Insert the new movie into MongoDB
    mongo.insert_document("movies", new_movie.to_dict())

    return jsonify({"message": "Movie created successfully"}), 201


@auth_bp.route("/movies", methods=["GET"])
@token_required
def get_movies():
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
    movies = mongo.find_documents(
        "movies", query={}, sort=sort_criteria, skip=skip, limit=per_page
    )

    return jsonify([movie for movie in movies]), 200


@auth_bp.route("/movies/<show_id>", methods=["GET"])
@token_required
def get_movie(show_id):
    # Fetch the movie from MongoDB
    movie_data = mongo.find_document("movies", {"show_id": show_id})

    if not movie_data:
        return jsonify({"error": "Movie not found"}), 404

    # Convert the fetched data into a Movie instance
    movie = Movie(**movie_data)  # This assumes mongo.find_document returns a dictionary

    return jsonify(movie.to_dict()), 200


@auth_bp.route("/movies/<show_id>", methods=["PUT"])
@token_required
def update_movie(show_id):
    data = request.get_json()

    # Find the movie in the database
    movie = mongo.find_document("movies", {"show_id": show_id})

    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    # Update the movie fields (replace this with the fields you need to update)
    updated_fields = {
        field: data[field] for field in data if field in Movie.__annotations__
    }
    mongo.update_document("movies", {"show_id": show_id}, {"$set": updated_fields})

    return jsonify({"message": "Movie updated successfully"}), 200


@auth_bp.route("/movies/<show_id>", methods=["DELETE"])
@token_required
def delete_movie(show_id):
    # Find the movie in the database
    movie = mongo.find_document("movies", {"show_id": show_id})

    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    # Delete the movie from MongoDB
    mongo.delete_document("movies", {"show_id": show_id})

    return jsonify({"message": "Movie deleted successfully"}), 200
