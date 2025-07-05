"""
Common type definitions for the KP Analysis Toolkit.

This module provides reusable type aliases that are used across multiple
modules in the toolkit for consistent type hinting and better code documentation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

# Generic TypeVar for type-preserving operations
T = TypeVar("T")

# Common value types that can be displayed in Rich output or exported to Excel
DisplayableValue = (
    str
    | int
    | float
    | bool
    | None
    | Path
    | list[Any]
    | tuple[Any, ...]
    | set[Any]
    | dict[str, Any]
)

# Configuration values (subset of DisplayableValue, typically simpler types)
ConfigValue = str | int | float | bool | None | Path | list[Any] | dict[str, Any]

# File path types (commonly used throughout the toolkit)
PathLike = str | Path

# Result data structures (used in search results, CSV processing, etc.)
ResultData = dict[str, DisplayableValue]
ResultList = list[ResultData]

# Excel export data types
ExcelData = dict[str, list[DisplayableValue]]
WorksheetData = dict[str, ExcelData]  # Multiple sheets
