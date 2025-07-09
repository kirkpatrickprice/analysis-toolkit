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
