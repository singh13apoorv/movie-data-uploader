from typing import Any, Dict

from mongo import MongoConnect


def create_test_document():
    """
    Summary: Create and insert a test movie document into MongoDB.
    """
    mongo = MongoConnect()

    # Manually create the document with the format from the CSV
    document: Dict[str, Any] = {
        "show_id": "119",  # Show ID as string
        "type": "Movie",  # Type of content (e.g., movie, show)
        "title": "Gurgaon",  # Title of the movie
        "director": "Shanker Raman",  # Director of the movie
        "cast": [
            "Akshay Oberoi",
            "Pankaj Tripathi",
            "Ragini Khanna",
            "Aamir Bashir",
            "Shalini Vatsa",
            "Ashish Verma",
        ],  # List of cast members
        "country": "India",  # Country of origin
        "date_added": "September 2, 2021",  # Date when it was added
        "release_year": 2017,  # Release year as integer
        "rating": "TV-14",  # Rating of the movie
        "duration": "106 min",  # Duration of the movie
        "listed_in": [
            "Dramas",
            "International Movies",
            "Thrillers",
        ],  # List of genres or collections
        "description": "When the daughter of a wealthy family returns from college, she gets a frosty welcome from her brother, who has problems – and plans – of his own.",  # Description of the movie
    }

    # Insert the document into MongoDB
    result = mongo.insert_document("movies", document)
    print(f"Inserted document with ID: {result}")

    mongo.close_connection()


# Call the function to insert the test document
create_test_document()
