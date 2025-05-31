from pathlib import Path

import pandas as pd

from .data_models import SearchResults


def export_search_results_to_excel(
    search_results: list[SearchResults],
    output_path: Path,
) -> None:
    """Export search results to Excel with each search as a separate worksheet."""
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for search_result in search_results:
            # Create DataFrame from results
            df = _create_dataframe_from_results(search_result)

            # Write to Excel with search name as sheet name
            sheet_name = _sanitize_sheet_name(search_result.config.name)
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)

            # Add comment at the top
            worksheet = writer.sheets[sheet_name]
            if search_result.config.comment:
                worksheet["A1"] = search_result.config.comment

            # Format as Excel table
            if not df.empty:
                _format_as_table(worksheet, df, startrow=3)


def _create_dataframe_from_results(search_results: SearchResults) -> pd.DataFrame:
    """Convert search results to pandas DataFrame."""
    if not search_results.results:
        return pd.DataFrame()

    # Start with basic columns
    data = []

    for result in search_results.results:
        row = {
            "System Name": result.system_name,
            "Line Number": result.line_number,
            "Matched Text": result.matched_text,
        }

        # Add extracted fields if they exist
        if result.extracted_fields:
            row.update(result.extracted_fields)

        data.append(row)

    return pd.DataFrame(data)
