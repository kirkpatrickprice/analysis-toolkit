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

### 1. Hierarchical Container Architecture

Create a modular dependency injection system with clear separation of concerns:

#### Core Container (Shared Services)

```python
# src/kp_analysis_toolkit/core/containers/core.py
from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services import (
    ConfigurationService,
    ExcelExportService,
    FileProcessingService,
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


# src/kp_analysis_toolkit/core/containers/file_processing.py
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


# src/kp_analysis_toolkit/core/containers/configuration.py
class ConfigurationContainer(containers.DeclarativeContainer):
    """Configuration loading and YAML processing services."""

    # Dependencies
    core = providers.DependenciesContainer()

    # Configuration Components
    yaml_parser = providers.Factory(
        "kp_analysis_toolkit.core.services.configuration.PyYamlParser"
    )
    
    file_resolver = providers.Factory(
        "kp_analysis_toolkit.core.services.configuration.StandardFileResolver"
    )
    
    include_processor = providers.Factory(
        "kp_analysis_toolkit.core.services.configuration.StandardIncludeProcessor",
        yaml_parser=yaml_parser,
        file_resolver=file_resolver,
    )
    
    # Main Service
    configuration_service = providers.Factory(
        ConfigurationService,
        yaml_parser=yaml_parser,
        file_resolver=file_resolver,
        include_processor=include_processor,
        rich_output=core.rich_output,
    )


# src/kp_analysis_toolkit/core/containers/excel_export.py
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

#### Module-Specific Containers

```python
# src/kp_analysis_toolkit/process_scripts/container.py
from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services import (
    ParallelProcessingService,
    SearchEngineService,
    SystemDetectionService,
)


