# Data Models Architecture

## Overview

The KP Analysis Toolkit implements a comprehensive data modeling architecture built on Pydantic for type safety, validation, and serialization. All data models inherit from a common base class and follow consistent patterns for configuration, validation, and error handling.

## Architecture Principles

### Base Model Foundation

All data models inherit from `KPATBaseModel`, providing:

- Consistent Pydantic configuration across the application
- Support for `Path` objects through `arbitrary_types_allowed=True`
- Standardized validation patterns and error handling
- Common serialization and deserialization behavior

### Type Safety and Validation Strategy

The architecture enforces strict type checking and validation through:

- Comprehensive type hints for all fields
- Field validators with custom validation logic
- Cross-field validation for complex business rules
- Path validation mixins for file system operations

## Core Model Hierarchy

### Base Model Structure

```python
from pydantic import BaseModel, ConfigDict

class KPATBaseModel(BaseModel):
    """Base model for all data models in the KP Analysis Toolkit."""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allows Path objects
        validate_assignment=True,
        str_strip_whitespace=True,
    )
```

### Model Categories

#### Program Configuration Models

Program configuration models handle application settings and user preferences as provided through defaults or on the CLI at invocation:

A unique, per-command `ProgramConfig` model exists to capture each command's unique requirements.  Common parameters include:
```python
class ProgramConfig(KPATBaseModel):
    """Class to hold the program configuration."""

    program_path: Path = Path(__file__).parent.parent
    input_file: Path | None = None
    source_files_path: Path | None = None
```

See each command's specific documentation and implementation for additional details

#### Additional Per-Command Models

In addition to each command's `ProgramConfig` model, additional models may be required to represent the data used by each command.  See each command's additional documentation for specific details, with `process_scripts` representing the most complex tool currently in the toolkit.

## Validation Patterns

### Field Validation

Fields are validated at instantiation to ensure that data used by the rest of the application is accurate, well-formed and type-safe.

Datatype-specific mixins are used (especially in `process_scripts`) to ensure that paths, strings, and other unique validation requirements are uniformly implemented.

### Path Validation Mixins

File system validation through reusable mixins:

```python
from pathlib import Path
from pydantic import field_validator

class PathValidationMixin:
    """Mixin for path validation patterns."""
    
    @field_validator('*', mode='before')
    @classmethod
    def validate_path_fields(cls, v):
        if isinstance(v, str) and hasattr(cls, '__path_fields__'):
            field_name = cls.__get_field_name__()
            if field_name in cls.__path_fields__:
                return Path(v)
        return v
```

## Data Processing Integration

### CSV Processing Models

Models supporting CSV data operations:

- DataFrame validation with schema enforcement
- Column requirement validation
- Encoding detection integration
- Error handling with detailed reporting

### Excel Export Models

Models for Excel data transformation:

- Sheet configuration with name sanitization
- Table generation parameters
- Formatting specification models
- Multi-workbook export coordination


## Type System Integration

### Generic Type Support

The architecture supports generic types for reusable models:

- `ResultContainer[T]` for typed result containers
- `ConfigurableModel[TConfig]` for configuration-dependent models
- `ValidationResult[TData]` for validation outcome containers

## Model Extension Patterns

### Service-Specific Extensions

Modules extend base models for specialized requirements. Each command module implements its own specific data models that inherit from the base patterns defined here.

For detailed information about command-specific data models, see:

- [Process Scripts Data Models](./process-scripts-data-models.md) - Complex search configurations, system detection, and YAML processing models

```python
class BaseServiceConfig(KPATBaseModel):
    """Base configuration for service-specific models."""
    service_name: str
    processing_options: dict[str, Any] = Field(default_factory=dict)
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    
    @field_validator('service_name')
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Service name cannot be empty")
        return v.strip()
```

### Composition over Inheritance

Complex models use composition for flexibility:

```python
class ComplexProcessingConfig(KPATBaseModel):
    search_config: SearchConfig
    batch_config: BatchProcessingConfig
    output_config: ExcelExportConfig
    
    def get_effective_config(self) -> dict:
        """Merge configurations with precedence rules."""
        return {
            **self.search_config.model_dump(),
            **self.batch_config.model_dump(),
            **self.output_config.model_dump(),
        }
```

Futher composition is achieved with available mix-ins:
```python
# Provide the "validate_non_empty_string" from the ValidationMixin
from kp_analysis_toolkit.process_scripts.models.base import (
    ConfigModel,
    PathValidationMixin,
    ValidationMixin,
)

class ProgramConfig(KPATBaseModel, PathValidationMixin, ValidationMixin, ConfigModel):
    """Class to hold the program configuration."""

    program_path: Path = Path(__file__).parent.parent
    config_path: Path = program_path / GLOBALS["CONF_PATH"]
    audit_config_file: Path | str | None = None
    source_files_path: Path | None = None
    source_files_spec: str
    out_path: str
    list_audit_configs: bool = False
    list_sections: bool = False
    list_source_files: bool = False
    list_systems: bool = False
    verbose: bool = False

    ...

    @field_validator("source_files_spec")
    @classmethod
    def validate_source_files_spec(cls, value: str) -> str:
        """Validate that source files spec is not empty."""
        return cls.validate_non_empty_string(value) or value
```

## Error Handling and Validation

### Structured Error Reporting

Models provide detailed validation error information:

- Field-level error messages with context
- User-friendly error formatting for CLI output
- Structured error data for programmatic handling

### Validation Context

Validation operates within specific contexts:

- CLI validation for user input
- Service validation for inter-component data
- File validation for external data sources
- Configuration validation for application settings

## Integration with Core Services

### Dependency Injection Integration

Models integrate seamlessly with the DI container:

- Service configuration through model validation
- Runtime model creation through factory patterns
- Service parameter validation through model constraints

### Rich Output Integration

Models support rich text output formatting:

- Structured display for validation errors
- Progress reporting for long-running validations
- Colorized output for different validation states
- Table formatting for model collections

## Testing and Quality Assurance

### Model Testing Patterns

Comprehensive testing covers:

- Field validation edge cases
- Cross-field validation scenarios
- Serialization and deserialization roundtrips
- Error message formatting and clarity

### Test Data Generation

Models support test data creation:

- Factory patterns for model generation
- Faker integration for realistic test data
- Property-based testing for validation logic
- Mock data generation for service testing

## Performance Considerations

### Validation Performance

Optimization strategies include:

- Lazy validation for expensive operations
- Cached validation results for repeated checks
- Minimal validation for internal data transfers
- Optimized regex compilation for pattern validation

### Memory Management

Efficient memory usage through:

- Immutable model instances where appropriate
- Shared validation state for repeated operations
- Garbage collection optimization for large datasets
- Stream processing for large file operations

### Schema Evolution

The application does not currently integrate with a back-end database, so schema updates are not a significant concern.

## Conclusion

The data models architecture provides a robust foundation for type-safe, validated data handling throughout the KP Analysis Toolkit.

The combination of Pydantic's validation capabilities with custom base classes and validation mixins ensures consistent data handling while maintaining flexibility for module-specific requirements.

Key benefits include:

- **Type Safety**: Comprehensive type hints and runtime validation
- **Consistency**: Uniform patterns across all modules
- **Extensibility**: Clear extension points for specialized requirements
- **Integration**: Seamless operation with core services and DI container
- **Quality**: Robust error handling and validation reporting
