import csv
import os

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from backend.app import mongo
from backend.app.auth.utils import token_required

UPLOAD_FOLDER = "path_to_your_upload_folder"  # Change this to your desired folder
ALLOWED_EXTENSIONS = {"csv"}


# Helper function to check if the file is allowed
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


upload_bp = Blueprint("upload", __name__)


# Route to handle the CSV upload
@upload_bp.route("/upload", methods=["POST"])
@token_required
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Start processing the CSV in a background task (optional)
        process_csv(filepath)

        return jsonify({"message": "File uploaded successfully"}), 200

    return jsonify({"error": "Invalid file format"}), 400
