# Temporary Development Files System

This directory houses temporary files created during development, refactoring, and restructuring work. It includes an automated audit logging system to track files and facilitate periodic cleanup.

## 📁 Directory Structure

```
temp_dev_files/
├── TEMP_FILES_AUDIT.md      # Automated audit log (DO NOT EDIT MANUALLY)
├── audit_logger.py          # Utility script for logging files
├── README.md               # This file
├── migration_scripts/      # Code migration and restructuring scripts
├── debug_tools/           # Debug scripts, analyzers, diagnostic tools
├── refactoring_helpers/   # Helper scripts for code refactoring
└── logs_and_dumps/        # Temporary logs, cache dumps, data exports
```

## 🔧 Usage

### Creating & Logging Files

When creating any temporary file in this directory:

1. **Create your file** in the appropriate subdirectory
2. **Log it immediately** using the audit logger:

```bash
# Log a new file
python temp_dev_files/audit_logger.py log "debug_tools/env_analyzer.py" "Environment debugging script" "Active"

# Update file status
python temp_dev_files/audit_logger.py update "debug_tools/env_analyzer.py" "Completed" "Issue resolved"

# List all tracked files  
python temp_dev_files/audit_logger.py list
```

### Example Workflow

```bash
# 1. Create a migration script
touch temp_dev_files/migration_scripts/migrate_scrapers.py

# 2. Log it immediately
python temp_dev_files/audit_logger.py log "migration_scripts/migrate_scrapers.py" "Migrate scrapers to service architecture" "Active"

# 3. Later, when complete
python temp_dev_files/audit_logger.py update "migration_scripts/migrate_scrapers.py" "Completed" "Migration successful"

# 4. Eventually mark for cleanup  
python temp_dev_files/audit_logger.py update "migration_scripts/migrate_scrapers.py" "Ready for deletion" "Validated for 30+ days"
```

## 🧹 Periodic Cleanup

### Monthly Review Process

1. **List all files**: `python temp_dev_files/audit_logger.py list`
2. **Review the audit log**: Check `TEMP_FILES_AUDIT.md` 
3. **Follow retention policy**:
   - Migration Scripts: Keep 30+ days after completion
   - Debug Tools: Delete after issue resolution
   - Refactoring Helpers: Keep until refactor is validated
   - Logs & Dumps: Clean weekly, keep significant ones

### Safe Deletion Checklist
- [ ] File purpose is complete
- [ ] No active references in current work
- [ ] Important insights backed up elsewhere  
- [ ] Audit log updated with deletion status
- [ ] Workflow tested after removal

## 🎯 Benefits

- **Organized**: Structured directories by purpose
- **Tracked**: Automatic audit trail of all temporary files
- **Documented**: Clear purpose and status for each file
- **Maintainable**: Easy periodic cleanup with safety guidelines
- **Transparent**: Team visibility into temporary development assets

## ⚠️ Important Notes

- **Always log files** immediately after creation
- **Never edit** `TEMP_FILES_AUDIT.md` manually - use `audit_logger.py`
- **Include purpose** - future you will thank present you
- **Update status** as work progresses
- **Follow retention policy** to avoid accumulation
