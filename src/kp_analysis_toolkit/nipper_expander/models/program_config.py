from pathlib import Path
from typing import Annotated

from pydantic import Field, computed_field

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.utils.get_timestamp import get_timestamp


class ProgramConfig(KPATBaseModel):
    """Class to hold the program configuration."""

    program_path: Path = Path(__file__).parent.parent
    input_file: Annotated[Path, Field(description="Path to the input CSV file")]
    source_files_path: Path | None = None

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
