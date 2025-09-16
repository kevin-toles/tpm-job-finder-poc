# Models Component

The Models component provides the core data structures and schemas for the TPM Job Finder POC system. It defines standardized data models for jobs, users, applications, resumes, and multi-resume intelligence features, ensuring consistent data representation across all system components.

## Architecture Overview

The models component follows a modular design with specialized models for different domain areas:

```
models/
├── job.py                      # Job posting data model
├── user.py                     # User profile and preferences
├── application.py              # Job application tracking
├── resume.py                   # Resume data model
├── resume_inventory.py         # Multi-resume intelligence models
└── __init__.py                 # Module initialization
```

## Core Components

### 1. Job Model (job.py)
**Purpose**: Represents job postings with comprehensive metadata and compatibility layers
- **Flexible initialization**: Supports various input formats from different sources
- **UUID generation**: Automatic unique ID assignment for tracking
- **Salary handling**: Multiple salary representation formats (range, string, numeric)
- **Source tracking**: Maintains origin information for data lineage
- **Compatibility aliases**: Supports legacy field names for seamless integration

### 2. User Model (user.py)
**Purpose**: User profile management with skills, preferences, and metadata
- **Dataclass design**: Immutable-by-default with controlled mutation methods
- **Skills management**: Dynamic skill addition/removal with validation
- **Preferences system**: Flexible key-value preference storage
- **Serialization support**: JSON-compatible serialization and deserialization
- **Timestamp tracking**: Automatic creation and update timestamp management

### 3. Application Model (application.py)
**Purpose**: Job application tracking and status management
- **Pydantic validation**: Strict schema validation for data integrity
- **Status tracking**: Application lifecycle management
- **Relationship mapping**: Links users to specific job postings
- **Metadata support**: Flexible notes and additional information storage

### 4. Resume Model (resume.py)
**Purpose**: Resume data representation with structured content
- **Pydantic schema**: Type-safe resume data validation
- **Content parsing**: Structured representation of resume sections
- **Skills extraction**: Dedicated skills list management
- **Experience tracking**: Work history and education representation
- **Version control**: Creation and update timestamp tracking

### 5. Resume Inventory Models (resume_inventory.py)
**Purpose**: Advanced multi-resume intelligence system data structures
- **Portfolio management**: Complete resume portfolio representation
- **Domain classification**: Professional domain categorization system
- **Selection algorithms**: Resume selection result tracking
- **Enhancement system**: Resume improvement recommendation models
- **Intelligence results**: Comprehensive job analysis output structures

## Data Models

### Job Model
```python
from tpm_job_finder_poc.models.job import Job

class Job:
    """Represents a job posting with comprehensive metadata."""
    
    def __init__(self,
                 title: str,
                 company: str,
                 location: str = "",
                 description: str = "",
                 url: str = "",
                 salary_min: Optional[float] = None,
                 salary_max: Optional[float] = None,
                 salary: Optional[str] = None,
                 remote: bool = False,
                 job_type: str = "full-time",
                 posted_date: Optional[datetime] = None,
                 date_posted: Optional[datetime] = None,  # Compatibility alias
                 source: str = "",
                 id: Optional[str] = None,
                 **kwargs)
    
    def to_dict(self) -> Dict[str, Any]
    def __str__(self) -> str
    def __repr__(self) -> str
```

### User Model
```python
from tpm_job_finder_poc.models.user import User

@dataclass
class User:
    """User profile with skills, preferences, and metadata."""
    
    id: str
    name: str
    email: str
    skills: List[str]
    experience_years: int
    current_title: Optional[str] = None
    location: Optional[str] = None
    resume_path: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def add_skill(self, skill: str) -> None
    def remove_skill(self, skill: str) -> None
    def update_preference(self, key: str, value: Any) -> None
    def get_preference(self, key: str, default: Any = None) -> Any
    def to_dict(self) -> Dict[str, Any]
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User'
```

### Application Model
```python
from tpm_job_finder_poc.models.application import Application

class Application(BaseModel):
    """Job application tracking with status management."""
    
    id: Optional[str] = None
    job_id: str
    user_id: str
    status: str = "applied"
    applied_at: str
    notes: Optional[str] = None
```

### Resume Model
```python
from tpm_job_finder_poc.models.resume import Resume

class Resume(BaseModel):
    """Resume data with structured content representation."""
    
    id: Optional[str] = None
    user_id: str
    content: str
    skills: List[str] = []
    experience: List[dict] = []
    education: List[dict] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

### Resume Inventory Models
```python
from tpm_job_finder_poc.models.resume_inventory import (
    ResumeType, DomainClassification, ResumeMetadata,
    ResumeInventory, JobKeywords, SelectionResult,
    BulletPoint, Enhancement, JobIntelligenceResult
)

