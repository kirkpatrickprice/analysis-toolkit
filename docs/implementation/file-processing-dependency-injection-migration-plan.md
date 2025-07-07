# File Processing Service Dependency Injection Migration Plan

## Overview

This document outlines a comprehensive migration plan to implement the `file_processing` core service using the `dependency-injector` framework. The plan addresses the consolidation of file processing utilities (encoding detection, hash generation, and file validation) currently scattered across the codebase into a unified, dependency-injected service architecture.

## Current State Analysis

### Existing File Processing Utilities

| Component | Current Location | Usage Pattern | DI Status |
|-----------|------------------|---------------|-----------|
| **Encoding Detection** | `utils.get_file_encoding.detect_encoding()` | Direct function calls | ❌ Not DI |
| **Hash Generation** | `utils.hash_generator.HashGenerator` | Direct instantiation | ❌ Not DI |
| **File Validation** | Scattered across modules | Ad-hoc implementations | ❌ Not DI |

### Current Usage Locations

#### Encoding Detection (`detect_encoding`)
- `process_scripts/models/base.py` - File model encoding detection
- `process_scripts/process_systems.py` - System file processing
- `rtf_to_text/process_rtf.py` - RTF file encoding detection
- Multiple test files for validation

#### Hash Generation (`hash_file`, `HashGenerator`)
- `process_scripts/process_systems.py` - System file hashing
- `utils/hash_generator.py` - Core hash utilities
- Multiple test files for validation

#### File Validation
- No centralized implementation currently exists
- Ad-hoc path validation scattered across modules
- CLI utilities provide some path validation

### Partially Implemented DI Structure

The framework already has:
- ✅ `FileProcessingService` protocol and service class defined
- ✅ `FileProcessingContainer` container defined (but with incorrect provider references)
- ✅ Protocol definitions for `EncodingDetector`, `HashGenerator`, `FileValidator`
- ❌ Missing concrete implementations for the protocols
- ❌ Missing wiring configuration

## Migration Strategy

### Phase 1: Implementation Layer Creation

Create concrete implementations that conform to the existing protocols.

#### 1.1 Add Protocol Implementations to Existing Utilities

**Approach:** Instead of creating a new implementations file, extend existing utility files to conform to the protocols defined in the file processing service.

**Update File:** `src/kp_analysis_toolkit/utils/get_file_encoding.py`

```python
# Add protocol implementation class to existing file
from __future__ import annotations

from pathlib import Path

from kp_analysis_toolkit.core.services.file_processing import EncodingDetector

# ...existing detect_encoding function...

class ChardetEncodingDetector:
    """Encoding detector implementation using charset-normalizer."""
    
    def detect_encoding(self, file_path: Path) -> str | None:
        """Detect file encoding using charset-normalizer."""
        return detect_encoding(file_path)  # Use existing function
```

**Update File:** `src/kp_analysis_toolkit/utils/shared_funcs.py`

```python
# Add protocol implementation classes to existing file
from __future__ import annotations

from pathlib import Path

from kp_analysis_toolkit.core.services.file_processing import (
    FileValidator,
    HashGenerator,
)

# ...existing hash_file function and HashGenerator class...

class SHA384HashGenerator:
    """Hash generator implementation using SHA384 algorithm."""
    
    def __init__(self) -> None:
        self._generator = HashGenerator()  # Use existing class
    
    def generate_hash(self, file_path: Path) -> str:
        """Generate SHA384 hash for file."""
        return self._generator.hash_file(file_path)


class PathLibFileValidator:
    """File validator implementation using pathlib operations."""
    
    def validate_file_exists(self, file_path: Path) -> bool:
        """Check if file exists and is a file."""
        return file_path.exists() and file_path.is_file()
    
    def validate_directory_exists(self, dir_path: Path) -> bool:
        """Check if directory exists and is a directory."""
        return dir_path.exists() and dir_path.is_dir()
```

#### 1.2 Fix Container Provider References

**Update:** `src/kp_analysis_toolkit/core/containers/file_processing.py`

```python
# File Processing Components
encoding_detector: providers.Factory = providers.Factory(
    "kp_analysis_toolkit.utils.get_file_encoding.ChardetEncodingDetector",
)

hash_generator: providers.Factory = providers.Factory(
    "kp_analysis_toolkit.utils.shared_funcs.SHA384HashGenerator",
)

file_validator: providers.Factory = providers.Factory(
    "kp_analysis_toolkit.utils.shared_funcs.PathLibFileValidator",
)
```

