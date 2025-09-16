# Storage Component

The Storage component provides a secure, centralized storage abstraction layer for the TPM Job Finder POC system. It implements secure file operations, metadata management, audit logging, and provides extension points for cloud storage integration.

## Architecture Overview

The storage component follows a secure-by-design pattern with comprehensive audit trails:

```
storage/
├── secure_storage.py           # Centralized secure storage implementation
└── __init__.py                 # Module initialization
```

## Core Components

### 1. SecureStorage (secure_storage.py)
**Purpose**: Centralized secure storage for files, metadata, and audit logs
- **File operations**: Secure file saving, retrieval, and management
- **Metadata management**: Structured metadata storage with JSON serialization
- **Audit logging**: Comprehensive audit trails for all storage operations
- **Extension stubs**: Ready-to-implement encryption, access control, and cloud integration
- **Directory management**: Automatic creation and management of storage directories

## Data Architecture

### Storage Directory Structure
```
secure_storage/
├── files/                      # File storage directory
│   ├── sample_resume.txt       # User files and documents
│   └── [other_files]
├── metadata/                   # Metadata storage directory  
│   ├── sample_resume.txt.json  # File metadata in JSON format
│   └── [other_metadata]
└── logs/                       # Audit logging directory
    └── audit.jsonl             # JSON Lines audit log
```

### Metadata Schema
```python
# Example metadata structure
{
    "user_id": "user123",
    "file_type": "pdf",
    "upload_timestamp": "2025-01-15T10:30:00Z",
    "file_size": 1024000,
    "processing_status": "completed",
    "tags": ["resume", "technical"],
    "security_classification": "personal"
}
```

### Audit Log Schema
```python
# Example audit log entry
{
    "action": "save_file",
    "details": {
        "filename": "resume.pdf",
        "user_id": "user123",
        "timestamp": "2025-01-15T10:30:00Z",
        "client_ip": "192.168.1.100"
    }
}
```

## Public API

### SecureStorage Class

```python
from tpm_job_finder_poc.storage.secure_storage import SecureStorage

class SecureStorage:
    def __init__(self, base_dir: str = "secure_storage")
    
    # File operations
    def save_file(self, src_path: str, dest_name: str) -> str
    def retrieve_file(self, filename: str) -> Optional[str]
    def delete_file(self, filename: str) -> bool
    def list_files(self) -> List[str]
    
    # Metadata operations
    def save_metadata(self, filename: str, metadata: Dict[str, Any]) -> str
    def retrieve_metadata(self, filename: str) -> Optional[Dict[str, Any]]
    def delete_metadata(self, filename: str) -> bool
    def list_metadata(self) -> List[str]
    
    # Audit logging
    def log_action(self, action: str, details: Dict[str, Any]) -> None
    
    # Extension stubs (for future implementation)
    def _encryption_stub(self, path: str) -> None
    def _access_control_stub(self, path: str) -> None
    def _cloud_integration_stub(self, path: str) -> None
```

## Usage Examples

### 1. Basic File Operations
```python
from tpm_job_finder_poc.storage.secure_storage import SecureStorage

# Initialize secure storage
storage = SecureStorage()

# Save a file with automatic audit logging
file_path = storage.save_file("local_resume.pdf", "user123_resume.pdf")
print(f"File saved to: {file_path}")

# Save metadata for the file
metadata = {
    "user_id": "user123",
    "file_type": "pdf",
    "upload_timestamp": "2025-01-15T10:30:00Z",
    "processing_status": "pending"
}
meta_path = storage.save_metadata("user123_resume.pdf", metadata)

# Retrieve file for processing
stored_file_path = storage.retrieve_file("user123_resume.pdf")
if stored_file_path:
    print(f"File location: {stored_file_path}")

# List all stored files
files = storage.list_files()
print(f"Stored files: {files}")
```

### 2. Metadata Management
```python
from tpm_job_finder_poc.storage.secure_storage import SecureStorage

storage = SecureStorage()

# Save comprehensive metadata
metadata = {
    "user_id": "user456",
    "original_filename": "senior_pm_resume.pdf",
    "file_type": "pdf",
    "file_size": 2048000,
    "upload_timestamp": "2025-01-15T14:20:00Z",
    "processing_status": "completed",
    "tags": ["resume", "product_management", "senior"],
    "security_classification": "personal",
    "retention_policy": "5_years",
    "last_accessed": "2025-01-15T14:25:00Z"
}

# Save metadata
storage.save_metadata("user456_resume.pdf", metadata)

# Retrieve and update metadata
existing_metadata = storage.retrieve_metadata("user456_resume.pdf")
if existing_metadata:
    existing_metadata["last_accessed"] = "2025-01-15T15:00:00Z"
    existing_metadata["access_count"] = existing_metadata.get("access_count", 0) + 1
    storage.save_metadata("user456_resume.pdf", existing_metadata)

# List all metadata files
metadata_files = storage.list_metadata()
print(f"Metadata files: {metadata_files}")
```

