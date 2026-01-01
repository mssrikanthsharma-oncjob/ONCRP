"""Vercel-compatible Flask application entry point."""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask app
from app import create_app

# Create app instance
app = create_app('production')