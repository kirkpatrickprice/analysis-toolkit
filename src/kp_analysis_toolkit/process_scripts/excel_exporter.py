"""
Excel export functionality for search results.

Provides comprehensive Excel output with proper formatting, tables, and comments.
"""

import datetime
import random
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils.exceptions import IllegalCharacterError
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig
from kp_analysis_toolkit.process_scripts.models.results.base import (
    SearchResult,
    SearchResults,
)


def export_results_by_os_type(
    search_results: list[SearchResults],
    systems: list,
    output_dir: Path,
) -> dict[str, Path]:
    """
    Export search results to separate Excel files grouped by OS type.

    Args:
        search_results: List of SearchResults objects to export
        systems: List of systems processed
        output_dir: Directory to save reports

    Returns:
        Dictionary mapping OS types to file paths

    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Group systems by OS family
    systems_by_os = defaultdict(list)
    for system in systems:
        os_family = system.os_family.value if system.os_family else "Unknown"
        systems_by_os[os_family].append(system)

    # Generate timestamp for filenames
    timestamp: str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")  # noqa: DTZ005

    created_files = {}

    # Create a separate Excel file for each OS type
    for os_type, os_systems in systems_by_os.items():
        # Get system names for this OS type
        system_names: set[str] = {system.system_name for system in os_systems}

        # Filter search results for this OS type
        os_search_results: list[SearchResults] = []
        for search_result in search_results:
            # Create a copy of search result with only relevant systems
            filtered_results: list[SearchResult] = [
                r for r in search_result.results if r.system_name in system_names
            ]

            if filtered_results:
                # Create a copy of the search result with filtered results
                filtered_search_result = SearchResults(
                    search_config=search_result.search_config,
                    results=filtered_results,
                )
                os_search_results.append(filtered_search_result)

        # Skip if no results for this OS type
        if not os_search_results:
            continue

        # Create filename with OS type and timestamp
        sanitized_os_type = "".join(c if c.isalnum() else "_" for c in os_type)
        filename = f"{sanitized_os_type}-{timestamp}.xlsx"
        output_path = output_dir / filename

        # Export results for this OS type
        export_search_results_to_excel(os_search_results, output_path)

        # Add to created files dictionary
        created_files[os_type] = output_path

    return created_files


def export_search_results_to_excel(
    search_results: list[SearchResults],
    output_path: Path,
) -> None:
    """
    Export search results to Excel with each search as a separate worksheet.

    Args:
        search_results: List of SearchResults objects to export
        output_path: Path where the Excel file should be saved

    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Sort search results based on their configuration name
    sorted_search_configs = sorted(
        search_results,
        key=lambda sr: sr.search_config.excel_sheet_name
        if sr.search_config.name
        else "",
    )

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        summary_data: list = []

        for search_result in sorted_search_configs:
            sheet_name: str = sanitize_sheet_name(
                search_result.search_config.excel_sheet_name
                or search_result.search_config.name,
            )

            # Collect summary data
            summary_data.append(
                {
                    "Search Name": search_result.search_config.name,
                    "Sheet Name": sheet_name,
                    "Total Results": search_result.result_count,
                    "Unique Systems": search_result.unique_systems,
                    "Has Extracted Fields": search_result.has_extracted_fields,
                },
            )

            if not search_result.results:
                # Create sheet for searches with no results
                _create_empty_results_sheet(writer, search_result, sheet_name)
            else:
                # Create sheet with results
                _create_results_sheet(writer, search_result, sheet_name)

        # Create summary sheet
        _create_summary_sheet(writer, summary_data)


