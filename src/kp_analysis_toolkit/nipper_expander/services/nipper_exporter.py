from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

    from kp_analysis_toolkit.core.services.excel_export.protocols import (
        ExcelExportService,
    )
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.models.types import PathLike
    from kp_analysis_toolkit.nipper_expander.protocols import NipperExporter


class NipperExporter(NipperExporter):
    """Protocol for Nipper-specific Excel export operations."""

    def __init__(
        self,
        excel_exporter: ExcelExportService,
        rich_output: RichOutputService,
    ) -> None:
        """
        Inititiaize the NipperExporter Service.

        Args:
            rich_output: Service for rich terminal output
            excel_exporter: Service for exporting DataFrames to Excel files

        """
        self.excel_exporter: ExcelExportService = excel_exporter
        self.rich_output: RichOutputService = rich_output

    def export_nipper_results(
        self,
        data_frame: pd.DataFrame,
        output_path: PathLike,
        *,
        sheet_name: str = "Expanded Nipper Results",
        title: str = "Nipper Expanded Report - One row per device/finding",
    ) -> None:
        """
        Write the expanded DataFrame to an Excel file.

        Args:
            data_frame (pd.DataFrame): The DataFrame to export.
            output_path (PathLike): The path where the Excel file will be saved.
            sheet_name (str, optional): The name of the sheet in the Excel file. Defaults to "Expanded Nipper Results".
            title (str, optional): The title for the report. Defaults to "Nipper Expanded Report - One row per device/finding".

        """
        self.excel_exporter.export_dataframe_to_excel(
            data_frame=data_frame,
            output_path=output_path,
            sheet_name=sheet_name,
            title=title,
            as_table=True,
        )