class ProcessScriptsContainer(containers.DeclarativeContainer):
    """Services specific to the process scripts module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()
    configuration = providers.DependenciesContainer()
    excel_export = providers.DependenciesContainer()

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

    # Parallel Processing Services (process_scripts specific)
    executor_factory = providers.Factory(
        "kp_analysis_toolkit.process_scripts.parallel_engine.ProcessPoolExecutorFactory",
        max_workers=core.config.max_workers.provided,
    )
    
    progress_tracker = providers.Factory(
        "kp_analysis_toolkit.process_scripts.parallel_engine.ProgressTracker",
        rich_output=core.rich_output,
    )
    
    interrupt_handler = providers.Factory(
        "kp_analysis_toolkit.process_scripts.parallel_engine.InterruptHandler",
        rich_output=core.rich_output,
    )
    
    parallel_processing_service = providers.Factory(
        ParallelProcessingService,
        executor_factory=executor_factory,
        progress_tracker=progress_tracker,
        interrupt_handler=interrupt_handler,
        rich_output=core.rich_output,
    )

    # Main Module Service
    process_scripts_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.service.ProcessScriptsService",
        search_engine=search_engine_service,
        parallel_processing=parallel_processing_service,
        system_detection=system_detection_service,
        excel_export=excel_export.excel_export_service,
        file_processing=file_processing.file_processing_service,
        configuration=configuration.configuration_service,
        rich_output=core.rich_output,
    )


# src/kp_analysis_toolkit/nipper_expander/container.py
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
from dependency_injector import containers, providers

from kp_analysis_toolkit.core.containers.core import CoreContainer
from kp_analysis_toolkit.core.containers.configuration import ConfigurationContainer
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
    
    configuration = providers.Container(
        ConfigurationContainer,
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
        configuration=configuration,
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

### 2. Container Directory Structure

```
src/kp_analysis_toolkit/
├── core/
│   └── containers/
│       ├── __init__.py
│       ├── core.py              # Core services (RichOutput)
│       ├── file_processing.py   # File processing services
│       ├── configuration.py     # Configuration services
│       ├── excel_export.py      # Excel export services
│       └── application.py       # Main application container
├── process_scripts/
│   ├── container.py            # Process scripts specific services
│   └── service.py              # Main process scripts service
├── nipper_expander/
│   ├── container.py            # Nipper expander specific services
│   └── service.py              # Main nipper expander service
└── rtf_to_text/
    ├── container.py            # RTF to text specific services
    └── service.py              # Main RTF to text service
```

### 3. Wiring and Configuration

```python
# src/kp_analysis_toolkit/core/containers/__init__.py
from kp_analysis_toolkit.core.containers.application import ApplicationContainer
from kp_analysis_toolkit.core.containers.core import CoreContainer

__all__ = ["ApplicationContainer", "CoreContainer"]


# src/kp_analysis_toolkit/core/containers/application.py (continued)
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
from kp_analysis_toolkit.core.services.configuration import ConfigurationService
from kp_analysis_toolkit.core.services.excel_export import ExcelExportService
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.parallel_processing import ParallelProcessingService
from kp_analysis_toolkit.core.services.search_engine import SearchEngineService
from kp_analysis_toolkit.core.services.system_detection import SystemDetectionService

__all__ = [
    "ConfigurationService",
    "ExcelExportService", 
    "FileProcessingService",
    "ParallelProcessingService",
    "SearchEngineService",
    "SystemDetectionService",
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

### 3. Dependency Injection Integration

```python
# src/kp_analysis_toolkit/process_scripts/context.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.application import ApplicationContextProtocol
    from kp_analysis_toolkit.utils.rich_output import RichOutput


class ProcessScriptsContext:
    """Context for process scripts module operations."""
    
    def __init__(self, app_context: ApplicationContextProtocol) -> None:
        """Initialize with application context."""
        self.app_context = app_context
        self._rich_output = app_context.get_rich_output()
    
    @property
    def rich_output(self) -> RichOutput:
        """Get the RichOutput instance."""
        return self._rich_output
    
    def create_parallel_engine(self) -> ParallelEngine:
        """Factory method for creating parallel engine with dependencies."""
        from kp_analysis_toolkit.process_scripts.parallel_engine import ParallelEngine
        return ParallelEngine(rich_output=self._rich_output)
    
    def create_search_engine(self) -> SearchEngine:
        """Factory method for creating search engine with dependencies."""
        from kp_analysis_toolkit.process_scripts.search_engine import SearchEngine
        return SearchEngine(rich_output=self._rich_output)
```

### 3. Refactored Core Classes

#### Parallel Engine with Dependency Injection

```python
# src/kp_analysis_toolkit/process_scripts/parallel_engine.py (refactored)
from __future__ import annotations

import contextlib
import multiprocessing as mp
import signal
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, NamedTuple

from kp_analysis_toolkit.process_scripts.models.results.base import SearchResults
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.utils.rich_output import RichOutput


class ProcessingContext(NamedTuple):
    """Context for processing futures with common parameters."""

    future_to_config: dict[object, SearchConfig]
    results: list[SearchResults]
    progress: object
    search_task: int
    max_name_width: int
    rich_output: RichOutput  # Now explicitly typed


class InterruptHandler:
    """Thread-safe interrupt handler for graceful cancellation."""

    def __init__(self, rich_output: RichOutput) -> None:
        """Initialize with explicit RichOutput dependency."""
        self.interrupted = False
        self.force_terminate = False
        self.original_handler = None
        self.rich_output = rich_output
        self._lock = mp.Lock()

    # ... rest of implementation unchanged


class ParallelEngine:
    """Parallel execution engine with dependency injection."""
    
    def __init__(self, rich_output: RichOutput) -> None:
        """Initialize with RichOutput dependency."""
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
        interrupt_handler = InterruptHandler(self.rich_output)
        interrupt_handler.setup()

        try:
            with self.rich_output.progress(
                show_eta=True,
                show_percentage=True,
                show_time_elapsed=True,
            ) as progress:
                # ... rest of implementation using self.rich_output
                
        finally:
            interrupt_handler.cleanup()

        return results
```

#### Search Engine with Dependency Injection

```python
# src/kp_analysis_toolkit/process_scripts/search_engine.py (refactored)
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_analysis_toolkit.utils.rich_output import RichOutput


class SearchEngine:
    """Search engine with dependency injection."""
    
    def __init__(self, rich_output: RichOutput) -> None:
        """Initialize with RichOutput dependency."""
        self.rich_output = rich_output
    
    def execute_search(
        self,
        search_config: SearchConfig,
        systems: list[Systems],
    ) -> SearchResults:
        """Execute search with injected dependencies."""
        try:
            # Use self.rich_output instead of get_rich_output()
            self.rich_output.debug(f"Executing search: {search_config.name}")
            # ... rest of implementation
        except Exception as e:
            self.rich_output.error(f"Search failed: {e}")
            raise
```

### 4. Updated CLI Entry Points

#### Main CLI with Application Context

```python
# src/kp_analysis_toolkit/cli.py (refactored)
import platform
import sys
from collections.abc import Callable
from pathlib import Path

import rich_click as click

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.core.application import ApplicationContext, ApplicationSettings
from kp_analysis_toolkit.utils.version_checker import check_and_prompt_update

# ... rich_click configuration remains the same ...


def _version_callback(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    """Display version information with Rich formatting and exit."""
    if not value or ctx.resilient_parsing:
        return

    # Create application context for version display
    app_context = ApplicationContext()
    rich_output = app_context.get_rich_output()

    # Include the expected text for test compatibility
    rich_output.print("kpat_cli version " + cli_version)
    rich_output.print("")

    # Main banner
    rich_output.banner(
        title="🔧 KP Analysis Toolkit",
        subtitle="Python utilities for security analysis and data processing",
        version=cli_version,
        force=True,
    )
    # ... rest of implementation


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--quiet",
    "-q", 
    is_flag=True,
    help="Suppress non-essential output",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """KP Analysis Toolkit - Security analysis and data processing utilities."""
    
    # Create application context and store in click context
    settings = ApplicationSettings(
        verbose=verbose,
        quiet=quiet,
    )
    ctx.ensure_object(dict)
    ctx.obj['app_context'] = ApplicationContext(settings)


@cli.command()
@click.pass_context  
def process_scripts(ctx: click.Context) -> None:
    """Process configuration scripts and generate analysis reports."""
    app_context = ctx.obj['app_context']
    
    # Pass app_context to process_scripts module
    from kp_analysis_toolkit.process_scripts.cli import process_command_line
    process_command_line(app_context)
```

#### Process Scripts CLI with Context

```python
# src/kp_analysis_toolkit/process_scripts/cli.py (refactored)
from __future__ import annotations

from typing import TYPE_CHECKING

import rich_click as click

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.application import ApplicationContextProtocol


def process_command_line(app_context: ApplicationContextProtocol) -> None:
    """Process command line with application context."""
    from kp_analysis_toolkit.process_scripts.context import ProcessScriptsContext
    
    # Create module context
    module_context = ProcessScriptsContext(app_context)
    
    # Use the context for all operations
    rich_output = module_context.rich_output
    
    try:
        rich_output.header("Process Scripts Module")
        # ... rest of CLI implementation using module_context
        
    except Exception as e:
        rich_output.error(f"Error in process scripts: {e}")
        raise
```

### 5. Updated Function Signatures

#### CLI Functions with Context

```python
# src/kp_analysis_toolkit/process_scripts/cli_functions.py (refactored)
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_analysis_toolkit.process_scripts.context import ProcessScriptsContext
    from kp_analysis_toolkit.utils.rich_output import RichOutput


def list_systems(
    program_config: ProgramConfig,
    context: ProcessScriptsContext,
) -> None:
    """List all systems found in the specified source files."""
    rich_output = context.rich_output
    rich_output.header("Systems Found")

    systems = list(process_systems.enumerate_systems_from_source_files(program_config))

    if not systems:
        rich_output.warning("No systems found")
        return

    # ... rest of implementation using rich_output parameter


def process_and_export_searches(
    program_config: ProgramConfig,
    context: ProcessScriptsContext,
) -> None:
    """Process search configurations and export results."""
    rich_output = context.rich_output
    rich_output.header("Processing Source Files")

    # Create results path
    create_results_path(program_config)

    # Load systems
    systems: list[Systems] = list(
        process_systems.enumerate_systems_from_source_files(program_config),
    )
    rich_output.info(f"Found {len(systems)} systems to process")

    # Create parallel engine with context
    parallel_engine = context.create_parallel_engine()
    
    # ... rest of implementation
```

### 6. Migration Strategy for Process Systems

```python
# src/kp_analysis_toolkit/process_scripts/process_systems.py (minimal changes)
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_analysis_toolkit.utils.rich_output import RichOutput

# Keep existing functions but add optional rich_output parameter
def enumerate_systems_from_source_files(
    program_config: ProgramConfig,
    rich_output: RichOutput | None = None,
) -> Generator[Systems, None, None]:
    """Process the text files to enumerate the systems."""
    
    # Use injected rich_output or fall back to module function for compatibility
    if rich_output is None:
        from kp_analysis_toolkit.utils.rich_output import warning as _warning
        warning_func = _warning
    else:
        warning_func = rich_output.warning
    
    for file in get_source_files(program_config):
        # ... existing implementation
        
        # Skip files where producer cannot be determined
        if producer == ProducerType.OTHER:
            warning_func(f"Skipping file due to unknown producer: {file}")
            continue
            
        # ... rest of implementation unchanged
```

## Backwards Compatibility Strategy

### 1. Transitional Module Functions

Keep existing module-level convenience functions during transition:

```python
# src/kp_analysis_toolkit/utils/rich_output.py (backwards compatibility)

# Keep existing RichOutput class unchanged

# Transitional global singleton (marked for deprecation)
_rich_output: RichOutput | None = None
_creation_lock = threading.Lock()

def get_rich_output(*, verbose: bool | None = None, quiet: bool | None = None) -> RichOutput:
    """
    Get or create the global RichOutput instance.
    
    DEPRECATED: Use dependency injection with ApplicationContext instead.
    This function is maintained for backwards compatibility only.
    """
    global _rich_output
    # ... existing implementation with deprecation warning
    import warnings
    warnings.warn(
        "get_rich_output() is deprecated. Use ApplicationContext with dependency injection.",
        DeprecationWarning,
        stacklevel=2,
    )
    # ... rest of existing implementation


# Keep existing convenience functions with deprecation warnings
def info(text: str, *, force: bool = False) -> None:
    """Display an info message. DEPRECATED: Use context.rich_output.info() instead."""
    import warnings
    warnings.warn(
        "Module-level info() is deprecated. Use context.rich_output.info() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    get_rich_output().info(text, force=force)

# ... similar for other convenience functions
```

### 2. Gradual Migration Path

1. **Phase 1**: Implement ApplicationContext and update CLI entry points
2. **Phase 2**: Update major classes (ParallelEngine, SearchEngine) to accept RichOutput
3. **Phase 3**: Update module functions to accept optional RichOutput parameter
4. **Phase 4**: Remove deprecation warnings and backwards compatibility code

## Testing Strategy

### 1. Context-Based Testing

```python
# tests/test_with_context.py
import pytest

from kp_analysis_toolkit.core.application import ApplicationContext, ApplicationSettings
from kp_analysis_toolkit.process_scripts.context import ProcessScriptsContext


@pytest.fixture
def app_context():
    """Provide application context for testing."""
    settings = ApplicationSettings(verbose=True, quiet=False)
    return ApplicationContext(settings)


@pytest.fixture  
def process_scripts_context(app_context):
    """Provide process scripts context for testing."""
    return ProcessScriptsContext(app_context)


def test_parallel_engine_with_context(process_scripts_context):
    """Test parallel engine with dependency injection."""
    engine = process_scripts_context.create_parallel_engine()
    assert engine.rich_output is not None
    assert engine.rich_output.verbose is True


def test_isolated_contexts():
    """Test that different contexts are isolated."""
    ctx1 = ApplicationContext(ApplicationSettings(verbose=True))
    ctx2 = ApplicationContext(ApplicationSettings(verbose=False))
    
    assert ctx1.get_rich_output().verbose is True
    assert ctx2.get_rich_output().verbose is False
    assert ctx1.get_rich_output() is not ctx2.get_rich_output()
```

### 2. Mock-Friendly Testing

```python
# tests/test_with_mocks.py
from unittest.mock import Mock

def test_parallel_engine_with_mock():
    """Test parallel engine with mocked RichOutput."""
    mock_rich_output = Mock()
    engine = ParallelEngine(rich_output=mock_rich_output)
    
    # Test that methods are called correctly
    engine.search_configs_with_processes([], [], 1)
    mock_rich_output.progress.assert_called_once()
```

## Implementation Timeline (Hierarchical Approach)

### Phase 1: Core Infrastructure (Week 1-2)
1. **Install dependency-injector framework**
   ```bash
   uv add dependency-injector
   ```

2. **Create core container hierarchy**
   - `src/kp_analysis_toolkit/core/containers/core.py` - Core services
   - `src/kp_analysis_toolkit/core/containers/file_processing.py` - File processing
   - `src/kp_analysis_toolkit/core/containers/excel_export.py` - Excel export
   - `src/kp_analysis_toolkit/core/containers/configuration.py` - Configuration
   - `src/kp_analysis_toolkit/core/containers/application.py` - Main container

3. **Update main CLI entry point**
   - Add hierarchical container initialization
   - Wire dependency injection
   - Maintain backward compatibility

### Phase 2: Core Service Containers (Week 3)
1. **Implement core service containers**
   - CoreContainer with RichOutput
   - FileProcessingContainer with encoding/hash/validation
   - ConfigurationContainer with YAML processing
   - ExcelExportContainer with formatting/tables

2. **Create service interface protocols**
   - File processing protocols
   - Configuration protocols
   - Excel export protocols

3. **Update related utilities and tests**

### Phase 3: Module-Specific Containers (Week 4-5)
1. **Create ProcessScriptsContainer**
   - System detection services
   - Search engine services  
   - Parallel processing services
   - ProcessScriptsService

2. **Create NipperExpanderContainer**
   - NipperExpanderService
   - Any module-specific services

3. **Create RtfToTextContainer**
   - RtfToTextService
   - Any module-specific services

### Phase 4: Integration and Wiring (Week 6-7)
1. **Complete ApplicationContainer**
   - Wire all containers together
   - Configure dependency relationships
   - Test container hierarchy

2. **Update all CLI commands**
   - Use hierarchical container paths
   - Update injection decorators
   - Test CLI integration

3. **Implement module service providers**
   - Complete service implementations
   - Test service functionality

### Phase 5: Testing and Documentation (Week 8)
1. **Comprehensive testing with hierarchical DI**
   - Unit tests for each container
   - Integration tests with container hierarchy
   - Performance testing

2. **Update documentation**
   - Hierarchical architecture documentation
   - Container organization guide
   - Migration guide

3. **Remove deprecated code and backward compatibility**

## File Organization Summary

### New Files (Hierarchical Approach)
```
src/kp_analysis_toolkit/core/containers/
├── __init__.py
├── core.py              # CoreContainer
├── file_processing.py   # FileProcessingContainer  
├── configuration.py     # ConfigurationContainer
├── excel_export.py      # ExcelExportContainer
└── application.py       # ApplicationContainer

src/kp_analysis_toolkit/process_scripts/
├── container.py         # ProcessScriptsContainer
└── service.py          # ProcessScriptsService

src/kp_analysis_toolkit/nipper_expander/
├── container.py         # NipperExpanderContainer
└── service.py          # NipperExpanderService

src/kp_analysis_toolkit/rtf_to_text/
├── container.py         # RtfToTextContainer
└── service.py          # RtfToTextService

tests/core/containers/   # Tests for each container
tests/integration/       # Integration tests
```

## Detailed Service Implementations

### Configuration Service Implementation

```python
# src/kp_analysis_toolkit/core/services/configuration.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import yaml

from kp_analysis_toolkit.utils.rich_output import RichOutput


class YamlParser(Protocol):
    """Protocol for YAML parsing operations."""
    
    def parse_yaml(self, content: str) -> dict[str, Any]: ...
    def load_yaml_file(self, file_path: Path) -> dict[str, Any]: ...


class FileResolver(Protocol):
    """Protocol for file resolution operations."""
    
    def resolve_path(self, base_path: Path, relative_path: str) -> Path: ...
    def find_config_file(self, search_paths: list[Path], filename: str) -> Path | None: ...


class IncludeProcessor(Protocol):
    """Protocol for processing include directives in configuration."""
    
    def process_includes(self, config: dict[str, Any], base_path: Path) -> dict[str, Any]: ...


class ConfigurationService:
    """Service for configuration loading and processing."""
    
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
    
    def load_configuration(self, config_path: Path) -> dict[str, Any]:
        """Load and process configuration file with includes."""
        try:
            self.rich_output.debug(f"Loading configuration from {config_path}")
            
            # Load base configuration
            config = self.yaml_parser.load_yaml_file(config_path)
            
            # Process any include directives
            config = self.include_processor.process_includes(config, config_path.parent)
            
            self.rich_output.debug(f"Configuration loaded successfully")
            return config
            
        except Exception as e:
            self.rich_output.error(f"Failed to load configuration: {e}")
            raise


# Implementation classes
class PyYamlParser:
    """PyYAML-based YAML parser implementation."""
    
    def parse_yaml(self, content: str) -> dict[str, Any]:
        """Parse YAML content string."""
        return yaml.safe_load(content)
    
    def load_yaml_file(self, file_path: Path) -> dict[str, Any]:
        """Load YAML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)


