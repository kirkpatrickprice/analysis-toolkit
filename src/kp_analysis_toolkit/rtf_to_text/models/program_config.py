from pathlib import Path

from pydantic import computed_field, field_validator, model_validator

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.utils.get_timestamp import get_timestamp


class ProgramConfig(KPATBaseModel):
    """Class to hold the RTF to text converter program configuration."""

    program_path: Path = Path(__file__).parent.parent
    input_file: Path | None = None
    source_files_path: Path | None = None
    _timestamp: str = ""

    @model_validator(mode="after")
    def set_timestamp(self) -> "ProgramConfig":
        """Set timestamp once during model creation."""
        if not self._timestamp:
            self._timestamp = get_timestamp()
        return self

    @field_validator("input_file")
    @classmethod
    def validate_infile(cls, value: Path | None) -> Path:
        """Validate the input file path."""
        if value is None:
            message: str = "Input file is required."
            raise ValueError(message)
        return value

    @computed_field
    @property
    def output_file(self) -> Path:
        """Return the path for the converted text output file."""
        # Get the input file's stem (filename without extension)
        stem: str = self.input_file.stem

        # Create new filename with "_converted.txt" suffix using cached timestamp
        converted_filename: str = f"{stem}_converted-{self._timestamp}.txt"

        # Return the complete path in the same directory as the input file
        return (self.input_file.parent / converted_filename).absolute()