class ResumeType(Enum):
    """Resume classification types."""
    MASTER = "master"
    CANDIDATE = "candidate"

class DomainClassification(Enum):
    """Professional domain categorization."""
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    CREATIVE = "creative"
    GENERIC = "generic"

@dataclass
class ResumeMetadata:
    """Metadata for individual resume files."""
    id: str
    file_path: Path
    filename: str
    resume_type: ResumeType
    domain: DomainClassification
    skills: List[str]
    experience_years: int
    last_modified: str
    file_size: int
    parsed_content: Optional[Dict[str, Any]] = None

@dataclass
class ResumeInventory:
    """Complete portfolio of user's resumes."""
    master_resume: Optional[ResumeMetadata]
    candidate_resumes: List[ResumeMetadata]
    base_path: Path
    total_resumes: int = field(init=False)
    
    def get_candidates_by_domain(self, domain: DomainClassification) -> List[ResumeMetadata]
    def get_candidate_by_filename(self, filename: str) -> Optional[ResumeMetadata]

@dataclass
class JobIntelligenceResult:
    """Complete multi-resume intelligence analysis result."""
    job_posting: Dict[str, Any]
    selected_resume: Optional[ResumeMetadata]
    selection_rationale: str
    enhancements: List[Enhancement]
    processing_metadata: Dict[str, Any]
```

## Public API

### Job Model API
```python
from tpm_job_finder_poc.models.job import Job

# Create job with flexible initialization
job = Job(
    title="Senior Product Manager",
    company="Tech Corp",
    location="San Francisco, CA",
    description="Leading product development...",
    url="https://example.com/job/123",
    salary="$120k - $160k",
    remote=True,
    source="linkedin"
)

# Convert to dictionary for serialization
job_dict = job.to_dict()

# String representation
print(job)  # Job(id='uuid...', title='Senior Product Manager', ...)
```

### User Model API
```python
from tpm_job_finder_poc.models.user import User

# Create user
user = User(
    id="user123",
    name="John Doe",
    email="john@example.com",
    skills=["Python", "Product Management"],
    experience_years=5,
    current_title="Senior PM"
)

# Manage skills
user.add_skill("Machine Learning")
user.remove_skill("Python")

# Manage preferences
user.update_preference("salary_min", 100000)
preferred_location = user.get_preference("location", "Remote")

# Serialization
user_dict = user.to_dict()
restored_user = User.from_dict(user_dict)
```

### Application Model API
```python
from tpm_job_finder_poc.models.application import Application
from datetime import datetime

# Create application
application = Application(
    job_id="job123",
    user_id="user456",
    status="applied",
    applied_at=datetime.now().isoformat(),
    notes="Applied through LinkedIn"
)

# Pydantic validation automatically enforced
validated_app = Application(**raw_application_data)
```

### Resume Model API
```python
from tpm_job_finder_poc.models.resume import Resume

# Create resume
resume = Resume(
    user_id="user123",
    content="Full resume text content...",
    skills=["Python", "Machine Learning", "Product Management"],
    experience=[
        {"title": "Senior PM", "company": "Tech Corp", "years": 3},
        {"title": "PM", "company": "Startup Inc", "years": 2}
    ],
    education=[
        {"degree": "MBA", "school": "Business School", "year": 2020}
    ]
)

# Automatic validation and ID generation
validated_resume = Resume(**resume_data)
```

### Resume Inventory API
```python
from tpm_job_finder_poc.models.resume_inventory import (
    ResumeInventory, DomainClassification, JobIntelligenceResult
)

# Portfolio management
inventory = ResumeInventory(
    master_resume=master_metadata,
    candidate_resumes=candidate_list,
    base_path=Path("~/resumes")
)

# Domain-based filtering
tech_resumes = inventory.get_candidates_by_domain(DomainClassification.TECHNOLOGY)

# Intelligence result processing
result = JobIntelligenceResult(
    job_posting=job_data,
    selected_resume=selected_resume_metadata,
    selection_rationale="Best match for AI/ML requirements",
    enhancements=enhancement_list,
    processing_metadata={"timestamp": "2025-01-15T10:00:00Z"}
)
```

## Usage Examples

### 1. Complete Job Processing Pipeline
```python
from tpm_job_finder_poc.models.job import Job
from tpm_job_finder_poc.models.user import User
from tpm_job_finder_poc.models.application import Application