class StandardFileResolver:
    """Standard file resolver implementation."""
    
    def resolve_path(self, base_path: Path, relative_path: str) -> Path:
        """Resolve relative path against base path."""
        return (base_path / relative_path).resolve()
    
    def find_config_file(self, search_paths: list[Path], filename: str) -> Path | None:
        """Find configuration file in search paths."""
        for search_path in search_paths:
            candidate = search_path / filename
            if candidate.exists():
                return candidate
        return None


class StandardIncludeProcessor:
    """Standard include processor implementation."""
    
    def __init__(self, yaml_parser: YamlParser, file_resolver: FileResolver) -> None:
        self.yaml_parser = yaml_parser
        self.file_resolver = file_resolver
    
    def process_includes(self, config: dict[str, Any], base_path: Path) -> dict[str, Any]:
        """Process include directives in configuration."""
        if 'includes' not in config:
            return config
        
        # Process each include
        for include_path in config['includes']:
            resolved_path = self.file_resolver.resolve_path(base_path, include_path)
            include_config = self.yaml_parser.load_yaml_file(resolved_path)
            
            # Merge configurations (simple merge, can be enhanced)
            config.update(include_config)
        
        # Remove includes directive after processing
        del config['includes']
        return config
```

### System Detection Service Implementation

```python
# src/kp_analysis_toolkit/core/services/system_detection.py
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.process_scripts.models.enums.producer_type import ProducerType
from kp_analysis_toolkit.utils.rich_output import RichOutput


