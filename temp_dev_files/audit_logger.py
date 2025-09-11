#!/usr/bin/env python3
"""
Temporary Files Audit Logger

Utility to automatically log temporary development files to the audit tracking system.
Use this when creating files in temp_dev_files/ to maintain proper documentation.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

TEMP_DIR = Path(__file__).parent
AUDIT_FILE = TEMP_DIR / "TEMP_FILES_AUDIT.md"

def get_file_size(filepath):
    """Get human-readable file size."""
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except OSError:
        return "Unknown"

def log_temp_file(relative_path, purpose, status="Created", notes=""):
    """
    Log a temporary file to the audit system.
    
    Args:
        relative_path: Path relative to temp_dev_files/ (e.g., "debug_tools/analyze.py")  
        purpose: Description of what this file does
        status: Current status (Created, Active, Completed, Archived, etc.)
        notes: Additional notes or context
    """
    full_path = TEMP_DIR / relative_path
    date_str = datetime.now().strftime("%Y-%m-%d")
    size = get_file_size(full_path) if full_path.exists() else "Pending"
    
    # Read current audit file
    if AUDIT_FILE.exists():
        with open(AUDIT_FILE, 'r') as f:
            content = f.read()
    else:
        print(f"Error: Audit file {AUDIT_FILE} not found!")
        return
    
    # Find the table and add new entry
    lines = content.split('\n')
    table_end_idx = None
    
    for i, line in enumerate(lines):
        if line.startswith('| 2025-') or line.startswith('| Date Created'):
            continue
        elif line.startswith('|') and '---' in line:
            continue  
        elif line.startswith('##') and 'Cleanup Guidelines' in line:
            table_end_idx = i
            break
    
    if table_end_idx:
        # Insert new entry before cleanup section
        new_entry = f"| {date_str} | {relative_path} | {purpose} | {size} | {status} | {notes} |"
        lines.insert(table_end_idx - 1, new_entry)
        
        # Update the "Last updated" line
        for i, line in enumerate(lines):
            if line.startswith('*Last updated:'):
                lines[i] = f"*Last updated: {date_str}*"
                break
        
        # Write back to file
        with open(AUDIT_FILE, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Logged: {relative_path} - {purpose}")
    else:
        print("❌ Error: Could not find table structure in audit file")

def update_file_status(relative_path, new_status, notes=""):
    """Update the status of an existing logged file."""
    if not AUDIT_FILE.exists():
        print(f"Error: Audit file {AUDIT_FILE} not found!")
        return
        
    with open(AUDIT_FILE, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if f"| {relative_path} |" in line or f"{relative_path} " in line:
            parts = line.split('|')
            if len(parts) >= 6:
                parts[5] = f" {new_status} "
                if notes:
                    parts[6] = f" {notes} "
                lines[i] = '|'.join(parts)
                updated = True
                break
    
    if updated:
        # Update the "Last updated" line
        date_str = datetime.now().strftime("%Y-%m-%d")
        for i, line in enumerate(lines):
            if line.startswith('*Last updated:'):
                lines[i] = f"*Last updated: {date_str}*"
                break
        
        with open(AUDIT_FILE, 'w') as f:
            f.write('\n'.join(lines))
        print(f"✅ Updated: {relative_path} status -> {new_status}")
    else:
        print(f"❌ File not found in audit log: {relative_path}")

def list_temp_files():
    """List all currently tracked temporary files."""
    if not AUDIT_FILE.exists():
        print(f"Error: Audit file {AUDIT_FILE} not found!")
        return
        
    with open(AUDIT_FILE, 'r') as f:
        content = f.read()
    
    print("\n📋 Current Temporary Files:")
    print("=" * 60)
    
    in_table = False
    for line in content.split('\n'):
        if line.startswith('| Date Created'):
            in_table = True
            print(line)
        elif line.startswith('|') and '---' in line and in_table:
            print(line)
        elif line.startswith('| 2025-') and in_table:
            print(line)
        elif line.startswith('##') and in_table:
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python audit_logger.py log <relative_path> <purpose> [status] [notes]")
        print("  python audit_logger.py update <relative_path> <new_status> [notes]") 
        print("  python audit_logger.py list")
        print("\nExample:")
        print('  python audit_logger.py log "debug_tools/env_analyzer.py" "Environment debugging" "Active"')
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "log":
        if len(sys.argv) < 4:
            print("Error: log requires <relative_path> and <purpose>")
            sys.exit(1)
        relative_path = sys.argv[2]
        purpose = sys.argv[3]
        status = sys.argv[4] if len(sys.argv) > 4 else "Created"
        notes = sys.argv[5] if len(sys.argv) > 5 else ""
        log_temp_file(relative_path, purpose, status, notes)
        
    elif command == "update":
        if len(sys.argv) < 4:
            print("Error: update requires <relative_path> and <new_status>")
            sys.exit(1)
        relative_path = sys.argv[2]
        new_status = sys.argv[3]
        notes = sys.argv[4] if len(sys.argv) > 4 else ""
        update_file_status(relative_path, new_status, notes)
        
    elif command == "list":
        list_temp_files()
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
