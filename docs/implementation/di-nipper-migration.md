# Nipper Expander Dependency Injection Migration Plan

## Overview

This document provides detailed migration recommendations for converting the Nipper Expander module from direct utility usage to Dependency Injection (DI) services. The migration follows Phase 3.2 of the [full DI migration](di-full-migration-plan.md) plan and applies the established command-level service patterns.

## Current Functionality Analysis

### Existing Process Flow

The current `process_nipper_csv()` function in `process_nipper.py` performs:

1. **CSV File Reading**: Direct pandas `read_csv()` usage
2. **Data Validation**: Column existence checking and NipperRowData validation  
3. **Data Expansion**: Split devices by line breaks and create expanded rows
4. **Excel Export**: Direct call to `export_dataframe_to_excel()` utility function
5. **Error Handling**: Basic exception handling with KeyError for missing columns

### Current Dependencies

```python
# Current imports and dependencies
import pandas as pd
from kp_analysis_toolkit.nipper_expander.models.nipper_row_data import NipperRowData
from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig
from kp_analysis_toolkit.utils.excel_utils import export_dataframe_to_excel  # ← DI Migration Target
```

### Key Processing Logic

- **Device Expansion**: Multi-line device strings are split into individual rows
- **Data Validation**: Uses Pydantic model (`NipperRowData`) for validation
- **Error Recovery**: Graceful handling of invalid device data
- **Excel Output**: Formatted Excel export with table styling

## Recommended DI Service Architecture

### Service Breakdown by Concern

Following the service-package-pattern, the Nipper Expander functionality should be broken down into these services:

#### 1. **CSV Processing Service** (Core Service)
**Responsibility**: CSV file reading, validation, and basic data processing

**Note**: The CSV processing functionality is implemented as a **core service** in `core/services/csv_processing/service.py` rather than a Nipper-specific service. This design allows CSV processing capabilities to be reused across multiple toolkit commands that need to process CSV files.

The core CSV processing service provides:
- File existence validation using the file processing service
- Automatic encoding detection for CSV files
- Enhanced error handling with Rich Output integration
- Column validation with descriptive error messages
- Complete CSV processing pipeline with validation

**Service Location**: `kp_analysis_toolkit.core.services.csv_processing.service.CSVProcessorService`
**Protocol Location**: `kp_analysis_toolkit.core.services.csv_processing.protocols.CSVProcessor`

#### 2. **Data Expansion Service** (`services/data_expander.py`)
**Responsibility**: Device expansion logic and row transformation

```python
class DataExpansionService:
    """Service for expanding multi-value data fields into separate rows."""
    
    def __init__(self, rich_output: RichOutputService) -> None:
        self.rich_output = rich_output
    
    def expand_device_rows(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Expand rows with multi-line device data into individual rows."""
        
    def validate_and_clean_devices(self, devices_str: str) -> list[str]:
        """Validate device data using NipperRowData model and return cleaned list."""
        
    def _split_devices(self, devices_str: str) -> list[str]:
        """Split device string by line breaks and clean whitespace."""
        
    def _create_expanded_row(
        self, 
        original_row: pd.Series, 
        device: str
    ) -> dict[str, Any]:
        """Create a new row for a single device."""
```

#### 3. **Nipper Export Service** (`services/nipper_exporter.py`)
**Responsibility**: Nipper-specific Excel export formatting and configuration

```python
class NipperExportService:
    """Service for Nipper-specific Excel export with custom formatting."""
    
    def __init__(
        self,
        excel_export: ExcelExportService,
        rich_output: RichOutputService,
    ) -> None:
        self.excel_export = excel_export
        self.rich_output = rich_output
    
    def export_nipper_results(
        self,
        data_frame: pd.DataFrame,
        output_path: Path,
        *,
        sheet_name: str = "Expanded Nipper",
        title: str = "Nipper Expanded Report - One row per device/finding",
    ) -> None:
        """Export Nipper results with standard formatting and styling."""
```

### Main Orchestration Service

#### **Nipper Expander Service** (`service.py`)
**Responsibility**: Orchestrate all Nipper processing operations

```python
class NipperExpanderService:
    """Main service for Nipper Expander module orchestration."""
    
    def __init__(
        self,
        csv_processor: CSVProcessor,
        data_expander: DataExpander, 
        nipper_exporter: NipperExporter,
        rich_output: RichOutputService,
        file_processing: FileProcessingService,
    ) -> None:
        self.csv_processor = csv_processor
        self.data_expander = data_expander
        self.nipper_exporter = nipper_exporter
        self.rich_output = rich_output
        self.file_processing = file_processing
    
    def process_nipper_csv(self, program_config: ProgramConfig) -> pd.DataFrame:
        """
        Process a Nipper CSV file by expanding rows with multiple devices.
        
        This method replaces the current process_nipper_csv() function
        and provides the same functionality through DI services.
        """
        
    def process_nipper_batch(
        self,
        input_files: list[Path],
        output_directory: Path,
    ) -> list[pd.DataFrame]:
        """Process multiple Nipper CSV files in batch."""
```