class OSDetector(Protocol):
    """Protocol for operating system detection."""
    
    def detect_os(self, file_content: str, file_path: Path) -> str | None: ...


class ProducerDetector(Protocol):
    """Protocol for producer detection."""
    
    def detect_producer(self, file_content: str, file_path: Path) -> ProducerType: ...


class DistroClassifier(Protocol):
    """Protocol for distribution classification."""
    
    def classify_distribution(self, file_content: str, os_name: str) -> str | None: ...


class SystemDetectionService:
    """Service for system detection and classification."""
    
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
    
    def detect_system(self, file_path: Path, file_content: str) -> Systems | None:
        """Detect system information from file content."""
        try:
            # Detect producer type
            producer = self.producer_detector.detect_producer(file_content, file_path)
            if producer == ProducerType.OTHER:
                self.rich_output.warning(f"Unknown producer for file: {file_path}")
                return None
            
            # Detect operating system
            os_name = self.os_detector.detect_os(file_content, file_path)
            if not os_name:
                self.rich_output.warning(f"Could not detect OS for file: {file_path}")
                return None
            
            # Classify distribution if applicable
            distribution = self.distro_classifier.classify_distribution(file_content, os_name)
            
            return Systems(
                file_path=file_path,
                producer=producer,
                os_name=os_name,
                distribution=distribution,
            )
            
        except Exception as e:
            self.rich_output.error(f"System detection failed for {file_path}: {e}")
            return None
