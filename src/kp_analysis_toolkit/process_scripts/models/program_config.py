import multiprocessing as mp
from pathlib import Path

from pydantic import computed_field, field_validator

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts import GLOBALS
from kp_analysis_toolkit.process_scripts.models.base import (
    ConfigModel,
    PathValidationMixin,
    ValidationMixin,
)


class ProgramConfig(KPATBaseModel, PathValidationMixin, ValidationMixin, ConfigModel):
    """Class to hold the program configuration."""

    program_path: Path = Path(__file__).parent.parent
    config_path: Path = program_path / GLOBALS["CONF_PATH"]
    audit_config_file: Path | str | None = None
    source_files_path: Path | None = None
    source_files_spec: str
    out_path: str
    list_audit_configs: bool = False
    list_sections: bool = False
    list_source_files: bool = False
    list_systems: bool = False
    verbose: bool = False
    max_workers: int | None = None  # Will be computed to int during validation

    @field_validator("audit_config_file")
    @classmethod
    def validate_audit_config_file(cls, value: Path | None, values: dict) -> Path:
        """Validate the audit configuration file path."""
        if value is None:
            message: str = "Audit configuration file is required."
            raise ValueError(message)

        config_path: Path = values.data.get("config_path")
        if config_path is None:
            message: str = "Configuration path is not set."
            raise ValueError(message)

        # Validate config_path exists using mixin
        cls.validate_directory_exists(config_path)

        config_file: Path = config_path / Path(value)
        return cls.validate_file_exists(config_file)

    @computed_field
    @property
    def results_path(self) -> Path:
        """Convert it to a pathlib.Path object and return the absolute path."""
        # print(f"Validating results path: {cls.results_path}")
        p: Path = Path(self.source_files_path) / self.out_path

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

    @field_validator("source_files_spec")
    @classmethod
    def validate_source_files_spec(cls, value: str) -> str:
        """Validate that source files spec is not empty."""
        return cls.validate_non_empty_string(value) or value

    @field_validator("out_path")
    @classmethod
    def validate_out_path(cls, value: str) -> str:
        """Validate that output path is not empty."""
        return cls.validate_non_empty_string(value) or value

    @field_validator("max_workers")
    @classmethod
    def validate_max_workers(cls, value: int | None) -> int:
        """Validate and compute max_workers value."""
        if value is None:
            # If no value provided, use CPU count
            return mp.cpu_count()
        if value <= 0:
            message: str = "max_workers must be a positive integer"
            raise ValueError(message)
        return value

    @computed_field  # type: ignore[misc]
    @property
    def is_single_threaded(self) -> bool:
        """Check if single-threaded execution is requested."""
        return self.max_workers == 1

    @computed_field  # type: ignore[misc]
    @property
    def worker_description(self) -> str:
        """Get a description of the worker configuration."""
        if self.is_single_threaded:
            return "single-threaded execution (max_workers=1)"
        # Check if this was auto-computed (equals CPU count) or user-provided
        if self.max_workers == mp.cpu_count():
            return f"multiprocess execution with auto workers ({self.max_workers})"
        return f"multiprocess execution with {self.max_workers} workers"

    def ensure_results_path_exists(self) -> None:
        """Ensure the results path directory exists, creating it if necessary."""
        results_path: Path = self.results_path
        if not results_path.exists():
            results_path.mkdir(parents=True, exist_ok=True)
