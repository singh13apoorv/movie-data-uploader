from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """
    Summary: Data model for User.
    """

    email: EmailStr  # Unique identifier for the user
    password_hash: str  # Hashed password for secure authentication
    full_name: str  # Full name of the user
    date_joined: datetime  # Date when the user signed up
    last_login: Optional[datetime] = None  # Last login timestamp
    is_active: bool = True  # Whether the user account is active

    class Config:
        """
        Summary: Convert datetime to ISO format for MongoDB storage
        """

        json_encoders = {datetime: lambda v: v.isoformat()}

    def to_dict(self) -> dict:
        """Convert the User model to a dictionary."""
        return self.model_dump()


class Movie(BaseModel):
    """
    Summary: Data model for movie.
    """

    show_id: str  # Unique show ID
    movie_type: str  # Movie or TV Show
    title: str  # Title of the movie/show
    director: str  # Director(s) of the movie/show
    cast: List[str]  # List of cast members
    country: str  # Country of origin
    date_added: datetime  # Date when the movie was added to the system
    release_year: int  # Release year of the movie/show
    rating: str  # Rating (e.g., TV-14, R, PG)
    duration: str  # Duration (e.g., "106 min")
    listed_in: List[str]  # Genres or categories
    description: str  # Description of the movie/show

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def to_dict(self) -> dict:
        """Convert the Movie model instance to a dictionary."""
        return self.model_dump()

    @classmethod
    def from_csv(cls, row: dict) -> "Movie":
        """Create a Movie instance from a CSV row."""
        date_added = datetime.strptime(row["date_added"], "%B %d, %Y")
        return cls(
            show_id=row["show_id"],
            movie_type=row["type"],
            title=row["title"],
            director=row["director"],
            cast=[actor.strip() for actor in row["cast"].split(",")],
            country=row["country"],
            date_added=date_added,
            release_year=int(row["release_year"]),
            rating=row["rating"],
            duration=row["duration"],
            listed_in=[genre.strip() for genre in row["listed_in"].split(",")],
            description=row["description"],
        )


class UploadStatus(BaseModel):
    """
    Summary: Data model for upload status.
    """

    user_id: str  # ID of the user who uploaded the CSV
    file_name: str  # Name of the uploaded CSV file
    status: str  # Status of the upload ("in_progress", "completed", "failed")
    progress: float  # Progress percentage (0 to 100)
    timestamp: datetime  # Timestamp when the upload status was last updated
    total_rows: Optional[int] = 0  # Total number of rows in the CSV
    uploaded_rows: Optional[int] = 0  # Number of rows successfully uploaded

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def to_dict(self) -> dict:
        """Convert the UploadStatus model instance to a dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "UploadStatus":
        """Create an UploadStatus instance from a dictionary."""
        return cls(**data)


class MovieSortCriteria(BaseModel):
    """
    Summary: Data model for sorting criteria.
    """

    sort_by: Optional[str] = (
        "date_added"  # Field to sort by (e.g., date_added, release_year, duration)
    )
    sort_order: Optional[str] = "asc"  # Sort order (asc or desc)
    page_number: int = 1  # Current page number
    page_size: int = 20  # Number of items per page

    def to_dict(self) -> dict:
        """Convert the MovieSortCriteria model instance to a dictionary."""
        return self.model_dump()