### Phase 2: Service Integration

#### 2.1 Extend Core Services Export

**Update:** `src/kp_analysis_toolkit/core/services/__init__.py`

```python
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService

__all__ = [
    "ExcelExportService",
    "FileProcessingService",  # Add file processing service
    "ParallelProcessingService",
    "SearchEngineService",
]
```

#### 2.2 Add to Core Container

**Update:** `src/kp_analysis_toolkit/core/containers/core.py`

```python
from kp_analysis_toolkit.core.containers.file_processing import FileProcessingContainer

class CoreContainer(containers.DeclarativeContainer):
    """Core services shared across all modules."""
    
    # Configuration
    config = providers.Configuration()
    
    # Rich Output Service
    rich_output: providers.Singleton = providers.Singleton(
        RichOutput,
        verbose=config.verbose,
        quiet=config.quiet,
    )
    
    # File Processing Services
    file_processing_container: providers.Container = providers.Container(
        FileProcessingContainer,
        core=providers.Self(),
    )
    
    file_processing: providers.DependenciesContainer = providers.DependenciesContainer(
        file_processing_service=file_processing_container.file_processing_service,
    )
    
    # Parallel Processing Service
    parallel_processing: providers.Factory[ParallelProcessingService] = providers.Factory(
        ParallelProcessingService,
        rich_output=rich_output,
        max_workers=config.max_workers,
    )
```

#### 2.3 Add to Main Application Container

**Update:** `src/kp_analysis_toolkit/core/containers/application.py`

```python
from kp_analysis_toolkit.core.containers.file_processing import FileProcessingContainer

class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container that wires all module containers together."""
    
    # Core containers
    core: providers.Container = providers.Container(CoreContainer)
    file_processing: providers.Container = providers.Container(
        FileProcessingContainer,
        core=core,
    )
    excel_export: providers.Container = providers.Container(
        ExcelExportContainer,
        core=core,
    )
    
    # Module containers will reference file_processing when needed
```

### Phase 3: Module-by-Module Migration

#### 3.1 Process Scripts Module Migration

**High Priority** - This module heavily uses both encoding detection and hash generation.

**Migration Steps:**

1. **Update Container:** `src/kp_analysis_toolkit/process_scripts/container.py`

```python
class ProcessScriptsContainer(containers.DeclarativeContainer):
    """Services specific to the process scripts module."""
    
    # Dependencies from core
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()
    
    # Process Scripts Services
    system_detection: providers.Factory = providers.Factory(
        SystemDetectionService,
        rich_output=core.rich_output,
        file_processing=file_processing.file_processing_service,  # Inject file processing
    )
    
    search_engine: providers.Factory = providers.Factory(
        SearchEngineService,
        rich_output=core.rich_output,
        file_processing=file_processing.file_processing_service,  # Inject file processing
    )
```

2. **Update Service:** `src/kp_analysis_toolkit/process_scripts/service.py`

```python
class ProcessScriptsService:
    """Main service for the process scripts module."""
    
    def __init__(
        self,
        rich_output: RichOutput,
        file_processing: FileProcessingService,  # Accept file processing service
        system_detection: SystemDetectionService,
        search_engine: SearchEngineService,
    ) -> None:
        self.rich_output = rich_output
        self.file_processing = file_processing  # Store file processing service
        self.system_detection = system_detection
        self.search_engine = search_engine
    
    def _process_system_file(self, file_path: Path) -> dict[str, str | None]:
        """Process a system file using the file processing service."""
        return self.file_processing.process_file(file_path)
```

3. **Update Legacy Usage:** `src/kp_analysis_toolkit/process_scripts/process_systems.py`

Replace direct imports:
```python
# Remove these direct imports
# from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding
# from kp_analysis_toolkit.utils.hash_generator import hash_file

# Add dependency injection usage through service
def generate_file_hash(file: Path, file_processing: FileProcessingService) -> str:
    """Generate the file hash using injected service."""
    result = file_processing.process_file(file)
    return result.get("hash", "")
```

#### 3.2 RTF to Text Module Migration

