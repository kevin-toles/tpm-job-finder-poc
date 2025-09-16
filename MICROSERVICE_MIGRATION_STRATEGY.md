# Microservice Migration Strategy

## Overview
Staged migration approach that maintains application functionality while transitioning components to microservices.

## Migration Phases

### Phase 1: Service Creation (Current)
```
tpm_job_finder_poc/
├── audit_logger/              # 🟡 OLD (still functioning)
├── audit_service/             # 🟢 NEW (service implementation)
├── shared/contracts/          # 🟢 NEW (service contracts)
└── _adapters/                 # 🔄 BRIDGE (adapter layer)
    └── audit_logger_adapter.py
```

### Phase 2: Adapter Bridge
```python
# _adapters/audit_logger_adapter.py
"""
Adapter that bridges old audit_logger API to new audit_service.
Allows gradual migration while maintaining backward compatibility.
"""

from tpm_job_finder_poc.audit_service import AuditService
from tpm_job_finder_poc.shared.contracts.audit_service import AuditEvent, AuditLevel

class AuditLogger:
    """Adapter class that mimics old AuditLogger API but uses new audit_service."""
    
    def __init__(self):
        self._service = AuditService.get_instance()
    
    @staticmethod
    def log(message: str, level: str = "INFO"):
        """Old API method - bridges to new service."""
        event = AuditEvent(
            action="legacy_log",
            message=message,
            level=AuditLevel(level.lower()),
            service_name="legacy_adapter"
        )
        asyncio.create_task(AuditService.get_instance().log_event(event))

# Update old import path to use adapter
# tpm_job_finder_poc/audit_logger/__init__.py
from tpm_job_finder_poc._adapters.audit_logger_adapter import AuditLogger
```

### Phase 3: Consumer Migration
```python
# Consumers gradually migrate from:
from tpm_job_finder_poc.audit_logger.logger import AuditLogger
AuditLogger.log("message")

# To new service contracts:
from tpm_job_finder_poc.shared.contracts.audit_service import IAuditService
await audit_service.log_event(event)
```

### Phase 4: Adapter Removal
```
tpm_job_finder_poc/
├── audit_service/             # 🟢 ONLY (fully migrated)
├── shared/contracts/          # 🟢 ACTIVE
└── DEPRECATED/
    ├── audit_logger/          # 🔴 MOVED (obsolete)
    └── _adapters/             # 🔴 MOVED (no longer needed)
```

## Migration Benefits

### ✅ **Maintains Functionality**
- Application works throughout migration
- No breaking changes for existing features
- Gradual transition reduces risk

### ✅ **Clear Migration Path**
1. **Create** new service implementation
2. **Bridge** old API via adapter
3. **Migrate** consumers one by one
4. **Remove** adapter when complete
5. **Deprecate** old files

### ✅ **Testing Strategy**
- Test new service independently
- Test adapter compatibility
- Test consumer migrations incrementally
- Validate end-to-end functionality

## Implementation Example

### Current State (audit_logger component)
```python
# tpm_job_finder_poc/audit_logger/logger.py
class AuditLogger:
    @staticmethod
    def log(message: str):
        # Old implementation
        pass

# Usage throughout codebase
from tpm_job_finder_poc.audit_logger.logger import AuditLogger
AuditLogger.log("Something happened")
```

### Migration State (with adapter)
```python
# tpm_job_finder_poc/audit_service/ (NEW)
class AuditService:
    async def log_event(self, event: AuditEvent):
        # New service implementation
        pass

# tpm_job_finder_poc/_adapters/audit_logger_adapter.py (BRIDGE)
class AuditLogger:
    @staticmethod
    def log(message: str):
        # Adapter bridges to new service
        service = get_audit_service()
        event = AuditEvent(action="legacy_log", message=message, service_name="adapter")
        asyncio.create_task(service.log_event(event))

# tpm_job_finder_poc/audit_logger/__init__.py (UPDATED)
from tpm_job_finder_poc._adapters.audit_logger_adapter import AuditLogger

# Existing usage still works!
from tpm_job_finder_poc.audit_logger.logger import AuditLogger
AuditLogger.log("Something happened")  # -> Routes to new service
```

### Final State (post-migration)
```python
# tpm_job_finder_poc/audit_service/ (ONLY)
# Direct service usage
from tpm_job_finder_poc.shared.contracts.audit_service import IAuditService
await audit_service.log_event(event)

# DEPRECATED/ (MOVED)
# All old files moved to deprecated
```

## Migration Timeline

### Component-by-Component Approach
1. **audit_logger** → **audit_service** (Current focus)
2. **job_aggregator** → **job_collection_service** 
3. **enrichment** → **ai_intelligence_service**
4. **scraping_service** → **web_scraping_service**
5. **Continue systematically...**

### Per-Component Steps
1. **Week 1**: Create new service + tests (RED/GREEN/REFACTOR)
2. **Week 2**: Create adapter bridge + validate compatibility  
3. **Week 3**: Migrate high-priority consumers to new contracts
4. **Week 4**: Complete consumer migration + remove adapter + deprecate old files

## Complexity Assessment

### ✅ **Manageable Complexity**
- **Clear boundaries** between old/new/adapter code
- **Single responsibility** per adapter (1:1 component mapping)
- **Time-bounded** complexity (adapters are temporary)
- **Testable** at each stage

### ⚠️ **Complexity to Manage**
- **Dual import paths** during transition
- **Async/sync bridging** in adapters
- **Version consistency** across old/new APIs
- **Team coordination** on migration priorities

## Recommendation: YES, Maintain Functionality

**Benefits outweigh complexity** for this migration approach:

1. **Low Risk** - Application never breaks
2. **Incremental Progress** - Can deploy and validate continuously  
3. **Business Value** - Features continue shipping during migration
4. **Team Flexibility** - Different components can migrate at different speeds
5. **Rollback Safety** - Can revert individual services if needed

The adapter pattern provides clean separation and makes the complexity manageable and time-bounded.