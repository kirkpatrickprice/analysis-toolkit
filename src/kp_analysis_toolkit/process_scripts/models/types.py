"""Type definitions for KP Analysis Toolkit."""

# Define type aliases for primitive and collection types to imrove reusability and readability
type PrimitiveType = str | int | float
type CollectionType = (
    list[str] | list[int] | list[float] | set[str] | set[int] | set[float]
)
type SysFilterValueType = PrimitiveType | CollectionType
