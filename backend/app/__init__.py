from flask import flask
from flask_pymongo import pymongo

from backend.app.mongo import MongoConnect

# initialize the flask app
app = flask(__name__)

# configure your mongodb connection string (make sure it's in the config)
mongo = MongoConnect()

# Now you can use mongo.db in your other modules for database access
