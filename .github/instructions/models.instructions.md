---
applyTo: "src/**/models/**"
---

# GitHub Copilot Instructions for Data Models

You are a Python data modeling expert. Create robust, type-safe models using Pydantic with clear inheritance patterns.

## Model Standards
- Use Pydantic v2+ with modern syntax (`str | None`, not `Optional[str]`)
- Apply Python 3.13+ type hints and modern generic syntax: `class Model[T] (BaseModel):`

- Follow PEP 8 and SOLID principles
- Lint with `uv ruff` and validate with `uv mypy`
- Use clear inheritance hierarchies

## Organization Structure
```
src/package_name/
├── models/base.py           # Universal base model
└── concern_name/models/
    ├── __init__.py         # Exports
    ├── base.py            # Concern-specific base
    ├── entities.py        # Core domain models
    ├── inputs.py          # CLI args, configs, forms
    ├── outputs.py         # Reports, results, displays
    └── operations.py      # Commands, batch ops
```

## Base Model Templates

### Universal Base Model (`src/package_name/models/base.py`)
```python
from pydantic import BaseModel, ConfigDict
from typing import Any

class UniversalBaseModel(BaseModel):
    """Universal base with standard config."""
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=False,
        ser_json_bytes="base64",
        ser_json_inf_nan="constants",
        strict=False,
        extra="forbid",
    )
    
    def model_dump_safe(self, **kwargs: Any) -> dict[str, Any]:
        defaults = {"exclude_none": True, "mode": "python"}
        defaults.update(kwargs)
        return self.model_dump(**defaults)
```

### Concern-Specific Base Model (`src/package_name/concern_name/models/base.py`)
```python
from pydantic import Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import ClassVar
from ...models.base import UniversalBaseModel

class ConcernBaseModel(UniversalBaseModel):
    """Concern-specific base with common fields."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)
    
    MAX_STRING_LENGTH: ClassVar[int] = 255

class ConcernReadOnlyModel(ConcernBaseModel):
    """Read-only model with frozen configuration."""
    model_config = ConcernBaseModel.model_config.copy()
    model_config.update({"frozen": True, "extra": "ignore"})
```

## Key Patterns

### Modern Generics
```python
class OperationResult[T] (ConcernReadOnlyModel):
    status: str
    data: T | None = None
    errors: list[str] = Field(default_factory=list)
```

### Validation
```python
@field_validator("email")
@classmethod
def normalize_email(cls, value: str) -> str:
    return value.lower().strip()

@computed_field
@property
def display_name(self) -> str:
    return self.metadata.get("full_name", self.username)
```

### Class Methods for Conversion
```python
@classmethod
def from_entity(cls, entity: SomeEntity) -> "SomeModel":
    return cls(field1=entity.field1, field2=entity.field2)
```

## Model Types & Guidelines
- **Entities**: Core business objects with full validation
- **Inputs**: CLI args, configs, creation data - use `from_namespace()` for argparse
- **Outputs**: Results, reports, summaries - prefer read-only models
- **Operations**: Commands, batch ops, file operations with context

## Essential Practices
- Use `ClassVar` for class constants
- Use `Field()` with descriptions for important fields
- Implement `from_*` class methods for conversions
- Use `frozen=True` for output/result models
- Validate paths, emails, and domain-specific rules
- Include computed fields for derived data
- Use `model_dump_safe()` for consistent serialization

