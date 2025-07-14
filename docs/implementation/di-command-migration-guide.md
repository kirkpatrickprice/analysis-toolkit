# Dependency Injection Command Migration Guide

## Overview

This document provides a comprehensive guide for migrating existing toolkit commands to use the Dependency Injection (DI) architecture. It establishes patterns, folder structures, and best practices based on the successful `rtf_to_text` implementation and core service architecture.

## Migration Prerequisites

Before beginning a command migration:

1. **Phase 1 Core Services**: Ensure all core services are available and tested

   - ✅ Rich Output Service (Singleton)
   - ✅ File Processing Service (Factory)
   - ✅ Excel Export Service (Factory)

2. **Understanding**: Review the following architecture documents:

   - `service-package-pattern.md` - Service organization principles
   - `di-service-type.md` - Factory vs Singleton provider decisions
   - `di-full-migration-plan.md` - Overall migration strategy

3. **Testing Foundation**: Existing command functionality should have test coverage

## Standard Folder Structure

### Module Layout Pattern

Each DI-migrated command should follow this standardized folder structure:

```
src/kp_analysis_toolkit/<command_name>/
├── __init__.py                    # Public API exports
├── protocols.py                   # Service protocols/interfaces
├── service.py                     # Main orchestration service
├── container.py                   # DI container configuration
├── models/                        # Data models and configuration
│   ├── __init__.py
│   └── program_config.py          # Pydantic configuration model
└── services/                      # Feature-specific implementations
    ├── __init__.py
    ├── <concern_a>.py              # Specific business logic service
    ├── <concern_b>.py              # Another business logic service
    └── <concern_c>.py              # Additional services as needed
```

### Example: RTF to Text Structure

```
src/kp_analysis_toolkit/rtf_to_text/
├── __init__.py                    # Exports: RtfConverter, RtfToTextService, RtfToTextServiceImpl
├── protocols.py                   # RtfConverter, RtfToTextService protocols
├── service.py                     # RtfToTextService implementation
├── container.py                   # RtfToTextContainer configuration
├── models/
│   ├── __init__.py
│   └── program_config.py          # ProgramConfig for RTF conversion
└── services/
    ├── __init__.py
    └── rtf_converter.py            # RtfConverterService implementation
```

## Key File Purposes and Patterns

### 1. `__init__.py` - Public API Definition

**Purpose**: Define the public interface for external consumption.

**Pattern**:
```python
"""<Command description> module."""

from kp_analysis_toolkit.<command_path>.protocols import (
    <CommandProtocol>,
    <ServiceProtocol>,
)
from kp_analysis_toolkit.<command_path>.service import <CommandService> as <CommandServiceImpl>

__version__ = "0.2.0"

__all__ = [
    "<CommandProtocol>",
    "<ServiceProtocol>", 
    "<CommandServiceImpl>",
]

"""Change History
0.1    Initial version
0.2.0  YYYY-MM-DD: Refactor to use Dependency Injection patterns
"""
```

**Guidelines**:

- Export protocols and main service implementation
- Use descriptive aliases to distinguish protocols from implementations
- Define explicit `__all__` for API control
- Include version history noting DI migration

### 2. `protocols.py` - Interface Definitions

**Purpose**: Define contracts between service consumers and providers using Python protocols.

**Pattern**:
```python
"""Protocol definitions for <command> services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path
    # Other type-only imports


class <FeatureService>(Protocol):
    """Protocol for <specific feature> operations."""

    def <primary_method>(self, <params>) -> <return_type>:
        """One-line docstring to capture the intent of the method."""
        ...


class <CommandService>(Protocol):
    """Protocol for the main <command> service orchestration."""

    def <orchestration_method>(self, <params>) -> <return_type>:
        """One-line docstring to capture the intent of the method."""
       ...
```

**Guidelines**:

- One protocol per major service interface
- Use minimal docstrings on the class definition and usually no docstrings on the class methods as these will be defined in more detail on the implementations
- Use `TYPE_CHECKING` imports to avoid circular dependencies
- Follow the established naming convention: `<ServiceName>` (not `<ServiceName>Protocol`)

### 3. `service.py` - Main Orchestration Service

**Purpose**: Implement the main service that coordinates all command functionality.

