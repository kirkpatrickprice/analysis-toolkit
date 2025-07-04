from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import pandas as pd

from kp_analysis_toolkit.utils.rich_output import RichOutput

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd

    from kp_analysis_toolkit.utils.rich_output import RichOutput


class CSVReader(Protocol):
    """Protocol for CSV reading operations."""

    def read_csv(self, file_path: Path) -> pd.DataFrame: ...
    def validate_csv_structure(self, data_frame: pd.DataFrame) -> bool: ...


class DataExpander(Protocol):
    """Protocol for data expansion operations."""

    def expand_ranges(
        self,
        data_frame: pd.DataFrame,
        range_columns: list[str],
    ) -> pd.DataFrame: ...
    def expand_lists(
        self,
        data_frame: pd.DataFrame,
        list_columns: list[str],
    ) -> pd.DataFrame: ...


class DataValidator(Protocol):
    """Protocol for data validation."""

    def validate_required_columns(
        self,
        data_frame: pd.DataFrame,
        required_columns: list[str],
    ) -> bool: ...
    def validate_data_types(
        self,
        data_frame: pd.DataFrame,
        column_types: dict[str, type],
    ) -> bool: ...


class CSVProcessorService:
    """Service for processing Nipper CSV files."""

    def __init__(
        self,
        csv_reader: CSVReader,
        data_expander: DataExpander,
        data_validator: DataValidator,
        rich_output: RichOutput,
    ) -> None:
        self.csv_reader: CSVReader = csv_reader
        self.data_expander: DataExpander = data_expander
        self.data_validator: DataValidator = data_validator
        self.rich_output: RichOutput = rich_output

    def process_nipper_csv(
        self,
        csv_file_path: Path,
        *,  # Optional parameters for expansion
        expand_ranges: bool = True,
        expand_lists: bool = True,
    ) -> pd.DataFrame:
        """Process Nipper CSV file with expansion options."""
        try:
            # Read CSV file
            data_frame: pd.DataFrame = self.csv_reader.read_csv(csv_file_path)

            # Validate basic structure
            if not self.csv_reader.validate_csv_structure(data_frame):
                message: str = f"Invalid CSV structure: {csv_file_path}"
                raise ValueError(message)  # noqa: TRY301

            # Validate required columns for Nipper format
            required_columns: list[str] = ["Source", "Destination", "Service", "Action"]
            if not self.data_validator.validate_required_columns(
                data_frame,
                required_columns,
            ):
                message: str = f"Missing required columns in: {csv_file_path}"
                raise ValueError(message)  # noqa: TRY301

            # Expand ranges if requested
            if expand_ranges:
                range_columns: list[str] = ["Source", "Destination"]
                data_frame = self.data_expander.expand_ranges(data_frame, range_columns)

            # Expand lists if requested
            if expand_lists:
                list_columns: list[str] = ["Service"]
                data_frame = self.data_expander.expand_lists(data_frame, list_columns)

            self.rich_output.success(f"Processed Nipper CSV: {csv_file_path}")

        except Exception as e:
            self.rich_output.error(f"Failed to process CSV {csv_file_path}: {e}")
            raise
        else:
            return data_frame
