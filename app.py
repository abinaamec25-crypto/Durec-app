"""
Main Flask Web Application Entry Point.
Anna University Regulation 2025 Data Structures Academic Project.
Title: Duplicate Record Detection Using Hashing Technique

Runs Flask web server on port 3000 to integrate with local browsers
and the Cloud Run nginx reverse proxy.
"""
import os
from flask import Flask
from config import HOST, PORT, DEBUG, BASE_DIR
from backend.routes import api_bp


def create_app():
    """Application factory for the Flask web application."""
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
    )

    # Register API blueprint
    app.register_blueprint(api_bp)

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 70)
    print(" ANNA UNIVERSITY REGULATION 2025 - DATA STRUCTURES PROJECT")
    print(" Duplicate Record Detection Using Hashing Technique")
    print(f" Web Server running at: http://localhost:{PORT}")
    print("=" * 70)
    app.run(host=HOST, port=PORT, debug=DEBUG)
