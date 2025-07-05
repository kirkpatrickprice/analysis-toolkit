import pandas as pd
from pydantic import Field, field_validator

from kp_analysis_toolkit.models.base import KPATBaseModel


class NipperRowData(KPATBaseModel):
    """Model for validating Nipper CSV row data."""

    devices: str = Field(..., description="Devices column from Nipper CSV")

    @field_validator("devices")
    @classmethod
    def validate_devices(cls, value: str) -> str:
        """Validate and clean devices field."""
        if pd.isna(value) or value is None:
            return ""
        return str(value).strip()