```

### Complete Container Configuration

```python
# src/kp_analysis_toolkit/core/container.py (complete implementation)
from __future__ import annotations

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

# Import all service interfaces
from kp_analysis_toolkit.core.services.configuration import (
    ConfigurationService,
    PyYamlParser,
    StandardFileResolver,
    StandardIncludeProcessor,
)
from kp_analysis_toolkit.core.services.excel_export import ExcelExportService
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.parallel_processing import ParallelProcessingService
from kp_analysis_toolkit.core.services.search_engine import SearchEngineService
from kp_analysis_toolkit.core.services.system_detection import SystemDetectionService
from kp_analysis_toolkit.utils.rich_output import RichOutput


class ApplicationContainer(containers.DeclarativeContainer):
    """Main dependency injection container for the KP Analysis Toolkit."""

    # Configuration
    config = providers.Configuration()

    # Core Services
    rich_output = providers.Singleton(
        RichOutput,
        verbose=config.verbose.provided,
        quiet=config.quiet.provided,
    )

    # File Processing Services
    encoding_detector = providers.Factory(
        "kp_analysis_toolkit.utils.get_file_encoding.ChardetEncodingDetector"
    )
    
    hash_generator = providers.Factory(
        "kp_analysis_toolkit.utils.shared_funcs.SHA256HashGenerator"
    )
    
    file_validator = providers.Factory(
        "kp_analysis_toolkit.utils.shared_funcs.PathLibFileValidator"
    )
    
    file_processing_service = providers.Factory(
        FileProcessingService,
        encoding_detector=encoding_detector,
        hash_generator=hash_generator,
        file_validator=file_validator,
        rich_output=rich_output,
    )

    # Configuration Services
    yaml_parser = providers.Factory(PyYamlParser)
    
    file_resolver = providers.Factory(StandardFileResolver)
    
    include_processor = providers.Factory(
        StandardIncludeProcessor,
        yaml_parser=yaml_parser,
        file_resolver=file_resolver,
    )
    
    configuration_service = providers.Factory(
        ConfigurationService,
        yaml_parser=yaml_parser,
        file_resolver=file_resolver,
        include_processor=include_processor,
        rich_output=rich_output,
    )

    # System Detection Services
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
        rich_output=rich_output,
    )

    # Excel Export Services
    workbook_engine = providers.Factory(
        "kp_analysis_toolkit.utils.excel_utils.OpenpyxlEngine"
    )
    
    excel_formatter = providers.Factory(
        "kp_analysis_toolkit.utils.excel_utils.StandardExcelFormatter"
    )
    
    table_generator = providers.Factory(
        "kp_analysis_toolkit.utils.excel_utils.StandardTableGenerator"
    )
    
    excel_export_service = providers.Factory(
        ExcelExportService,
        workbook_engine=workbook_engine,
        formatter=excel_formatter,
        table_generator=table_generator,
        rich_output=rich_output,
    )

    # Search Engine Services
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
        rich_output=rich_output,
    )

    # Parallel Processing Services
    executor_factory = providers.Factory(
        "kp_analysis_toolkit.process_scripts.parallel_engine.ProcessPoolExecutorFactory",
        max_workers=config.max_workers.provided,
    )
    
    progress_tracker = providers.Factory(
        "kp_analysis_toolkit.process_scripts.parallel_engine.ProgressTracker",
        rich_output=rich_output,
    )
    
    interrupt_handler = providers.Factory(
        "kp_analysis_toolkit.process_scripts.parallel_engine.InterruptHandler",
        rich_output=rich_output,
    )
    
    parallel_processing_service = providers.Factory(
        ParallelProcessingService,
        executor_factory=executor_factory,
        progress_tracker=progress_tracker,
        interrupt_handler=interrupt_handler,
        rich_output=rich_output,
    )

    # Module-Level Services
    process_scripts_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.service.ProcessScriptsService",
        search_engine=search_engine_service,
        parallel_processing=parallel_processing_service,
        system_detection=system_detection_service,
        excel_export=excel_export_service,
        file_processing=file_processing_service,
        configuration=configuration_service,
        rich_output=rich_output,
    )
    
    nipper_expander_service = providers.Factory(
        "kp_analysis_toolkit.nipper_expander.service.NipperExpanderService",
        excel_export=excel_export_service,
        file_processing=file_processing_service,
        rich_output=rich_output,
    )
    
    rtf_to_text_service = providers.Factory(
        "kp_analysis_toolkit.rtf_to_text.service.RtfToTextService",
        file_processing=file_processing_service,
        rich_output=rich_output,
    )


