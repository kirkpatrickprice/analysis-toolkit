"""Protocol definitions for Nipper Expander services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import pandas as pd

    from kp_analysis_toolkit.models.types import PathLike


class RowExpanderService(Protocol):
    """Protocol for data expansion operations."""

    def expand_device_rows(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Expand the finding to one row per device."""
        ...


class NipperExporterService(Protocol):
    """Protocol for Nipper-specific Excel export operations."""

    def export_nipper_results(
        self,
        data_frame: pd.DataFrame,
        output_path: PathLike,
        *,
        sheet_name: str = "Expanded Nipper Results",
        title: str = "Nipper Expanded Report - One row per device/finding",
    ) -> None:
        """Write the expanded DataFrame to an Excel file."""
        ...


class NipperExpanderService(Protocol):
    """Protocol for the main Nipper Expander service orchestration."""

    def process_nipper_csv(self, file: PathLike) -> None:
        """Process a single Nipper CSV file and return the expanded DataFrame."""
        ...
