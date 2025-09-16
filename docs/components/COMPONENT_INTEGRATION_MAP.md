# Component Integration Map

**Purpose**: Visual and textual mapping of how all TPM Job Finder components work together to deliver the complete global job intelligence platform.

**Audience**: Developers, System Architects, Product Managers  
**Scope**: Cross-component data flows, integration patterns, and system architecture

---

## 🗺️ **SYSTEM OVERVIEW MAP**

### **High-Level Component Ecosystem**
```
                    🌐 External World
                         ↓
    ┌─────────────────────────────────────────────┐
    │              User Interface                 │
    │  ┌─────────────┐  ┌─────────────────────┐   │
    │  │     CLI     │  │   Resume Uploader   │   │
    │  └─────────────┘  └─────────────────────┘   │
    └─────────────┬───────────────┬───────────────┘
                  │               │
                  ▼               ▼
    ┌─────────────────────────────────────────────┐
    │             Core Intelligence               │
    │  ┌────────────┐  ┌───────────────────────┐  │
    │  │ Enrichment │  │    LLM Provider       │  │
    │  └────────────┘  └───────────────────────┘  │
    └─────────────┬───────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────┐
    │           Data Collection                   │
    │  ┌───────────────┐  ┌──────────────────────┐│
    │  │Job Aggregator │  │  Scraping Service    ││
    │  └───────────────┘  └──────────────────────┘│
    └─────────────┬───────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────┐
    │        Data Processing                      │
    │  ┌──────────────┐  ┌─────────────────────┐  │
    │  │Job Normalizer│  │       Cache         │  │
    │  └──────────────┘  └─────────────────────┘  │
    └─────────────┬───────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────┐
    │          Infrastructure                     │
    │ ┌───────┐ ┌────────┐ ┌────────┐ ┌─────────┐ │
    │ │Models │ │Storage │ │ Config │ │SecureStr│ │
    │ └───────┘ └────────┘ └────────┘ └─────────┘ │
    └─────────────┬───────────────────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────┐
    │         Observability                       │
    │ ┌──────────┐ ┌───────────┐ ┌──────────────┐ │
    │ │HealthMon │ │ErrorHandle│ │ AuditLogger  │ │
    │ └──────────┘ └───────────┘ └──────────────┘ │
    └─────────────────────────────────────────────┘
```

---

## 🔄 **DATA FLOW PATTERNS**

### **1. Complete Job Search Workflow**
```
User Input → CLI → Config → Resume Upload → Enrichment
    ↓
Job Collection → Job Aggregator → Scraping Service
    ↓
Data Processing → Job Normalizer → Cache → Models
    ↓
AI Analysis → LLM Provider → Enrichment → Results
    ↓
Data Persistence → Storage → Secure Storage → Output
```

### **2. Multi-Resume Intelligence Flow**
```
Resume Portfolio Discovery
    ↓
┌─────────────────────────────────────────┐
│          Enrichment Component           │
│                                         │
│  Resume Discovery → Portfolio Scanning  │
│         ↓                               │
│  Master Identification → Classification │
│         ↓                               │
│  Hybrid Selection → LLM Scoring         │
│         ↓                               │
│  Enhancement Generation → Validation    │
└─────────────────────────────────────────┘
    ↓
Enhanced Job Matching Results
```

### **3. Enterprise Multi-User Flow**
```
Team Configuration → Config Manager → User Permissions
    ↓
Collaborative Search → Job Aggregator → Shared Opportunities
    ↓
Team Analytics → Enrichment → Market Intelligence
    ↓
Expansion Tracking → Storage → Progress Reports
```

---

## 🔗 **COMPONENT INTEGRATION PATTERNS**

### **Pattern 1: Service Orchestration**
**Components**: Job Aggregator ↔ Scraping Service ↔ LLM Provider

```python
# Job Aggregator orchestrates multiple data sources
class JobAggregatorService:
    def __init__(self):
        self.scraping_service = ScrapingOrchestrator()
        self.api_aggregators = [RemoteOKConnector(), GreenhouseConnector()]
        
    async def collect_all_jobs(self, search_params):
        # Parallel collection from API and browser sources
        api_jobs = await self._collect_api_jobs(search_params)
        scraped_jobs = await self.scraping_service.collect_jobs(search_params)
        return self._merge_and_deduplicate(api_jobs + scraped_jobs)
```

