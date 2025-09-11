#!/usr/bin/env python3
"""
Simple functional test for the audit logger to verify it works in our environment.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

def test_audit_logger_basic_functionality():
    """Test basic audit logger functionality."""
    print("Testing audit logger basic functionality...")
    
    # Get the path to our audit logger
    project_root = Path(__file__).parent.parent.parent.parent
    audit_logger_path = project_root / "temp_dev_files" / "audit_logger.py"
    python_path = project_root / ".venv" / "bin" / "python"
    
    if not audit_logger_path.exists():
        print(f"❌ Audit logger not found at {audit_logger_path}")
        return False
    
    if not python_path.exists():
        print(f"❌ Python venv not found at {python_path}")
        return False
    
    try:
        # Change to temp_dev_files directory for testing
        os.chdir(project_root / "temp_dev_files")
        
        # Test 1: List command (should work even with empty list)
        result = subprocess.run([str(python_path), "audit_logger.py", "list"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ List command failed: {result.stderr}")
            return False
        print("✅ List command works")
        
        # Test 2: Log a file
        result = subprocess.run([str(python_path), "audit_logger.py", "log", 
                               "test_file.py", "Test logging functionality", "Active"],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Log command failed: {result.stderr}")
            return False
        if "Logged:" not in result.stdout:
            print(f"❌ Log command didn't provide expected output: {result.stdout}")
            return False
        print("✅ Log command works")
        
        # Test 3: Update the file
        result = subprocess.run([str(python_path), "audit_logger.py", "update",
                               "test_file.py", "Completed", "Test successful"],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Update command failed: {result.stderr}")
            return False
        if "Updated:" not in result.stdout:
            print(f"❌ Update command didn't provide expected output: {result.stdout}")
            return False
        print("✅ Update command works")
        
        # Test 4: Verify the file appears in list
        result = subprocess.run([str(python_path), "audit_logger.py", "list"],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Final list command failed: {result.stderr}")
            return False
        if "test_file.py" not in result.stdout or "Completed" not in result.stdout:
            print(f"❌ File not properly tracked: {result.stdout}")
            return False
        print("✅ File tracking works end-to-end")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_audit_logger_basic_functionality()
    if success:
        print("\n🎉 All audit logger tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Audit logger tests failed!")
        sys.exit(1)
