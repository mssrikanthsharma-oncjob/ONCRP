"""Integration tests for booking management frontend functionality."""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Booking


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Check if demo users already exist, if not create them
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password='admin123', role='admin')
            db.session.add(admin_user)
        
        sales_user = User.query.filter_by(username='sales').first()
        if not sales_user:
            sales_user = User(username='sales', password='sales123', role='sales_person')
            db.session.add(sales_user)
        
        db.session.commit()
        
        yield app
        
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for admin user."""
    response = client.post('/api/auth/login', 
                          json={'username': 'admin', 'password': 'admin123'})
    data = json.loads(response.data)
    token = data['data']['token']
    return {'Authorization': f'Bearer {token}'}


def test_booking_crud_operations(client, auth_headers):
    """Test complete CRUD operations for bookings through API."""
    
    # Test CREATE booking
    booking_data = {
        'customer_name': 'John Doe',
        'contact_number': '9876543210',
        'project_name': 'Sunrise Apartments',
        'type': '2BHK',
        'area': 1200.5,
        'agreement_cost': 5000000.0,
        'amount': 4800000.0,
        'tax_gst': 240000.0,
        'timeline': (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    
    # Create booking
    response = client.post('/api/bookings/', 
                          json=booking_data, 
                          headers=auth_headers)
    assert response.status_code == 201
    
    created_booking = json.loads(response.data)['booking']
    booking_id = created_booking['id']
    
    # Verify booking was created with correct data
    assert created_booking['customer_name'] == 'John Doe'
    assert created_booking['project_name'] == 'Sunrise Apartments'
    assert created_booking['type'] == '2BHK'
    assert created_booking['area'] == 1200.5
    assert created_booking['status'] == 'active'
    
    # Test READ booking
    response = client.get(f'/api/bookings/{booking_id}', headers=auth_headers)
    assert response.status_code == 200
    
    retrieved_booking = json.loads(response.data)['booking']
    assert retrieved_booking['id'] == booking_id
    assert retrieved_booking['customer_name'] == 'John Doe'
    
    # Test UPDATE booking
    update_data = {
        'customer_name': 'John Smith',
        'amount': 5000000.0,
        'status': 'complete'
    }
    
    response = client.put(f'/api/bookings/{booking_id}', 
                         json=update_data, 
                         headers=auth_headers)
    assert response.status_code == 200
    
    updated_booking = json.loads(response.data)['booking']
    assert updated_booking['customer_name'] == 'John Smith'
    assert updated_booking['amount'] == 5000000.0
    assert updated_booking['status'] == 'complete'
    
    # Test DELETE booking (soft delete)
    response = client.delete(f'/api/bookings/{booking_id}', headers=auth_headers)
    assert response.status_code == 200
    
    deleted_booking = json.loads(response.data)['booking']
    assert deleted_booking['status'] == 'cancelled'


def test_booking_search_and_filter(client, auth_headers):
    """Test booking search and filtering functionality."""
    
    # Create multiple test bookings
    bookings_data = [
        {
            'customer_name': 'Alice Johnson',
            'contact_number': '9876543210',
            'project_name': 'Green Valley',
            'type': '3BHK',
            'area': 1500.0,
            'agreement_cost': 6000000.0,
            'amount': 5800000.0,
            'status': 'active',
            'timeline': (datetime.utcnow() + timedelta(days=30)).isoformat()
        },
        {
            'customer_name': 'Bob Wilson',
            'contact_number': '9876543211',
            'project_name': 'Blue Heights',
            'type': '2BHK',
            'area': 1200.0,
            'agreement_cost': 4500000.0,
            'amount': 4300000.0,
            'status': 'complete',
            'timeline': (datetime.utcnow() + timedelta(days=45)).isoformat()
        }
    ]
    
    # Create bookings
    for booking_data in bookings_data:
        response = client.post('/api/bookings/', 
                              json=booking_data, 
                              headers=auth_headers)
        assert response.status_code == 201
    
    # Test search functionality
    response = client.get('/api/bookings/search?q=Alice', headers=auth_headers)
    assert response.status_code == 200
    
    search_results = json.loads(response.data)
    assert search_results['count'] == 1
    assert search_results['results'][0]['customer_name'] == 'Alice Johnson'
    
    # Test filtering by status
    response = client.get('/api/bookings/?status=active', headers=auth_headers)
    assert response.status_code == 200
    
    filtered_results = json.loads(response.data)
    active_bookings = [b for b in filtered_results['bookings'] if b['status'] == 'active']
    assert len(active_bookings) >= 1
    
    # Test filtering by project name
    response = client.get('/api/bookings/?project_name=Green', headers=auth_headers)
    assert response.status_code == 200
    
    project_results = json.loads(response.data)
    assert len(project_results['bookings']) >= 1
    assert 'Green' in project_results['bookings'][0]['project_name']


def test_booking_validation(client, auth_headers):
    """Test booking data validation."""
    
    # Test missing required fields
    invalid_booking = {
        'customer_name': '',  # Empty required field
        'contact_number': '123',  # Too short
        'project_name': 'Test Project',
        'type': '2BHK',
        'area': -100,  # Negative area
        'agreement_cost': -5000,  # Negative cost
        'amount': 4800000.0,
        'timeline': (datetime.utcnow() - timedelta(days=1)).isoformat()  # Past date
    }
    
    response = client.post('/api/bookings/', 
                          json=invalid_booking, 
                          headers=auth_headers)
    assert response.status_code == 400
    
    error_data = json.loads(response.data)
    assert 'error' in error_data


def test_booking_stats_integration(client, auth_headers):
    """Test booking statistics endpoint integration."""
    
    # Create a test booking
    booking_data = {
        'customer_name': 'Stats Test User',
        'contact_number': '9876543210',
        'project_name': 'Stats Test Project',
        'type': '2BHK',
        'area': 1000.0,
        'agreement_cost': 4000000.0,
        'amount': 3800000.0,
        'status': 'active',
        'timeline': (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    
    response = client.post('/api/bookings/', 
                          json=booking_data, 
                          headers=auth_headers)
    assert response.status_code == 201
    
    # Test stats endpoint
    response = client.get('/api/bookings/stats', headers=auth_headers)
    assert response.status_code == 200
    
    stats = json.loads(response.data)
    assert 'total_bookings' in stats
    assert 'total_revenue' in stats
    assert 'completion_rate' in stats
    assert stats['total_bookings'] >= 1
    assert stats['total_revenue'] >= 3800000.0


def test_unauthorized_access(client):
    """Test that booking operations require authentication."""
    
    # Test without authentication headers
    response = client.get('/api/bookings/')
    assert response.status_code == 401
    
    response = client.post('/api/bookings/', json={})
    assert response.status_code == 401
    
    response = client.put('/api/bookings/1', json={})
    assert response.status_code == 401
    
    response = client.delete('/api/bookings/1')
    assert response.status_code == 401