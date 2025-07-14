"""Protocol definitions for RTF to text conversion services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path


class RtfConverter(Protocol):
    """Protocol for RTF to text conversion operations."""

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
        ...

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
            PermissionError: If write permissions are insufficient

        """
        ...


class RtfToTextService(Protocol):
    """Protocol for the main RTF to text service that orchestrates conversion operations."""

    def convert_file(self, input_file: Path, output_file: Path) -> None:
        """
        Convert a single RTF file to text format.

        Args:
            input_file: Path to the RTF file to convert
            output_file: Path where the converted text should be saved

        Raises:
            FileNotFoundError: If the input file doesn't exist
            ValueError: If the file processing fails or is not a valid RTF file
            OSError: If the output file cannot be written
            PermissionError: If write permissions are insufficient

        """
        ...

    def convert_files_batch(
        self,
        input_files: list[Path],
        output_directory: Path,
        *,
        preserve_structure: bool = True,
    ) -> None:
        """
        Convert multiple RTF files to text format.

        Args:
            input_files: List of RTF files to convert
            output_directory: Directory where converted files should be saved
            preserve_structure: Whether to preserve directory structure

        Raises:
            ValueError: If no input files are provided or conversion fails

        """
        ...

    def discover_rtf_files(self, input_path: Path) -> list[Path]:
        """
        Discover RTF files in the given path.

        Args:
            input_path: Path to search for RTF files (file or directory)

        Returns:
            List of RTF file paths found

        """
        ...
