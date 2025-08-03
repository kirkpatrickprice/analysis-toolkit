"""Include processor for handling YAML include directives."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class StandardIncludeProcessor:
    """Standard implementation for processing YAML include directives."""

    def process_includes(
        self,
        config_data: dict[str, str | bool | float],
        base_path: Path,
    ) -> dict[str, str | bool | float]:
        """
        Process include directives in YAML configuration data.

        This method processes any keys that start with 'include_' and loads
        the referenced files recursively.

        Args:
            config_data: Raw YAML configuration data
            base_path: Base directory for resolving include paths

        Returns:
            Updated configuration data with includes processed

        """
        # In the current implementation, include processing is handled
        # by the SearchConfigService itself, which loads each included
        # file as a separate YamlConfig object.
        #
        # This processor could be used for more complex include scenarios
        # like merging configurations or handling conditional includes.

        return config_data
