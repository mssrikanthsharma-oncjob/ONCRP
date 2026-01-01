"""Test basic Flask application setup."""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create test application."""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_app_creation():
    """Test that the Flask app can be created."""
    app = create_app('testing')
    assert app is not None
    assert app.config['TESTING'] is True


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'ONC REALTY PARTNERS' in data['message']


def test_cors_configuration(app):
    """Test CORS configuration."""
    assert 'http://localhost:3000' in app.config['CORS_ORIGINS']
    assert 'http://127.0.0.1:3000' in app.config['CORS_ORIGINS']


def test_json_configuration(app):
    """Test JSON handling configuration."""
    assert app.config['JSON_SORT_KEYS'] is False
    assert app.json.ensure_ascii is False