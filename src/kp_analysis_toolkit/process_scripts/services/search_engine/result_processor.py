"""Result processor service implementation using dependency injection."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kp_analysis_toolkit.process_scripts.models.results.search import SearchResult
    from kp_analysis_toolkit.process_scripts.models.results.system import Systems
    from kp_analysis_toolkit.process_scripts.models.search.configs import SearchConfig


class DefaultResultProcessor:
    """Service for processing and managing search results using DI services."""

    def create_search_result(
        self,
        search_config: SearchConfig,  # noqa: ARG002
        system: Systems,
        text: str,
        line_num: int,
        matching_dict: dict[str, str | Any],
    ) -> SearchResult:
        """
        Create a SearchResult object from search data.

        Args:
            search_config: Search configuration used
            system: System where the result was found
            text: Matched text content
            line_num: Line number where match was found
            matching_dict: Dictionary of extracted fields

        Returns:
            SearchResult object

        """
        # Import here to avoid circular imports
        from kp_analysis_toolkit.process_scripts.models.results.search import (
            SearchResult,
        )

        # Filter out illegal Excel characters
        clean_text = self.filter_excel_illegal_chars(text)

        # Filter out illegal Excel characters from extracted fields
        clean_dict: dict[str, str | float | None] = {}
        for key, value in matching_dict.items():
            if value is None:
                clean_dict[key] = None
            elif isinstance(value, str):
                clean_dict[key] = self.filter_excel_illegal_chars(value)
            else:
                # Preserve numeric types (int, float)
                clean_dict[key] = value

        return SearchResult(
            system_name=system.system_name,
            line_number=line_num,
            matched_text=clean_text,
            extracted_fields=clean_dict if clean_dict else None,
        )

    def deduplicate_results(self, results: list[SearchResult]) -> list[SearchResult]:
        """
        Remove duplicate results based on unique criteria.

        Args:
            results: List of search results to deduplicate

        Returns:
            List of unique search results

        """
        if not results:
            return results

        unique_results = []
        seen_combinations = set()

        for result in results:
            # Create a unique key based on system name and matched text
            key = (result.system_name, result.matched_text.strip())

            # If we haven't seen this combination before, add it
            if key not in seen_combinations:
                seen_combinations.add(key)
                unique_results.append(result)

        return unique_results

    def should_skip_line(self, line: str) -> bool:
        """
        Check if a line should be skipped based on predefined patterns.

        Lines are skipped if they contain:
        1. "###[BEGIN]"
        2. "###Processing Command:"
        3. "###Running:"
        4. "###[END]"
        5. Any comments noted by "###" (noted by three or more hashes)

        Args:
            line: The line to check

        Returns:
            True if the line should be skipped, False otherwise

        """
        # Check for specific patterns first
        specific_patterns = [
            "###[BEGIN]",
            "###Processing Command:",
            "###Running:",
            "###[END]",
        ]

        for pattern in specific_patterns:
            if pattern in line:
                return True

        # Check for general ### comments (three or more hashes)
        # This will match ###, ####, #####, etc. at the beginning of lines
        return bool(re.search(r"###", line.strip()))

    def filter_excel_illegal_chars(self, text: str) -> str:
        """
        Filter out characters that are illegal in Excel.

        Args:
            text: Text to filter

        Returns:
            Filtered text safe for Excel

        """
        if not text:
            return text

        # Excel doesn't support certain control characters
        # Remove characters in ranges 0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F
        illegal_chars = [
            "\x00",
            "\x01",
            "\x02",
            "\x03",
            "\x04",
            "\x05",
            "\x06",
            "\x07",
            "\x08",
            "\x0b",
            "\x0c",
            "\x0e",
            "\x0f",
            "\x10",
            "\x11",
            "\x12",
            "\x13",
            "\x14",
            "\x15",
            "\x16",
            "\x17",
            "\x18",
            "\x19",
            "\x1a",
            "\x1b",
            "\x1c",
            "\x1d",
            "\x1e",
            "\x1f",
        ]

        filtered_text = text
        for char in illegal_chars:
            filtered_text = filtered_text.replace(char, "")

        return filtered_text
