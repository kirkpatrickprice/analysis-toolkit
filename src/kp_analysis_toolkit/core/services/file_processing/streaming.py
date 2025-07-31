# AI-GEN: gpt-4o|2025-01-30|content-streaming-core-service|reviewed:no
"""Content streaming protocols and implementations for file processing service."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from kp_analysis_toolkit.core.services.file_processing.protocols import ContentStreamer

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


class FileContentStreamer(ContentStreamer):
    """
    Implementation of ContentStreamer for file-based content.

    Provides efficient streaming access to file content with caching for
    repeated operations and early termination for performance optimization.
    """

    def __init__(self, file_path: Path, encoding: str = "utf-8") -> None:
        """
        Initialize the file content streamer.

        Args:
            file_path: Path to the file to stream
            encoding: Character encoding of the file

        """
        self.file_path = file_path
        self.encoding = encoding
        self._cached_header: list[str] | None = None
        self._full_content_cache: list[str] | None = None

    def get_file_header(self, lines: int = 10) -> list[str]:
        """Get the first N lines of the file with caching."""
        if self._cached_header is None or len(self._cached_header) < lines:
            with self.file_path.open("r", encoding=self.encoding) as file:
                header_lines = []
                for i, file_line in enumerate(file):
                    if i >= lines:
                        break
                    header_lines.append(file_line.rstrip("\n\r"))
                self._cached_header = header_lines

        return self._cached_header[:lines]

    def stream_pattern_matches(
        self,
        pattern: str,
        *,
        max_matches: int | None = None,
        ignore_case: bool = True,
    ) -> Generator[str, None, None]:
        """Stream lines matching a regex pattern with early termination."""
        flags = re.IGNORECASE if ignore_case else 0
        compiled_pattern = re.compile(pattern, flags)
        matches_found = 0

        with self.file_path.open("r", encoding=self.encoding) as file:
            for file_line in file:
                cleaned_line = file_line.rstrip("\n\r")
                if compiled_pattern.search(cleaned_line):
                    yield cleaned_line
                    matches_found += 1
                    if max_matches is not None and matches_found >= max_matches:
                        break

    def stream_section_content(
        self,
        start_pattern: str,
        end_pattern: str | None = None,
        *,
        include_markers: bool = False,
        ignore_case: bool = True,
    ) -> Generator[str, None, None]:
        """Stream content between start and end patterns."""
        flags = re.IGNORECASE if ignore_case else 0
        start_regex = re.compile(start_pattern, flags)
        end_regex = re.compile(end_pattern, flags) if end_pattern else None

        in_section = False
        with self.file_path.open("r", encoding=self.encoding) as file:
            for file_line in file:
                cleaned_line = file_line.rstrip("\n\r")

                # Check for start pattern
                if not in_section and start_regex.search(cleaned_line):
                    in_section = True
                    if include_markers:
                        yield cleaned_line
                    continue

                # Check for end pattern
                if in_section and end_regex and end_regex.search(cleaned_line):
                    if include_markers:
                        yield cleaned_line
                    break

                # Yield content if we're in the section
                if in_section:
                    yield cleaned_line

    def stream_lines(self) -> Generator[str, None, None]:
        """Stream all lines in the file."""
        with self.file_path.open("r", encoding=self.encoding) as file:
            for file_line in file:
                yield file_line.rstrip("\n\r")

    def find_first_match(
        self,
        pattern: str,
        *,
        ignore_case: bool = True,
    ) -> str | None:
        """Find the first line matching a pattern with early termination."""
        flags = re.IGNORECASE if ignore_case else 0
        compiled_pattern = re.compile(pattern, flags)

        with self.file_path.open("r", encoding=self.encoding) as file:
            for file_line in file:
                cleaned_line = file_line.rstrip("\n\r")
                if compiled_pattern.search(cleaned_line):
                    return cleaned_line
        return None

    def search_multiple_patterns(
        self,
        patterns: dict[str, str],
        *,
        ignore_case: bool = True,
        early_termination: bool = True,
    ) -> dict[str, list[str]]:
        """
        Search for multiple patterns in a single file pass.

        Args:
            patterns: Dictionary mapping pattern names to regex patterns
            ignore_case: Whether to ignore case in pattern matching
            early_termination: Stop searching once all patterns found a match

        Returns:
            Dictionary mapping pattern names to lists of matching lines

        """
        flags = re.IGNORECASE if ignore_case else 0
        compiled_patterns = {
            name: re.compile(pattern, flags) for name, pattern in patterns.items()
        }

        results: dict[str, list[str]] = {name: [] for name in patterns}
        patterns_found = set()

        with self.file_path.open("r", encoding=self.encoding) as file:
            for file_line in file:
                cleaned_line = file_line.rstrip("\n\r")

                for pattern_name, compiled_pattern in compiled_patterns.items():
                    if compiled_pattern.search(cleaned_line):
                        results[pattern_name].append(cleaned_line)
                        patterns_found.add(pattern_name)

                # Early termination if all patterns found at least one match
                if early_termination and len(patterns_found) == len(patterns):
                    break

        return results


# END AI-GEN
