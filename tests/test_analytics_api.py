"""Test analytics API endpoints."""
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


@pytest.fixture
def sample_bookings(client, auth_headers):
    """Create sample bookings for testing analytics."""
    bookings_data = [
        {
            'customer_name': 'John Doe',
            'contact_number': '9876543210',
            'project_name': 'Sunrise Apartments',
            'type': '2BHK',
            'area': 1200.0,
            'agreement_cost': 5000000.0,
            'amount': 4800000.0,
            'tax_gst': 240000.0,
            'status': 'active',
            'timeline': (datetime.utcnow() + timedelta(days=30)).isoformat()
        },
        {
            'customer_name': 'Jane Smith',
            'contact_number': '9876543211',
            'project_name': 'Green Valley',
            'type': '3BHK',
            'area': 1500.0,
            'agreement_cost': 6000000.0,
            'amount': 5800000.0,
            'tax_gst': 290000.0,
            'status': 'complete',
            'timeline': (datetime.utcnow() + timedelta(days=45)).isoformat()
        }
    ]
    
    for booking_data in bookings_data:
        response = client.post('/api/bookings/', 
                              json=booking_data, 
                              headers=auth_headers)
        assert response.status_code == 201


def test_analytics_dashboard(client, auth_headers, sample_bookings):
    """Test analytics dashboard endpoint."""
    response = client.get('/api/analytics/dashboard', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that dashboard data contains expected keys
    assert 'kpis' in data
    assert 'charts' in data
    assert 'date_range' in data


def test_analytics_kpis(client, auth_headers, sample_bookings):
    """Test KPIs endpoint."""
    response = client.get('/api/analytics/kpis', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check KPI structure - data is nested under 'kpis' key
    assert 'kpis' in data
    kpis = data['kpis']
    assert 'total_bookings' in kpis
    assert 'total_revenue' in kpis
    assert 'completion_rate' in kpis
    assert 'avg_booking_value' in kpis
    
    # Verify data types and reasonable values
    assert isinstance(kpis['total_bookings'], int)
    assert kpis['total_bookings'] >= 2  # We created 2 sample bookings
    assert isinstance(kpis['total_revenue'], (int, float))
    assert kpis['total_revenue'] > 0


def test_analytics_trends(client, auth_headers, sample_bookings):
    """Test trends endpoint."""
    response = client.get('/api/analytics/trends', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check trends data structure
    assert 'trends' in data
    assert 'trend_type' in data
    assert isinstance(data['trends'], list)
    assert data['trend_type'] == 'monthly'


def test_analytics_projects(client, auth_headers, sample_bookings):
    """Test projects analytics endpoint."""
    response = client.get('/api/analytics/projects', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check projects data structure
    assert 'projects' in data
    assert isinstance(data['projects'], list)
    
    # Should have data for our sample projects
    project_names = [item['project_name'] for item in data['projects']]
    assert 'Sunrise Apartments' in project_names or 'Green Valley' in project_names


def test_analytics_property_types(client, auth_headers, sample_bookings):
    """Test property types analytics endpoint."""
    response = client.get('/api/analytics/property-types', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check property types data structure
    assert 'property_types' in data
    assert isinstance(data['property_types'], list)
    
    # Should have data for our sample types
    type_names = [item['property_type'] for item in data['property_types']]
    assert '2BHK' in type_names or '3BHK' in type_names


def test_analytics_unauthorized_access(client):
    """Test that analytics endpoints require authentication."""
    endpoints = [
        '/api/analytics/dashboard',
        '/api/analytics/kpis',
        '/api/analytics/trends',
        '/api/analytics/projects',
        '/api/analytics/property-types'
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401


def test_analytics_export(client, auth_headers, sample_bookings):
    """Test analytics export functionality."""
    response = client.get('/api/analytics/export?format=json', headers=auth_headers)
    
    assert response.status_code == 200
    
    # Check that we get some export data
    if response.content_type == 'application/json':
        data = json.loads(response.data)
        assert 'bookings' in data or 'data' in data