## Protocol Definitions

### Service Protocols (`protocols.py`)

```python
"""Protocol definitions for Nipper Expander services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path
    import pandas as pd
    from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig


### Service Protocols (`protocols.py`)

```python
"""Protocol definitions for Nipper Expander services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path
    import pandas as pd
    from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig
    from kp_analysis_toolkit.core.services.csv_processing.protocols import CSVProcessor


# Note: CSVProcessor protocol is imported from core services
# from kp_analysis_toolkit.core.services.csv_processing.protocols import CSVProcessor


class DataExpander(Protocol):
    """Protocol for data expansion operations."""
    
    def expand_device_rows(self, data_frame: pd.DataFrame) -> pd.DataFrame: ...
    def validate_and_clean_devices(self, devices_str: str) -> list[str]: ...


class NipperExporter(Protocol):
    """Protocol for Nipper-specific Excel export operations."""
    
    def export_nipper_results(
        self,
        data_frame: pd.DataFrame, 
        output_path: Path,
        *,
        sheet_name: str = "Expanded Nipper",
        title: str = "Nipper Expanded Report - One row per device/finding",
    ) -> None: ...


class NipperExpanderService(Protocol):
    """Protocol for the main Nipper Expander service orchestration."""
    
    def process_nipper_csv(self, program_config: ProgramConfig) -> pd.DataFrame: ...
    def process_nipper_batch(self, input_files: list[Path], output_directory: Path) -> list[pd.DataFrame]: ...
```

## Container Configuration

### Nipper Expander Container (`container.py`)

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

if TYPE_CHECKING:
    from kp_analysis_toolkit.nipper_expander.protocols import (
        CSVProcessor,
        DataExpander,
        NipperExporter,
        NipperExpanderService,
    )


class NipperExpanderContainer(containers.DeclarativeContainer):
    """Services specific to the Nipper Expander module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()

    # Note: CSV processing is provided by core services
    # Access through: core.csv_processor_service

    # Feature Services - Factory providers for stateless operations
    data_expander: providers.Factory[DataExpander] = providers.Factory(
        "kp_analysis_toolkit.nipper_expander.services.data_expander.DataExpansionService",
        rich_output=core.rich_output,
    )

    nipper_exporter: providers.Factory[NipperExporter] = providers.Factory(
        "kp_analysis_toolkit.nipper_expander.services.nipper_exporter.NipperExportService",
        excel_export=core.excel_export_service,
        rich_output=core.rich_output,
    )

    # Main Module Service - Factory provider for each processing operation
    nipper_expander_service: providers.Factory[NipperExpanderService] = providers.Factory(
        "kp_analysis_toolkit.nipper_expander.service.NipperExpanderService",
        csv_processor=core.csv_processor_service,  # Using core CSV processor service
        data_expander=data_expander,
        nipper_exporter=nipper_exporter,
        rich_output=core.rich_output,
        file_processing=core.file_processing_service,
    )


# Module's global container instance
container = NipperExpanderContainer()


def wire_nipper_expander_container() -> None:
    """
    Wire the Nipper Expander container for dependency injection.
    
    This function should be called when the Nipper Expander module is initialized
    to ensure all dependencies are properly wired for injection.
    
    Note: CSV processor wiring is handled by core services.
    """
    container.wire(
        modules=[
            "kp_analysis_toolkit.nipper_expander.service",
            "kp_analysis_toolkit.nipper_expander.services.data_expander", 
            "kp_analysis_toolkit.nipper_expander.services.nipper_exporter",
        ],
    )
```

## Core Service Integration Patterns

### Rich Output Service Usage

```python
# Progress reporting for CSV processing
self.rich_output.info(f"Reading CSV file: {file_path}")
with self.rich_output.progress() as progress:
    task = progress.add_task("Processing rows...", total=len(data_frame))
    for _, row in data_frame.iterrows():
        # Process row
        progress.advance(task)

# Data validation feedback
self.rich_output.success(f"Successfully validated {len(data_frame)} rows")
self.rich_output.warning(f"Found {invalid_count} rows with invalid device data")

# Error reporting
self.rich_output.error(f"Missing required column 'Devices' in CSV file")
```

### File Processing Service Usage

```python
# File validation before processing
if not self.file_processing.validate_file_exists(file_path):
    raise FileNotFoundError(f"CSV file not found: {file_path}")

