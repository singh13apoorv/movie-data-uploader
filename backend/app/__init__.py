from flask import Flask
from flask_pymongo import PyMongo

# Initialize the Flask app
app = Flask(__name__)

# Configure your MongoDB connection string (make sure it's in the config)
app.config["MONGO_URI"] = (
    "mongodb+srv://singh13apoorv:XETTcALhmWfzBXIx@cluster0.qsk4j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your Mongo URI
)

# Initialize PyMongo with the Flask app
mongo = PyMongo(app)

# Now you can use mongo.db in your other modules for database access
