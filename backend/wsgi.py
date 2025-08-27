# wsgi.py
# Import the Flask app instance from backend/app.py
from backend.app import app as application

# This "application" variable is what EB expects by default
if __name__ == "__main__":
    application.run()