### 3. Audit Logging and Compliance
```python
from tpm_job_finder_poc.storage.secure_storage import SecureStorage
import json

storage = SecureStorage()

# Manual audit logging for custom operations
storage.log_action("user_login", {
    "user_id": "user123",
    "timestamp": "2025-01-15T10:00:00Z",
    "ip_address": "192.168.1.100",
    "user_agent": "TPM-Job-Finder-CLI/1.0"
})

storage.log_action("job_search_initiated", {
    "user_id": "user123",
    "search_terms": ["product manager", "remote"],
    "filters": {"location": "worldwide", "salary_min": 100000}
})

# Read audit logs for compliance reporting
def generate_audit_report(user_id: str = None, action: str = None):
    """Generate audit report with optional filtering."""
    audit_log_path = f"{storage.base_dir}/logs/audit.jsonl"
    
    with open(audit_log_path, 'r') as f:
        entries = [json.loads(line) for line in f]
    
    # Filter entries
    filtered_entries = entries
    if user_id:
        filtered_entries = [e for e in filtered_entries if e.get('details', {}).get('user_id') == user_id]
    if action:
        filtered_entries = [e for e in filtered_entries if e.get('action') == action]
    
    return filtered_entries

# Generate compliance report
user_activity = generate_audit_report(user_id="user123")
print(f"User activity log: {len(user_activity)} entries")
```

### 4. Integration with Job Processing Pipeline
```python
from tpm_job_finder_poc.storage.secure_storage import SecureStorage
from datetime import datetime

def process_resume_for_job_application(resume_path: str, job_id: str, user_id: str):
    """Process resume for job application with secure storage."""
    storage = SecureStorage()
    
    # Save resume securely
    secure_filename = f"{user_id}_{job_id}_resume.pdf"
    stored_path = storage.save_file(resume_path, secure_filename)
    
    # Save processing metadata
    metadata = {
        "user_id": user_id,
        "job_id": job_id,
        "original_filename": resume_path.split('/')[-1],
        "processing_timestamp": datetime.now().isoformat(),
        "processing_status": "in_progress",
        "application_context": {
            "job_platform": "linkedin",
            "application_method": "automated",
            "resume_version": "v1.2"
        }
    }
    storage.save_metadata(secure_filename, metadata)
    
    # Log application attempt
    storage.log_action("resume_processing_started", {
        "user_id": user_id,
        "job_id": job_id,
        "resume_filename": secure_filename,
        "processing_pipeline": "automated_application"
    })
    
    try:
        # Simulate resume processing
        process_resume_content(stored_path)
        
        # Update metadata on success
        metadata["processing_status"] = "completed"
        metadata["completion_timestamp"] = datetime.now().isoformat()
        storage.save_metadata(secure_filename, metadata)
        
        # Log successful processing
        storage.log_action("resume_processing_completed", {
            "user_id": user_id,
            "job_id": job_id,
            "status": "success"
        })
        
    except Exception as e:
        # Update metadata on failure
        metadata["processing_status"] = "failed"
        metadata["error_message"] = str(e)
        metadata["failure_timestamp"] = datetime.now().isoformat()
        storage.save_metadata(secure_filename, metadata)
        
        # Log processing failure
        storage.log_action("resume_processing_failed", {
            "user_id": user_id,
            "job_id": job_id,
            "error": str(e)
        })
        raise

def process_resume_content(resume_path: str):
    """Placeholder for resume processing logic."""
    # Actual resume processing would go here
    pass
```

### 5. Bulk Operations and Management
```python
from tpm_job_finder_poc.storage.secure_storage import SecureStorage
import os
from typing import List, Dict

def bulk_file_management(storage: SecureStorage):
    """Demonstrate bulk file operations."""
    
    # Bulk file upload
    source_files = [
        ("resumes/resume1.pdf", "user1_technical_resume.pdf"),
        ("resumes/resume2.pdf", "user1_management_resume.pdf"),
        ("cover_letters/cover1.txt", "user1_cover_letter.txt")
    ]
    
    for src_path, dest_name in source_files:
        if os.path.exists(src_path):
            storage.save_file(src_path, dest_name)
            storage.save_metadata(dest_name, {
                "batch_upload": True,
                "upload_session": "session_2025_01_15",
                "user_id": "user1"
            })
    
    # Bulk metadata update
    all_files = storage.list_files()
    for filename in all_files:
        metadata = storage.retrieve_metadata(filename)
        if metadata and metadata.get("user_id") == "user1":
            metadata["last_reviewed"] = "2025-01-15T16:00:00Z"
            metadata["review_status"] = "pending"
            storage.save_metadata(filename, metadata)
    
    # File cleanup based on criteria
    def cleanup_old_files(older_than_days: int = 30):
        """Clean up files older than specified days."""
        import time
        cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
        
        for filename in storage.list_files():
            file_path = storage.retrieve_file(filename)
            if file_path and os.path.getmtime(file_path) < cutoff_time:
                storage.log_action("file_cleanup", {
                    "filename": filename,
                    "reason": f"older_than_{older_than_days}_days"
                })
                storage.delete_file(filename)
                storage.delete_metadata(filename)
    
    # Example: cleanup files older than 30 days
    # cleanup_old_files(30)
```

