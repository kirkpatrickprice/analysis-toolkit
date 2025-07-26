# Process Scripts DI Migration Plan

## Executive Summary

This document outlines the migration plan to fully integrate the `process_scripts` module into the existing Dependency Injection (DI) architecture. The migration will transform the current functional-based implementation into a service-oriented architecture that leverages existing core services and extends the core `ExcelExportService` for process scripts' unique Excel export requirements.

**Migration Goals:**
- Migrate all process scripts functionality to DI-based services
- Extend core Excel export capabilities for complex multi-sheet requirements  
- **AGGRESSIVE REMOVAL STRATEGY**: Immediately delete legacy implementations upon completion of DI replacement
- Force complete migration by eliminating backward compatibility paths after service implementation
- Establish service boundaries for YAML configuration, search engine, and system detection
- Create enhanced Excel export services that build upon core capabilities

## Current State Assessment

### ✅ **Partially Implemented (Phase 1)**
- **Container Structure**: Process scripts container exists with partial service definitions
- **Service Interfaces**: Basic service classes exist but need full implementation
- **Enhanced Excel Service**: Stub implementation exists, needs full functionality
- **CLI Integration**: Currently bypasses DI services, uses legacy functions directly

### ❌ **Not Yet Migrated**
- **YAML Configuration Loading**: Still uses standalone functions (`load_search_configs`, `process_includes`)
- **Search Engine Execution**: Still uses standalone functions (`execute_search`, `execute_all_searches`)
- **System Detection**: Still uses standalone functions (`enumerate_systems_from_source_files`)
- **Excel Export**: Complex multi-sheet export still uses legacy `excel_exporter.py`
- **CLI Command Integration**: CLI still calls legacy functions directly

### 🔍 **Migration Complexity Factors**
- **Multi-OS Support**: Windows, Linux, macOS with different search configurations
- **Complex Excel Output**: Multi-sheet workbooks with conditional formatting, metadata, and summary sheets
- **YAML Include Processing**: Recursive file inclusion with inheritance patterns
- **Parallel Processing**: Search execution across multiple systems and configurations
- **Legacy Integration**: Extensive existing test coverage and user workflows to preserve

---

## Proposed Directory Structure for `process_scripts`

```
src/kp_analysis_toolkit/process_scripts/
├── __init__.py                           # Module initialization
├── container.py                          # DI container configuration
├── service.py                           # Main ProcessScriptsService
│
├── models/                              # Pydantic data models
│   ├── __init__.py
│   ├── search/                          # Search configuration models
│   │   ├── __init__.py
│   │   ├── configs.py                   # SearchConfig, YamlConfig, GlobalConfig models
│   │   ├── filters.py                   # SystemFilter models
│   │   └── merge_fields.py              # MergeFieldConfig models
│   │
│   ├── program_config.py                # Standard ProgramConfig (following RTF/Nipper pattern)
│   │
│   ├── results/                         # Result models
│   │   ├── __init__.py
│   │   ├── search_results.py            # SearchResults, SearchResult models
│   │   ├── system_results.py            # Systems, SystemInfo models
│   │   └── workflow.py                  # ProcessScriptsResult model
│   │
│   └── types/                           # Type definitions and enums
│       ├── __init__.py
│       ├── os_types.py                  # OSFamilyType, DistroType enums
│       └── producer_types.py            # ProducerType enums
│
├── services/                            # Core services
│   ├── __init__.py
│   ├── search_config/                   # Search configuration service
│   │   ├── __init__.py
│   │   ├── service.py                   # SearchConfigService
│   │   ├── protocols.py                 # YamlParser, FileResolver, IncludeProcessor
│   │   ├── yaml_parser.py               # PyYamlParser implementation
│   │   ├── file_resolver.py             # StandardFileResolver implementation
│   │   └── include_processor.py         # StandardIncludeProcessor implementation
│   │
│   ├── system_detection/                # System detection service
│   │   ├── __init__.py
│   │   ├── service.py                   # SystemDetectionService
│   │   ├── protocols.py                 # OSDetector, ProducerDetector protocols
│   │   ├── os_detection.py              # RegexOSDetector implementation
│   │   ├── producer_detection.py        # ProducerDetector implementation
│   │   └── distro_classification.py     # DistroClassifier implementation
│   │
│   ├── search_engine/                   # Search engine service
│   │   ├── __init__.py
│   │   ├── service.py                   # SearchEngineService
│   │   ├── protocols.py                 # PatternCompiler, FieldExtractor, ResultProcessor
│   │   ├── pattern_compiler.py          # RegexPatternCompiler implementation
│   │   ├── field_extractor.py           # StandardFieldExtractor implementation
│   │   └── result_processor.py          # StandardResultProcessor implementation
│   │
│   └── enhanced_excel_export/           # Enhanced Excel export service
│       ├── __init__.py
│       ├── service.py                   # EnhancedExcelExportService
│       ├── protocols.py                 # WorksheetBuilder, Formatter, Validator protocols
│       ├── worksheet_builder.py         # AdvancedWorksheetBuilder implementation
│       ├── formatters.py                # MultiSheetFormatter, ConditionalFormattingEngine
│       └── validators.py                # DataValidationEngine implementation

tests/unit/process_scripts/              # Unit tests (mirrors source structure)
├── __init__.py
├── test_container.py                    # Container configuration tests
├── test_service.py                      # Main service tests
│
├── models/
│   ├── test_search_configs.py
│   ├── test_program_workflow.py
│   ├── test_system_results.py
│   └── test_workflow_results.py
│
├── services/
│   ├── test_search_config/              # Search config service tests
│   │   ├── test_service.py
│   │   ├── test_yaml_parser.py
│   │   ├── test_file_resolver.py
│   │   └── test_include_processor.py
│   │
│   ├── test_system_detection/           # System detection service tests
│   │   ├── test_service.py
│   │   ├── test_os_detection.py
│   │   ├── test_producer_detection.py
│   │   └── test_distro_classification.py
│   │
│   ├── test_search_engine/              # Search engine service tests
│   │   ├── test_service.py
│   │   ├── test_pattern_compiler.py
│   │   ├── test_field_extractor.py
│   │   └── test_result_processor.py
│   │
│   └── test_enhanced_excel_export/      # Enhanced Excel export tests
│       ├── test_service.py
│       ├── test_worksheet_builder.py
│       ├── test_formatters.py
│       └── test_validators.py

tests/integration/process_scripts/       # Integration tests
├── __init__.py
├── test_full_workflow.py                # End-to-end workflow testing
├── test_service_integration.py          # Service interaction testing
├── test_excel_export_integration.py     # Excel export integration testing
└── test_cli_integration.py              # CLI command integration testing

testdata/process_scripts/                # Test data (mirrors existing structure)
├── configs/                             # Test YAML configurations
│   ├── sample_audit_config.yaml
│   ├── with_includes/
│   └── edge_cases/
│
├── systems/                             # Test system files
│   ├── windows/
│   ├── linux/
│   └── macos/
│
└── expected_results/                    # Expected output files
    ├── excel_exports/
    └── search_results/
```

