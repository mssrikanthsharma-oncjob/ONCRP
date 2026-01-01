# ONC REALTY PARTNERS Booking System

A Python Flask-based web application for managing real estate bookings with role-based authentication and analytics dashboard.

## Project Structure

```
├── app/                    # Main application package
│   ├── auth/              # Authentication module
│   ├── booking/           # Booking management module
│   ├── analytics/         # Analytics and reporting module
│   ├── models/            # Database models
│   ├── config.py          # Application configuration
│   └── __init__.py        # Application factory
├── tests/                 # Test package
├── venv/                  # Virtual environment
├── run.py                 # Application entry point
└── requirements.txt       # Python dependencies
```

## Setup Instructions

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

## API Endpoints

- `GET /api/health` - Health check endpoint

## Configuration

The application supports different configurations:
- `development` - Debug mode enabled
- `production` - Production settings
- `testing` - In-memory database for testing

Environment variables can be set in a `.env` file (see `.env.example`).

## Technologies Used

- **Backend**: Flask, SQLAlchemy, PyJWT
- **Database**: SQLite (development), configurable for production
- **Testing**: pytest, hypothesis (property-based testing)
- **CORS**: flask-cors for cross-origin requests# ONCRP
