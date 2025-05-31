import uuid
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any, TypeAlias

from pydantic import BaseModel, Field, computed_field, field_validator

from kp_analysis_toolkit.process_scripts import GLOBALS

# Define type aliases for primitive and collection types to imrove reusability and readability
PrimitiveType: TypeAlias = str | int | float
CollectionType: TypeAlias = (
    list[str] | list[int] | list[float] | set[str] | set[int] | set[float]
)
SysFilterValueType: TypeAlias = PrimitiveType | CollectionType


class RegexPatterns(BaseModel):
    """Generic configuration for regex-based data extraction and formatting."""

    patterns: dict[str, str]
    formatter: Callable[[dict[str, str]], str] | None = None

    class Config:
        arbitrary_types_allowed = True  # Allow Callable type


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


class SysFilterComp(str, Enum):
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
    comp: SysFilterComp
    value: SysFilterValueType

    @field_validator("value")
    @classmethod
    def validate_value_for_operator(
        cls,
        value: SysFilterValueType,
        info: dict,
    ) -> SysFilterValueType:
        """Validate that the value type is appropriate for the comparison operator."""
        comp: str = info.data.get("comp")

        if comp == SysFilterComp.IN:
            if not isinstance(value, list | set):
                message: str = "'in' operator requires a list or set value"
                raise ValueError(message)
        elif comp in [
            SysFilterComp.GREATER_THAN,
            SysFilterComp.LESS_THAN,
            SysFilterComp.GREATER_EQUAL,
            SysFilterComp.LESS_EQUAL,
        ] and isinstance(value, list | set):
            message: str = f"'{comp}' operator cannot be used with list or set values"
            raise ValueError(message)

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
    def validate_max_results(cls, value: int) -> int:
        """Validate max_results is -1 (unlimited) or positive integer."""
        if value != -1 and value <= 0:
            message: str = "max_results must be -1 (unlimited) or a positive integer"
            raise ValueError(message)
        return value

    @field_validator("only_matching")
    @classmethod
    def validate_field_list_with_only_matching(cls, value: bool, info: dict) -> bool:  # noqa: FBT001
        """Validate that field_list is only used with only_matching=True."""
        if info.data.get("field_list") and not value:
            # Override only_matching to True if field_list is specified
            return True
        return value

    @field_validator("combine")
    @classmethod
    def validate_combine_with_field_list(cls, value: bool, info: dict) -> bool:  # noqa: FBT001
        """Validate that combine is only used when field_list is specified."""
        if value and not info.data.get("field_list"):
            message: str = "combine can only be used when field_list is specified"
            raise ValueError(message)
        return value

    @field_validator("rs_delimiter")
    @classmethod
    def validate_rs_delimiter_with_field_list(
        cls,
        value: str | None,
        info: dict,
    ) -> str | None:
        """Validate that rs_delimiter is only used when field_list is specified."""
        if value is not None and not info.data.get("field_list"):
            message: str = "rs_delimiter can only be used when field_list is specified"
            raise ValueError(message)
        return value

    @field_validator("combine")
    @classmethod
    def validate_combine_with_rs_delimiter(cls, value: bool, info: dict) -> bool:  # noqa: FBT001
        """Validate that rs_delimiter is only used with combine=True."""
        if info.data.get("rs_delimiter") and not value:
            message = "rs_delimiter can only be used with combine=True"
            raise ValueError(message)
        return value

    def merge_global_config(self, global_config: GlobalConfig) -> "SearchConfig":
        """Merge global configuration into this search config, with local config taking precedence."""
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
    search_configs: dict[str, SearchConfig] = {}
    include_configs: dict[str, IncludeConfig] = {}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "YamlConfig":
        """Create YamlConfig from parsed YAML dictionary."""
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

    line_number: int = Field(gt=0, description="Line number must be a positive integer")


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
        return len({result.system_name for result in self.results})

    @computed_field
    @property
    def has_extracted_fields(self) -> bool:
        """Check if any results have extracted fields."""
        return any(result.extracted_fields for result in self.results)