## Architecture Decisions

### 1. Secure-by-Design Pattern
- **Audit logging**: All operations automatically logged for compliance
- **Metadata separation**: File content and metadata stored separately for security
- **Extension stubs**: Ready-to-implement security features
- **Path validation**: Secure file path handling throughout

### 2. Flexible Storage Architecture
- **Local-first design**: Optimized for local development and small deployments
- **Cloud-ready stubs**: Extension points for cloud storage integration
- **Directory isolation**: Separate directories for different data types
- **JSON metadata**: Human-readable, debuggable metadata format

### 3. Audit and Compliance Focus
- **JSONL format**: Machine-readable audit logs for analysis
- **Comprehensive logging**: All storage operations tracked
- **Retention policies**: Metadata support for data retention management
- **Access patterns**: Detailed tracking of file access patterns

### 4. Integration-Friendly Design
- **Simple API**: Straightforward methods for common operations
- **Error handling**: Robust error handling with detailed logging
- **Batch operations**: Support for efficient bulk operations
- **Metadata richness**: Flexible metadata schema for various use cases

## Security Features

### Current Security Measures
```python
# Automatic audit logging
def save_file(self, src_path: str, dest_name: str) -> str:
    # File operation with automatic logging
    dest_path = os.path.join(self.files_dir, dest_name)
    with open(src_path, "rb") as src, open(dest_path, "wb") as dst:
        dst.write(src.read())
    
    # Security extension points
    self._encryption_stub(dest_path)  # Future: file encryption
    self._access_control_stub(dest_path)  # Future: access control
    
    # Audit logging
    self.log_action("save_file", {"dest_name": dest_name})
    return dest_path
```

### Future Security Enhancements (Stubs)
```python
def _encryption_stub(self, path: str) -> None:
    """Stub for encryption at rest implementation."""
    # Future implementation:
    # - File-level encryption using AES-256
    # - Key management integration
    # - Encryption metadata tracking
    pass

def _access_control_stub(self, path: str) -> None:
    """Stub for access control implementation."""
    # Future implementation:
    # - User-based access control
    # - Role-based permissions
    # - File access logging
    pass

def _cloud_integration_stub(self, path: str) -> None:
    """Stub for cloud storage integration."""
    # Future implementation:
    # - AWS S3 integration
    # - Google Cloud Storage
    # - Azure Blob Storage
    # - Hybrid cloud/local storage
    pass
```

## Performance Characteristics

### Local Storage Performance
- **File operations**: Direct filesystem operations for optimal speed
- **Metadata access**: JSON files for fast metadata retrieval
- **Audit logging**: Append-only JSONL for minimal I/O overhead
- **Directory structure**: Organized for efficient file system operations

### Scalability Considerations
- **Batch operations**: Efficient bulk file handling
- **Metadata indexing**: Structured for future database migration
- **Cloud readiness**: Architecture supports cloud storage backends
- **Audit log rotation**: Supports log rotation for long-term storage

## Testing

### Unit Tests
```bash
# Test core storage functionality
pytest tests/unit/test_storage/test_secure_storage.py -v

# Test file operations
pytest tests/unit/test_storage/test_file_operations.py -v

# Test metadata management
pytest tests/unit/test_storage/test_metadata_operations.py -v

# Test audit logging
pytest tests/unit/test_storage/test_audit_logging.py -v
```

### Integration Tests
```bash
# Test storage integration with other components
pytest tests/integration/test_storage_integration.py -v

# Test file processing pipeline
pytest tests/integration/test_file_processing_pipeline.py -v

# Test audit compliance
pytest tests/integration/test_audit_compliance.py -v
```

