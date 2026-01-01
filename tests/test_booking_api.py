"""Test booking API endpoints."""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Booking


@pytest.fixture
def app():
    """Create test application."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for testing."""
    # Login as admin user
    response = client.post('/api/auth/demo-login', 
                          json={'role': 'admin'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    token = data['data']['token']
    
    return {'Authorization': f'Bearer {token}'}


def test_create_booking(client, auth_headers):
    """Test creating a new booking."""
    booking_data = {
        'customer_name': 'John Doe',
        'contact_number': '1234567890',
        'project_name': 'Sunrise Apartments',
        'type': '2BHK',
        'area': 1200.5,
        'agreement_cost': 5000000.00,
        'amount': 4500000.00,
        'tax_gst': 450000.00,
        'timeline': (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    
    response = client.post('/api/bookings/', 
                          json=booking_data,
                          headers=auth_headers)
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Booking created successfully'
    assert data['booking']['customer_name'] == 'John Doe'
    assert data['booking']['project_name'] == 'Sunrise Apartments'


def test_get_bookings(client, auth_headers):
    """Test retrieving bookings."""
    response = client.get('/api/bookings/', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'bookings' in data
    assert 'pagination' in data


def test_search_bookings(client, auth_headers):
    """Test searching bookings."""
    response = client.get('/api/bookings/search?q=test', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'results' in data
    assert 'query' in data
    assert data['query'] == 'test'


def test_booking_stats(client, auth_headers):
    """Test getting booking statistics."""
    response = client.get('/api/bookings/stats', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_bookings' in data
    assert 'total_revenue' in data
    assert 'completion_rate' in data


def test_unauthorized_access(client):
    """Test that endpoints require authentication."""
    response = client.get('/api/bookings/')
    assert response.status_code == 401
    
    response = client.post('/api/bookings/', json={})
    assert response.status_code == 401


def test_create_booking_validation(client, auth_headers):
    """Test booking creation validation."""
    # Test missing required fields
    response = client.post('/api/bookings/', 
                          json={'customer_name': 'John'},  # Missing other required fields
                          headers=auth_headers)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Missing required fields' in data['error']
    
    # Test invalid timeline format
    booking_data = {
        'customer_name': 'John Doe',
        'contact_number': '1234567890',
        'project_name': 'Test Project',
        'type': '2BHK',
        'area': 1200,
        'agreement_cost': 5000000,
        'amount': 4500000,
        'timeline': 'invalid-date'
    }
    
    response = client.post('/api/bookings/', 
                          json=booking_data,
                          headers=auth_headers)
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid timeline format' in data['error']