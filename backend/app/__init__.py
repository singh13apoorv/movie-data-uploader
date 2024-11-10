from celery import Celery
from flask import Flask
from flask_pymongo import pymongo

from backend.app.mongo import MongoConnect

# Initialize Flask app
app = Flask(__name__)

# Configure MongoDB (MongoConnect should handle your MongoDB connection)
mongo = MongoConnect()


# Celery configuration
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
    )
    celery.conf.update(app.config)
    return celery


# Celery configuration (you can set these values in the app config)
app.config.update(
    CELERY_BROKER_URL="redis://localhost:6379/0",  # Redis as the message broker
    CELERY_RESULT_BACKEND="redis://localhost:6379/0",  # Store task results in Redis
)

# Initialize Celery
celery = make_celery(app)
