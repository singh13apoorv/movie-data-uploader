import logging

from app.auth.utils import token_required
from flask import Blueprint, g, jsonify, request
from flask_cors import cross_origin

movie_bp = Blueprint("movie", __name__)
logging.basicConfig(level=logging.INFO)

from bson import ObjectId


# Helper function to convert ObjectId to string
def convert_objectid(obj):
    """Recursively converts ObjectId to string in dictionaries and lists."""
    if isinstance(obj, ObjectId):
        return str(obj)  # Convert ObjectId to string
    elif isinstance(obj, dict):
        return {key: convert_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    return obj


# Route for listing movies with pagination and sorting
@movie_bp.route("/movie_dashboard", methods=["OPTIONS", "GET"])
@cross_origin(origins=["http://localhost:3000", "http://127.0.0.1:3000"])
@token_required
def list_movies():
    """
    List movies with pagination and sorting.
    Query parameters:
    - page (int): The page number for pagination (default is 1)
    - per_page (int): The number of items per page (default is 20)
    - sort_by (str): The field by which to sort the movies (default is "date_added")
    - sort_order (str): The sorting order (default is "asc")
    """
    try:
        # Fetch query parameters for pagination and sorting
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        sort_by = request.args.get(
            "sort_by", "date_added"
        )  # Default sorting by date_added
        sort_order = request.args.get(
            "sort_order", "asc"
        )  # Default sorting order is ascending

        # Log query parameters
        logging.info(
            f"Received parameters: page={page}, per_page={per_page}, sort_by={sort_by}, sort_order={sort_order}"
        )

        # Map the sorting fields to their corresponding MongoDB fields
        sort_fields = {
            "date_added": "date_added",  # Sort by the date the movie was added
            "release_date": "release_date",  # Sort by release date
            "duration": "duration",  # Sort by movie duration (e.g., in minutes)
        }

        # Ensure sort_by is a valid field
        if sort_by not in sort_fields:
            sort_by = "date_added"
            logging.warning(
                f"Invalid 'sort_by' parameter received: {sort_by}. Defaulting to 'date_added'."
            )

        # Determine the sort direction (ascending or descending)
        sort_direction = 1 if sort_order == "asc" else -1
        sort_criteria = [(sort_fields.get(sort_by, "date_added"), sort_direction)]

        # Log the sorting criteria
        logging.info(f"Sorting criteria: {sort_criteria}")

        # Calculate the skip value for pagination
        skip = (page - 1) * per_page
        logging.info(f"Pagination: skip={skip}, limit={per_page}")

        # Fetch movies from MongoDB with pagination and sorting
        movies = g.mongo.find_documents(
            "movies", query={}, sort=sort_criteria, skip=skip, limit=per_page
        )

        # Log number of movies fetched
        logging.info(f"Fetched {len(movies)} movies")

        # Get total count for pagination metadata
        total_movies = g.mongo.count_documents("movies", query={})
        total_pages = (total_movies // per_page) + (1 if total_movies % per_page else 0)

        # Log pagination metadata
        logging.info(f"Total movies: {total_movies}, Total pages: {total_pages}")

        # Convert ObjectId to string for all movies
        serialized_movies = [convert_objectid(movie) for movie in movies]

        return (
            jsonify(
                {
                    "movies": serialized_movies,
                    "pagination": {
                        "current_page": page,
                        "total_pages": total_pages,
                        "total_movies": total_movies,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Error in list_movies: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