**Medium Priority** - Uses encoding detection.

**Migration Steps:**

1. **Update Container:** `src/kp_analysis_toolkit/rtf_to_text/container.py`

```python
class RtfToTextContainer(containers.DeclarativeContainer):
    """Services specific to the RTF to text module."""
    
    # Dependencies from core
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()
    
    # RTF Parser Service
    rtf_parser: providers.Factory = providers.Factory(
        RTFParserService,
        rich_output=core.rich_output,
        file_processing=file_processing.file_processing_service,
    )
```

2. **Update Service:** `src/kp_analysis_toolkit/rtf_to_text/services/rtf_parser.py`

```python
class RTFParserService:
    """Service for parsing RTF files and converting to text."""
    
    def __init__(
        self,
        rich_output: RichOutput,
        file_processing: FileProcessingService,
    ) -> None:
        self.rich_output = rich_output
        self.file_processing = file_processing
    
    def convert_rtf_to_text(self, input_file: Path) -> str:
        """Convert RTF file to text using file processing service for encoding."""
        file_info = self.file_processing.process_file(input_file)
        encoding = file_info.get("encoding")
        
        if not encoding:
            raise ValueError(f"Could not detect encoding for {input_file}")
        
        # Continue with RTF processing using detected encoding
        # ...
```

3. **Update Legacy Code:** `src/kp_analysis_toolkit/rtf_to_text/process_rtf.py`

Replace direct usage with service injection pattern where the service is passed to functions that need file processing capabilities.

#### 3.3 Nipper Expander Module Migration

**Lower Priority** - Limited file processing needs, but may benefit from validation.

Use file processing service for CSV file validation and potential future encoding detection needs.

### Phase 4: Testing Migration

#### 4.1 Update Existing Tests

**High Priority Items:**
- Update all tests that mock `detect_encoding` to use the new service
- Update all tests that mock `hash_file` to use the new service
- Create integration tests for the file processing service

#### 4.2 Create Service-Specific Tests

**New File:** `tests/unit/core/services/test_file_processing_service.py`

```python
class TestFileProcessingService:
    """Tests for the FileProcessingService."""
    
    def test_process_file_success(self, tmp_path: Path) -> None:
        """Test successful file processing."""
        # Create test implementations
        encoding_detector = Mock(spec=EncodingDetector)
        hash_generator = Mock(spec=HashGenerator)
        file_validator = Mock(spec=FileValidator)
        rich_output = Mock(spec=RichOutput)
        
        # Configure mocks
        encoding_detector.detect_encoding.return_value = "utf-8"
        hash_generator.generate_hash.return_value = "abc123"
        file_validator.validate_file_exists.return_value = True
        
        # Test service
        service = FileProcessingService(
            encoding_detector=encoding_detector,
            hash_generator=hash_generator,
            file_validator=file_validator,
            rich_output=rich_output,
        )
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        result = service.process_file(test_file)
        
        assert result["encoding"] == "utf-8"
        assert result["hash"] == "abc123"
        assert result["path"] == str(test_file)
```

#### 4.3 Create Container Tests

**New File:** `tests/unit/core/containers/test_file_processing_container.py`

Test that the container properly wires all dependencies.

### Phase 5: Wiring Integration

#### 5.1 Update Application Wiring

**Update:** `src/kp_analysis_toolkit/core/containers/application.py`

```python
def configure_process_scripts_container(
    core_container: CoreContainer,
    file_processing_container: FileProcessingContainer,
    excel_export_container: ExcelExportContainer,
) -> None:
    """Configure the process scripts container with its dependencies."""
    from kp_analysis_toolkit.process_scripts.container import container
    
    container.core.override(core_container)
    container.file_processing.override(file_processing_container)
    container.excel_export.override(excel_export_container)
```

#### 5.2 Update CLI Integration

**Update:** CLI commands to initialize the file processing service through the application container.

### Phase 6: Legacy Code Cleanup

#### 6.1 Remove Direct Imports (After Migration)

After migration is complete, update all modules to stop importing:
- `from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding`
- `from kp_analysis_toolkit.utils.shared_funcs import hash_file` (if it exists)

Instead, these modules should receive the `FileProcessingService` through dependency injection.

#### 6.2 Maintain Backward Compatibility

