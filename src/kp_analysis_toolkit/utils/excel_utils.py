"""
Common Excel utilities for the analysis toolkit.

Provides reusable Excel formatting, table creation, and export functionality
that can be used across all modules in the toolkit.
"""

from pathlib import Path

import pandas as pd
from openpyxl.styles import Font


def export_dataframe_to_excel(
    df: pd.DataFrame,
    output_path: Path,
    sheet_name: str = "Sheet1",
    title: str | None = None,
    *,
    as_table: bool = True,
) -> None:
    """
    General-purpose DataFrame to Excel export with formatting.

    Args:
        df: DataFrame to export
        output_path: Path to save Excel file
        sheet_name: Name of the worksheet
        title: Optional title to add at the top
        as_table: Whether to format as Excel table

    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        start_row = 2 if title else 1
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row)
        worksheet = writer.sheets[sheet_name]

        if title:
            worksheet["A1"] = title
            worksheet["A1"].font = Font(bold=True, size=12, color="1F497D")

        if as_table and not df.empty:
            format_as_excel_table(worksheet, df, startrow=start_row + 1)
        else:
            auto_adjust_column_widths(worksheet, df)
