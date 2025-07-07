"""Tests for core search engine functionality."""

from unittest.mock import Mock, patch

from kp_analysis_toolkit.process_scripts.models.enums import (
    DistroFamilyType,
    OSFamilyType,
    ProducerType,
    SysFilterAttr,
    SysFilterComparisonOperators,
)
from kp_analysis_toolkit.process_scripts.models.search.sys_filters import SystemFilter
from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.process_scripts.search_engine import (
    _filter_excel_illegal_chars,
    compare_values,
    compare_version,
    evaluate_system_filters,
    get_system_attribute_value,
    system_matches_all_filters,
)


class TestCompareVersion:
    """Tests for the compare_version function."""

    def test_equal_versions(self) -> None:
        """Test equality comparison of versions."""
        assert compare_version("1.2.3", SysFilterComparisonOperators.EQUALS, "1.2.3")
        assert not compare_version(
            "1.2.3",
            SysFilterComparisonOperators.EQUALS,
            "1.2.4",
        )

    def test_greater_than_versions(self) -> None:
        """Test greater than comparison of versions."""
        assert compare_version(
            "1.2.4",
            SysFilterComparisonOperators.GREATER_THAN,
            "1.2.3",
        )
        assert compare_version(
            "2.0.0",
            SysFilterComparisonOperators.GREATER_THAN,
            "1.9.9",
        )
        assert not compare_version(
            "1.2.3",
            SysFilterComparisonOperators.GREATER_THAN,
            "1.2.3",
        )

    def test_greater_equal_versions(self) -> None:
        """Test greater than or equal comparison of versions."""
        assert compare_version(
            "1.2.3",
            SysFilterComparisonOperators.GREATER_EQUAL,
            "1.2.3",
        )
        assert compare_version(
            "1.2.4",
            SysFilterComparisonOperators.GREATER_EQUAL,
            "1.2.3",
        )
        assert not compare_version(
            "1.2.2",
            SysFilterComparisonOperators.GREATER_EQUAL,
            "1.2.3",
        )

    def test_less_than_versions(self) -> None:
        """Test less than comparison of versions."""
        assert compare_version("1.2.2", SysFilterComparisonOperators.LESS_THAN, "1.2.3")
        assert not compare_version(
            "1.2.3",
            SysFilterComparisonOperators.LESS_THAN,
            "1.2.3",
        )

    def test_less_equal_versions(self) -> None:
        """Test less than or equal comparison of versions."""
        assert compare_version(
            "1.2.3",
            SysFilterComparisonOperators.LESS_EQUAL,
            "1.2.3",
        )
        assert compare_version(
            "1.2.2",
            SysFilterComparisonOperators.LESS_EQUAL,
            "1.2.3",
        )
        assert not compare_version(
            "1.2.4",
            SysFilterComparisonOperators.LESS_EQUAL,
            "1.2.3",
        )

    def test_none_system_version(self) -> None:
        """Test handling of None system version."""
        assert (
            compare_version(None, SysFilterComparisonOperators.EQUALS, "1.2.3") is False
        )
        assert (
            compare_version(None, SysFilterComparisonOperators.GREATER_EQUAL, "1.2.3")
            is False
        )


class TestCompareValues:
    """Tests for the compare_values function."""

    def test_string_equality(self) -> None:
        """Test string equality comparison."""
        assert compare_values("test", SysFilterComparisonOperators.EQUALS, "test")
        assert compare_values(
            "TEST",
            SysFilterComparisonOperators.EQUALS,
            "test",
        )  # Case insensitive
        assert not compare_values("test", SysFilterComparisonOperators.EQUALS, "other")

    def test_numeric_comparisons(self) -> None:
        """Test numeric comparison operations."""
        assert compare_values("10", SysFilterComparisonOperators.GREATER_THAN, "5")
        assert compare_values(10, SysFilterComparisonOperators.GREATER_THAN, 5)
        assert compare_values("5", SysFilterComparisonOperators.LESS_THAN, "10")

    def test_string_comparisons_fallback(self) -> None:
        """Test that invalid numeric values fall back to string comparison."""
        assert compare_values("abc", SysFilterComparisonOperators.GREATER_THAN, "aaa")
        assert not compare_values(
            "aaa",
            SysFilterComparisonOperators.GREATER_THAN,
            "abc",
        )

    def test_in_operator(self) -> None:
        """Test the IN operator with lists."""
        assert compare_values(
            "windows",
            SysFilterComparisonOperators.IN,
            ["windows", "linux"],
        )
        assert compare_values(
            "WINDOWS",
            SysFilterComparisonOperators.IN,
            ["windows", "linux"],
        )  # Case insensitive
        assert not compare_values(
            "macos",
            SysFilterComparisonOperators.IN,
            ["windows", "linux"],
        )

    def test_in_operator_with_single_value(self) -> None:
        """Test the IN operator with single value (converted to list)."""
        assert compare_values("test", SysFilterComparisonOperators.IN, "test")

    def test_none_system_value(self) -> None:
        """Test handling of None system value."""
        assert not compare_values(None, SysFilterComparisonOperators.EQUALS, "test")
        assert not compare_values(None, SysFilterComparisonOperators.IN, ["test"])

    def test_exception_handling(self) -> None:
        """Test that exceptions return False."""
        # This should not raise an exception but return False
        result = compare_values(
            "invalid",
            SysFilterComparisonOperators.GREATER_THAN,
            None,
        )
        assert result is False


