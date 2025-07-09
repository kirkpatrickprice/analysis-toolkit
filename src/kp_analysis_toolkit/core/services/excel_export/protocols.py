from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path

    import openpyxl.worksheet.worksheet
    import pandas as pd


class WorkbookEngine(Protocol):
    """Protocol for Excel workbook engines."""

    def create_writer(self, output_path: Path) -> pd.ExcelWriter: ...


class ExcelFormatter(Protocol):
    """Protocol for Excel formatting."""

    def format_worksheet(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        data: pd.DataFrame,
    ) -> None: ...


class TableGenerator(Protocol):
    """Protocol for Excel table generation."""

    def create_table(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        data: pd.DataFrame,
    ) -> None: ...


class SheetNameSanitizer(Protocol):
    def sanitize_sheet_name(self, name: str) -> str: ...


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
        startrow: int,
    ) -> None: ...


class RowHeightAdjuster(Protocol):
    def adjust_row_heights(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        df: pd.DataFrame,
        startrow: int,
    ) -> None: ...


class ExcelUtilities(Protocol):
    def get_column_letter(self, col_num: int) -> str: ...
    def set_table_alignment(
        self,
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        table_range: str,
    ) -> None: ...