### Test Examples
```python
import pytest
import tempfile
import shutil
from pathlib import Path
from tpm_job_finder_poc.storage.secure_storage import SecureStorage

@pytest.fixture
def temp_storage():
    """Create temporary storage for testing."""
    temp_dir = tempfile.mkdtemp()
    storage = SecureStorage(temp_dir)
    yield storage
    shutil.rmtree(temp_dir)

def test_file_save_and_retrieve(temp_storage):
    """Test basic file save and retrieve operations."""
    # Create test file
    test_content = b"Test resume content"
    test_file = tempfile.NamedTemporaryFile(delete=False)
    test_file.write(test_content)
    test_file.close()
    
    try:
        # Save file
        saved_path = temp_storage.save_file(test_file.name, "test_resume.txt")
        assert saved_path is not None
        
        # Retrieve file
        retrieved_path = temp_storage.retrieve_file("test_resume.txt")
        assert retrieved_path is not None
        
        # Verify content
        with open(retrieved_path, 'rb') as f:
            assert f.read() == test_content
            
    finally:
        Path(test_file.name).unlink()

def test_metadata_operations(temp_storage):
    """Test metadata save and retrieve operations."""
    metadata = {
        "user_id": "test123",
        "file_type": "pdf",
        "tags": ["resume", "test"]
    }
    
    # Save metadata
    temp_storage.save_metadata("test_file.pdf", metadata)
    
    # Retrieve metadata
    retrieved_metadata = temp_storage.retrieve_metadata("test_file.pdf")
    assert retrieved_metadata == metadata
    
    # Update metadata
    metadata["updated"] = True
    temp_storage.save_metadata("test_file.pdf", metadata)
    
    # Verify update
    updated_metadata = temp_storage.retrieve_metadata("test_file.pdf")
    assert updated_metadata["updated"] is True

def test_audit_logging(temp_storage):
    """Test audit logging functionality."""
    # Perform operations that should be logged
    temp_storage.log_action("test_action", {"test": "data"})
    
    # Check audit log exists
    audit_log_path = Path(temp_storage.logs_dir) / "audit.jsonl"
    assert audit_log_path.exists()
    
    # Verify log content
    with open(audit_log_path, 'r') as f:
        log_entries = [json.loads(line) for line in f]
    
    assert len(log_entries) > 0
    assert log_entries[-1]["action"] == "test_action"
    assert log_entries[-1]["details"]["test"] == "data"

def test_file_deletion(temp_storage):
    """Test file and metadata deletion."""
    # Create test file and metadata
    test_file = tempfile.NamedTemporaryFile(delete=False)
    test_file.write(b"test content")
    test_file.close()
    
    try:
        # Save file and metadata
        temp_storage.save_file(test_file.name, "test_delete.txt")
        temp_storage.save_metadata("test_delete.txt", {"test": "metadata"})
        
        # Verify they exist
        assert temp_storage.retrieve_file("test_delete.txt") is not None
        assert temp_storage.retrieve_metadata("test_delete.txt") is not None
        
        # Delete file and metadata
        assert temp_storage.delete_file("test_delete.txt") is True
        assert temp_storage.delete_metadata("test_delete.txt") is True
        
        # Verify they're gone
        assert temp_storage.retrieve_file("test_delete.txt") is None
        assert temp_storage.retrieve_metadata("test_delete.txt") is None
        
    finally:
        Path(test_file.name).unlink(missing_ok=True)
```

## Dependencies

### Core Dependencies
- **os**: File system operations
- **json**: Metadata serialization and audit logging
- **typing**: Type hints for API clarity

### Internal Dependencies
- **None**: Storage component is designed to be dependency-free for maximum portability

## Security Considerations

### Data Protection
- **Local file storage**: All files stored in secure local directories
- **Metadata separation**: File content and metadata stored separately
- **Audit trails**: Comprehensive logging of all storage operations
- **Path validation**: Secure file path handling to prevent traversal attacks

### Future Security Enhancements
- **Encryption at rest**: File-level encryption for sensitive data
- **Access control**: User-based file access permissions
- **Cloud security**: Secure cloud storage integration with encryption in transit
- **Key management**: Integration with enterprise key management systems

## Future Enhancements

### Planned Features
1. **Cloud storage integration**: AWS S3, Google Cloud Storage, Azure Blob Storage
2. **Database backends**: PostgreSQL, MongoDB for metadata and audit logs
3. **Encryption support**: AES-256 encryption for files and metadata
4. **Access control**: Role-based access control and user permissions
5. **Data lifecycle management**: Automated retention policies and cleanup

### Performance Improvements
1. **Caching layer**: Redis-based caching for frequently accessed files
2. **Compression**: File compression for storage efficiency
3. **Indexing**: Database indexing for fast metadata queries
4. **Streaming**: Large file streaming support for memory efficiency

### Integration Enhancements
1. **Message queues**: Asynchronous file processing with queues
2. **Event system**: File operation events for reactive architectures
3. **API layer**: RESTful API for external storage access
4. **Monitoring**: Prometheus metrics for storage operations