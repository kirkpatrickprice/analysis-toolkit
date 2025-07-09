import random

from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet


def format_as_excel_table(
    worksheet: Worksheet,
    df: pd.DataFrame,
    startrow: int = 1,
) -> None:
    """
    Format DataFrame as an Excel table with proper styling.

    Args:
        worksheet: The worksheet to format
        df: DataFrame that was written to the worksheet
        startrow: Row where the data starts (1-indexed)

    """
    if df.empty:
        return

    # Calculate table range
    end_row: int = startrow + len(df)
    end_col_letter: str = get_column_letter(len(df.columns))
    table_range: str = f"A{startrow}:{end_col_letter}{end_row}"

    # Create unique table name
    random_suffix: int = random.randint(1000, 9999)
    table_name: str = f"Table_{worksheet.title}_{random_suffix}".replace(
        " ",
        "_",
    ).replace(
        "-",
        "_",
    )
    # Ensure table name doesn't start with a number or contain invalid chars
    table_name = "".join(c if c.isalnum() or c == "_" else "_" for c in table_name)
    if table_name[0].isdigit():
        table_name = "T_" + table_name

    # Create table
    table = Table(displayName=table_name, ref=table_range)

    # Add table style
    style = TableStyleInfo(
        name="TableStyleMedium9",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    table.tableStyleInfo = style

    # Add table to worksheet
    try:
        worksheet.add_table(table)
    except ValueError as e:
        message = f"Error adding table to worksheet '{worksheet.title}': {e}. "
        raise ValueError(message) from e

    # Set top-left alignment for all cells in table range
    set_table_alignment(worksheet, table_range)

    # Format date columns
    format_date_columns(worksheet, df, startrow)

    # Auto-adjust column widths
    auto_adjust_column_widths(worksheet, df)

    # Adjust row heights based on content
    adjust_row_heights(worksheet, df, startrow)
