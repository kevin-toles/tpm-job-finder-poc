# TPM Job Finder POC

A proof-of-concept application for finding and managing Technical Program Manager (TPM) job opportunities.

## Project Structure

```
tpm-job-finder-poc/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore patterns
├── src/                     # Main source code
│   ├── __init__.py
│   ├── core/                # Core application logic
│   │   └── __init__.py
│   ├── connectors/          # Job board connectors
│   │   └── __init__.py
│   ├── models/              # Data models
│   │   └── __init__.py
│   └── utils/               # Utility functions
│       └── __init__.py
├── tests/                   # Test files
│   ├── __init__.py
│   ├── unit/                # Unit tests
│   │   └── __init__.py
│   └── integration/         # Integration tests
│       └── __init__.py
├── config/                  # Configuration files
│   └── __init__.py
└── docs/                    # Documentation
    └── README.md
```

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kevin-toles/tpm-job-finder-poc.git
   cd tpm-job-finder-poc
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/

# Run specific test file
python -m pytest tests/unit/test_example.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Contributing

This is a proof-of-concept project. Please follow standard Python development practices:

1. Write tests for new functionality
2. Ensure code passes linting and formatting checks
3. Update documentation as needed

## License

This project is for demonstration purposes only.