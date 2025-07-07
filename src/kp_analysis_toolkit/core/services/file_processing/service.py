"""Main file processing service implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.utils.rich_output import RichOutput

    from .protocols import EncodingDetector, FileValidator, HashGenerator


class FileProcessingService:
    """Service for all file processing operations."""

    def __init__(
        self,
        encoding_detector: EncodingDetector,
        hash_generator: HashGenerator,
        file_validator: FileValidator,
        rich_output: RichOutput,
    ) -> None:
        """
        Initialize the file processing service.

        Args:
            encoding_detector: Service for detecting file encodings
            hash_generator: Service for generating file hashes
            file_validator: Service for validating file paths
            rich_output: Service for rich console output

        """
        self.encoding_detector: EncodingDetector = encoding_detector
        self.hash_generator: HashGenerator = hash_generator
        self.file_validator: FileValidator = file_validator
        self.rich_output: RichOutput = rich_output

    def process_file(self, file_path: Path) -> dict[str, str | None]:
        """
        Process a file and return metadata.

        Args:
            file_path: Path to the file to process

        Returns:
            Dictionary containing file metadata including encoding, hash, and path.
            Returns empty dict if file validation fails.

        """
        if not self.file_validator.validate_file_exists(file_path):
            self.rich_output.error(f"File not found: {file_path}")
            return {}

        encoding: str | None = self.encoding_detector.detect_encoding(file_path)
        if encoding is None:
            self.rich_output.warning(f"Could not detect encoding for: {file_path}")
            return {}

        file_hash: str = self.hash_generator.generate_hash(file_path)

        return {
            "encoding": encoding,
            "hash": file_hash,
            "path": str(file_path),
        }
