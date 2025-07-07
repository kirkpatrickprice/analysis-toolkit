from typing import Any

import pytest  # noqa: F401

from kp_analysis_toolkit.process_scripts.models.search.base import MergeFieldConfig
from kp_analysis_toolkit.process_scripts.search_engine import merge_result_fields


class TestMergeResultFields:
    """Tests for the merge_result_fields function."""

    def test_basic_merge(self) -> None:
        """Test basic field merging with populated source fields."""
        # Setup
        extracted_fields: dict[str, Any] = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
        }
        merge_config: list[MergeFieldConfig] = [
            MergeFieldConfig(
                source_columns=["field1", "field2"],
                dest_column="merged_field",
            ),
        ]

        # Execute
        result: dict[str, Any] = merge_result_fields(extracted_fields, merge_config)

        # Verify
        assert "merged_field" in result
        assert result["merged_field"] == "value1"  # First non-empty value
        assert "field1" not in result  # Source fields should be removed
        assert "field2" not in result
        assert "field3" in result  # Unrelated field should remain

    def test_empty_source_fields(self) -> None:
        """Test merging when first source field is empty."""
        # Setup
        extracted_fields: dict[str, Any] = {
            "field1": "",
            "field2": "value2",
            "field3": "value3",
        }
        merge_config: list[MergeFieldConfig] = [
            MergeFieldConfig(
                source_columns=["field1", "field2"],
                dest_column="merged_field",
            ),
        ]

        # Execute
        result: dict[str, Any] = merge_result_fields(extracted_fields, merge_config)

        # Verify
        assert "merged_field" in result
        assert result["merged_field"] == "value2"  # Second field since first is empty
        assert "field1" not in result
        assert "field2" not in result
        assert "field3" in result

    def test_all_empty_source_fields(self) -> None:
        """Test merging when all source fields are empty."""
        # Setup
        extracted_fields: dict[str, Any] = {
            "field1": "",
            "field2": "",
            "field3": "value3",
        }
        merge_config: list[MergeFieldConfig] = [
            MergeFieldConfig(
                source_columns=["field1", "field2"],
                dest_column="merged_field",
            ),
        ]

        # Execute
        result: dict[str, Any] = merge_result_fields(extracted_fields, merge_config)

        # Verify
        assert "merged_field" not in result  # No value to merge
        assert "field1" not in result
        assert "field2" not in result
        assert "field3" in result

    def test_no_merge_config(self) -> None:
        """Test when merge_fields_config is empty."""
        # Setup
        extracted_fields: dict[str, Any] = {"field1": "value1", "field2": "value2"}

        # Execute
        result: dict[str, Any] = merge_result_fields(extracted_fields, [])

        # Verify
        assert result == extracted_fields  # Should return original dict unchanged

    def test_empty_extracted_fields(self) -> None:
        """Test when extracted_fields is empty."""
        # Setup
        merge_config: list[MergeFieldConfig] = [
            MergeFieldConfig(
                source_columns=["field1", "field2"],
                dest_column="merged_field",
            ),
        ]

        # Execute
        result: dict[str, Any] = merge_result_fields({}, merge_config)

        # Verify
        assert result == {}  # Should return empty dict

    def test_multiple_merges(self) -> None:
        """Test multiple merge operations in the same call."""
        # Setup
        extracted_fields: dict[str, Any] = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
            "field4": "value4",
        }
        merge_config: list[MergeFieldConfig] = [
            MergeFieldConfig(
                source_columns=["field1", "field2"],
                dest_column="merged1",
            ),
            MergeFieldConfig(
                source_columns=["field3", "field4"],
                dest_column="merged2",
            ),
        ]

        # Execute
        result: dict[str, Any] = merge_result_fields(extracted_fields, merge_config)

        # Verify
        assert "merged1" in result
        assert "merged2" in result
        assert result["merged1"] == "value1"
        assert result["merged2"] == "value3"
        assert "field1" not in result
        assert "field2" not in result
        assert "field3" not in result
        assert "field4" not in result

    def test_missing_source_fields(self) -> None:
        """Test when some source fields don't exist in extracted_fields."""
        # Setup
        extracted_fields: dict[str, Any] = {
            "field1": "value1",
            # field2 doesn't exist
            "field3": "value3",
        }
        merge_config: list[MergeFieldConfig] = [
            MergeFieldConfig(
                source_columns=["field1", "field2"],
                dest_column="merged_field",
            ),
        ]

        # Execute
        result: dict[str, Any] = merge_result_fields(extracted_fields, merge_config)

        # Verify
        assert "merged_field" in result
        assert result["merged_field"] == "value1"  # Only existing field used
        assert "field1" not in result
        assert "field3" in result

    def test_nonstring_values(self) -> None:
        """Test merging with non-string values."""
        # Setup
        extracted_fields: dict[str, Any] = {
            "field1": 123,
            "field2": True,
            "field3": None,
        }
        merge_config: list[MergeFieldConfig] = [
            MergeFieldConfig(
                source_columns=["field1", "field2", "field3"],
                dest_column="merged_field",
            ),
        ]

        # Execute
        result: dict[str, Any] = merge_result_fields(extracted_fields, merge_config)

        # Verify
        assert "merged_field" in result
        assert result["merged_field"] == 123  # First non-empty value  # noqa: PLR2004
        assert "field1" not in result
        assert "field2" not in result
        assert "field3" not in result

    def test_overlapping_source_fields(self) -> None:
        """Test when the same field is used in multiple merge configs."""
        # Setup
        extracted_fields: dict[str, Any] = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
        }
        merge_config: list[MergeFieldConfig] = [
            MergeFieldConfig(
                source_columns=["field1", "field2"],
                dest_column="merged1",
            ),
            MergeFieldConfig(
                source_columns=["field2", "field3"],
                dest_column="merged2",
            ),
        ]

        # Execute
        result: dict[str, Any] = merge_result_fields(extracted_fields, merge_config)

        # Verify
        assert "merged1" in result
        assert "merged2" in result
        assert result["merged1"] == "value1"
        assert result["merged2"] == "value2"
        assert "field1" not in result
        assert "field2" not in result
        assert "field3" not in result
