# Type Hints Requirements

## Overview

This document establishes the requirements and best practices for using type hints in the KP Analysis Toolkit project. All code must follow these guidelines to ensure consistency, maintainability, and compatibility with Pydantic data validation.

## Python Version Compatibility

- **Target Version**: Python 3.13+
- **Type Checking**: All code must pass strict type checking with `mypy`
- **Runtime**: Type hints should not negatively impact runtime performance

## Project Type System

The KP Analysis Toolkit provides predefined type aliases to ensure consistency across the codebase:

### Common Types (`kp_analysis_toolkit.models.types`)

- **`DisplayableValue`**: Values that can be displayed in Rich output or exported to Excel
- **`ConfigValue`**: Configuration values (simpler subset of DisplayableValue)
- **`PathLike`**: File path types (str | Path)
- **`ResultData`**: Single result record (dict[str, DisplayableValue])
- **`ResultList`**: Collection of results (list[ResultData])
- **`ExcelData`**: Data structure for Excel export
- **`T`**: Generic TypeVar for type-preserving operations

### Process Script Types (`kp_analysis_toolkit.process_scripts.models.types`)

- **`PrimitiveType`**: Basic primitive types (str | int | float)
- **`CollectionType`**: Collection types for primitives
- **`SysFilterValueType`**: Values used in system filtering operations

**Always prefer these predefined types** over creating your own type aliases for similar purposes.

## Core Requirements

### 1. All Functions and Methods Must Have Type Hints

**Required:**
```python
def process_file(file_path: Path, encoding: str = "utf-8") -> ProcessingResult:
    """Process a file and return results."""
    pass

async def async_process(data: list[str]) -> dict[str, Any]:
    """Asynchronously process data."""
    pass
```

**Forbidden:**
```python
def process_file(file_path, encoding="utf-8"):  # Missing type hints
    pass
```

### 2. Class Attributes Must Be Annotated

**Required:**
```python
class FileProcessor:
    """File processing service."""
    
    encoding: str
    max_size: int
    _cache: dict[str, Any]
    
    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding
        self.max_size = 1024 * 1024
        self._cache = {}
```

### 3. Pydantic Model Requirements

All Pydantic models must inherit from `KPATBaseModel` and use proper type annotations:

**Required:**
```python
from src.kp_analysis_toolkit.models.base import KPATBaseModel
from pydantic import Field
from typing import Optional
from pathlib import Path

class FileMetadata(KPATBaseModel):
    """Metadata for processed files."""
    
    file_path: Path = Field(..., description="Path to the processed file")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    encoding: str = Field(default="utf-8", description="File encoding")
    hash_sha256: Optional[str] = Field(None, description="SHA256 hash of file content")
    processed_at: datetime = Field(default_factory=datetime.now)
```

## Type Hint Standards

### 1. Use Modern Union Syntax (Python 3.10+)

**Preferred (Python 3.13):**
```python
def process_data(value: str | int | None = None) -> dict[str, Any]:
    pass
```

**Legacy (avoid in new code):**
```python
from typing import Union, Optional, Dict, Any

def process_data(value: Optional[Union[str, int]] = None) -> Dict[str, Any]:
    pass
```

### 2. Generic Collections

**Preferred:**
```python
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

def cache_results(results: dict[str, list[FileMetadata]]) -> None:
    pass
```

**Legacy (avoid):**
```python
from typing import List, Dict

def process_items(items: List[str]) -> Dict[str, int]:
    pass
```

### 3. Path Handling

Always use `pathlib.Path` for file system paths, or the `PathLike` type alias for flexibility:

**Preferred:**
```python
from pathlib import Path
from kp_analysis_toolkit.models.types import PathLike

def read_config(config_path: Path) -> dict[str, Any]:
    """Read configuration from file."""
    pass

def process_file_path(file_path: PathLike) -> Path:
    """Process a file path, accepting both str and Path objects."""
    return Path(file_path)

def save_results(data: dict[str, Any], output_path: PathLike) -> None:
    """Save results to file."""
    output_file = Path(output_path)
    # Implementation here
    pass
```

**Forbidden:**
```python
def read_config(config_path: str) -> dict[str, Any]:  # Use Path or PathLike instead
    pass
```

### 4. Exception Handling

Type hint exception handling properly:

