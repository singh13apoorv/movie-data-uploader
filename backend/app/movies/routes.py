import csv
import uuid
from datetime import datetime

from flask import Blueprint, g, jsonify, request

from app.auth.utils import token_required
from app.models import Movie, UploadStatus

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
    movies = g.mongo.find_documents(
        "movies", query={}, sort=sort_criteria, skip=skip, limit=per_page
    )

    # Get total count for pagination metadata
    total_movies = g.mongo.count_documents("movies", query={})
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


@movie_bp.route("/upload_csv", methods=["POST"])
@token_required
def upload_csv():
    file = g.files.get("file")
    if not file or not file.filename.endswith(".csv"):
        return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

    # Generate a unique task ID for this upload
    task_id = str(uuid.uuid4())

    # Initialize upload status with the task_id
    upload_status = UploadStatus(
        user_id=g.user.id,
        file_name=file.filename or "unknown",
        status="in_progress",
        progress=0,
        timestamp=datetime.now(),
        task_id=task_id,  # Store task ID in the database
    )
    g.mongo.insert_document(
        "upload_status", upload_status.to_dict()
    )  # Insert initial status

    # Process the CSV
    csv_reader = csv.DictReader(file.stream.decode("utf-8").splitlines())
    total_rows = sum(1 for _ in csv_reader)
    file.stream.seek(0)  # Reset file pointer
    movies, uploaded_rows = [], 0

    for row in csv_reader:
        movie = Movie.from_csv(row)
        movies.append(movie.to_dict())
        uploaded_rows += 1

        if uploaded_rows % 1000 == 0:  # Insert in batches
            g.mongo.insert_many_documents("movies", movies)
            movies.clear()

            # Update progress
            progress = (uploaded_rows / total_rows) * 100
            g.mongo.update_document(
                "upload_status",
                {"task_id": task_id},
                {"$set": {"progress": progress, "uploaded_rows": uploaded_rows}},
            )

    # Final insertion for remaining movies and update progress
    if movies:
        g.mongo.insert_many_documents("movies", movies)
    g.mongo.update_document(
        "upload_status",
        {"task_id": task_id},
        {"$set": {"status": "completed", "progress": 100}},
    )

    return jsonify({"message": "CSV upload started", "task_id": task_id}), 202


@movie_bp.route("/upload_progress/<task_id>", methods=["GET"])
@token_required
def upload_progress(task_id):
    # Retrieve upload status from MongoDB using the task_id
    upload_status = g.mongo.find_document("upload_status", {"task_id": task_id})

    if not upload_status:
        return jsonify({"error": "Upload task not found"}), 404

    return (
        jsonify(
            {
                "status": upload_status["status"],
                "progress": upload_status["progress"],
                "uploaded_rows": upload_status.get("uploaded_rows", 0),
                "file_name": upload_status["file_name"],
            }
        ),
        200,
    )