def process_job_application(raw_job_data, user_data):
    """Process job application with proper data modeling."""
    # Create job from raw data
    job = Job(
        title=raw_job_data.get('title'),
        company=raw_job_data.get('company'),
        location=raw_job_data.get('location'),
        description=raw_job_data.get('description'),
        url=raw_job_data.get('url'),
        salary=raw_job_data.get('salary'),
        source=raw_job_data.get('source', 'unknown')
    )
    
    # Load user profile
    user = User.from_dict(user_data)
    
    # Create application record
    application = Application(
        job_id=job.id,
        user_id=user.id,
        status="applied",
        applied_at=datetime.now().isoformat(),
        notes=f"Auto-applied via TPM Job Finder"
    )
    
    return {
        'job': job.to_dict(),
        'user': user.to_dict(),
        'application': application.dict()
    }
```

### 2. Multi-Resume Intelligence Integration
```python
from tpm_job_finder_poc.models.resume_inventory import (
    ResumeInventory, ResumeMetadata, DomainClassification,
    JobIntelligenceResult, SelectionResult
)

def analyze_job_with_portfolio(job_data, resume_portfolio_path):
    """Analyze job using multi-resume intelligence."""
    # Load resume portfolio
    inventory = ResumeInventory.from_directory(resume_portfolio_path)
    
    # Job analysis and resume selection
    selection_result = SelectionResult(
        selected_resume=inventory.get_best_match(job_data),
        confidence_score=0.85,
        selection_criteria=["keyword_match", "domain_alignment", "experience_level"],
        alternative_resumes=inventory.get_alternatives(job_data, limit=3)
    )
    
    # Generate intelligence result
    intelligence_result = JobIntelligenceResult(
        job_posting=job_data,
        selected_resume=selection_result.selected_resume,
        selection_rationale=selection_result.get_rationale(),
        enhancements=generate_enhancements(job_data, inventory.master_resume),
        processing_metadata={
            "analysis_timestamp": datetime.now().isoformat(),
            "total_resumes_analyzed": len(inventory.candidate_resumes),
            "processing_time_ms": 1250
        }
    )
    
    return intelligence_result
```

### 3. User Profile Management
```python
from tpm_job_finder_poc.models.user import User

def manage_user_profile(user_id, profile_updates):
    """Manage user profile with validation and tracking."""
    # Load existing user
    user = User.from_dict(load_user_data(user_id))
    
    # Update skills
    if 'new_skills' in profile_updates:
        for skill in profile_updates['new_skills']:
            user.add_skill(skill)
    
    if 'remove_skills' in profile_updates:
        for skill in profile_updates['remove_skills']:
            user.remove_skill(skill)
    
    # Update preferences
    if 'preferences' in profile_updates:
        for key, value in profile_updates['preferences'].items():
            user.update_preference(key, value)
    
    # Update basic fields
    if 'current_title' in profile_updates:
        user.current_title = profile_updates['current_title']
    
    if 'location' in profile_updates:
        user.location = profile_updates['location']
    
    # Save updated profile
    save_user_data(user.to_dict())
    
    return user
```

### 4. Application Tracking System
```python
from tpm_job_finder_poc.models.application import Application
from typing import List, Dict

def track_job_applications(user_id: str) -> Dict[str, Any]:
    """Track all job applications for a user."""
    applications = load_user_applications(user_id)
    
    # Application statistics
    stats = {
        'total_applications': len(applications),
        'by_status': {},
        'recent_applications': [],
        'application_rate': 0.0
    }
    
    # Status breakdown
    for app_data in applications:
        app = Application(**app_data)
        status = app.status
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
    
    # Recent applications (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_apps = [
        Application(**app_data) for app_data in applications
        if datetime.fromisoformat(app_data['applied_at']) > thirty_days_ago
    ]
    
    stats['recent_applications'] = len(recent_apps)
    stats['application_rate'] = len(recent_apps) / 30.0  # per day
    
    return stats

def update_application_status(application_id: str, new_status: str, notes: str = None):
    """Update application status with optional notes."""
    app_data = load_application(application_id)
    application = Application(**app_data)
    
    # Update status (validation handled by Pydantic)
    updated_application = Application(
        id=application.id,
        job_id=application.job_id,
        user_id=application.user_id,
        status=new_status,
        applied_at=application.applied_at,
        notes=notes or application.notes
    )
    
    save_application(updated_application.dict())
    return updated_application
