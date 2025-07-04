# Comprehensive Dependency Injection Implementation Plan

## Overview

This document outlines a comprehensive refactoring plan to implement dependency injection throughout the KP Analysis Toolkit codebase using the `dependency-injector` framework. This approach addresses not only the RichOutput global singleton pattern but also provides a holistic DI architecture for all major components.

**Navigation Links:**
- [Framework Selection - dependency-injector](#framework-selection-dependency-injector)
- [Core Container Implementation](#core-container-shared-services)
- [File Processing Container](#file-processing-container) 
- [Excel Export Container](#excel-export-container)
- [Application Container](#main-application-container)
- [Process Scripts Container](#process-scripts-container)
- [CLI Integration](#updated-cli-integration-with-hierarchical-containers)
- [Testing Strategy](#testing-strategy)
- [Implementation Timeline](#implementation-timeline-hierarchical-approach)

## Framework Selection: `dependency-injector`

We will use the `dependency-injector` framework for several key reasons:

1. **Declarative Configuration**: Clean container definitions with type safety
2. **Multiple Provider Types**: Singleton, Factory, Resource, Configuration providers
3. **Lazy Initialization**: Components created only when needed
4. **Excellent Testing Support**: Built-in mocking and overriding capabilities
5. **Minimal Performance Overhead**: Optimized for production use
6. **Type Safety**: Full mypy support with proper type annotations

## Directory Structure and File Organization

The following directory structure shows the complete organization of containers, services, and related files for the dependency injection implementation:

```
src/kp_analysis_toolkit/
├── core/
│   ├── containers/
│   │   ├── __init__.py                    # Container exports
│   │   ├── core.py                        # Core services (RichOutput, ParallelProcessing)
│   │   ├── file_processing.py             # File processing container
│   │   ├── excel_export.py                # Excel export container
│   │   └── application.py                 # Main application container
│   ├── services/
│   │   ├── __init__.py                    # Service exports
│   │   ├── file_processing.py             # File processing service & protocols
│   │   ├── excel_export.py                # Excel export service & protocols
│   │   └── parallel_processing.py         # Parallel processing service & protocols
│   └── parallel_engine/                   # Parallel processing implementations
│       ├── __init__.py
│       ├── executor_factory.py            # ProcessPoolExecutorFactory
│       ├── progress_tracker.py            # ProgressTracker
│       └── interrupt_handler.py           # InterruptHandler
├── process_scripts/
│   ├── container.py                       # Process scripts container
│   ├── service.py                         # Main process scripts service
│   ├── services/
│   │   ├── __init__.py
│   │   ├── search_config.py               # YAML search config service & protocols
│   │   ├── search_engine.py               # Search engine service & protocols
│   │   └── system_detection.py            # System detection service & protocols
│   └── utils/                            # Process scripts utilities
│       ├── os_detection.py               # OS detection implementations
│       ├── producer_detection.py         # Producer detection implementations
│       └── distro_classification.py      # Distribution classification implementations
├── nipper_expander/
│   ├── container.py                       # Nipper expander container
│   ├── service.py                         # Main nipper expander service
│   └── services/                          # Module-specific services (future)
│       └── __init__.py
├── rtf_to_text/
│   ├── container.py                       # RTF to text container
│   ├── service.py                         # Main RTF to text service
│   └── services/                          # Module-specific services (future)
│       └── __init__.py
└── utils/
    ├── rich_output.py                     # RichOutput (with backward compatibility)
    ├── excel_utils.py                     # Excel utilities & implementations
    ├── get_file_encoding.py               # Encoding detection implementations
    └── shared_funcs.py                    # Hash & validation implementations
```

**File Organization Summary:**

| Component Type | Location | Purpose |
|---|---|---|
| **Core Containers** | `core/containers/` | Shared service DI configuration |
| **Core Services** | `core/services/` | Reusable service implementations |
| **Module Containers** | `{module}/container.py` | Module-specific DI configuration |
| **Module Services** | `{module}/service.py` | Main module service classes |
| **Module Utilities** | `{module}/services/` | Module-specific implementations |
| **Global Utilities** | `utils/` | Shared utility implementations |
| **Protocol Classes** | Embedded | Implemented in services |
| **Implementation Classes** | Embdded | Concrete implementations included in containers |

**Key Benefits:**

This hierarchical approach provides several key benefits:

1. **Separation of Concerns**: Each container has a single, clear responsibility
2. **Module Independence**: Process scripts services are only loaded when the process scripts module is used
3. **Maintainability**: Changes to one module don't affect others
4. **Testing**: Each container can be tested independently
5. **Performance**: Only necessary services are instantiated
6. **Team Development**: Different teams can work on different containers without conflicts

## Dependency Injection Wiring Strategy

This implementation follows a **Distributed Wiring** approach, where each module is responsible for wiring its own dependencies. This approach provides the best balance of modularity, maintainability, and clear separation of concerns.

### Architectural Rationale

**Why Distributed Wiring?**

1. **Module Independence**: Each module controls its own dependency wiring, making modules more self-contained and easier to understand
2. **Reduced Coupling**: Modules don't need to know about the internal wiring details of other modules
3. **Easier Testing**: Each module can be tested in isolation with its own container configuration
4. **Team Development**: Different teams can work on different modules without interfering with each other's DI setup
5. **Cleaner Architecture**: The application container focuses only on orchestrating high-level module composition

**Cross-Module Dependency Handling:**

- **Core Services**: Shared services (RichOutput, ParallelProcessing, FileProcessing, ExcelExport) are managed by the application container
- **Module Services**: Each module wires its own internal dependencies and receives shared services as parameters
- **Service Boundaries**: Clear interfaces define what services are shared vs. module-specific

**Wiring Responsibility Distribution:**

| Component | Wiring Responsibility | Purpose |
|---|---|---|
| **Application Container** | Cross-module service composition | Orchestrates core containers and module containers |
| **Module Containers** | Module-specific service wiring | Wires internal module dependencies |
| **Core Container** | Shared service wiring | Wires services used across multiple modules |

### Wiring Function Patterns

Each module follows a consistent pattern for dependency injection:

1. **Container Definition**: Declarative container with all module dependencies
2. **Wiring Function**: `wire_<module>_container()` - Wires the container to specific modules
3. **Configuration Function**: `configure_<module>_container()` - Receives and configures cross-module dependencies
4. **Orchestration**: Application container calls module wiring functions in correct order

This pattern ensures that:
- Module containers are self-contained and independently testable
- Cross-module dependencies are explicitly managed by the application container
- Wiring logic is distributed but coordinated
- Each module can evolve its internal DI setup without affecting other modules

## Architecture Details

Create a modular dependency injection system with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                APPLICATION CONTAINER                                    │
│                                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                      │
│  │   CORE          │    │ FILE PROCESSING │    │  EXCEL EXPORT   │                      │
│  │   CONTAINER     │    │   CONTAINER     │    │   CONTAINER     │                      │
│  │                 │    │                 │    │                 │                      │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │                      │
│  │ │RichOutput   │ │    │ │FileProcess  │ │    │ │ExcelExport  │ │                      │
│  │ │Service      │ │    │ │Service      │ │    │ │Service      │ │                      │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │                      │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │                      │
│  │ │Parallel     │ │    │ │Encoding     │ │    │ │Workbook     │ │                      │
│  │ │Processing   │ │    │ │Detector     │ │    │ │Engine       │ │                      │
│  │ │Service      │ │    │ │             │ │    │ │             │ │                      │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │                      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                      │
│             │                       │                       │                           │
│             └───────────────────────┼───────────────────────┼────────────────────────┐  │
│                                     │                       │                        │  │
└─────────────────────────────────────┼───────────────────────┼────────────────────────┼──┘
                                      │                       │                        │
              ┌───────────────────────┼───────────────────────┼────────────────────────┼─────┐
              │                       │                       │                        │     │
              │                       ▼                       ▼                        ▼     │
              │  ┌───────────────────────────────────────────────────────────────────────────┴┐
              │  │                     MODULE CONTAINERS                                   |  │
              │  │                                                                         |  │
              │  │ ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │  │
              │  │ │ PROCESS SCRIPTS  │  │ NIPPER EXPANDER  │  │   RTF TO TEXT    │        │  │
              │  │ │    CONTAINER     │  │    CONTAINER     │  │    CONTAINER     │        │  │
              │  │ │                  │  │                  │  │                  │        │  │
              │  │ │ ┌──────────────┐ │  │ ┌──────────────┐ │  │ ┌──────────────┐ │        │  │
              │  │ │ │ProcessScripts│ │  │ │NipperExpander│ │  │ │RtfToText     │ │        │  │
              │  │ │ │Service       │ │  │ │Service       │ │  │ │Service       │ │        │  │
              │  │ │ └──────────────┘ │  │ └──────────────┘ │  │ └──────────────┘ │        │  │
              │  │ │ ┌──────────────┐ │  │                  │  │ ┌──────────────┐ │        │  │
              │  │ │ │SearchEngine  │ │  │                  │  │ │RTFParser     │ │        │  │
              │  │ │ │Service       │ │  │                  │  │ │Service       │ │        │  │
              │  │ │ └──────────────┘ │  │                  │  │ └──────────────┘ │        │  │
              │  │ │ ┌──────────────┐ │  │                  │  │                  │        │  │
              │  │ │ │Enhanced      │ │  │                  │  │                  │        │  │
              │  │ │ │ExcelExport   │ │  │                  │  │                  │        │  │
              │  │ │ │Service       │ │  │                  │  │                  │        │  │
              │  │ │ └──────────────┘ │  │                  │  │                  │        │  │
              │  │ └──────────────────┘  └──────────────────┘  └──────────────────┘        │  │
              │  └─────────────────────────────────────────────────────────────────────────┘  │
              │                                                                               │
              └───────────────────────────────────────────────────────────────────────────────┘
```

```
                                         DEPENDENCY FLOW
                                            
                    CLI ──► Application Container ──► Core Containers ──► Module Containers
                     │                   │                    │                    │
                     │                   │                    │                    │
                     ▼                   ▼                    ▼                    ▼
                Configuration      Cross-Module          Shared Service      Module Service
                   Setup            Wiring              Instantiation        Instantiation
                     │                   │                    │                    │
                     │                   │                    │                    │
                     └───────────────────┴────────────────────┴────────────────────┘
                                                      │
                                                      ▼
                                             Ready for Execution
```

### 1. Core Containers

Containers providing core services used throughout the application, including:
* `ExcelExportService` for basic Excel output handling common to all modules
* `FileProcessingService` for file-related services common to all modules
* `ParallelProcessingService` for concurrency services which could be used by specific modules
* `RichOutput` for handling enhanced text display throughout the entire toolkit

#### Core Container (Shared Services)

```python
# src/kp_analysis_toolkit/core/containers/core.py
from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services import (
    ExcelExportService,
    FileProcessingService,
    ParallelProcessingService,
)
from kp_analysis_toolkit.utils.rich_output import RichOutput


class CoreContainer(containers.DeclarativeContainer):
    """Core services shared across all modules."""

    # Configuration
    config = providers.Configuration()

    # Core Services
    rich_output = providers.Singleton(
        RichOutput,
        verbose=config.verbose,
        quiet=config.quiet,
    )

    # Parallel Processing Services (global, available to all modules)
    executor_factory = providers.Factory(
        "kp_analysis_toolkit.core.parallel_engine.ProcessPoolExecutorFactory",
        max_workers=config.max_workers.provided,
    )
    
    progress_tracker = providers.Factory(
        "kp_analysis_toolkit.core.parallel_engine.ProgressTracker",
        rich_output=rich_output,
    )
    
    interrupt_handler = providers.Factory(
        "kp_analysis_toolkit.core.parallel_engine.InterruptHandler",
        rich_output=rich_output,
    )
    
    parallel_processing_service = providers.Factory(
        ParallelProcessingService,
        executor_factory=executor_factory,
        progress_tracker=progress_tracker,
        interrupt_handler=interrupt_handler,
        rich_output=rich_output,
    )
```

#### File Processing Container

```python
# src/kp_analysis_toolkit/core/containers/file_processing.py
from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services.file_processing import FileProcessingService


class FileProcessingContainer(containers.DeclarativeContainer):
    """File processing and encoding services."""

    # Dependencies
    core = providers.DependenciesContainer()

    # File Processing Components
    encoding_detector = providers.Factory(
        "kp_analysis_toolkit.utils.get_file_encoding.ChardetEncodingDetector"
    )
    
    hash_generator = providers.Factory(
        "kp_analysis_toolkit.utils.shared_funcs.SHA256HashGenerator"
    )
    
    file_validator = providers.Factory(
        "kp_analysis_toolkit.utils.shared_funcs.PathLibFileValidator"
    )
    
    # Main Service
    file_processing_service = providers.Factory(
        FileProcessingService,
        encoding_detector=encoding_detector,
        hash_generator=hash_generator,
        file_validator=file_validator,
        rich_output=core.rich_output,
    )
```

#### Excel Export Container

```python
# src/kp_analysis_toolkit/core/containers/excel_export.py
from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services.excel_export import ExcelExportService


class ExcelExportContainer(containers.DeclarativeContainer):
    """Excel export and formatting services."""

    # Dependencies
    core = providers.DependenciesContainer()

    # Excel Components
    workbook_engine = providers.Factory(
        "kp_analysis_toolkit.utils.excel_utils.OpenpyxlEngine"
    )
    
    excel_formatter = providers.Factory(
        "kp_analysis_toolkit.utils.excel_utils.StandardExcelFormatter"
    )
    
    table_generator = providers.Factory(
        "kp_analysis_toolkit.utils.excel_utils.StandardTableGenerator"
    )
    
    # Main Service
    excel_export_service = providers.Factory(
        ExcelExportService,
        workbook_engine=workbook_engine,
        formatter=excel_formatter,
        table_generator=table_generator,
        rich_output=core.rich_output,
    )
```

### 2. Module-Specific Containers

Containers to implement for specific modules

#### Process Scripts Containers

Process Scripts-specific services include:
* SystemDetectionService to identify the operating system, producer and other key details about discovered collection script result files
* SearchConfigService to process search configurations as defined in the module
* SearchEngineService to conduct searches on collection script result files
* EnhancedExcelExportService to extend the `core` ExcelExportService' capabilities with additional functionality required by `process_scripts`

```python
# src/kp_analysis_toolkit/process_scripts/container.py
from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services import (
    SearchEngineService,
)
from kp_analysis_toolkit.process_scripts.services.search_config import SearchConfigService
from kp_analysis_toolkit.process_scripts.services.system_detection import SystemDetectionService


class ProcessScriptsContainer(containers.DeclarativeContainer):
    """Services specific to the process scripts module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()
    excel_export = providers.DependenciesContainer()

    # Search Configuration Services (process_scripts specific)
    yaml_parser = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.search_config.PyYamlParser"
    )
    
    file_resolver = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.search_config.StandardFileResolver"
    )
    
    include_processor = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.search_config.StandardIncludeProcessor",
        yaml_parser=yaml_parser,
        file_resolver=file_resolver,
    )
    
    search_config_service = providers.Factory(
        SearchConfigService,
        yaml_parser=yaml_parser,
        file_resolver=file_resolver,
        include_processor=include_processor,
        rich_output=core.rich_output,
    )

    # System Detection Services (process_scripts specific)
    os_detector = providers.Factory(
        "kp_analysis_toolkit.process_scripts.utils.os_detection.RegexOSDetector"
    )
    
    producer_detector = providers.Factory(
        "kp_analysis_toolkit.process_scripts.utils.producer_detection.SignatureProducerDetector"
    )
    
    distro_classifier = providers.Factory(
        "kp_analysis_toolkit.process_scripts.utils.distro_classification.PatternDistroClassifier"
    )
    
    system_detection_service = providers.Factory(
        SystemDetectionService,
        os_detector=os_detector,
        producer_detector=producer_detector,
        distro_classifier=distro_classifier,
        rich_output=core.rich_output,
    )

    # Search Engine Services (process_scripts specific)
    pattern_compiler = providers.Factory(
        "kp_analysis_toolkit.process_scripts.search_engine_core.RegexPatternCompiler"
    )
    
    field_extractor = providers.Factory(
        "kp_analysis_toolkit.process_scripts.search_engine_core.StandardFieldExtractor"
    )
    
    result_processor = providers.Factory(
        "kp_analysis_toolkit.process_scripts.search_engine_core.StandardResultProcessor"
    )
    
    search_engine_service = providers.Factory(
        SearchEngineService,
        pattern_compiler=pattern_compiler,
        field_extractor=field_extractor,
        result_processor=result_processor,
        rich_output=core.rich_output,
    )

    # Enhanced Excel Export Services (process_scripts specific)
    advanced_worksheet_builder = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.AdvancedWorksheetBuilder",
        base_workbook_engine=excel_export.workbook_engine,
        rich_output=core.rich_output,
    )
    
    multi_sheet_formatter = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.MultiSheetFormatter",
        base_formatter=excel_export.excel_formatter,
    )
    
    conditional_formatting_engine = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.ConditionalFormattingEngine"
    )
    
    data_validation_engine = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.DataValidationEngine"
    )
    
    enhanced_excel_export_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.EnhancedExcelExportService",
        base_excel_service=excel_export.excel_export_service,
        worksheet_builder=advanced_worksheet_builder,
        multi_sheet_formatter=multi_sheet_formatter,
        conditional_formatter=conditional_formatting_engine,
        data_validator=data_validation_engine,
        rich_output=core.rich_output,
    )

    # Main Module Service
    process_scripts_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.service.ProcessScriptsService",
        search_engine=search_engine_service,
        parallel_processing=core.parallel_processing_service,
        system_detection=system_detection_service,
        excel_export=enhanced_excel_export_service,  # Use enhanced service instead of base
        file_processing=file_processing.file_processing_service,
        search_config=search_config_service,
        rich_output=core.rich_output,
    )
```

#### Nipper Expander Containers

Nipper Expander provides the following capabilities:


```python
# src/kp_analysis_toolkit/nipper_expander/container.py
from __future__ import annotations

from dependency_injector import containers, providers


class NipperExpanderContainer(containers.DeclarativeContainer):
    """Services specific to the nipper expander module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()
    excel_export = providers.DependenciesContainer()

    # Module-specific services would go here
    # (Currently nipper expander only uses shared services)

    # Main Module Service
    nipper_expander_service = providers.Factory(
        "kp_analysis_toolkit.nipper_expander.service.NipperExpanderService",
        excel_export=excel_export.excel_export_service,
        file_processing=file_processing.file_processing_service,
        rich_output=core.rich_output,
    )
```

#### RTF to Text Containers



```python
# src/kp_analysis_toolkit/rtf_to_text/container.py
from __future__ import annotations

from dependency_injector import containers, providers


class RtfToTextContainer(containers.DeclarativeContainer):
    """Services specific to the RTF to text module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()

    # Module-specific services would go here
    # (Currently RTF to text only uses shared services)

    # Main Module Service
    rtf_to_text_service = providers.Factory(
        "kp_analysis_toolkit.rtf_to_text.service.RtfToTextService",
        file_processing=file_processing.file_processing_service,
        rich_output=core.rich_output,
    )
```

### Module-Level Wiring Functions (Distributed Wiring)

Each module is responsible for wiring its own dependencies. These functions ensure that module containers are properly wired for dependency injection when the module is used.

```
                                        WIRING STRATEGY
                                            
              ┌────────────────────────────────────────────────────────────────────────────────┐
              │                          DISTRIBUTED WIRING                                    │
              │                                                                                │
              │  Application Container      │  Module Containers    │  Core Containers         │
              │  ─────────────────────      │  ─────────────────    │  ───────────────         │
              │                             │                       │                          │
              │  • Orchestrates modules     │  • Wire own services  │  • Wire shared services  │
              │  • Manages cross-module     │  • Internal DI setup  │  • Provide protocols     │
              │    dependencies             │  • Module-specific    │  • Singleton management  │
              │  • Calls module wiring      │    implementations    │  • Configuration mgmt    │
              │    functions                │  • Self-contained     │                          │
              │                             │    testing            │                          │
              └────────────────────────────────────────────────────────────────────────────────┘
```

#### Process Scripts Module Wiring

```python
# src/kp_analysis_toolkit/process_scripts/container.py (additional wiring function)

# Global container instance
container = ProcessScriptsContainer()


def wire_process_scripts_container() -> None:
    """Wire the process scripts container for dependency injection.
    
    This function should be called when the process scripts module is initialized
    to ensure all dependencies are properly wired for injection.
    """
    container.wire(modules=[
        "kp_analysis_toolkit.process_scripts.cli",
        "kp_analysis_toolkit.process_scripts.service",
        "kp_analysis_toolkit.process_scripts.cli_functions",
        "kp_analysis_toolkit.process_scripts.process_systems",
        "kp_analysis_toolkit.process_scripts.search_engine",
        "kp_analysis_toolkit.process_scripts.excel_exporter",
    ])


def configure_process_scripts_container(
    core_container: CoreContainer,
    file_processing_container: FileProcessingContainer,
    excel_export_container: ExcelExportContainer,
) -> None:
    """Configure the process scripts container with its dependencies.
    
    Args:
        core_container: The core services container
        file_processing_container: The file processing container
        excel_export_container: The excel export container
    """
    container.core.override(core_container)
    container.file_processing.override(file_processing_container)
    container.excel_export.override(excel_export_container)
```

#### Nipper Expander Module Wiring

```python
# src/kp_analysis_toolkit/nipper_expander/container.py (additional wiring function)

# Global container instance  
container = NipperExpanderContainer()


def wire_nipper_expander_container() -> None:
    """Wire the nipper expander container for dependency injection.
    
    This function should be called when the nipper expander module is initialized
    to ensure all dependencies are properly wired for injection.
    """
    container.wire(modules=[
        "kp_analysis_toolkit.nipper_expander.cli",
        "kp_analysis_toolkit.nipper_expander.service",
        "kp_analysis_toolkit.nipper_expander.process_nipper",
    ])


def configure_nipper_expander_container(
    core_container: CoreContainer,
    file_processing_container: FileProcessingContainer,
    excel_export_container: ExcelExportContainer,
) -> None:
    """Configure the nipper expander container with its dependencies.
    
    Args:
        core_container: The core services container
        file_processing_container: The file processing container
        excel_export_container: The excel export container
    """
    container.core.override(core_container)
    container.file_processing.override(file_processing_container)
    container.excel_export.override(excel_export_container)
```

#### RTF to Text Module Wiring

```python
# src/kp_analysis_toolkit/rtf_to_text/container.py (additional wiring function)

# Global container instance
container = RtfToTextContainer()


def wire_rtf_to_text_container() -> None:
    """Wire the RTF to text container for dependency injection.
    
    This function should be called when the RTF to text module is initialized
    to ensure all dependencies are properly wired for injection.
    """
    container.wire(modules=[
        "kp_analysis_toolkit.rtf_to_text.cli",
        "kp_analysis_toolkit.rtf_to_text.service", 
        "kp_analysis_toolkit.rtf_to_text.process_rtf",
    ])


def configure_rtf_to_text_container(
    core_container: CoreContainer,
    file_processing_container: FileProcessingContainer,
) -> None:
    """Configure the RTF to text container with its dependencies.
    
    Args:
        core_container: The core services container
        file_processing_container: The file processing container
    """
    container.core.override(core_container)
    container.file_processing.override(file_processing_container)
```

#### Main Application Container

```python
# src/kp_analysis_toolkit/core/containers/application.py
from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.containers.core import CoreContainer
from kp_analysis_toolkit.core.containers.excel_export import ExcelExportContainer
from kp_analysis_toolkit.core.containers.file_processing import FileProcessingContainer
from kp_analysis_toolkit.process_scripts.container import ProcessScriptsContainer
from kp_analysis_toolkit.nipper_expander.container import NipperExpanderContainer
from kp_analysis_toolkit.rtf_to_text.container import RtfToTextContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container that wires all module containers together."""

    # Core containers
    core = providers.Container(CoreContainer)
    
    file_processing = providers.Container(
        FileProcessingContainer,
        core=core
    )
    
    excel_export = providers.Container(
        ExcelExportContainer,
        core=core
    )

    # Module containers
    process_scripts = providers.Container(
        ProcessScriptsContainer,
        core=core,
        file_processing=file_processing,
        excel_export=excel_export,
    )
    
    nipper_expander = providers.Container(
        NipperExpanderContainer,
        core=core,
        file_processing=file_processing,
        excel_export=excel_export,
    )
    
    rtf_to_text = providers.Container(
        RtfToTextContainer,
        core=core,
        file_processing=file_processing,
    )


# Global container instance
container = ApplicationContainer()


def wire_application_container() -> None:
    """Wire the main application container and all module containers.
    
    This function orchestrates the wiring of all containers in the application.
    It ensures that the core containers are wired first, followed by module containers.
    """
    # Wire the main application container for CLI integration
    container.wire(modules=[
        "kp_analysis_toolkit.cli",
    ])


def wire_module_containers() -> None:
    """Wire all module containers using their respective wiring functions.
    
    This function coordinates the wiring of individual module containers,
    demonstrating Distributed Wiring where each module is responsible
    for its own dependency wiring.
    """
    from kp_analysis_toolkit.process_scripts.container import (
        wire_process_scripts_container,
        configure_process_scripts_container,
    )
    from kp_analysis_toolkit.nipper_expander.container import (
        wire_nipper_expander_container,
        configure_nipper_expander_container,
    )
    from kp_analysis_toolkit.rtf_to_text.container import (
        wire_rtf_to_text_container,
        configure_rtf_to_text_container,
    )

    # Configure module containers with their dependencies
    configure_process_scripts_container(
        core_container=container.core(),
        file_processing_container=container.file_processing(),
        excel_export_container=container.excel_export(),
    )
    
    configure_nipper_expander_container(
        core_container=container.core(),
        file_processing_container=container.file_processing(),
        excel_export_container=container.excel_export(),
    )
    
    configure_rtf_to_text_container(
        core_container=container.core(),
        file_processing_container=container.file_processing(),
    )

    # Wire each module container
    wire_process_scripts_container()
    wire_nipper_expander_container()
    wire_rtf_to_text_container()


def configure_application_container(
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """Configure the application container with runtime settings.
    
    Args:
        verbose: Enable verbose output
        quiet: Enable quiet mode
        max_workers: Maximum number of worker processes
    """
    container.core().config.verbose.from_value(verbose)
    container.core().config.quiet.from_value(quiet)
    container.core().config.max_workers.from_value(max_workers or 4)


def initialize_dependency_injection(
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """Initialize the complete dependency injection system.
    
    This is the main entry point for setting up DI throughout the application.
    It configures and wires all containers in the correct order.
    
    Args:
        verbose: Enable verbose output
        quiet: Enable quiet mode
        max_workers: Maximum number of worker processes
    """
    # 1. Configure the application container
    configure_application_container(verbose, quiet, max_workers)
    
    # 2. Wire the application container
    wire_application_container()
    
    # 3. Wire all module containers  
    wire_module_containers()
```

### 3. Service Interfaces and Implementations

Define clean service interfaces for all major components:

#### Core Services

##### Moodule Initialization

```python
# src/kp_analysis_toolkit/core/services/__init__.py
from __future__ import annotations

from kp_analysis_toolkit.core.services.excel_export import ExcelExportService
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.parallel_processing import ParallelProcessingService
from kp_analysis_toolkit.core.services.search_engine import SearchEngineService

__all__ = [
    "ExcelExportService", 
    "FileProcessingService",
    "ParallelProcessingService",
    "SearchEngineService",
]
```

##### File Processing Service

```python
# src/kp_analysis_toolkit/core/services/file_processing.py
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from kp_analysis_toolkit.utils.rich_output import RichOutput


class EncodingDetector(Protocol):
    """Protocol for file encoding detection."""
    
    def detect_encoding(self, file_path: Path) -> str | None: ...


class HashGenerator(Protocol):
    """Protocol for file hash generation."""
    
    def generate_hash(self, file_path: Path) -> str: ...


class FileValidator(Protocol):
    """Protocol for file validation."""
    
    def validate_file_exists(self, file_path: Path) -> bool: ...
    def validate_directory_exists(self, dir_path: Path) -> bool: ...


class FileProcessingService:
    """Service for all file processing operations."""
    
    def __init__(
        self,
        encoding_detector: EncodingDetector,
        hash_generator: HashGenerator,
        file_validator: FileValidator,
        rich_output: RichOutput,
    ) -> None:
        self.encoding_detector = encoding_detector
        self.hash_generator = hash_generator
        self.file_validator = file_validator
        self.rich_output = rich_output
    
    def process_file(self, file_path: Path) -> dict[str, str | None]:
        """Process a file and return metadata."""
        if not self.file_validator.validate_file_exists(file_path):
            self.rich_output.error(f"File not found: {file_path}")
            return {}
        
        encoding = self.encoding_detector.detect_encoding(file_path)
        if encoding is None:
            self.rich_output.warning(f"Could not detect encoding for: {file_path}")
            return {}
        
        file_hash = self.hash_generator.generate_hash(file_path)
        
        return {
            "encoding": encoding,
            "hash": file_hash,
            "path": str(file_path),
        }
```

##### Excel Exporter Service

```python
# src/kp_analysis_toolkit/core/services/excel_export.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import pandas as pd

from kp_analysis_toolkit.utils.rich_output import RichOutput


class WorkbookEngine(Protocol):
    """Protocol for Excel workbook engines."""
    
    def create_writer(self, output_path: Path) -> Any: ...


class ExcelFormatter(Protocol):
    """Protocol for Excel formatting."""
    
    def format_worksheet(self, worksheet: Any, data: pd.DataFrame) -> None: ...


class TableGenerator(Protocol):
    """Protocol for Excel table generation."""
    
    def create_table(self, worksheet: Any, data: pd.DataFrame) -> None: ...


class ExcelExportService:
    """Service for Excel export operations."""
    
    def __init__(
        self,
        workbook_engine: WorkbookEngine,
        formatter: ExcelFormatter,
        table_generator: TableGenerator,
        rich_output: RichOutput,
    ) -> None:
        self.workbook_engine = workbook_engine
        self.formatter = formatter
        self.table_generator = table_generator
        self.rich_output = rich_output
    
    def export_dataframe(
        self,
        data: pd.DataFrame,
        output_path: Path,
        sheet_name: str = "Sheet1",
    ) -> None:
        """Export DataFrame to Excel with formatting."""
        try:
            with self.workbook_engine.create_writer(output_path) as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                worksheet = writer.sheets[sheet_name]
                self.formatter.format_worksheet(worksheet, data)
                self.table_generator.create_table(worksheet, data)
            
            self.rich_output.success(f"Exported data to {output_path}")
        except Exception as e:
            self.rich_output.error(f"Failed to export Excel file: {e}")
            raise
```

##### Parallel Processing Service

```python
# src/kp_analysis_toolkit/core/services/parallel_processing.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from kp_analysis_toolkit.process_scripts.models.results.base import SearchResults
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.utils.rich_output import RichOutput


class ExecutorFactory(Protocol):
    """Protocol for executor factory."""
    
    def create_executor(self, max_workers: int) -> Any: ...


class ProgressTracker(Protocol):
    """Protocol for progress tracking."""
    
    def track_progress(self, total: int, description: str) -> Any: ...


class InterruptHandler(Protocol):
    """Protocol for interrupt handling."""
    
    def setup(self) -> None: ...
    def cleanup(self) -> None: ...
    def is_interrupted(self) -> bool: ...


class ParallelProcessingService:
    """Service for parallel processing operations."""
    
    def __init__(
        self,
        executor_factory: ExecutorFactory,
        progress_tracker: ProgressTracker,
        interrupt_handler: InterruptHandler,
        rich_output: RichOutput,
    ) -> None:
        self.executor_factory = executor_factory
        self.progress_tracker = progress_tracker
        self.interrupt_handler = interrupt_handler
        self.rich_output = rich_output
    
    def search_configs_with_processes(
        self,
        search_configs: list[SearchConfig],
        systems: list[Systems],
        max_workers: int,
    ) -> list[SearchResults]:
        """Execute multiple search configurations in parallel using processes."""
        if not search_configs:
            return []

        # Engine now uses injected RichOutput instead of global singleton
        # Calculate the maximum width needed for search config names
        max_name_width = max(
            len(getattr(config, "name", "Unknown")) for config in search_configs
        )

        results: list[SearchResults] = []
        
        # Set up interrupt handling with injected RichOutput
        self.interrupt_handler.setup()

        try:
            with self.rich_output.progress(
                show_eta=True,
                show_percentage=True,
                show_time_elapsed=True,
            ) as progress:
                # Implementation details for parallel processing...
                pass
                
        finally:
            self.interrupt_handler.cleanup()

        return results
```

#### Module-Specific Services

##### Process Scripts Services
##### Search Engine Service

```python
# src/kp_analysis_toolkit/process_scripts/services/search_engine.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from kp_analysis_toolkit.process_scripts.models.results.base import SearchResults
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.utils.rich_output import RichOutput


class PatternCompiler(Protocol):
    """Protocol for regex pattern compilation."""
    
    def compile_pattern(self, pattern: str) -> Any: ...
    def validate_pattern(self, pattern: str) -> bool: ...


class FieldExtractor(Protocol):
    """Protocol for field extraction from search results."""
    
    def extract_fields(self, line: str, config: SearchConfig) -> dict[str, str]: ...


class ResultProcessor(Protocol):
    """Protocol for processing search results."""
    
    def process_results(self, raw_results: list[dict[str, str]], config: SearchConfig) -> SearchResults: ...


class SearchEngineService:
    """Service for search engine operations."""
    
    def __init__(
        self,
        pattern_compiler: PatternCompiler,
        field_extractor: FieldExtractor,
        result_processor: ResultProcessor,
        rich_output: RichOutput,
    ) -> None:
        self.pattern_compiler = pattern_compiler
        self.field_extractor = field_extractor
        self.result_processor = result_processor
        self.rich_output = rich_output
    
    def search_file(
        self,
        file_path: Path,
        search_config: SearchConfig,
    ) -> SearchResults:
        """Search a file using the provided configuration."""
        # Implementation would handle file searching with pattern matching
        # and field extraction using injected dependencies
        pass
```

##### Search Configuration Service

```python
# src/kp_analysis_toolkit/process_scripts/services/search_config.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.utils.rich_output import RichOutput


class YamlParser(Protocol):
    """Protocol for YAML parsing operations."""
    
    def load_yaml(self, file_path: Path) -> dict[str, Any]: ...
    def validate_yaml_structure(self, data: dict[str, Any]) -> bool: ...


class FileResolver(Protocol):
    """Protocol for resolving file paths and includes."""
    
    def resolve_path(self, base_path: Path, relative_path: str) -> Path: ...
    def find_include_files(self, config_dir: Path, pattern: str) -> list[Path]: ...


class IncludeProcessor(Protocol):
    """Protocol for processing YAML includes."""
    
    def process_includes(self, config_data: dict[str, Any], base_path: Path) -> dict[str, Any]: ...


class SearchConfigService:
    """Service for loading and processing YAML search configurations."""
    
    def __init__(
        self,
        yaml_parser: YamlParser,
        file_resolver: FileResolver,
        include_processor: IncludeProcessor,
        rich_output: RichOutput,
    ) -> None:
        self.yaml_parser = yaml_parser
        self.file_resolver = file_resolver
        self.include_processor = include_processor
        self.rich_output = rich_output
    
    def load_search_configs(self, config_path: Path) -> list[SearchConfig]:
        """Load search configurations from YAML files with include processing."""
        try:
            # Load main configuration file
            config_data = self.yaml_parser.load_yaml(config_path)
            
            # Process any includes
            processed_data = self.include_processor.process_includes(
                config_data, 
                config_path.parent
            )
            
            # Convert to SearchConfig models
            configs = self._convert_to_search_configs(processed_data)
            
            self.rich_output.info(f"Loaded {len(configs)} search configurations")
            return configs
            
        except Exception as e:
            self.rich_output.error(f"Failed to load search configurations: {e}")
            raise
    
    def _convert_to_search_configs(self, data: dict[str, Any]) -> list[SearchConfig]:
        """Convert YAML data to SearchConfig models."""
        # Implementation would convert YAML data to Pydantic models
        pass
```

##### System Detection Service

```python
# src/kp_analysis_toolkit/process_scripts/services/system_detection.py
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.utils.rich_output import RichOutput


class OSDetector(Protocol):
    """Protocol for operating system detection."""
    
    def detect_os(self, file_content: str) -> str | None: ...
    def get_supported_os_types(self) -> list[str]: ...


class ProducerDetector(Protocol):
    """Protocol for detecting system/software producers."""
    
    def detect_producer(self, file_content: str, file_path: Path) -> str | None: ...
    def get_known_producers(self) -> list[str]: ...


class DistroClassifier(Protocol):
    """Protocol for Linux distribution classification."""
    
    def classify_distribution(self, os_info: str, file_content: str) -> str | None: ...
    def get_supported_distributions(self) -> list[str]: ...


class SystemDetectionService:
    """Service for detecting system information from configuration files."""
    
    def __init__(
        self,
        os_detector: OSDetector,
        producer_detector: ProducerDetector,
        distro_classifier: DistroClassifier,
        rich_output: RichOutput,
    ) -> None:
        self.os_detector = os_detector
        self.producer_detector = producer_detector
        self.distro_classifier = distro_classifier
        self.rich_output = rich_output
    
    def analyze_system_file(self, file_path: Path, file_content: str) -> Systems:
        """Analyze a system file and extract system information."""
        try:
            # Detect operating system
            detected_os = self.os_detector.detect_os(file_content)
            if detected_os is None:
                self.rich_output.warning(f"Could not detect OS for: {file_path}")
                detected_os = "Unknown"
            
            # Detect producer/vendor
            producer = self.producer_detector.detect_producer(file_content, file_path)
            if producer is None:
                self.rich_output.warning(f"Could not detect producer for: {file_path}")
                producer = "Unknown"
            
            # Classify distribution (for Linux systems)
            distribution = None
            if detected_os.lower() == "linux":
                distribution = self.distro_classifier.classify_distribution(
                    detected_os, 
                    file_content
                )
            
            return Systems(
                file_path=str(file_path),
                operating_system=detected_os,
                producer=producer,
                distribution=distribution,
                file_hash=None,  # Would be populated by file processing service
            )
            
        except Exception as e:
            self.rich_output.error(f"Failed to analyze system file {file_path}: {e}")
            raise
```

###### Mai#n Process Scripts Service

```python
# src/kp_analysis_toolkit/process_scripts/service.py
from __future__ import annotations

from pathlib import Path
from typing import Any

from kp_analysis_toolkit.core.services.excel_export import ExcelExportService
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.parallel_processing import ParallelProcessingService
from kp_analysis_toolkit.process_scripts.services.search_engine import SearchEngineService
from kp_analysis_toolkit.process_scripts.services.search_config import SearchConfigService
from kp_analysis_toolkit.process_scripts.services.system_detection import SystemDetectionService
from kp_analysis_toolkit.process_scripts.services.excel_export import EnhancedExcelExportService
from kp_analysis_toolkit.utils.rich_output import RichOutput


class ProcessScriptsService:
    """Main service for the process scripts module."""
    
    def __init__(
        self,
        search_engine: SearchEngineService,
        parallel_processing: ParallelProcessingService,
        system_detection: SystemDetectionService,
        excel_export: EnhancedExcelExportService,  # Use enhanced service
        file_processing: FileProcessingService,
        search_config: SearchConfigService,
        rich_output: RichOutput,
    ) -> None:
        self.search_engine = search_engine
        self.parallel_processing = parallel_processing
        self.system_detection = system_detection
        self.excel_export = excel_export
        self.file_processing = file_processing
        self.search_config = search_config
        self.rich_output = rich_output
    
    def execute(
        self,
        input_directory: Path,
        config_file: Path,
        output_path: Path,
        max_workers: int = 4,
    ) -> None:
        """Execute the complete process scripts workflow."""
        try:
            self.rich_output.header("Starting Process Scripts Analysis")
            
            # Load search configurations
            search_configs = self.search_config.load_search_configs(config_file)
            
            # Discover and analyze system files
            system_files = self._discover_system_files(input_directory)
            systems = self._analyze_systems(system_files)
            
            # Execute search configurations in parallel
            search_results = self.parallel_processing.search_configs_with_processes(
                search_configs,
                systems,
                max_workers,
            )
            
            # Export results to Excel
            self._export_results(search_results, output_path)
            
            self.rich_output.success("Process Scripts analysis completed successfully")
            
        except Exception as e:
            self.rich_output.error(f"Process Scripts execution failed: {e}")
            raise
    
    def _discover_system_files(self, directory: Path) -> list[Path]:
        """Discover system configuration files in the input directory."""
        # Implementation would scan directory for supported file types
        pass
    
    def _analyze_systems(self, file_paths: list[Path]) -> list[Any]:
        """Analyze system files to extract system information."""
        # Implementation would process files using system detection service
        pass
    
    def _export_results(self, results: list[Any], output_path: Path) -> None:
        """Export search results to Excel format using enhanced capabilities."""
        try:
            # Use enhanced Excel export service with process scripts specific features
            self.excel_export.export_search_results(
                search_results=results,
                output_path=output_path,
                include_summary=True,  # Create summary sheet
                apply_formatting=True,  # Apply conditional formatting
            )
            
            # Also create a simplified version for quick review
            simplified_path = output_path.with_name(f"simplified_{output_path.name}")
            self.excel_export.base_excel_service.export_dataframe(
                data=self._create_simplified_dataframe(results),
                output_path=simplified_path,
                sheet_name="Quick View"
            )
            
        except Exception as e:
            self.rich_output.error(f"Failed to export results: {e}")
            raise
    
    def _create_simplified_dataframe(self, results: list[Any]) -> Any:
        """Create a simplified DataFrame for quick review."""
        # Implementation would create a condensed view of the results
        pass
```

##### RTF to Text Services

###### RTF Parser Service

```python
# src/kp_analysis_toolkit/rtf_to_text/services/rtf_parser.py
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from kp_analysis_toolkit.utils.rich_output import RichOutput


class RTFDecoder(Protocol):
    """Protocol for RTF decoding operations."""
    
    def decode_rtf(self, rtf_content: bytes) -> str: ...
    def validate_rtf_format(self, file_path: Path) -> bool: ...


class TextCleaner(Protocol):
    """Protocol for text cleaning operations."""
    
    def clean_text(self, raw_text: str) -> str: ...
    def remove_control_characters(self, text: str) -> str: ...


class EncodingConverter(Protocol):
    """Protocol for encoding conversion."""
    
    def convert_encoding(self, text: str, target_encoding: str) -> str: ...
    def detect_text_encoding(self, text: str) -> str: ...


class RTFParserService:
    """Service for parsing RTF files and converting to text."""
    
    def __init__(
        self,
        rtf_decoder: RTFDecoder,
        text_cleaner: TextCleaner,
        encoding_converter: EncodingConverter,
        rich_output: RichOutput,
    ) -> None:
        self.rtf_decoder = rtf_decoder
        self.text_cleaner = text_cleaner
        self.encoding_converter = encoding_converter
        self.rich_output = rich_output
    
    def convert_rtf_to_text(
        self,
        rtf_file_path: Path,
        output_encoding: str = "utf-8",
    ) -> str:
        """Convert RTF file to clean text format."""
        try:
            # Validate RTF format
            if not self.rtf_decoder.validate_rtf_format(rtf_file_path):
                raise ValueError(f"Invalid RTF format: {rtf_file_path}")
            
            # Read and decode RTF content
            with open(rtf_file_path, 'rb') as f:
                rtf_content = f.read()
            
            raw_text = self.rtf_decoder.decode_rtf(rtf_content)
            
            # Clean the extracted text
            cleaned_text = self.text_cleaner.clean_text(raw_text)
            
            # Convert encoding if needed
            final_text = self.encoding_converter.convert_encoding(
                cleaned_text, 
                output_encoding
            )
            
            self.rich_output.success(f"Successfully converted RTF: {rtf_file_path}")
            return final_text
            
        except Exception as e:
            self.rich_output.error(f"Failed to convert RTF file {rtf_file_path}: {e}")
            raise
```

###### Main RTF to Text Service

```python
# src/kp_analysis_toolkit/rtf_to_text/service.py
from __future__ import annotations

from pathlib import Path

from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.rtf_to_text.services.rtf_parser import RTFParserService
from kp_analysis_toolkit.utils.rich_output import RichOutput


class RtfToTextService:
    """Main service for the RTF to text module."""
    
    def __init__(
        self,
        rtf_parser: RTFParserService,
        file_processing: FileProcessingService,
        rich_output: RichOutput,
    ) -> None:
        self.rtf_parser = rtf_parser
        self.file_processing = file_processing
        self.rich_output = rich_output
    
    def execute(
        self,
        input_path: Path,
        output_directory: Path,
        preserve_structure: bool = True,
    ) -> None:
        """Execute RTF to text conversion workflow."""
        try:
            self.rich_output.header("Starting RTF to Text Conversion")
            
            # Discover RTF files
            rtf_files = self._discover_rtf_files(input_path)
            
            if not rtf_files:
                self.rich_output.warning("No RTF files found")
                return
            
            # Process each RTF file
            for rtf_file in rtf_files:
                self._convert_single_file(
                    rtf_file, 
                    output_directory, 
                    preserve_structure
                )
            
            self.rich_output.success(
                f"Successfully converted {len(rtf_files)} RTF files"
            )
            
        except Exception as e:
            self.rich_output.error(f"RTF to Text conversion failed: {e}")
            raise
    
    def _discover_rtf_files(self, path: Path) -> list[Path]:
        """Discover RTF files in the input path."""
        if path.is_file() and path.suffix.lower() == '.rtf':
            return [path]
        elif path.is_dir():
            return list(path.rglob('*.rtf'))
        else:
            return []
    
    def _convert_single_file(
        self,
        rtf_file: Path,
        output_directory: Path,
        preserve_structure: bool,
    ) -> None:
        """Convert a single RTF file to text."""
        try:
            # Convert RTF to text
            text_content = self.rtf_parser.convert_rtf_to_text(rtf_file)
            
            # Determine output path
            output_path = self._determine_output_path(
                rtf_file, 
                output_directory, 
                preserve_structure
            )
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write text file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            self.rich_output.info(f"Converted: {rtf_file} -> {output_path}")
            
        except Exception as e:
            self.rich_output.error(f"Failed to convert {rtf_file}: {e}")
            raise
    
    def _determine_output_path(
        self,
        rtf_file: Path,
        output_directory: Path,
        preserve_structure: bool,
    ) -> Path:
        """Determine the output path for the converted text file."""
        if preserve_structure:
            # Maintain directory structure
            relative_path = rtf_file.relative_to(rtf_file.anchor)
            output_path = output_directory / relative_path
        else:
            # Flat structure
            output_path = output_directory / rtf_file.name
        
        # Change extension to .txt
        return output_path.with_suffix('.txt')
```

##### Nipper Expander Services

###### CSV Processing Service

```python
# src/kp_analysis_toolkit/nipper_expander/services/csv_processor.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import pandas as pd

from kp_analysis_toolkit.utils.rich_output import RichOutput


class CSVReader(Protocol):
    """Protocol for CSV reading operations."""
    
    def read_csv(self, file_path: Path, **kwargs: Any) -> pd.DataFrame: ...
    def validate_csv_structure(self, df: pd.DataFrame) -> bool: ...


class DataExpander(Protocol):
    """Protocol for data expansion operations."""
    
    def expand_ranges(self, df: pd.DataFrame, range_columns: list[str]) -> pd.DataFrame: ...
    def expand_lists(self, df: pd.DataFrame, list_columns: list[str]) -> pd.DataFrame: ...


class DataValidator(Protocol):
    """Protocol for data validation."""
    
    def validate_required_columns(self, df: pd.DataFrame, required_columns: list[str]) -> bool: ...
    def validate_data_types(self, df: pd.DataFrame, column_types: dict[str, type]) -> bool: ...


class CSVProcessorService:
    """Service for processing Nipper CSV files."""
    
    def __init__(
        self,
        csv_reader: CSVReader,
        data_expander: DataExpander,
        data_validator: DataValidator,
        rich_output: RichOutput,
    ) -> None:
        self.csv_reader = csv_reader
        self.data_expander = data_expander
        self.data_validator = data_validator
        self.rich_output = rich_output
    
    def process_nipper_csv(
        self,
        csv_file_path: Path,
        expand_ranges: bool = True,
        expand_lists: bool = True,
    ) -> pd.DataFrame:
        """Process Nipper CSV file with expansion options."""
        try:
            # Read CSV file
            df = self.csv_reader.read_csv(csv_file_path)
            
            # Validate basic structure
            if not self.csv_reader.validate_csv_structure(df):
                raise ValueError(f"Invalid CSV structure: {csv_file_path}")
            
            # Validate required columns for Nipper format
            required_columns = ['Source', 'Destination', 'Service', 'Action']
            if not self.data_validator.validate_required_columns(df, required_columns):
                raise ValueError(f"Missing required columns in: {csv_file_path}")
            
            # Expand ranges if requested
            if expand_ranges:
                range_columns = ['Source', 'Destination']
                df = self.data_expander.expand_ranges(df, range_columns)
            
            # Expand lists if requested
            if expand_lists:
                list_columns = ['Service']
                df = self.data_expander.expand_lists(df, list_columns)
            
            self.rich_output.success(f"Processed Nipper CSV: {csv_file_path}")
            return df
            
        except Exception as e:
            self.rich_output.error(f"Failed to process CSV {csv_file_path}: {e}")
            raise
```

###### Main Nipper Expander Service


```python
# src/kp_analysis_toolkit/nipper_expander/service.py
from __future__ import annotations

from pathlib import Path

from kp_analysis_toolkit.core.services.excel_export import ExcelExportService
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.nipper_expander.services.csv_processor import CSVProcessorService
from kp_analysis_toolkit.utils.rich_output import RichOutput


class NipperExpanderService:
    """Main service for the Nipper Expander module."""
    
    def __init__(
        self,
        csv_processor: CSVProcessorService,
        excel_export: ExcelExportService,
        file_processing: FileProcessingService,
        rich_output: RichOutput,
    ) -> None:
        self.csv_processor = csv_processor
        self.excel_export = excel_export
        self.file_processing = file_processing
        self.rich_output = rich_output
    
    def execute(
        self,
        input_path: Path,
        output_path: Path,
        expand_ranges: bool = True,
        expand_lists: bool = True,
    ) -> None:
        """Execute Nipper expansion workflow."""
        try:
            self.rich_output.header("Starting Nipper Expansion")
            
            # Discover CSV files
            csv_files = self._discover_csv_files(input_path)
            
            if not csv_files:
                self.rich_output.warning("No CSV files found")
                return
            
            # Process each CSV file
            all_expanded_data = []
            for csv_file in csv_files:
                expanded_data = self.csv_processor.process_nipper_csv(
                    csv_file,
                    expand_ranges=expand_ranges,
                    expand_lists=expand_lists,
                )
                all_expanded_data.append(expanded_data)
            
            # Combine all data if multiple files
            if len(all_expanded_data) > 1:
                import pandas as pd
                combined_data = pd.concat(all_expanded_data, ignore_index=True)
            else:
                combined_data = all_expanded_data[0]
            
            # Export to Excel
            self.excel_export.export_dataframe(
                combined_data,
                output_path,
                sheet_name="Expanded_Rules",
            )
            
            self.rich_output.success(
                f"Successfully expanded {len(csv_files)} CSV files to {output_path}"
            )
            
        except Exception as e:
            self.rich_output.error(f"Nipper Expansion failed: {e}")
            raise
    
    def _discover_csv_files(self, path: Path) -> list[Path]:
        """Discover CSV files in the input path."""
        if path.is_file() and path.suffix.lower() == '.csv':
            return [path]
        elif path.is_dir():
            return list(path.glob('*.csv'))
        else:
            return []
```

### 4. Wiring and Configuration (Distributed Wiring)

The application uses distributed wiring where each module is responsible for its own dependency injection setup. The application container orchestrates cross-module dependencies but does not directly wire individual module internals.

```python
# src/kp_analysis_toolkit/core/containers/__init__.py
from __future__ import annotations

from kp_analysis_toolkit.core.containers.application import (
    ApplicationContainer,
    initialize_dependency_injection,
    wire_application_container,
    wire_module_containers,
    configure_application_container,
)
from kp_analysis_toolkit.core.containers.core import CoreContainer

__all__ = [
    "ApplicationContainer", 
    "CoreContainer",
    "initialize_dependency_injection",
    "wire_application_container", 
    "wire_module_containers",
    "configure_application_container",
]
```

#### Application-Level Wiring Configuration

The application container provides orchestration functions that coordinate module wiring:

```python
# Example of how wiring is coordinated (from application.py above)

def initialize_dependency_injection(
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """Initialize the complete dependency injection system.
    
    This is the main entry point for setting up DI throughout the application.
    It configures and wires all containers in the correct order.
    """
    # 1. Configure the application container
    configure_application_container(verbose, quiet, max_workers)
    
    # 2. Wire the application container
    wire_application_container()
    
    # 3. Wire all module containers  
    wire_module_containers()
```

#### Module-Level Wiring Pattern

Each module follows the same wiring pattern for consistency:

```python
# Pattern followed by each module container (e.g., process_scripts/container.py)

# 1. Container definition with dependencies
class ModuleContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()
    # ... other dependencies and services

# 2. Global container instance
container = ModuleContainer()

# 3. Module wiring function
def wire_module_container() -> None:
    """Wire this module's container for dependency injection."""
    container.wire(modules=[
        "module.specific.modules",
    ])

# 4. Configuration function for cross-module dependencies
def configure_module_container(core_container, other_containers) -> None:
    """Configure this module's container with external dependencies."""
    container.core.override(core_container)
    # ... configure other dependencies
```

This pattern ensures that:
- Each module is self-contained and independently testable
- Cross-module dependencies are explicitly managed by the application container
- Module teams can modify their DI setup without affecting other modules
- The wiring logic is distributed but follows consistent patterns

#### Service Extension Pattern for Module-Specific Requirements

The distributed wiring architecture supports elegant extension of core services for module-specific requirements. To demonstrate, below we use this pattern to extend the `core` Excel export capabilities for use in `process_scripts` without modifying core services.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              Service Extension Example                              │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐         ┌───────────────────────────────────────────────┐
│       Core Layer        │         │              Process Scripts Layer            │
│                         │         │                                               │
│  ┌─────────────────┐    │         │  ┌─────────────────────────────────────────┐  │
│  │ ExcelExportSvc  │    │         │  │    EnhancedExcelExportService           │  │
│  │                 │    │         │  │                                         │  │
│  │ • basic_export()│◄───┼─────────┼──┤ • base_service: ExcelExportService      │  │
│  │ • format_sheet()│    │         │  │ • export_search_results()               │  │
│  │ • create_table()│    │         │  │ • export_comparison_report()            │  │
│  └─────────────────┘    │         │  │ • create_summary_data()                 │  │
│                         │         │  │ • apply_conditional_formatting()        │  │
│  ┌─────────────────┐    │         │  └─────────────────────────────────────────┘  │
│  │ WorkbookEngine  │    │         │                        ▲                      │
│  └─────────────────┘    │         │                        │                      │
│                         │         │                        │ Dependency           │
│  ┌─────────────────┐    │         │  ┌─────────────────────────────────────────┐  │
│  │ ExcelFormatter  │    │         │  │    AdvancedWorksheetBuilder             │  │
│  └─────────────────┘    │         │  │                                         │  │
│                         │         │  │ • create_summary_worksheet()            │  │
│  ┌─────────────────┐    │         │  │ • create_detailed_worksheet()           │  │
│  │ TableGenerator  │    │         │  │ • add_charts_and_graphs()               │  │
│  └─────────────────┘    │         │  └─────────────────────────────────────────┘  │
└─────────────────────────┘         │                                               │
                                    │  ┌─────────────────────────────────────────┐  │
    Used by ALL modules             │  │    ConditionalFormattingEngine          │  │
                                    │  │                                         │  │
                                    │  │ • apply_severity_formatting()           │  │
                                    │  │ • apply_status_formatting()             │  │
                                    │  │ • apply_threshold_highlighting()        │  │
                                    │  └─────────────────────────────────────────┘  │
                                    │                                               │
                                    │           Used ONLY by process_scripts        │
                                    └───────────────────────────────────────────────┘

                                    ┌─────────────────────────────────────┐
                                    │          Dependency Injection       │
                                    │                                     │
                                    │   enhanced_service = Factory(       │
                                    │     EnhancedExcelExportService,     │
                                    │     base_service=core.excel_export, │
                                    │     worksheet_builder=...,          │
                                    │     conditional_formatter=...       │
                                    │   )                                 │
                                    └─────────────────────────────────────┘
```


##### Extension Strategy

**✅ Core Service Provides Foundation:**
- `ExcelExportService` in core provides basic Excel functionality
- Uses protocols for extensibility points
- Handles common use cases for all modules

**✅ Module Service Extends Capabilities:**
- `EnhancedExcelExportService` in process_scripts adds specialized features
- Composes the base service rather than inheriting from it
- Adds process_scripts-specific functionality through dependency injection

**✅ Container Orchestration:**
- Process scripts container wires enhanced service with base service as dependency
- Other modules continue using base service directly
- No breaking changes to core architecture

##### Key Benefits

1. **Separation of Concerns**: Core services remain focused on common functionality
2. **Module Independence**: Each module can extend services without affecting others  
3. **Composition over Inheritance**: Uses dependency injection for flexible service composition
4. **Testability**: Enhanced services can be tested independently with mocked base services
5. **Backward Compatibility**: Base service interface remains unchanged

##### Implementation Pattern

```python
# Core service provides foundation
class CoreExcelService:
    def basic_export(self, data, path): ...

# Module extends through composition
class EnhancedExcelService:
    def __init__(self, base_service: CoreExcelService):
        self.base_service = base_service
    
    def enhanced_export(self, data, path, **advanced_options):
        # Use base service + add enhancements
        ...

# Container wires the composition
enhanced_service = providers.Factory(
    EnhancedExcelService,
    base_service=core_excel_service  # Inject base service
)
```

This pattern can be applied to any core service that needs module-specific enhancements, such as:
- Enhanced file processing for specific file types
- Specialized progress tracking for long-running operations  
- Module-specific validation or transformation logic
