"""Table generation utilities for Excel export."""

import random
from typing import TYPE_CHECKING

from openpyxl.worksheet.table import Table

from kp_analysis_toolkit.core.services.excel_export.protocols import (
    ColumnWidthAdjuster,
    DateFormatter,
    ExcelFormatter,
    RowHeightAdjuster,
    TableGenerator,
    TableStyler,
)
from kp_analysis_toolkit.core.services.excel_export.sheet_management import (
    DefaultSheetNameSanitizer,
)

if TYPE_CHECKING:
    import pandas as pd
    from openpyxl.worksheet.worksheet import Worksheet


class DefaultTableGenerator(TableGenerator):
    """Default implementation for formatting DataFrame as an Excel table using dependency injection."""

    def __init__(
        self,
        formatter: ExcelFormatter,
        date_formatter: DateFormatter,
        column_width_adjuster: ColumnWidthAdjuster,
        row_height_adjuster: RowHeightAdjuster,
        table_styler: TableStyler,
    ) -> None:
        """
        Initialize the table generator with required formatters and adjusters.

        Args:
            formatter: Excel formatter for table alignment and column widths
            date_formatter: Formatter for detecting and formatting date columns
            column_width_adjuster: Adjuster for automatically sizing column widths
            row_height_adjuster: Adjuster for automatically sizing row heights
            table_styler: Styler for applying Excel table styles

        """
        self.formatter: ExcelFormatter = formatter
        self.date_formatter: DateFormatter = date_formatter
        self.column_width_adjuster: ColumnWidthAdjuster = column_width_adjuster
        self.row_height_adjuster: RowHeightAdjuster = row_height_adjuster
        self.table_styler: TableStyler = table_styler

    def _get_table_range(self, df: "pd.DataFrame", startrow: int) -> str:
        """
        Calculate the Excel range string for the DataFrame table.

        Args:
            df: The DataFrame to calculate the range for
            startrow: The starting row number (1-based)

        Returns:
            str: Excel range string in format "A1:Z10" covering the DataFrame data

        """
        end_row: int = startrow + len(df)
        end_col_letter: str = DefaultSheetNameSanitizer().get_column_letter(
            len(df.columns),
        )
        return f"A{startrow}:{end_col_letter}{end_row}"

    def _generate_table_name(self, worksheet_title: str) -> str:
        """
        Generate a unique, valid Excel table name from the worksheet title.

        Excel table names must be unique within a workbook and follow specific naming rules.
        This method creates a name by combining the worksheet title with a random suffix,
        then sanitizing it to ensure compliance with Excel naming requirements.

        Args:
            worksheet_title: The title of the worksheet containing the table

        Returns:
            str: A unique, sanitized table name safe for use in Excel

        """
        random_suffix: int = random.randint(1000, 9999)
        table_name: str = f"Table_{worksheet_title}_{random_suffix}".replace(
            " ",
            "_",
        ).replace("-", "_")
        table_name = "".join(c if c.isalnum() or c == "_" else "_" for c in table_name)
        if table_name[0].isdigit():
            table_name = "T_" + table_name
        return table_name

    def format_as_excel_table(
        self,
        worksheet: "Worksheet",
        df: "pd.DataFrame",
        startrow: int = 1,
    ) -> None:
        """
        Format a DataFrame as a styled Excel table in the given worksheet.

        This method creates a properly formatted Excel table with styling, date formatting,
        auto-adjusted column widths, and row heights. If the DataFrame is empty, no action
        is taken.

        Args:
            worksheet: The openpyxl worksheet to add the table to
            df: The pandas DataFrame containing the data to format
            startrow: The starting row number for the table (default: 1, 1-based indexing)

        Raises:
            ValueError: If the table cannot be added to the worksheet (e.g., overlapping ranges)

        """
        if df.empty:
            return

        # Calculate table range
        table_range: str = self._get_table_range(df, startrow)

        # Create unique table name
        table_name: str = self._generate_table_name(worksheet.title)

        # Create table
        table = Table(displayName=table_name, ref=table_range)

        # Add table style
        self.table_styler.apply_style(table)

        # Add table to worksheet
        try:
            worksheet.add_table(table)
        except ValueError as e:
            message: str = f"Error adding table to worksheet '{worksheet.title}': {e}. "
            raise ValueError(message) from e

        # Set top-left alignment for all cells in table range
        self.formatter.set_table_alignment(worksheet, table_range)

        # Format date columns
        self.date_formatter.format_date_columns(worksheet, df, startrow)

        # Auto-adjust column widths
        self.column_width_adjuster.auto_adjust_column_widths(worksheet, df)

        # Adjust row heights based on content
        self.row_height_adjuster.adjust_row_heights(worksheet, df, startrow)
