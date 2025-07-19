from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from kp_analysis_toolkit.core.services.csv_processing.service import CSVProcessorService
from kp_analysis_toolkit.nipper_expander.protocols import (
    NipperExpanderService,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd

    from kp_analysis_toolkit.core.services.csv_processing import (
        CSVProcessorService,
    )
    from kp_analysis_toolkit.nipper_expander.protocols import (
        NipperExpanderService,
        NipperExporterService,
    )
    from kp_analysis_toolkit.utils.rich_output import RichOutput


class NipperExpanderService(NipperExpanderService):
    """Main service for the Nipper Expander module."""

    def __init__(
        self,
        csv_processor: CSVProcessorService,
        data_expander: NipperExpanderService,
        nipper_exporter: NipperExporterService,
        rich_output: RichOutput,
    ) -> None:
        self.csv_processor: CSVProcessorService = csv_processor
        self.data_expander: NipperExpanderService = data_expander
        self.nipper_exporter: NipperExporterService = nipper_exporter
        self.rich_output: RichOutput = rich_output

    def process_nipper_csv(
        self,
        input_path: Path,
        output_path: Path,
    ) -> None:
        """
        Process one Nipper CSV file and export the expanded results to an Excel file.

        Args:
            input_path: Path to the input Nipper CSV file
            output_path: Path to the output Nipper CSV file

        Raises (in order of likelihood):
            FileNotFoundError: Input CSV file not found or output directory doesn't exist
            PermissionError: Insufficient permissions to read input or write output
            ValueError: Invalid CSV data, missing required columns, or data format issues
            pd.errors.ParserError: Malformed CSV file structure
            pd.errors.EmptyDataError: Input CSV file is empty
            UnicodeDecodeError: File encoding problems
            OSError: File system errors (disk space, invalid paths)
            MemoryError: Insufficient memory for processing large datasets

        """
        try:
            data_frame: pd.DataFrame = self.csv_processor.read_and_validate_csv_file(
                input_path,
                required_columns=["Devices"],
            )

            expanded_data_frame: pd.DataFrame = self.data_expander.expand_device_rows(
                data_frame,
            )

            self.nipper_exporter.export_nipper_results(
                expanded_data_frame,
                output_path,
            )

        except Exception as e:
            message: str = f"Failed to process Nipper CSV file {input_path}: {e}"
            self.rich_output.error(message)
            raise
