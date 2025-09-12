#!/usr/bin/env python3
"""
Unit Tests for Temporary Files Audit Logger

Tests the core functionality of audit_logger.py utility including:
- File logging operations
- Status updates
- File listing
- Error handling
- Edge cases
"""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime
import sys

# Add the temp_dev_files directory to Python path for imports
temp_dev_files_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'temp_dev_files')
sys.path.insert(0, temp_dev_files_path)

from audit_logger import log_temp_file, update_file_status, list_temp_files, get_file_size

class TestAuditLoggerCore(unittest.TestCase):
    """Test core audit logger functionality."""
    
    def setUp(self):
        """Set up test environment with temporary audit file."""
        self.test_dir = tempfile.mkdtemp()
        self.original_temp_dir = None
        self.original_audit_file = None
        
        # Create test audit file structure
        self.test_audit_content = """# Temporary Development Files Audit Log

This file automatically tracks all temporary files created to assist with development, refactoring, and restructuring work.

## Directory Structure
- `migration_scripts/` - Scripts for migrating code structure, packages, tests
- `debug_tools/` - Debug scripts, environment analyzers, diagnostic tools  
- `refactoring_helpers/` - Helper scripts for restructuring code
- `logs_and_dumps/` - Log files, cache dumps, temporary data exports

## File Audit Trail

| Date Created | File Path | Purpose | Size | Status | Notes |
|-------------|-----------|---------|------|--------|-------|
| 2025-09-10 | - | Audit system initialized | - | Active | Base tracking system created |

## Cleanup Guidelines

### Retention Policy
- **Migration Scripts**: Keep until migration is fully validated (30+ days)
- **Debug Tools**: Keep until issue is resolved, then archive
- **Refactoring Helpers**: Keep until refactor is complete and tested
- **Logs & Dumps**: Clean weekly, keep only recent or significant logs

---
*Last updated: 2025-09-10*"""
        
        self.test_audit_file = Path(self.test_dir) / "TEMP_FILES_AUDIT.md"
        with open(self.test_audit_file, 'w') as f:
            f.write(self.test_audit_content)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_get_file_size_existing_file(self):
        """Test get_file_size with existing file."""
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Hello World!")
        
        size = get_file_size(test_file)
        self.assertEqual(size, "12.0 B")
    
    def test_get_file_size_nonexistent_file(self):
        """Test get_file_size with non-existent file."""
        size = get_file_size("/path/to/nonexistent/file.txt")
        self.assertEqual(size, "Unknown")
    
    def test_get_file_size_units(self):
        """Test get_file_size unit conversions."""
        test_file = Path(self.test_dir) / "large.txt"
        
        # Create 1KB+ file
        test_file.write_text("x" * 1500)
        size = get_file_size(test_file)
        self.assertTrue(size.endswith("KB"))
        self.assertIn("1.5", size)

class TestAuditLoggerIntegration(unittest.TestCase):
    """Integration tests for audit logger with file system operations."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_audit_file = Path(self.test_dir) / "TEMP_FILES_AUDIT.md"
        
        # Patch the global AUDIT_FILE variable
        import audit_logger
        self.original_audit_file = audit_logger.AUDIT_FILE
        self.original_temp_dir = audit_logger.TEMP_DIR
        audit_logger.AUDIT_FILE = self.test_audit_file
        audit_logger.TEMP_DIR = Path(self.test_dir)
        
        # Create initial audit file
        audit_content = """# Temporary Development Files Audit Log

## File Audit Trail

| Date Created | File Path | Purpose | Size | Status | Notes |
|-------------|-----------|---------|------|--------|-------|
| 2025-09-10 | - | Audit system initialized | - | Active | Base tracking system created |

