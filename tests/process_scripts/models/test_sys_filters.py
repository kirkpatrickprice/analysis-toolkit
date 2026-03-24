"""Tests for SystemFilter.validate_value_for_operator()."""
import pytest
from pydantic import ValidationError

from kp_analysis_toolkit.process_scripts.models.search.sys_filters import SystemFilter


class TestSystemFilterValidation:
    """Tests for the value/operator compatibility validator on SystemFilter."""

    def test_in_operator_with_list_is_valid(self) -> None:
        """IN operator accepts a list value."""
        f = SystemFilter(attr="os_family", comp="in", value=["Windows", "Linux"])
        assert f.value == ["Windows", "Linux"]

    def test_in_operator_with_set_is_valid(self) -> None:
        """IN operator accepts a set value."""
        f = SystemFilter(attr="os_family", comp="in", value={"Windows", "Linux"})
        assert isinstance(f.value, set)

    def test_in_operator_with_string_raises_validation_error(self) -> None:
        """IN operator rejects a plain string value."""
        with pytest.raises(ValidationError, match="'in' operator requires a list or set value"):
            SystemFilter(attr="os_family", comp="in", value="Windows")

    def test_gt_operator_with_list_raises_validation_error(self) -> None:
        """GT operator rejects list values."""
        with pytest.raises(ValidationError):
            SystemFilter(attr="producer_version", comp="gt", value=["1.0", "2.0"])

    def test_lt_operator_with_list_raises_validation_error(self) -> None:
        """LT operator rejects list values."""
        with pytest.raises(ValidationError):
            SystemFilter(attr="producer_version", comp="lt", value=["1.0"])

    def test_ge_operator_with_set_raises_validation_error(self) -> None:
        """GE operator rejects set values."""
        with pytest.raises(ValidationError):
            SystemFilter(attr="producer_version", comp="ge", value={"1.0"})

    def test_le_operator_with_set_raises_validation_error(self) -> None:
        """LE operator rejects set values."""
        with pytest.raises(ValidationError):
            SystemFilter(attr="producer_version", comp="le", value={"1.0"})

    def test_eq_operator_with_string_is_valid(self) -> None:
        """EQ operator accepts a plain string value."""
        f = SystemFilter(attr="os_family", comp="eq", value="Windows")
        assert f.value == "Windows"

    def test_eq_operator_with_int_is_valid(self) -> None:
        """EQ operator accepts an integer value."""
        f = SystemFilter(attr="producer_version", comp="eq", value=1)
        assert f.value == 1  # noqa: PLR2004
