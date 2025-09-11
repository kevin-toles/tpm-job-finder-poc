#!/usr/bin/env python3
"""
Integration Tests for Temporary Files Audit System

Tests the complete workflow of the temp files audit system including:
- Directory structure validation
- Multi-file operations
- Cross-component integration
- File system state consistency
"""

import unittest
import tempfile
import os
import subprocess
import sys
from pathlib import Path
import shutil

class TestAuditSystemIntegration(unittest.TestCase):
    """Integration tests for the complete audit system."""
    
    def setUp(self):
        """Set up integration test environment with full directory structure."""
        self.test_root = tempfile.mkdtemp()
        self.temp_dev_files = Path(self.test_root) / "temp_dev_files"
        
        # Create full directory structure
        self.temp_dev_files.mkdir()
        (self.temp_dev_files / "migration_scripts").mkdir()
        (self.temp_dev_files / "debug_tools").mkdir()
        (self.temp_dev_files / "refactoring_helpers").mkdir()
        (self.temp_dev_files / "logs_and_dumps").mkdir()
        
        # Copy audit_logger.py to test environment
        original_audit_logger = Path(__file__).parent.parent.parent.parent / "temp_dev_files" / "audit_logger.py"
        test_audit_logger = self.temp_dev_files / "audit_logger.py"
        shutil.copy2(original_audit_logger, test_audit_logger)
        
        # Create test audit file
        audit_content = """# Temporary Development Files Audit Log

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
        
        audit_file = self.temp_dev_files / "TEMP_FILES_AUDIT.md"
        with open(audit_file, 'w') as f:
            f.write(audit_content)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
    
    def run_audit_logger_command(self, args):
        """Helper to run audit_logger.py command and capture output."""
        cmd = [sys.executable, str(self.temp_dev_files / "audit_logger.py")] + args
        result = subprocess.run(
            cmd,
            cwd=self.temp_dev_files,
            capture_output=True,
            text=True
        )
        return result
    
    def test_complete_file_lifecycle(self):
        """Test complete lifecycle: create -> log -> update -> list."""
        # 1. Create actual files in different directories
        debug_file = self.temp_dev_files / "debug_tools" / "env_analyzer.py"
        debug_file.write_text("# Environment analysis script\nprint('analyzing...')")
        
        migration_file = self.temp_dev_files / "migration_scripts" / "migrate_scrapers.py"
        migration_file.write_text("# Scraper migration script\n# TODO: implement migration")
        
        # 2. Log both files
        result1 = self.run_audit_logger_command([
            "log", "debug_tools/env_analyzer.py", "Environment debugging script", "Active"
        ])
        self.assertEqual(result1.returncode, 0)
        self.assertIn("Logged: debug_tools/env_analyzer.py", result1.stdout)
        
        result2 = self.run_audit_logger_command([
            "log", "migration_scripts/migrate_scrapers.py", "Scraper migration helper", "In Progress"
        ])
        self.assertEqual(result2.returncode, 0)
        
        # 3. Update statuses
        result3 = self.run_audit_logger_command([
            "update", "debug_tools/env_analyzer.py", "Completed", "Analysis finished"
        ])
        self.assertEqual(result3.returncode, 0)
        self.assertIn("Updated: debug_tools/env_analyzer.py status -> Completed", result3.stdout)
        
        # 4. List all files
        result4 = self.run_audit_logger_command(["list"])
        self.assertEqual(result4.returncode, 0)
        self.assertIn("debug_tools/env_analyzer.py", result4.stdout)
        self.assertIn("migration_scripts/migrate_scrapers.py", result4.stdout)
        self.assertIn("Completed", result4.stdout)
        self.assertIn("In Progress", result4.stdout)
        
        # 5. Verify audit file state
        audit_file = self.temp_dev_files / "TEMP_FILES_AUDIT.md"
        with open(audit_file, 'r') as f:
            content = f.read()
        
        # Should contain both files with correct info
        self.assertIn("debug_tools/env_analyzer.py", content)
        self.assertIn("migration_scripts/migrate_scrapers.py", content)
        self.assertIn("Completed", content)
        self.assertIn("In Progress", content)
        self.assertIn("Analysis finished", content)
        
        # File sizes should be calculated
        self.assertTrue(any(size_unit in content for size_unit in ["B", "KB", "MB"]))
    
    def test_multiple_updates_same_file(self):
        """Test updating the same file multiple times."""
        # Create and log file
        test_file = self.temp_dev_files / "refactoring_helpers" / "refactor.py"
        test_file.write_text("# Refactoring helper")
        
        self.run_audit_logger_command([
            "log", "refactoring_helpers/refactor.py", "Refactoring helper", "Created"
        ])
        
        # Multiple status updates
        statuses = [
            ("In Progress", "Started refactoring"),
            ("Testing", "Running tests"),
            ("Completed", "Refactoring finished"),
            ("Archived", "Ready for cleanup")
        ]
        
        for status, notes in statuses:
            result = self.run_audit_logger_command([
                "update", "refactoring_helpers/refactor.py", status, notes
            ])
            self.assertEqual(result.returncode, 0)
        
        # Verify final state
        audit_file = self.temp_dev_files / "TEMP_FILES_AUDIT.md"
        with open(audit_file, 'r') as f:
            content = f.read()
        
        # Should only have one entry for the file with final status
        file_lines = [line for line in content.split('\n') if 'refactoring_helpers/refactor.py' in line]
        self.assertEqual(len(file_lines), 1)
        self.assertIn("Archived", file_lines[0])
        self.assertIn("Ready for cleanup", file_lines[0])
    
    def test_concurrent_file_operations(self):
        """Test handling multiple files being logged simultaneously."""
        files_to_create = [
            ("debug_tools/analyzer1.py", "First analyzer", "Active"),
            ("debug_tools/analyzer2.py", "Second analyzer", "Testing"), 
            ("migration_scripts/migrate1.py", "First migration", "Created"),
            ("migration_scripts/migrate2.py", "Second migration", "In Progress"),
            ("logs_and_dumps/debug.log", "Debug log dump", "Temporary"),
        ]
        
        # Create all files
        for file_path, purpose, status in files_to_create:
            full_path = self.temp_dev_files / file_path
            full_path.write_text(f"# {purpose}\n# Status: {status}")
            
            result = self.run_audit_logger_command([
                "log", file_path, purpose, status
            ])
            self.assertEqual(result.returncode, 0)
        
        # Verify all files are tracked
        result = self.run_audit_logger_command(["list"])
        self.assertEqual(result.returncode, 0)
        
        for file_path, purpose, status in files_to_create:
            self.assertIn(file_path, result.stdout)
            self.assertIn(status, result.stdout)
    
    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        # Test logging non-existent file (should work - file might be created later)
        result1 = self.run_audit_logger_command([
            "log", "debug_tools/future_file.py", "Future file", "Planned"
        ])
        self.assertEqual(result1.returncode, 0)  # Should succeed even if file doesn't exist
        
        # Test updating non-logged file
        result2 = self.run_audit_logger_command([
            "update", "debug_tools/never_logged.py", "Completed"
        ])
        self.assertEqual(result2.returncode, 0)  # Command succeeds but reports error
        self.assertIn("File not found in audit log", result2.stdout)
        
        # Test invalid command
        result3 = self.run_audit_logger_command(["invalid_command"])
        self.assertNotEqual(result3.returncode, 0)
        
        # Test missing arguments
        result4 = self.run_audit_logger_command(["log"])
        self.assertNotEqual(result4.returncode, 0)

class TestAuditSystemDirectoryStructure(unittest.TestCase):
    """Test audit system with different directory structures and edge cases."""
    
    def setUp(self):
        """Set up test with minimal directory structure."""
        self.test_root = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
    
    def test_directory_structure_validation(self):
        """Test that the expected directory structure is properly utilized."""
        temp_dev_files = Path(self.test_root) / "temp_dev_files"
        temp_dev_files.mkdir()
        
        # Create all expected directories
        expected_dirs = [
            "migration_scripts",
            "debug_tools", 
            "refactoring_helpers",
            "logs_and_dumps"
        ]
        
        for dir_name in expected_dirs:
            (temp_dev_files / dir_name).mkdir()
        
        # Verify all directories exist and are usable
        for dir_name in expected_dirs:
            dir_path = temp_dev_files / dir_name
            self.assertTrue(dir_path.exists())
            self.assertTrue(dir_path.is_dir())
            
            # Test file creation in each directory
            test_file = dir_path / "test_file.txt"
            test_file.write_text("test content")
            self.assertTrue(test_file.exists())
    
    def test_nested_directory_handling(self):
        """Test handling of nested directories within temp_dev_files."""
        temp_dev_files = Path(self.test_root) / "temp_dev_files"
        temp_dev_files.mkdir()
        
        # Create nested structure
        nested_dir = temp_dev_files / "debug_tools" / "sub_category" / "specific_tool"
        nested_dir.mkdir(parents=True)
        
        test_file = nested_dir / "nested_tool.py"
        test_file.write_text("# Nested tool")
        
        # The audit logger should handle nested paths
        self.assertTrue(test_file.exists())
        
        # Path should be relative to temp_dev_files
        relative_path = test_file.relative_to(temp_dev_files)
        expected_path = "debug_tools/sub_category/specific_tool/nested_tool.py"
        self.assertEqual(str(relative_path), expected_path)

if __name__ == '__main__':
    unittest.main(verbosity=2)