# Global container instance
container = ApplicationContainer()


# Wiring configuration for dependency injection
def wire_container() -> None:
    """Wire the container for dependency injection."""
    container.wire(modules=[
        "kp_analysis_toolkit.cli",
        "kp_analysis_toolkit.process_scripts.cli",
        "kp_analysis_toolkit.nipper_expander.cli",
        "kp_analysis_toolkit.rtf_to_text.cli",
    ])


# Configuration helper
def configure_container(
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """Configure the container with runtime settings."""
    container.config.verbose.from_value(verbose)
    container.config.quiet.from_value(quiet)
    container.config.max_workers.from_value(max_workers or 4)
```

## Implementation Benefits

### 1. **Explicit Dependencies**
- Clear what each class needs to function
- Easier to test and mock
- Type-safe dependency relationships

### 2. **No Global State**  
- Each context is isolated
- Concurrent operations don't interfere
- Easier parallel processing

### 3. **Flexible Configuration**
- Different contexts can have different settings
- Easy to create specialized configurations
- Runtime reconfiguration possible

### 4. **Better Testing**
- Easy to inject mocks and stubs
- Isolated test environments
- No global state cleanup needed

### 5. **Future-Proof Architecture**
- Easy to add new dependencies
- Clean separation of concerns
- Scalable for larger applications

### 6. **Framework Benefits (dependency-injector)**
- Lazy initialization of components
- Automatic lifecycle management
- Built-in configuration management
- Excellent type safety and IDE support
- Production-ready performance optimization

## Complete CLI Integration Example

### Updated Main CLI with DI Framework

```python
# src/kp_analysis_toolkit/cli.py (complete DI integration)
from __future__ import annotations

import platform
import sys
from collections.abc import Callable
from pathlib import Path

import rich_click as click
from dependency_injector.wiring import Provide, inject

from kp_analysis_toolkit import __version__ as cli_version
from kp_analysis_toolkit.core.containers.application import container, configure_container, wire_container
from kp_analysis_toolkit.process_scripts.service import ProcessScriptsService
from kp_analysis_toolkit.rtf_to_text.service import RtfToTextService
from kp_analysis_toolkit.utils.rich_output import RichOutput
from kp_analysis_toolkit.utils.version_checker import check_and_prompt_update

# Initialize DI container
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
    service: ProcessScriptsService = Provide[container.process_scripts_service],
    rich_output: RichOutput = Provide[container.rich_output],
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
    service: NipperExpanderService = Provide[container.nipper_expander_service],
    rich_output: RichOutput = Provide[container.rich_output],
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
    service: RtfToTextService = Provide[container.rtf_to_text_service],
    rich_output: RichOutput = Provide[container.rich_output],
) -> None:
    """Convert RTF files to text format."""
    try:
        rich_output.header("RTF to Text Module")
        service.execute()
    except Exception as e:
        rich_output.error(f"Error in rtf to text: {e}")
        raise
```

### Module Service Implementations

```python
# src/kp_analysis_toolkit/process_scripts/service.py
from __future__ import annotations

from kp_analysis_toolkit.core.services.configuration import ConfigurationService
from kp_analysis_toolkit.core.services.excel_export import ExcelExportService
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.parallel_processing import ParallelProcessingService
from kp_analysis_toolkit.core.services.search_engine import SearchEngineService
from kp_analysis_toolkit.core.services.system_detection import SystemDetectionService
from kp_analysis_toolkit.utils.rich_output import RichOutput


