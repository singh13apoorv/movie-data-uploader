import csv
import logging
import uuid
from datetime import datetime

from app.auth.utils import token_required
from app.models import Movie, UploadStatus
from flask import Blueprint, g, jsonify, request

upload_bp = Blueprint("upload", __name__)
logging.basicConfig(level=logging.INFO)


@upload_bp.route("/upload_csv", methods=["POST"])
@token_required
def upload_csv():
    file = request.files.get("file")

    # Check if a file was provided in the request
    if "file" not in request.files:
        logging.error("No file part in request")
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    # Check if no file is selected or file is not a valid CSV
    if file.filename == "":
        logging.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    if not file or not file.filename.endswith(".csv"):
        logging.error("Invalid file format. Expected a CSV file.")
        return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

    task_id = str(uuid.uuid4())

    # Initialize upload status with the task_id
    upload_status = UploadStatus(
        user_id=g.current_user_email,
        file_name=file.filename or "unknown",
        status="in_progress",
        progress=0,
        timestamp=datetime.now(),
        task_id=task_id,  # Store task ID in the database
    )

    try:
        # Insert initial upload status
        g.mongo.insert_document("upload_status", upload_status.to_dict())
    except Exception as e:
        logging.error(f"Error inserting upload status: {e}")
        return jsonify({"error": "Error initializing upload status."}), 500

    # Process the CSV
    try:
        csv_content = file.stream.read().decode("utf-8")
        csv_reader = csv.DictReader(csv_content.splitlines())
        logging.info(f"csv_reader: {csv_reader}")
        total_rows = sum(1 for _ in csv_reader)
        logging.info(f"Total rows: {total_rows}")
        file.stream.seek(0)  # Reset file pointer
        movies, uploaded_rows = [], 0

        csv_content = file.stream.read().decode("utf-8")
        csv_reader = csv.DictReader(csv_content.splitlines())

        for row in csv_reader:
            logging.info(f"A {row}")
            movie = Movie.from_csv(row)
            movies.append(movie.to_dict())
            uploaded_rows += 1

            if uploaded_rows % 1000 == 0:  # Insert in batches
                try:
                    g.mongo.insert_many_documents("movies", movies)
                    movies.clear()

                    # Update progress
                    progress = (uploaded_rows / total_rows) * 100
                    g.mongo.update_document(
                        "upload_status",
                        {"task_id": task_id},
                        {"progress": progress, "uploaded_rows": uploaded_rows},
                    )
                except Exception as e:
                    logging.error(f"Error inserting batch of movies: {e}")
                    return jsonify({"error": "Error inserting movies."}), 500

        # Final insertion for remaining movies and update progress
        if movies:
            try:
                g.mongo.insert_many_documents("movies", movies)
            except Exception as e:
                logging.error(f"Error inserting remaining movies: {e}")
                return jsonify({"error": "Error inserting remaining movies."}), 500

        g.mongo.update_document(
            "upload_status",
            {"task_id": task_id},
            {"status": "completed", "progress": 100},
        )
    except Exception as e:
        logging.error(f"Error processing CSV: {e}")
        return jsonify({"error": "Error processing CSV."}), 500

    return jsonify({"message": "CSV upload started", "task_id": task_id}), 202


@upload_bp.route("/upload_progress/<task_id>", methods=["GET"])
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
