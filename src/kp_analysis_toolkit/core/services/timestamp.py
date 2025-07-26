"""Timestamp service for generating and formatting timestamps."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class TimeStamper(Protocol):
    """Protocol for timestamp services."""

    def get_timestamp(self) -> str:
        """Get the current timestamp as a string."""
        ...


class TimeStampService(TimeStamper):
    """Generates timestamps in the format YYYYMMDD-HHMMSS."""

    def get_timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d-%H%M%S")  # noqa: DTZ005