### Key Design Principles

#### **Service Layer Organization (Following Core Pattern)**

- **`services/<service_name>/`**: Each service has its own directory containing service, protocols, and implementations
- **Co-located Protocols**: Protocols are defined alongside their service implementations for better cohesion
- **Consistent Structure**: Follows the established pattern in `core/services` for architectural consistency
- **Clear Boundaries**: Each service directory encapsulates all related functionality
- **Core Service Reuse**: Leverages existing `core.file_processing`, `core.excel_export`, and other core services

#### **Service Directory Structure**

Each service follows this consistent pattern:

- **`service.py`**: Main service class implementation
- **`protocols.py`**: Protocol definitions for dependency injection
- **`*_implementation.py`**: Concrete implementations of protocols
- **`__init__.py`**: Public API exports

#### **Core Service Integration Strategy**

- **Core Application Container**: The `process_scripts/container.py` module configures the local container while also providing an integration point for `core/containers/application.py` to tie into the larger toolkit.  Reference [DI Command Pattern](docs/architecture/di-command-pattern.md) for additional details
- **File Operations**: Use `core.file_processing.FileProcessingService` for all file system operations
- **Excel Operations**: Build upon `core.excel_export.ExcelExportService` for enhanced Excel functionality
- **Parallel Processing**: Use `core.parallel_processing.ParallelProcessingService` for concurrent operations
- **Output Management**: Use `core.rich_output.RichOutputService` for all user feedback
- **Legacy Elimination**: Immediately remove legacy implementations to force DI adoption

#### **Model Organization**
- **`models/search/`**: Search configuration models that define regex patterns, field extraction, and search behavior
- **`models/program_config.py`**: Standard program configuration following RTF/Nipper pattern for CLI arguments and processing options
- **`models/results/`**: Result and output data models
- **`models/types/`**: Enums and type definitions

#### **Detailed Model Organization Rationale**

The revised model structure maintains consistency with other toolkit modules while properly separating search domain models from program configuration:

**Search Configuration Models (`models/search/`)**
- **Purpose**: Define how individual searches are executed against system files
- **Scope**: Search-specific behavior, regex patterns, field extraction rules, system filters
- **Used By**: `SearchConfigService`, `SearchEngineService`
- **Examples**: 
  - `SearchConfig` - Individual search definition with regex, field extraction, limits
  - `YamlConfig` - Complete YAML file structure with multiple search configurations
  - `SystemFilter` - Criteria for limiting which systems a search applies to
  - `MergeFieldConfig` - Rules for combining multiple source columns into destination columns

**Program Configuration Model (`models/program_config.py`)**
- **Purpose**: Define CLI arguments, file paths, and processing options (same as RTF/Nipper modules)
- **Scope**: Standard program configuration including input/output paths, operation modes, verbosity
- **Used By**: `ProcessScriptsService`, CLI commands, same as other modules
- **Examples**:
  - `ProgramConfig` - Standard configuration with audit_config_file, source_files_path, results_path, verbose flags
  - No additional workflow or CLI adapter models needed

**Key Benefits of This Simplified Organization**:

1. **Architectural Consistency**: Follows same `ProgramConfig` pattern as RTF-to-Text and Nipper Expander
2. **Clear Responsibility Boundaries**: Search models only care about search execution, program config only cares about CLI/file concerns
3. **Reduced Complexity**: Single program configuration model reduces maintenance overhead  
4. **Reusable Patterns**: Developers already understand this pattern from other modules
5. **Service Integration**: Services accept standard `ProgramConfig` directly without additional adapters

#### **Model File Contents**

**Search Configuration Models (`models/search/`)**
```python
# configs.py - Core search configuration models
class SearchConfig(KPATBaseModel):
    """Configuration for a single search operation."""
    name: str
    regex: str
    comment: str | None = None
    excel_sheet_name: str
    max_results: int = -1
    field_list: list[str] | None = None
    # ... other search-specific fields

class YamlConfig(KPATBaseModel):
    """Complete YAML configuration file structure."""
    global_config: GlobalConfig | None = None
    search_configs: dict[str, SearchConfig]
    include_configs: dict[str, IncludeConfig]

# filters.py - System filtering models  
class SystemFilter(KPATBaseModel):
    """System filter configuration for limiting search applicability."""
    attr: SysFilterAttr
    comp: SysFilterComparisonOperators
    value: SysFilterValueType

# merge_fields.py - Field merging configuration
class MergeFieldConfig(KPATBaseModel):
    """Configuration for merging multiple source columns into a single destination column."""
    source_columns: list[str]
    dest_column: str
```

**Program Configuration Model (`models/program_config.py`)**
```python
# program_config.py - Standard program configuration following RTF/Nipper pattern
class ProgramConfig(KPATBaseModel):
    """Standard program configuration for process scripts (following RTF/Nipper pattern)."""
    # Core paths and files
    program_path: Path = Path(__file__).parent.parent
    audit_config_file: Path | None = None
    source_files_path: Path | None = None
    source_files_spec: str = "*.txt"
    
    # Output configuration
    out_path: str = "./results"
    
    # Operation modes (CLI flags)
    list_audit_configs: bool = False
    list_sections: bool = False  
    list_source_files: bool = False
    list_systems: bool = False
    verbose: bool = False
    
    @computed_field
    def results_path(self) -> Path:
        """Generate results output path with timestamp."""
        return Path(self.out_path) / f"results-{get_timestamp()}"
```

#### **Enhanced Excel Export Structure**
- **`services/enhanced_excel_export/`**: Dedicated service following core pattern
- Separates concerns: export service, worksheet building, formatting, validation
- Builds upon core `ExcelExportService` while adding process scripts-specific features

#### **Legacy Removal Strategy**
- **IMMEDIATE DELETION**: Legacy functions are deleted immediately after DI service implementation is complete
- **NO BACKWARD COMPATIBILITY**: Remove legacy function calls completely to force adoption of DI services
- **AGGRESSIVE TIMELINE**: Each legacy implementation must be completely removed within the same phase as service implementation
- **FORCED MIGRATION**: By removing legacy code immediately, all consumers must use the new DI services
- **COMPREHENSIVE REMOVAL**: Delete both implementation files and function calls throughout the codebase

#### **Testing Structure**
- **Unit tests**: Mirror source structure with service-specific test directories
- **Integration tests**: Focus on service interactions and workflows
- **Test data**: Organized by type with realistic samples

#### **Advantages of Following Core Pattern**

`process_scripts` is the most complicated tool currently in the Toolkit and there's a temptation account for this by implementing unique patterns.  Strict adherence to established patterns will lead to more maintainable code in the future, including:

- **Architectural Consistency**: Aligns with existing `core/services` structure
- **Developer Familiarity**: Team already understands this pattern
- **Protocol Co-location**: Protocols and implementations stay together for better maintainability
- **Service Encapsulation**: Each service directory is self-contained
- **Easier Navigation**: Related files are grouped together logically
- **Core Service Leverage**: Reuses proven core services instead of duplicating functionality
- **Reduced Coupling**: Eliminates shared utility dependencies between services

