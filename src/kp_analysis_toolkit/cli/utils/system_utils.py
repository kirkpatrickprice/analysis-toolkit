"""System-related utility functions for CLI operations."""

import sys
from pathlib import Path
from typing import Any

from kp_analysis_toolkit.models.types import PathLike

# Constants
BYTES_PER_KB = 1024


def get_object_size(obj: Any, seen: set[int] | None = None) -> int:  # noqa: ANN401
    """
    Recursively calculate the size of an object and its contents in bytes.

    This function handles circular references and provides accurate size
    calculations for complex nested data structures.

    Args:
        obj: The object to measure
        seen: Set of already-seen object IDs (used internally for recursion)

    Returns:
        Total size in bytes

    Example:
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        size_bytes = get_object_size(data)
        print(f"Data structure uses {size_bytes:,} bytes")

    """
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # Mark object as seen to handle circular references
    seen.add(obj_id)
    size: int = sys.getsizeof(obj)

    # Recursively calculate size for container types
    if isinstance(obj, list | tuple | set):
        size += sum(get_object_size(item, seen) for item in obj)
    elif isinstance(obj, dict):
        size += sum(
            get_object_size(key, seen) + get_object_size(value, seen)
            for key, value in obj.items()
        )

    return size


def format_bytes(size_bytes: int) -> str:
    """
    Format byte size into human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")

    Example:
        size = get_object_size(large_data)
        print(f"Data size: {format_bytes(size)}")

    """
    units: list[str] = ["bytes", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)

    for unit in units:
        if size < BYTES_PER_KB or unit == units[-1]:
            if unit == "bytes":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= BYTES_PER_KB

    return f"{size:.1f} {units[-1]}"


def get_file_size(file_path: PathLike) -> str:
    """
    Get the formatted file size for a given file path.

    Args:
        file_path: Path to the file

    Returns:
        Formatted file size string (e.g., "1.5 KB", "2.3 MB", "Unknown")

    Example:
        size = get_file_size("data.csv")
        print(f"File size: {size}")  # "File size: 1.2 KB"

    """
    try:
        file_size = Path(file_path).stat().st_size
        return format_bytes(file_size)
    except OSError:
        return "Unknown"
