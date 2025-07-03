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

## Architecture Details

Create a modular dependency injection system with clear separation of concerns:

### 1. Core Containers

Containers providing core services used throughout the application

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
```

#### Nipper Expander Containers

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
from kp_analysis_toolkit.utils.rich_output import RichOutput


class ProcessScriptsService:
    """Main service for the process scripts module."""
    
    def __init__(
        self,
        search_engine: SearchEngineService,
        parallel_processing: ParallelProcessingService,
        system_detection: SystemDetectionService,
        excel_export: ExcelExportService,
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
        """Export search results to Excel format."""
        # Implementation would format and export results
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


`python
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

### 4. Wiring and Configuration

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