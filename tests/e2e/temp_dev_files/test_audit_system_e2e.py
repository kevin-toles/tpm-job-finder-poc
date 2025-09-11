#!/usr/bin/env python3
"""
End-to-End Tests for Temporary Files Audit System

Tests the complete audit system from a user perspective including:
- Real-world usage workflows  
- Command-line interface testing
- File system persistence
- Long-term audit trail management
"""

import unittest
import tempfile
import os
import subprocess
import sys
import time
from pathlib import Path
import shutil
from datetime import datetime, timedelta

class TestAuditSystemE2E(unittest.TestCase):
    """End-to-end tests simulating real development workflows."""
    
    def setUp(self):
        """Set up full temp_dev_files system for E2E testing."""
        self.test_root = tempfile.mkdtemp()
        self.temp_dev_files = Path(self.test_root) / "temp_dev_files"
        
        # Create complete directory structure
        directories = [
            "migration_scripts",
            "debug_tools",
            "refactoring_helpers", 
            "logs_and_dumps"
        ]
        
        self.temp_dev_files.mkdir()
        for dir_name in directories:
            (self.temp_dev_files / dir_name).mkdir()
        
        # Copy audit system files
        original_temp_dev = Path(__file__).parent.parent.parent.parent / "temp_dev_files"
        
        # Copy audit_logger.py
        shutil.copy2(
            original_temp_dev / "audit_logger.py",
            self.temp_dev_files / "audit_logger.py"
        )
        
        # Copy README.md
        shutil.copy2(
            original_temp_dev / "README.md", 
            self.temp_dev_files / "README.md"
        )
        
        # Create initial audit file
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

### Safe Deletion Checklist
1. ✅ Verify file purpose is complete
2. ✅ Check if file is referenced in active work
3. ✅ Backup important insights/findings
4. ✅ Update this audit log with deletion date
5. ✅ Test that deletion doesn't break workflow

---
*Last updated: 2025-09-10*"""
        
        audit_file = self.temp_dev_files / "TEMP_FILES_AUDIT.md"
        with open(audit_file, 'w') as f:
            f.write(audit_content)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
    
    def run_command(self, args, expect_success=True):
        """Helper to run audit_logger commands."""
        cmd = [sys.executable, str(self.temp_dev_files / "audit_logger.py")] + args
        result = subprocess.run(
            cmd,
            cwd=self.temp_dev_files,
            capture_output=True,
            text=True
        )
        
        if expect_success:
            if result.returncode != 0:
                self.fail(f"Command failed: {' '.join(args)}\nStdout: {result.stdout}\nStderr: {result.stderr}")
        
        return result
    
    def test_real_world_development_workflow(self):
        """Test complete development workflow with temp files."""
        # Scenario: Developer is refactoring scrapers into service
        
        # Phase 1: Analysis and Planning
        analysis_script = self.temp_dev_files / "debug_tools" / "analyze_scrapers.py"
        analysis_script.write_text("""#!/usr/bin/env python3
# Scraper Analysis Tool
import os
import ast

def analyze_scraper_dependencies():
    print("Analyzing scraper dependencies...")
    return {"dependencies": ["requests", "datetime"], "complexity": "medium"}

if __name__ == "__main__":
    analyze_scraper_dependencies()
""")
        
        self.run_command([
            "log", "debug_tools/analyze_scrapers.py", 
            "Analyze scraper dependencies before refactoring", "Active"
        ])
        
        # Phase 2: Create migration scripts
        migration_script = self.temp_dev_files / "migration_scripts" / "extract_scraper_service.py"
        migration_script.write_text("""#!/usr/bin/env python3
# Migration Script: Extract Scraper Service
import shutil
from pathlib import Path

def migrate_scrapers():
    print("Migrating scrapers to service architecture...")
    # Migration logic here
    pass

if __name__ == "__main__":
    migrate_scrapers()
""")
        
        self.run_command([
            "log", "migration_scripts/extract_scraper_service.py",
            "Extract scrapers into independent service", "In Progress"
        ])
        
        # Phase 3: Create refactoring helpers
        refactor_helper = self.temp_dev_files / "refactoring_helpers" / "service_interface_generator.py"
        refactor_helper.write_text("""#!/usr/bin/env python3
# Service Interface Generator
def generate_service_interfaces():
    interfaces = ["ScraperService", "JobAggregator", "DataNormalizer"]
    for interface in interfaces:
        print(f"Generated {interface} interface")

if __name__ == "__main__":
    generate_service_interfaces()
""")
        
        self.run_command([
            "log", "refactoring_helpers/service_interface_generator.py",
            "Generate service interfaces for scraper refactoring", "Created"
        ])
        
        # Phase 4: Generate logs and dumps
        debug_log = self.temp_dev_files / "logs_and_dumps" / "scraper_analysis_output.log"
        debug_log.write_text("""2025-09-10 10:00:00 - Starting scraper analysis
