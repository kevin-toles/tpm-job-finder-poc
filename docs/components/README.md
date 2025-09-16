# Component Documentation Navigation

This directory serves as a navigation hub for all system components. **Component documentation is now co-located with code** for better maintainability and developer experience.

## 📍 **Component Documentation Locations**

All comprehensive component documentation is now located within each component's directory:

### 🎯 **Core Intelligence Components**
- **[Enrichment](../../tpm_job_finder_poc/enrichment/README.md)** - Multi-resume intelligence system with AI-powered matching
- **[LLM Provider](../../tpm_job_finder_poc/llm_provider/README.md)** - Multi-provider LLM integration with fallback support
- **[Job Normalizer](../../tpm_job_finder_poc/job_normalizer/README.md)** - Job data standardization and validation

### 🔄 **Data Collection & Processing**
- **[Job Aggregator](../../tpm_job_finder_poc/job_aggregator/README.md)** - Multi-source job collection orchestration
- **[Scraping Service](../../tpm_job_finder_poc/scraping_service/README.md)** - Browser automation with anti-detection

### 🏗️ **System Infrastructure**
- **[Models](../../tpm_job_finder_poc/models/README.md)** - Core data structures and schemas
- **[Storage](../../tpm_job_finder_poc/storage/README.md)** - Secure storage abstraction layer
- **[Cache](../../tpm_job_finder_poc/cache/README.md)** - Multi-level caching with deduplication
- **[Config](../../tpm_job_finder_poc/config/README.md)** - Centralized configuration management

### 👤 **User Interface & Services**
- **[CLI](../../tpm_job_finder_poc/cli/README.md)** - Comprehensive command-line interface
- **[Resume Uploader](../../tpm_job_finder_poc/resume_uploader/README.md)** - File upload and processing
- **[Secure Storage](../../tpm_job_finder_poc/secure_storage/README.md)** - Security and audit logging

### 🔧 **Supporting Services**
- **[Webhook](../../tpm_job_finder_poc/webhook/README.md)** - HTTP webhooks and integrations
- **[Audit Logger](../../tpm_job_finder_poc/audit_logger/README.md)** - Logging and audit trails
- **[Error Handler](../../tpm_job_finder_poc/error_handler/README.md)** - Error management and recovery
- **[Health Monitor](../../tpm_job_finder_poc/health_monitor/README.md)** - System monitoring and health checks

---

## 🔗 **Component Integration Patterns**

### **Data Flow Architecture**
```
CLI Entry → Resume Processing → Multi-Source Collection → LLM Scoring → Geographic Export
     ↓              ↓                    ↓                   ↓              ↓
File Upload → Text Extraction → Job Aggregation → AI Analysis → Excel Workbooks
```

### **Service Dependencies**
```
                    LLM Provider ←→ Enrichment
                         ↑              ↓
Job Aggregator → Job Normalizer → Cache → Storage
      ↑                                      ↓
Scraping Service                    Secure Storage
      ↑                                      ↓
Health Monitor ←→ Error Handler ←→ Audit Logger
```

### **Component Interaction Patterns**

#### **1. Data Collection Flow**
- **Job Aggregator** orchestrates collection from API and browser sources
- **Scraping Service** provides browser-based data extraction
- **Job Normalizer** standardizes data into consistent schemas
- **Cache** eliminates duplicates and tracks application state

#### **2. Intelligence Processing Flow**
- **Enrichment** coordinates AI-powered job analysis
- **LLM Provider** routes requests across multiple AI providers
- **Models** define data structures for all components
- **Storage** persists results with audit trails

#### **3. User Interface Flow**
- **CLI** provides unified command-line interface
- **Config** manages system-wide configuration
- **Resume Uploader** handles file processing
- **Error Handler** ensures graceful failure recovery

---

## 📚 **Related System Documentation**

### **Architecture & Design**
- **[Business Process Architecture](../architecture/BUSINESS_PROCESS_ARCHITECTURE.md)** - Complete business workflows
- **[System Architecture Workflows](../architecture/SYSTEM_ARCHITECTURE_WORKFLOWS.md)** - Technical architecture patterns

### **Implementation Guides**
- **[Component Integration Map](./COMPONENT_INTEGRATION_MAP.md)** - How components work together
- **[Development Patterns](../implementation/)** - Implementation best practices

### **Testing & Quality**
- **[Testing Strategy](../testing/)** - Component testing approaches
- **[TDD Component Audit](../testing/TDD_COMPONENT_AUDIT_CATALOG.md)** - Systematic testing inventory

---

## 🚀 **Quick Start Guide**

### **For New Developers**
1. Start with **[Project Overview](../../README.md)** for system understanding
2. Review **[Component Integration Map](./COMPONENT_INTEGRATION_MAP.md)** for architecture overview
3. Dive into specific component READMEs based on your focus area
4. Check **[Development Patterns](../implementation/)** for coding standards

### **For Component Development**
1. Use component READMEs as authoritative documentation source
2. Follow patterns established in existing component documentation
3. Update component README when making architectural changes
4. Maintain co-location of documentation with code

### **For System Integration**
1. Review **[Business Process Architecture](../architecture/BUSINESS_PROCESS_ARCHITECTURE.md)** for workflow understanding
2. Check component dependencies in individual READMEs
3. Use **[Health Monitor](../../tpm_job_finder_poc/health_monitor/README.md)** for system observability
4. Follow **[Error Handler](../../tpm_job_finder_poc/error_handler/README.md)** patterns for robust integration

---

## 📝 **Documentation Standards**

### **Component README Structure**
Each component README follows a standardized template:
- **Overview** - Purpose and business value
- **Architecture** - Component structure and design
- **Public API** - Interfaces and key classes
- **Usage Examples** - 5-6 practical examples
- **Testing** - Testing approaches and examples
- **Security** - Security considerations
- **Dependencies** - Component relationships
- **Future Enhancements** - Planned improvements

### **Maintenance Guidelines**
- Component documentation lives with code for easier maintenance
- Business process documentation lives in `docs/` for stakeholder access
- Integration patterns documented in this navigation hub
- Cross-component workflows documented in architecture guides

---

**Note**: This navigation approach eliminates documentation duplication while providing developers with documentation exactly where they expect it - alongside the code they're working with.