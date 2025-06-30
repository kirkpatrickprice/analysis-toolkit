# Comprehensive Dependency Injection Implementation Plan

## Overview

This document outlines a comprehensive refactoring plan to implement dependency injection throughout the KP Analysis Toolkit codebase using the `dependency-injector` framework. This approach addresses not only the RichOutput global singleton pattern but also provides a holistic DI architecture for all major components.

## Framework Selection: dependency-injector

We will use the `dependency-injector` framework for several key reasons:

1. **Declarative Configuration**: Clean container definitions with type safety
2. **Multiple Provider Types**: Singleton, Factory, Resource, Configuration providers
3. **Lazy Initialization**: Components created only when needed
4. **Excellent Testing Support**: Built-in mocking and overriding capabilities
5. **Minimal Performance Overhead**: Optimized for production use
6. **Type Safety**: Full mypy support with proper type annotations

## Proposed Architecture

## Directory Structure and File Organization {#directory-structure}

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
│   │   ├── parallel_processing.py         # Parallel processing service & protocols
│   │   └── search_engine.py               # Search engine service & protocols
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

**Key Directory Features:**

- **`core/containers/`**: Hierarchical DI containers for shared services
- **`core/services/`**: Service interfaces and implementations for core functionality  
- **`core/parallel_engine/`**: Parallel processing component implementations
- **`{module}/container.py`**: Module-specific dependency injection containers
- **`{module}/service.py`**: Main service class for each module
- **`{module}/services/`**: Module-specific service implementations
- **Protocol Definitions**: Service protocols are co-located with implementations
- **Implementation Classes**: Concrete implementations referenced by string in containers

**File Organization Summary:**

| Component Type | Location | Purpose |
|---|---|---|
| **Core Containers** | `core/containers/` | Shared service DI configuration |
| **Core Services** | `core/services/` | Reusable service implementations |
| **Module Containers** | `{module}/container.py` | Module-specific DI configuration |
| **Module Services** | `{module}/service.py` | Main module service classes |
| **Module Utilities** | `{module}/services/` | Module-specific implementations |
| **Global Utilities** | `utils/` | Shared utility implementations |

**Key Benefits:**
This hierarchical approach provides several key benefits:

1. **Separation of Concerns**: Each container has a single, clear responsibility
2. **Module Independence**: Process scripts services are only loaded when the process scripts module is used
3. **Maintainability**: Changes to one module don't affect others
4. **Testing**: Each container can be tested independently
5. **Performance**: Only necessary services are instantiated
6. **Team Development**: Different teams can work on different containers without conflicts