**Pattern**:
```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.<command>.protocols import <FeatureService>


class <CommandService>:
    """Main service for the <command> module."""

    def __init__(
        self,
        <feature_service>: <FeatureService>,
        rich_output: RichOutputService,
        file_processing: FileProcessingService,
    ) -> None:
        """
        Initialize the <command> service.

        Args:
            <feature_service>: Service for <specific functionality>
            rich_output: Service for rich terminal output
            file_processing: Service for file processing operations

        """
        self.<feature_service> = <feature_service>
        self.rich_output = rich_output
        self.file_processing = file_processing

    def <main_operation>(self, <params>) -> <return_type>:
        """
        <Description of main operation>.

        Args:
            <param>: <description>

        Returns:
            <return description>

        Raises:
            <ExceptionType>: <when this is raised>

        """
        try:
            self.rich_output.info(f"Starting <operation>: {<param>}")

            # Delegate to feature service
            result = self.<feature_service>.<operation>(<params>)

            self.rich_output.success(f"Completed <operation>")
            return result

        except Exception as e:
            self.rich_output.error(f"<Operation> failed: {e}")
            raise
```

**Guidelines**:

- Accept feature services through protocol interfaces
- Always inject core services (rich_output, file_processing, excel_export as needed)
- Use dependency injection for all external services
- Delegate implementation details to feature services
- Maintain consistent error handling and logging patterns
- Add thorough docstrings to the implementations

### 4. `container.py` - DI Container Configuration

**Purpose**: Configure dependency injection providers and wiring for the module.

**Pattern**:
```python
from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

if TYPE_CHECKING:
    from kp_analysis_toolkit.<command>.protocols import <FeatureService>, <CommandService>


class <CommandContainer>(containers.DeclarativeContainer):
    """Services specific to the <command> module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()

    # Feature Services
    <feature_service>: providers.Factory[<FeatureService>] = providers.Factory(
        "kp_analysis_toolkit.<command>.services.<feature_module>.<FeatureServiceImpl>",
        rich_output=core.rich_output,
        file_processing=core.file_processing_service,
    )

    # Main Module Service
    <command_service>: providers.Factory[<CommandService>] = providers.Factory(
        "kp_analysis_toolkit.<command>.service.<CommandServiceImpl>",
        <feature_service>=<feature_service>,
        rich_output=core.rich_output,
        file_processing=core.file_processing_service,
    )


# Module's global container instance
container = <CommandContainer>()


def wire_<command>_container() -> None:
    """
    Wire the <command> container for dependency injection.

    This function should be called when the <command> module is initialized
    to ensure all dependencies are properly wired for injection.
    """
    container.wire(
        modules=[
            "kp_analysis_toolkit.<command>.service",
            "kp_analysis_toolkit.<command>.services.<feature_module>",
        ],
    )
```

**Guidelines**:

- Use `Factory` providers by default (see Provider Type Decisions below)
- Reference core services through `core.` dependency container
- Use string references for service classes to avoid circular imports
- Include type annotations for all providers
- Include descriptive docstrings throughout
- Document wiring function purpose and usage as docstrings

### 5. `services/<concern>.py` - Feature Implementation

**Purpose**: Implement specific business logic for distinct functional areas.

**Pattern**:
```python
"""<Feature description> service using dependency injection."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService


class <FeatureServiceImpl>:
    """Service for <specific feature> using DI services."""

    def __init__(
        self,
        rich_output: RichOutputService,
        file_processing: FileProcessingService,
    ) -> None:
        """
        Initialize the <feature> service.

        Args:
            rich_output: Service for rich terminal output
            file_processing: Service for file processing operations

        """
        self.rich_output = rich_output
        self.file_processing = file_processing

    def <feature_method>(self, <params>) -> <return_type>:
        """
        <Feature-specific operation>.

        Args:
            <param>: <description>

        Returns:
            <return description>

        Raises:
            <ExceptionType>: <when this is raised>

        """
        # Implementation using injected services
        try:
            # Use self.rich_output for user feedback
            # Use self.file_processing for file operations
            # Use self.excel_export for Excel operations (if injected)
            
            result = <implementation>
            
            self.rich_output.debug(f"Successfully completed <operation>")
            return result
            
        except Exception as e:
            error_msg = f"Failed <operation>: {e}"
            self.rich_output.error(error_msg)
            raise <SpecificException>(error_msg) from e
```

**Guidelines**:

- Focus on single responsibility (one concern per service)
- Use injected core services for all I/O operations
- Include comprehensive error handling with user feedback
- Use specific exception types where appropriate
- Use descriptive docstrings for all methods
- Follow consistent patterns for logging and debugging
- Create non-public helper functions ("def _helper_function") to simplify code in exported functions