```python
from typing import Type

def handle_error(
    error: Exception, 
    error_types: tuple[Type[Exception], ...] = (ValueError, FileNotFoundError)
) -> bool:
    """Handle specific error types."""
    return type(error) in error_types
```

### 5. Async/Await

Properly type async functions:

```python
from typing import AsyncGenerator
import asyncio

async def process_files_async(file_paths: list[Path]) -> list[ProcessingResult]:
    """Process multiple files asynchronously."""
    tasks = [process_single_file(path) for path in file_paths]
    return await asyncio.gather(*tasks)

async def stream_results() -> AsyncGenerator[ProcessingResult, None]:
    """Stream processing results."""
    for result in get_results():
        yield result
```

## Advanced Type Hints

### 1. Protocol Classes for Duck Typing

Use `Protocol` for structural typing:

```python
from typing import Protocol
from pathlib import Path

class EncodingDetector(Protocol):
    """Protocol for file encoding detection."""
    
    def detect_encoding(self, file_path: Path) -> str | None:
        """Detect the encoding of a file."""
        ...

class FileValidator(Protocol):
    """Protocol for file validation."""
    
    def validate_file_exists(self, file_path: Path) -> bool:
        """Validate that a file exists and is accessible."""
        ...

def process_file_encoding(
    file_path: Path, 
    detector: EncodingDetector,
    validator: FileValidator
) -> str:
    """Process a file's encoding using dependency injection."""
    if not validator.validate_file_exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    encoding = detector.detect_encoding(file_path)
    return encoding or "utf-8"
```

### 2. Predefined Type Aliases

Use the predefined type aliases from `kp_analysis_toolkit.models.types` and `kp_analysis_toolkit.process_scripts.models.types`:

```python
from kp_analysis_toolkit.models.types import (
    DisplayableValue,
    ConfigValue,
    PathLike,
    ResultData,
    ResultList,
    ExcelData,
    T,  # Generic TypeVar
)
from kp_analysis_toolkit.process_scripts.models.types import (
    PrimitiveType,
    CollectionType,
    SysFilterValueType,
)
from pathlib import Path

def process_config_value(value: ConfigValue) -> DisplayableValue:
    """Process a configuration value for display."""
    if isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, Path):
        return str(value)
    return str(value) if value is not None else None

def format_search_results(results: ResultList) -> ExcelData:
    """Format search results for Excel export."""
    if not results:
        return {}
    
    # Extract columns from first result
    columns = list(results[0].keys())
    excel_data = {col: [] for col in columns}
    
    for result in results:
        for col in columns:
            excel_data[col].append(result.get(col))
    
    return excel_data

def validate_filter_value(value: Any) -> SysFilterValueType:
    """Validate and convert a filter value to the correct type."""
    if isinstance(value, (str, int, float)):
        return value
    elif isinstance(value, (list, set)):
        return value
    else:
        raise ValueError(f"Invalid filter value type: {type(value)}")
```

### 3. TypeVar for Generic Functions

When the predefined types don't meet your needs, use TypeVar for custom generic functions:

```python
from typing import TypeVar, Callable
from kp_analysis_toolkit.models.types import T

# Use the predefined T when possible, or define custom TypeVars
U = TypeVar('U')

def transform_list(items: list[T], transformer: Callable[[T], U]) -> list[U]:
    """Transform a list using the provided function."""
    return [transformer(item) for item in items]

def filter_results(data: ResultList, predicate: Callable[[ResultData], bool]) -> ResultList:
    """Filter results using a predicate function."""
    return [item for item in data if predicate(item)]
```

### 4. Literal Types vs Enums

Choose between `Literal` types and `Enum` classes based on your use case:

**Use `Enum` or `StrEnum` for:**
- Constants that need behavior or methods
- Values used across multiple modules
- When you need case-insensitive matching (with `EnumStrMixin`)
- Business domain concepts

```python
from enum import StrEnum
from kp_analysis_toolkit.models.enums import MessageType
from kp_analysis_toolkit.process_scripts.models.enums import ProducerType
from kp_analysis_toolkit.process_scripts.models.base import EnumStrMixin

# Use existing enums when available
def log_message(message: str, msg_type: MessageType) -> None:
    """Log a message with the specified type."""
    pass

def process_audit_data(producer: ProducerType, data: dict[str, Any]) -> None:
    """Process audit data based on producer type."""
    pass

# Create new enums for domain concepts
class OutputFormat(EnumStrMixin, StrEnum):
    """Supported output formats for data export."""
    
    JSON = "json"
    CSV = "csv" 
    EXCEL = "excel"
    YAML = "yaml"

def export_data(data: dict[str, Any], format: OutputFormat) -> Path:
    """Export data in the specified format."""
    pass
```