class LinuxFamilyType(str, Enum):
    """Enum to define the types of Linux families."""

    DEB = "deb"
    RPM = "rpm"
    APK = "apk"
    OTHER = "other"


class ProgramConfig(BaseModel):
    """Class to hold the program configuration."""

    program_path: Path = Path(__file__).parent
    config_path: Path = program_path / GLOBALS["CONF_PATH"]
    audit_config_file: Path | None = None
    source_files_path: Path | None = None
    source_files_spec: str
    out_path: str
    list_audit_configs: bool = False
    list_sections: bool = False
    list_source_files: bool = False
    list_systems: bool = False
    verbose: bool = False

    @field_validator("audit_config_file")
    @classmethod
    def validate_audit_config_file(cls, value: Path | None, values: dict) -> Path:
        """Validate the audit configuration file path."""
        if value is None:
            message: str = "Audit configuration file is required."
            raise ValueError(message)

        if not values.data.get("config_path").exists():
            message: str = (
                f"Configuration path {values.data.get('config_path')} does not exist."
            )
            raise ValueError(message)

        config_file: Path = values.data.get("config_path") / value
        if not config_file.exists():
            message: str = f"Audit configuration file {config_file} does not exist."
            raise ValueError(message)

        return config_file.absolute()

    @computed_field
    @property
    def results_path(self) -> Path:
        """Convert it to a pathlib.Path object and return the absolute path."""
        # print(f"Validating results path: {cls.results_path}")
        p: Path = Path(self.source_files_path) / self.out_path

        return p.absolute()

    @computed_field
    @property
    def database_path(self) -> Path:
        """Convert it to a pathlib.Path object and return the absolute path."""
        # print(f"Validating database path: {cls.database_path}")
        p: Path = self.results_path / GLOBALS["DB_FILENAME"]

        return p.absolute()

    @field_validator("source_files_path")
    @classmethod
    def validate_source_path(cls, value: str) -> Path:
        """Convert it to a pathlib.Path object and return the absolute path."""
        p = Path(value)

        if not p.exists():
            message: str = f"Source files path {p} does not exist."
            raise ValueError(message)

        return p.absolute()


class ProducerType(str, Enum):
    """Enum to define the types of producers."""

    KPNIXAUDIT = "KPNIXAUDIT"
    KPWINAUDIT = "KPWINAUDIT"
    KPMACAUDIT = "KPMACAUDIT"
    OTHER = "Other"


class SystemType(str, Enum):
    """Enum to define the types of systems."""

    DARWIN = "Darwin"
    LINUX = "Linux"
    WINDOWS = "Windows"
    OTHER = "Other"
    UNDEFINED = "Undefined"


class Systems(BaseModel):
    """
    Class to hold the systems configuration.

    Attributes:
        - system_id: INTEGER PRIMARY KEY
        - system_name: TEXT (derived from the file name)
        - system_type: TEXT (Darwin, Linux, Windows, etc.)
        - system_os: TEXT
        - producer: TEXT (KPNIXAUDIT, KPWINAUDIT, etc.)
        - producer_version: TEXT (Version of the producer)
        - file_hash: TEXT (SHA256 hash of the source file)
        - file: TEXT (Absolute path to the source file)

    """

    __tablename__ = "systems"
    system_id: uuid.UUID
    system_name: str
    file_encoding: str | None = None
    system_type: SystemType
    linux_family: LinuxFamilyType | None = None
    system_os: str | None = None
    producer: ProducerType
    producer_version: str
    file_hash: str = None
    file: Path


class RawData(BaseModel):
    """Class to hold the raw data from the source file."""

    __tablename__ = "raw_data"
    raw_data_id: uuid.UUID
    section: str
    section_heading: str
    raw_data: str
    system_id: uuid.UUID
    # system: Systems = Relationship(back_populates="systems")

    @field_validator("raw_data")
    @classmethod
    def validate_section_data(cls, value: str) -> str:
        """Ensure section data is not empty."""
        if not value.strip():
            message: str = "Section data cannot be empty."
            raise ValueError(message)
        return value.strip()
