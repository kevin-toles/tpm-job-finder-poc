# TPM Job Finder POC - Microservices Monorepo Structure

## Overview
This shows the target structure after all components are refactored into true microservices.

## Target Structure (All Components → Microservices)

```
tpm_job_finder_poc/
├── shared/                           # Common contracts and utilities
│   ├── __init__.py
│   ├── contracts/                    # Service interface contracts
│   │   ├── __init__.py
│   │   ├── audit_service.py         # Audit service contract
│   │   ├── job_collection_service.py # Job collection contract
│   │   ├── ai_intelligence_service.py # AI/ML service contract
│   │   ├── web_scraping_service.py   # Scraping service contract
│   │   ├── data_pipeline_service.py  # Data processing contract
│   │   ├── llm_gateway_service.py    # LLM service contract
│   │   ├── config_service.py         # Configuration service contract
│   │   ├── storage_service.py        # Storage service contract
│   │   └── health_monitoring_service.py # Health service contract
│   ├── types/                        # Common data types
│   │   ├── __init__.py
│   │   ├── job_types.py             # Job posting schemas
│   │   ├── resume_types.py          # Resume schemas
│   │   ├── user_types.py            # User schemas
│   │   └── common_types.py          # Common schemas
│   ├── auth/                         # Authentication utilities
│   │   ├── __init__.py
│   │   ├── token_validator.py
│   │   └── context_provider.py
│   └── monitoring/                   # Observability tools
│       ├── __init__.py
│       ├── metrics.py
│       ├── tracing.py
│       └── logging.py
│
├── audit_service/                    # 🔄 REPLACES: audit_logger/
│   ├── __init__.py
│   ├── api.py                       # FastAPI HTTP endpoints
│   ├── service.py                   # Core service implementation
│   ├── storage.py                   # Storage abstraction
│   ├── builders.py                  # Event builders
│   ├── config.py                    # Service configuration
│   ├── main.py                      # Service entry point
│   ├── requirements.txt             # Service dependencies
│   ├── Dockerfile                   # Container definition
│   ├── README.md                    # Service documentation
│   └── tests/                       # Service-specific tests
│       ├── __init__.py
│       ├── test_service.py
│       ├── test_api.py
│       ├── test_storage.py
│       └── test_integration.py
│
├── job_collection_service/          # 🔄 REPLACES: job_aggregator/
│   ├── __init__.py
│   ├── api.py                       # Job collection HTTP API
│   ├── service.py                   # Orchestration service
│   ├── aggregators/                 # API-based collectors
│   │   ├── __init__.py
│   │   ├── base_aggregator.py
│   │   ├── remoteok.py
│   │   ├── greenhouse.py
│   │   ├── lever.py
│   │   ├── ashby.py
│   │   ├── workable.py
│   │   └── smartrecruiters.py
│   ├── scrapers/                    # Browser-based collectors
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── indeed.py
│   │   ├── linkedin.py
│   │   └── ziprecruiter.py
│   ├── storage.py                   # Job storage layer
│   ├── deduplication.py            # Job deduplication
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── ai_intelligence_service/         # 🔄 REPLACES: enrichment/
│   ├── __init__.py
│   ├── api.py                       # AI processing HTTP API
│   ├── service.py                   # Intelligence orchestrator
│   ├── resume_discovery.py          # Resume portfolio scanning
│   ├── hybrid_selection.py          # Multi-resume selection
│   ├── content_analysis.py          # Semantic analysis
│   ├── cultural_fit.py              # Cultural fit assessment
│   ├── geographic_classifier.py     # Geographic analysis
│   ├── market_trends.py             # Market trend analysis
│   ├── salary_benchmarking.py       # Salary analysis
│   ├── immigration_support.py       # Immigration analysis
│   ├── enterprise_features.py       # Enterprise functionality
│   ├── storage.py                   # AI model storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── web_scraping_service/            # 🔄 REPLACES: scraping_service/
│   ├── __init__.py
│   ├── api.py                       # Scraping HTTP API
│   ├── service.py                   # Scraping orchestrator
│   ├── core/                        # Core scraping engine
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── browser_manager.py
│   │   ├── profile_manager.py
│   │   └── anti_detection.py
│   ├── sources/                     # Site-specific scrapers
│   │   ├── __init__.py
│   │   ├── indeed.py
│   │   ├── linkedin.py
│   │   ├── ziprecruiter.py
│   │   └── greenhouse.py
│   ├── storage.py                   # Scraping results storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── data_pipeline_service/           # 🔄 REPLACES: job_normalizer/
│   ├── __init__.py
│   ├── api.py                       # Data processing HTTP API
│   ├── service.py                   # Pipeline orchestrator
│   ├── parsers/                     # Data parsers
│   │   ├── __init__.py
│   │   ├── base_parser.py
│   │   ├── job_parser.py
│   │   └── resume_parser.py
│   ├── normalizers/                 # Data normalizers
│   │   ├── __init__.py
│   │   ├── base_normalizer.py
│   │   ├── job_normalizer.py
│   │   └── schema_validator.py
│   ├── transformers/                # Data transformers
│   │   ├── __init__.py
│   │   ├── base_transformer.py
│   │   └── enrichment_transformer.py
│   ├── storage.py                   # Pipeline storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── llm_gateway_service/             # 🔄 REPLACES: llm_provider/
│   ├── __init__.py
│   ├── api.py                       # LLM gateway HTTP API
│   ├── service.py                   # LLM orchestrator
│   ├── providers/                   # LLM provider integrations
│   │   ├── __init__.py
│   │   ├── base_provider.py
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── azure_provider.py
│   │   └── local_provider.py
│   ├── prompt_manager.py            # Prompt templates
│   ├── cost_tracker.py              # Usage cost tracking
│   ├── rate_limiter.py              # Rate limiting
│   ├── storage.py                   # Conversation storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── config_service/                  # 🔄 REPLACES: config/
│   ├── __init__.py
│   ├── api.py                       # Configuration HTTP API
│   ├── service.py                   # Config management service
│   ├── providers/                   # Config providers
│   │   ├── __init__.py
│   │   ├── base_provider.py
│   │   ├── file_provider.py
│   │   ├── env_provider.py
│   │   └── vault_provider.py
│   ├── validation.py                # Config validation
│   ├── encryption.py                # Secret encryption
│   ├── storage.py                   # Config storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── storage_service/                 # 🔄 REPLACES: storage/ + secure_storage/
│   ├── __init__.py
│   ├── api.py                       # Storage HTTP API
│   ├── service.py                   # Storage orchestrator
│   ├── providers/                   # Storage providers
│   │   ├── __init__.py
│   │   ├── base_provider.py
│   │   ├── file_provider.py
│   │   ├── s3_provider.py
│   │   ├── database_provider.py
│   │   └── secure_provider.py
│   ├── encryption.py                # Data encryption
│   ├── access_control.py            # Access control
│   ├── metadata.py                  # File metadata
│   ├── storage.py                   # Storage abstraction
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── cache_service/                   # 🔄 REPLACES: cache/
│   ├── __init__.py
│   ├── api.py                       # Cache HTTP API
│   ├── service.py                   # Cache service
│   ├── providers/                   # Cache providers
│   │   ├── __init__.py
│   │   ├── base_provider.py
│   │   ├── memory_provider.py
│   │   ├── redis_provider.py
│   │   └── file_provider.py
│   ├── strategies/                  # Caching strategies
│   │   ├── __init__.py
│   │   ├── lru_strategy.py
│   │   ├── ttl_strategy.py
│   │   └── hybrid_strategy.py
│   ├── storage.py                   # Cache storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── health_monitoring_service/       # 🔄 REPLACES: health_monitor/
│   ├── __init__.py
│   ├── api.py                       # Health monitoring HTTP API
│   ├── service.py                   # Health service
│   ├── monitors/                    # Health monitors
│   │   ├── __init__.py
│   │   ├── base_monitor.py
│   │   ├── service_monitor.py
│   │   ├── database_monitor.py
│   │   └── resource_monitor.py
│   ├── alerts.py                    # Alerting system
│   ├── metrics.py                   # Metrics collection
│   ├── dashboard.py                 # Health dashboard
│   ├── storage.py                   # Health data storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── user_management_service/         # 🔄 REPLACES: models/user.py
│   ├── __init__.py
│   ├── api.py                       # User management HTTP API
│   ├── service.py                   # User service
│   ├── authentication.py            # Auth logic
│   ├── authorization.py             # Permissions
│   ├── profile_manager.py           # User profiles
│   ├── storage.py                   # User storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── resume_management_service/       # 🔄 REPLACES: resume_store/ + resume_uploader/
│   ├── __init__.py
│   ├── api.py                       # Resume management HTTP API
│   ├── service.py                   # Resume service
│   ├── upload_handler.py            # File upload processing
│   ├── parser.py                    # Resume parsing
│   ├── metadata_extractor.py        # Resume analysis
│   ├── storage.py                   # Resume storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── cli_service/                     # 🔄 REPLACES: cli/ + cli_runner/
│   ├── __init__.py
│   ├── api.py                       # CLI service HTTP API
│   ├── service.py                   # CLI orchestrator
│   ├── commands/                    # CLI command handlers
│   │   ├── __init__.py
│   │   ├── base_command.py
│   │   ├── job_commands.py
│   │   ├── resume_commands.py
│   │   └── export_commands.py
│   ├── runners/                     # Command runners
│   │   ├── __init__.py
│   │   ├── async_runner.py
│   │   └── batch_runner.py
│   ├── storage.py                   # CLI results storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── webhook_service/                 # 🔄 REPLACES: webhook/
│   ├── __init__.py
│   ├── api.py                       # Webhook HTTP API
│   ├── service.py                   # Webhook service
│   ├── handlers/                    # Webhook handlers
│   │   ├── __init__.py
│   │   ├── base_handler.py
│   │   ├── deploy_handler.py
│   │   └── integration_handler.py
│   ├── security.py                  # Webhook security
│   ├── storage.py                   # Webhook storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── ml_training_service/             # 🔄 REPLACES: ml_training_pipeline.py
│   ├── __init__.py
│   ├── api.py                       # ML training HTTP API
│   ├── service.py                   # Training service
│   ├── pipelines/                   # Training pipelines
│   │   ├── __init__.py
│   │   ├── base_pipeline.py
│   │   ├── job_matching_pipeline.py
│   │   └── resume_ranking_pipeline.py
│   ├── models/                      # ML models
│   │   ├── __init__.py
│   │   └── model_registry.py
│   ├── storage.py                   # Model storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── ml_scoring_service/              # 🔄 REPLACES: ml_scoring_api.py
│   ├── __init__.py
│   ├── api.py                       # ML scoring HTTP API
│   ├── service.py                   # Scoring service
│   ├── scorers/                     # Scoring engines
│   │   ├── __init__.py
│   │   ├── base_scorer.py
│   │   ├── job_match_scorer.py
│   │   └── resume_rank_scorer.py
│   ├── models/                      # Model loading
│   │   ├── __init__.py
│   │   └── model_loader.py
│   ├── storage.py                   # Scoring storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── analytics_service/               # 🔄 REPLACES: analytics_shared.py + embeddings_service.py
│   ├── __init__.py
│   ├── api.py                       # Analytics HTTP API
│   ├── service.py                   # Analytics service
│   ├── processors/                  # Data processors
│   │   ├── __init__.py
│   │   ├── base_processor.py
│   │   ├── embeddings_processor.py
│   │   └── metrics_processor.py
│   ├── storage.py                   # Analytics storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
├── import_export_service/           # 🔄 REPLACES: import_*.py + excel_exporter.py
│   ├── __init__.py
│   ├── api.py                       # Import/Export HTTP API
│   ├── service.py                   # Import/Export service
│   ├── importers/                   # Data importers
│   │   ├── __init__.py
│   │   ├── base_importer.py
│   │   ├── excel_importer.py
│   │   └── csv_importer.py
│   ├── exporters/                   # Data exporters
│   │   ├── __init__.py
│   │   ├── base_exporter.py
│   │   ├── excel_exporter.py
│   │   └── csv_exporter.py
│   ├── storage.py                   # Import/Export storage
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── README.md
│   └── tests/
│
└── gateway_service/                 # 🆕 NEW: API Gateway for service orchestration
    ├── __init__.py
    ├── api.py                       # Gateway HTTP API
    ├── service.py                   # Gateway service
    ├── routing.py                   # Service routing
    ├── load_balancer.py            # Load balancing
    ├── rate_limiter.py             # Rate limiting
    ├── auth_middleware.py          # Authentication
    ├── config.py
    ├── main.py
    ├── requirements.txt
    ├── Dockerfile
    ├── README.md
    └── tests/

# Root level files remain
├── requirements.txt                 # Global dependencies
├── setup.py                        # Package setup
├── pytest.ini                      # Test configuration
├── conftest.py                     # Global test configuration
├── docker-compose.yml              # Multi-service orchestration
├── Dockerfile                      # Main application container
└── README.md                       # Main project documentation

# Deprecated folder contains OLD component files
DEPRECATED/
├── audit_logger/                    # ❌ OLD: Replaced by audit_service/
├── job_aggregator/                  # ❌ OLD: Replaced by job_collection_service/
├── enrichment/                      # ❌ OLD: Replaced by ai_intelligence_service/
├── scraping_service/                # ❌ OLD: Replaced by web_scraping_service/
├── job_normalizer/                  # ❌ OLD: Replaced by data_pipeline_service/
├── llm_provider/                    # ❌ OLD: Replaced by llm_gateway_service/
├── config/                          # ❌ OLD: Replaced by config_service/
├── storage/                         # ❌ OLD: Replaced by storage_service/
├── secure_storage/                  # ❌ OLD: Replaced by storage_service/
├── cache/                           # ❌ OLD: Replaced by cache_service/
├── health_monitor/                  # ❌ OLD: Replaced by health_monitoring_service/
├── resume_store/                    # ❌ OLD: Replaced by resume_management_service/
├── resume_uploader/                 # ❌ OLD: Replaced by resume_management_service/
├── cli/                             # ❌ OLD: Replaced by cli_service/
├── cli_runner/                      # ❌ OLD: Replaced by cli_service/
├── webhook/                         # ❌ OLD: Replaced by webhook_service/
├── poc/                             # ❌ OLD: Experimental files
├── models/                          # ❌ OLD: Distributed across services
├── ml_training_pipeline.py          # ❌ OLD: Replaced by ml_training_service/
├── ml_scoring_api.py                # ❌ OLD: Replaced by ml_scoring_service/
├── analytics_shared.py              # ❌ OLD: Replaced by analytics_service/
├── embeddings_service.py            # ❌ OLD: Replaced by analytics_service/
├── excel_exporter.py                # ❌ OLD: Replaced by import_export_service/
├── import_analysis.py               # ❌ OLD: Replaced by import_export_service/
├── import_excel.py                  # ❌ OLD: Replaced by import_export_service/
└── error_handler/                   # ❌ OLD: Error handling distributed across services
```

## Key Principles

### 1. **True Microservice Structure**
Each service is completely self-contained with:
- **API Layer** (`api.py`) - HTTP endpoints
- **Service Layer** (`service.py`) - Business logic
- **Storage Layer** (`storage.py`) - Data persistence
- **Configuration** (`config.py`) - Service config
- **Entry Point** (`main.py`) - Service startup
- **Dependencies** (`requirements.txt`) - Service-specific deps
- **Containerization** (`Dockerfile`) - Independent deployment
- **Documentation** (`README.md`) - Service documentation
- **Tests** (`tests/`) - Service-specific test suite

### 2. **Service Communication**
- **Contracts** (`shared/contracts/`) - Define service interfaces
- **Types** (`shared/types/`) - Common data schemas
- **Gateway** (`gateway_service/`) - Service orchestration and routing

### 3. **Deployment Independence**
- Each service can be deployed independently
- Each service has its own container
- Services communicate via HTTP APIs or message queues
- Load balancing and service discovery through gateway

### 4. **Development Workflow**
1. Refactor component → Create new service structure
2. Move old component files → `DEPRECATED/`
3. Update imports to use service contracts
4. Add comprehensive tests for service
5. Update documentation

This structure provides true microservice independence while maintaining monorepo benefits for development and coordination.