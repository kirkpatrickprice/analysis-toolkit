from enum import Enum
from pathlib import Path
from typing import ClassVar, Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, computed_field, field_validator

from kp_analysis_toolkit.process_scripts import GLOBALS

T = TypeVar("T", bound=BaseModel)


class LinuxFamilyType(str, Enum):
    """Enum to define the types of Linux families."""

    DEB = "deb"
    RPM = "rpm"
    APK = "apk"
    OTHER = "Other"


class ProgramConfig(BaseModel):
    """Class to hold the program configuration."""

    program_path: Path = Path(__file__).parent
    config_path: Path = program_path / GLOBALS["CONF_PATH"]
    audit_config_file: Optional[Path] = None
    source_files_path: Optional[Path] = None
    source_files_spec: str
    out_path: str
    list_audit_configs: bool = False
    list_sections: bool = False
    list_source_files: bool = False
    list_systems: bool = False
    verbose: bool = False

    @field_validator("audit_config_file")
    @classmethod
    def validate_audit_config_file(cls, value: Optional[Path], values: dict) -> Path:
        """Validate the audit configuration file path."""
        if value is None:
            raise ValueError("Audit configuration file is required.")

        if not values.data.get("config_path").exists():
            raise ValueError(
                f"Configuration path {values.data.get('config_path')} does not exist."
            )

        config_file: Path = values.data.get("config_path") / value
        if not config_file.exists():
            raise ValueError(f"Audit configuration file {config_file} does not exist.")

        return config_file.absolute()

    @computed_field
    @property
    def results_path(cls) -> Path:
        """Convert it to a pathlib.Path object and return the absolute path."""
        # print(f"Validating results path: {cls.results_path}")
        p: Path = Path(cls.source_files_path) / cls.out_path

        return p.absolute()

    @computed_field
    @property
    def database_path(cls) -> Path:
        """Convert it to a pathlib.Path object and return the absolute path."""
        # print(f"Validating database path: {cls.database_path}")
        p: Path = cls.results_path / GLOBALS["DB_FILENAME"]

        return p.absolute()

    @field_validator("source_files_path")
    @classmethod
    def validate_source_path(cls, value: str) -> Path:
        """Convert it to a pathlib.Path object and return the absolute path."""
        p = Path(value)

        if not p.exists():
            raise ValueError(f"Source files path {p} does not exist.")

        return p.absolute()


class ProducerType(str, Enum):
    """Enum to define the types of producers."""

    KPNIXAUDIT = "KPNIXAUDIT"
    KPWINAUDIT = "KPWINAUDIT"
    KPMACAUDIT = "KPMACAUDIT"
    OTHER = "Other"


class RawData(BaseModel):
    """Class to hold the raw data from the source file."""

    db_table_name: ClassVar[str] = "raw_data"
    system_id: UUID
    section: str
    section_heading: str
    raw_data: str

    @field_validator("raw_data")
    @classmethod
    def validate_section_data(cls, value: str) -> str:
        """Ensure section data is not empty."""
        if not value.strip():
            raise ValueError("Section data cannot be empty.")
        return value.strip()


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

    db_table_name: ClassVar[str] = "systems"
    system_id: UUID = uuid4()
    system_name: str
    file_encoding: str | None = None
    system_type: SystemType
    linux_family: LinuxFamilyType | None = None
    system_os: str | None = None
    producer: ProducerType
    producer_version: str
    file_hash: str = None
    file: Path
