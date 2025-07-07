import pytest

from kp_analysis_toolkit.process_scripts.models.base import ValidationMixin


class TestValidationMixin:
    """Test cases for ValidationMixin."""

    def test_validate_positive_integer_with_positive_values(self) -> None:
        """Test validate_positive_integer accepts positive integers."""
        assert ValidationMixin.validate_positive_integer(1) == 1
        assert ValidationMixin.validate_positive_integer(100) == 100  # noqa: PLR2004

    def test_validate_positive_integer_with_zero(self) -> None:
        """Test validate_positive_integer rejects zero."""
        with pytest.raises(ValueError) as excinfo:
            ValidationMixin.validate_positive_integer(0)
        assert "must be a positive integer" in str(excinfo.value)

    def test_validate_positive_integer_with_negative_values(self) -> None:
        """Test validate_positive_integer rejects negative values."""
        with pytest.raises(ValueError) as excinfo:
            ValidationMixin.validate_positive_integer(-5)
        assert "must be a positive integer" in str(excinfo.value)

    def test_validate_positive_integer_with_neg_one_allowed(self) -> None:
        """Test validate_positive_integer accepts -1 when allowed."""
        assert ValidationMixin.validate_positive_integer(-1, allow_neg_one=True) == -1

    def test_validate_positive_integer_with_neg_one_not_allowed(self) -> None:
        """Test validate_positive_integer rejects -1 when not allowed."""
        with pytest.raises(ValueError) as excinfo:
            ValidationMixin.validate_positive_integer(-1)
        assert "must be a positive integer" in str(excinfo.value)

    def test_validate_non_empty_string_with_valid_string(self) -> None:
        """Test validate_non_empty_string accepts valid strings."""
        assert ValidationMixin.validate_non_empty_string("hello") == "hello"
        assert ValidationMixin.validate_non_empty_string("123") == "123"

    def test_validate_non_empty_string_with_empty_string(self) -> None:
        """Test validate_non_empty_string rejects empty strings."""
        with pytest.raises(ValueError) as excinfo:
            ValidationMixin.validate_non_empty_string("")
        assert "String cannot be empty" in str(excinfo.value)

    def test_validate_non_empty_string_with_whitespace_string(self) -> None:
        """Test validate_non_empty_string rejects whitespace-only strings."""
        with pytest.raises(ValueError) as excinfo:
            ValidationMixin.validate_non_empty_string("   ")
        assert "String cannot be empty" in str(excinfo.value)

    def test_validate_non_empty_string_with_none(self) -> None:
        """Test validate_non_empty_string passes None through unchanged."""
        assert ValidationMixin.validate_non_empty_string(None) is None

    def test_validate_sys_filter_value_collection_allowed_with_collection(self) -> None:
        """Test validate_sys_filter_value accepts collections when allowed."""
        assert ValidationMixin.validate_sys_filter_value([1, 2, 3], "in") == [1, 2, 3]
        assert ValidationMixin.validate_sys_filter_value({1, 2, 3}, "in") == {1, 2, 3}

    def test_validate_sys_filter_value_collection_allowed_with_non_collection(
        self,
    ) -> None:
        """Test validate_sys_filter_value rejects non-collections when collections required."""
        with pytest.raises(ValueError) as excinfo:
            ValidationMixin.validate_sys_filter_value(5, "in")
        assert "requires a collection value" in str(excinfo.value)

    def test_validate_sys_filter_value_collection_not_allowed_with_collection(
        self,
    ) -> None:
        """Test validate_sys_filter_value rejects collections when not allowed."""
        with pytest.raises(ValueError) as excinfo:
            ValidationMixin.validate_sys_filter_value(
                [1, 2, 3],
                "eq",
                collection_allowed=False,
            )
        assert "cannot be used with collection values" in str(excinfo.value)

    def test_validate_sys_filter_value_collection_not_allowed_with_non_collection(
        self,
    ) -> None:
        """Test validate_sys_filter_value accepts non-collections when collections not required."""
        assert (
            ValidationMixin.validate_sys_filter_value(5, "eq", collection_allowed=False)
            == 5  # noqa: PLR2004
        )
        assert (
            ValidationMixin.validate_sys_filter_value(
                "text",
                "eq",
                collection_allowed=False,
            )
            == "text"
        )