## Core Service Integration Patterns

### Consuming Core Services

All command services should consume core services through the `core` dependency container:

```python
# In container.py
class <CommandContainer>(containers.DeclarativeContainer):
    # Dependencies from core containers
    core = providers.DependenciesContainer()

    # Service configuration
    <service>: providers.Factory[<ServiceType>] = providers.Factory(
        "<service_class_path>",
        rich_output=core.rich_output,                    # Singleton
        file_processing=core.file_processing_service,    # Factory
        excel_export=core.excel_export_service,          # Factory (if needed)
    )
```

### Core Service Usage Patterns

#### Rich Output Service (Singleton)
```python
# User feedback and progress reporting
self.rich_output.info("Starting operation...")
self.rich_output.success("Operation completed")
self.rich_output.error("Operation failed")
self.rich_output.warning("Potential issue detected")
self.rich_output.debug("Debug information")

# Progress tracking
with self.rich_output.progress() as progress:
    task = progress.add_task("Processing files...", total=len(files))
    for file in files:
        # Process file
        progress.advance(task)
```

#### File Processing Service (Factory)
```python
# File validation and encoding detection
if not self.file_processing.validate_file_exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

encoding = self.file_processing.detect_encoding(file_path)
file_hash = self.file_processing.generate_hash(file_path)
```

#### Excel Export Service (Factory - if needed)
```python
# Excel workbook creation and data export
self.excel_export.export_dataframe_to_excel(
    df=processed_data,
    output_path=output_file,
    sheet_name="Results",
    title="Processing Results",
    as_table=True,
)
```

## Container Connection Architecture

### Application Container Integration

Each command container must be integrated into the main application container:

```python
# In src/kp_analysis_toolkit/core/containers/application.py
class ApplicationContainer(containers.DeclarativeContainer):
    
    # Core services
    core = providers.Container(
        CoreContainer,
        # ... core configuration
    )
    
    # Command containers
    <command> = providers.Container(
        <CommandContainer>,
        core=core,
    )
```

### Container Dependency Flow

```
ApplicationContainer
├── CoreContainer (core)
│   ├── RichOutputService (Singleton)
│   ├── FileProcessingService (Factory)
│   └── ExcelExportService (Factory)
│
└── <CommandContainer> (<command>)
    ├── core = DependenciesContainer() → CoreContainer
    ├── <FeatureService> (Factory)
    │   ├── rich_output → core.rich_output
    │   └── file_processing → core.file_processing_service
    │
    └── <CommandService> (Factory)
        ├── <feature_service> → <FeatureService>
        ├── rich_output → core.rich_output
        └── file_processing → core.file_processing_service
```

## Provider Type Decisions

### Factory vs Singleton Guidelines

Based on `di-service-type.md`, follow these patterns:

#### Use Factory Provider (Default)

- **Command services**: Each command execution should get fresh instances
- **Feature services**: Stateless operations that don't maintain state
- **Data processing services**: Services that transform data without side effects
- **Validation services**: Services that validate input without maintaining state

```python
# Example: RTF conversion services
rtf_converter_service: providers.Factory[RtfConverter] = providers.Factory(...)
rtf_to_text_service: providers.Factory[RtfToTextService] = providers.Factory(...)
```

#### Use Singleton Provider (Rare)

- **Stateful services with global configuration**: Only if the command service needs to maintain state across operations
- **Resource-heavy services**: Services expensive to create
- **Services with side effects**: Where consistency across operations matters

```python
# Example: If a command needed to maintain global state
command_config_service: providers.Singleton[ConfigService] = providers.Singleton(...)
```

### Default Recommendation
**Use Factory providers for all command services** unless you have a specific requirement for shared state.

## Migration Checklist

### Phase 1: Preparation

- [ ] Review existing command functionality and identify distinct concerns
- [ ] Map out core service dependencies (rich_output, file_processing, excel_export)
- [ ] Design protocol interfaces based on existing public methods
- [ ] Plan service breakdown for `services/` folder

### Phase 2: Structure Creation

- [ ] Create folder structure following standard layout
- [ ] Implement `protocols.py` with comprehensive interfaces
- [ ] Create `models/program_config.py` if not already DI-compatible
- [ ] Set up `container.py` with proper provider configuration

### Phase 3: Service Implementation