**Integration Points**:
- **Data Exchange**: JobPosting objects via Models component
- **Error Handling**: Centralized via Error Handler component
- **Health Monitoring**: Service status via Health Monitor component

---

### **Pattern 2: Data Pipeline Processing**
**Components**: Job Normalizer → Cache → Storage

```python
# Sequential data processing pipeline
class DataProcessingPipeline:
    def __init__(self):
        self.normalizer = JobNormalizer()
        self.cache = CacheManager()
        self.storage = SecureStorage()
        
    def process_job_batch(self, raw_jobs):
        # Stage 1: Normalize data
        normalized_jobs = self.normalizer.normalize_batch(raw_jobs)
        
        # Stage 2: Deduplicate via cache
        unique_jobs = self.cache.filter_duplicates(normalized_jobs)
        
        # Stage 3: Persist results
        return self.storage.save_job_batch(unique_jobs)
```

**Integration Points**:
- **Schema Validation**: JobPosting model from Models component
- **Duplicate Detection**: SQLite cache via Cache component
- **Audit Logging**: File operations via Audit Logger component

---

### **Pattern 3: AI Intelligence Coordination**
**Components**: Enrichment ↔ LLM Provider ↔ Models

```python
# AI-powered job analysis coordination
class IntelligenceOrchestrator:
    def __init__(self):
        self.llm_adapter = LLMAdapter()
        self.enrichment = MultiResumeIntelligenceOrchestrator()
        
    async def analyze_job_compatibility(self, job, resume_portfolio):
        # Stage 1: Select optimal resume
        selected_resume = await self.enrichment.select_optimal_resume(
            job, resume_portfolio
        )
        
        # Stage 2: LLM analysis with multiple providers
        compatibility_score = await self.llm_adapter.score_job(
            job, selected_resume
        )
        
        # Stage 3: Generate enhancements
        enhancements = await self.enrichment.generate_enhancements(
            job, selected_resume, compatibility_score
        )
        
        return {
            'selected_resume': selected_resume,
            'compatibility_score': compatibility_score,
            'enhancements': enhancements
        }
```

**Integration Points**:
- **Multi-Provider Routing**: LLM Provider handles provider failures
- **Resume Portfolio Management**: Enrichment coordinates selection
- **Data Models**: Structured data via Models component

---

## 🏗️ **ARCHITECTURAL INTEGRATION LAYERS**

### **Layer 1: Presentation & Interface**
```
┌─────────────────────────────────────────────┐
│  CLI Component                              │
│  ├── Automated CLI (daily-search)          │
│  ├── Multi-Resume CLI (enhanced workflows) │
│  └── Legacy CLI (backward compatibility)   │
└─────────────────────────────────────────────┘
```
**Dependencies**: Config, Resume Uploader, Error Handler

### **Layer 2: Business Logic & Intelligence**
```
┌─────────────────────────────────────────────┐
│  Enrichment Component                       │
│  ├── Multi-Resume Orchestrator             │
│  ├── Hybrid Selection Engine               │
│  ├── Enhanced Content Analyzer             │
│  └── Resume Discovery Service              │
└─────────────────────────────────────────────┘
```
**Dependencies**: LLM Provider, Models, Cache, Storage

### **Layer 3: Data Collection & Integration**
```
┌─────────────────────────────────────────────┐
│  Job Aggregator + Scraping Service         │
│  ├── API Aggregators (RemoteOK, Careerjet) │
│  ├── Browser Scrapers (Indeed, LinkedIn)   │
│  └── Service Registry & Health Monitoring  │
└─────────────────────────────────────────────┘
```
**Dependencies**: Job Normalizer, Cache, Health Monitor

### **Layer 4: Data Processing & Persistence**
```
┌─────────────────────────────────────────────┐
│  Storage + Cache + Models                   │
│  ├── Secure Storage (files + metadata)     │
│  ├── Cache Manager (deduplication)         │
│  └── Data Models (schemas + validation)    │
└─────────────────────────────────────────────┘
```
**Dependencies**: Audit Logger, Error Handler

