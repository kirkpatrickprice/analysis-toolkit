import pytest

from kp_analysis_toolkit.process_scripts.models.search.base import (
    GlobalConfig,
    MergeFieldConfig,
    SearchConfig,
    get_sysfilter_os_type,
)
from kp_analysis_toolkit.process_scripts.models.search.sys_filters import SystemFilter


class TestSearchConfig:
    """Test cases for the SearchConfig class."""

    def test_validate_regex_valid(self) -> None:
        """Test that valid regex patterns are accepted."""
        config = SearchConfig(
            name="test",
            regex=r"test\d+",
            excel_sheet_name="Sheet1",
        )
        assert config.regex == r"test\d+"

    def test_validate_regex_invalid(self) -> None:
        """Test that invalid regex patterns are rejected."""
        with pytest.raises(ValueError) as excinfo:  # noqa: PT011
            SearchConfig(
                name="test",
                regex=r"test[",  # Invalid regex - unclosed character class
                excel_sheet_name="Sheet1",
            )
        assert "Invalid regex pattern" in str(excinfo.value)

    def test_validate_max_results_valid(self) -> None:
        """Test that valid max_results values are accepted."""
        # Unlimited results
        config1 = SearchConfig(
            name="test1",
            regex=r"test",
            excel_sheet_name="Sheet1",
            max_results=-1,
        )
        assert config1.max_results == -1

        # Positive integer
        config2 = SearchConfig(
            name="test2",
            regex=r"test",
            excel_sheet_name="Sheet1",
            max_results=10,
        )
        assert config2.max_results == 10  # noqa: PLR2004

    def test_validate_max_results_invalid(self) -> None:
        """Test that invalid max_results values are rejected."""
        with pytest.raises(ValueError) as excinfo:  # noqa: PT011
            SearchConfig(
                name="test",
                regex=r"test",
                excel_sheet_name="Sheet1",
                max_results=0,
            )
        assert "max_results must be -1 (unlimited) or a positive integer" in str(
            excinfo.value,
        )

        with pytest.raises(ValueError) as excinfo:  # noqa: PT011
            SearchConfig(
                name="test",
                regex=r"test",
                excel_sheet_name="Sheet1",
                max_results=-2,
            )
        assert "max_results must be -1 (unlimited) or a positive integer" in str(
            excinfo.value,
        )

    def test_field_list_with_only_matching(self) -> None:
        """Test that field_list automatically sets only_matching to True."""
        config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            field_list=["field1", "field2"],
            only_matching=False,  # This should be overridden
        )
        assert config.only_matching is True

    def test_multiline_without_field_list(self) -> None:
        """Test that multiline requires field_list."""
        with pytest.raises(ValueError) as excinfo:  # noqa: PT011
            SearchConfig(
                name="test",
                regex=r"test",
                excel_sheet_name="Sheet1",
                multiline=True,
                field_list=None,
            )
        assert "multiline can only be used when field_list is specified" in str(
            excinfo.value,
        )

    def test_rs_delimiter_without_multiline(self) -> None:
        """Test that rs_delimiter requires multiline."""
        with pytest.raises(ValueError) as excinfo:  # noqa: PT011
            SearchConfig(
                name="test",
                regex=r"test",
                excel_sheet_name="Sheet1",
                field_list=["field1", "field2"],
                rs_delimiter="|",
                multiline=False,
            )
        assert "rs_delimiter can only be used with multiline=True" in str(excinfo.value)

    def test_rs_delimiter_without_field_list(self) -> None:
        """Test that rs_delimiter requires field_list."""
        with pytest.raises(ValueError) as excinfo:  # noqa: PT011
            SearchConfig(
                name="test",
                regex=r"test",
                excel_sheet_name="Sheet1",
                rs_delimiter="|",
                field_list=None,
            )
        assert "rs_delimiter can only be used when field_list is specified" in str(
            excinfo.value,
        )


