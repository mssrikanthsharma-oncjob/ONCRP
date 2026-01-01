"""Booking management API routes."""
from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy import or_, and_
from app import db
from app.models import Booking, User
from app.auth.auth_service import token_required, auth_required

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/', methods=['GET'])
@auth_required(['admin', 'sales_person'])
def get_bookings():
    """Get all bookings with optional search and filtering."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)  # Max 100 per page
        
        # Search parameters
        search = request.args.get('search', '').strip()
        project_name = request.args.get('project_name', '').strip()
        customer_name = request.args.get('customer_name', '').strip()
        status = request.args.get('status', '').strip()
        property_type = request.args.get('type', '').strip()
        
        # Date range filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Sorting
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = Booking.query
        
        # Apply search filters
        if search:
            search_filter = or_(
                Booking.customer_name.ilike(f'%{search}%'),
                Booking.project_name.ilike(f'%{search}%'),
                Booking.contact_number.ilike(f'%{search}%'),
                Booking.type.ilike(f'%{search}%'),
                Booking.invoice_status.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Apply specific filters
        if project_name:
            query = query.filter(Booking.project_name.ilike(f'%{project_name}%'))
        
        if customer_name:
            query = query.filter(Booking.customer_name.ilike(f'%{customer_name}%'))
        
        if status and status in ['active', 'complete', 'cancelled']:
            query = query.filter(Booking.status == status)
        
        if property_type:
            query = query.filter(Booking.type.ilike(f'%{property_type}%'))
        
        # Date range filtering
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Booking.created_at >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format.'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Booking.created_at <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format.'}), 400
        
        # Apply sorting
        valid_sort_fields = ['created_at', 'updated_at', 'customer_name', 'project_name', 
                           'amount', 'timeline', 'status']
        if sort_by in valid_sort_fields:
            sort_column = getattr(Booking, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(Booking.created_at.desc())
        
        # Execute paginated query
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        bookings = [booking.to_dict() for booking in pagination.items]
        
        return jsonify({
            'bookings': bookings,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters_applied': {
                'search': search,
                'project_name': project_name,
                'customer_name': customer_name,
                'status': status,
                'type': property_type,
                'start_date': start_date,
                'end_date': end_date,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@booking_bp.route('/<int:booking_id>', methods=['GET'])
@auth_required(['admin', 'sales_person'])
def get_booking(booking_id):
    """Get a specific booking by ID."""
    try:
        booking = Booking.query.get(booking_id)
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        return jsonify({
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@booking_bp.route('/', methods=['POST'])
@auth_required(['admin', 'sales_person'])
def create_booking():
    """Create a new booking."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Required fields validation
        required_fields = [
            'customer_name', 'contact_number', 'project_name', 'type', 
            'area', 'agreement_cost', 'amount', 'timeline'
        ]
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Parse timeline
        try:
            timeline = datetime.fromisoformat(data['timeline'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return jsonify({'error': 'Invalid timeline format. Use ISO format.'}), 400
        
        # Create booking instance
        booking_data = {
            'customer_name': data['customer_name'].strip(),
            'contact_number': data['contact_number'].strip(),
            'project_name': data['project_name'].strip(),
            'type': data['type'].strip(),
            'area': float(data['area']),
            'agreement_cost': float(data['agreement_cost']),
            'amount': float(data['amount']),
            'timeline': timeline,
            'created_by': request.current_user['user_id']
        }
        
        # Optional fields
        optional_fields = [
            'tax_gst', 'refund_buyer', 'refund_referral', 'onc_trust_fund',
            'oncct_funded', 'invoice_status', 'loan_req', 'status'
        ]
        
        for field in optional_fields:
            if field in data:
                if field in ['tax_gst', 'refund_buyer', 'refund_referral', 
                           'onc_trust_fund', 'oncct_funded']:
                    booking_data[field] = float(data[field])
                else:
                    booking_data[field] = data[field]
        
        booking = Booking(**booking_data)
        
        # Validate booking data
        validation_errors = booking.validate_data()
        if validation_errors:
            return jsonify({
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Save to database
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking': booking.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data type: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@booking_bp.route('/<int:booking_id>', methods=['PUT'])
@auth_required(['admin', 'sales_person'])
def update_booking(booking_id):
    """Update an existing booking."""
    try:
        booking = Booking.query.get(booking_id)
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Parse timeline if provided
        if 'timeline' in data:
            try:
                data['timeline'] = datetime.fromisoformat(data['timeline'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return jsonify({'error': 'Invalid timeline format. Use ISO format.'}), 400
        
        # Update booking from data
        booking.update_from_dict(data)
        
        # Validate updated booking
        validation_errors = booking.validate_data()
        if validation_errors:
            return jsonify({
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'message': 'Booking updated successfully',
            'booking': booking.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data type: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@booking_bp.route('/<int:booking_id>', methods=['DELETE'])
@auth_required(['admin', 'sales_person'])
def delete_booking(booking_id):
    """Delete a booking (soft delete by changing status)."""
    try:
        booking = Booking.query.get(booking_id)
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check if booking is already cancelled
        if booking.status == 'cancelled':
            return jsonify({'error': 'Booking is already cancelled'}), 400
        
        # Soft delete by changing status to cancelled
        booking.status = 'cancelled'
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@booking_bp.route('/<int:booking_id>/hard-delete', methods=['DELETE'])
@auth_required(['admin'])  # Only admin can hard delete
def hard_delete_booking(booking_id):
    """Permanently delete a booking (admin only)."""
    try:
        booking = Booking.query.get(booking_id)
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Store booking data for response
        booking_data = booking.to_dict()
        
        # Permanently delete from database
        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking permanently deleted',
            'deleted_booking': booking_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@booking_bp.route('/search', methods=['GET'])
@auth_required(['admin', 'sales_person'])
def search_bookings():
    """Advanced search endpoint for bookings."""
    try:
        # Get search parameters
        query_text = request.args.get('q', '').strip()
        
        if not query_text:
            return jsonify({'error': 'Search query parameter "q" is required'}), 400
        
        # Perform search across multiple fields
        search_filter = or_(
            Booking.customer_name.ilike(f'%{query_text}%'),
            Booking.project_name.ilike(f'%{query_text}%'),
            Booking.contact_number.ilike(f'%{query_text}%'),
            Booking.type.ilike(f'%{query_text}%'),
            Booking.invoice_status.ilike(f'%{query_text}%')
        )
        
        bookings = Booking.query.filter(search_filter).order_by(
            Booking.created_at.desc()
        ).limit(50).all()  # Limit to 50 results for performance
        
        return jsonify({
            'query': query_text,
            'results': [booking.to_dict() for booking in bookings],
            'count': len(bookings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@booking_bp.route('/stats', methods=['GET'])
@auth_required(['admin', 'sales_person'])
def get_booking_stats():
    """Get basic booking statistics."""
    try:
        # Get total counts by status
        total_bookings = Booking.query.count()
        active_bookings = Booking.query.filter_by(status='active').count()
        completed_bookings = Booking.query.filter_by(status='complete').count()
        cancelled_bookings = Booking.query.filter_by(status='cancelled').count()
        
        # Get total revenue (sum of amounts for active and completed bookings)
        from sqlalchemy import func
        revenue_result = db.session.query(
            func.sum(Booking.amount)
        ).filter(
            Booking.status.in_(['active', 'complete'])
        ).scalar()
        
        total_revenue = float(revenue_result) if revenue_result else 0.0
        
        return jsonify({
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'total_revenue': total_revenue,
            'completion_rate': (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500