**Navigation Links:**
- [Core Container Implementation](#core-container-shared-services)
- [File Processing Container](#file-processing-container) 
- [Excel Export Container](#excel-export-container)
- [Application Container](#main-application-container)
- [Process Scripts Container](#process-scripts-container)
- [CLI Integration](#updated-cli-integration-with-hierarchical-containers)
- [Testing Strategy](#testing-strategy)
- [Implementation Timeline](#implementation-timeline-hierarchical-approach)

## Container Architecture Details

### 1. Hierarchical Container Architecture

Create a modular dependency injection system with clear separation of concerns:

#### Core Container (Shared Services) {#core-container-shared-services}

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

#### File Processing Container {#file-processing-container}

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

#### Excel Export Container {#excel-export-container}

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

#### Module-Specific Containers {#process-scripts-container}

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

    # Main Module Service
    process_scripts_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.service.ProcessScriptsService",
        search_engine=search_engine_service,
        parallel_processing=core.parallel_processing_service,
        system_detection=system_detection_service,
        excel_export=excel_export.excel_export_service,
        file_processing=file_processing.file_processing_service,
        search_config=search_config_service,
        rich_output=core.rich_output,
    )


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
```

### 3. Wiring and Configuration

```python
# src/kp_analysis_toolkit/core/containers/__init__.py
from __future__ import annotations

from kp_analysis_toolkit.core.containers.application import ApplicationContainer
from kp_analysis_toolkit.core.containers.core import CoreContainer

__all__ = ["ApplicationContainer", "CoreContainer"]


# src/kp_analysis_toolkit/core/containers/application.py (continued)
from __future__ import annotations


def wire_container() -> None:
    """Wire the container for dependency injection."""
    container.wire(modules=[
        "kp_analysis_toolkit.cli",
        "kp_analysis_toolkit.process_scripts.cli",
        "kp_analysis_toolkit.nipper_expander.cli",
        "kp_analysis_toolkit.rtf_to_text.cli",
    ])


def configure_container(
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """Configure the container with runtime settings."""
    container.core.config.verbose.from_value(verbose)
    container.core.config.quiet.from_value(quiet)
    container.core.config.max_workers.from_value(max_workers or 4)
```

### 4. Service Interfaces and Implementations

Define clean service interfaces for all major components:

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

### 5. Updated CLI Integration with Hierarchical Containers

#### Main CLI with Hierarchical DI

```python
# src/kp_analysis_toolkit/cli.py (hierarchical DI integration)
from __future__ import annotations

import platform
import sys
from collections.abc import Callable
from pathlib import Path

import rich_click as click
from dependency_injector.wiring import Provide, inject

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.core.containers.application import ApplicationContainer, wire_container, configure_container
from kp_analysis_toolkit.utils.rich_output import RichOutput
from kp_analysis_toolkit.utils.version_checker import check_and_prompt_update

# Initialize DI container
container = ApplicationContainer()
wire_container()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--max-workers", type=int, help="Maximum number of worker processes")
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    quiet: bool,
    max_workers: int | None,
) -> None:
    """KP Analysis Toolkit - Security analysis and data processing utilities."""
    
    # Configure DI container with runtime settings
    configure_container(
        verbose=verbose,
        quiet=quiet,
        max_workers=max_workers,
    )
    
    # Store container in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['container'] = container


@cli.command()
@click.pass_context
@inject
def process_scripts(
    ctx: click.Context,
    service=Provide[container.process_scripts.process_scripts_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Process configuration scripts and generate analysis reports."""
    try:
        rich_output.header("Process Scripts Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in process scripts: {e}")
        raise


@cli.command()
@click.pass_context
@inject
def nipper_expander(
    ctx: click.Context,
    service=Provide[container.nipper_expander.nipper_expander_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Expand and process Nipper configuration files."""
    try:
        rich_output.header("Nipper Expander Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in nipper expander: {e}")
        raise


@cli.command()
@click.pass_context
@inject
def rtf_to_text(
    ctx: click.Context,
    service=Provide[container.rtf_to_text.rtf_to_text_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Convert RTF files to text format."""
    try:
        rich_output.header("RTF to Text Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in rtf to text: {e}")
        raise
```

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

### Parallel Processing Service

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

### 2. Container Directory Structure

See the comprehensive [Directory Structure and File Organization](#directory-structure) section for complete details.

### 3. Wiring and Configuration

```python
# src/kp_analysis_toolkit/core/containers/__init__.py
from __future__ import annotations

from kp_analysis_toolkit.core.containers.application import ApplicationContainer
from kp_analysis_toolkit.core.containers.core import CoreContainer

__all__ = ["ApplicationContainer", "CoreContainer"]


# src/kp_analysis_toolkit/core/containers/application.py (continued)
from __future__ import annotations


def wire_container() -> None:
    """Wire the container for dependency injection."""
    container.wire(modules=[
        "kp_analysis_toolkit.cli",
        "kp_analysis_toolkit.process_scripts.cli",
        "kp_analysis_toolkit.nipper_expander.cli",
        "kp_analysis_toolkit.rtf_to_text.cli",
    ])


def configure_container(
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """Configure the container with runtime settings."""
    container.core.config.verbose.from_value(verbose)
    container.core.config.quiet.from_value(quiet)
    container.core.config.max_workers.from_value(max_workers or 4)
```

### 4. Service Interfaces and Implementations

Define clean service interfaces for all major components:

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

### 5. Updated CLI Integration with Hierarchical Containers

#### Main CLI with Hierarchical DI

```python
# src/kp_analysis_toolkit/cli.py (hierarchical DI integration)
from __future__ import annotations

import platform
import sys
from collections.abc import Callable
from pathlib import Path

import rich_click as click
from dependency_injector.wiring import Provide, inject

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.core.containers.application import ApplicationContainer, wire_container, configure_container
from kp_analysis_toolkit.utils.rich_output import RichOutput
from kp_analysis_toolkit.utils.version_checker import check_and_prompt_update

# Initialize DI container
container = ApplicationContainer()
wire_container()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--max-workers", type=int, help="Maximum number of worker processes")
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    quiet: bool,
    max_workers: int | None,
) -> None:
    """KP Analysis Toolkit - Security analysis and data processing utilities."""
    
    # Configure DI container with runtime settings
    configure_container(
        verbose=verbose,
        quiet=quiet,
        max_workers=max_workers,
    )
    
    # Store container in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['container'] = container


@cli.command()
@click.pass_context
@inject
def process_scripts(
    ctx: click.Context,
    service=Provide[container.process_scripts.process_scripts_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Process configuration scripts and generate analysis reports."""
    try:
        rich_output.header("Process Scripts Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in process scripts: {e}")
        raise


@cli.command()
@click.pass_context
@inject
def nipper_expander(
    ctx: click.Context,
    service=Provide[container.nipper_expander.nipper_expander_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Expand and process Nipper configuration files."""
    try:
        rich_output.header("Nipper Expander Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in nipper expander: {e}")
        raise


@cli.command()
@click.pass_context
@inject
def rtf_to_text(
    ctx: click.Context,
    service=Provide[container.rtf_to_text.rtf_to_text_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Convert RTF files to text format."""
    try:
        rich_output.header("RTF to Text Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in rtf to text: {e}")
        raise
```

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

### Parallel Processing Service

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

#### Module-Specific Containers

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

    # Main Module Service
    process_scripts_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.service.ProcessScriptsService",
        search_engine=search_engine_service,
        parallel_processing=core.parallel_processing_service,
        system_detection=system_detection_service,
        excel_export=excel_export.excel_export_service,
        file_processing=file_processing.file_processing_service,
        search_config=search_config_service,
        rich_output=core.rich_output,
    )


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
```

#### Container Organization and Benefits

This hierarchical approach provides several key benefits:

1. **Separation of Concerns**: Each container has a single, clear responsibility
2. **Module Independence**: Process scripts services are only loaded when the process scripts module is used
3. **Maintainability**: Changes to one module don't affect others
4. **Testing**: Each container can be tested independently
5. **Performance**: Only necessary services are instantiated
6. **Team Development**: Different teams can work on different containers without conflicts

### 3. Wiring and Configuration

```python
# src/kp_analysis_toolkit/core/containers/__init__.py
from __future__ import annotations

from kp_analysis_toolkit.core.containers.application import ApplicationContainer
from kp_analysis_toolkit.core.containers.core import CoreContainer

__all__ = ["ApplicationContainer", "CoreContainer"]


# src/kp_analysis_toolkit/core/containers/application.py (continued)
from __future__ import annotations


def wire_container() -> None:
    """Wire the container for dependency injection."""
    container.wire(modules=[
        "kp_analysis_toolkit.cli",
        "kp_analysis_toolkit.process_scripts.cli",
        "kp_analysis_toolkit.nipper_expander.cli",
        "kp_analysis_toolkit.rtf_to_text.cli",
    ])


def configure_container(
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """Configure the container with runtime settings."""
    container.core.config.verbose.from_value(verbose)
    container.core.config.quiet.from_value(quiet)
    container.core.config.max_workers.from_value(max_workers or 4)
```

### 4. Service Interfaces and Implementations

Define clean service interfaces for all major components:

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

### 5. Updated CLI Integration with Hierarchical Containers

#### Main CLI with Hierarchical DI

```python
# src/kp_analysis_toolkit/cli.py (hierarchical DI integration)
from __future__ import annotations

import platform
import sys
from collections.abc import Callable
from pathlib import Path

import rich_click as click
from dependency_injector.wiring import Provide, inject

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.core.containers.application import ApplicationContainer, wire_container, configure_container
from kp_analysis_toolkit.utils.rich_output import RichOutput
from kp_analysis_toolkit.utils.version_checker import check_and_prompt_update

# Initialize DI container
container = ApplicationContainer()
wire_container()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--max-workers", type=int, help="Maximum number of worker processes")
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    quiet: bool,
    max_workers: int | None,
) -> None:
    """KP Analysis Toolkit - Security analysis and data processing utilities."""
    
    # Configure DI container with runtime settings
    configure_container(
        verbose=verbose,
        quiet=quiet,
        max_workers=max_workers,
    )
    
    # Store container in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['container'] = container


@cli.command()
@click.pass_context
@inject
def process_scripts(
    ctx: click.Context,
    service=Provide[container.process_scripts.process_scripts_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Process configuration scripts and generate analysis reports."""
    try:
        rich_output.header("Process Scripts Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in process scripts: {e}")
        raise


@cli.command()
@click.pass_context
@inject
def nipper_expander(
    ctx: click.Context,
    service=Provide[container.nipper_expander.nipper_expander_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Expand and process Nipper configuration files."""
    try:
        rich_output.header("Nipper Expander Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in nipper expander: {e}")
        raise


@cli.command()
@click.pass_context
@inject
def rtf_to_text(
    ctx: click.Context,
    service=Provide[container.rtf_to_text.rtf_to_text_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Convert RTF files to text format."""
    try:
        rich_output.header("RTF to Text Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in rtf to text: {e}")
        raise
```

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

### Parallel Processing Service

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

#### Module-Specific Containers

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

    # Main Module Service
    process_scripts_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.service.ProcessScriptsService",
        search_engine=search_engine_service,
        parallel_processing=core.parallel_processing_service,
        system_detection=system_detection_service,
        excel_export=excel_export.excel_export_service,
        file_processing=file_processing.file_processing_service,
        search_config=search_config_service,
        rich_output=core.rich_output,
    )


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
```

#### Container Organization and Benefits

This hierarchical approach provides several key benefits:

1. **Separation of Concerns**: Each container has a single, clear responsibility
2. **Module Independence**: Process scripts services are only loaded when the process scripts module is used
3. **Maintainability**: Changes to one module don't affect others
4. **Testing**: Each container can be tested independently
5. **Performance**: Only necessary services are instantiated
6. **Team Development**: Different teams can work on different containers without conflicts

### 3. Wiring and Configuration

```python
# src/kp_analysis_toolkit/core/containers/__init__.py
from __future__ import annotations

from kp_analysis_toolkit.core.containers.application import ApplicationContainer
from kp_analysis_toolkit.core.containers.core import CoreContainer

__all__ = ["ApplicationContainer", "CoreContainer"]


# src/kp_analysis_toolkit/core/containers/application.py (continued)
from __future__ import annotations


def wire_container() -> None:
    """Wire the container for dependency injection."""
    container.wire(modules=[
        "kp_analysis_toolkit.cli",
        "kp_analysis_toolkit.process_scripts.cli",
        "kp_analysis_toolkit.nipper_expander.cli",
        "kp_analysis_toolkit.rtf_to_text.cli",
    ])


def configure_container(
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """Configure the container with runtime settings."""
    container.core.config.verbose.from_value(verbose)
    container.core.config.quiet.from_value(quiet)
    container.core.config.max_workers.from_value(max_workers or 4)
```

### 4. Service Interfaces and Implementations

Define clean service interfaces for all major components:

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

### 5. Updated CLI Integration with Hierarchical Containers

#### Main CLI with Hierarchical DI

```python
# src/kp_analysis_toolkit/cli.py (hierarchical DI integration)
from __future__ import annotations

import platform
import sys
from collections.abc import Callable
from pathlib import Path

import rich_click as click
from dependency_injector.wiring import Provide, inject

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.core.containers.application import ApplicationContainer, wire_container, configure_container
from kp_analysis_toolkit.utils.rich_output import RichOutput
from kp_analysis_toolkit.utils.version_checker import check_and_prompt_update

# Initialize DI container
container = ApplicationContainer()
wire_container()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--max-workers", type=int, help="Maximum number of worker processes")
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: bool,
    quiet: bool,
    max_workers: int | None,
) -> None:
    """KP Analysis Toolkit - Security analysis and data processing utilities."""
    
    # Configure DI container with runtime settings
    configure_container(
        verbose=verbose,
        quiet=quiet,
        max_workers=max_workers,
    )
    
    # Store container in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['container'] = container


@cli.command()
@click.pass_context
@inject
def process_scripts(
    ctx: click.Context,
    service=Provide[container.process_scripts.process_scripts_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Process configuration scripts and generate analysis reports."""
    try:
        rich_output.header("Process Scripts Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in process scripts: {e}")
        raise


@cli.command()
@click.pass_context
@inject
def nipper_expander(
    ctx: click.Context,
    service=Provide[container.nipper_expander.nipper_expander_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Expand and process Nipper configuration files."""
    try:
        rich_output.header("Nipper Expander Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in nipper expander: {e}")
        raise


@cli.command()
@click.pass_context
@inject
def rtf_to_text(
    ctx: click.Context,
    service=Provide[container.rtf_to_text.rtf_to_text_service],
    rich_output: RichOutput = Provide[container.core.rich_output],
) -> None:
    """Convert RTF files to text format."""
    try:
        rich_output.header("RTF to Text Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in rtf to text: {e}")
        raise
```

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

### Parallel Processing Service

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

#### Module-Specific Containers

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

    # Main Module Service
    process_scripts_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.service.ProcessScriptsService",
        search_engine=search_engine_service,
        parallel_processing=core.parallel_processing_service,
        system_detection=system_detection_service,
        excel_export=excel_export.excel_export_service,
        file_processing=file_processing.file_processing_service,
        search_config=search_config_service,
        rich_output=core.rich_output,
    )


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

#### Main Application Container

```python
# src/kp_analysis_toolkit/core/containers/application.py
from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.containers.core import CoreContainer
from kp_analysis_toolkit.core.containers.excel_export import ExcelExportContainer
from kp_analysis_toolkit.core.containers.file_processing import FileProcessingContainer
from kp_analysis_toolkit.process_scripts