**Use `Literal` for:**
- Simple string constants in function signatures
- One-off parameter constraints
- When you don't need enum functionality

```python
from typing import Literal

# Simple parameter constraints
def set_log_level(level: Literal["debug", "info", "warning", "error"]) -> None:
    """Set the logging level."""
    pass

# One-off API parameters  
def generate_report(style: Literal["compact", "detailed"]) -> str:
    """Generate a report in the specified style."""
    pass
```

### 5. Overloads for Multiple Signatures

```python
from typing import overload

@overload
def get_data(source: Path) -> dict[str, Any]:
    ...

@overload
def get_data(source: str, encoding: str) -> dict[str, Any]:
    ...

def get_data(source: Path | str, encoding: str = "utf-8") -> dict[str, Any]:
    """Get data from various sources."""
    if isinstance(source, Path):
        return read_from_path(source)
    return parse_string(source, encoding)
```

## Testing Type Hints

### 1. Type Checking in Tests

Tests should also be properly typed:

```python
import pytest
from pathlib import Path
from src.kp_analysis_toolkit.models.base import KPATBaseModel

def test_file_processing(tmp_path: Path) -> None:
    """Test file processing functionality."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    result = process_file(test_file)
    assert isinstance(result, ProcessingResult)

@pytest.fixture
def sample_data() -> dict[str, Any]:
    """Provide sample data for testing."""
    return {"key": "value", "number": 42}
```

### 2. Mypy Configuration

Ensure strict type checking and `pydantic` support in `pyproject.toml`:

```toml
[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

## Common Patterns

### 1. Configuration Classes

**Preferred: Use Pydantic models inheriting from `KPATBaseModel`**

```python
from pathlib import Path
from pydantic import Field, field_validator
from kp_analysis_toolkit.models.base import KPATBaseModel

class ProcessingConfig(KPATBaseModel):
    """Configuration for file processing."""
    
    input_directory: Path = Field(..., description="Directory containing input files")
    output_directory: Path = Field(..., description="Directory for output files")
    max_file_size: int = Field(
        default=10 * 1024 * 1024, 
        ge=1, 
        description="Maximum file size in bytes"
    )
    allowed_extensions: frozenset[str] = Field(
        default_factory=lambda: frozenset({".txt", ".csv", ".rtf"}),
        description="Allowed file extensions"
    )
    parallel_workers: int = Field(default=4, ge=1, le=16, description="Number of parallel workers")
    
    @field_validator('input_directory', 'output_directory')
    @classmethod
    def validate_directory_exists(cls, v: Path) -> Path:
        """Ensure directories exist and are accessible."""
        if not v.exists():
            raise ValueError(f"Directory does not exist: {v}")
        if not v.is_dir():
            raise ValueError(f"Path is not a directory: {v}")
        return v
    
    @field_validator('allowed_extensions')
    @classmethod
    def validate_extensions_format(cls, v: frozenset[str]) -> frozenset[str]:
        """Ensure all extensions start with a dot."""
        invalid = [ext for ext in v if not ext.startswith('.')]
        if invalid:
            raise ValueError(f"Extensions must start with '.': {invalid}")
        return v
```

**Avoid: Python dataclasses for data models**

```python
# DON'T DO THIS - Use Pydantic instead
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ProcessingConfig:  # Missing validation, no field descriptions
    input_directory: Path
    output_directory: Path
    max_file_size: int = 10 * 1024 * 1024
    allowed_extensions: frozenset[str] = frozenset({".txt", ".csv", ".rtf"})
    parallel_workers: int = 4
```

**Benefits of Pydantic over dataclasses:**
- **Automatic validation**: Field constraints (`ge=1`, `le=16`) are enforced
- **Custom validators**: Can validate paths exist, formats are correct, etc.
- **JSON serialization**: Built-in support for JSON export/import
- **Documentation**: Field descriptions for better API documentation
- **Type coercion**: Automatic conversion of compatible types
- **Integration**: Seamless integration with the rest of the KPAT models

### 2. Result Objects

```python
from typing import Generic
from enum import Enum

from kp_analysis_toolkit.models.types import T

class ResultStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"

