# AI-GEN: claude-3.5-sonnet|2025-01-19|batch-processing-service|reviewed:yes
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
# END AI-GEN
