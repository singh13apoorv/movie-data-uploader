import csv
from datetime import datetime

from backend.app import mongo


# Helper function to parse the CSV and insert the data into MongoDB
def process_csv(filepath: str):
    with open(filepath, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Parse data
            movie_data = {
                "show_id": row["show_id"],
                "type": row["type"],
                "title": row["title"],
                "director": row["director"],
                "cast": row["cast"],
                "country": row["country"],
                "date_added": datetime.strptime(
                    row["date_added"], "%B %d, %Y"
                ),  # Adjust format as needed
                "release_year": int(row["release_year"]),
                "rating": row["rating"],
                "duration": int(row["duration"]),
                "listed_in": row["listed_in"],
                "description": row["description"],
            }

            # Insert movie into MongoDB
            mongo.insert_document("movies", movie_data)
