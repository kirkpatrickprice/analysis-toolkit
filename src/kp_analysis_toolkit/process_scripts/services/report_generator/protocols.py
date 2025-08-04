"""Protocol definitions for report generator services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from pathlib import Path


class ReportGeneratorService(Protocol):
    """Protocol for report generation services."""

    def generate_config_hierarchy_report(
        self,
        config_file: Path,
    ) -> dict[str, Any]:
        """
        Generate a hierarchical report of search configurations.

        Args:
            config_file: Path to the root configuration file

        Returns:
            Dictionary representing the hierarchical structure with statistics

        """
        ...
