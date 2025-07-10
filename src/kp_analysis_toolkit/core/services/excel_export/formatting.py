"""Formatting utilities for Excel export."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import pandas as pd
from openpyxl.styles import Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo

from kp_analysis_toolkit.core.services.excel_export.protocols import (
    ColumnWidthAdjuster,
    DateFormatter,
    ExcelFormatter,
    RowHeightAdjuster,
    TableStyler,
)
from kp_analysis_toolkit.core.services.excel_export.sheet_management import (
    DefaultSheetNameSanitizer,
)

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet

    from kp_analysis_toolkit.models.types import DisplayableValue


class DefaultColumnWidthAdjuster(ColumnWidthAdjuster):
    """Default implementation for auto-adjusting column widths."""

    def auto_adjust_column_widths(self, worksheet: Worksheet, df: pd.DataFrame) -> None:
        for col_num, column_name in enumerate(df.columns, 1):
            column_letter: str = DefaultSheetNameSanitizer().get_column_letter(col_num)
            max_length: int = len(str(column_name))
            for value in df.iloc[:, col_num - 1]:
                if pd.notna(value):
                    length: int = len(str(value))
                    max_length = max(max_length, length)
            width: int = min(max(max_length + 2, 10), 50)
            worksheet.column_dimensions[column_letter].width = width


class DefaultDateFormatter(DateFormatter):
    """Default implementation for formatting date columns."""

    def __init__(self) -> None:
        self.DATE_PATTERNS: list[str] = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
        ]

    def _is_date_column(self, column_name: str, sample_values: pd.Series) -> bool:
        if "date" in column_name.lower() or "time" in column_name.lower():
            return True
        date_count = 0
        for value in sample_values:
            if self._is_date_value(value):
                date_count += 1
        return len(sample_values) > 0 and date_count >= len(sample_values) * 0.5

    def _is_date_value(self, value: DisplayableValue) -> bool:
        return value is not None and pd.notna(value) and self._parse_date(str(value))

    def _parse_date(self, value: str) -> datetime | None:
        for pattern in self.DATE_PATTERNS:
            try:
                return datetime.strptime(value, pattern)  # noqa: DTZ007
            except ValueError:
                continue
        return None

    def _is_valid_cell_value(self, value: DisplayableValue) -> bool:
        return value is not None and pd.notna(value)

    def format_date_columns(
        self,
        worksheet: Worksheet,
        df: pd.DataFrame,
        startrow: int = 1,
    ) -> None:
        for col_num, column_name in enumerate(df.columns, 1):
            column_letter: str = DefaultSheetNameSanitizer().get_column_letter(col_num)
            sample_values: pd.Series[Any] = df.iloc[:5, col_num - 1].dropna()
            if self._is_date_column(str(column_name), sample_values):
                for row_num in range(startrow + 1, startrow + len(df) + 1):
                    cell: str = f"{column_letter}{row_num}"
                    try:
                        value: DisplayableValue = worksheet[cell].value
                        if self._is_valid_cell_value(value):
                            parsed_date: datetime | None = self._parse_date(str(value))
                            if parsed_date:
                                worksheet[cell].value = parsed_date.strftime("%Y-%m-%d")

                                # Apply Excel date formatting
                                worksheet[cell].number_format = "yyyy-mm-dd"
                    except Exception:  # noqa: BLE001, S110
                        # Ignore errors and keep the original value
                        pass


class DefaultRowHeightAdjuster(RowHeightAdjuster):
    """Default implementation for adjusting row heights."""

    def adjust_row_heights(
        self,
        worksheet: Worksheet,
        df: pd.DataFrame,
        startrow: int = 1,
    ) -> None:
        worksheet.row_dimensions[startrow].height = 20
        for row_num in range(startrow + 1, startrow + len(df) + 1):
            max_lines = 1
            for col_num in range(1, len(df.columns) + 1):
                column_letter: str = DefaultSheetNameSanitizer().get_column_letter(
                    col_num,
                )
                cell_value: DisplayableValue = worksheet[
                    f"{column_letter}{row_num}"
                ].value
                if cell_value and isinstance(cell_value, str):
                    lines: int = cell_value.count("\n") + 1
                    max_lines: int = max(max_lines, lines)
            height: float = max(15, min(max_lines * 15, 100))
            worksheet.row_dimensions[row_num].height = height


class DefaultExcelFormatter(ExcelFormatter):
    """Default implementation for Excel table alignment and column width."""

    def set_table_alignment(self, worksheet: Worksheet, table_range: str) -> None:
        for row in worksheet[table_range]:
            for cell in row:
                cell.alignment = Alignment(
                    horizontal="left",
                    vertical="top",
                    wrap_text=True,
                )

    def auto_adjust_column_widths(self, worksheet: Worksheet, df: pd.DataFrame) -> None:
        DefaultColumnWidthAdjuster().auto_adjust_column_widths(worksheet, df)


class DefaultTableStyler(TableStyler):
    def apply_style(self, table: Table) -> None:
        style = TableStyleInfo(
            name="TableStyleMedium9",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        table.tableStyleInfo = style
