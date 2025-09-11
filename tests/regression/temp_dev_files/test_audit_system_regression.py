#!/usr/bin/env python3
"""
Regression Tests for Temporary Files Audit System

Tests to prevent regressions in the audit system including:
- Backward compatibility with existing audit files
- Performance characteristics
- Data integrity over time
- Feature stability
"""

import unittest
import tempfile
import os
import subprocess
import sys
import time
from pathlib import Path
import shutil
from datetime import datetime

class TestAuditSystemRegression(unittest.TestCase):
    """Regression tests to ensure audit system stability."""
    
    def setUp(self):
        """Set up regression test environment."""
        self.test_root = tempfile.mkdtemp()
        self.temp_dev_files = Path(self.test_root) / "temp_dev_files"
        self.temp_dev_files.mkdir()
        
        # Copy audit_logger.py for testing
        original_audit_logger = Path(__file__).parent.parent.parent.parent / "temp_dev_files" / "audit_logger.py"
        test_audit_logger = self.temp_dev_files / "audit_logger.py"
        shutil.copy2(original_audit_logger, test_audit_logger)
    
    def tearDown(self):
        """Clean up regression test environment."""
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
    
    def create_audit_file(self, content):
        """Helper to create audit file with specific content."""
        audit_file = self.temp_dev_files / "TEMP_FILES_AUDIT.md"
        with open(audit_file, 'w') as f:
            f.write(content)
        return audit_file
    
    def run_command(self, args):
        """Helper to run audit_logger commands."""
        cmd = [sys.executable, str(self.temp_dev_files / "audit_logger.py")] + args
        result = subprocess.run(
            cmd,
            cwd=self.temp_dev_files,
            capture_output=True,
            text=True
        )
        return result
    
    def test_backward_compatibility_original_format(self):
        """Test compatibility with original audit file format."""
        # Create audit file in original format
        original_format = """# Temporary Development Files Audit Log

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
        
        self.create_audit_file(original_format)
        
        # Should be able to log new files
        result = self.run_command([
            "log", "debug_tools/test.py", "Test backward compatibility", "Active"
        ])
        self.assertEqual(result.returncode, 0)
        
        # Should be able to list files
        result = self.run_command(["list"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("test.py", result.stdout)
    
    def test_malformed_audit_file_handling(self):
        """Test handling of malformed audit files."""
        # Test with missing table structure
        malformed_content = """# Temporary Development Files Audit Log

Some content but no table structure.

## Cleanup Guidelines
*Last updated: 2025-09-10*"""
        
        self.create_audit_file(malformed_content)
        
        result = self.run_command([
            "log", "debug_tools/test.py", "Test malformed handling"
        ])
        # Should handle gracefully
        self.assertIn("Error:", result.stdout)
    
    def test_large_audit_file_performance(self):
        """Test performance with large audit files."""
        # Create audit file with many entries
        base_content = """# Temporary Development Files Audit Log

## File Audit Trail

