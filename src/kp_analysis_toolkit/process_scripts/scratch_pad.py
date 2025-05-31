"""
Data models for the analysis toolkit using Pydantic for validation and type safety.
Contains all the data structures needed for search configurations, system information,
and search results.
"""

from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field, field_validator

from kp_analysis_toolkit.process_scripts import GLOBALS


class RegexPatterns(BaseModel):
    """Generic configuration for regex-based data extraction and formatting."""

    patterns: dict[str, str]
    formatter: Callable[[dict[str, str]], str] | None = None

    class Config:
        arbitrary_types_allowed = True


class LinuxFamilyType(str, Enum):
    """Enum to define the types of Linux families."""

    DEB = "deb"
    RPM = "rpm"
    APK = "apk"
    OTHER = "other"
    UNKNOWN = "unknown"


class ProducerType(str, Enum):
    """Enum to define the types of producers/audit scripts."""

    KPNIXAUDIT = "KPNIXAUDIT"
    KPWINAUDIT = "KPWINAUDIT"
    KPMACAUDIT = "KPMACAUDIT"


class SystemType(str, Enum):
    """Enum to define the types of operating systems."""

    WINDOWS = "Windows"
    LINUX = "Linux"
    DARWIN = "Darwin"  # MacOS


class SysFilterAttr(str, Enum):
    """Enum for sys_filter attribute names."""

    OS_FAMILY = "os_family"
    PRODUCER = "producer"
    KP_MAC_VERSION = "kp_mac_version"
    KP_NIX_VERSION = "kp_nix_version"
    KP_WIN_VERSION = "kp_win_version"
    PRODUCT_NAME = "product_name"
    RELEASE_ID = "release_id"
    CURRENT_BUILD = "current_build"
    UBR = "ubr"
    DISTRO_FAMILY = "distro_family"
    OS_PRETTY_NAME = "os_pretty_name"
    RPM_PRETTY_NAME = "rpm_pretty_name"
    OS_VERSION = "os_version"


class SysFilterComparisonOperators(str, Enum):
    """Enum for sys_filter comparison operators."""

    EQUALS = "eq"  # Equals -- an exact comparison
    GREATER_THAN = "gt"  # Greater than -- compares numbers, strings, list members, etc
    LESS_THAN = "lt"  # Less than -- compares numbers, strings, list members, etc
    GREATER_EQUAL = "ge"  # Greater than or equals
    LESS_EQUAL = "le"  # Less than or equals
    IN = "in"  # Tests set membership


class SystemFilter(BaseModel):
    """System filter configuration for limiting search applicability."""

    attr: SysFilterAttr
    comp: SysFilterComparisonOperators
    value: str | int | float | list[str] | list[int] | list[float]

    @field_validator("value")
    @classmethod
    def validate_value_for_operator(cls, value, info):
        """Validate that the value type is appropriate for the comparison operator."""
        comp = info.data.get("comp")

        if comp == SysFilterComparisonOperators.IN:
            if not isinstance(value, list):
                raise ValueError("'in' operator requires a list value")
        elif comp in [
            SysFilterComparisonOperators.GREATER_THAN,
            SysFilterComparisonOperators.LESS_THAN,
            SysFilterComparisonOperators.GREATER_EQUAL,
            SysFilterComparisonOperators.LESS_EQUAL,
        ]:
            if isinstance(value, list):
                raise ValueError(f"'{comp}' operator cannot be used with list values")

        return value


class GlobalConfig(BaseModel):
    """Global configuration that can be applied to all search sections."""

    sys_filter: list[SystemFilter] | None = None
    max_results: int | None = None
    only_matching: bool | None = None
    unique: bool | None = None
    full_scan: bool | None = None


