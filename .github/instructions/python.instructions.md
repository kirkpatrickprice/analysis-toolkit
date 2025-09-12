---
applyTo: "**/*.py"
---

# GitHub Copilot Instructions for Python Code

You are a Python expert working as a collaborative development partner. Write high-quality, type-safe, well-tested Python code that adheres to strict standards.

## Code Quality Standards

### Type Safety & Static Analysis
- **MyPy Compliance**: All code MUST pass strict MyPy type checking (`uv run mypy src`)
  - Use Python 3.13+ modern type hints: `str | None` instead of `Optional[str]`
  - Add explicit type annotations to all function signatures and class attributes
  - Use generic types properly: `list[str]`, `dict[str, int]`, etc.
  - Apply `from __future__ import annotations` for forward references when needed
  - Never use `typing.Any` except in very specific cases with justification

- **Ruff Compliance**: All code MUST pass Ruff linting (`uv run ruff check .`)
  - Follow PEP 8 naming conventions and formatting
  - Apply SOLID principles and clean code practices
  - Remove unused imports and variables
  - Use proper docstring formatting (Google style for mkdocstrings)
  - Follow security best practices (avoid f-strings in exceptions, etc.)

### Development Workflow
Before suggesting any code changes:
1. **Analyze existing patterns** in the codebase for consistency
2. **Check import statements** and follow existing module organization
3. **Validate type annotations** are complete and accurate
4. **Consider testing requirements** and suggest test cases

After writing code:
1. **Verify MyPy compliance**: Ensure all types are properly annotated
2. **Verify Ruff compliance**: Follow all linting rules and style guidelines
3. **Suggest corresponding tests**: Recommend unit tests for new functionality
4. **Update documentation**: Include docstrings and suggest doc updates

## Python Language Requirements

### Modern Python Syntax (3.13+)
- Use union types: `str | int | None` instead of `Union[str, int, None]`
- Use built-in generics: `list[str]` instead of `List[str]`
- Apply structural pattern matching (`match`/`case`) when appropriate
- Use positional-only and keyword-only parameters when beneficial

### Type Annotations
```python
# Required: Complete type annotations
def process_data(
    data: list[dict[str, str | int]],
    config: Config | None = None,
    *,
    validate: bool = True,
) -> ProcessResult:
    """Process data with optional configuration."""
    ...

# Required: Generic class annotations
class Repository[T: BaseModel]:
    def save(self, entity: T) -> T:
        ...
```

### Error Handling
- Use specific exception types
- Store f-string messages in variables before raising exceptions
- Implement proper context managers for resource management
- Apply early returns to reduce nesting

### Dependency Injection
- Follow existing DI patterns using `dependency-injector`
- Use protocol/interface definitions for dependencies
- Implement proper container configuration
- Apply constructor injection over property injection

## Code Organization

### Module Structure
- Group related functionality into packages
- Use `__init__.py` files for public API exports
- Apply clear separation between interfaces, models, and implementations
- Follow the existing project structure patterns

### Imports
- Use absolute imports only
- Group imports: standard library, third-party, local
- Sort imports alphabetically within groups
- Remove unused imports

### Documentation
- Write Google-style docstrings for mkdocstrings compatibility
- Include type information in docstrings when helpful
- Document exceptions that may be raised
- Provide usage examples for complex functions

## Testing Requirements

### Unit Test Coverage
- Write pytest-based unit tests for all new functionality
- Use descriptive test names: `test_should_return_valid_result_when_input_is_valid`
- Follow Arrange-Act-Assert pattern
- Mock external dependencies using pytest fixtures

### Test Organization
```python
def test_should_calculate_correct_value_when_given_valid_input():
    # Arrange
    calculator = Calculator()
    input_value = 42
    
    # Act
    result = calculator.calculate(input_value)
    
    # Assert
    assert result == expected_value
```

## Quality Checklist

Before submitting code, ensure:
- [ ] All type annotations are complete and accurate
- [ ] `uv run mypy src` passes with zero errors
- [ ] `uv run ruff check .` passes with zero violations
- [ ] Unit tests exist and pass (`uv run pytest`)
- [ ] Docstrings follow Google style for mkdocstrings
- [ ] Dependencies are properly injected via containers
- [ ] No security violations (checked by Ruff)
- [ ] Code follows existing project patterns and conventions

## Example: High-Quality Function

```python
from __future__ import annotations

from typing import Protocol

from myproject.core.models import ProcessResult, Config


class DataProcessor(Protocol):
    """Protocol for data processing services."""
    
    def process(self, data: list[dict[str, object]]) -> ProcessResult:
        """Process the provided data and return results."""
        ...


def process_user_data(
    data: list[dict[str, object]],
    processor: DataProcessor,
    *,
    config: Config | None = None,
    validate_input: bool = True,
) -> ProcessResult:
    """
    Process user data using the specified processor.
    
    Args:
        data: List of user data dictionaries to process
        processor: Service to handle the data processing
        config: Optional configuration for processing behavior
        validate_input: Whether to validate input data before processing
        
    Returns:
        ProcessResult containing the processed data and metadata
        
    Raises:
        ValueError: If input data is invalid and validation is enabled
        ProcessingError: If the processor encounters an error
        
    Example:
        >>> data = [{"name": "John", "age": 30}]
        >>> processor = UserDataProcessor()
        >>> result = process_user_data(data, processor)
        >>> assert result.success
    """
    if validate_input:
        _validate_user_data(data)
    
    try:
        return processor.process(data)
    except Exception as exc:
        msg = f"Failed to process {len(data)} records"
        raise ProcessingError(msg) from exc


def _validate_user_data(data: list[dict[str, object]]) -> None:
    """Validate that user data contains required fields."""
    for record in data:
        if "name" not in record:
            msg = "Missing required field 'name' in user data"
            raise ValueError(msg)
```

## Integration with Project Tools

### Running Quality Checks
```bash
# Type checking
uv run mypy src

# Linting
uv run ruff check .

# Testing
uv run pytest

# All checks (recommended before committing)
uv run mypy src && uv run ruff check . && uv run pytest
```

Remember: Quality is not negotiable. Every piece of code must meet these standards before being considered complete.
