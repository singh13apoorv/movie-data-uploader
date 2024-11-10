from flask import Blueprint, jsonify, request

from backend.app import mongo
from backend.app.auth.utils import token_required

movie_bp = Blueprint("movie", __name__)


# Route for listing movies with pagination and sorting
@movie_bp.route("/", methods=["GET"])
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
    # Fetch query parameters for pagination and sorting
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    sort_by = request.args.get("sort_by", "date_added")  # Default sorting by date_added
    sort_order = request.args.get(
        "sort_order", "asc"
    )  # Default sorting order is ascending

    # Map the sorting fields to their corresponding MongoDB fields
    sort_fields = {
        "date_added": "date_added",  # Sort by the date the movie was added
        "release_date": "release_date",  # Sort by release date
        "duration": "duration",  # Sort by movie duration (e.g., in minutes)
    }

    # Determine the sort direction (ascending or descending)
    sort_direction = 1 if sort_order == "asc" else -1
    sort_criteria = [(sort_fields.get(sort_by, "date_added"), sort_direction)]

    # Calculate the skip value for pagination
    skip = (page - 1) * per_page

    # Fetch movies from MongoDB with pagination and sorting
    movies = mongo.find_documents(
        "movies", query={}, sort=sort_criteria, skip=skip, limit=per_page
    )

    # Get total count for pagination metadata
    total_movies = mongo.count_documents("movies", query={})
    total_pages = (total_movies // per_page) + (1 if total_movies % per_page else 0)

    return (
        jsonify(
            {
                "movies": [movie for movie in movies],
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_movies": total_movies,
                },
            }
        ),
        200,
    )
