# Storage Component - README

## Overview
This folder contains utilities and stubs for local and future cloud storage of resumes, job data, and analytics outputs.

## Main Components
- **SecureStorage:** Centralized class for all file, metadata, and log operations. Includes stubs for encryption, access control, and cloud integration.
- **LocalFS:** (Legacy stub) For local file system storage and retrieval.

## Extensibility
- SecureStorage is designed for future upgrades:
	- Encryption at rest
	- Access control
	- Cloud storage integration (S3, Azure Blob, etc.)
See [STUB_CATALOG.md](../../STUB_CATALOG.md) for a full list of stubs and extension points.

## Usage
- Use SecureStorage for all file, metadata, and log operations in POC workflows.


---

_Last updated: September 8, 2025_