## Improved Model Organization Summary

The revised model organization follows established toolkit patterns while maintaining proper separation between search domain and program configuration concerns:

### **Search Domain Models (`models/search/`)**
- **`configs.py`**: SearchConfig, YamlConfig, GlobalConfig - Define what and how to search
- **`filters.py`**: SystemFilter - Define which systems searches apply to  
- **`merge_fields.py`**: MergeFieldConfig - Define how to combine search result fields
- **Consumed by**: SearchConfigService, SearchEngineService
- **Purpose**: Everything related to defining and configuring individual search operations

### **Program Configuration Model (`models/program_config.py`)**  
- **`ProgramConfig`**: Standard program configuration following RTF/Nipper pattern
- **Consumed by**: ProcessScriptsService, CLI commands
- **Purpose**: CLI arguments, file paths, processing options - same pattern as other modules

### **Key Architectural Benefits**

1. **Domain Separation**: Search configuration concerns are completely separate from program execution concerns
2. **Consistent Architecture**: Follows same `ProgramConfig` pattern as RTF-to-Text and Nipper Expander modules  
3. **Simplified Testing**: Reuses established testing patterns from other modules
4. **Reduced Complexity**: Single configuration model reduces maintenance overhead
5. **Service Alignment**: Services accept standard `ProgramConfig` directly without additional adapters

This organization maintains architectural consistency with other toolkit modules while properly separating search domain models from program configuration concerns.

---

## Phase 1: Service Implementation Foundation

### 1.1 Complete Search Configuration Service Implementation

#### Current State
- `SearchConfigService` class exists but has placeholder implementation
- YAML parsing logic exists in `search_engine.py` functions
- Include processing logic needs service extraction

#### Required Actions

**A. Implement Service Protocols**
```python
# File: src/kp_analysis_toolkit/process_scripts/services/search_config/protocols.py

class YamlParser(Protocol):
    """Protocol for YAML parsing operations."""
    
    def load_yaml(self, file_path: Path) -> dict[str, Any]: ...
    def validate_yaml_structure(self, data: dict[str, Any]) -> bool: ...

class FileResolver(Protocol):
    """Protocol for resolving file paths and includes."""
    
    def resolve_config_path(self, base_path: Path, config_name: str) -> Path: ...
    def find_include_files(self, config_dir: Path, pattern: str) -> list[Path]: ...

class IncludeProcessor(Protocol):
    """Protocol for processing YAML includes."""
    
    def process_includes(
        self, 
        yaml_config: YamlConfig, 
        base_path: Path
    ) -> list[SearchConfig]: ...
```

**B. Create Concrete Implementations**
```python
# File: src/kp_analysis_toolkit/process_scripts/services/search_config/yaml_parser.py

class PyYamlParser:
    """Standard YAML parser using PyYAML."""
    
    def load_yaml(self, file_path: Path) -> dict[str, Any]:
        """Load and parse YAML file."""
        # Implementation from current load_yaml_config function

# File: src/kp_analysis_toolkit/process_scripts/services/search_config/file_resolver.py

class StandardFileResolver:
    """Standard file resolver for YAML configurations."""
    
    def __init__(self, file_processing: FileProcessingService) -> None:
        """Initialize with core file processing service."""
        self.file_processing = file_processing
    
    def resolve_config_path(self, base_path: Path, config_name: str) -> Path:
        """Resolve configuration file path, checking conf.d directory."""
        # Use file_processing service for file system operations
        # Implementation from current config file resolution logic

# File: src/kp_analysis_toolkit/process_scripts/services/search_config/include_processor.py

class StandardIncludeProcessor:
    """Standard processor for YAML include directives."""
    
    def __init__(
        self, 
        yaml_parser: YamlParser, 
        file_resolver: FileResolver,
        file_processing: FileProcessingService
    ) -> None:
        """Initialize with injected dependencies including core file processing."""
        self.yaml_parser = yaml_parser
        self.file_resolver = file_resolver
        self.file_processing = file_processing
    
    def process_includes(
        self, 
        yaml_config: YamlConfig, 
        base_path: Path
    ) -> list[SearchConfig]:
        """Process include configurations recursively."""
        # Use file_processing service for file operations
        # Implementation from current process_includes function
        # Models imported from: kp_analysis_toolkit.process_scripts.models.search
```
```

**C. Complete SearchConfigService Implementation**
```python
# File: src/kp_analysis_toolkit/process_scripts/services/search_config/service.py

class SearchConfigService:
    """Service for loading and processing YAML search configurations."""
    
    def __init__(
        self,
        yaml_parser: YamlParser,
        file_resolver: FileResolver,
        include_processor: IncludeProcessor,
        file_processing: FileProcessingService,
        rich_output: RichOutputService,
    ) -> None:
        """Initialize with injected dependencies including core services."""
        self.yaml_parser = yaml_parser
        self.file_resolver = file_resolver
        self.include_processor = include_processor
        self.file_processing = file_processing
        self.rich_output = rich_output
    
    def load_search_configs(self, config_path: Path) -> list[SearchConfig]:
        """Load search configurations with full include processing."""
        # Full implementation using injected protocols and core services
        # Models imported from: kp_analysis_toolkit.process_scripts.models.search
        
    def validate_configurations(self, configs: list[SearchConfig]) -> list[str]:
        """Validate search configurations and return warnings/errors."""
        # Implementation from current validate_search_configs function
        
    def get_available_configs(self, config_dir: Path) -> list[Path]:
        """Get list of available configuration files."""
        # Use file_processing service for directory operations
```

#### Migration Steps
1. Extract YAML parsing logic from `search_engine.py` into service implementations
2. Move include processing logic into `StandardIncludeProcessor`
3. Update container configuration to use concrete implementations
4. Create unit tests for each service component
5. **IMMEDIATE REMOVAL**: Delete legacy functions in `search_engine.py` upon service completion
6. **Update all callers**: Find and replace all legacy function calls with DI service calls using:
   ```powershell
   # Search for legacy function calls
   Select-String -Path "src\**\*.py" -Pattern "load_search_configs|process_includes"
   ```

#### Expected Duration: 3-4 days

---

### 1.2 Complete System Detection Service Implementation

#### Current State
- `SystemDetectionService` class exists with basic structure
- System enumeration logic exists in `process_systems.py`
- OS detection, producer detection, and distro classification components defined in container

#### Required Actions

**A. Implement Core System Detection Service**
```python
# File: src/kp_analysis_toolkit/process_scripts/services/system_detection/service.py

