from flask import Flask, g
from flask_pymongo import pymongo

from app.mongo import MongoConnect


def create_app(config_name="development"):
    """Create and configure the Flask app."""

    # Initialize Flask app
    app = Flask(__name__)

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

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(movie_bp, url_prefix="/movies")

    return app