class SearchConfig(BaseModel):
    """Configuration for a single search operation."""

    name: str  # The YAML section name
    systems: list[str] | None = None
    regex: str
    comment: str | None = None
    max_results: int = -1
    only_matching: bool = False
    unique: bool = False
    field_list: list[str] | None = None
    full_scan: bool = False
    rs_delimiter: str | None = None
    combine: bool = False
    sys_filter: list[SystemFilter] | None = None

    @field_validator("max_results")
    @classmethod
    def validate_max_results(cls, value):
        """Validate max_results is -1 (unlimited) or positive integer."""
        if value != -1 and value <= 0:
            raise ValueError("max_results must be -1 (unlimited) or a positive integer")
        return value

    @field_validator("field_list")
    @classmethod
    def validate_field_list_with_only_matching(cls, value, info):
        """Validate that field_list is only used with only_matching=True."""
        if value is not None and not info.data.get("only_matching", False):
            raise ValueError("field_list can only be used with only_matching=True")
        return value

    @field_validator("combine")
    @classmethod
    def validate_combine_with_field_list(cls, value, info):
        """Validate that combine is only used when field_list is specified."""
        if value and not info.data.get("field_list"):
            raise ValueError("combine can only be used when field_list is specified")
        return value

    @field_validator("rs_delimiter")
    @classmethod
    def validate_rs_delimiter_with_combine(cls, value, info):
        """Validate that rs_delimiter is only used with combine=True."""
        if value is not None and not info.data.get("combine", False):
            raise ValueError("rs_delimiter can only be used with combine=True")
        return value

    def merge_global_config(self, global_config: GlobalConfig) -> "SearchConfig":
        """
        Merge global configuration into this search config, with local config taking precedence.

        Args:
            global_config: Global configuration to merge

        Returns:
            New SearchConfig with merged settings

        """
        merged_data = self.model_dump()

        # Apply global settings only if not already set locally
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


class IncludeConfig(BaseModel):
    """Configuration for including other YAML files."""

    files: list[str]


class YamlConfig(BaseModel):
    """Complete YAML configuration file structure."""

    global_config: GlobalConfig | None = None
    search_configs: dict[str, SearchConfig] = Field(default_factory=dict)
    include_configs: dict[str, IncludeConfig] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "YamlConfig":
        """
        Create YamlConfig from parsed YAML dictionary.

        Args:
            data: Dictionary from parsed YAML file

        Returns:
            YamlConfig object with structured data

        """
        global_config = None
        search_configs = {}
        include_configs = {}

        for key, value in data.items():
            if key == "global":
                global_config = GlobalConfig(**value)
            elif key.startswith("include_"):
                include_configs[key] = IncludeConfig(**value)
            else:
                # Regular search configuration
                search_configs[key] = SearchConfig(name=key, **value)

        return cls(
            global_config=global_config,
            search_configs=search_configs,
            include_configs=include_configs,
        )


class SearchResult(BaseModel):
    """Individual search result."""

    system_name: str
    line_number: int
    matched_text: str
    extracted_fields: dict[str, str] | None = None

    @field_validator("line_number")
    @classmethod
    def validate_line_number(cls, value):
        """Ensure line number is positive."""
        if value <= 0:
            raise ValueError("line_number must be a positive integer")
        return value


class SearchResults(BaseModel):
    """Collection of results for a search configuration."""

    config: SearchConfig
    results: list[SearchResult]

    @computed_field
    @property
    def result_count(self) -> int:
        """Return the number of results."""
        return len(self.results)

    @computed_field
    @property
    def unique_systems(self) -> int:
        """Return the number of unique systems that had matches."""
        return len(set(result.system_name for result in self.results))

    @computed_field
    @property
    def has_extracted_fields(self) -> bool:
        """Check if any results have extracted fields."""
        return any(result.extracted_fields for result in self.results)


class Systems(BaseModel):
    """
    Class to hold the systems configuration.
    Updated to include all the sys_filter attributes for proper filtering.
    """

    __tablename__ = "systems"

    system_id: UUID = Field(default_factory=uuid4)
    system_name: str
    file_encoding: str | None = None
    system_type: SystemType
    linux_family: LinuxFamilyType | None = None
    system_os: str | None = None
    producer: ProducerType
    producer_version: str
    file_hash: str | None = None
    file: Path

    # Additional fields for sys_filter support
    os_family: str | None = None  # Maps to system_type but as string for filtering
    kp_mac_version: str | None = None
    kp_nix_version: str | None = None
    kp_win_version: str | None = None
    product_name: str | None = None
    release_id: str | None = None
    current_build: str | None = None
    ubr: str | None = None
    distro_family: str | None = None  # Maps to linux_family but as string
    os_pretty_name: str | None = None
    rpm_pretty_name: str | None = None
    os_version: str | None = None

    @computed_field
    @property
    def os_family_computed(self) -> str:
        """Compute os_family from system_type for sys_filter compatibility."""
        return self.system_type.value if self.system_type else "Unknown"

    @computed_field
    @property
    def distro_family_computed(self) -> str:
        """Compute distro_family from linux_family for sys_filter compatibility."""
        return self.linux_family.value if self.linux_family else "unknown"

    @computed_field
    @property
    def producer_computed(self) -> str:
        """Compute producer string for sys_filter compatibility."""
        return self.producer.value if self.producer else "Unknown"

    class Config:
        arbitrary_types_allowed = True


