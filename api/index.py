"""Vercel serverless function entry point."""
import os
import sys

# Add the parent directory to the Python path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask application for production
app = create_app('production')

# This is the WSGI application that Vercel will call
def application(environ, start_response):
    return app(environ, start_response)

# For compatibility, also export as 'app'
handler = app