| Date Created | File Path | Purpose | Size | Status | Notes |
|-------------|-----------|---------|------|--------|-------|
| 2025-09-10 | - | Audit system initialized | - | Active | Base tracking system created |"""
        
        # Add many entries
        for i in range(100):
            base_content += f"\n| 2025-09-10 | debug_tools/file_{i:03d}.py | Test file {i} | 1.0 KB | Active | Generated entry |"
        
        base_content += "\n\n## Cleanup Guidelines\n*Last updated: 2025-09-10*"
        
        self.create_audit_file(base_content)
        
        # Time the operations
        start_time = time.time()
        result = self.run_command([
            "log", "debug_tools/new_file.py", "Performance test file", "Active"
        ])
        log_time = time.time() - start_time
        
        self.assertEqual(result.returncode, 0)
        self.assertLess(log_time, 5.0)  # Should complete within 5 seconds
        
        # Test list performance
        start_time = time.time()
        result = self.run_command(["list"])
        list_time = time.time() - start_time
        
        self.assertEqual(result.returncode, 0)
        self.assertLess(list_time, 3.0)  # Should complete within 3 seconds
        self.assertIn("new_file.py", result.stdout)
    
    def test_special_characters_regression(self):
        """Test handling of special characters doesn't regress."""
        self.create_audit_file("""# Temporary Development Files Audit Log

## File Audit Trail

| Date Created | File Path | Purpose | Size | Status | Notes |
|-------------|-----------|---------|------|--------|-------|

## Cleanup Guidelines
*Last updated: 2025-09-10*""")
        
        # Test various special characters that have caused issues
        special_cases = [
            ("debug_tools/file-with-dashes.py", "File with dashes"),
            ("debug_tools/file_with_underscores.py", "File with underscores"),
            ("debug_tools/file.with.dots.py", "File with dots"),
            ("debug_tools/file with spaces.py", "File with spaces"),
            ("debug_tools/file(with)parens.py", "File with parentheses"),
        ]
        
        for file_path, purpose in special_cases:
            result = self.run_command(["log", file_path, purpose, "Active"])
            self.assertEqual(result.returncode, 0, f"Failed for {file_path}")
            
            # Verify it can be updated
            result = self.run_command(["update", file_path, "Completed"])
            self.assertEqual(result.returncode, 0, f"Failed update for {file_path}")
        
        # Verify all are listed correctly
        result = self.run_command(["list"])
        self.assertEqual(result.returncode, 0)
        
        for file_path, _ in special_cases:
            self.assertIn(file_path.split('/')[-1], result.stdout)
    
    def test_concurrent_access_safety(self):
        """Test safety when multiple processes might access audit file."""
        self.create_audit_file("""# Temporary Development Files Audit Log

## File Audit Trail

| Date Created | File Path | Purpose | Size | Status | Notes |
|-------------|-----------|---------|------|--------|-------|

## Cleanup Guidelines
*Last updated: 2025-09-10*""")
        
        # Simulate concurrent logging attempts
        import threading
        import queue
        
        results = queue.Queue()
        
        def log_file(file_num):
            result = self.run_command([
                "log", f"debug_tools/concurrent_{file_num}.py", 
                f"Concurrent test {file_num}", "Active"
            ])
            results.put((file_num, result.returncode))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check all operations succeeded
        while not results.empty():
            file_num, return_code = results.get()
            self.assertEqual(return_code, 0, f"Concurrent operation {file_num} failed")
        
        # Verify all files were logged
        result = self.run_command(["list"])
        for i in range(5):
            self.assertIn(f"concurrent_{i}.py", result.stdout)
    
    def test_data_integrity_over_operations(self):
        """Test data integrity maintained over many operations."""
        self.create_audit_file("""# Temporary Development Files Audit Log

## File Audit Trail

| Date Created | File Path | Purpose | Size | Status | Notes |
|-------------|-----------|---------|------|--------|-------|

## Cleanup Guidelines
*Last updated: 2025-09-10*""")
        
        # Perform many operations
        file_operations = []
        
        # Log many files
        for i in range(20):
            file_path = f"debug_tools/integrity_test_{i:02d}.py"
            result = self.run_command([
                "log", file_path, f"Integrity test file {i}", "Active"
            ])
            self.assertEqual(result.returncode, 0)
            file_operations.append(file_path)
        
        # Update statuses multiple times
        statuses = ["In Progress", "Testing", "Completed", "Archived"]
        for file_path in file_operations[:5]:
            for status in statuses:
                result = self.run_command(["update", file_path, status])
                self.assertEqual(result.returncode, 0)
        
        # Verify data integrity
        audit_file = self.temp_dev_files / "TEMP_FILES_AUDIT.md"
        with open(audit_file, 'r') as f:
            content = f.read()
        
        # Each file should appear exactly once
        for file_path in file_operations:
            file_lines = [line for line in content.split('\n') if file_path in line]
            self.assertEqual(len(file_lines), 1, f"File {file_path} should appear exactly once")
        
        # Final statuses should be correct
        for file_path in file_operations[:5]:
            self.assertIn("Archived", content.split(file_path)[1].split('\n')[0])
        
        for file_path in file_operations[5:]:
            self.assertIn("Active", content.split(file_path)[1].split('\n')[0])
    
    def test_edge_case_file_sizes(self):
        """Test edge cases in file size calculation."""
        self.create_audit_file("""# Temporary Development Files Audit Log

## File Audit Trail

| Date Created | File Path | Purpose | Size | Status | Notes |
|-------------|-----------|---------|------|--------|-------|

## Cleanup Guidelines
*Last updated: 2025-09-10*""")
        
        # Create files of various sizes
        test_cases = [
            ("empty.py", ""),  # 0 bytes
            ("small.py", "x"),  # 1 byte
            ("medium.py", "x" * 1024),  # 1 KB
            ("large.py", "x" * (1024 * 1024)),  # 1 MB
        ]
        
        for filename, content in test_cases:
            file_path = self.temp_dev_files / "debug_tools" / filename
            file_path.parent.mkdir(exist_ok=True)
            file_path.write_text(content)
            
            result = self.run_command([
                "log", f"debug_tools/{filename}", f"Size test {filename}", "Active"
            ])
            self.assertEqual(result.returncode, 0)
        
        # Verify sizes are calculated correctly
        result = self.run_command(["list"])
        self.assertEqual(result.returncode, 0)
        
        # Check for appropriate size units
        self.assertIn("0.0 B", result.stdout)  # empty file
        self.assertIn("1.0 B", result.stdout)  # 1 byte file
        self.assertIn("1.0 KB", result.stdout)  # 1 KB file
        self.assertIn("1.0 MB", result.stdout)  # 1 MB file

if __name__ == '__main__':
    unittest.main(verbosity=2)
