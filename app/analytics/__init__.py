"""Analytics module for booking system data processing and reporting."""
from .analytics_service import AnalyticsService
from .routes import analytics_bp

__all__ = ['AnalyticsService', 'analytics_bp']