# Component README Template

Use this template for creating README.md files in each component directory within `tpm_job_finder_poc/`.

## Template Structure

```markdown
# [Component Name]

[Brief one-line description of component purpose]

## Overview

[2-3 paragraph description covering:
- Primary purpose and responsibilities
- Position in overall system architecture
- Key capabilities and features]

## Architecture

[Directory structure and key files with descriptions]

```
component_name/
├── __init__.py              # Package exports and public interface
├── main_service.py          # Primary service/orchestrator class
├── interfaces.py            # Public interfaces and contracts
├── models.py               # Component-specific data models
├── config.py               # Configuration management
└── utils/                  # Supporting utilities
    ├── helpers.py
    └── validators.py
```

## Public API

### Core Classes

#### [PrimaryServiceClass]
```python
class PrimaryService:
    def __init__(self, config: ComponentConfig): ...
    
    def primary_method(self, input: InputType) -> OutputType:
        """Primary public method description.
        
        Args:
            input: Description of input parameter
            
        Returns:
            Description of return value
            
        Raises:
            SpecificError: When specific condition occurs
        """
```

### Key Methods

#### `method_name(params) -> ReturnType`
- **Purpose**: Brief description
- **Parameters**: Parameter descriptions
- **Returns**: Return value description
- **Example**: Code usage example

## Configuration

### Environment Variables
```bash
COMPONENT_API_KEY=your_api_key_here
COMPONENT_TIMEOUT_MS=30000
COMPONENT_MAX_RETRIES=3
```

### Configuration Class
```python
@dataclass
class ComponentConfig:
    api_key: str
    timeout_ms: int = 30000
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> "ComponentConfig":
        return cls(
            api_key=os.environ["COMPONENT_API_KEY"],
            timeout_ms=int(os.environ.get("COMPONENT_TIMEOUT_MS", "30000")),
            max_retries=int(os.environ.get("COMPONENT_MAX_RETRIES", "3"))
        )
```

## Usage Examples

### Basic Usage
```python
from tpm_job_finder_poc.component_name import ComponentService, ComponentConfig

# Initialize
config = ComponentConfig.from_env()
service = ComponentService(config)

# Use primary functionality
result = service.primary_method(input_data)
```

### Advanced Usage
```python
# More complex usage patterns
# Integration with other components
# Error handling examples
```

## Architecture Decisions

### Key Design Choices
1. **[Decision 1]**: Rationale and trade-offs
2. **[Decision 2]**: Rationale and trade-offs
3. **[Decision 3]**: Rationale and trade-offs

### Dependencies
- **Internal**: List of other TPM components this depends on
- **External**: Third-party libraries and their purposes
- **Optional**: Optional dependencies and feature flags

### Interfaces
- **Implements**: Interfaces this component implements
- **Provides**: Services this component provides to others
- **Consumes**: Services this component consumes from others

## Error Handling

### Exception Types
```python
class ComponentError(Exception):
    """Base exception for component errors."""
    
class ValidationError(ComponentError):
    """Input validation failures."""
    
class ServiceUnavailableError(ComponentError):
    """External service unavailable."""
```

### Error Recovery
- **Retry Logic**: How retries are handled
- **Fallback Strategies**: What happens when primary methods fail
- **Circuit Breaker**: If implemented, how it works

## Testing

### Test Structure
```
tests/
├── unit/
│   ├── test_component_service.py
│   └── test_component_config.py
├── integration/
│   └── test_component_integration.py
└── fixtures/
    └── component_test_data.py
```

### Running Tests
```bash
# Unit tests
pytest tests/unit/test_component_*

# Integration tests  
pytest tests/integration/test_component_*

# Component-specific tests
pytest -k "component_name"
```

## Performance

### Benchmarks
- **Throughput**: Expected operations per second
- **Latency**: Typical response times
- **Memory**: Memory usage patterns
- **Concurrency**: Thread/async safety notes

### Monitoring
- **Health Checks**: Available health check endpoints
- **Metrics**: Key metrics exposed
- **Logging**: Log levels and formats

## Security

### Authentication
- **API Keys**: How API keys are managed
- **Tokens**: Token handling and refresh

### Data Protection
- **PII Handling**: How personally identifiable information is protected
- **Secrets**: Secret management practices
- **Logging**: What is and isn't logged for security

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run component in development mode
python -m tpm_job_finder_poc.component_name.main
```

### Contributing
- **Code Style**: Follow project coding standards
- **Testing**: Add tests for new functionality
- **Documentation**: Update this README for changes

## Related Documentation

- **[Central Component Docs](../../docs/components/component_name.md)**: High-level overview
- **[API Reference](../../docs/api/component_name.rst)**: Detailed API documentation
- **[Integration Guide](../../docs/integration/)**: How to integrate with other components

---

*For questions or issues with this component, see the main project documentation or create an issue.*
```

## Guidelines for Using This Template

### What to Include
- **Real architecture** - Reflect actual code structure
- **Working examples** - Use actual classes and methods from your component
- **Current configuration** - Document actual environment variables and config
- **Honest performance** - Real benchmarks and limitations

### What to Customize
- Replace `[Component Name]` with actual component name
- Update directory structure to match reality
- Replace example classes with actual component classes
- Add component-specific sections as needed

### Keep Updated
- Update when adding new public methods
- Refresh examples when interfaces change
- Update architecture decisions when code evolves
- Keep performance numbers current