# Encoding detection for CSV files
encoding = self.file_processing.detect_encoding(file_path)
self.rich_output.debug(f"Detected encoding: {encoding}")

# File metadata for auditing
file_hash = self.file_processing.generate_hash(file_path)
```

### CSV Processing Service Usage

```python
# Core CSV reading with data validation
data_frame = self.csv_processor.read_csv(
    file_path=csv_path,
    required_columns=['Devices', 'Type'],
    validation_rules={
        'Devices': lambda x: len(x.strip()) > 0,
        'Type': lambda x: x in ['Critical', 'High', 'Medium', 'Low']
    }
)

# Custom CSV writing with specific formatting
self.csv_processor.write_csv(
    data_frame=expanded_data_frame,
    output_path=expanded_csv_path,
    encoding='utf-8'
)
```

### Excel Export Service Usage

```python
# Standard Excel export with Nipper-specific formatting
self.excel_export.export_dataframe_to_excel(
    data_frame=expanded_data_frame,
    output_path=output_path,
    sheet_name="Expanded Nipper",
    title="Nipper Expanded Report - One row per device/finding",
    as_table=True,
)

# Log export success
self.rich_output.success(f"Exported {len(expanded_data_frame)} expanded rows to {output_path}")
```

## Migration Implementation Details

### Phase 1: Service Implementation (3-4 days)

1. **Create CSV Processor Service**
   - Migrate CSV reading logic with encoding detection
   - Add column validation with descriptive error messages
   - Integrate file processing service for validation and encoding

2. **Create Data Expansion Service**
   - Extract device splitting and validation logic
   - Maintain NipperRowData model integration
   - Add progress reporting for large datasets

3. **Create Nipper Export Service**
   - Wrap Excel export service with Nipper-specific defaults
   - Maintain existing sheet naming and title conventions
   - Add export validation and success reporting

### Phase 2: Main Service Implementation (2-3 days)

1. **Implement NipperExpanderService**
   - Orchestrate all feature services
   - Maintain exact functional compatibility with `process_nipper_csv()`
   - Add enhanced error handling and user feedback

2. **Add Batch Processing Support**
   - Implement `process_nipper_batch()` for multiple files
   - Use progress reporting for batch operations
   - Handle per-file errors gracefully

### Phase 3: Container and Integration (2-3 days)

1. **Configure DI Container**
   - Set up all service providers with proper dependencies
   - Configure container wiring for all modules

2. **Update Application Container**
   - Add NipperExpanderContainer to main application
   - Ensure proper dependency flow from core services

3. **CLI Integration** 
   - Update CLI command to use DI services
   - Remove direct `process_nipper_csv()` calls
   - Maintain all existing CLI options and behavior

### Phase 4: Testing and Validation (2-3 days)

1. **Unit Testing**
   - Test each service independently with mocked dependencies
   - Verify protocol compliance for all implementations
   - Test error handling scenarios

2. **Integration Testing**
   - End-to-end testing with real CSV files
   - Validate Excel output format and content
   - Performance testing with large datasets

3. **Regression Testing**
   - Ensure exact output compatibility with current implementation
   - Validate all CLI options work correctly
   - Test batch processing scenarios

## Error Handling Improvements

### Enhanced Error Reporting

```python
class CSVProcessorService:
    def validate_required_columns(self, data_frame: pd.DataFrame, required_columns: list[str]) -> None:
        """Enhanced column validation with detailed error reporting."""
        missing_columns = [col for col in required_columns if col not in data_frame.columns]
        
        if missing_columns:
            available_columns = ", ".join(data_frame.columns.tolist())
            error_msg = (
                f"Missing required columns: {missing_columns}. "
                f"Available columns: {available_columns}"
            )
            self.rich_output.error(error_msg)
            raise KeyError(error_msg)
        
        self.rich_output.success(f"Validated required columns: {required_columns}")
```

### Graceful Data Recovery

```python
class DataExpansionService:
    def validate_and_clean_devices(self, devices_str: str) -> list[str]:
        """Enhanced device validation with recovery strategies."""
        try:
            # Use NipperRowData for validation
            row_data = NipperRowData(devices=devices_str)
            cleaned_devices = row_data.devices
        except Exception as e:
            # Log validation error but continue processing
            self.rich_output.warning(f"Invalid device data encountered: {e}")
            cleaned_devices = ""
        
        devices = [d.strip() for d in cleaned_devices.splitlines() if d.strip()]
        
        if not devices:
            self.rich_output.debug("Empty or invalid device data, using empty list")
        
        return devices
