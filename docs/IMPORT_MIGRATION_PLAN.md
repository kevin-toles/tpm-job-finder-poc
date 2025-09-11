# Scraping Service Import Migration Plan

## Overview
This document outlines the plan to update all import statements from `scraping_service_v2` to `tpm_job_finder_poc.scraping_service` after the service was moved during repository reorganization.

## Current Status
- ✅ **Compatibility module created**: `scraping_service_v2.py` provides backward compatibility
- ✅ **System is functional**: All imports work through compatibility layer
- 🔄 **Next step**: Update imports to use new location directly

## Files Requiring Import Updates

### **High Priority - Core Application Files**

#### 1. **Job Aggregator Service** 
**File**: `tpm_job_finder_poc/job_aggregator/main.py`
**Lines**: 70, 183
```python
# Current (lines 70, 183):
from scraping_service_v2 import registry
from scraping_service_v2.core.base_job_source import FetchParams

# Update to:
from tpm_job_finder_poc.scraping_service import registry
from tpm_job_finder_poc.scraping_service.core.base_job_source import FetchParams
```

#### 2. **Moved Scraping Service Internal Files**
**Files**: 
- `tpm_job_finder_poc/scraping_service/validate_phase2.py`
- `tpm_job_finder_poc/scraping_service/demo_phase2.py`
- `tpm_job_finder_poc/scraping_service/core/service_registry.py`
- `tpm_job_finder_poc/scraping_service/scrapers/__init__.py`

**Issue**: These files still import from `scraping_service_v2` internally
**Priority**: HIGH - These should be self-referential now

### **Medium Priority - Test Files**

#### 3. **Unit Tests**
**Files**:
- `tests/unit/scraping_service_v2/test_core.py`
- `tests/unit/scraping_service_v2/test_scrapers.py`

**Options**:
- A) Update imports and rename directory to `tests/unit/scraping_service/`
- B) Keep compatibility imports for now

#### 4. **Integration Tests**
**Files**:
- `tests/integration/scraping_service_v2/test_integration.py`

#### 5. **Regression Tests**
**Files**:
- `tests/regression/scraping_service_v2/test_regression.py`

#### 6. **E2E Tests**
**Files**:
- `tests/e2e/test_complete_workflows.py` (lines 23, 305, 363, 561)

### **Medium Priority - Test Configuration**

#### 7. **Test Runner Configuration**
**File**: `scripts/run_tests.py` (moved from root)
**Lines**: 210, 213, 215, 285
```python
# Current:
"tests/unit/scraping_service_v2",
"tests/integration/scraping_service_v2", 
"tests/regression/scraping_service_v2",

# Update to:
"tests/unit/scraping_service",
"tests/integration/scraping_service",
"tests/regression/scraping_service",
```

#### 8. **Test Configuration**
**File**: `tests/conftest.py`
**Line**: 72
```python
# Current:
"scraping_service_v2/logs",

# Update to:
"tpm_job_finder_poc/scraping_service/logs",
```

### **Low Priority - Development Files**

#### 9. **Debug Tools**
**Files** (in `temp_dev_files/`):
- `debug_tools/scraper_service_v2_demo.py`
- `debug_tools/scraper_service_v2_browser_demo.py`

**Recommendation**: Update or mark as legacy

## Migration Strategy

### **Phase 1: Core Application (IMMEDIATE)**
1. Update `tpm_job_finder_poc/job_aggregator/main.py`
2. Fix internal imports in moved scraping service files
3. Test job aggregator functionality

### **Phase 2: Test Structure (PLANNED)**
1. Rename test directories from `scraping_service_v2` to `scraping_service`
2. Update all test imports
3. Update test configuration files
4. Run full test suite validation

### **Phase 3: Cleanup (FUTURE)**
1. Update debug tools or move to legacy
2. Remove compatibility module when all imports updated
3. Final validation

## Implementation Commands

### **Core Application Updates**
```bash
# Update job aggregator imports
sed -i 's/from scraping_service_v2/from tpm_job_finder_poc.scraping_service/g' tpm_job_finder_poc/job_aggregator/main.py

# Fix internal scraping service imports
find tpm_job_finder_poc/scraping_service -name "*.py" -exec sed -i 's/from scraping_service_v2/from tpm_job_finder_poc.scraping_service/g' {} \;
find tpm_job_finder_poc/scraping_service -name "*.py" -exec sed -i 's/import scraping_service_v2/import tpm_job_finder_poc.scraping_service as scraping_service_v2/g' {} \;
```

### **Test Structure Updates** 
```bash
# Rename test directories
mv tests/unit/scraping_service_v2 tests/unit/scraping_service
mv tests/integration/scraping_service_v2 tests/integration/scraping_service  
mv tests/regression/scraping_service_v2 tests/regression/scraping_service

# Update test imports
find tests/ -name "*.py" -exec sed -i 's/from scraping_service_v2/from tpm_job_finder_poc.scraping_service/g' {} \;
find tests/ -name "*.py" -exec sed -i 's/import scraping_service_v2/import tpm_job_finder_poc.scraping_service as scraping_service_v2/g' {} \;
```

## Validation Steps

### **After Each Phase**
1. **Import Test**: `python3 -c "from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService"`
2. **Instantiation Test**: `python3 -c "from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService; JobAggregatorService()"`
3. **Test Suite**: Run relevant test categories
4. **Full Integration**: Run complete workflow test

### **Success Criteria**
- ✅ All imports resolve without compatibility module
- ✅ Job aggregator service initializes properly
- ✅ All tests pass with new import structure
- ✅ No references to `scraping_service_v2` remain (except compatibility module)

## Rollback Plan
If issues arise:
1. **Keep compatibility module** until all issues resolved
2. **Revert specific files** that cause problems
3. **Gradual migration** rather than bulk updates

## Timeline
- **Phase 1**: Immediate (within current session)
- **Phase 2**: Next development session  
- **Phase 3**: When convenient / during cleanup sprint

---

**Status**: ✅ Compatibility module in place - system functional
**Next Action**: Execute Phase 1 core application updates