class SystemDetectionService:
    """Service for detecting and analyzing system configuration files."""
    
    def __init__(
        self,
        os_detector: OSDetector,
        producer_detector: ProducerDetector,
        distro_classifier: DistroClassifier,
        file_processing: FileProcessingService,
        rich_output: RichOutputService,
    ) -> None:
        """Initialize with injected dependencies including core services."""
        self.os_detector = os_detector
        self.producer_detector = producer_detector
        self.distro_classifier = distro_classifier
        self.file_processing = file_processing
        self.rich_output = rich_output
    
    def enumerate_systems_from_files(
        self, 
        source_directory: Path,
        file_spec: str = "*.txt"
    ) -> list[Systems]:
        """Discover and analyze system files in source directory."""
        # Use file_processing service for file discovery and reading
        # Implementation from enumerate_systems_from_source_files
        
    def analyze_system_file(self, file_path: Path) -> Systems:
        """Analyze individual system file to extract system information."""
        # Use file_processing service for file reading and encoding detection
        # Implementation from current system analysis logic
        
    def filter_systems_by_criteria(
        self, 
        systems: list[Systems], 
        filters: list[SystemFilter] | None
    ) -> list[Systems]:
        """Filter systems based on system filter criteria."""
        # Implementation from current filter_systems_by_criteria function
        # SystemFilter imported from: kp_analysis_toolkit.process_scripts.models.search.filters
```
```

**B. Enhance OS/Producer Detection Components**
```python
# File: src/kp_analysis_toolkit/process_scripts/services/system_detection/os_detection.py

class RegexOSDetector:
    """OS detection using regex patterns."""
    
    def detect_os_family(self, content: str) -> OSFamilyType:
        """Detect OS family from system content."""
        # Enhanced implementation with better error handling

# File: src/kp_analysis_toolkit/process_scripts/services/system_detection/producer_detection.py

class SignatureProducerDetector:
    """Producer detection using signature patterns."""
    
    def detect_producer(self, content: str) -> ProducerType:
        """Detect system producer from content signatures."""
        # Enhanced implementation with confidence scoring
```

#### Migration Steps
1. Extract system enumeration logic from `process_systems.py` into service
2. Enhance OS/producer detection components with DI integration
3. **Use core `FileProcessingService`** for all file operations (reading, encoding detection, validation)
4. Add comprehensive error handling and logging through `RichOutputService`
5. Create unit tests with mock file systems
6. **IMMEDIATE REMOVAL**: Delete legacy functions in `process_systems.py` upon service completion
7. **Update all callers**: Find and replace all legacy function calls with DI service calls using:
   ```powershell
   # Search for legacy system processing function calls
   Select-String -Path "src\**\*.py" -Pattern "enumerate_systems_from_source_files|filter_systems_by_criteria"
   ```

#### Expected Duration: 3-4 days

---

### 1.3 Complete Search Engine Service Implementation

#### Current State
- `SearchEngineService` class stub exists in container
- Core search logic exists in `search_engine.py` functions
- Pattern compilation, field extraction, result processing components defined

#### Required Actions

**A. Implement Search Engine Core Service**
```python
# File: src/kp_analysis_toolkit/process_scripts/services/search_engine/service.py

class SearchEngineService:
    """Service for executing regex-based searches against system files."""
    
    def __init__(
        self,
        pattern_compiler: PatternCompiler,
        field_extractor: FieldExtractor,
        result_processor: ResultProcessor,
        parallel_processing: ParallelProcessingService,
        rich_output: RichOutputService,
    ) -> None:
        """Initialize with injected dependencies including core services."""
        self.pattern_compiler = pattern_compiler
        self.field_extractor = field_extractor
        self.result_processor = result_processor
        self.parallel_processing = parallel_processing
        self.rich_output = rich_output
    
    def execute_search(
        self, 
        search_config: SearchConfig, 
        systems: list[Systems]
    ) -> SearchResults:
        """Execute single search configuration against systems."""
        # Implementation from current execute_search function
        
    def execute_all_searches(
        self,
        search_configs: list[SearchConfig],
        systems: list[Systems]
    ) -> list[SearchResults]:
        """Execute all search configurations against systems."""
        # Implementation from current execute_all_searches function
        
    def execute_parallel_searches(
        self,
        search_configs: list[SearchConfig],
        systems: list[Systems],
        max_workers: int = 4
    ) -> list[SearchResults]:
        """Execute searches in parallel using core ParallelProcessingService."""
        # Use core parallel processing service instead of custom implementation
```

**B. Implement Search Engine Components**
```python
# File: src/kp_analysis_toolkit/process_scripts/services/search_engine/pattern_compiler.py

class RegexPatternCompiler:
    """Service for compiling and validating regex patterns."""
    
    def compile_pattern(self, regex: str, multiline: bool = False) -> re.Pattern:
        """Compile regex pattern with validation."""

# File: src/kp_analysis_toolkit/process_scripts/services/search_engine/field_extractor.py
        
class StandardFieldExtractor:
    """Service for extracting fields from regex matches."""
    
    def extract_fields(
        self, 
        match: re.Match, 
        field_list: list[str] | None
    ) -> dict[str, str]:
        """Extract named fields from regex match."""

# File: src/kp_analysis_toolkit/process_scripts/services/search_engine/result_processor.py
        
class StandardResultProcessor:
    """Service for processing and filtering search results."""
    
    def process_results(
        self, 
        raw_results: list[SearchResult], 
        search_config: SearchConfig
    ) -> list[SearchResult]:
        """Process results with deduplication, filtering, and limits."""
```

#### Migration Steps
1. Extract search execution logic from `search_engine.py` into service
2. **Use core `ParallelProcessingService`** for parallel search execution instead of custom implementation
3. Create comprehensive error handling for regex compilation and execution
4. Add progress reporting through `RichOutputService`
5. **IMMEDIATE REMOVAL**: Delete legacy search functions in `search_engine.py` upon service completion
6. **Update all callers**: Find and replace all legacy function calls with DI service calls using:
   ```powershell
   # Search for legacy search engine function calls
   Select-String -Path "src\**\*.py" -Pattern "execute_search|execute_all_searches"
   ```

#### Expected Duration: 4-5 days

---

## Phase 2: Enhanced Excel Export Service Implementation

### 2.1 Extend Core Excel Export Service

#### Current State
- Core `ExcelExportService` handles basic single-sheet exports with tables
- Process scripts needs multi-sheet workbooks with complex formatting
- Legacy `excel_exporter.py` contains 545 lines of complex Excel logic

#### Required Actions

**A. Analyze Core Service Extension Points**
Current core `ExcelExportService` provides:
- Basic DataFrame export with table formatting
- Title formatting and sheet name sanitization
- Column width adjustment and date formatting
- Simple table generation
- Foundation for building complex multi-sheet workbooks

