import hashlib
from enum import Enum
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, field_validator

from kp_analysis_toolkit.process_scripts import GLOBALS


class ProgramConfig(BaseModel):
    """Class to hold the program configuration."""

    program_path: Path = Path(__file__).parent
    config_path: Path = program_path / GLOBALS["CONF_PATH"]
    audit_config_file: Optional[Path] = None
    out_path: Optional[Path] = None
    source_files_path: Optional[Path] = None
    source_files_spec: str
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

    @field_validator("out_path", "source_files_path")
    @classmethod
    def validate_path(cls, value: Optional[Path], values: dict) -> Path:
        """Validate the path and convert it to an absolute path."""
        if value is None:
            return Path().cwd()

        p = Path(value)

        return p.absolute()


class PathType(str, Enum):
    """Enum to define the type of path."""

    RELATIVE = "relative"
    ABSOLUTE = "absolute"


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

    system_id: UUID = uuid4()
    system_name: str
    system_type: SystemType
    system_os: str
    producer: ProducerType
    producer_version: str
    file_hash: Optional[str] = None
    file: Path

    @field_validator("file_hash")
    @classmethod
    def generate_file_hash(cls, value: Optional[str], values: dict) -> str:
        """Generate the file hash if not provided."""
        if value is not None:
            return value

        file_path: Path = values.get("file")
        if file_path is None or not file_path.exists():
            raise ValueError("File path is required to generate the hash.")

        # Generate the hash (SHA256) of the file
        sha256_hash: hashlib.HASH = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read and update hash in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (IOError, PermissionError) as e:
            raise ValueError(f"Error reading file {file_path}: {e}") from e
