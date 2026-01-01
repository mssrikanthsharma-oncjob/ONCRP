"""Authentication API routes."""
from flask import Blueprint, request, jsonify
from app.auth.auth_service import AuthService, token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        result, error = AuthService.login(username, password)
        
        if error:
            return jsonify({'error': error}), 401
        
        return jsonify({
            'message': 'Login successful',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/demo-login', methods=['POST'])
def demo_login():
    """Demo login endpoint with predefined credentials."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        role = data.get('role', '').strip().lower()
        
        # Map role to demo credentials
        demo_credentials = {
            'admin': {'username': 'admin', 'password': 'admin123'},
            'sales': {'username': 'sales', 'password': 'sales123'},
            'sales_person': {'username': 'sales', 'password': 'sales123'}
        }
        
        if role not in demo_credentials:
            return jsonify({
                'error': 'Invalid role. Use "admin" or "sales"',
                'available_roles': ['admin', 'sales']
            }), 400
        
        credentials = demo_credentials[role]
        result, error = AuthService.login(credentials['username'], credentials['password'])
        
        if error:
            return jsonify({'error': error}), 401
        
        return jsonify({
            'message': f'Demo login successful as {role}',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """Verify current token and return user info."""
    try:
        return jsonify({
            'message': 'Token is valid',
            'user': request.current_user
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """User logout endpoint (client-side token removal)."""
    try:
        return jsonify({
            'message': 'Logout successful. Please remove token from client storage.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500