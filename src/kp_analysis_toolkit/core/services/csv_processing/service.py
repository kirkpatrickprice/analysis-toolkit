"""CSV processing service implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from kp_analysis_toolkit.core.services.file_processing.service import (
    FileProcessingService,
)
from kp_analysis_toolkit.core.services.rich_output import RichOutputService

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService


class CSVProcessorService:
    """Service for CSV file processing with validation and error handling."""

    def __init__(
        self,
        file_processing: FileProcessingService,
        rich_output: RichOutputService,
    ) -> None:
        """
        Initialize the CSV processor service.

        Args:
            file_processing: Service for file processing operations
            rich_output: Service for rich terminal output

        """
        self.file_processing: FileProcessingService = file_processing
        self.rich_output: RichOutputService = rich_output

    def read_csv_file(self, file_path: Path) -> pd.DataFrame:
        """
        Read and validate CSV file with encoding detection.

        Args:
            file_path: Path to the CSV file to read

        Returns:
            DataFrame containing the CSV data

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the file cannot be read or is not a valid CSV
            OSError: If there are file access permissions issues

        """
        # Validate file exists using file processing service
        if not self.file_processing.validate_file_exists(file_path):
            error_msg: str = f"CSV file not found: {file_path}"
            self.rich_output.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Detect encoding for proper CSV reading
        encoding: str | None = self.file_processing.detect_encoding(file_path)
        if encoding is None:
            self.rich_output.warning(
                f"Could not detect encoding for {file_path}, using utf-8",
            )
            encoding = "utf-8"
        else:
            self.rich_output.debug(f"Detected encoding: {encoding} for {file_path}")

        try:
            # Read CSV with detected encoding
            self.rich_output.info(f"Reading CSV file: {file_path}")
            data_frame: pd.DataFrame = pd.read_csv(file_path, encoding=encoding)

            self.rich_output.success(
                f"Successfully read CSV with {len(data_frame)} rows and {len(data_frame.columns)} columns",
            )
        except pd.errors.EmptyDataError as e:
            error_msg = f"CSV file is empty: {file_path}"
            self.rich_output.error(error_msg)
            raise ValueError(error_msg) from e
        except pd.errors.ParserError as e:
            error_msg = f"Failed to parse CSV file {file_path}: {e}"
            self.rich_output.error(error_msg)
            raise ValueError(error_msg) from e
        except UnicodeDecodeError as e:
            error_msg = (
                f"Encoding error reading CSV file {file_path} with {encoding}: {e}"
            )
            self.rich_output.error(error_msg)
            raise ValueError(error_msg) from e
        except (OSError, PermissionError) as e:
            error_msg = f"File access error reading CSV {file_path}: {e}"
            self.rich_output.error(error_msg)
            raise OSError(error_msg) from e
        else:
            return data_frame

    def validate_required_columns(
        self,
        data_frame: pd.DataFrame,
        required_columns: list[str],
    ) -> None:
        """
        Validate that required columns exist in the DataFrame.

        Args:
            data_frame: DataFrame to validate
            required_columns: List of column names that must be present

        Raises:
            KeyError: If any required columns are missing

        """
        if not required_columns:
            self.rich_output.debug("No required columns to validate")
            return

        missing_columns: list[str] = [
            col for col in required_columns if col not in data_frame.columns
        ]

        if missing_columns:
            available_columns: str = ", ".join(data_frame.columns.tolist())
            error_msg: str = (
                f"Missing required columns: {missing_columns}. "
                f"Available columns: {available_columns}"
            )
            self.rich_output.error(error_msg)
            raise KeyError(error_msg)

        self.rich_output.success(f"Validated required columns: {required_columns}")

    def process_csv_with_validation(
        self,
        file_path: Path,
        required_columns: list[str],
    ) -> pd.DataFrame:
        """
        Complete CSV processing pipeline with validation.

        Args:
            file_path: Path to the CSV file to process
            required_columns: List of column names that must be present

        Returns:
            DataFrame containing the validated CSV data

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            KeyError: If any required columns are missing
            ValueError: If the file cannot be read or is not a valid CSV

        """
        # Read the CSV file with encoding detection
        data_frame: pd.DataFrame = self.read_csv_file(file_path)

        # Validate required columns exist
        self.validate_required_columns(data_frame, required_columns)

        self.rich_output.info(f"CSV processing complete for {file_path}")
        return data_frame
