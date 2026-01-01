"""Analytics data processing service for booking system."""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import func, extract, and_, or_
from app import db
from app.models.booking import Booking


class AnalyticsService:
    """Service class for processing booking data into analytics insights."""
    
    @staticmethod
    def get_kpi_summary(start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None,
                       filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate key performance indicators for bookings.
        
        Args:
            start_date: Filter bookings from this date
            end_date: Filter bookings until this date
            filters: Additional filters (status, project_name, etc.)
            
        Returns:
            Dictionary containing KPI metrics
        """
        # Build base query
        query = Booking.query
        
        # Apply date filters
        if start_date:
            query = query.filter(Booking.created_at >= start_date)
        if end_date:
            query = query.filter(Booking.created_at <= end_date)
        
        # Apply additional filters
        if filters:
            query = AnalyticsService._apply_filters(query, filters)
        
        # Calculate basic counts
        total_bookings = query.count()
        active_bookings = query.filter(Booking.status == 'active').count()
        completed_bookings = query.filter(Booking.status == 'complete').count()
        cancelled_bookings = query.filter(Booking.status == 'cancelled').count()
        
        # Calculate revenue metrics
        revenue_query = query.filter(Booking.status.in_(['active', 'complete']))
        total_revenue = db.session.query(func.sum(Booking.amount)).filter(
            Booking.id.in_(revenue_query.with_entities(Booking.id))
        ).scalar() or 0
        
        total_tax = db.session.query(func.sum(Booking.tax_gst)).filter(
            Booking.id.in_(revenue_query.with_entities(Booking.id))
        ).scalar() or 0
        
        # Calculate average metrics
        avg_booking_value = (total_revenue / total_bookings) if total_bookings > 0 else 0
        completion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Calculate area metrics
        total_area = db.session.query(func.sum(Booking.area)).filter(
            Booking.id.in_(query.with_entities(Booking.id))
        ).scalar() or 0
        
        avg_area = (total_area / total_bookings) if total_bookings > 0 else 0
        
        return {
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'total_revenue': float(total_revenue),
            'total_tax': float(total_tax),
            'total_revenue_with_tax': float(total_revenue + total_tax),
            'avg_booking_value': float(avg_booking_value),
            'completion_rate': float(completion_rate),
            'total_area': float(total_area),
            'avg_area': float(avg_area),
            'cancellation_rate': (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
        }
    
    @staticmethod
    def get_monthly_trends(start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get monthly booking trends data.
        
        Args:
            start_date: Start date for trend analysis
            end_date: End date for trend analysis
            filters: Additional filters
            
        Returns:
            List of monthly trend data points
        """
        # Default to last 12 months if no dates provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        # Build query
        query = Booking.query.filter(
            and_(
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        )
        
        # Apply additional filters
        if filters:
            query = AnalyticsService._apply_filters(query, filters)
        
        # Group by year and month
        monthly_data = db.session.query(
            extract('year', Booking.created_at).label('year'),
            extract('month', Booking.created_at).label('month'),
            func.count(Booking.id).label('booking_count'),
            func.sum(Booking.amount).label('total_revenue'),
            func.sum(Booking.area).label('total_area'),
            func.count(func.nullif(Booking.status, 'cancelled')).label('non_cancelled_count')
        ).filter(
            Booking.id.in_(query.with_entities(Booking.id))
        ).group_by(
            extract('year', Booking.created_at),
            extract('month', Booking.created_at)
        ).order_by(
            extract('year', Booking.created_at),
            extract('month', Booking.created_at)
        ).all()
        
        # Format results
        trends = []
        for data in monthly_data:
            month_str = f"{int(data.year)}-{int(data.month):02d}"
            trends.append({
                'period': month_str,
                'year': int(data.year),
                'month': int(data.month),
                'booking_count': data.booking_count,
                'total_revenue': float(data.total_revenue or 0),
                'total_area': float(data.total_area or 0),
                'avg_booking_value': float((data.total_revenue or 0) / data.booking_count) if data.booking_count > 0 else 0,
                'non_cancelled_count': data.non_cancelled_count
            })
        
        return trends
    
    @staticmethod
    def get_project_distribution(start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get booking distribution by project.
        
        Args:
            start_date: Filter bookings from this date
            end_date: Filter bookings until this date
            filters: Additional filters
            
        Returns:
            List of project distribution data
        """
        # Build query
        query = Booking.query
        
        # Apply date filters
        if start_date:
            query = query.filter(Booking.created_at >= start_date)
        if end_date:
            query = query.filter(Booking.created_at <= end_date)
        
        # Apply additional filters
        if filters:
            query = AnalyticsService._apply_filters(query, filters)
        
        # Group by project
        project_data = db.session.query(
            Booking.project_name,
            func.count(Booking.id).label('booking_count'),
            func.sum(Booking.amount).label('total_revenue'),
            func.sum(Booking.area).label('total_area'),
            func.avg(Booking.amount).label('avg_revenue'),
            func.count(func.nullif(Booking.status, 'cancelled')).label('active_complete_count')
        ).filter(
            Booking.id.in_(query.with_entities(Booking.id))
        ).group_by(
            Booking.project_name
        ).order_by(
            func.count(Booking.id).desc()
        ).all()
        
        # Format results
        distribution = []
        for data in project_data:
            distribution.append({
                'project_name': data.project_name,
                'booking_count': data.booking_count,
                'total_revenue': float(data.total_revenue or 0),
                'total_area': float(data.total_area or 0),
                'avg_revenue': float(data.avg_revenue or 0),
                'active_complete_count': data.active_complete_count,
                'success_rate': (data.active_complete_count / data.booking_count * 100) if data.booking_count > 0 else 0
            })
        
        return distribution
    
    @staticmethod
    def get_property_type_analysis(start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get booking analysis by property type.
        
        Args:
            start_date: Filter bookings from this date
            end_date: Filter bookings until this date
            filters: Additional filters
            
        Returns:
            List of property type analysis data
        """
        # Build query
        query = Booking.query
        
        # Apply date filters
        if start_date:
            query = query.filter(Booking.created_at >= start_date)
        if end_date:
            query = query.filter(Booking.created_at <= end_date)
        
        # Apply additional filters
        if filters:
            query = AnalyticsService._apply_filters(query, filters)
        
        # Group by property type
        type_data = db.session.query(
            Booking.type,
            func.count(Booking.id).label('booking_count'),
            func.sum(Booking.amount).label('total_revenue'),
            func.sum(Booking.area).label('total_area'),
            func.avg(Booking.amount).label('avg_revenue'),
            func.avg(Booking.area).label('avg_area')
        ).filter(
            Booking.id.in_(query.with_entities(Booking.id))
        ).group_by(
            Booking.type
        ).order_by(
            func.count(Booking.id).desc()
        ).all()
        
        # Format results
        analysis = []
        for data in type_data:
            analysis.append({
                'property_type': data.type,
                'booking_count': data.booking_count,
                'total_revenue': float(data.total_revenue or 0),
                'total_area': float(data.total_area or 0),
                'avg_revenue': float(data.avg_revenue or 0),
                'avg_area': float(data.avg_area or 0),
                'revenue_per_sqft': float(data.total_revenue or 0) / float(data.total_area or 1) if data.total_area else 0
            })
        
        return analysis
    
    @staticmethod
    def get_revenue_trends(start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          filters: Optional[Dict[str, Any]] = None,
                          group_by: str = 'month') -> List[Dict[str, Any]]:
        """
        Get revenue trends over time.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            filters: Additional filters
            group_by: Grouping period ('month', 'quarter', 'year')
            
        Returns:
            List of revenue trend data points
        """
        # Default to last 12 months if no dates provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        # Build query
        query = Booking.query.filter(
            and_(
                Booking.created_at >= start_date,
                Booking.created_at <= end_date
            )
        )
        
        # Apply additional filters
        if filters:
            query = AnalyticsService._apply_filters(query, filters)
        
        # Determine grouping based on group_by parameter
        if group_by == 'year':
            group_fields = [extract('year', Booking.created_at).label('year')]
            order_fields = [extract('year', Booking.created_at)]
        elif group_by == 'quarter':
            group_fields = [
                extract('year', Booking.created_at).label('year'),
                func.ceil(extract('month', Booking.created_at) / 3).label('quarter')
            ]
            order_fields = [
                extract('year', Booking.created_at),
                func.ceil(extract('month', Booking.created_at) / 3)
            ]
        else:  # default to month
            group_fields = [
                extract('year', Booking.created_at).label('year'),
                extract('month', Booking.created_at).label('month')
            ]
            order_fields = [
                extract('year', Booking.created_at),
                extract('month', Booking.created_at)
            ]
        
        # Execute query
        revenue_data = db.session.query(
            *group_fields,
            func.sum(Booking.amount).label('total_revenue'),
            func.sum(Booking.tax_gst).label('total_tax'),
            func.count(Booking.id).label('booking_count'),
            func.avg(Booking.amount).label('avg_revenue')
        ).filter(
            Booking.id.in_(query.with_entities(Booking.id))
        ).group_by(
            *group_fields
        ).order_by(
            *order_fields
        ).all()
        
        # Format results
        trends = []
        for data in revenue_data:
            if group_by == 'year':
                period = str(int(data.year))
            elif group_by == 'quarter':
                period = f"{int(data.year)}-Q{int(data.quarter)}"
            else:  # month
                period = f"{int(data.year)}-{int(data.month):02d}"
            
            trends.append({
                'period': period,
                'total_revenue': float(data.total_revenue or 0),
                'total_tax': float(data.total_tax or 0),
                'total_with_tax': float((data.total_revenue or 0) + (data.total_tax or 0)),
                'booking_count': data.booking_count,
                'avg_revenue': float(data.avg_revenue or 0)
            })
        
        return trends
    
    @staticmethod
    def get_chart_data(chart_type: str, 
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get formatted data for specific chart types.
        
        Args:
            chart_type: Type of chart ('monthly_trends', 'project_distribution', 
                       'property_types', 'revenue_trends')
            start_date: Start date for data
            end_date: End date for data
            filters: Additional filters
            
        Returns:
            Formatted chart data with labels and datasets
        """
        if chart_type == 'monthly_trends':
            data = AnalyticsService.get_monthly_trends(start_date, end_date, filters)
            return {
                'labels': [item['period'] for item in data],
                'datasets': [
                    {
                        'label': 'Bookings',
                        'data': [item['booking_count'] for item in data],
                        'type': 'line'
                    },
                    {
                        'label': 'Revenue',
                        'data': [item['total_revenue'] for item in data],
                        'type': 'bar'
                    }
                ]
            }
        
        elif chart_type == 'project_distribution':
            data = AnalyticsService.get_project_distribution(start_date, end_date, filters)
            return {
                'labels': [item['project_name'] for item in data],
                'datasets': [
                    {
                        'label': 'Bookings by Project',
                        'data': [item['booking_count'] for item in data],
                        'type': 'pie'
                    }
                ]
            }
        
        elif chart_type == 'property_types':
            data = AnalyticsService.get_property_type_analysis(start_date, end_date, filters)
            return {
                'labels': [item['property_type'] for item in data],
                'datasets': [
                    {
                        'label': 'Revenue by Type',
                        'data': [item['total_revenue'] for item in data],
                        'type': 'doughnut'
                    }
                ]
            }
        
        elif chart_type == 'revenue_trends':
            data = AnalyticsService.get_revenue_trends(start_date, end_date, filters)
            return {
                'labels': [item['period'] for item in data],
                'datasets': [
                    {
                        'label': 'Revenue',
                        'data': [item['total_revenue'] for item in data],
                        'type': 'line'
                    },
                    {
                        'label': 'Revenue + Tax',
                        'data': [item['total_with_tax'] for item in data],
                        'type': 'line'
                    }
                ]
            }
        
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
    
    @staticmethod
    def _apply_filters(query, filters: Dict[str, Any]):
        """
        Apply additional filters to a query.
        
        Args:
            query: SQLAlchemy query object
            filters: Dictionary of filter criteria
            
        Returns:
            Modified query with filters applied
        """
        if 'status' in filters and filters['status']:
            if isinstance(filters['status'], list):
                query = query.filter(Booking.status.in_(filters['status']))
            else:
                query = query.filter(Booking.status == filters['status'])
        
        if 'project_name' in filters and filters['project_name']:
            query = query.filter(Booking.project_name.ilike(f"%{filters['project_name']}%"))
        
        if 'property_type' in filters and filters['property_type']:
            query = query.filter(Booking.type.ilike(f"%{filters['property_type']}%"))
        
        if 'customer_name' in filters and filters['customer_name']:
            query = query.filter(Booking.customer_name.ilike(f"%{filters['customer_name']}%"))
        
        if 'min_amount' in filters and filters['min_amount'] is not None:
            query = query.filter(Booking.amount >= filters['min_amount'])
        
        if 'max_amount' in filters and filters['max_amount'] is not None:
            query = query.filter(Booking.amount <= filters['max_amount'])
        
        if 'min_area' in filters and filters['min_area'] is not None:
            query = query.filter(Booking.area >= filters['min_area'])
        
        if 'max_area' in filters and filters['max_area'] is not None:
            query = query.filter(Booking.area <= filters['max_area'])
        
        return query
    
    @staticmethod
    def export_data(data_type: str,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   filters: Optional[Dict[str, Any]] = None,
                   format_type: str = 'json') -> Dict[str, Any]:
        """
        Export analytics data in specified format.
        
        Args:
            data_type: Type of data to export ('kpis', 'trends', 'projects', 'types')
            start_date: Start date for data
            end_date: End date for data
            filters: Additional filters
            format_type: Export format ('json', 'csv_data')
            
        Returns:
            Exported data in requested format
        """
        # Get the appropriate data
        if data_type == 'kpis':
            data = AnalyticsService.get_kpi_summary(start_date, end_date, filters)
        elif data_type == 'trends':
            data = AnalyticsService.get_monthly_trends(start_date, end_date, filters)
        elif data_type == 'projects':
            data = AnalyticsService.get_project_distribution(start_date, end_date, filters)
        elif data_type == 'types':
            data = AnalyticsService.get_property_type_analysis(start_date, end_date, filters)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        # Format for export
        export_data = {
            'data_type': data_type,
            'generated_at': datetime.utcnow().isoformat(),
            'date_range': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            },
            'filters': filters or {},
            'data': data
        }
        
        if format_type == 'csv_data':
            # Convert to CSV-friendly format
            if isinstance(data, dict):
                # For KPI data, convert to list of key-value pairs
                csv_data = [{'metric': k, 'value': v} for k, v in data.items()]
            else:
                # For list data, use as-is
                csv_data = data
            
            export_data['csv_data'] = csv_data
        
        return export_data