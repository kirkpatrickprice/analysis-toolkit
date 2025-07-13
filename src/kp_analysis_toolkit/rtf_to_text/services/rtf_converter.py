"""RTF conversion service using dependency injection."""

from __future__ import annotations

import re
from pathlib import Path  # noqa: TC003  # Path is used at runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService


class RtfConverterService:
    """Service for converting RTF files to plain text using DI services."""

    def __init__(
        self,
        rich_output: RichOutputService,
        file_processing: FileProcessingService,
    ) -> None:
        """
        Initialize the RTF converter service.

        Args:
            rich_output: Service for rich terminal output
            file_processing: Service for file processing operations

        """
        self.rich_output = rich_output
        self.file_processing = file_processing

    def convert_rtf_to_text(self, rtf_file_path: Path) -> str:
        """
        Convert an RTF file to plain text.

        Args:
            rtf_file_path: Path to the RTF file to convert

        Returns:
            Plain text content extracted from the RTF file

        Raises:
            FileNotFoundError: If the input file doesn't exist
            ValueError: If the file processing fails or file is not RTF format

        """
        # Validate input file exists
        if not rtf_file_path.exists():
            error_msg = f"Input file not found: {rtf_file_path}"
            self.rich_output.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Validate RTF file extension
        if rtf_file_path.suffix.lower() != ".rtf":
            error_msg = f"Input file must have .rtf extension: {rtf_file_path}"
            self.rich_output.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Try using striprtf first (preferred for pure Python)
            return self._convert_with_striprtf(rtf_file_path)
        except ImportError:
            # Fallback to basic RTF parsing if striprtf is not available
            self.rich_output.warning(
                "striprtf library not available, using basic RTF parsing",
            )
            return self._convert_with_basic_parser(rtf_file_path)

    def _convert_with_striprtf(self, rtf_file_path: Path) -> str:
        """Convert RTF file using the striprtf library."""
        from striprtf.striprtf import rtf_to_text

        # Detect file encoding using the file processing service
        detected_encoding = self.file_processing.detect_encoding(rtf_file_path)

        if detected_encoding != "unknown":
            rtf_content = rtf_file_path.read_text(encoding=detected_encoding)
        else:
            # Fallback to utf-8 with error handling if detection fails
            rtf_content = rtf_file_path.read_text(encoding="utf-8", errors="ignore")
            self.rich_output.warning(
                f"Could not detect encoding for {rtf_file_path}, using UTF-8 with error handling",
            )

        # Convert RTF to plain text
        plain_text = rtf_to_text(rtf_content)

        self.rich_output.debug(f"Successfully converted {rtf_file_path} using striprtf")
        # Ensure we return a string even if striprtf returns Any
        return str(plain_text) if plain_text is not None else ""

    def _convert_with_basic_parser(self, rtf_file_path: Path) -> str:
        """
        Basic RTF to text conversion fallback.

        This is a simple fallback that strips basic RTF formatting.
        It's not as comprehensive as striprtf but works for basic files.

        Args:
            rtf_file_path: Path to the RTF file

        Returns:
            Plain text content

        Raises:
            ValueError: If the file processing fails

        """
        try:
            # Detect file encoding using the file processing service
            detected_encoding = self.file_processing.detect_encoding(rtf_file_path)

            if detected_encoding != "unknown":
                rtf_content = rtf_file_path.read_text(encoding=detected_encoding)
            else:
                # Fallback to utf-8 with error handling if detection fails
                rtf_content = rtf_file_path.read_text(encoding="utf-8", errors="ignore")
                self.rich_output.warning(
                    f"Could not detect encoding for {rtf_file_path}, using UTF-8 with error handling",
                )

            # Basic RTF control sequence removal
            # Remove RTF header and control words
            text = re.sub(r"{\\rtf.*?}", "", rtf_content, flags=re.DOTALL)
            text = re.sub(r"\\[a-z]+\d*\s?", "", text)
            text = re.sub(r"\\[^a-z]", "", text)
            text = re.sub(r"[{}]", "", text)

            # Clean up whitespace
            text = re.sub(r"\s+", " ", text)
            result = text.strip()

            self.rich_output.debug(
                f"Successfully converted {rtf_file_path} using basic parser",
            )

        except Exception as e:
            error_msg = f"Failed to process RTF file {rtf_file_path}: {e}"
            self.rich_output.error(error_msg)
            raise ValueError(error_msg) from e
        else:
            return result

    def save_as_text(
        self,
        text_content: str,
        output_file_path: Path,
        *,
        encoding: str = "ascii",
    ) -> None:
        """
        Save text content to a file with specified encoding.

        Args:
            text_content: The text content to save
            output_file_path: Path where the text file should be saved
            encoding: Text encoding to use (default: "ascii")

        Raises:
            OSError: If the file cannot be written

        """
        try:
            # Ensure output directory exists
            output_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the plain text to output file with specified encoding
            output_file_path.write_text(
                text_content,
                encoding=encoding,
                errors="ignore",
            )

            self.rich_output.debug(f"Successfully saved text to {output_file_path}")

        except Exception as e:
            error_msg = f"Failed to save text file {output_file_path}: {e}"
            self.rich_output.error(error_msg)
            raise OSError(error_msg) from e