```

## Performance Considerations

### Large Dataset Handling

```python
class NipperExpanderService:
    def process_nipper_csv(self, program_config: ProgramConfig) -> pd.DataFrame:
        """Process CSV with performance optimizations for large files."""
        self.rich_output.info(f"Processing Nipper CSV: {program_config.input_file}")
        
        # Read and validate CSV
        data_frame = self.csv_processor.process_csv_with_validation(
            program_config.input_file, 
            required_columns=["Devices"]
        )
        
        # Show dataset size for user awareness
        self.rich_output.info(f"Processing {len(data_frame)} rows for device expansion")
        
        # Expand data with progress reporting
        expanded_data_frame = self.data_expander.expand_device_rows(data_frame)
        
        # Report expansion results
        expansion_ratio = len(expanded_data_frame) / len(data_frame) if len(data_frame) > 0 else 0
        self.rich_output.success(
            f"Expanded {len(data_frame)} rows to {len(expanded_data_frame)} rows "
            f"(expansion ratio: {expansion_ratio:.2f}x)"
        )
        
        # Export results
        self.nipper_exporter.export_nipper_results(expanded_data_frame, program_config.output_file)
        
        return expanded_data_frame
```

### Memory Optimization

```python
class DataExpansionService:
    def expand_device_rows(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Memory-efficient device expansion for large datasets."""
        expanded_rows = []
        
        # Process in chunks for memory efficiency with large datasets
        chunk_size = 1000  # Process 1000 rows at a time
        
        with self.rich_output.progress() as progress:
            task = progress.add_task("Expanding device rows...", total=len(data_frame))
            
            for start_idx in range(0, len(data_frame), chunk_size):
                end_idx = min(start_idx + chunk_size, len(data_frame))
                chunk = data_frame.iloc[start_idx:end_idx]
                
                for _, row in chunk.iterrows():
                    devices = self.validate_and_clean_devices(row["Devices"])
                    
                    if len(devices) > 1:
                        for device in devices:
                            new_row = row.to_dict()
                            new_row["Devices"] = device
                            expanded_rows.append(new_row)
                    else:
                        row_dict = row.to_dict()
                        if devices:
                            row_dict["Devices"] = devices[0]
                        expanded_rows.append(row_dict)
                
                progress.advance(task, advance=len(chunk))
        
        return pd.DataFrame(expanded_rows)
```

## Public API Definition

### Module Exports (`__init__.py`)

```python
"""Nipper Expander module for processing CSV files with device expansion."""

from kp_analysis_toolkit.nipper_expander.protocols import (
    CSVProcessor,
    DataExpander,
    NipperExporter,
    NipperExpanderService,
)
from kp_analysis_toolkit.nipper_expander.service import NipperExpanderService as NipperExpanderServiceImpl

__version__ = "0.2.0"

__all__ = [
    "CSVProcessor",
    "DataExpander", 
    "NipperExporter",
    "NipperExpanderService",
    "NipperExpanderServiceImpl",
]

"""Change History
0.1    Initial version with direct utility functions
0.2.0  2025-01-14: Refactor to use Dependency Injection patterns
"""
```

## Migration Benefits

### Improved Maintainability

1. **Clear Separation of Concerns**: Each service has a single responsibility
2. **Enhanced Testability**: Protocol-based interfaces enable easy mocking
3. **Better Error Handling**: Centralized error reporting through Rich Output
4. **Performance Monitoring**: Built-in progress reporting and metrics

### Enhanced User Experience

1. **Better Progress Feedback**: Real-time progress bars for large files
2. **Detailed Error Messages**: Clear validation errors with suggested fixes
3. **Performance Insights**: Expansion ratios and processing statistics
4. **Consistent Output**: Standardized Excel formatting across the toolkit

### Future Extensibility

1. **Additional Export Formats**: Easy to add new export services
2. **Advanced Validation**: Extensible validation through protocol interfaces
3. **Batch Processing**: Built-in support for processing multiple files
4. **Custom Formatting**: Nipper-specific formatting can be easily customized

## Conclusion

This migration plan transforms the Nipper Expander from a single-function utility to a comprehensive, well-architected service-based system. The new architecture provides:

- **Functional Equivalence**: Exact same behavior as the current implementation
- **Enhanced Capabilities**: Better error handling, progress reporting, and batch processing
- **Improved Maintainability**: Clear service boundaries and dependency injection
- **Future Extensibility**: Easy to add new features and export formats
- **Consistent Patterns**: Follows established DI patterns from the toolkit

The migration follows the established patterns from the RTF to Text implementation while accommodating the more complex data processing requirements of the Nipper Expander module.