import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional

import jwt
from flask import g, jsonify, request
from werkzeug.utils import secure_filename

from backend.app import app

# Secret key for encoding and decoding JWT tokens
SECRET_KEY = os.urandom(32).hex()


# Utility function to create a JWT token for authenticated users
def create_jwt_token(email: str) -> str:
    """
    Create a JWT token for the user.

    Args:
        email (str): The email of the user to encode into the token.

    Returns:
        str: A JWT token for the user.
    """
    expiration = datetime.now(timezone.utc) + timedelta(
        hours=1
    )  # Token expires in 1 hour
    payload = {"email": email, "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


# Utility function to verify JWT token (e.g., to protect routes)
def token_required(f):
    """
    A decorator to protect routes requiring authentication via JWT.

    Args:
        f: The route handler to wrap.

    Returns:
        Wrapped function with token validation.
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            # Decode the token using the secret key
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_email = payload["email"]
            g.current_user_email = current_user_email  # Store email in g
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        # Call the original function
        return f(*args, **kwargs)

    return decorator


# Utility function for handling CSV file uploads
def allowed_file(filename: str, allowed_extensions: Optional[list] = None) -> bool:
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename (str): The filename of the uploaded file.
        allowed_extensions (list, optional): A list of allowed file extensions. Defaults to ['csv'].

    Returns:
        bool: True if file extension is allowed, False otherwise.
    """
    if allowed_extensions is None:
        allowed_extensions = ["csv"]

    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_file(file, upload_folder: str) -> str:
    """
    Save the uploaded file to the server.

    Args:
        file: The uploaded file.
        upload_folder (str): The directory where the file will be saved.

    Returns:
        str: The path where the file is saved.
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return file_path
    else:
        raise ValueError("Invalid file type or file size")
