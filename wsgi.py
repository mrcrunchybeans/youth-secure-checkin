"""
WSGI entry point for production deployments
"""
from app import app, ensure_db

# Initialize database on startup
ensure_db()

if __name__ == "__main__":
    app.run()
