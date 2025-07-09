import re
from datetime import datetime

import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet


def auto_adjust_column_widths(worksheet: Worksheet, df: pd.DataFrame) -> None:
    """
    Auto-adjust column widths based on content.

    Args:
        worksheet: The worksheet to adjust
        df: DataFrame that was written to the worksheet

    """
    for col_num, column_name in enumerate(df.columns, 1):
        column_letter = get_column_letter(col_num)

        # Calculate max width needed
        max_length = len(str(column_name))  # Header length

        # Check data in the column
        for value in df.iloc[:, col_num - 1]:
            if pd.notna(value):
                length = len(str(value))
                max_length = max(max_length, length)

        # Set a reasonable width (with limits)
        width = min(max(max_length + 2, 10), 50)
        worksheet.column_dimensions[column_letter].width = width


def format_date_columns(  # noqa: C901, PLR0912
    worksheet: Worksheet,
    df: pd.DataFrame,
    startrow: int = 1,
) -> None:
    """
    Format date columns in the worksheet.

    Args:
        worksheet: The worksheet to format
        df: DataFrame that was written to the worksheet
        startrow: Row where the data starts (1-indexed)

    """
    for col_num, column_name in enumerate(df.columns, 1):
        column_letter = get_column_letter(col_num)

        # Check if this looks like a date column
        is_date_column = False
        if "date" in str(column_name).lower() or "time" in str(column_name).lower():
            is_date_column = True
        else:
            # Sample some values to see if they look like dates
            sample_values = df.iloc[:5, col_num - 1].dropna()
            date_count = 0
            for value in sample_values:
                if pd.notna(value):
                    str_value = str(value)
                    # Simple date pattern check
                    if re.match(r"\d{4}-\d{2}-\d{2}", str_value) or re.match(
                        r"\d{2}/\d{2}/\d{4}",
                        str_value,
                    ):
                        date_count += 1
            if date_count >= len(sample_values) * 0.5:  # 50% or more look like dates
                is_date_column = True

        if is_date_column:
            # Apply date formatting to the entire column
            for row_num in range(startrow + 1, startrow + len(df) + 1):
                cell = f"{column_letter}{row_num}"

                # Try to parse and standardize date values
                try:
                    value = worksheet[cell].value
                    if value and pd.notna(value):
                        # Try to parse various date formats
                        parsed_date = None
                        str_value = str(value)

                        # Common date patterns
                        patterns: list[str] = [
                            "%Y-%m-%d",
                            "%m/%d/%Y",
                            "%d/%m/%Y",
                            "%Y-%m-%d %H:%M:%S",
                            "%m/%d/%Y %H:%M:%S",
                        ]

                        for pattern in patterns:
                            try:
                                parsed_date: datetime = datetime.strptime(  # noqa: DTZ007
                                    str_value,
                                    pattern,
                                )
                                break
                            except ValueError:
                                continue

                        # If we successfully parsed the date, standardize it
                        if parsed_date:
                            # Update the cell with the standardized date string
                            worksheet[cell].value = parsed_date.strftime("%Y-%m-%d")
                except Exception:  # noqa: BLE001, S110
                    # If parsing fails, keep the original value
                    pass

                # Apply Excel date formatting
                worksheet[cell].number_format = "yyyy-mm-dd"


def set_table_alignment(worksheet: Worksheet, table_range: str) -> None:
    """
    Set alignment for table cells.

    Args:
        worksheet: The worksheet containing the table
        table_range: Excel range string (e.g., "A1:D10")

    """
    for row in worksheet[table_range]:
        for cell in row:
            cell.alignment = Alignment(
                horizontal="left",
                vertical="top",
                wrap_text=True,
            )


def adjust_row_heights(
    worksheet: Worksheet,
    df: pd.DataFrame,
    startrow: int = 1,
) -> None:
    """
    Adjust row heights based on content.

    Args:
        worksheet: The worksheet to adjust
        df: DataFrame that was written to the worksheet
        startrow: Row where the data starts (1-indexed)

    """
    # Set minimum row height for header
    worksheet.row_dimensions[startrow].height = 20

    # Adjust data row heights
    for row_num in range(startrow + 1, startrow + len(df) + 1):
        max_lines = 1

        # Check each cell in the row for line breaks
        for col_num in range(1, len(df.columns) + 1):
            column_letter = get_column_letter(col_num)
            cell_value = worksheet[f"{column_letter}{row_num}"].value

            if cell_value and isinstance(cell_value, str):
                lines = cell_value.count("\n") + 1
                max_lines = max(max_lines, lines)

        # Set row height (approximate 15 points per line)
        height = max(15, min(max_lines * 15, 100))
        worksheet.row_dimensions[row_num].height = height
