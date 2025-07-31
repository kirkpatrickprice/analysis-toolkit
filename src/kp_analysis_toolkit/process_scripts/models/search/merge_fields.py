from pydantic import field_validator

from kp_analysis_toolkit.models.base import KPATBaseModel


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
