from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd

    from kp_analysis_toolkit.core.services.excel_export.protocols import (
        ExcelFormatter,
        TableGenerator,
        WorkbookEngine,
    )
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService


class ExcelExportService:
    """Service for Excel export operations."""

    def __init__(
        self,
        workbook_engine: WorkbookEngine,
        formatter: ExcelFormatter,
        table_generator: TableGenerator,
        rich_output: RichOutputService,
    ) -> None:
        self.workbook_engine: WorkbookEngine = workbook_engine
        self.formatter: ExcelFormatter = formatter
        self.table_generator: TableGenerator = table_generator
        self.rich_output: RichOutputService = rich_output

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
