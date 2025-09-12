from pydantic import ValidationInfo, field_validator

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.base import ConfigModel
from kp_analysis_toolkit.process_scripts.models.enums import SysFilterAttr
from kp_analysis_toolkit.process_scripts.models.search.sys_filters import SystemFilter
from kp_analysis_toolkit.utils.rich_output import get_rich_output


class MergeFieldConfig(KPATBaseModel):
    """Configuration for merging multiple source columns into a single destination column."""

    source_columns: list[str]
    dest_column: str

    @field_validator("source_columns")
    @classmethod
    def validate_source_columns(cls, value: list[str]) -> list[str]:
        min_source_columns: int = 2
        """Validate that at least two source columns are specified."""
        if len(value) < min_source_columns:
            message: str = "merge_fields must specify at least two source_columns"
            raise ValueError(message)
        return value


class GlobalConfig(KPATBaseModel, ConfigModel):
    """Global configuration that can be applied to all search sections."""

    topic: str | None = None
    sys_filter: list[SystemFilter] | None = None
    max_results: int | None = None
    only_matching: bool | None = None
    unique: bool | None = None
    full_scan: bool | None = None


class SearchConfig(KPATBaseModel, ConfigModel):
    """Configuration for a single search operation."""

    name: str  # The YAML section name
    regex: str
    comment: str | None = None
    excel_sheet_name: str
    topic: str | None = None
    max_results: int = -1
    field_list: list[str] | None = None
    only_matching: bool = False
    unique: bool = False
    full_scan: bool = False
    rs_delimiter: str | None = None
    multiline: bool = False
    merge_fields: list[MergeFieldConfig] | None = None
    sys_filter: list[SystemFilter] | None = None
    show_missing: bool = False
    source_file: str | None = None  # Track the source file for better error reporting

    @field_validator("regex")
    @classmethod
    def validate_regex(cls, value: str) -> str:
        """Validate that the regex pattern is valid."""
        import re

        try:
            re.compile(value)
        except re.error as e:
            message: str = f"Invalid regex pattern: {e}"
            raise ValueError(message) from e
        return value

    @field_validator("max_results")
    @classmethod
    def validate_max_results(cls, value: int) -> int:
        """Validate max_results is -1 (unlimited) or positive integer."""
        if value != -1 and value <= 0:
            message: str = "max_results must be -1 (unlimited) or a positive integer"
            raise ValueError(message)
        return value

    @field_validator("only_matching")
    @classmethod
    def validate_field_list_with_only_matching(
        cls,
        value: bool,
        info: ValidationInfo,
    ) -> bool:
        """Validate that field_list is only used with only_matching=True."""
        if info.data.get("field_list") and not value:
            # Override only_matching to True if field_list is specified
            return True
        return value

    @field_validator("multiline")
    @classmethod
    def validate_multiline_with_field_list(
        cls,
        value: bool,
        info: ValidationInfo,
    ) -> bool:
        """Validate that multiline is only used when field_list is specified."""
        if value and not info.data.get("field_list"):
            message: str = "multiline can only be used when field_list is specified"
            raise ValueError(message)
        return value

    @field_validator("multiline")
    @classmethod
    def validate_multiline_with_rs_delimiter(
        cls,
        value: bool,
        info: ValidationInfo,
    ) -> bool:
        """Validate that rs_delimiter is only used with multiline=True."""
        if info.data.get("rs_delimiter") and not value:
            message = "rs_delimiter can only be used with multiline=True"
            raise ValueError(message)
        return value

    @field_validator("rs_delimiter")
    @classmethod
    def validate_rs_delimiter_with_field_list(
        cls,
        value: str | None,
        info: ValidationInfo,
    ) -> str | None:
        """Validate that rs_delimiter is only used when field_list is specified."""
        if value is not None and not info.data.get("field_list"):
            message: str = "rs_delimiter can only be used when field_list is specified"
            raise ValueError(message)
        return value

    def merge_global_config(self, global_config: GlobalConfig) -> "SearchConfig":
        """Merge global configuration into this search config, with local config taking precedence."""
        merged_data = self.model_dump()

        # Apply global settings only if not already set locally
        if global_config.topic and not merged_data.get("topic"):
            merged_data["topic"] = global_config.topic

        if global_config.sys_filter and not merged_data.get("sys_filter"):
            merged_data["sys_filter"] = global_config.sys_filter
        elif global_config.sys_filter and merged_data.get("sys_filter"):
            # Combine global and local sys_filters
            merged_data["sys_filter"] = list(global_config.sys_filter) + list(
                merged_data["sys_filter"],
            )

        if global_config.max_results is not None and merged_data["max_results"] == -1:
            merged_data["max_results"] = global_config.max_results

        if global_config.only_matching is not None and not merged_data["only_matching"]:
            merged_data["only_matching"] = global_config.only_matching

        if global_config.unique is not None and not merged_data["unique"]:
            merged_data["unique"] = global_config.unique

        if global_config.full_scan is not None and not merged_data["full_scan"]:
            merged_data["full_scan"] = global_config.full_scan

        return SearchConfig(**merged_data)


def get_sysfilter_os_type(config: SearchConfig) -> str:
    """Get the OS type from the search configuration."""
    try:
        # Check if sys_filter is None or empty
        if not config.sys_filter:
            return "Unknown"

        # Iterate through the sys_filter list to find the first one with an os_family
        for sysfilter in config.sys_filter:
            if sysfilter.attr == SysFilterAttr.OS_FAMILY:
                return str(sysfilter.value)

    except Exception as e:
        # Provide detailed error context including configuration name
        config_name = getattr(config, "name", "Unknown")
        source_file = getattr(config, "source_file", "Unknown file")

        rich_output = get_rich_output()
        rich_output.error(
            f"Error processing search configuration '{config_name}' "
            f"from {source_file}: {e}",
        )

        # Re-raise with better context
        error_msg = (
            f"Failed to get OS type from search configuration '{config_name}' "
            f"(loaded from {source_file}): {e}"
        )
        raise ValueError(error_msg) from e
    else:
        return "Unknown"
