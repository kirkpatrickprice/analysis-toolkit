"""Type definitions for KP Analysis Toolkit."""

from kp_analysis_toolkit.process_scripts.models.types.os_types import (
    DistroFamilyType,
    OSFamilyType,
)
from kp_analysis_toolkit.process_scripts.models.types.producer_types import ProducerType

# Define type aliases for primitive and collection types to improve reusability and readability
type PrimitiveType = str | int | float | bool
type CollectionType = (
    list[str] | list[int] | list[float] | set[str] | set[int] | set[float]
)
type SysFilterValueType = PrimitiveType | CollectionType
type ConfigurationValueType = PrimitiveType | CollectionType | None

__all__: list[str] = [
    "CollectionType",
    "ConfigurationValueType",
    "DistroFamilyType",
    "OSFamilyType",
    "PrimitiveType",
    "ProducerType",
    "SysFilterValueType",
]
