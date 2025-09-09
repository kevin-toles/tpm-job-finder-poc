
# Resume Component - README

## Overview
This folder contains services and utilities for resume intake, storage, and metadata registration. Designed for extensibility and future UI/API integration.

## Supported File Types
- .txt
- .pdf
- .doc
- .docx

## Main Components
- **ResumeUploader:** Backend service for accepting txt/pdf/doc/docx resumes, registering metadata, locating files, and saving to ResumeStore for e2e/manual testing.
- **ResumeStore:** Local storage and secure metadata management.
	- Stubs for:
		- Access control (future: restrict file access by user/role)
		- Encryption (future: encrypt resumes/metadata at rest)
		- Audit logging (future: compliance and traceability)
		- API endpoints (future: RESTful interface for resume ops)
See [STUB_CATALOG.md](../../STUB_CATALOG.md) for a full list of stubs and extension points.

## Main Responsibilities
- **File Intake:** Accepts resume files from a designated directory or via upload. Can locate files by filename for manual/e2e testing.
- **Metadata Registration:** Extracts and stores metadata (filename, type, size, user ID, etc.) for downstream processing.
- **Storage:** Stores files and metadata locally, ready for future integration with cloud/local storage or a database. Stubs for access control, encryption, and audit logging.
- **Integration Points:** Can be called by a UI, CLI, or automated workflow. Metadata and file paths are passed to downstream components (e.g., resume parser, scoring engine).

## Main Methods
- `upload_resume(file_path, user_id=None)`: Accepts a file path, registers metadata, and saves to ResumeStore.
- `register_metadata(metadata)`: Stores metadata in the system (stubbed; ready for DB/file integration).
- `find_resume(filename)`: Locates a resume file in a designated directory for manual/e2e testing.
- `save_resume(file_path, metadata)`: Save resume and metadata locally, with schema validation.
- `retrieve_resume(filename)`: Retrieve resume file by filename.
- `retrieve_metadata(filename)`: Retrieve metadata JSON by filename.
- `delete_resume(filename)`: Delete resume file and metadata.
- `list_resumes()`: List all stored resume files.
- `list_metadata()`: List all stored metadata files.
- API stubs for save, retrieve, delete, and audit log actions.

## Extensibility
- UI/API can be added to call backend methods for real user uploads.
- Storage logic can be extended for cloud/local storage or database integration.
- Access control, encryption, and audit logging can be implemented for production.

## Usage
- Place resume files in a designated directory for manual/e2e testing.
- Use ResumeUploader methods to intake, register, and save resumes to ResumeStore.
- Use ResumeStore to retrieve, delete, and list resumes and metadata.

## Security Notes
- Stubs for access control, encryption, and audit logging are included for future upgrades. See STUB_CATALOG.md for details.

## Project Goal
To provide a modular, extensible backend for resume intake, storage, and registration, supporting rapid POC development and future production features.

---

_Last updated: September 8, 2025_