- [ ] Implement feature services in `services/` folder
- [ ] Implement main orchestration service in `service.py`
- [ ] Update `__init__.py` with proper exports
- [ ] Configure container wiring function

### Phase 4: Integration

- [ ] Add command container to application container
- [ ] Update CLI command to use DI services
- [ ] Remove direct utility function calls
- [ ] Update error handling to use injected Rich Output

### Phase 5: Testing and Validation

- [ ] Run mypy type checking (strict mode)
- [ ] Run ruff linting
- [ ] Execute all existing unit tests
- [ ] Execute integration tests
- [ ] Verify performance benchmarks
- [ ] Test CLI integration end-to-end

### Phase 6: Documentation

- [ ] Update command documentation
- [ ] Document any new service interfaces
- [ ] Update migration plan status
- [ ] Create any necessary troubleshooting notes

## Common Patterns and Best Practices

### Error Handling Pattern
```python
try:
    self.rich_output.info(f"Starting {operation}")
    result = self._perform_operation(params)
    self.rich_output.success(f"Completed {operation}")
    return result
except SpecificException as e:
    self.rich_output.error(f"{operation} failed: {e}")
    raise
except Exception as e:
    self.rich_output.error(f"Unexpected error in {operation}: {e}")
    raise
```

### Progress Reporting Pattern
```python
def process_multiple_items(self, items: list[Item]) -> list[Result]:
    """Process multiple items with progress reporting."""
    if not items:
        self.rich_output.warning("No items provided for processing")
        return []

    self.rich_output.header(f"Processing {len(items)} items")
    
    results = []
    successful = 0
    
    with self.rich_output.progress() as progress:
        task = progress.add_task("Processing items...", total=len(items))
        
        for item in items:
            try:
                result = self._process_single_item(item)
                results.append(result)
                successful += 1
            except Exception as e:
                self.rich_output.error(f"Failed to process {item}: {e}")
            finally:
                progress.advance(task)
    
    self.rich_output.success(f"Successfully processed {successful}/{len(items)} items")
    return results
```

### File Discovery Pattern
```python
def discover_files(self, input_path: Path, pattern: str = "*.ext") -> list[Path]:
    """Discover files matching pattern."""
    if input_path.is_file() and input_path.match(pattern):
        return [input_path]
    elif input_path.is_dir():
        files = list(input_path.rglob(pattern))
        self.rich_output.info(f"Found {len(files)} files in {input_path}")
        return files
    else:
        self.rich_output.warning(f"No files found at {input_path}")
        return []
```

## Troubleshooting

### Common Issues

1. **Circular Import Errors**: Use string references in container providers and TYPE_CHECKING imports
2. **Protocol Compliance**: Ensure concrete implementations match protocol method signatures exactly
3. **Container Wiring**: Remember to call wiring function during module initialization
4. **Provider Types**: Default to Factory unless you need shared state

### Testing Protocol Compliance
```python
def test_protocol_compliance():
    """Verify concrete implementations satisfy protocols."""
    from <command>.protocols import <ServiceProtocol>
    from <command>.services.<service> import <ServiceImpl>
    
    # This will fail if signatures don't match
    service: <ServiceProtocol> = <ServiceImpl>(mock_deps)
    assert hasattr(service, 'required_method')
```

## Migration Examples

### Simple Command (RTF to Text Pattern)

- Single feature service (`rtf_converter.py`)
- Simple orchestration service
- Uses rich_output and file_processing core services
- No Excel export requirements

### Medium Command (Nipper Expander Pattern)

- Multiple feature services (`csv_processor.py`, `data_expander.py`)
- Orchestration with batch processing
- Uses all core services including excel_export
- Complex data transformation pipeline

### Complex Command (Process Scripts Pattern)

- Multiple feature services with different concerns
- Advanced service orchestration
- Custom service requirements (search engine, system detection)
- Parallel processing coordination
- Multiple Excel workbook outputs

## Conclusion

This migration guide provides the foundation for consistently implementing DI-based command services. Following these patterns ensures:

- **Consistency**: All commands follow the same architectural patterns
- **Maintainability**: Clear separation of concerns and well-defined interfaces
- **Testability**: Protocol-based interfaces enable easy mocking and testing
- **Scalability**: Service-based architecture supports future enhancements
- **Type Safety**: Full mypy compliance with comprehensive type annotations

Each migration should reference this guide and adapt the patterns to the specific requirements of the command being migrated.
