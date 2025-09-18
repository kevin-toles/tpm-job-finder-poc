"""
Storage Service Interface - Abstract Base Class
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator
from .models import (
    StorageResult, StorageFileInfo, HealthStatus, BulkOperationRequest,
    BulkOperationResult, AuditLogEntry, StorageMetrics, StorageConfiguration,
    FilterCriteria, StorageQuota, StorageMetadata, StorageFilePath,
    StorageFileName, UserId, OperationId
)


class IStorageService(ABC):
    """
    Abstract interface for storage service implementations.
    
    Defines the contract for storage services supporting file operations,
    metadata management, audit logging, and microservice patterns.
    """

    # === File Operations ===
    
    @abstractmethod
    def save_file(
        self,
        src_path: StorageFilePath,
        dest_name: StorageFileName,
        metadata: Optional[StorageMetadata] = None,
        user_id: Optional[UserId] = None,
        overwrite: bool = False
    ) -> StorageResult:
        """
        Save a file to storage with optional metadata.
        
        Args:
            src_path: Source file path
            dest_name: Destination filename
            metadata: Optional metadata to associate with file
            user_id: User performing the operation
            overwrite: Whether to overwrite existing files
            
        Returns:
            StorageResult with operation details
        """
        pass

    @abstractmethod
    def retrieve_file(
        self,
        filename: StorageFileName,
        user_id: Optional[UserId] = None
    ) -> Optional[StorageFileInfo]:
        """
        Retrieve file information and path.
        
        Args:
            filename: Name of file to retrieve
            user_id: User performing the operation
            
        Returns:
            StorageFileInfo if file exists, None otherwise
        """
        pass

    @abstractmethod
    def delete_file(
        self,
        filename: StorageFileName,
        user_id: Optional[UserId] = None,
        soft_delete: bool = False
    ) -> StorageResult:
        """
        Delete a file from storage.
        
        Args:
            filename: Name of file to delete
            user_id: User performing the operation
            soft_delete: Whether to perform soft delete
            
        Returns:
            StorageResult with operation details
        """
        pass

    @abstractmethod
    def list_files(
        self,
        filter_criteria: Optional[FilterCriteria] = None,
        user_id: Optional[UserId] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[StorageFileInfo]:
        """
        List files matching criteria.
        
        Args:
            filter_criteria: Filtering criteria
            user_id: User performing the operation
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of StorageFileInfo objects
        """
        pass

    @abstractmethod
    def file_exists(
        self,
        filename: StorageFileName,
        user_id: Optional[UserId] = None
    ) -> bool:
        """
        Check if file exists.
        
        Args:
            filename: Name of file to check
            user_id: User performing the operation
            
        Returns:
            True if file exists, False otherwise
        """
        pass

    # === Metadata Operations ===

    @abstractmethod
    def save_metadata(
        self,
        filename: StorageFileName,
        metadata: StorageMetadata,
        user_id: Optional[UserId] = None,
        merge: bool = True
    ) -> StorageResult:
        """
        Save metadata for a file.
        
        Args:
            filename: Name of file
            metadata: Metadata to save
            user_id: User performing the operation
            merge: Whether to merge with existing metadata
            
        Returns:
            StorageResult with operation details
        """
        pass

    @abstractmethod
    def retrieve_metadata(
        self,
        filename: StorageFileName,
        user_id: Optional[UserId] = None
    ) -> Optional[StorageMetadata]:
        """
        Retrieve metadata for a file.
        
        Args:
            filename: Name of file
            user_id: User performing the operation
            
        Returns:
            Metadata dictionary if exists, None otherwise
        """
        pass

    @abstractmethod
    def update_metadata(
        self,
        filename: StorageFileName,
        metadata_updates: StorageMetadata,
        user_id: Optional[UserId] = None
    ) -> StorageResult:
        """
        Update metadata for a file.
        
        Args:
            filename: Name of file
            metadata_updates: Metadata updates to apply
            user_id: User performing the operation
            
        Returns:
            StorageResult with operation details
        """
        pass

    @abstractmethod
    def delete_metadata(
        self,
        filename: StorageFileName,
        user_id: Optional[UserId] = None
    ) -> StorageResult:
        """
        Delete metadata for a file.
        
        Args:
            filename: Name of file
            user_id: User performing the operation
            
        Returns:
            StorageResult with operation details
        """
        pass

    @abstractmethod
    def search_by_metadata(
        self,
        search_criteria: Dict[str, Any],
        user_id: Optional[UserId] = None,
        limit: Optional[int] = None
    ) -> List[StorageFileInfo]:
        """
        Search files by metadata criteria.
        
        Args:
            search_criteria: Metadata search criteria
            user_id: User performing the operation
            limit: Maximum number of results
            
        Returns:
            List of matching StorageFileInfo objects
        """
        pass

    # === Bulk Operations ===

    @abstractmethod
    def bulk_save_files(
        self,
        request: BulkOperationRequest,
        user_id: Optional[UserId] = None
    ) -> BulkOperationResult:
        """
        Save multiple files in a batch operation.
        
        Args:
            request: Bulk operation request
            user_id: User performing the operation
            
        Returns:
            BulkOperationResult with batch operation details
        """
        pass

    @abstractmethod
    def bulk_delete_files(
        self,
        filenames: List[StorageFileName],
        user_id: Optional[UserId] = None,
        soft_delete: bool = False
    ) -> BulkOperationResult:
        """
        Delete multiple files in a batch operation.
        
        Args:
            filenames: List of filenames to delete
            user_id: User performing the operation
            soft_delete: Whether to perform soft delete
            
        Returns:
            BulkOperationResult with batch operation details
        """
        pass

    # === Audit and Logging ===

    @abstractmethod
    def get_audit_logs(
        self,
        filename: Optional[StorageFileName] = None,
        user_id: Optional[UserId] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[AuditLogEntry]:
        """
        Retrieve audit logs with filtering.
        
        Args:
            filename: Filter by filename
            user_id: Filter by user ID
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of results
            
        Returns:
            List of AuditLogEntry objects
        """
        pass

    @abstractmethod
    def log_custom_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        user_id: Optional[UserId] = None
    ) -> StorageResult:
        """
        Log a custom event to audit trail.
        
        Args:
            event_type: Type of event
            details: Event details
            user_id: User associated with event
            
        Returns:
            StorageResult with logging details
        """
        pass

    # === Health and Monitoring ===

    @abstractmethod
    def health_check(self) -> HealthStatus:
        """
        Perform comprehensive health check.
        
        Returns:
            HealthStatus with service health information
        """
        pass

    @abstractmethod
    def get_metrics(self) -> StorageMetrics:
        """
        Get storage service metrics.
        
        Returns:
            StorageMetrics with current metrics
        """
        pass

    @abstractmethod
    def get_quota_info(
        self,
        user_id: UserId
    ) -> StorageQuota:
        """
        Get storage quota information for user.
        
        Args:
            user_id: User ID to check quota for
            
        Returns:
            StorageQuota with quota information
        """
        pass

    # === Configuration Management ===

    @abstractmethod
    def get_configuration(self) -> StorageConfiguration:
        """
        Get current storage configuration.
        
        Returns:
            StorageConfiguration with current settings
        """
        pass

    @abstractmethod
    def update_configuration(
        self,
        config_updates: Dict[str, Any]
    ) -> StorageResult:
        """
        Update storage configuration.
        
        Args:
            config_updates: Configuration updates to apply
            
        Returns:
            StorageResult with update details
        """
        pass

    # === Service Lifecycle ===

    @abstractmethod
    def initialize(
        self,
        config: Optional[StorageConfiguration] = None
    ) -> StorageResult:
        """
        Initialize the storage service.
        
        Args:
            config: Optional configuration to use
            
        Returns:
            StorageResult with initialization details
        """
        pass

    @abstractmethod
    def shutdown(self) -> StorageResult:
        """
        Gracefully shutdown the storage service.
        
        Returns:
            StorageResult with shutdown details
        """
        pass

    @abstractmethod
    def reset(self) -> StorageResult:
        """
        Reset the storage service (for testing).
        
        Returns:
            StorageResult with reset details
        """
        pass

    # === Async Operations ===

    @abstractmethod
    async def save_file_async(
        self,
        src_path: StorageFilePath,
        dest_name: StorageFileName,
        metadata: Optional[StorageMetadata] = None,
        user_id: Optional[UserId] = None
    ) -> StorageResult:
        """
        Asynchronously save a file to storage.
        
        Args:
            src_path: Source file path
            dest_name: Destination filename
            metadata: Optional metadata
            user_id: User performing the operation
            
        Returns:
            StorageResult with operation details
        """
        pass

    @abstractmethod
    async def stream_file_async(
        self,
        filename: StorageFileName,
        user_id: Optional[UserId] = None
    ) -> AsyncIterator[bytes]:
        """
        Stream file contents asynchronously.
        
        Args:
            filename: Name of file to stream
            user_id: User performing the operation
            
        Yields:
            File content chunks
        """
        pass

    # === Security Operations ===

    @abstractmethod
    def encrypt_file(
        self,
        filename: StorageFileName,
        encryption_key: Optional[str] = None
    ) -> StorageResult:
        """
        Encrypt a stored file (stub for future implementation).
        
        Args:
            filename: Name of file to encrypt
            encryption_key: Optional encryption key
            
        Returns:
            StorageResult with encryption details
        """
        pass

    @abstractmethod
    def decrypt_file(
        self,
        filename: StorageFileName,
        decryption_key: Optional[str] = None
    ) -> StorageResult:
        """
        Decrypt a stored file (stub for future implementation).
        
        Args:
            filename: Name of file to decrypt
            decryption_key: Optional decryption key
            
        Returns:
            StorageResult with decryption details
        """
        pass

    @abstractmethod
    def set_access_permissions(
        self,
        filename: StorageFileName,
        permissions: Dict[str, Any],
        user_id: Optional[UserId] = None
    ) -> StorageResult:
        """
        Set access permissions for a file (stub for future implementation).
        
        Args:
            filename: Name of file
            permissions: Permission settings
            user_id: User setting permissions
            
        Returns:
            StorageResult with permission details
        """
        pass

    @abstractmethod
    def check_access_permissions(
        self,
        filename: StorageFileName,
        user_id: UserId,
        operation: str
    ) -> bool:
        """
        Check if user has permission for operation (stub for future implementation).
        
        Args:
            filename: Name of file
            user_id: User to check permissions for
            operation: Operation to check (read, write, delete)
            
        Returns:
            True if permitted, False otherwise
        """
        pass