from app import create_app

# Create an app instance using the appropriate configuration
app = create_app("development")  # Use "production" or "testing" for other environments

if __name__ == "__main__":
    app.run(debug=True)  # Set to False for production
