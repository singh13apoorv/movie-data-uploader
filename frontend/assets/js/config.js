const config = {
  API_URL: "http://localhost:5000", // Base URL of your backend
  AUTH_API: {
    LOGIN: "/auth/login",
    SIGNUP: "/auth/signup",
  },
  UPLOAD_API: {
    CSV_UPLOAD: "/upload/upload_csv", // Correct route for CSV upload
    STATUS: "/upload/upload_progress", // Correct route for upload progress
  },
  MOVIE_API: {
    GET_MOVIES: "/movies/", // Get movies endpoint with pagination
  },
};
