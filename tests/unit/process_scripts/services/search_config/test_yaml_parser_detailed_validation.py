"""Tests for detailed YAML parser validation functionality."""

import pytest

from kp_analysis_toolkit.core.services.file_processing.service import (
    FileProcessingService,
)
from kp_analysis_toolkit.process_scripts.services.search_config.yaml_parser import (
    PyYamlParser,
)


class TestYamlParserDetailedValidation:
    """Test class for detailed YAML parser validation."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        file_processing = FileProcessingService()
        self.parser = PyYamlParser(file_processing)

    def test_validate_yaml_structure_detailed_missing_keywords_field(self) -> None:
        """Test that missing keywords field is reported specifically."""
        data = {
            "test_search": {
                "regex": "test_pattern",
                "excel_sheet_name": "Test Sheet",
                "comment": "Test comment",
                # Missing keywords field
            },
        }

        with pytest.raises(
            ValueError,
            match=r".*missing required fields.*'keywords'.*",
        ):
            self.parser.validate_yaml_structure_detailed(data)

    def test_validate_yaml_structure_detailed_multiple_missing_fields(self) -> None:
        """Test that multiple missing fields are reported."""
        data = {
            "test_search": {
                "regex": "test_pattern",
                # Missing excel_sheet_name, comment, and keywords
            },
        }

        with pytest.raises(ValueError) as exc_info:
            self.parser.validate_yaml_structure_detailed(data)

        error_message = str(exc_info.value)
        assert "missing required fields" in error_message
        assert "excel_sheet_name" in error_message
        assert "comment" in error_message
        assert "keywords" in error_message

    def test_validate_yaml_structure_detailed_invalid_regex(self) -> None:
        """Test that invalid regex patterns are reported specifically."""
        data = {
            "test_search": {
                "regex": "[invalid regex",  # Invalid regex pattern
                "excel_sheet_name": "Test Sheet",
                "comment": "Test comment",
                "keywords": ["test"],
            },
        }

        with pytest.raises(ValueError, match=r".*Invalid regex pattern.*"):
            self.parser.validate_yaml_structure_detailed(data)

    def test_validate_yaml_structure_detailed_invalid_data_type(self) -> None:
        """Test that invalid data types are reported specifically."""
        data = "not a dictionary"  # Should be a dict

        with pytest.raises(TypeError, match=r"YAML data must be a dictionary"):
            self.parser.validate_yaml_structure_detailed(data)

    def test_validate_yaml_structure_detailed_invalid_section_type(self) -> None:
        """Test that invalid section types are reported specifically."""
        data = {
            "test_search": "not a dictionary",  # Should be a dict
        }

        with pytest.raises(
            ValueError,
            match=r".*Search section must be a dictionary.*",
        ):
            self.parser.validate_yaml_structure_detailed(data)

    def test_validate_yaml_structure_detailed_invalid_global_section(self) -> None:
        """Test that invalid global section types are reported specifically."""
        data = {
            "global": "not a dictionary",  # Should be a dict
        }

        with pytest.raises(TypeError, match=r"Global section must be a dictionary"):
            self.parser.validate_yaml_structure_detailed(data)

    def test_validate_yaml_structure_detailed_invalid_include_section(self) -> None:
        """Test that invalid include section types are reported specifically."""
        data = {
            "include_something": {
                # Missing 'files' key
            },
        }

        with pytest.raises(
            ValueError,
            match=r"Include section must contain a 'files' key",
        ):
            self.parser.validate_yaml_structure_detailed(data)

    def test_validate_yaml_structure_detailed_invalid_include_files_type(self) -> None:
        """Test that invalid include files types are reported specifically."""
        data = {
            "include_something": {
                "files": "not a list",  # Should be a list
            },
        }

        with pytest.raises(TypeError, match=r"Include section 'files' must be a list"):
            self.parser.validate_yaml_structure_detailed(data)

    def test_validate_yaml_structure_detailed_valid_data_passes(self) -> None:
        """Test that valid data passes detailed validation."""
        data = {
            "test_search": {
                "regex": "valid_pattern",
                "excel_sheet_name": "Test Sheet",
                "comment": "Test comment",
                "keywords": ["test", "keywords"],
            },
        }

        # Should not raise any exception
        self.parser.validate_yaml_structure_detailed(data)

    def test_validate_yaml_structure_boolean_method_still_works(self) -> None:
        """Test that the boolean validation method still works as before."""
        # Valid data
        valid_data = {
            "test_search": {
                "regex": "valid_pattern",
                "excel_sheet_name": "Test Sheet",
                "comment": "Test comment",
                "keywords": ["test", "keywords"],
            },
        }
        assert self.parser.validate_yaml_structure(valid_data) is True

        # Invalid data
        invalid_data = {
            "test_search": {
                "regex": "valid_pattern",
                # Missing required fields
            },
        }
        assert self.parser.validate_yaml_structure(invalid_data) is False

    def test_section_specific_error_messages(self) -> None:
        """Test that section-specific error messages are provided."""
        data = {
            "test_search": {
                "regex": "valid_pattern",
                # Missing other required fields
            },
        }

        with pytest.raises(ValueError) as exc_info:
            self.parser.validate_yaml_structure_detailed(data)

        error_message = str(exc_info.value)
        assert "section 'test_search'" in error_message
        assert "missing required fields" in error_message

    def test_regex_validation_with_detailed_error(self) -> None:
        """Test detailed regex validation error messages."""
        data = {
            "test_search": {
                "regex": 123,  # Wrong type
                "excel_sheet_name": "Test Sheet",
                "comment": "Test comment",
                "keywords": ["test"],
            },
        }

        with pytest.raises(TypeError, match=r"Regex pattern must be a string"):
            self.parser.validate_yaml_structure_detailed(data)
