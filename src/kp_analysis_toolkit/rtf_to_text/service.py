from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.rtf_to_text.services.rtf_parser import RTFParserService
    from kp_analysis_toolkit.utils.rich_output import RichOutput


class RtfToTextService:
    """Main service for the RTF to text module."""

    def __init__(
        self,
        rtf_parser: RTFParserService,
        file_processing: FileProcessingService,
        rich_output: RichOutput,
    ) -> None:
        self.rtf_parser: RTFParserService = rtf_parser
        self.file_processing: FileProcessingService = file_processing
        self.rich_output: RichOutput = rich_output

    def execute(
        self,
        input_path: Path,
        output_directory: Path,
        *,
        preserve_structure: bool = True,
    ) -> None:
        """Execute RTF to text conversion workflow."""
        try:
            self.rich_output.header("Starting RTF to Text Conversion")

            # Discover RTF files
            rtf_files: list[Path] = self._discover_rtf_files(input_path)

            if not rtf_files:
                self.rich_output.warning("No RTF files found")
                return

            # Process each RTF file
            for rtf_file in rtf_files:
                self._convert_single_file(
                    rtf_file,
                    output_directory,
                    preserve_structure,
                )

            self.rich_output.success(
                f"Successfully converted {len(rtf_files)} RTF files",
            )

        except Exception as e:
            self.rich_output.error(f"RTF to Text conversion failed: {e}")
            raise

    def _discover_rtf_files(self, path: Path) -> list[Path]:
        """Discover RTF files in the input path."""
        if path.is_file() and path.suffix.lower() == ".rtf":
            return [path]
        if path.is_dir():
            return list(path.rglob("*.rtf"))
        return []

    def _convert_single_file(
        self,
        rtf_file: Path,
        output_directory: Path,
        *,
        preserve_structure: bool,
    ) -> None:
        """Convert a single RTF file to text."""
        try:
            # Convert RTF to text
            text_content: str = self.rtf_parser.convert_rtf_to_text(rtf_file)

            # Determine output path
            output_path: Path = self._determine_output_path(
                rtf_file,
                output_directory,
                preserve_structure,
            )

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write text file
            with output_path.open("w", encoding="utf-8") as f:
                f.write(text_content)

            self.rich_output.info(f"Converted: {rtf_file} -> {output_path}")

        except Exception as e:
            self.rich_output.error(f"Failed to convert {rtf_file}: {e}")
            raise

    def _determine_output_path(
        self,
        rtf_file: Path,
        output_directory: Path,
        *,
        preserve_structure: bool,
    ) -> Path:
        """Determine the output path for the converted text file."""
        if preserve_structure:
            # Maintain directory structure
            relative_path: Path = rtf_file.relative_to(rtf_file.anchor)
            output_path: Path = output_directory / relative_path
        else:
            # Flat structure
            output_path: Path = output_directory / rtf_file.name

        # Change extension to .txt
        return output_path.with_suffix(".txt")