class Result(Generic[T], KPATBaseModel):
    """Generic result wrapper."""
    
    status: ResultStatus
    data: T | None = None
    error_message: str | None = None
    
    @property
    def is_success(self) -> bool:
        return self.status == ResultStatus.SUCCESS
```

### 3. Service Interfaces

```python
from abc import ABC, abstractmethod
from typing import Protocol

class FileProcessor(Protocol):
    """Protocol for file processing services."""
    
    def process(self, file_path: Path) -> ProcessingResult:
        """Process a single file."""
        ...
    
    def batch_process(self, file_paths: list[Path]) -> list[ProcessingResult]:
        """Process multiple files."""
        ...
```

## Error Handling and Type Safety

### 1. Validation Errors

```python
from pydantic import ValidationError
from typing import Type

def safe_model_creation(
    model_class: Type[KPATBaseModel], 
    data: dict[str, Any]
) -> tuple[KPATBaseModel | None, list[str]]:
    """Safely create a model instance with error collection."""
    try:
        instance = model_class(**data)
        return instance, []
    except ValidationError as e:
        errors = [f"{error['loc']}: {error['msg']}" for error in e.errors()]
        return None, errors
```

### 2. Type Guards

```python
from typing import TypeGuard

def is_string_list(value: Any) -> TypeGuard[list[str]]:
    """Check if value is a list of strings."""
    return (
        isinstance(value, list) and 
        all(isinstance(item, str) for item in value)
    )

def process_if_string_list(data: Any) -> None:
    if is_string_list(data):
        # TypeGuard ensures data is list[str] here
        for item in data:
            print(item.upper())  # Safe to call str methods
```

## Integration with Pydantic

### 1. Custom Validators

```python
from pydantic import field_validator, model_validator
from typing import Any

class FileConfig(KPATBaseModel):
    """File processing configuration."""
    
    file_path: Path
    max_size: int
    
    @field_validator('file_path')
    @classmethod
    def validate_file_exists(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"File does not exist: {v}")
        return v
    
    @model_validator(mode='after')
    def validate_size_reasonable(self) -> 'FileConfig':
        if self.max_size > 100 * 1024 * 1024:  # 100MB
            raise ValueError("Max size too large")
        return self
```

### 2. Computed Fields

```python
from pydantic import computed_field

class ProcessingResult(KPATBaseModel):
    """Result of file processing."""
    
    file_path: Path
    size_bytes: int
    processing_time_seconds: float
    
    @computed_field
    @property
    def throughput_mbps(self) -> float:
        """Calculate processing throughput in MB/s."""
        if self.processing_time_seconds <= 0:
            return 0.0
        size_mb = self.size_bytes / (1024 * 1024)
        return size_mb / self.processing_time_seconds
```

## Tools and Enforcement

### 1. Pre-commit Hooks

Ensure type checking runs automatically:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, types-requests]
```

### 2. CI/CD Integration

Include type checking in your build pipeline:

```yaml
# In GitHub Actions or similar
- name: Type check with mypy
  run: uv run mypy src/ tests/
```

### 3. IDE Configuration

Configure your IDE for optimal type hint support:

- Enable strict type checking
- Show type information on hover
- Highlight type errors in real-time
- Auto-completion based on type information

## Best Practices Summary

1. **Always use type hints** for all functions, methods, and class attributes
2. **Prefer modern syntax** (`list[str]` over `List[str]`)
3. **Use predefined type aliases** from `kp_analysis_toolkit.models.types` and `kp_analysis_toolkit.process_scripts.models.types`
4. **Use `Path` objects or `PathLike`** for all file system operations
5. **Inherit from `KPATBaseModel`** for all data models
6. **Validate at boundaries** using Pydantic validation
7. **Use `Protocol`** for structural typing and interfaces
8. **Type your tests** to catch test-related bugs
9. **Run `mypy` regularly** and fix all type errors
10. **Document complex types** with clear comments
11. **Keep types simple** - avoid overly complex generic constructs when possible

## Migration Strategy

For existing code without type hints:

1. **Start with public APIs** - add type hints to public functions first
2. **Use `# type: ignore`** temporarily for complex legacy code
3. **Gradually increase strictness** in mypy configuration
4. **Focus on critical paths** - prioritize code that handles data validation
5. **Add tests** to verify type correctness during migration

This approach ensures a smooth transition while maintaining code quality and type safety throughout the project.