class RawData(BaseModel):
    """Base model for raw data processing."""

    data: str
    source_file: Path
    line_number: int | None = None
    timestamp: str | None = None

    class Config:
        arbitrary_types_allowed = True


class ProgramConfig(BaseModel):
    """Class to hold the program configuration."""

    program_path: Path = Path(__file__).parent
    config_path: Path = Field(
        default_factory=lambda: Path(__file__).parent / GLOBALS["CONF_PATH"],
    )
    audit_config_file: Path | None = None
    source_files_path: Path | None = None
    source_files_spec: str = "**/*"
    out_path: str = "./results"
    list_audit_configs: bool = False
    list_sections: bool = False
    list_source_files: bool = False
    list_systems: bool = False
    verbose: bool = False

    @field_validator("audit_config_file")
    @classmethod
    def validate_audit_config_file(cls, value):
        """Validate that the audit config file exists if provided."""
        if value is not None and not value.exists():
            raise ValueError(f"Audit config file does not exist: {value}")
        return value

    @field_validator("source_files_path")
    @classmethod
    def validate_source_files_path(cls, value):
        """Validate that the source files path exists if provided."""
        if value is not None and not value.exists():
            raise ValueError(f"Source files path does not exist: {value}")
        return value

    @computed_field
    @property
    def results_path(self) -> Path:
        """Compute the results path based on out_path."""
        return Path(self.out_path)

    @computed_field
    @property
    def source_files_path_computed(self) -> Path:
        """Compute source files path with fallback to program path."""
        if self.source_files_path:
            return self.source_files_path
        return self.program_path / "testdata"

    class Config:
        arbitrary_types_allowed = True


class SearchStatistics(BaseModel):
    """Statistics about search execution."""

    total_searches: int
    searches_with_results: int
    searches_without_results: int
    total_matches: int
    average_matches_per_search: float
    unique_systems_found: int
    systems_with_matches: int
    searches_with_extracted_fields: int
    top_searches_by_results: list[tuple[str, int]]


class ValidationMessage(BaseModel):
    """Validation message for search configurations."""

    level: str  # "WARNING", "ERROR", "INFO"
    search_name: str | None = None
    message: str

    def __str__(self) -> str:
        if self.search_name:
            return f"{self.level}: [{self.search_name}] {self.message}"
        return f"{self.level}: {self.message}"


class ConfigValidationResult(BaseModel):
    """Result of configuration validation."""

    is_valid: bool
    messages: list[ValidationMessage]
    error_count: int = 0
    warning_count: int = 0

    def __post_init__(self):
        """Count errors and warnings after initialization."""
        self.error_count = sum(1 for msg in self.messages if msg.level == "ERROR")
        self.warning_count = sum(1 for msg in self.messages if msg.level == "WARNING")
        self.is_valid = self.error_count == 0


class ProcessingReport(BaseModel):
    """Comprehensive report of processing execution."""

    program_config: ProgramConfig
    systems_found: int
    search_configs_loaded: int
    search_results: list[SearchResults]
    statistics: SearchStatistics
    validation_result: ConfigValidationResult | None = None
    processing_time_seconds: float | None = None
    output_files: dict[str, Path] = Field(default_factory=dict)

    @computed_field
    @property
    def success(self) -> bool:
        """Determine if processing was successful."""
        return (
            self.systems_found > 0
            and self.search_configs_loaded > 0
            and (self.validation_result is None or self.validation_result.is_valid)
        )


class ExportOptions(BaseModel):
    """Options for exporting search results."""

    include_summary_sheet: bool = True
    include_metadata: bool = True
    create_detailed_report: bool = False
    auto_adjust_columns: bool = True
    max_column_width: int = 80
    include_empty_searches: bool = True
    table_style: str = "TableStyleMedium9"


class SystemSummary(BaseModel):
    """Summary information about a system."""

    system_name: str
    system_type: str
    producer: str
    producer_version: str
    file_path: str
    file_size_bytes: int | None = None
    search_matches: int = 0
    unique_searches_matched: int = 0

    @computed_field
    @property
    def file_size_mb(self) -> float | None:
        """Return file size in megabytes."""
        if self.file_size_bytes is not None:
            return round(self.file_size_bytes / (1024 * 1024), 2)
        return None