class TestGlobalConfigInheritance:
    """Test cases for the inheritance of GlobalConfig in SearchConfig."""

    def test_inherit_sys_filter(self) -> None:
        """Test inheriting sys_filter from global config when not set locally."""
        global_config = GlobalConfig(
            sys_filter=[SystemFilter(attr="os_family", comp="eq", value="test")],
        )
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert len(merged_config.sys_filter) == 1
        assert merged_config.sys_filter[0].attr == "os_family"
        assert merged_config.sys_filter[0].comp == "eq"
        assert merged_config.sys_filter[0].value == "test"

    def test_combine_sys_filters(self) -> None:
        """Test combining sys_filters from global and local configs."""
        global_config = GlobalConfig(
            sys_filter=[
                SystemFilter(attr="distro_family", comp="eq", value="global_test"),
            ],
        )
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            sys_filter=[
                SystemFilter(attr="distro_family", comp="eq", value="local_test"),
            ],
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert len(merged_config.sys_filter) == 2  # noqa: PLR2004
        assert merged_config.sys_filter[0].value == "global_test"
        assert merged_config.sys_filter[1].value == "local_test"

    def test_inherit_max_results(self) -> None:
        """Test inheriting max_results from global config when local is default."""
        global_config = GlobalConfig(max_results=50)
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            max_results=-1,  # Default value
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert merged_config.max_results == 50  # noqa: PLR2004

    def test_local_max_results_precedence(self) -> None:
        """Test that local max_results takes precedence over global."""
        global_config = GlobalConfig(max_results=50)
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            max_results=25,  # Local value should take precedence
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert merged_config.max_results == 25  # noqa: PLR2004

    def test_inherit_only_matching(self) -> None:
        """Test inheriting only_matching from global config when not set locally."""
        global_config = GlobalConfig(only_matching=True)
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            only_matching=False,  # Default value
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert merged_config.only_matching is True

    def test_local_only_matching_precedence(self) -> None:
        """Test that local only_matching takes precedence over global."""
        global_config = GlobalConfig(only_matching=False)
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            only_matching=True,  # Local value should take precedence
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert merged_config.only_matching is True

    def test_inherit_unique(self) -> None:
        """Test inheriting unique from global config when not set locally."""
        global_config = GlobalConfig(unique=True)
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            unique=False,  # Default value
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert merged_config.unique is True

    def test_local_unique_precedence(self) -> None:
        """Test that local unique takes precedence over global."""
        global_config = GlobalConfig(unique=False)
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            unique=True,  # Local value should take precedence
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert merged_config.unique is True

    def test_inherit_full_scan(self) -> None:
        """Test inheriting full_scan from global config when not set locally."""
        global_config = GlobalConfig(full_scan=True)
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            full_scan=False,  # Default value
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert merged_config.full_scan is True

    def test_local_full_scan_precedence(self) -> None:
        """Test that local full_scan takes precedence over global."""
        global_config = GlobalConfig(full_scan=False)
        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            full_scan=True,  # Local value should take precedence
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)
        assert merged_config.full_scan is True

    def test_comprehensive_merge(self) -> None:
        """Test a comprehensive merge of all global config options."""
        global_config = GlobalConfig(
            sys_filter=[
                SystemFilter(attr="distro_family", comp="eq", value="global_test"),
            ],
            max_results=50,
            only_matching=True,
            unique=True,
            full_scan=True,
        )

        search_config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            sys_filter=[
                SystemFilter(attr="distro_family", comp="eq", value="local_test"),
            ],
            max_results=25,  # Should take precedence
            only_matching=False,  # Should be overridden by global
            unique=False,  # Should be overridden by global
            full_scan=False,  # Should be overridden by global
        )

        merged_config: SearchConfig = search_config.merge_global_config(global_config)

        # Check sys_filter (combined)
        assert len(merged_config.sys_filter) == 2  # noqa: PLR2004

        # Check local precedence
        assert merged_config.max_results == 25  # noqa: PLR2004

        # Check global inheritance
        assert merged_config.only_matching is True
        assert merged_config.unique is True
        assert merged_config.full_scan is True


class TestMergeFieldConfig:
    """Tests for MergeFieldConfig.validate_source_columns()."""

    def test_one_source_column_raises_error(self) -> None:
        """Fewer than two source columns raises ValidationError."""
        with pytest.raises(ValueError, match="at least two source_columns"):
            MergeFieldConfig(source_columns=["col1"], dest_column="dest")

    def test_zero_source_columns_raises_error(self) -> None:
        """Zero source columns raises ValidationError."""
        with pytest.raises(ValueError, match="at least two source_columns"):
            MergeFieldConfig(source_columns=[], dest_column="dest")

    def test_two_source_columns_is_valid(self) -> None:
        """Exactly two source columns is the minimum valid configuration."""
        mfc = MergeFieldConfig(source_columns=["col1", "col2"], dest_column="dest")
        assert len(mfc.source_columns) == 2  # noqa: PLR2004

    def test_three_source_columns_is_valid(self) -> None:
        """More than two source columns is also valid."""
        mfc = MergeFieldConfig(
            source_columns=["col1", "col2", "col3"], dest_column="dest"
        )
        assert len(mfc.source_columns) == 3  # noqa: PLR2004


class TestGetSysfilterOsType:
    """Tests for get_sysfilter_os_type()."""

    def test_no_sys_filter_returns_unknown(self) -> None:
        """A config with no sys_filter returns 'Unknown'."""
        config = SearchConfig(name="test", regex=r"test", excel_sheet_name="Sheet1")
        assert get_sysfilter_os_type(config) == "Unknown"

    def test_empty_sys_filter_returns_unknown(self) -> None:
        """A config with sys_filter=None returns 'Unknown'."""
        config = SearchConfig(
            name="test", regex=r"test", excel_sheet_name="Sheet1", sys_filter=None
        )
        assert get_sysfilter_os_type(config) == "Unknown"

    def test_os_family_filter_returns_value_string(self) -> None:
        """A sys_filter on OS_FAMILY returns that filter's value as a string."""
        config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            sys_filter=[SystemFilter(attr="os_family", comp="eq", value="Windows")],
        )
        assert get_sysfilter_os_type(config) == "Windows"

    def test_non_os_family_filter_returns_unknown(self) -> None:
        """A sys_filter on a non-OS_FAMILY attribute returns 'Unknown'."""
        config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            sys_filter=[SystemFilter(attr="distro_family", comp="eq", value="deb")],
        )
        assert get_sysfilter_os_type(config) == "Unknown"

    def test_multiple_filters_returns_os_family_value(self) -> None:
        """When multiple filters exist, the OS_FAMILY filter's value is returned."""
        config = SearchConfig(
            name="test",
            regex=r"test",
            excel_sheet_name="Sheet1",
            sys_filter=[
                SystemFilter(attr="distro_family", comp="eq", value="deb"),
                SystemFilter(attr="os_family", comp="eq", value="Linux"),
            ],
        )
        assert get_sysfilter_os_type(config) == "Linux"
