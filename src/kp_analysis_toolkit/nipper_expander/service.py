from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.excel_export import ExcelExportService
    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.nipper_expander.services.csv_processor import (
        CSVProcessorService,
    )
    from kp_analysis_toolkit.utils.rich_output import RichOutput


class NipperExpanderService:
    """Main service for the Nipper Expander module."""

    def __init__(
        self,
        csv_processor: CSVProcessorService,
        excel_export: ExcelExportService,
        file_processing: FileProcessingService,
        rich_output: RichOutput,
    ) -> None:
        self.csv_processor = csv_processor
        self.excel_export = excel_export
        self.file_processing = file_processing
        self.rich_output = rich_output

    def execute(
        self,
        input_path: Path,
        output_path: Path,
        *,
        expand_ranges: bool = True,
        expand_lists: bool = True,
    ) -> None:
        """Execute Nipper expansion workflow."""
        try:
            self.rich_output.header("Starting Nipper Expansion")

            # Discover CSV files
            csv_files = self._discover_csv_files(input_path)

            if not csv_files:
                self.rich_output.warning("No CSV files found")
                return

            # Process each CSV file
            all_expanded_data = []
            for csv_file in csv_files:
                expanded_data = self.csv_processor.process_nipper_csv(
                    csv_file,
                    expand_ranges=expand_ranges,
                    expand_lists=expand_lists,
                )
                all_expanded_data.append(expanded_data)

            # Combine all data if multiple files
            if len(all_expanded_data) > 1:
                import pandas as pd

                combined_data = pd.concat(all_expanded_data, ignore_index=True)
            else:
                combined_data = all_expanded_data[0]

            # Export to Excel
            self.excel_export.export_dataframe(
                combined_data,
                output_path,
                sheet_name="Expanded_Rules",
            )

            self.rich_output.success(
                f"Successfully expanded {len(csv_files)} CSV files to {output_path}",
            )

        except Exception as e:
            self.rich_output.error(f"Nipper Expansion failed: {e}")
            raise

    def _discover_csv_files(self, path: Path) -> list[Path]:
        """Discover CSV files in the input path."""
        if path.is_file() and path.suffix.lower() == ".csv":
            return [path]
        if path.is_dir():
            return list(path.glob("*.csv"))
        return []