class ProcessScriptsService:
    """Main service for process scripts module."""
    
    def __init__(
        self,
        search_engine: SearchEngineService,
        parallel_processing: ParallelProcessingService,
        system_detection: SystemDetectionService,
        excel_export: ExcelExportService,
        file_processing: FileProcessingService,
        configuration: ConfigurationService,
        rich_output: RichOutput,
    ) -> None:
        self.search_engine = search_engine
        self.parallel_processing = parallel_processing
        self.system_detection = system_detection
        self.excel_export = excel_export
        self.file_processing = file_processing
        self.configuration = configuration
        self.rich_output = rich_output
    
    def execute(self) -> None:
        """Execute the process scripts workflow."""
        # Use injected services for all operations
        self.rich_output.info("Starting process scripts execution")
        
        # Load configuration
        config = self.configuration.load_configuration("config.yml")
        
        # Process systems
        systems = self.system_detection.detect_systems_from_files(config['source_files'])
        
        # Execute searches
        results = self.search_engine.execute_searches(config['searches'], systems)
        
        # Export results
        self.excel_export.export_results(results, config['output_file'])
        
        self.rich_output.success("Process scripts completed successfully")


# src/kp_analysis_toolkit/nipper_expander/service.py
class NipperExpanderService:
    """Main service for nipper expander module."""
    
    def __init__(
        self,
        excel_export: ExcelExportService,
        file_processing: FileProcessingService,
        rich_output: RichOutput,
    ) -> None:
        self.excel_export = excel_export
        self.file_processing = file_processing
        self.rich_output = rich_output
    
    def execute(self) -> None:
        """Execute the nipper expander workflow."""
        self.rich_output.info("Starting nipper expander execution")
        # Implementation with injected services
        self.rich_output.success("Nipper expander completed successfully")


# src/kp_analysis_toolkit/rtf_to_text/service.py  
class RtfToTextService:
    """Main service for RTF to text module."""
    
    def __init__(
        self,
        file_processing: FileProcessingService,
        rich_output: RichOutput,
    ) -> None:
        self.file_processing = file_processing
        self.rich_output = rich_output
    
    def execute(self) -> None:
        """Execute the RTF to text workflow."""
        self.rich_output.info("Starting RTF to text conversion")
        # Implementation with injected services
        self.rich_output.success("RTF to text conversion completed successfully")
```

## Testing Strategy with Hierarchical DI Framework

### 1. Container-Based Testing

```python
# tests/conftest.py
import pytest
from dependency_injector import providers

from kp_analysis_toolkit.core.containers.application import ApplicationContainer
from kp_analysis_toolkit.core.containers.core import CoreContainer
from kp_analysis_toolkit.process_scripts.container import ProcessScriptsContainer


@pytest.fixture
def core_container():
    """Provide a test core container."""
    container = CoreContainer()
    container.config.verbose.from_value(True)
    container.config.quiet.from_value(False)
    container.config.max_workers.from_value(1)
    return container


@pytest.fixture
def process_scripts_container(core_container):
    """Provide a test process scripts container."""
    container = ProcessScriptsContainer()
    container.core.override(core_container)
    return container


@pytest.fixture
def application_container():
    """Provide a complete test application container."""
    container = ApplicationContainer()
    
    # Override with test configuration
    container.core.config.verbose.from_value(True)
    container.core.config.quiet.from_value(False)
    container.core.config.max_workers.from_value(1)
    
    return container


@pytest.fixture
def mock_services(application_container):
    """Provide mocked services for testing."""
    from unittest.mock import Mock
    
    # Override specific services with mocks
    mock_file_processing = Mock()
    mock_search_engine = Mock()
    
    application_container.file_processing.file_processing_service.override(
        providers.Object(mock_file_processing)
    )
    application_container.process_scripts.search_engine_service.override(
        providers.Object(mock_search_engine)
    )
    
    yield {
        'file_processing': mock_file_processing,
        'search_engine': mock_search_engine,
    }
    
    # Reset overrides
    application_container.file_processing.file_processing_service.reset_override()
    application_container.process_scripts.search_engine_service.reset_override()
```

### 2. Individual Container Testing

```python
# tests/core/containers/test_core_container.py
import pytest

from kp_analysis_toolkit.core.containers.core import CoreContainer


def test_core_container_configuration():
    """Test core container configuration."""
    container = CoreContainer()
    container.config.verbose.from_value(True)
    container.config.quiet.from_value(False)
    
    rich_output = container.rich_output()
    assert rich_output.verbose is True
    assert rich_output.quiet is False


# tests/core/containers/test_file_processing_container.py
def test_file_processing_container(core_container):
    """Test file processing container."""
    from kp_analysis_toolkit.core.containers.file_processing import FileProcessingContainer
    
    container = FileProcessingContainer()
    container.core.override(core_container)
    
    service = container.file_processing_service()
    assert service.rich_output is not None
    assert service.encoding_detector is not None


# tests/process_scripts/test_container.py
def test_process_scripts_container(core_container):
    """Test process scripts container."""
    from kp_analysis_toolkit.process_scripts.container import ProcessScriptsContainer
    
    container = ProcessScriptsContainer()
    container.core.override(core_container)
    
    # Test module-specific services
    system_detection = container.system_detection_service()
    search_engine = container.search_engine_service()
    
    assert system_detection.rich_output is not None
    assert search_engine.rich_output is not None
```

### 3. Integration Testing with Hierarchical Containers

```python
# tests/integration/test_hierarchical_di.py
def test_full_hierarchical_integration(application_container):
    """Test full hierarchical dependency injection integration."""
    
    # Test core services
    rich_output = application_container.core.rich_output()
    assert rich_output is not None
    
    # Test shared services
    file_processing = application_container.file_processing.file_processing_service()
    excel_export = application_container.excel_export.excel_export_service()
    
    # Test module services
    process_scripts_service = application_container.process_scripts.process_scripts_service()
    nipper_service = application_container.nipper_expander.nipper_expander_service()
    
    # Test that shared services are properly injected
    assert file_processing.rich_output is rich_output
    assert excel_export.rich_output is rich_output
    assert process_scripts_service.rich_output is rich_output
    assert nipper_service.rich_output is rich_output


