"""
Storage Service Package

Unified microservice for storage operations consolidating storage/ and secure_storage/ components.
"""

from .interface import IStorageService
from .service import StorageService
from .models import (
    StorageResult, StorageFileInfo, HealthStatus, BulkOperationRequest,
    BulkOperationResult, AuditLogEntry, StorageMetrics, StorageConfiguration,
    FilterCriteria, StorageQuota, StorageOperationType, StorageErrorCode
)
from .exceptions import (
    StorageServiceException, FileNotFoundException, MetadataNotFoundException,
    InvalidPathException, PermissionDeniedException, StorageFullException,
    InvalidMetadataException, EncryptionException, AccessControlException,
    CloudIntegrationException, AuditLogException, ServiceUnavailableException
)

__all__ = [
    # Interface and Implementation
    'IStorageService',
    'StorageService',
    
    # Models
    'StorageResult',
    'StorageFileInfo', 
    'HealthStatus',
    'BulkOperationRequest',
    'BulkOperationResult',
    'AuditLogEntry',
    'StorageMetrics',
    'StorageConfiguration',
    'FilterCriteria',
    'StorageQuota',
    'StorageOperationType',
    'StorageErrorCode',
    
    # Exceptions
    'StorageServiceException',
    'FileNotFoundException',
    'MetadataNotFoundException',
    'InvalidPathException',
    'PermissionDeniedException',
    'StorageFullException',
    'InvalidMetadataException',
    'EncryptionException',
    'AccessControlException',
    'CloudIntegrationException',
    'AuditLogException',
    'ServiceUnavailableException',
]

__version__ = '1.0.0'