Keep the utility functions available for any external usage or modules not yet migrated, but add deprecation warnings.

#### 6.3 Update Documentation

Update all documentation to reference the new dependency injection approach.

## Naming Convention Rationale

### Why Not `file_processing_implementations.py`?

The original migration plan proposed creating a new file called `file_processing_implementations.py`, but this conflicts with established naming conventions throughout the codebase:

**❌ Problems with `_implementations` Suffix:**
1. **Inconsistent**: No other files in the codebase use `_implementations` suffix
2. **Redundant**: File location already indicates these are implementations
3. **Too Verbose**: Established patterns use shorter, descriptive names

**✅ Established Conventions:**
- **Service Files**: `{service_name}.py` (e.g., `file_processing.py`, `excel_export.py`)
- **Utility Files**: Descriptive names in `utils/` (e.g., `get_file_encoding.py`, `shared_funcs.py`)
- **Container Files**: `container.py` or descriptive core names
- **Main Services**: `service.py` for module entry points

### Better Approach: Extend Existing Utilities

Instead of creating new files, we extend existing utility files to implement the required protocols:

| Implementation | Existing Location | Approach |
|---|---|---|
| **Encoding Detection** | `utils/get_file_encoding.py` | Add `ChardetEncodingDetector` class |
| **Hash Generation** | `utils/shared_funcs.py` | Add `SHA384HashGenerator` class |
| **File Validation** | `utils/shared_funcs.py` | Add `PathLibFileValidator` class |

**Benefits:**
- ✅ Maintains backward compatibility with existing functions
- ✅ Follows established naming patterns
- ✅ Keeps related functionality together
- ✅ Reduces file proliferation
- ✅ Clear separation: `utils/` = implementations, `core/services/` = interfaces

## Implementation Priority

### High Priority (Phase 1-2)
1. **Create implementation layer** - Foundation for all other work
2. **Fix container provider references** - Critical for DI to work
3. **Integrate with core container** - Makes service available system-wide

### Medium Priority (Phase 3)
1. **Process scripts migration** - Highest usage of file processing utilities
2. **RTF to text migration** - Uses encoding detection extensively

### Lower Priority (Phase 4-6)
1. **Nipper expander migration** - Limited current usage
2. **Test migration and cleanup** - Important but non-blocking
3. **Legacy cleanup** - Can be done incrementally

## Benefits Expected

### 1. **Consistency**
- Unified file processing interface across all modules
- Consistent error handling and logging
- Standardized file metadata extraction

### 2. **Testability**
- Easy to mock file processing components in tests
- Service-level testing with clear interfaces
- Better integration test capabilities

### 3. **Maintainability**
- Single location for file processing logic changes
- Clear dependency relationships
- Protocol-based design allows easy implementation swapping

### 4. **Extensibility**
- Easy to add new file processing capabilities
- Module-specific extensions through enhanced services
- Clear extension points through protocols

## Risk Assessment

### Low Risk
- **Backward compatibility** - Utility functions remain available
- **Incremental migration** - Can be done module by module
- **Clear interfaces** - Protocols define expected behavior

### Medium Risk
- **Test migration complexity** - Many tests mock file processing utilities
- **Cross-module dependencies** - Need careful wiring coordination

### Mitigation Strategies
- **Comprehensive testing** at each phase
- **Gradual migration** with fallback to legacy utilities
- **Clear documentation** of migration steps
- **Backup of current working state** before major changes

## Success Criteria

### Technical Criteria
- [ ] All file processing utilities use dependency injection
- [ ] All tests pass with new implementation
- [ ] No direct imports of file processing utilities in business logic
- [ ] Service can be easily mocked and tested

### Quality Criteria
- [ ] No regression in functionality
- [ ] Improved test coverage of file processing operations
- [ ] Clear separation of concerns between modules
- [ ] Consistent error handling across all file processing operations

## Conclusion

This migration plan provides a structured approach to implementing the file processing core service using dependency injection. The phased approach allows for incremental migration with minimal risk, while the protocol-based design ensures maintainability and extensibility. The plan aligns with the existing dependency injection architecture outlined in the comprehensive DI implementation plan and leverages the already-defined service interfaces.

The migration will significantly improve the codebase's testability, maintainability, and consistency while providing a solid foundation for future file processing enhancements across all modules.
