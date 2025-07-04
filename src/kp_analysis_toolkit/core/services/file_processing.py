from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.utils.rich_output import RichOutput


class EncodingDetector(Protocol):
    """Protocol for file encoding detection."""

    def detect_encoding(self, file_path: Path) -> str | None: ...


class HashGenerator(Protocol):
    """Protocol for file hash generation."""

    def generate_hash(self, file_path: Path) -> str: ...


class FileValidator(Protocol):
    """Protocol for file validation."""

    def validate_file_exists(self, file_path: Path) -> bool: ...
    def validate_directory_exists(self, dir_path: Path) -> bool: ...


class FileProcessingService:
    """Service for all file processing operations."""

    def __init__(
        self,
        encoding_detector: EncodingDetector,
        hash_generator: HashGenerator,
        file_validator: FileValidator,
        rich_output: RichOutput,
    ) -> None:
        self.encoding_detector = encoding_detector
        self.hash_generator = hash_generator
        self.file_validator = file_validator
        self.rich_output = rich_output

    def process_file(self, file_path: Path) -> dict[str, str | None]:
        """Process a file and return metadata."""
        if not self.file_validator.validate_file_exists(file_path):
            self.rich_output.error(f"File not found: {file_path}")
            return {}

        encoding = self.encoding_detector.detect_encoding(file_path)
        if encoding is None:
            self.rich_output.warning(f"Could not detect encoding for: {file_path}")
            return {}

        file_hash = self.hash_generator.generate_hash(file_path)

        return {
            "encoding": encoding,
            "hash": file_hash,
            "path": str(file_path),
        }