class TestGetSystemAttributeValue:
    """Tests for the get_system_attribute_value function."""

    def test_get_os_family(self) -> None:
        """Test getting OS family attribute."""
        system = Mock(spec=Systems)
        system.os_family = OSFamilyType.WINDOWS

        result = get_system_attribute_value(system, SysFilterAttr.OS_FAMILY)
        assert result == OSFamilyType.WINDOWS

    def test_get_producer(self) -> None:
        """Test getting producer attribute."""
        system = Mock(spec=Systems)
        system.producer = ProducerType.KPWINAUDIT

        result = get_system_attribute_value(system, SysFilterAttr.PRODUCER)
        assert result == ProducerType.KPWINAUDIT

    def test_get_producer_version(self) -> None:
        """Test getting producer version attribute."""
        system = Mock(spec=Systems)
        system.producer_version = "0.4.7"

        result = get_system_attribute_value(system, SysFilterAttr.PRODUCER_VERSION)
        assert result == "0.4.7"

    def test_get_distro_family(self) -> None:
        """Test getting distro family attribute."""
        system = Mock(spec=Systems)
        system.distro_family = DistroFamilyType.DEB

        result = get_system_attribute_value(system, SysFilterAttr.DISTRO_FAMILY)
        assert result == DistroFamilyType.DEB

    def test_get_product_name(self) -> None:
        """Test getting product name attribute."""
        system = Mock(spec=Systems)
        system.product_name = "Windows 10 Pro"

        result = get_system_attribute_value(system, SysFilterAttr.PRODUCT_NAME)
        assert result == "Windows 10 Pro"

    def test_get_nonexistent_attribute(self) -> None:
        """Test getting non-existent attribute returns None."""
        system = Mock(spec=Systems)
        # Remove the os_family attribute to simulate missing attribute
        if hasattr(system, "os_family"):
            delattr(system, "os_family")

        result = get_system_attribute_value(system, SysFilterAttr.OS_FAMILY)
        assert result is None


class TestSystemMatchesAllFilters:
    """Tests for the system_matches_all_filters function."""

    def test_no_filters_returns_true(self) -> None:
        """Test that empty filter list returns True."""
        system = Mock(spec=Systems)
        assert system_matches_all_filters(system, [])

    def test_single_matching_filter(self) -> None:
        """Test system matching single filter."""
        system = Mock(spec=Systems)
        system.os_family = OSFamilyType.WINDOWS

        filter_config = SystemFilter(
            attr=SysFilterAttr.OS_FAMILY,
            comp=SysFilterComparisonOperators.EQUALS,
            value="Windows",
        )

        assert system_matches_all_filters(system, [filter_config])

    def test_single_non_matching_filter(self) -> None:
        """Test system not matching single filter."""
        system = Mock(spec=Systems)
        system.os_family = OSFamilyType.LINUX

        filter_config = SystemFilter(
            attr=SysFilterAttr.OS_FAMILY,
            comp=SysFilterComparisonOperators.EQUALS,
            value="Windows",
        )

        assert not system_matches_all_filters(system, [filter_config])

    def test_multiple_matching_filters(self) -> None:
        """Test system matching multiple filters."""
        system = Mock(spec=Systems)
        system.os_family = OSFamilyType.WINDOWS
        system.producer = ProducerType.KPWINAUDIT
        system.producer_version = "0.4.7"

        filters = [
            SystemFilter(
                attr=SysFilterAttr.OS_FAMILY,
                comp=SysFilterComparisonOperators.EQUALS,
                value="Windows",
            ),
            SystemFilter(
                attr=SysFilterAttr.PRODUCER,
                comp=SysFilterComparisonOperators.EQUALS,
                value="KPWINAUDIT",
            ),
        ]

        assert system_matches_all_filters(system, filters)

    def test_mixed_matching_filters(self) -> None:
        """Test system failing on one of multiple filters."""
        system = Mock(spec=Systems)
        system.os_family = OSFamilyType.WINDOWS
        system.producer = ProducerType.KPWINAUDIT

        filters = [
            SystemFilter(
                attr=SysFilterAttr.OS_FAMILY,
                comp=SysFilterComparisonOperators.EQUALS,
                value="Windows",
            ),
            SystemFilter(
                attr=SysFilterAttr.PRODUCER,
                comp=SysFilterComparisonOperators.EQUALS,
                value="KPNIXAUDIT",  # This won't match
            ),
        ]

        assert not system_matches_all_filters(system, filters)


