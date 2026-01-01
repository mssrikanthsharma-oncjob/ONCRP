"""Booking model for real estate transaction management."""
from datetime import datetime
from sqlalchemy import CheckConstraint, Numeric
from app import db


class Booking(db.Model):
    """Booking model for real estate transactions."""
    
    __tablename__ = 'bookings'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Customer information
    customer_name = db.Column(db.String(255), nullable=False, index=True)
    contact_number = db.Column(db.String(20), nullable=False)
    
    # Project information
    project_name = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)  # 2BHK, 3BHK, etc.
    area = db.Column(db.Float, nullable=False)  # in sq ft
    
    # Financial information
    agreement_cost = db.Column(Numeric(15, 2), nullable=False)
    amount = db.Column(Numeric(15, 2), nullable=False)
    tax_gst = db.Column(Numeric(15, 2), nullable=False, default=0)
    refund_buyer = db.Column(Numeric(15, 2), nullable=False, default=0)
    refund_referral = db.Column(Numeric(15, 2), nullable=False, default=0)
    onc_trust_fund = db.Column(Numeric(15, 2), nullable=False, default=0)
    oncct_funded = db.Column(Numeric(15, 2), nullable=False, default=0)
    
    # Status and timeline
    invoice_status = db.Column(db.String(50), nullable=False, default='pending')
    timeline = db.Column(db.DateTime, nullable=False)
    loan_req = db.Column(db.String(10), nullable=False, default='no')  # yes/no
    status = db.Column(
        db.Enum('active', 'complete', 'cancelled', name='booking_status'), 
        nullable=False, 
        default='active'
    )
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='bookings', lazy=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('area > 0', name='check_area_positive'),
        CheckConstraint('agreement_cost >= 0', name='check_agreement_cost_non_negative'),
        CheckConstraint('amount >= 0', name='check_amount_non_negative'),
        CheckConstraint('tax_gst >= 0', name='check_tax_gst_non_negative'),
        CheckConstraint('refund_buyer >= 0', name='check_refund_buyer_non_negative'),
        CheckConstraint('refund_referral >= 0', name='check_refund_referral_non_negative'),
        CheckConstraint('onc_trust_fund >= 0', name='check_onc_trust_fund_non_negative'),
        CheckConstraint('oncct_funded >= 0', name='check_oncct_funded_non_negative'),
        CheckConstraint("loan_req IN ('yes', 'no')", name='check_loan_req_valid'),
    )
    
    def __init__(self, **kwargs):
        """Initialize booking with validation."""
        # Set default values
        if 'status' not in kwargs:
            kwargs['status'] = 'active'
        if 'invoice_status' not in kwargs:
            kwargs['invoice_status'] = 'pending'
        if 'loan_req' not in kwargs:
            kwargs['loan_req'] = 'no'
        
        # Initialize with provided values
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def total_amount(self):
        """Calculate total amount including tax."""
        return float(self.amount) + float(self.tax_gst)
    
    @property
    def net_refund(self):
        """Calculate net refund amount."""
        return float(self.refund_buyer) + float(self.refund_referral)
    
    def validate_data(self):
        """Validate booking data constraints."""
        errors = []
        
        # Required field validation
        if not self.customer_name or not self.customer_name.strip():
            errors.append("Customer name is required")
        
        if not self.project_name or not self.project_name.strip():
            errors.append("Project name is required")
        
        if not self.contact_number or not self.contact_number.strip():
            errors.append("Contact number is required")
        
        if not self.type or not self.type.strip():
            errors.append("Property type is required")
        
        # Numeric validation
        if self.area <= 0:
            errors.append("Area must be greater than 0")
        
        if self.agreement_cost < 0:
            errors.append("Agreement cost cannot be negative")
        
        if self.amount < 0:
            errors.append("Amount cannot be negative")
        
        # Timeline validation
        if self.timeline and self.timeline < datetime.utcnow():
            errors.append("Timeline cannot be in the past")
        
        # Contact number format validation (basic)
        if self.contact_number and len(self.contact_number.strip()) < 10:
            errors.append("Contact number must be at least 10 digits")
        
        return errors
    
    def to_dict(self):
        """Convert booking to dictionary representation."""
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'contact_number': self.contact_number,
            'project_name': self.project_name,
            'type': self.type,
            'area': float(self.area),
            'agreement_cost': float(self.agreement_cost),
            'amount': float(self.amount),
            'tax_gst': float(self.tax_gst),
            'refund_buyer': float(self.refund_buyer),
            'refund_referral': float(self.refund_referral),
            'onc_trust_fund': float(self.onc_trust_fund),
            'oncct_funded': float(self.oncct_funded),
            'invoice_status': self.invoice_status,
            'timeline': self.timeline.isoformat() if self.timeline else None,
            'loan_req': self.loan_req,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'total_amount': self.total_amount,
            'net_refund': self.net_refund
        }
    
    def update_from_dict(self, data):
        """Update booking from dictionary data."""
        updatable_fields = [
            'customer_name', 'contact_number', 'project_name', 'type', 'area',
            'agreement_cost', 'amount', 'tax_gst', 'refund_buyer', 'refund_referral',
            'onc_trust_fund', 'oncct_funded', 'invoice_status', 'timeline', 
            'loan_req', 'status'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(self, field, data[field])
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        """String representation of booking."""
        return f'<Booking {self.id}: {self.customer_name} - {self.project_name}>'