def test_container_isolation():
    """Test that different containers are properly isolated."""
    container1 = ApplicationContainer()
    container2 = ApplicationContainer()
    
    container1.core.config.verbose.from_value(True)
    container2.core.config.verbose.from_value(False)
    
    service1 = container1.process_scripts.process_scripts_service()
    service2 = container2.process_scripts.process_scripts_service()
    
    assert service1.rich_output.verbose is True
    assert service2.rich_output.verbose is False
    assert service1 is not service2
```

### 4. Module-Specific Testing

```python
# tests/process_scripts/test_service.py
def test_process_scripts_service_with_mocks():
    """Test process scripts service with mocked dependencies."""
    from unittest.mock import Mock
    from kp_analysis_toolkit.process_scripts.service import ProcessScriptsService
    
    # Mock all dependencies
    mock_search_engine = Mock()
    mock_parallel_processing = Mock()
    mock_system_detection = Mock()
    mock_excel_export = Mock()
    mock_file_processing = Mock()
    mock_configuration = Mock()
    mock_rich_output = Mock()
    
    service = ProcessScriptsService(
        search_engine=mock_search_engine,
        parallel_processing=mock_parallel_processing,
        system_detection=mock_system_detection,
        excel_export=mock_excel_export,
        file_processing=mock_file_processing,
        configuration=mock_configuration,
        rich_output=mock_rich_output,
    )
    
    # Test service functionality
    service.execute()
    
    # Verify mocks were called
    mock_rich_output.info.assert_called()
    mock_configuration.load_configuration.assert_called()
```

## Migration Checklist (Hierarchical Approach)

### Phase 1: Core Infrastructure ✓
- [ ] Install `dependency-injector` package
- [ ] Create `src/kp_analysis_toolkit/core/containers/core.py`
- [ ] Create `src/kp_analysis_toolkit/core/containers/file_processing.py`
- [ ] Create `src/kp_analysis_toolkit/core/containers/configuration.py`
- [ ] Create `src/kp_analysis_toolkit/core/containers/excel_export.py`
- [ ] Create `src/kp_analysis_toolkit/core/containers/application.py`
- [ ] Update main CLI with hierarchical container initialization
- [ ] Create basic test infrastructure

### Phase 2: Core Service Containers ✓
- [ ] Implement CoreContainer with RichOutput
- [ ] Implement FileProcessingContainer with encoding/hash/validation
- [ ] Implement ConfigurationContainer with YAML processing
- [ ] Implement ExcelExportContainer with formatting/tables
- [ ] Create service interface protocols
- [ ] Update related utilities and tests

### Phase 3: Module-Specific Containers ✓
- [ ] Create `src/kp_analysis_toolkit/process_scripts/container.py`
- [ ] Create `src/kp_analysis_toolkit/nipper_expander/container.py`
- [ ] Create `src/kp_analysis_toolkit/rtf_to_text/container.py`
- [ ] Implement ProcessScriptsContainer with system detection, search engine, parallel processing
- [ ] Implement NipperExpanderContainer with module services
- [ ] Implement RtfToTextContainer with module services
- [ ] Create module service implementations

### Phase 4: Integration and Wiring ✓
- [ ] Complete ApplicationContainer with all container wiring
- [ ] Update CLI commands to use hierarchical container paths
- [ ] Test container hierarchy and dependency relationships
- [ ] Update all injection decorators
- [ ] Verify module isolation and shared service access

### Phase 5: Testing & Documentation ✓
- [ ] Unit tests for each individual container
- [ ] Integration tests with hierarchical container structure
- [ ] Module-specific service testing
- [ ] Performance testing with hierarchical DI
- [ ] Update architecture documentation
- [ ] Create container organization guide
- [ ] Remove deprecated global functions
- [ ] Update migration documentation

## Architecture Benefits of Hierarchical Approach

### 1. **Modular Design**
- Each container has a single, clear responsibility
- Services are organized by domain and usage patterns
- Easy to understand and maintain container boundaries

### 2. **Improved Performance**
- Only necessary services are loaded per module
- Lazy initialization at the container level
- Reduced memory footprint for single-module usage

### 3. **Better Testing**
- Individual containers can be tested in isolation
- Easy to mock dependencies at the container level
- Clear test boundaries and responsibilities

### 4. **Team Development**
- Different teams can work on different containers
- Changes to one module don't affect others
- Clear ownership and maintenance boundaries

### 5. **Deployment Flexibility**
- Potential for future module splitting
- Clear service boundaries for microservice evolution
- Container-level configuration and overrides

## Expected Performance Impact

### Memory Usage
- **Slightly Higher**: Service instances instead of global singletons
- **More Predictable**: Clear lifecycle management
- **Better Isolation**: No shared state between contexts

### CPU Performance
- **Minimal Overhead**: `dependency-injector` is optimized for production
- **Lazy Loading**: Services created only when needed
- **Better Parallelization**: No global locks or shared state

### Development Velocity
- **Faster Testing**: Easy mocking and isolation
- **Cleaner Code**: Explicit dependencies
- **Better Debugging**: Clear dependency chains
- **Easier Maintenance**: Modular, testable architecture
