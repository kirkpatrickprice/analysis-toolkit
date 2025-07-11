"""Protocol classes for Excel export services."""

from pathlib import Path
from typing import Protocol

import openpyxl.worksheet.worksheet
import pandas as pd
from openpyxl.worksheet.table import Table


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


class TableStyler(Protocol):
    def apply_style(self, table: Table) -> None: ...

class TitleFormatter(Protocol):
    def apply_title_format(self, worksheet: openpyxl.worksheet.worksheet.Worksheet, title: str, row: int = 1, col: int = 1) -> None: ...