**B. Create Enhanced Excel Export Service**
```python
# File: src/kp_analysis_toolkit/process_scripts/services/enhanced_excel_export/service.py

class EnhancedExcelExportService:
    """Enhanced Excel export service for complex process scripts requirements."""
    
    def __init__(
        self,
        base_excel_service: ExcelExportService,  # Core service
        worksheet_builder: AdvancedWorksheetBuilder,
        multi_sheet_formatter: MultiSheetFormatter,
        conditional_formatter: ConditionalFormattingEngine,
        data_validator: DataValidationEngine,
        rich_output: RichOutputService,  # Core service
    ) -> None:
        """Inject core services and enhanced components."""
        self.base_excel_service = base_excel_service
        self.worksheet_builder = worksheet_builder
        self.multi_sheet_formatter = multi_sheet_formatter
        self.conditional_formatter = conditional_formatter
        self.data_validator = data_validator
        self.rich_output = rich_output
        
    def export_search_results_workbook(
        self,
        search_results: list[SearchResults],
        output_path: Path,
        systems: list[Systems] | None = None,
        include_summary: bool = True,
    ) -> None:
        """Export search results to multi-sheet Excel workbook."""
        # Delegate basic operations to core ExcelExportService
        # Use enhanced components for complex multi-sheet features
        
    def export_systems_summary_workbook(
        self,
        systems: list[Systems],
        output_path: Path,
    ) -> None:
        """Export systems summary to Excel workbook."""
        # Build upon core service capabilities
        
    def create_os_specific_reports(
        self,
        search_results: list[SearchResults],
        systems: list[Systems],
        output_dir: Path,
    ) -> dict[str, Path]:
        """Create separate Excel reports for each OS type."""
        # Use core service for individual workbook creation
```

**C. Create Enhanced Excel Components**
```python
# File: src/kp_analysis_toolkit/process_scripts/services/enhanced_excel_export/worksheet_builder.py

class AdvancedWorksheetBuilder:
    """Service for building complex worksheets with metadata and comments."""
    
    def __init__(self, base_excel_service: ExcelExportService) -> None:
        """Initialize with core Excel service for basic operations."""
        self.base_excel_service = base_excel_service
    
    def create_search_results_sheet(
        self,
        worksheet: Worksheet,
        search_results: SearchResults,
        include_metadata: bool = True,
    ) -> None:
        """Build worksheet for search results with full formatting."""
        # Use core service for basic table creation
        # Add process scripts-specific metadata and comments
        
    def create_summary_sheet(
        self,
        worksheet: Worksheet,
        summary_data: list[dict],
        title: str = "Search Results Summary",
    ) -> None:
        """Build summary worksheet with overview data."""
        # Delegate to core service for basic formatting

# File: src/kp_analysis_toolkit/process_scripts/services/enhanced_excel_export/formatters.py

class MultiSheetFormatter:
    """Service for formatting multi-sheet workbooks."""
    
    def format_workbook(self, workbook: Workbook) -> None:
        """Apply consistent formatting across all sheets."""
        
    def organize_sheet_order(
        self, 
        workbook: Workbook, 
        priority_sheets: list[str]
    ) -> None:
        """Organize sheets in logical order (Summary first, etc.)."""

class ConditionalFormattingEngine:
    """Service for applying conditional formatting to Excel sheets."""
    
    def apply_result_count_formatting(self, worksheet: Worksheet) -> None:
        """Apply conditional formatting based on result counts."""
        
    def apply_system_status_formatting(self, worksheet: Worksheet) -> None:
        """Apply conditional formatting for system status indicators."""

# File: src/kp_analysis_toolkit/process_scripts/services/enhanced_excel_export/validators.py

class DataValidationEngine:
    """Service for data validation and Excel compatibility."""
    
    def sanitize_excel_data(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Sanitize DataFrame for Excel compatibility (illegal characters, etc.)."""
        
    def validate_sheet_names(self, sheet_names: list[str]) -> list[str]:
        """Validate and sanitize Excel sheet names."""
```

#### Migration Steps
1. **Analyze Legacy Excel Logic**: Map all functionality in `excel_exporter.py` to service components
2. **Build Upon Core Service**: Ensure enhanced service delegates basic operations to core `ExcelExportService`
3. **Create Enhanced Components**: Implement advanced worksheet builder and formatters as extensions
4. **Implement Multi-Sheet Logic**: Create workbook-level operations for complex exports
5. **Add Rich Output Integration**: Use core `RichOutputService` for progress reporting
6. **Create Comprehensive Tests**: Test complex workbook generation scenarios
7. **IMMEDIATE REMOVAL**: Delete entire `excel_exporter.py` file upon service completion
8. **Update all callers**: Find and replace all legacy Excel function calls with DI service calls using:
   ```powershell
   # Search for legacy Excel export function calls
   Select-String -Path "src\**\*.py" -Pattern "export_search_results_to_excel|export_systems_summary_to_excel|export_results_by_os_type"
   ```

#### Expected Duration: 5-6 days

---

### 2.2 Map Legacy Excel Functions to Enhanced Services

#### Required Mappings

| Legacy Function | Enhanced Service Method | Notes |
|---|---|---|
| `export_search_results_to_excel` | `export_search_results_workbook` | Main export function |
| `export_systems_summary_to_excel` | `export_systems_summary_workbook` | Systems summary export |
| `export_results_by_os_type` | `create_os_specific_reports` | OS-separated reports |
| `create_dataframe_from_results` | `AdvancedWorksheetBuilder.prepare_results_data` | Data preparation |
| `_create_results_sheet` | `AdvancedWorksheetBuilder.create_search_results_sheet` | Sheet creation |
| `_create_summary_sheet` | `AdvancedWorksheetBuilder.create_summary_sheet` | Summary creation |
| `_add_search_comment` | `AdvancedWorksheetBuilder.add_comment_section` | Comment formatting |
| `_add_search_metadata` | `AdvancedWorksheetBuilder.add_metadata_section` | Metadata display |

---

## Phase 3: Main Service Integration

### 3.1 Complete ProcessScriptsService Implementation

#### Current State
- `ProcessScriptsService` class exists with basic structure
- Needs full implementation using completed services from Phase 1 and 2

#### Required Actions

**A. Implement Main Orchestration Service**
```python
# File: src/kp_analysis_toolkit/process_scripts/service.py

class ProcessScriptsService:
    """Main orchestration service for the process scripts module."""
    
    def __init__(
        self,
        search_config: SearchConfigService,
        system_detection: SystemDetectionService,
        search_engine: SearchEngineService,
        excel_export: EnhancedExcelExportService,
        file_processing: FileProcessingService,  # Core service
        rich_output: RichOutputService,  # Core service
    ) -> None:
        """Initialize with all required services including core services."""
        self.search_config = search_config
        self.system_detection = system_detection
        self.search_engine = search_engine
        self.excel_export = excel_export
        self.file_processing = file_processing
        self.rich_output = rich_output
    
    def execute_workflow(
        self,
        program_config: ProgramConfig,
    ) -> ProcessScriptsResult:
        """Execute complete process scripts workflow using standard config."""
        # ProcessScriptsResult imported from: kp_analysis_toolkit.process_scripts.models.results.workflow
        
        try:
            # Validate inputs using core file processing service
            self.file_processing.validate_directory_exists(program_config.source_files_path)
            self.file_processing.validate_file_exists(program_config.audit_config_file)
            
            # Load search configurations
            search_configs = self.search_config.load_search_configs(program_config.audit_config_file)
            
            # Discover and analyze systems
            systems = self.system_detection.enumerate_systems_from_files(
                program_config.source_files_path, 
                program_config.source_files_spec
            )
            
            # Execute searches with default parallelism
            search_results = self.search_engine.execute_parallel_searches(
                search_configs, 
                systems
            )
            
            # Export results to program_config.results_path
            exported_files = self.excel_export.export_search_results_workbook(
                search_results, 
                systems, 
                program_config.results_path
            )
            
            return ProcessScriptsResult(
                execution_id=get_timestamp(),
                systems_processed=len(systems),
                searches_executed=len(search_configs),
                total_results=sum(r.result_count for r in search_results),
                exported_files=exported_files,
                execution_time=0.0,  # Calculate from start time
            )
            
        except Exception as e:
            self.rich_output.error(f"Process scripts workflow failed: {e}")
            raise
            
    def list_available_configs(self, config_directory: Path) -> list[Path]:
        """List available audit configuration files."""
        return self.search_config.get_available_configs(config_directory)
        
    def preview_systems(
        self, 
        input_directory: Path, 
        file_spec: str = "*.txt"
    ) -> list[Systems]:
        """Preview systems that would be processed."""
        return self.system_detection.enumerate_systems_from_files(
            input_directory, file_spec
        )
```

