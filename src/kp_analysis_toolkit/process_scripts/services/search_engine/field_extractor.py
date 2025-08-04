"""Field extractor service implementation using dependency injection."""

from __future__ import annotations

import re  # noqa: TC003
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kp_analysis_toolkit.process_scripts.models.search.merge_fields import (
        MergeFieldConfig,
    )


class DefaultFieldExtractor:
    """Service for extracting fields from search matches using DI services."""

    def extract_fields_from_match(
        self,
        match: re.Match[str],
        field_list: list[str] | None,
    ) -> dict[str, str | None | float]:
        """
        Extract named group fields from a regex match.

        Args:
            match: Regex match object containing named groups
            field_list: Optional list of specific fields to extract

        Returns:
            Dictionary of extracted field names and values

        """
        if not match:
            return {}

        # Get all named groups from the match
        all_groups = match.groupdict()

        # If field_list is specified, only return those fields
        if field_list:
            extracted = {}
            for field_name in field_list:
                if field_name in all_groups:
                    value = all_groups[field_name]
                    # Try to convert to numeric if possible
                    extracted[field_name] = self._try_convert_to_numeric(value)
                else:
                    extracted[field_name] = None
            return extracted

        # Otherwise, return all named groups
        extracted = {}
        for field_name, value in all_groups.items():
            extracted[field_name] = self._try_convert_to_numeric(value)

        return extracted

    def merge_result_fields(
        self,
        extracted_fields: dict[str, Any],
        merge_fields_config: list[MergeFieldConfig],
    ) -> dict[str, Any]:
        """
        Merge multiple source fields into destination fields.

        Uses a "first non-empty value" strategy where the first non-empty value
        from the source columns becomes the destination column value.

        Args:
            extracted_fields: Dictionary of extracted fields
            merge_fields_config: List of merge field configurations

        Returns:
            Dictionary with merged fields applied and source columns removed

        """
        if not merge_fields_config:
            return extracted_fields

        # Work with a copy to avoid modifying the original
        result_fields = extracted_fields.copy()
        columns_to_remove: set[str] = set()

        for merge_config in merge_fields_config:
            source_columns = merge_config.source_columns
            dest_column = merge_config.dest_column

            # Find the first non-empty value from source columns
            merged_value = None
            for col in source_columns:
                if extracted_fields.get(col):
                    merged_value = extracted_fields[col]
                    break

            # Add the merged column to the results
            if merged_value is not None:
                result_fields[dest_column] = merged_value

            # Mark source columns for removal
            columns_to_remove.update(source_columns)

        # Remove all source columns after merging
        for column in columns_to_remove:
            result_fields.pop(column, None)

        return result_fields

    def _try_convert_to_numeric(self, value: str | None) -> str | None | float:
        """
        Try to convert a string value to a numeric type.

        Args:
            value: String value to convert

        Returns:
            Numeric value if conversion succeeds, original string otherwise

        """
        if value is None:
            return None

        # Try to convert to float
        try:
            # Check if it's an integer
            if "." not in str(value) and value.isdigit():
                return float(int(value))
            # Otherwise try float conversion
            return float(value)
        except (ValueError, TypeError):
            return value