## Cleanup Guidelines
*Last updated: 2025-09-10*"""
        
        with open(self.test_audit_file, 'w') as f:
            f.write(audit_content)
    
    def tearDown(self):
        """Restore original configuration."""
        import audit_logger
        audit_logger.AUDIT_FILE = self.original_audit_file
        audit_logger.TEMP_DIR = self.original_temp_dir
        
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_log_temp_file_integration(self):
        """Test logging a temporary file end-to-end."""
        # Create a test file
        test_file = Path(self.test_dir) / "debug_tools" / "test_script.py"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text("print('test')")
        
        # Log the file
        log_temp_file("debug_tools/test_script.py", "Test debug script", "Active", "Integration test")
        
        # Verify it was logged
        with open(self.test_audit_file, 'r') as f:
            content = f.read()
        
        self.assertIn("debug_tools/test_script.py", content)
        self.assertIn("Test debug script", content)
        self.assertIn("Active", content)
        self.assertIn("Integration test", content)
        
        # Verify size calculation (allow for slight variations in file size)
        self.assertRegex(content, r"1[23]\.0 B")  # "print('test')" might be 12 or 13 bytes depending on encoding
    
    def test_update_file_status_integration(self):
        """Test updating file status end-to-end."""
        # First log a file
        log_temp_file("migration_scripts/migrate.py", "Migration script", "Active")
        
        # Then update its status
        update_file_status("migration_scripts/migrate.py", "Completed", "Migration successful")
        
        # Verify the update
        with open(self.test_audit_file, 'r') as f:
            content = f.read()
        
        self.assertIn("migration_scripts/migrate.py", content)
        self.assertIn("Completed", content)
        self.assertIn("Migration successful", content)
        self.assertNotIn("Active", content.split("migration_scripts/migrate.py")[1].split("\n")[0])

class TestAuditLoggerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up edge case test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Patch the global variables
        import audit_logger
        self.original_audit_file = audit_logger.AUDIT_FILE
        self.original_temp_dir = audit_logger.TEMP_DIR
        audit_logger.TEMP_DIR = Path(self.test_dir)
    
    def tearDown(self):
        """Restore original configuration."""
        import audit_logger
        audit_logger.AUDIT_FILE = self.original_audit_file
        audit_logger.TEMP_DIR = self.original_temp_dir
        
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_log_temp_file_no_audit_file(self):
        """Test logging when audit file doesn't exist."""
        import audit_logger
        audit_logger.AUDIT_FILE = Path(self.test_dir) / "nonexistent.md"
        
        # Should handle gracefully - we'll capture print output
        import io
        import contextlib
        
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            log_temp_file("test.py", "Test file")
        
        output = captured_output.getvalue()
        self.assertIn("Error: Audit file", output)
    
    def test_update_nonexistent_file(self):
        """Test updating a file that wasn't logged."""
        import audit_logger
        
        # Create minimal audit file
        audit_file = Path(self.test_dir) / "audit.md"
        audit_file.write_text("# Audit\n\n## File Audit Trail\n\n*Last updated: 2025-09-10*")
        audit_logger.AUDIT_FILE = audit_file
        
        import io
        import contextlib
        
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            update_file_status("nonexistent.py", "Completed")
        
        output = captured_output.getvalue()
        self.assertIn("File not found in audit log", output)
    
    def test_special_characters_in_file_paths(self):
        """Test handling files with special characters."""
        import audit_logger
        
        # Create audit file
        audit_file = Path(self.test_dir) / "audit.md"
        content = """# Audit

## File Audit Trail

| Date Created | File Path | Purpose | Size | Status | Notes |
|-------------|-----------|---------|------|--------|-------|

## Cleanup Guidelines
*Last updated: 2025-09-10*"""
        audit_file.write_text(content)
        audit_logger.AUDIT_FILE = audit_file
        
        # Test with special characters
        log_temp_file("debug_tools/test-file_v2.1.py", "Test with special chars", "Active")
        
        with open(audit_file, 'r') as f:
            audit_content = f.read()
        
        self.assertIn("test-file_v2.1.py", audit_content)

if __name__ == '__main__':
    unittest.main(verbosity=2)
