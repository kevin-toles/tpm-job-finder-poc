class ApplicationError(Exception):
    """Base class for application-specific errors."""
    pass

class ValidationError(ApplicationError):
    """Raised when validation fails."""
    pass

class ExternalServiceError(ApplicationError):
    """Raised when an external service call fails."""
    pass

class NotFoundError(ApplicationError):
    """Raised when a required resource is not found."""
    pass
