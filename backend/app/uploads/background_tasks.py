import csv
import time  # Add this import for time.sleep

from celery import Celery

from backend.app import mongo
from backend.app.utils import parse_csv_row


@celery.task(bind=True)
def process_csv(self, filename, user_email):
    """
    Process the CSV file in the background.
    """
    try:
        total_rows = sum(1 for row in open(filename))  # Count total rows in CSV file
        processed_rows = 0

        with open(filename, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Parse the row using the helper function
                movie_data = parse_csv_row(row)

                if movie_data:
                    # Insert movie into MongoDB
                    mongo.insert_document("movies", movie_data)

                    processed_rows += 1
                    # Update the progress in the database
                    progress = {
                        "user_email": user_email,
                        "total_rows": total_rows,
                        "processed_rows": processed_rows,
                    }
                    mongo.update_document(
                        "uploads_progress",
                        {"user_email": user_email},
                        {"$set": progress},
                        upsert=True,
                    )

                # Simulate processing delay (optional)
                time.sleep(0.1)

        return {
            "status": "Completed",
            "processed_rows": processed_rows,
            "total_rows": total_rows,
        }

    except Exception as e:
        return {"status": "Failed", "error": str(e)}
