"""File encoding detection implementations for the file processing service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from charset_normalizer import CharsetMatch, from_path

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.rich_output import RichOutputService


class CharsetNormalizerEncodingDetector:
    """Encoding detector using charset-normalizer for file processing."""

    def detect_encoding(self, file_path: Path) -> str | None:
        """
        Detect the encoding of a file using charset-normalizer.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected encoding name, or None if detection fails

        Raises:
            OSError: If file access errors occur
            Exception: If charset-normalizer fails

        """
        result: CharsetMatch | None = from_path(file_path).best()

        if result is not None:
            return result.encoding

        return None


class RobustEncodingDetector:
    """Robust encoding detector with error handling for file processing."""

    def __init__(
        self,
        rich_output: RichOutputService | None = None,
        *,
        enable_warnings: bool = True,
    ) -> None:
        """
        Initialize the robust encoding detector.

        Args:
            rich_output: Rich output service for logging warnings
            enable_warnings: Whether to log warnings for detection failures

        """
        self.rich_output = rich_output
        self.enable_warnings = enable_warnings
        self._detector = CharsetNormalizerEncodingDetector()

    def detect_encoding(self, file_path: Path) -> str | None:
        """
        Detect the encoding of a file with robust error handling.

        Args:
            file_path: Path to the file to analyze

        Returns:
            The detected encoding name, or None if detection fails

        """
        try:
            return self._detector.detect_encoding(file_path)
        except (OSError, Exception):
            if self.enable_warnings and self.rich_output is not None:
                self.rich_output.warning(
                    f"Skipping file due to encoding detection failure: {file_path}",
                )
            return None
