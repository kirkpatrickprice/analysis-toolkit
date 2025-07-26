"""Path utilities for file processing in the KP Analysis Toolkit."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.timestamp import TimeStamper
    from kp_analysis_toolkit.models.types import PathLike


class PathUtilitiesService:
    """Service for generating paths with timestamps."""

    def __init__(self, timestamp_service: TimeStamper) -> None:
        """
        Initialize the PathUtilitiesService.

        Args:
            timestamp_service: Service for generating timestamps

        """
        self.timestamp_service: TimeStamper = timestamp_service

    def generate_timestamped_path(
        self,
        base_path: PathLike,
        filename_prefix: str,
        extension: str,
    ) -> Path:
        """Generate a timestamped file path."""
        timestamp: str = self.timestamp_service.get_timestamp()

        return Path(base_path) / f"{filename_prefix}_{timestamp}{extension}"
