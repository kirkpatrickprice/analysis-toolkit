from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.rtf_to_text.protocols import RtfConverter


class RtfToTextService:
    """Main service for the RTF to text module."""

    def __init__(
        self,
        rtf_converter: RtfConverter,
        rich_output: RichOutputService,
        file_processing: FileProcessingService,
    ) -> None:
        """
        Initialize the RTF to text service.

        Args:
            rtf_converter: Service for converting RTF files to text
            rich_output: Service for rich terminal output
            file_processing: Service for file processing operations

        """
        self.rtf_converter = rtf_converter
        self.rich_output = rich_output
        self.file_processing = file_processing

    def convert_file(
        self,
        input_file: Path,
        output_file: Path,
    ) -> None:
        """
        Convert a single RTF file to text format.

        Args:
            input_file: Path to the RTF file to convert
            output_file: Path where the converted text should be saved

        Raises:
            FileNotFoundError: If the input file doesn't exist
            ValueError: If the file processing fails
            OSError: If the output file cannot be written

        """
        try:
            self.rich_output.info(f"Converting RTF file: {input_file}")

            # Convert RTF to text
            text_content = self.rtf_converter.convert_rtf_to_text(input_file)

            # Save the text content
            self.rtf_converter.save_as_text(text_content, output_file, encoding="ascii")

            self.rich_output.success(f"Converted: {input_file} -> {output_file}")

        except Exception as e:
            self.rich_output.error(f"RTF conversion failed: {e}")
            raise

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
        if not input_files:
            self.rich_output.warning("No RTF files provided for conversion")
            return

        self.rich_output.header(f"Converting {len(input_files)} RTF files")

        successful_conversions = 0
        for input_file in input_files:
            try:
                # Determine output path
                output_path = self._determine_output_path(
                    input_file,
                    output_directory,
                    preserve_structure=preserve_structure,
                )

                # Convert the file
                self.convert_file(input_file, output_path)
                successful_conversions += 1

            except (FileNotFoundError, ValueError, OSError) as e:
                self.rich_output.error(f"Failed to convert {input_file}: {e}")
                # Continue processing other files

        self.rich_output.success(
            f"Successfully converted {successful_conversions}/{len(input_files)} RTF files",
        )

    def discover_rtf_files(self, input_path: Path) -> list[Path]:
        """
        Discover RTF files in the given path.

        Args:
            input_path: Path to search for RTF files (file or directory)

        Returns:
            List of RTF file paths found

        """
        if input_path.is_file() and input_path.suffix.lower() == ".rtf":
            return [input_path]
        if input_path.is_dir():
            rtf_files = list(input_path.rglob("*.rtf"))
            self.rich_output.info(f"Found {len(rtf_files)} RTF files in {input_path}")
            return rtf_files
        self.rich_output.warning(f"No RTF files found at {input_path}")
        return []

    def _determine_output_path(
        self,
        rtf_file: Path,
        output_directory: Path,
        *,
        preserve_structure: bool,
    ) -> Path:
        """Determine the output path for the converted text file."""
        if preserve_structure and rtf_file.is_absolute():
            # Try to maintain directory structure relative to a common root
            try:
                # Get relative path from the rtf file's parent directory
                relative_path = rtf_file.relative_to(rtf_file.parent)
                output_path = output_directory / relative_path
            except ValueError:
                # If relative_to fails, use flat structure
                output_path = output_directory / rtf_file.name
        else:
            # Flat structure
            output_path = output_directory / rtf_file.name

        # Change extension to .txt
        return output_path.with_suffix(".txt")
