"""Service definition for dependency-injector implementation of Excel export functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd

    from kp_analysis_toolkit.core.services.excel_export.protocols import (
        ColumnWidthAdjuster,
        DateFormatter,
        ExcelFormatter,
        RowHeightAdjuster,
        SheetNameSanitizer,
        TableGenerator,
        WorkbookEngine,
    )


class ExcelExportService:
    """Service for all Excel export operations."""

    def __init__(  # noqa: PLR0913
        self,
        sheet_name_sanitizer: SheetNameSanitizer,
        column_width_adjuster: ColumnWidthAdjuster,
        date_formatter: DateFormatter,
        row_height_adjuster: RowHeightAdjuster,
        excel_formatter: ExcelFormatter,
        table_generator: TableGenerator,
        workbook_engine: WorkbookEngine,
    ) -> None:
        """
        Initialize the Excel export service.

        Args:
            sheet_name_sanitizer: Service for sanitizing and validating sheet names
            column_width_adjuster: Service for adjusting column widths
            date_formatter: Service for formatting date columns
            row_height_adjuster: Service for adjusting row heights
            excel_formatter: Service for table alignment and formatting
            table_generator: Service for creating and styling Excel tables
            workbook_engine: Service for creating Excel writers and managing output

        """
        self.sheet_name_sanitizer = sheet_name_sanitizer
        self.column_width_adjuster = column_width_adjuster
        self.date_formatter = date_formatter
        self.row_height_adjuster = row_height_adjuster
        self.excel_formatter = excel_formatter
        self.table_generator = table_generator
        self.workbook_engine = workbook_engine

    def export_dataframe_to_excel(
        self,
        df: pd.DataFrame,
        output_path: Path,
        sheet_name: str = "Sheet1",
        title: str | None = None,
        *,
        as_table: bool = True,
    ) -> None:
        """
        Export a DataFrame to an Excel file with formatting and optional table styling.

        Args:
            df: The DataFrame to export
            output_path: Path to the output Excel file
            sheet_name: Name of the worksheet (default: "Sheet1")
            title: Optional title to add to the worksheet
            as_table: Whether to format the data as an Excel table (default: True)

        """
        sanitized_sheet_name = self.sheet_name_sanitizer.sanitize_sheet_name(sheet_name)
        with self.workbook_engine.create_writer(output_path) as writer:
            df.to_excel(
                writer,
                sheet_name=sanitized_sheet_name,
                index=False,
                startrow=1 if title else 0,
            )
            worksheet = writer.sheets[sanitized_sheet_name]

            if title:
                worksheet.cell(row=1, column=1, value=title)
                # Optionally apply title formatting here

            if as_table:
                self.table_generator.format_as_excel_table(
                    worksheet,
                    df,
                    startrow=2 if title else 1,
                )

            self.column_width_adjuster.auto_adjust_column_widths(worksheet, df)
            self.date_formatter.format_date_columns(
                worksheet,
                df,
                startrow=2 if title else 1,
            )
            self.row_height_adjuster.adjust_row_heights(
                worksheet,
                df,
                startrow=2 if title else 1,
            )
            # Additional formatting as needed
