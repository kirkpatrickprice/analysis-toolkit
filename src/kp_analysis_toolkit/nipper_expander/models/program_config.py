from pathlib import Path

from pydantic import computed_field, field_validator

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.utils.get_timestamp import get_timestamp


class ProgramConfig(KPATBaseModel):
    """Class to hold the program configuration."""

    program_path: Path = Path(__file__).parent.parent
    input_file: Path | None = None
    source_files_path: Path | None = None

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
        """Return the path for the expanded XLSX output file."""
        # Get the input file's stem (filename without extension)
        stem: str = self.input_file.stem

        # Create new filename with "expanded" suffix and xlsx extension
        expanded_filename: str = f"{stem}_expanded-{get_timestamp()}.xlsx"

        # Return the complete path in the same directory as the input file
        return (self.input_file.parent / expanded_filename).absolute()
