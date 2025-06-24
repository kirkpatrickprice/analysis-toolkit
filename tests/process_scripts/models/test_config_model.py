from datetime import datetime
from pathlib import Path

import pytest  # noqa: F401
from pydantic import BaseModel  # noqa: F401

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.base import ConfigModel


class TestConfigModel(KPATBaseModel, ConfigModel):
    """Test model that inherits from both KPATBaseModel and ConfigModel."""

    string_field: str = "test string"
    int_field: int = 42
    float_field: float = 3.14
    bool_field: bool = True
    none_field: str | None = None  # Using Union syntax instead of Optional
    path_field: Path = Path("/test/path")
    datetime_field: datetime = datetime(2023, 1, 1, 12, 0, 0)  # noqa: DTZ001
    list_field: list[int] = [1, 2, 3]  # Using list[] instead of List[]  # noqa: RUF012
    dict_field: dict[str, str] = {  # noqa: RUF012
        "key": "value"  # noqa: COM812
    }  # Using dict[] instead of Dict[]


class TestConfigModelClass:
    def test_to_dict_returns_dictionary(self) -> None:
        """Test that to_dict returns a dictionary."""
        config = TestConfigModel()
        result: dict[str, str] = config.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_converts_values_to_strings(self) -> None:
        """Test that all values in the dictionary are strings."""
        config = TestConfigModel()
        result: dict[str, str] = config.to_dict()
        for value in result.values():
            assert isinstance(value, str)

    def test_to_dict_handles_none_values(self) -> None:
        """Test that None values are converted to 'None' string."""
        config = TestConfigModel()
        result: dict[str, str] = config.to_dict()
        assert result["none_field"] == "None"

    def test_to_dict_converts_different_types(self) -> None:
        """Test that different data types are properly converted to strings."""
        config = TestConfigModel()
        result: dict[str, str] = config.to_dict()

        assert result["string_field"] == "test string"
        assert result["int_field"] == "42"
        assert result["float_field"] == "3.14"
        assert result["bool_field"] == "True"
        assert (
            "path" in result["path_field"]
        )  # Path string representation contains 'path'
        assert (
            "2023-01-01" in result["datetime_field"]
        )  # datetime representation contains the date
        assert result["list_field"] == "[1, 2, 3]"
        assert result["dict_field"] == "{'key': 'value'}"

    def test_to_dict_includes_all_fields(self) -> None:
        """Test that all fields from the model are included in the dictionary."""
        config = TestConfigModel()
        result: dict[str, str] = config.to_dict()

        expected_fields = {
            "string_field",
            "int_field",
            "float_field",
            "bool_field",
            "none_field",
            "path_field",
            "datetime_field",
            "list_field",
            "dict_field",
        }

        assert set(result.keys()) == expected_fields

    def test_to_dict_with_custom_values(self) -> None:
        """Test to_dict with custom field values."""
        config = TestConfigModel(
            string_field="custom string",
            int_field=100,
            float_field=9.99,
            bool_field=False,
        )
        result: dict[str, str] = config.to_dict()

        assert result["string_field"] == "custom string"
        assert result["int_field"] == "100"
        assert result["float_field"] == "9.99"
        assert result["bool_field"] == "False"