2025-09-10 10:01:00 - Found 3 scrapers: Greenhouse, Lever, RemoteOK
2025-09-10 10:02:00 - Dependencies analysis complete
2025-09-10 10:03:00 - Service extraction plan generated
""")
        
        self.run_command([
            "log", "logs_and_dumps/scraper_analysis_output.log",
            "Debug output from scraper analysis", "Temporary"
        ])
        
        # Phase 5: Update statuses as work progresses
        self.run_command([
            "update", "debug_tools/analyze_scrapers.py", "Completed", 
            "Analysis complete, dependencies mapped"
        ])
        
        self.run_command([
            "update", "refactoring_helpers/service_interface_generator.py", "Active",
            "Generating interfaces"
        ])
        
        # Phase 6: Verify complete audit trail
        result = self.run_command(["list"])
        
        # Check that all files are tracked
        expected_files = [
            "debug_tools/analyze_scrapers.py",
            "migration_scripts/extract_scraper_service.py", 
            "refactoring_helpers/service_interface_generator.py",
            "logs_and_dumps/scraper_analysis_output.log"
        ]
        
        for expected_file in expected_files:
            self.assertIn(expected_file, result.stdout)
        
        # Check status updates
        self.assertIn("Completed", result.stdout)  # analyze_scrapers.py
        self.assertIn("In Progress", result.stdout)  # extract_scraper_service.py
        self.assertIn("Active", result.stdout)  # service_interface_generator.py
        self.assertIn("Temporary", result.stdout)  # scraper_analysis_output.log
        
        # Phase 7: Verify audit file integrity
        audit_file = self.temp_dev_files / "TEMP_FILES_AUDIT.md"
        with open(audit_file, 'r') as f:
            content = f.read()
        
        # Should contain all logged files
        for expected_file in expected_files:
            self.assertIn(expected_file, content)
        
        # Should have updated timestamp
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.assertIn(f"*Last updated: {current_date}*", content)
        
        # File sizes should be calculated and reasonable
        self.assertTrue(any(size in content for size in ["B", "KB"]))
    
    def test_cleanup_workflow_simulation(self):
        """Test simulated cleanup workflow after project completion."""
        # Create various temp files at different stages
        files_to_create = [
            ("debug_tools/old_analyzer.py", "Old analysis tool", "Completed", "30 days old"),
            ("migration_scripts/completed_migration.py", "Completed migration", "Archived", "Validated 45 days"),
            ("refactoring_helpers/active_refactor.py", "Active refactoring", "In Progress", "Current work"),
            ("logs_and_dumps/old_debug.log", "Old debug log", "Ready for deletion", "No longer needed"),
            ("logs_and_dumps/recent_debug.log", "Recent debug log", "Temporary", "Keep for analysis")
        ]
        
        for file_path, purpose, status, notes in files_to_create:
            full_path = self.temp_dev_files / file_path
            full_path.write_text(f"# {purpose}\n# {notes}")
            
            self.run_command(["log", file_path, purpose, status, notes])
        
        # Simulate cleanup decisions based on status
        cleanup_candidates = [
            ("debug_tools/old_analyzer.py", "Ready for deletion", "Analysis complete, insights documented"),
            ("logs_and_dumps/old_debug.log", "Deleted", "Removed during cleanup"),
        ]
        
        for file_path, new_status, notes in cleanup_candidates:
            self.run_command(["update", file_path, new_status, notes])
        
        # Verify cleanup tracking
        result = self.run_command(["list"])
        
        self.assertIn("Ready for deletion", result.stdout)
        self.assertIn("Deleted", result.stdout)
        self.assertIn("In Progress", result.stdout)  # Active work should remain
        
        # Verify audit file shows cleanup history
        audit_file = self.temp_dev_files / "TEMP_FILES_AUDIT.md"
        with open(audit_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Ready for deletion", content)
        self.assertIn("Deleted", content)
        self.assertIn("insights documented", content)
    
    def test_command_line_interface_edge_cases(self):
        """Test CLI edge cases and error handling."""
        # Test with no arguments
        result = subprocess.run(
            [sys.executable, str(self.temp_dev_files / "audit_logger.py")],
            cwd=self.temp_dev_files,
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)
        
        # Test invalid command
        result = self.run_command(["invalid_command"], expect_success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown command", result.stdout)
        
        # Test missing arguments
        result = self.run_command(["log"], expect_success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stdout)
        
        # Test missing arguments for update
        result = self.run_command(["update", "test.py"], expect_success=False)
        self.assertNotEqual(result.returncode, 0)
        
        # Test successful operations with minimal args
        self.run_command(["log", "debug_tools/test.py", "Test file"])
        self.run_command(["update", "debug_tools/test.py", "Completed"])
        self.run_command(["list"])
    
    def test_file_system_persistence(self):
        """Test that audit system persists state correctly."""
        # Create and log a file
        test_file = self.temp_dev_files / "debug_tools" / "persistence_test.py"
        test_file.write_text("# Persistence test")
        
        self.run_command([
            "log", "debug_tools/persistence_test.py", "Test persistence", "Active"
        ])
        
        # Verify file was logged
        audit_file = self.temp_dev_files / "TEMP_FILES_AUDIT.md"
        with open(audit_file, 'r') as f:
            original_content = f.read()
        
        self.assertIn("persistence_test.py", original_content)
        
        # Simulate system restart by creating new command instance
        self.run_command([
            "update", "debug_tools/persistence_test.py", "Completed", "Test passed"
        ])
        
        # Verify persistence across operations
        with open(audit_file, 'r') as f:
            updated_content = f.read()
        
        self.assertIn("persistence_test.py", updated_content)
        self.assertIn("Completed", updated_content)
        self.assertIn("Test passed", updated_content)
        
        # Original entry should be updated, not duplicated
        persistence_lines = [line for line in updated_content.split('\n') 
                           if 'persistence_test.py' in line]
        self.assertEqual(len(persistence_lines), 1)

if __name__ == '__main__':
    # Run with higher verbosity for E2E tests
    unittest.main(verbosity=2)
