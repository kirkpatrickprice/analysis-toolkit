"""Protocol definitions for <command> services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import pandas as pd


class DataExpander(Protocol):
    """Protocol for data expansion operations."""

    def expand_ranges(
        self,
        data_frame: pd.DataFrame,
        range_columns: list[str],
    ) -> pd.DataFrame:
        """Expand range columns in the DataFrame."""
        ...

    def expand_lists(
        self,
        data_frame: pd.DataFrame,
        list_columns: list[str],
    ) -> pd.DataFrame: ...


class DataValidator(Protocol):
    """Protocol for data validation."""

    def validate_required_columns(
        self,
        data_frame: pd.DataFrame,
        required_columns: list[str],
    ) -> bool: ...
    def validate_data_types(
        self,
        data_frame: pd.DataFrame,
        column_types: dict[str, type],
    ) -> bool: ...
