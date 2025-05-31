"""Type definitions for KP Analysis Toolkit."""

from typing import TypeAlias

# Define type aliases for primitive and collection types to imrove reusability and readability
PrimitiveType: TypeAlias = str | int | float
CollectionType: TypeAlias = (
    list[str] | list[int] | list[float] | set[str] | set[int] | set[float]
)
SysFilterValueType: TypeAlias = PrimitiveType | CollectionType
