# Backward Compatibility During DI Migration

## Overview

This document outlines the approach and patterns used for maintaining backward compatibility while migrating legacy utility modules to a dependency injection (DI) based architecture in the KP Analysis Toolkit. The key component of this strategy is the centralized `di_state.py` utility that provides a consistent pattern for DI integration across legacy modules.

**Navigation Links:**
- [Migration Strategy](#migration-strategy)
- [Centralized DI State Utility](#centralized-di-state-utility)
- [Implementation Pattern](#implementation-pattern)
- [Example Migrations](#example-migrations)
- [Testing Considerations](#testing-considerations)
- [Best Practices](#best-practices)

## Migration Strategy

### Goals

1. **Zero Breaking Changes**: Existing code using legacy utilities continues to work unchanged
2. **Gradual Migration**: Modules can adopt DI services incrementally
3. **Performance**: DI integration adds minimal overhead when not used
4. **Consistency**: All backward compatibility layers follow the same pattern
5. **Maintainability**: Centralized logic reduces code duplication and maintenance burden

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  MIGRATION ARCHITECTURE                                 │
│                                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                      │
│  │   LEGACY        │    │  BACKWARD       │    │   NEW DI        │                      │
│  │   USAGE         │    │  COMPATIBILITY  │    │   SERVICES      │                      │
│  │                 │    │     LAYER       │    │                 │                      │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │                      │
│  │ │Legacy       │ │    │ │utils/       │ │    │ │core/        │ │                      │
│  │ │Client Code  │ │────│→│hash_        │ │────│→│services/    │ │                      │
│  │ │             │ │    │ │generator.py │ │    │ │file_        │ │                      │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ │processing/  │ │                      │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ └─────────────┘ │                      │
│  │ │Legacy       │ │    │ │utils/       │ │    │ ┌─────────────┐ │                      │
│  │ │Client Code  │ │────│→│get_file_    │ │────│→│DI Container │ │                      │
│  │ │             │ │    │ │encoding.py  │ │    │ │Integration  │ │                      │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │                      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                      │
│           │                       │                       │                             │
│           │                       │                       │                             │
│           ▼                       ▼                       ▼                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                        CENTRALIZED DI STATE UTILITY                             │    │
│  │                              (di_state.py)                                      │    │
│  │                                                                                 │    │
│  │  • Consistent DI integration pattern across all legacy modules                  │    │
│  │  • Type-safe service management with generics                                   │    │
│  │  • Factory functions for easy setup                                             │    │
│  │  • Shared TypeVar for consistency                                               │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Centralized DI State Utility

### Core Components

The `src/kp_analysis_toolkit/utils/di_state.py` module provides the following key components:

#### 1. Generic DIState Class

```python
class DIState(Generic[T]):
    """
    Centralized state management for dependency injection integration.
    
    This class provides a standardized way to manage DI state across
    backward compatibility modules.
    """
    
    def __init__(self) -> None:
        self.enabled = False
        self.service: T | None = None
    
    def get_service(self) -> T | None:
        """Get the injected service if available."""
        
    def set_service(self, service: T) -> None:
        """Set the service for DI integration."""
        
    def clear_service(self) -> None:
        """Clear the DI integration state."""
        
    def is_enabled(self) -> bool:
        """Check if DI integration is enabled."""
```

#### 2. Specialized File Processing DI State

```python
class FileProcessingDIState(DIState[FileProcessingService]):
    """
    Specialized DI state for file processing service integration.
    
    This provides type-safe access to the file processing service
    for backward compatibility modules.
    """
```

#### 3. Factory Function for Complete DI Setup

```python
def create_file_processing_di_manager() -> tuple[
    FileProcessingDIState,
    Callable[[], FileProcessingService | None],
    Callable[[FileProcessingService], None],
    Callable[[], None],
]:
    """
    Create a complete DI management setup for file processing service.
    
    Returns:
        A tuple containing:
        - The DI state instance
        - A getter function for the service
        - A setter function for the service
        - A clear function for the service
    """
```

### Key Benefits

1. **Type Safety**: Uses generics to ensure type-safe service management
2. **Consistency**: All backward compatibility layers use the same pattern
3. **Shared TypeVar**: Uses the toolkit's shared `T` from `models/types.py`
4. **Easy Setup**: Factory function provides complete DI management in one call
5. **Testing Support**: Clear functions for test cleanup

## Implementation Pattern

### Standard Implementation Pattern for Legacy Modules

Each legacy utility module follows this consistent pattern:

#### 1. Import and Setup

```python
from kp_analysis_toolkit.utils.di_state import create_file_processing_di_manager

# Global DI state manager
_di_manager, _get_service, _set_service, _clear_service = create_file_processing_di_manager()
```

#### 2. Internal Helper Functions

```python
def _get_file_processing_service() -> object | None:
    """Get the file processing service if DI is available."""
    return _get_service()

def _set_file_processing_service(service: object) -> None:
    """Set the file processing service for DI integration."""
    _set_service(service)  # type: ignore[arg-type]
```

#### 3. Main Function with DI Integration

```python
def legacy_function(input_params) -> output_type:
    """
    Legacy function with DI integration support.
    
    This function supports dependency injection when available, falling back to
    direct implementation for backward compatibility.
    """
    # Try to use DI-based service first
    service = _get_file_processing_service()
    if service is not None:
        try:
            # Use the DI-based service
            return service.method_name(input_params)  # type: ignore[attr-defined]
        except (AttributeError, OSError, Exception):  # noqa: S110
            # Fall back to direct implementation if DI fails
            pass
    
    # Direct implementation fallback
    return direct_implementation(input_params)
```

#### 4. Public DI Integration API

```python
def set_file_processing_service(service: "FileProcessingService") -> None:
    """
    Set the file processing service for dependency injection integration.
    
    This allows the legacy function to use the DI-based service
    when available, while maintaining backward compatibility.
    """
    _set_file_processing_service(service)

def get_file_processing_service() -> object | None:
    """Get the current file processing service if DI is enabled."""
    return _get_file_processing_service()

def clear_file_processing_service() -> None:
    """Clear the file processing service DI integration."""
    _clear_service()
```

## Example Migrations

### 1. Hash Generator Migration

**File**: `src/kp_analysis_toolkit/utils/hash_generator.py`

**Before Migration**:
```python
def hash_string(data: str, algorithm: str = "sha256") -> str:
    """Hash a string using the specified algorithm."""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data.encode('utf-8'))
    return hash_obj.hexdigest()
```

**After Migration**:
```python
# DI state setup using centralized utility
(
    _di_state,
    _get_file_processing_service,
    _set_file_processing_service,
    _clear_file_processing_service,
) = create_file_processing_di_manager()

def hash_string(data: str, algorithm: str = TOOLKIT_HASH_ALGORITHM) -> str:
    """
    Hash a string using the specified algorithm.
    
    This function supports dependency injection when available, falling back to
    direct implementation for backward compatibility.
    """
    # Try to use DI-based file processing service first
    file_service = _get_file_processing_service()
    if file_service is not None:
        try:
            return file_service.hash_string(data, algorithm)  # type: ignore[attr-defined]
        except (AttributeError, ValueError, Exception):  # noqa: S110
            # Fall back to direct implementation if DI fails
            pass

    # Direct implementation fallback
    try:
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data.encode("utf-8"))
        return hash_obj.hexdigest()
    except ValueError as e:
        msg = f"Unsupported hash algorithm: {algorithm}"
        raise ValueError(msg) from e

# Public DI integration API
def set_file_processing_service(service: "FileProcessingService") -> None:
    """Set the file processing service for dependency injection integration."""
    _set_file_processing_service(service)
```

### 2. File Encoding Detection Migration

**File**: `src/kp_analysis_toolkit/utils/get_file_encoding.py`

**Before Migration**:
```python
def detect_encoding(file_path: str | Path) -> str | None:
    """Attempt to detect the encoding of the file."""
    try:
        result: CharsetMatch | None = from_path(file_path).best()
        return result.encoding if result else None
    except Exception:
        return None
```

**After Migration**:
```python
# DI state setup using centralized utility
_di_manager, _get_service, _set_service, _clear_service = create_file_processing_di_manager()

def detect_encoding(file_path: str | Path) -> str | None:
    """
    Attempt to detect the encoding of the file.
    
    This function supports dependency injection when available, falling back to
    direct implementation for backward compatibility.
    """
    # Convert to Path if needed
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Try to use DI-based file processing service first
    file_service = _get_service()
    if file_service is not None:
        try:
            # Use the DI-based encoding detector
            return file_service.detect_encoding(file_path)  # type: ignore[attr-defined]
        except (AttributeError, OSError, Exception):  # noqa: S110
            # Fall back to direct implementation if DI fails
            pass

    # Direct implementation fallback
    try:
        result: CharsetMatch | None = from_path(file_path).best()
    except (OSError, Exception):
        warning(f"Skipping file due to encoding detection failure: {file_path}")
        return None
    else:
        if result is not None:
            return result.encoding
        warning(f"Skipping file due to encoding detection failure: {file_path}")
        return None
```

## Testing Considerations

### 1. Test Structure

Each migrated utility should have comprehensive tests covering:

```python
class TestUtilityDIIntegration:
    """Test DI integration for the utility."""
    
    def test_di_not_set_falls_back_to_direct(self) -> None:
        """Test that function works without DI service set."""
        # Ensure no DI service is set
        clear_service_function()
        
        # Test that function still works with direct implementation
        result = utility_function(test_input)
        assert result == expected_output
    
    def test_di_service_is_used_when_available(self) -> None:
        """Test that DI service is used when available."""
        # Create mock service
        mock_service = Mock()
        mock_service.method_name.return_value = "di_result"
        
        # Set DI service
        set_service_function(mock_service)
        
        # Test that DI service is used
        result = utility_function(test_input)
        assert result == "di_result"
        mock_service.method_name.assert_called_once_with(test_input)
    
    def test_di_fallback_on_service_error(self) -> None:
        """Test fallback when DI service raises an exception."""
        # Create mock service that raises an exception
        mock_service = Mock()
        mock_service.method_name.side_effect = Exception("Service error")
        
        # Set DI service
        set_service_function(mock_service)
        
        # Test that function falls back to direct implementation
        result = utility_function(test_input)
        assert result == expected_direct_output
    
    def test_get_set_clear_service(self) -> None:
        """Test service management functions."""
        # Initially no service
        assert get_service_function() is None
        
        # Set service
        mock_service = Mock()
        set_service_function(mock_service)
        assert get_service_function() is mock_service
        
        # Clear service
        clear_service_function()
        assert get_service_function() is None
```

### 2. Test Cleanup

Always ensure proper cleanup in tests:

```python
@pytest.fixture(autouse=True)
def cleanup_di_state(self) -> Iterator[None]:
    """Ensure DI state is clean for each test."""
    # Clear any existing state
    clear_service_function()
    yield
    # Clean up after test
    clear_service_function()
```

## Best Practices

### 1. Consistent Error Handling

```python
# Try DI service first
service = _get_service()
if service is not None:
    try:
        return service.method_name(params)  # type: ignore[attr-defined]
    except (AttributeError, OSError, Exception):  # noqa: S110
        # Fall back to direct implementation if DI fails
        # Common failures: service lacks method, file issues, etc.
        pass

# Always provide direct implementation fallback
return direct_implementation(params)
```

### 2. Type Safety

```python
# Use type annotations for clarity
def set_service(service: "ServiceType") -> None:
    """Set the service for DI integration."""
    _set_service(service)  # type: ignore[arg-type]

# Return type should match original function
def utility_function(params) -> OriginalReturnType:
    """Function with DI integration."""
```

### 3. Documentation

```python
def utility_function(params) -> ReturnType:
    """
    Description of the function.
    
    This function supports dependency injection when available, falling back to
    direct implementation for backward compatibility.
    
    Args:
        params: Function parameters
        
    Returns:
        The same return type as the original function
        
    """
```

### 4. Service Interface Compatibility

Ensure DI services provide methods that match the legacy function signatures:

```python
# Legacy function
def hash_string(data: str, algorithm: str = "sha256") -> str:
    """Hash a string."""

# DI service should provide compatible method
class FileProcessingService:
    def hash_string(self, data: str, algorithm: str = "sha256") -> str:
        """Hash a string - compatible with legacy function."""
```

## Migration Checklist

When migrating a legacy utility to support DI:

- [ ] Import `create_file_processing_di_manager` from `di_state.py`
- [ ] Set up DI state using tuple unpacking pattern
- [ ] Create internal helper functions for service management
- [ ] Modify main function to try DI service first, then fall back
- [ ] Add public DI integration API functions
- [ ] Include proper error handling with broad exception catching
- [ ] Maintain exact same function signatures and behavior
- [ ] Add comprehensive tests for DI integration
- [ ] Update docstrings to mention DI support
- [ ] Verify no breaking changes to existing usage

## Future Considerations

### 1. Additional Service Types

The `di_state.py` utility can be extended to support other service types:

```python
def create_excel_export_di_manager() -> tuple[...]:
    """Create DI manager for Excel export services."""

def create_parallel_processing_di_manager() -> tuple[...]:
    """Create DI manager for parallel processing services."""
```

### 2. Migration Metrics

Consider adding optional metrics to track DI vs. direct implementation usage:

```python
def track_usage(service_used: bool) -> None:
    """Optional usage tracking for migration metrics."""
    if ENABLE_MIGRATION_METRICS:
        # Log usage patterns
        pass
```

### 3. Deprecation Path

Once DI adoption is complete, backward compatibility layers can be deprecated:

```python
@deprecated("Use DI-based FileProcessingService instead")
def legacy_function(...) -> ...:
    """Legacy function - use DI service instead."""
```

This approach ensures a smooth migration path while maintaining the reliability and compatibility that users expect from the KP Analysis Toolkit.
