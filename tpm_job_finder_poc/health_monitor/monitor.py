"""Health monitoring service."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging


class HealthMonitor:
    """Health monitoring service for system components."""
    
    def __init__(self):
        """Initialize health monitor."""
        self.logger = logging.getLogger(__name__)
        self.error_reports = []
        
    def report_error(self, error_message: str, service: str = None, error_type: str = None, 
                     component: str = None, metadata: Optional[Dict[str, Any]] = None):
        """Report an error to the health monitoring system.
        
        Args:
            error_message: Description of the error
            service: Service name that experienced the error (new parameter)
            error_type: Type/category of the error (new parameter)
            component: Component that experienced the error (legacy parameter)
            metadata: Additional error metadata
        """
        error_report = {
            'timestamp': datetime.now(timezone.utc),
            'error_message': error_message,
            'service': service or component or 'unknown',
            'error_type': error_type or 'unknown',
            'metadata': metadata or {}
        }
        
        self.error_reports.append(error_report)
        self.logger.error(f"Health Monitor: {service or component} - {error_message}")
        
        # In a real implementation, this might trigger alerts, send notifications, etc.
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        return {
            'status': 'healthy',
            'error_count': len(self.error_reports),
            'last_check': datetime.now(timezone.utc).isoformat()
        }
        
    def clear_errors(self):
        """Clear error history (for testing)."""
        self.error_reports.clear()


# Global instance for easy access
health_monitor = HealthMonitor()