def _create_results_sheet(
    writer: pd.ExcelWriter,
    search_result: SearchResults,
    sheet_name: str,
) -> None:
    """Create a worksheet with search results."""
    # Create DataFrame from results
    data_frame = create_dataframe_from_results(search_result)

    # Write to Excel starting at row 3 to leave room for comment
    try:
        data_frame.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)
    except IllegalCharacterError as e:
        message = f"""
            Error writing to Excel: {e}. Ensure no illegal characters in search results.
            Search name: {search_result.search_config.name}
            Sheet name: {sheet_name}
            Offending record: {data_frame.head(1).to_dict(orient="records")}"""
        raise ValueError(message) from e

    # Get the worksheet for formatting
    worksheet = writer.sheets[sheet_name]

    # Add and format comment
    _add_search_comment(worksheet, search_result.search_config.comment)

    # Format as Excel table
    if not data_frame.empty:
        _format_as_excel_table(worksheet, data_frame, startrow=3)

    # Add search metadata
    _add_search_metadata(worksheet, search_result, data_frame.shape[1])


def _create_empty_results_sheet(
    writer: pd.ExcelWriter,
    search_result: SearchResults,
    sheet_name: str,
) -> None:
    """Create a worksheet for searches with no results."""
    empty_df = pd.DataFrame(
        {
            "Search Results": ["No matches found for this search configuration"],
        },
    )
    empty_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)

    worksheet = writer.sheets[sheet_name]

    # Add comment
    _add_search_comment(worksheet, search_result.search_config.comment)

    # Style the "no results" message
    worksheet["A3"].font = Font(italic=True, color="808080")
    worksheet.column_dimensions["A"].width = 50


def _create_summary_sheet(writer: pd.ExcelWriter, summary_data: list[dict]) -> None:
    """Create a summary worksheet with overview of all searches."""
    summary_df = pd.DataFrame(summary_data)

    # Write summary to first sheet
    summary_df.to_excel(writer, sheet_name="Summary", index=False, startrow=1)

    worksheet = writer.sheets["Summary"]

    # Add title
    worksheet["A1"] = "Search Results Summary"
    worksheet["A1"].font = Font(bold=True, size=16, color="1F497D")

    # Format as table
    if not summary_df.empty:
        _format_as_excel_table(worksheet, summary_df, startrow=2)

    # Move summary sheet to first position
    workbook = writer.book
    workbook.move_sheet("Summary", offset=-len(workbook.worksheets) + 1)


def create_dataframe_from_results(search_results: SearchResults) -> pd.DataFrame:
    """
    Convert search results to pandas DataFrame with proper column ordering.

    Args:
        search_results: SearchResults object to convert

    Returns:
        pandas DataFrame with search results

    """
    if not search_results.results:
        return pd.DataFrame()

    data = []

    # Determine all possible extracted field names
    all_field_names: set[str] = set()
    for result in search_results.results:
        if result.extracted_fields:
            all_field_names.update(result.extracted_fields.keys())

    # Use field order from search configuration if available
    ordered_field_names: list[str] = []
    config_field_list: list[str | None] = search_results.search_config.field_list or []

    # First add fields that are in the configuration's field_list (preserving order)
    for field in config_field_list:
        if field in all_field_names:
            ordered_field_names.append(field)
            all_field_names.remove(field)

    # Then add any remaining fields (alphabetically sorted)
    ordered_field_names.extend(sorted(all_field_names))

    for result in search_results.results:
        row: dict[str, str] = {
            "System Name": result.system_name,
            "Line Number": result.line_number,
            "Matched Text": result.matched_text.replace("\n", "\r"),
        }

        # Add extracted fields in the ordered sequence
        if result.extracted_fields:
            for field_name in ordered_field_names:
                row[field_name] = result.extracted_fields.get(field_name, "")
        else:
            # Add empty columns for consistency if no extracted fields
            for field_name in ordered_field_names:
                row[field_name] = ""

        data.append(row)

    return pd.DataFrame(data)


