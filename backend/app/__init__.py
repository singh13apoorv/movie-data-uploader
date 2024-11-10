from flask import Flask
from flask_pymongo import PyMongo

from backend.app.mongo import MongoConnect

# Initialize the Flask app
app = Flask(__name__)

# Configure your MongoDB connection string (make sure it's in the config)
mongo = MongoConnect()

# Now you can use mongo.db in your other modules for database access
