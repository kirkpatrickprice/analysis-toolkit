# Excel Utilities DI Migration Plan

## Overview

This document outlines the plan to migrate the capabilities of `excel_utils.py` into a dependency-injector-based service package, following the service package pattern established in the toolkit. The migration will include a backward compatibility layer, similar to the approach used for file processing utilities, to ensure a smooth transition for all toolkit modules.

## Goals
- Modularize Excel export and formatting logic into concern-specific, testable components
- Enable dependency injection for all Excel-related operations
- Maintain backward compatibility for existing imports and function calls
- Align with the service package architecture pattern for maintainability and scalability

## Service Package Structure

The new service package will be located at:
```
src/kp_analysis_toolkit/core/services/excel_export/
```

It will be organized as follows:
```
excel_export/
├── __init__.py
├── protocols.py
├── service.py                # Main orchestrator (public API)
├── sheet_management.py       # Sheet name sanitization, column letter utilities
├── formatting.py             # Column width, date formatting, row height, alignment
├── table_generation.py       # Table creation and styling
├── workbook_engine.py        # ExcelWriter and file output logic
```

## Concern-Specific Implementations

1. **Sheet Management** (`sheet_management.py`)
```python
class SheetNameSanitizer(SheetNameSanitizer):
    def sanitize_sheet_name(self, name: str) -> str: ...
    def get_column_letter(self, col_num: int) -> str: ...
```

2. **Formatting** (`formatting.py`)
```python
class ColumnWidthAdjuster(ColumnWidthAdjuster):
    def auto_adjust_column_widths(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
    ) -> None: ...

class DateFormatter(DateFormatter):
    def format_date_columns(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
        startrow: int = 1,
    ) -> None: ...

class RowHeightAdjuster(RowHeightAdjuster):
    def adjust_row_heights(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
        startrow: int = 1,
    ) -> None: ...

class ExcelFormatter(ExcelFormatter):
    def set_table_alignment(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        table_range: str,
    ) -> None: ...
    def auto_adjust_column_widths(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
    ) -> None: ...
```

3. **Table Generation** (`table_generation.py`)
```python
class TableGenerator(TableGenerator):
    def __init__(
        self,
        formatter: ExcelFormatter,
        date_formatter: DateFormatter,
        column_width_adjuster: ColumnWidthAdjuster,
        row_height_adjuster: RowHeightAdjuster,
    ) -> None: ...
    def format_as_excel_table(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
        startrow: int = 1,
    ) -> None: ...
```

4. **Workbook Engine** (`workbook_engine.py`)
```python
class WorkbookEngine(WorkbookEngine):
    def create_writer(self, output_path: Path) -> pd.ExcelWriter: ...
```

5. **Service Orchestrator** (`service.py`)
```python
class ExcelExportService(ExcelExportService):
    def __init__(
        self,
        sheet_name_sanitizer: SheetNameSanitizer,
        column_width_adjuster: ColumnWidthAdjuster,
        date_formatter: DateFormatter,
        row_height_adjuster: RowHeightAdjuster,
        excel_formatter: ExcelFormatter,
        table_generator: TableGenerator,
        workbook_engine: WorkbookEngine,
    ) -> None: ...
    def export_dataframe_to_excel(
        self,
        df: pd.DataFrame,
        output_path: Path,
        sheet_name: str = "Sheet1",
        title: str | None = None,
        *,
        as_table: bool = True,
    ) -> None: ...
```

## Protocols and Interfaces

All concern-specific classes will implement protocols defined in `protocols.py`. The orchestrator will depend on these protocols, not concrete implementations, for maximum flexibility and testability.

**Expected Protocol Classes and Method Signatures:**

```python
from typing import Protocol
from pathlib import Path
import pandas as pd
import openpyxl.worksheet.worksheet

class SheetNameSanitizer(Protocol):
    def sanitize_sheet_name(self, name: str) -> str: ...
    def get_column_letter(self, col_num: int) -> str: ...

class ColumnWidthAdjuster(Protocol):
    def auto_adjust_column_widths(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
    ) -> None: ...

class DateFormatter(Protocol):
    def format_date_columns(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
        startrow: int = 1,
    ) -> None: ...

class RowHeightAdjuster(Protocol):
    def adjust_row_heights(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
        startrow: int = 1,
    ) -> None: ...

class ExcelFormatter(Protocol):
    def set_table_alignment(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        table_range: str,
    ) -> None: ...
    def auto_adjust_column_widths(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
    ) -> None: ...

class TableGenerator(Protocol):
    def format_as_excel_table(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
        startrow: int = 1,
    ) -> None: ...

class WorkbookEngine(Protocol):
    def create_writer(self, output_path: Path) -> pd.ExcelWriter: ...

class ExcelExportService(Protocol):
    def export_dataframe_to_excel(
        self,
        df: pd.DataFrame,
        output_path: Path,
        sheet_name: str = "Sheet1",
        title: str | None = None,
        *,
        as_table: bool = True,
    ) -> None: ...
```

These protocols ensure that each feature area is independently testable and swappable, and that the orchestrator can coordinate all Excel export operations via dependency injection.

## Backward Compatibility Layer
- The original `excel_utils.py` will be retained as a thin compatibility layer
- Each function (e.g., `export_dataframe_to_excel`, `sanitize_sheet_name`, etc.) will delegate to the DI-based service via the application container
- This allows gradual migration of toolkit modules to the new service without breaking existing code
- Example pattern:
  ```python
  from kp_analysis_toolkit.core.containers.application import container
  def export_dataframe_to_excel(...):
      service = container.excel_export().excel_export_service()
      return service.export_dataframe(...)
  ```

## Migration Steps
1. Define/expand protocols in `protocols.py` for all concern areas
2. Move each function from `excel_utils.py` to the appropriate concern-specific file, refactoring as class methods
3. Implement the orchestrator in `service.py` to coordinate all features
4. Update the DI container to provide all concern-specific implementations and the orchestrator
5. Implement the backward compatibility layer in `excel_utils.py`
6. Add/expand tests for each concern and the orchestrator
7. Document the new service and update usage examples

## Summary Table: Function Mapping
| excel_utils.py Function         | New Location (Class/Module)         |
|---------------------------------|-------------------------------------|
| sanitize_sheet_name             | sheet_management.py (SheetNameSanitizer) |
| get_column_letter               | sheet_management.py (SheetNameSanitizer/ExcelUtilities) |
| auto_adjust_column_widths       | formatting.py (ColumnWidthAdjuster/ExcelFormatter) |
| format_date_columns             | formatting.py (DateFormatter)       |
| set_table_alignment             | formatting.py (ExcelFormatter)      |
| adjust_row_heights              | formatting.py (RowHeightAdjuster)   |
| format_as_excel_table           | table_generation.py (TableGenerator)|
| export_dataframe_to_excel       | service.py (ExcelExportService)     |

## Testing and Validation
- Each concern-specific implementation will have its own unit tests
- The orchestrator will have integration tests
- The compatibility layer will be tested to ensure no regressions for existing imports

## Review and Approval
- This plan is intended for review prior to implementation
- Feedback on structure, naming, and migration steps is welcome