### **Layer 5: Infrastructure & Observability**
```
┌─────────────────────────────────────────────┐
│  Config + Monitoring + Error Handling      │
│  ├── Configuration Management              │
│  ├── Health Monitoring & Metrics           │
│  ├── Error Handling & Recovery             │
│  └── Audit Logging & Compliance            │
└─────────────────────────────────────────────┘
```
**Dependencies**: None (foundation layer)

---

## 📊 **CROSS-COMPONENT DATA FLOWS**

### **Data Flow 1: Job Collection to AI Analysis**
```
Search Parameters (Config)
    ↓
Job Sources (Job Aggregator + Scraping Service)
    ↓
Raw Job Data (Various APIs + Web Scraping)
    ↓
Normalized Jobs (Job Normalizer + Models)
    ↓
Deduplicated Jobs (Cache)
    ↓
Resume Portfolio (Enrichment + Resume Discovery)
    ↓
LLM Analysis (LLM Provider + Multiple AI Models)
    ↓
Scored Results (Enrichment + Enhanced Content Analyzer)
    ↓
Export Ready Data (Storage + Secure Storage)
```

### **Data Flow 2: Multi-Resume Intelligence**
```
Resume Portfolio Detection (Resume Discovery Service)
    ↓
Master Resume Identification (Enrichment)
    ↓
Domain Classification (Enhanced Content Analyzer)
    ↓
Two-Stage Selection Process (Hybrid Selection Engine)
    ↓
Keyword Pre-filtering (Cache + Models)
    ↓
LLM Scoring (LLM Provider)
    ↓
Enhancement Generation (Enhanced Content Analyzer)
    ↓
Uniqueness Validation (Enrichment)
    ↓
Excel Export (Storage)
```

### **Data Flow 3: Health Monitoring & Error Recovery**
```
Component Health Checks (Health Monitor)
    ↓
Service Status Aggregation (Health Monitor)
    ↓
Error Detection (Error Handler)
    ↓
Failure Recovery (LLM Provider Fallbacks, Export Fallbacks)
    ↓
Audit Trail (Audit Logger)
    ↓
Webhook Notifications (Webhook)
    ↓
System Metrics (Health Monitor)
```

---

## 🔧 **INTEGRATION CONFIGURATION**

### **Component Communication Protocols**

#### **Synchronous Integration**
- **CLI → Config**: Direct method calls for configuration loading
- **Job Normalizer → Models**: Direct schema validation
- **Cache → Storage**: Direct database operations

#### **Asynchronous Integration**
- **Job Aggregator → Scraping Service**: Async job collection
- **Enrichment → LLM Provider**: Async AI analysis
- **Health Monitor → Webhook**: Event-driven notifications

#### **Event-Driven Integration**
- **Error Handler → Audit Logger**: Error event logging
- **Health Monitor → Webhook**: Health status changes
- **Cache → Storage**: Audit trail events

---

## 🚀 **DEPLOYMENT INTEGRATION PATTERNS**

### **Development Environment**
```
Local Components → Direct Module Imports → Shared Configuration
```

### **Production Environment**
```
Containerized Components → Service Mesh → External Configuration
```

### **Enterprise Environment**
```
Microservices → API Gateway → Distributed Configuration + Monitoring
```

---

## 📈 **PERFORMANCE INTEGRATION CONSIDERATIONS**

### **Caching Strategy**
- **Memory Cache**: Hot data in Enrichment and LLM Provider
- **Disk Cache**: Job deduplication in Cache component
- **Database Cache**: Applied job tracking across sessions

### **Parallel Processing**
- **Job Collection**: Concurrent API and scraping operations
- **LLM Analysis**: Multiple provider requests in parallel
- **Export Generation**: Concurrent Excel worksheet creation

### **Resource Management**
- **Rate Limiting**: Per-source limits in Scraping Service
- **Provider Failover**: Automatic fallback in LLM Provider
- **Memory Management**: Large file handling in Storage components

---

This integration map provides a complete view of how the TPM Job Finder components work together to deliver the Phase 5+ global job intelligence platform. Each component is designed with clear interfaces and responsibilities while maintaining loose coupling for scalability and maintainability.