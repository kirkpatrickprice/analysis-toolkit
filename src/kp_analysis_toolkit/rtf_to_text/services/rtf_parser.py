from __future__ import annotations

from pathlib import Path
from typing import Protocol

from kp_analysis_toolkit.utils.rich_output import RichOutput


class RTFDecoder(Protocol):
    """Protocol for RTF decoding operations."""

    def decode_rtf(self, rtf_content: bytes) -> str: ...
    def validate_rtf_format(self, file_path: Path) -> bool: ...


class TextCleaner(Protocol):
    """Protocol for text cleaning operations."""

    def clean_text(self, raw_text: str) -> str: ...
    def remove_control_characters(self, text: str) -> str: ...


class EncodingConverter(Protocol):
    """Protocol for encoding conversion."""

    def convert_encoding(self, text: str, target_encoding: str) -> str: ...
    def detect_text_encoding(self, text: str) -> str: ...


class RTFParserService:
    """Service for parsing RTF files and converting to text."""

    def __init__(
        self,
        rtf_decoder: RTFDecoder,
        text_cleaner: TextCleaner,
        encoding_converter: EncodingConverter,
        rich_output: RichOutput,
    ) -> None:
        self.rtf_decoder = rtf_decoder
        self.text_cleaner = text_cleaner
        self.encoding_converter = encoding_converter
        self.rich_output = rich_output

    def convert_rtf_to_text(
        self,
        rtf_file_path: Path,
        output_encoding: str = "utf-8",
    ) -> str:
        """Convert RTF file to clean text format."""
        try:
            # Validate RTF format
            if not self.rtf_decoder.validate_rtf_format(rtf_file_path):
                raise ValueError(f"Invalid RTF format: {rtf_file_path}")

            # Read and decode RTF content
            with open(rtf_file_path, "rb") as f:
                rtf_content = f.read()

            raw_text = self.rtf_decoder.decode_rtf(rtf_content)

            # Clean the extracted text
            cleaned_text = self.text_cleaner.clean_text(raw_text)

            # Convert encoding if needed
            final_text = self.encoding_converter.convert_encoding(
                cleaned_text,
                output_encoding,
            )

            self.rich_output.success(f"Successfully converted RTF: {rtf_file_path}")
            return final_text

        except Exception as e:
            self.rich_output.error(f"Failed to convert RTF file {rtf_file_path}: {e}")
            raise