**B. Create Result Data Model**
```python
# File: src/kp_analysis_toolkit/process_scripts/models/results/workflow.py

class ProcessScriptsResult(KPATBaseModel):
    """Result of process scripts workflow execution."""
    
    systems_processed: int
    searches_executed: int
    total_results: int
    exported_files: dict[str, Path]
    execution_time: float
    success: bool
    errors: list[str] = []
```

#### Migration Steps
1. Implement complete workflow orchestration using all injected services
2. Add comprehensive error handling and rollback capabilities
3. Create rich progress reporting for all workflow stages
4. Implement result aggregation and summary reporting
5. Add validation for input parameters and configurations
6. **COMPLETE LEGACY REMOVAL**: After ProcessScriptsService is complete, remove ALL legacy process scripts functions:
   ```powershell
   # Find and remove all legacy process scripts function calls
   Select-String -Path "src\**\*.py" -Pattern "process_scipts_results" | ForEach-Object { Write-Host "Legacy call found: $($_.Line)" }
   ```

#### Expected Duration: 3-4 days

---

### 3.2 Update Container Configuration

#### Required Actions

**A. Complete Container Wiring**
```python
# File: src/kp_analysis_toolkit/process_scripts/container.py

# Update container to use fully implemented services with core service integration
process_scripts_service = providers.Factory(
    ProcessScriptsService,
    search_config=search_config_service,
    system_detection=system_detection_service,
    search_engine=search_engine_service,
    excel_export=enhanced_excel_export_service,
    file_processing=core.file_processing_service,  # Core service
    rich_output=core.rich_output,  # Core service
)
```

**B. Add Service Protocol Implementations with Core Service Dependencies**
```python
# Search config service with core dependencies
search_config_service = providers.Factory(
    SearchConfigService,
    yaml_parser=yaml_parser,
    file_resolver=file_resolver,
    include_processor=include_processor,
    file_processing=core.file_processing_service,  # Core service
    rich_output=core.rich_output,  # Core service
)

# System detection service with core dependencies
system_detection_service = providers.Factory(
    SystemDetectionService,
    os_detector=os_detector,
    producer_detector=producer_detector,
    distro_classifier=distro_classifier,
    file_processing=core.file_processing_service,  # Core service
    rich_output=core.rich_output,  # Core service
)

# Search engine service with core dependencies
search_engine_service = providers.Factory(
    SearchEngineService,
    pattern_compiler=pattern_compiler,
    field_extractor=field_extractor,
    result_processor=result_processor,
    parallel_processing=core.parallel_processing_service,  # Core service
    rich_output=core.rich_output,  # Core service
)

# Enhanced Excel components with core dependencies
enhanced_excel_export_service = providers.Factory(
    EnhancedExcelExportService,
    base_excel_service=core.excel_export_service,  # Core service
    worksheet_builder=advanced_worksheet_builder,
    multi_sheet_formatter=multi_sheet_formatter,
    conditional_formatter=conditional_formatting_engine,
    data_validator=data_validation_engine,
    rich_output=core.rich_output,  # Core service
)

advanced_worksheet_builder = providers.Factory(
    AdvancedWorksheetBuilder,
    base_excel_service=core.excel_export_service,  # Core service
)

# File resolver with core dependencies
file_resolver = providers.Factory(
    StandardFileResolver,
    file_processing=core.file_processing_service,  # Core service
)

# Include processor with core dependencies
include_processor = providers.Factory(
    StandardIncludeProcessor,
    yaml_parser=yaml_parser,
    file_resolver=file_resolver,
    file_processing=core.file_processing_service,  # Core service
)
```

#### Expected Duration: 1-2 days

---

## Phase 4: CLI Integration and Legacy Function Updates

### 4.1 Update CLI Command to Use DI Services

#### Current State
- CLI directly calls legacy functions (`process_scipts_results`, `load_search_configs`, etc.)
- Needs to be updated to use `ProcessScriptsService` through DI container

#### Required Actions

**A. Update CLI Command Function**
```python
# File: src/kp_analysis_toolkit/cli/commands/scripts.py

# Update imports to follow established pattern
from dependency_injector.wiring import Provide, inject
from kp_analysis_toolkit.core.containers.application import ApplicationContainer
from kp_analysis_toolkit.process_scripts.service import ProcessScriptsService

@custom_help_option("scripts")
@click.command(name="scripts")
@module_version_option(process_scripts_version, "scripts")
@start_directory_option()
@output_directory_option()
@verbose_option()
@click.option(
    "audit_config_file",
    "--conf",
    "-c", 
    default="audit-all.yaml",
    help="Default: audit-all.yaml. Provide a YAML configuration file to specify the options."
)
@click.option(
    "source_files_spec",
    "--filespec",
    "-f",
    default="*.txt", 
    help="Default: *.txt. Specify the file specification to match. This can be a glob pattern."
)
@click.option("--list-audit-configs", help="List all available audit configuration files and then exit", is_flag=True)
@click.option("--list-sections", help="List all sections headers found in FILESPEC and then exit", is_flag=True)
@click.option("--list-source-files", help="List all files found in FILESPEC and then exit", is_flag=True)
@click.option("--list-systems", help="Print system details found in FILESPEC and then exit", is_flag=True)
@inject
def process_command_line(
    **cli_config: dict[str, Any],
    process_scripts_service: ProcessScriptsService = Provide[
        ApplicationContainer.process_scripts.process_scripts_service
    ],
    rich_output: RichOutputService = Provide[ApplicationContainer.core.rich_output],
) -> None:
    """Process collector script results files (formerly adv-searchfor)."""
    try:
        program_config = validate_program_config(ProgramConfig, **cli_config)
    except ValueError as e:
        handle_fatal_error(e, error_prefix="Configuration validation failed")

    # Handle list operations
    if program_config.list_audit_configs:
        list_audit_configs(program_config, process_scripts_service, rich_output)
        return
    if program_config.list_sections:
        list_sections(rich_output)
        return  
    if program_config.list_source_files:
        list_source_files(program_config, process_scripts_service, rich_output)
        return
    if program_config.list_systems:
        list_systems(program_config, process_scripts_service, rich_output)
        return

    # Execute main processing workflow
    process_scipts_results(program_config, process_scripts_service, rich_output)


def process_scipts_results(
    program_config: ProgramConfig, 
    process_scripts_service: ProcessScriptsService,
    rich_output: RichOutputService,
) -> None:
    """Process the source files and execute searches using DI services."""
    try:
        # Execute workflow using injected service
        result = process_scripts_service.execute_workflow(program_config)
        
        # Display results summary
        rich_output.success(f"Processed {result.systems_processed} systems")
        rich_output.success(f"Executed {result.searches_executed} searches")
        rich_output.success(f"Found {result.total_results} total results")
        
    except Exception as e:
        rich_output.error(f"Process scripts execution failed: {e}")
        raise
```

