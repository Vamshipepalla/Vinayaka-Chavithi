"""WSGI entry point for production servers (Gunicorn, uWSGI, etc.)"""
from app import app

if __name__ == "__main__":
    app.run()