```

## Architecture Decisions

### 1. Mixed Model Paradigms
- **Dataclasses for User**: Mutable objects with controlled state management
- **Standard classes for Job**: Flexible initialization with compatibility support
- **Pydantic for validation**: Strict validation where data integrity is critical
- **Enums for classification**: Type-safe categorization systems

### 2. Backward Compatibility
- **Field aliases**: Support legacy field names during system evolution
- **Flexible initialization**: Accept various input formats from different sources
- **Graceful defaults**: Sensible defaults for optional fields
- **Migration support**: Smooth transition between model versions

### 3. Serialization Strategy
- **JSON compatibility**: All models support JSON serialization/deserialization
- **ISO datetime format**: Consistent timestamp representation
- **Nested object support**: Proper handling of complex nested structures
- **Optional field handling**: Graceful handling of missing or null values

### 4. Multi-Resume Intelligence Design
- **Domain separation**: Clear separation between portfolio and individual resume models
- **Result composition**: Comprehensive result objects for complex analysis
- **Metadata preservation**: Rich metadata tracking for debugging and optimization
- **Extensible enums**: Easy addition of new domains and classifications

## Data Validation

### Job Model Validation
```python
# Automatic UUID generation
job = Job(title="PM", company="Corp")
assert job.id is not None
assert len(job.id) == 36  # UUID format

# Date handling
job_with_date = Job(title="PM", company="Corp", posted_date=datetime.now())
assert job_with_date.date_posted == job_with_date.posted_date

# Compatibility aliases
job_legacy = Job(title="PM", company="Corp", date_posted=datetime.now())
assert job_legacy.posted_date == job_legacy.date_posted
```

### User Model Validation
```python
# Skills management validation
user = User(id="1", name="John", email="john@example.com", skills=[], experience_years=5)
user.add_skill("Python")
assert "Python" in user.skills

user.add_skill("Python")  # Duplicate
assert user.skills.count("Python") == 1  # No duplicates

# Timestamp tracking
original_time = user.updated_at
user.update_preference("test", "value")
assert user.updated_at > original_time
```

### Pydantic Model Validation
```python
from pydantic import ValidationError

# Application validation
try:
    Application(
        job_id="",  # Invalid: empty string
        user_id="user123",
        applied_at="invalid-date"  # Invalid: bad date format
    )
except ValidationError as e:
    print(f"Validation errors: {e.errors()}")

# Resume validation
valid_resume = Resume(
    user_id="user123",
    content="Resume content",
    skills=["Python", "ML"],
    experience=[{"title": "PM", "company": "Corp", "years": 3}]
)
assert valid_resume.user_id == "user123"
```

## Performance Considerations

### Memory Efficiency
- **Lazy loading**: Models support lazy loading of heavy content
- **Optional fields**: Minimize memory usage with optional metadata
- **Efficient serialization**: Optimized JSON serialization for large datasets
- **Reference management**: Proper cleanup of object references

### Processing Speed
- **Fast initialization**: Optimized object creation for batch processing
- **Cached properties**: Expensive computations cached appropriately
- **Batch operations**: Support for efficient batch model operations
- **Stream processing**: Models designed for streaming workflows

## Testing

### Unit Tests
```bash
# Test individual model functionality
pytest tests/unit/test_models/test_job_model.py -v
pytest tests/unit/test_models/test_user_model.py -v
pytest tests/unit/test_models/test_application_model.py -v
pytest tests/unit/test_models/test_resume_model.py -v
pytest tests/unit/test_models/test_resume_inventory.py -v
```

### Integration Tests
```bash
# Test model integration with other components
pytest tests/integration/test_models_integration.py -v

# Test serialization/deserialization
pytest tests/integration/test_model_serialization.py -v

# Test multi-resume intelligence models
pytest tests/integration/test_resume_intelligence_models.py -v
```

### Test Examples
```python
import pytest
from datetime import datetime
from tpm_job_finder_poc.models.job import Job
from tpm_job_finder_poc.models.user import User

def test_job_model_creation():
    """Test job model creation and serialization."""
    job = Job(
        title="Software Engineer",
        company="Tech Corp",
        location="San Francisco",
        salary="$100k - $150k"
    )
    
    assert job.title == "Software Engineer"
    assert job.company == "Tech Corp"
    assert job.id is not None
    assert isinstance(job.posted_date, datetime)
    
    # Test serialization
    job_dict = job.to_dict()
    assert job_dict['title'] == "Software Engineer"
    assert 'id' in job_dict