**B. Update List Functions to Use Services**
```python
def list_audit_configs(
    program_config: ProgramConfig, 
    process_scripts_service: ProcessScriptsService,
    rich_output: RichOutputService,
) -> None:
    """List all available audit configuration files using DI service."""
    configs = process_scripts_service.list_available_configs(program_config.config_path)
    # Display logic remains the same - use injected rich_output

def list_systems(
    program_config: ProgramConfig, 
    process_scripts_service: ProcessScriptsService,
    rich_output: RichOutputService,
) -> None:
    """List all systems found using DI service."""
    systems = process_scripts_service.preview_systems(
        program_config.source_files_path,
        program_config.source_files_spec
    )
    # Display logic remains the same - use injected rich_output

def list_sections(rich_output: RichOutputService) -> None:
    """List all sections found in the specified source files."""
    rich_output.info("Listing sections... (feature not yet implemented)")

def list_source_files(
    program_config: ProgramConfig,
    process_scripts_service: ProcessScriptsService, 
    rich_output: RichOutputService,
) -> None:
    """List all source files found in the specified path."""
    # Use process_scripts_service for file discovery and rich_output for display
    # Implementation details remain the same, but use injected services
```

#### Migration Steps
1. **Update imports**: Replace `from kp_analysis_toolkit.core.containers.application import container` with `from kp_analysis_toolkit.core.containers.application import ApplicationContainer`
2. **Add dependency injection**: Add `@inject` decorator and use `Provide[ApplicationContainer.process_scripts.service]` pattern
3. **Update function signatures**: Pass services through dependency injection instead of manual container access
4. **Follow established pattern**: Use same pattern as `nipper.py` and `rtf_to_text.py` CLI commands
5. **Maintain exact same user interface**: All CLI options and output formatting remain identical
6. **Update error handling**: Use injected `rich_output` service instead of manual container access
7. **Test all CLI commands thoroughly**: Ensure identical behavior with new DI pattern
8. **VERIFY LEGACY REMOVAL**: Ensure no CLI functions call legacy process scripts functions:
   ```powershell
   # Verify CLI uses only DI services and follows established patterns
   Select-String -Path "src\kp_analysis_toolkit\cli\**\*.py" -Pattern "container\..*\(\)" | ForEach-Object { Write-Host "Old container pattern found: $($_.Line)" }
   Select-String -Path "src\kp_analysis_toolkit\cli\**\*.py" -Pattern "load_search_configs|execute_search|export.*excel" | ForEach-Object { Write-Host "Legacy CLI call found: $($_.Line)" }
   ```

#### Expected Duration: 2-3 days

---

### 4.2 Complete Legacy Code Removal

#### Required Actions

**A. Delete Legacy Implementation Files**
```powershell
# Remove legacy implementation files completely
Remove-Item "src\kp_analysis_toolkit\process_scripts\search_engine.py" -Force
Remove-Item "src\kp_analysis_toolkit\process_scripts\excel_exporter.py" -Force  
Remove-Item "src\kp_analysis_toolkit\process_scripts\process_systems.py" -Force

# Verify removal
Get-ChildItem "src\kp_analysis_toolkit\process_scripts\" -Name "*.py" | Where-Object { $_ -match "(search_engine|excel_exporter|process_systems)" }
```

**B. Update All Import Statements**
```powershell
# Find all imports of legacy modules
Select-String -Path "src\**\*.py" -Pattern "from.*process_scripts.*(search_engine|excel_exporter|process_systems)|import.*(search_engine|excel_exporter|process_systems)"

# These must all be updated to use DI container services instead
```

**C. Remove Legacy Function Calls Throughout Codebase**
```powershell
# Search for any remaining legacy function calls
Select-String -Path "src\**\*.py" -Pattern "load_search_configs|execute_search|execute_all_searches|enumerate_systems_from_source_files|export_search_results_to_excel|export_systems_summary_to_excel|process_scipts_results"

# Each found occurrence must be replaced with DI service calls
```

**D. Update Test Files**
```powershell
# Find test files that import or test legacy functions
Select-String -Path "tests\**\*.py" -Pattern "search_engine|excel_exporter|process_systems"

# These tests must be updated to test DI services instead
```

#### Migration Steps
1. **Complete service implementation** for all process scripts functionality
2. **Update all callers** to use DI services through container
3. **Delete legacy files** immediately after service completion
4. **Remove all imports** of deleted legacy modules
5. **Update all tests** to use DI services instead of legacy functions
6. **Verify complete removal** using PowerShell searches above

#### Expected Duration: 2-3 days

---

## Phase 5: Testing and Validation

### 5.1 Comprehensive Testing Strategy

#### Unit Tests
- **Service Tests**: Test each service in isolation with mocked dependencies
- **Component Tests**: Test Excel export components with sample data
- **Integration Tests**: Test service interactions within process scripts module
- **Protocol Tests**: Verify all implementations satisfy their protocols

#### Integration Tests
- **End-to-End Workflow**: Test complete workflow from config loading to Excel export
- **Multi-OS Processing**: Test with Windows, Linux, and macOS sample data
- **Large Dataset Testing**: Test with extensive system files and configurations
- **Error Handling**: Test failure scenarios and recovery

#### Regression Tests
- **CLI Compatibility**: Ensure all CLI commands produce identical results
- **Excel Output Validation**: Compare Excel outputs with legacy implementation
- **Performance Benchmarks**: Ensure DI implementation doesn't degrade performance
- **Memory Usage**: Monitor memory consumption with large datasets

### 5.2 Migration Validation Checklist

