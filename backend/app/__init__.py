from app.mongo import MongoConnect
from flask import Flask, g
from flask_cors import CORS


def create_app(config_name="development"):
    """Create and configure the Flask app."""

    # Initialize Flask app
    app = Flask(__name__, static_folder="frontend/assets")

    # Enable CORS for frontend and backend communication
    CORS(
        app,
        origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_headers="*",
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    @app.before_request
    def before_request():
        """Set up the MongoDB connection before each request."""
        g.mongo = MongoConnect()

    # Register after_request to close the MongoDB connection after each request
    @app.teardown_appcontext
    def close_mongo_connection(exception=None):
        """Close the MongoDB connection after each request."""
        if hasattr(g, "mongo"):
            g.mongo.close_connection()

    # Register blueprints (authentication, movies, etc.)
    from app.auth.routes import auth_bp
    from app.movies.routes import movie_bp
    from app.upload.routes import upload_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(movie_bp, url_prefix="/movies")
    app.register_blueprint(upload_bp, url_prefix="/upload")

    return app