def test_user_skills_management():
    """Test user skills addition and removal."""
    user = User(
        id="test123",
        name="Test User",
        email="test@example.com",
        skills=["Python"],
        experience_years=3
    )
    
    # Add skill
    user.add_skill("Machine Learning")
    assert "Machine Learning" in user.skills
    
    # Remove skill
    user.remove_skill("Python")
    assert "Python" not in user.skills
    
    # Test duplicate prevention
    user.add_skill("Machine Learning")  # Already exists
    assert user.skills.count("Machine Learning") == 1

def test_user_serialization_round_trip():
    """Test user serialization and deserialization."""
    original_user = User(
        id="test123",
        name="Test User",
        email="test@example.com",
        skills=["Python", "ML"],
        experience_years=5,
        preferences={"location": "Remote", "salary_min": 100000}
    )
    
    # Serialize to dict
    user_dict = original_user.to_dict()
    
    # Deserialize back
    restored_user = User.from_dict(user_dict)
    
    # Verify all fields preserved
    assert restored_user.id == original_user.id
    assert restored_user.name == original_user.name
    assert restored_user.skills == original_user.skills
    assert restored_user.preferences == original_user.preferences

def test_resume_inventory_functionality():
    """Test resume inventory management."""
    from tpm_job_finder_poc.models.resume_inventory import (
        ResumeInventory, ResumeMetadata, DomainClassification, ResumeType
    )
    
    # Create test resumes
    tech_resume = ResumeMetadata(
        id="tech1",
        file_path=Path("/resumes/tech.pdf"),
        filename="tech.pdf",
        resume_type=ResumeType.CANDIDATE,
        domain=DomainClassification.TECHNOLOGY,
        skills=["Python", "ML"],
        experience_years=5,
        last_modified="2025-01-15",
        file_size=1024
    )
    
    business_resume = ResumeMetadata(
        id="biz1",
        file_path=Path("/resumes/business.pdf"),
        filename="business.pdf",
        resume_type=ResumeType.CANDIDATE,
        domain=DomainClassification.BUSINESS,
        skills=["Product Management", "Strategy"],
        experience_years=3,
        last_modified="2025-01-15",
        file_size=2048
    )
    
    # Create inventory
    inventory = ResumeInventory(
        master_resume=None,
        candidate_resumes=[tech_resume, business_resume],
        base_path=Path("/resumes")
    )
    
    # Test domain filtering
    tech_resumes = inventory.get_candidates_by_domain(DomainClassification.TECHNOLOGY)
    assert len(tech_resumes) == 1
    assert tech_resumes[0].filename == "tech.pdf"
    
    # Test filename lookup
    found_resume = inventory.get_candidate_by_filename("business.pdf")
    assert found_resume is not None
    assert found_resume.domain == DomainClassification.BUSINESS
```

## Dependencies

### Core Dependencies
- **dataclasses**: User model implementation
- **typing**: Type hints and annotations
- **datetime**: Timestamp management
- **uuid**: Unique identifier generation
- **pathlib**: File path handling for resume inventory
- **enum**: Classification enums

### External Dependencies
- **pydantic**: Application and Resume model validation
- **Optional dependencies**: JSON serialization libraries for optimization

## Security Considerations

### Data Protection
- **PII handling**: Careful handling of personally identifiable information
- **Email validation**: Proper email format validation in user models
- **Path sanitization**: Secure file path handling in resume inventory
- **Input validation**: Comprehensive input validation for all model fields

### Privacy Compliance
- **Data minimization**: Only store necessary user information
- **Consent tracking**: Support for privacy preference management
- **Data retention**: Configurable data retention policies
- **Audit trails**: Track data access and modifications

## Future Enhancements

### Planned Features
1. **Advanced validation**: Custom validation rules for business logic
2. **Model versioning**: Support for schema evolution and migration
3. **Relationship management**: ORM-style relationship definitions
4. **Caching layer**: Model-level caching for performance optimization
5. **Event system**: Model change events for reactive programming

### Performance Improvements
1. **Lazy loading**: Deferred loading of heavy model attributes
2. **Bulk operations**: Optimized batch model operations
3. **Memory pooling**: Object pooling for high-frequency model creation
4. **Serialization optimization**: Binary serialization options for performance

### Integration Enhancements
1. **Database adapters**: Direct database model mapping
2. **API serialization**: Optimized API response serialization
3. **GraphQL support**: GraphQL schema generation from models
4. **Event sourcing**: Event-driven model state management