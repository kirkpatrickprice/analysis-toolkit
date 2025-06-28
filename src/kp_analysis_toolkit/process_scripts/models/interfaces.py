import uuid
from typing import Any, Protocol


class Configurable(Protocol):
    """Protocol defining objects that can receive configuration."""

    def merge_global_config(self, global_config: Any) -> Any:  # noqa: ANN401
        """Merge global configuration with local configuration."""
        ...


class Identifiable(Protocol):
    """Protocol for objects requiring identification."""

    @property
    def identifier(self) -> str | uuid.UUID:
        """Return a unique identifier for this object."""
        ...