#### Functional Validation
- [ ] All CLI commands produce identical outputs
- [ ] Excel exports contain all legacy features (tables, formatting, metadata)
- [ ] YAML configuration loading handles all edge cases
- [ ] System detection accuracy matches legacy implementation
- [ ] Search execution produces identical results
- [ ] Error messages and user feedback remain consistent
- [ ] **COMPLETE LEGACY REMOVAL**: No legacy function calls remain in codebase:
  ```powershell
  # Verify complete legacy removal
  $legacyPatterns = @("load_search_configs", "execute_search", "execute_all_searches", "enumerate_systems_from_source_files", "export_search_results_to_excel", "export_systems_summary_to_excel", "process_scipts_results")
  foreach ($pattern in $legacyPatterns) {
      $results = Select-String -Path "src\**\*.py" -Pattern $pattern
      if ($results) { Write-Host "ERROR: Legacy calls still found for $pattern" }
  }
  ```

#### Performance Validation
- [ ] Processing time for large datasets within acceptable range
- [ ] Memory usage doesn't exceed legacy implementation
- [ ] Parallel processing effectiveness maintained
- [ ] Excel export speed comparable to legacy

#### Integration Validation
- [ ] All existing test cases pass
- [ ] **NO BACKWARD COMPATIBILITY**: All legacy function calls have been completely removed
- [ ] Container wiring resolves all dependencies
- [ ] Service protocols satisfied by implementations
- [ ] **COMPLETE FILE REMOVAL**: Legacy implementation files no longer exist:
  ```powershell
  # Verify legacy files are completely removed
  $legacyFiles = @("search_engine.py", "excel_exporter.py", "process_systems.py")
  foreach ($file in $legacyFiles) {
      if (Test-Path "src\kp_analysis_toolkit\process_scripts\$file") {
          Write-Host "ERROR: Legacy file still exists: $file"
      }
  }
  ```

#### Expected Duration: 4-5 days

---

## Risk Assessment and Mitigation

### High-Risk Areas

#### Complex Excel Export Logic
**Risk**: Excel export has 545 lines of complex logic with subtle formatting requirements
**Mitigation**: 
- Phase-by-phase testing with Excel output comparison
- Implement enhanced service as wrapper around legacy logic initially
- **AGGRESSIVE REMOVAL**: Delete legacy Excel exporter immediately after enhanced service is complete and tested

#### YAML Configuration Edge Cases
**Risk**: YAML include processing has recursive dependencies and error handling
**Mitigation**:
- Comprehensive test coverage for include scenarios
- Validate with all existing configuration files
- **FORCED MIGRATION**: Remove legacy YAML functions immediately to force DI adoption

#### Legacy Dependency Removal
**Risk**: Removing legacy code immediately could break existing functionality
**Mitigation**:
- **COMPREHENSIVE TESTING**: Ensure all functionality works with DI services before legacy removal
- **IMMEDIATE REPLACEMENT**: Update all callers to use DI services in the same commit as legacy removal
- **VERIFICATION SCRIPTS**: Use PowerShell scripts to verify complete legacy removal

### Medium-Risk Areas

#### Container Configuration Complexity
**Risk**: Complex dependency graph could lead to wiring issues
**Mitigation**:
- Incremental container testing
- Clear documentation of service dependencies
- Container validation tests

#### Multi-OS Testing Requirements
**Risk**: Process scripts supports Windows, Linux, macOS with different behaviors
**Mitigation**:
- Platform-specific test suites
- Mock system file generation for testing
- Continuous integration testing on multiple platforms

---

## Implementation Timeline

### Overall Timeline: 4-5 weeks

#### Week 1: Service Foundation (Phase 1)
- **Days 1-2**: Search Configuration Service implementation
- **Days 3-4**: System Detection Service implementation  
- **Days 5**: Search Engine Service implementation

#### Week 2: Excel Export Enhancement (Phase 2)
- **Days 1-3**: Enhanced Excel Export Service implementation
- **Days 4-5**: Advanced Excel components (worksheet builder, formatters)

#### Week 3: Main Service Integration and Legacy Removal (Phase 3 & 4)
- **Days 1-2**: ProcessScriptsService complete implementation
- **Days 3**: Container configuration completion
- **Days 4-5**: CLI integration and **COMPLETE LEGACY CODE REMOVAL**

#### Week 4: Testing and Validation (Phase 5)
- **Days 1-2**: Unit and integration testing
- **Days 3-4**: Regression testing and validation
- **Days 5**: Performance testing and optimization

#### Week 5: Final Integration and Documentation
- **Days 1-2**: Final testing and bug fixes
- **Days 3**: Documentation updates
- **Days 4-5**: Code review and deployment preparation

---

## Success Criteria

### Technical Success Metrics
- [ ] All process scripts functionality migrated to DI services
- [ ] **ZERO BACKWARD COMPATIBILITY**: All legacy functions completely removed
- [ ] All existing tests pass with DI services only
- [ ] Performance within 5% of legacy implementation
- [ ] Memory usage not exceeding legacy implementation
- [ ] **COMPLETE LEGACY REMOVAL VERIFICATION**:
  ```powershell
  # Final verification that no legacy code remains
  $verification = @{
      "Legacy files" = Get-ChildItem "src\kp_analysis_toolkit\process_scripts\" -Name "*.py" | Where-Object { $_ -match "(search_engine|excel_exporter|process_systems)" }
      "Legacy imports" = Select-String -Path "src\**\*.py" -Pattern "from.*process_scripts.*(search_engine|excel_exporter|process_systems)" 
      "Legacy calls" = Select-String -Path "src\**\*.py" -Pattern "load_search_configs|execute_search|export.*excel"
  }
  $verification.GetEnumerator() | ForEach-Object { 
      if ($_.Value) { Write-Host "FAIL: $($_.Key) found" } 
      else { Write-Host "PASS: No $($_.Key) found" }
  }
  ```

### Architectural Success Metrics
- [ ] Clean service boundaries with well-defined protocols
- [ ] Core Excel export service successfully extended
- [ ] Container properly configured with appropriate provider types
- [ ] Service dependencies clearly documented and testable

### User Experience Success Metrics
- [ ] CLI commands produce identical outputs
- [ ] Error messages remain clear and helpful
- [ ] Excel exports contain all expected features and formatting
- [ ] Processing time acceptable for typical workloads

---

## Conclusion

This migration plan provides a comprehensive roadmap for integrating the `process_scripts` module into the existing DI architecture. The phased approach ensures minimal risk while delivering significant architectural improvements. The plan leverages existing core services while extending them appropriately for process scripts' unique requirements.

Key benefits of this migration:
- **Improved Testability**: Service-based architecture enables better unit testing
- **Enhanced Maintainability**: Clear service boundaries and dependency injection
- **Core Service Leverage**: Reuses proven core services instead of duplicating functionality
- **Reduced Coupling**: Eliminates shared utility dependencies between services
- **Extended Core Services**: Excel export capabilities enhanced for complex scenarios
- **Complete Legacy Elimination**: Forced migration ensures no technical debt remains
- **Future Extensibility**: Service-oriented design enables future enhancements
- **Architectural Consistency**: Follows established patterns from core services
- **Aggressive Migration Strategy**: Immediate legacy removal prevents incomplete transitions

The migration balances architectural improvement with aggressive legacy removal, ensuring complete adoption of DI services and eliminating technical debt within the proposed timeline.