def sanitize_sheet_name(name: str) -> str:
    """
    Sanitize sheet name for Excel compatibility.

    Args:
        name: Original sheet name

    Returns:
        Sanitized sheet name safe for Excel

    """
    # Excel sheet names can't contain: / \ ? * [ ] :
    # Also limit to 31 characters
    invalid_chars = ["/", "\\", "?", "*", "[", "]", ":"]
    max_sheet_name_length = 31

    sanitized = name
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing spaces
    sanitized = sanitized.strip()

    # Ensure it's not empty
    if not sanitized:
        sanitized = "Unnamed_Search"

    # Limit to 31 characters (Excel limitation)
    if len(sanitized) > max_sheet_name_length:
        sanitized = sanitized[: max_sheet_name_length - 3] + "..."

    return sanitized


def _add_search_comment(worksheet: Worksheet, comment: str | None) -> None:
    """Add and format the search comment at the top of the worksheet."""
    if not comment:
        return

    worksheet.merge_cells("A1:D1")  # Merge first row for comment
    worksheet["A1"] = comment

    # Style the comment
    worksheet["A1"].font = Font(bold=False, size=9, color="1F497D", italic=True)
    worksheet["A1"].alignment = Alignment(
        wrap_text=True,
        vertical="top",
        horizontal="left",
    )

    # Set row height to accommodate wrapped text
    worksheet.row_dimensions[1].height = max(30, len(comment) // 120 * 15)


def _add_search_metadata(
    worksheet: Worksheet,
    search_result: SearchResults,
    data_columns: int,
) -> None:
    """Add search metadata to the right side of the data."""
    # Find column after data
    metadata_col = data_columns + 2  # Leave one empty column
    metadata_col_letter = chr(ord("A") + metadata_col - 1)

    # Add metadata headers and values
    metadata = [
        ("Search Configuration:", ""),
        ("Name:", search_result.search_config.name),
        ("Total Results:", search_result.result_count),
        ("Unique Systems:", search_result.unique_systems),
        (
            "Max Results:",
            search_result.search_config.max_results
            if search_result.search_config.max_results != -1
            else "Unlimited",
        ),
        (
            "Only Matching:",
            "Yes" if search_result.search_config.only_matching else "No",
        ),
        ("Unique Results:", "Yes" if search_result.search_config.unique else "No"),
        ("Full Scan:", "Yes" if search_result.search_config.full_scan else "No"),
    ]

    if search_result.search_config.field_list:
        metadata.append(
            ("Extracted Fields:", ", ".join(search_result.search_config.field_list)),
        )

    # Add metadata to worksheet
    for i, (label, value) in enumerate(metadata, start=3):
        label_cell = f"{metadata_col_letter}{i}"
        value_cell = f"{chr(ord(metadata_col_letter) + 1)}{i}"

        worksheet[label_cell] = label
        worksheet[value_cell] = value

        # Style metadata labels
        if label.endswith(":"):
            worksheet[label_cell].font = Font(bold=True, size=10)


def _format_date_columns(
    worksheet: Worksheet,
    df: pd.DataFrame,
    startrow: int = 1,
) -> None:
    """
    Format columns as dates and standardize date representations.

    Apply the following criteria:
    1. Column name contains 'date' (case-insensitive)
    2. Column values are in a common date format

    For identified date columns:
    - Applies Excel date formatting
    - Standardizes actual cell values to ISO format (YYYY-MM-DD)

    Args:
        worksheet: The worksheet to format
        df: DataFrame containing the data
        startrow: Row where the data starts (1-indexed)

    """
    is_date_column_threshold: float = 0.7

    # Common date patterns to check
    date_patterns: list[str] = [
        # MM/DD/YYYY or MM/DD/YY
        r"^\d{1,2}/\d{1,2}/\d{2,4}$",
        # DD-MM-YYYY or DD-MM-YY
        r"^\d{1,2}-\d{1,2}-\d{2,4}$",
        # YYYY-MM-DD
        r"^\d{4}-\d{1,2}-\d{1,2}$",
        # DD-MMM-YYYY or DD-MMM-YY (01-JAN-2025)
        r"^\d{1,2}-[A-Za-z]{3}-\d{2,4}$",
        # MMM DD, YYYY
        r"^[A-Za-z]{3} \d{1,2}, \d{4}$",
    ]

    # Date parsing formats to try
    date_formats = [
        "%m/%d/%Y",
        "%m/%d/%y",  # MM/DD/YYYY, MM/DD/YY
        "%d-%m-%Y",
        "%d-%m-%y",  # DD-MM-YYYY, DD-MM-YY
        "%Y-%m-%d",  # YYYY-MM-DD
        "%d-%b-%Y",
        "%d-%b-%y",  # DD-MMM-YYYY, DD-MMM-YY
        "%b %d, %Y",  # MMM DD, YYYY
    ]

    for col_num, column_name in enumerate(df.columns, 1):
        column_letter: str = _get_column_letter(col_num)
        is_date_column = False

        # Check if column name contains 'date'
        if "date" in column_name.lower():
            is_date_column = True

        # If not determined by name, check values
        if not is_date_column:
            # Sample up to 10 non-empty values from the column
            sample_values: list[str] = [
                str(val) for val in df[column_name].dropna().head(10) if pd.notna(val)
            ]

            if sample_values:
                # Check if most values match a date pattern
                matches = 0
                for value in sample_values:
                    if any(re.match(pattern, str(value)) for pattern in date_patterns):
                        matches += 1

                # If more than 70% of sampled values match a date pattern
                if matches / len(sample_values) > is_date_column_threshold:
                    is_date_column = True

        # Apply date formatting if it's a date column
        if is_date_column:
            # Get the data range for this column (excluding header)
            data_start_row: int = startrow + 1  # +1 for the header row
            data_end_row: int = data_start_row + len(df) - 1

            # Apply date format to all cells in the column
            for row in range(data_start_row, data_end_row + 1):
                cell: str = f"{column_letter}{row}"
                cell_value: str | float | None = worksheet[cell].value

                # Skip empty cells
                if not cell_value or cell_value == "":
                    continue

                # Convert the date string to a standardized format
                try:
                    # Try to parse the date with various formats
                    parsed_date = None

                    # If already a datetime object, just use it
                    if isinstance(cell_value, datetime.datetime):
                        parsed_date = cell_value
                    else:
                        # Try each format until one works
                        for date_format in date_formats:
                            try:
                                parsed_date: datetime.datetime = (
                                    datetime.datetime.strptime(  # noqa: DTZ007
                                        str(cell_value),
                                        date_format,
                                    )
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


def _format_as_excel_table(
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
    end_row = startrow + len(df)
    end_col_letter = _get_column_letter(len(df.columns))
    table_range = f"A{startrow}:{end_col_letter}{end_row}"

    # Create unique table name
    random_suffix = random.randint(1000, 9999)
    table_name = f"Table_{worksheet.title}_{random_suffix}".replace(
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
        message: str = f"Error adding table to worksheet '{worksheet.title}': {e}. "
        raise ValueError(message) from e

    # format date columns
    _format_date_columns(worksheet, df, startrow)

    # Auto-adjust column widths
    _auto_adjust_column_widths(worksheet, df)


def _get_column_letter(col_num: int) -> str:
    """Convert column number to Excel column letter."""
    result = ""
    while col_num > 0:
        col_num -= 1
        result = chr(col_num % 26 + ord("A")) + result
        col_num //= 26
    return result


def _auto_adjust_column_widths(
    worksheet: Worksheet,
    df: pd.DataFrame,
) -> None:
    """Auto-adjust column widths based on content."""
    for col_num, column_name in enumerate(df.columns, 1):
        column_letter = _get_column_letter(col_num)

        # Calculate max width needed
        max_length = len(str(column_name))  # Header length

        # Check data in column
        for value in df[column_name]:
            if pd.notna(value):
                max_length = max(max_length, len(str(value)))

        # Set width with reasonable bounds
        adjusted_width = min(max(max_length + 2, 10), 80)  # Min 10, Max 80 chars
        worksheet.column_dimensions[column_letter].width = adjusted_width


def export_systems_summary_to_excel(systems: list, output_path: Path) -> None:
    """
    Export a summary of all systems to Excel for reference.

    Args:
        systems: List of Systems objects
        output_path: Path where the Excel file should be saved

    """
    # Create systems summary data
    systems_data = []
    for system in systems:
        systems_data.append(
            {
                "System Name": system.system_name,
                "OS Family": system.os_family.value if system.os_family else "Unknown",
                "Producer": system.producer.value if system.producer else "Unknown",
                "Producer Version": system.producer_version,
                "Linux Family": system.distro_family.value
                if system.distro_family
                else "N/A",
                "File Path": str(system.file),
                "File Encoding": system.encoding or "Unknown",
            },
        )

    # Create DataFrame and export
    systems_df = pd.DataFrame(systems_data)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        systems_df.to_excel(writer, sheet_name="Systems_Summary", index=False)

        worksheet = writer.sheets["Systems_Summary"]

        # Add title
        worksheet.insert_rows(1)
        worksheet["A1"] = f"Systems Summary ({len(systems)} systems found)"
        worksheet["A1"].font = Font(bold=True, size=14, color="1F497D")

        # Format as table
        if not systems_df.empty:
            _format_as_excel_table(worksheet, systems_df, startrow=2)


def create_search_report(
    search_results: list[SearchResults],
    systems: list,
    output_dir: Path,
    program_config: ProgramConfig = None,
) -> dict[str, Path]:
    """
    Create comprehensive search report with multiple Excel files.

    Args:
        search_results: List of search results
        systems: List of systems processed
        output_dir: Directory to save reports
        program_config: Program configuration (optional)

    Returns:
        Dictionary mapping report types to file paths

    """
    output_dir.mkdir(parents=True, exist_ok=True)

    created_files = {}

    # Main search results
    search_results_path = output_dir / "search_results.xlsx"
    export_search_results_to_excel(search_results, search_results_path)
    created_files["search_results"] = search_results_path

    # Systems summary
    systems_summary_path = output_dir / "systems_summary.xlsx"
    export_systems_summary_to_excel(systems, systems_summary_path)
    created_files["systems_summary"] = systems_summary_path

    # Create OS-specific reports
    os_specific_files = export_results_by_os_type(search_results, systems, output_dir)
    for os_type, file_path in os_specific_files.items():
        created_files[f"os_specific_{os_type}"] = file_path

    # Detailed results by system (if requested)
    if (
        program_config
        and hasattr(program_config, "detailed_reports")
        and program_config.detailed_reports
    ):
        detailed_path = output_dir / "detailed_results_by_system.xlsx"
        _create_detailed_system_report(search_results, detailed_path)
        created_files["detailed_by_system"] = detailed_path

    return created_files


def _create_detailed_system_report(
    search_results: list[SearchResults],
    output_path: Path,
) -> None:
    """Create a detailed report organized by system."""
    # Group results by system
    system_results = {}

    for search_result in search_results:
        for result in search_result.results:
            system_name = result.system_name
            if system_name not in system_results:
                system_results[system_name] = []

            system_results[system_name].append(
                {
                    "Search Name": search_result.search_config.name,
                    "Line Number": result.line_number,
                    "Matched Text": result.matched_text,
                    "Extracted Fields": str(result.extracted_fields)
                    if result.extracted_fields
                    else "None",
                },
            )

    # Create Excel file with one sheet per system
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for system_name, results in system_results.items():
            data_frame = pd.DataFrame(results)
            sheet_name = sanitize_sheet_name(system_name)

            data_frame.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)

            worksheet = writer.sheets[sheet_name]
            worksheet["A1"] = f"Results for System: {system_name}"
            worksheet["A1"].font = Font(bold=True, size=12, color="1F497D")

            if not data_frame.empty:
                _format_as_excel_table(worksheet, data_frame, startrow=2)