class TestEvaluateSystemFilters:
    """Tests for the evaluate_system_filters function."""

    def test_no_filters_returns_true(self) -> None:
        """Test that empty filter list returns True."""
        system = Mock(spec=Systems)
        assert evaluate_system_filters(system, [])

    def test_version_comparison_filter(self) -> None:
        """Test version comparison filtering."""
        system = Mock(spec=Systems)
        system.producer = ProducerType.KPWINAUDIT
        system.producer_version = "0.4.7"
        system.os_family = OSFamilyType.WINDOWS

        # Mock the is_attribute_applicable to return True for this test
        with patch(
            "kp_analysis_toolkit.process_scripts.search_engine.is_attribute_applicable",
            return_value=True,
        ):
            filter_config = SystemFilter(
                attr=SysFilterAttr.PRODUCER_VERSION,
                comp=SysFilterComparisonOperators.GREATER_EQUAL,
                value="0.4.5",
            )

            assert evaluate_system_filters(system, [filter_config])

            # Test with version that's too new
            filter_config_too_new = SystemFilter(
                attr=SysFilterAttr.PRODUCER_VERSION,
                comp=SysFilterComparisonOperators.GREATER_EQUAL,
                value="0.5.0",
            )

            assert not evaluate_system_filters(system, [filter_config_too_new])


class TestFilterExcelIllegalChars:
    """Tests for the _filter_excel_illegal_chars function."""

    def test_remove_control_characters(self) -> None:
        """Test removal of illegal control characters."""
        # Create string with various control characters
        test_string = "Hello\x00\x01\x02World\x1f"
        result = _filter_excel_illegal_chars(test_string)
        assert result == "HelloWorld"

    def test_preserve_allowed_characters(self) -> None:
        """Test that allowed control characters are preserved."""
        # Tab, Line feed, Carriage return should be preserved
        test_string = "Hello\tWorld\nNext\rLine"
        result = _filter_excel_illegal_chars(test_string)
        assert result == test_string

    def test_normal_text_unchanged(self) -> None:
        """Test that normal text is unchanged."""
        test_string = "Normal text with spaces and punctuation!"
        result = _filter_excel_illegal_chars(test_string)
        assert result == test_string

    def test_empty_string(self) -> None:
        """Test handling of empty string."""
        result = _filter_excel_illegal_chars("")
        assert result == ""

    def test_only_illegal_characters(self) -> None:
        """Test string with only illegal characters."""
        test_string = "\x00\x01\x02\x03"
        result = _filter_excel_illegal_chars(test_string)
        assert result == ""


class TestSearchEngineIntegration:
    """Integration tests for search engine components."""

    def test_filter_chain_with_real_system(self) -> None:
        """Test complete filter chain with realistic system object."""
        # Create a realistic system mock
        system = Mock(spec=Systems)
        system.system_name = "test-windows-server"
        system.os_family = OSFamilyType.WINDOWS
        system.producer = ProducerType.KPWINAUDIT
        system.producer_version = "0.4.7"
        system.product_name = "Windows Server 2019"
        system.distro_family = None

        # Test with filters that should match
        matching_filters = [
            SystemFilter(
                attr=SysFilterAttr.OS_FAMILY,
                comp=SysFilterComparisonOperators.EQUALS,
                value="Windows",
            ),
            SystemFilter(
                attr=SysFilterAttr.PRODUCER,
                comp=SysFilterComparisonOperators.EQUALS,
                value="KPWINAUDIT",
            ),
        ]

        with patch(
            "kp_analysis_toolkit.process_scripts.search_engine.is_attribute_applicable",
            return_value=True,
        ):
            assert evaluate_system_filters(system, matching_filters)

        # Test with filters that should not match
        non_matching_filters = [
            SystemFilter(
                attr=SysFilterAttr.OS_FAMILY,
                comp=SysFilterComparisonOperators.EQUALS,
                value="Linux",
            ),
        ]

        with patch(
            "kp_analysis_toolkit.process_scripts.search_engine.is_attribute_applicable",
            return_value=True,
        ):
            assert not evaluate_system_filters(system, non_matching_filters)

    def test_error_handling_in_filters(self) -> None:
        """Test error handling in filter evaluation."""
        system = Mock(spec=Systems)
        system.os_family = None  # This could cause issues

        filter_config = SystemFilter(
            attr=SysFilterAttr.OS_FAMILY,
            comp=SysFilterComparisonOperators.EQUALS,
            value="Windows",
        )

        # Should handle gracefully and return False
        with patch(
            "kp_analysis_toolkit.process_scripts.search_engine.is_attribute_applicable",
            return_value=True,
        ):
            result = evaluate_system_filters(system, [filter_config])
            assert result is False
