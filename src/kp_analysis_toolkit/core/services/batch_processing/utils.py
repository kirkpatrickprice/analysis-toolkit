# AI-GEN: claude-3.5-sonnet|2025-01-19|batch-processing-service|reviewed:yes
"""Utility implementations for batch processing service."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from kp_analysis_toolkit.core.services.batch_processing.protocols import ConfigExtractor

if TYPE_CHECKING:
    from pathlib import Path


class DefaultConfigExtractor(ConfigExtractor):
    """Default implementation for extracting file paths from configuration objects."""

    def extract_file_paths(self, config: object) -> tuple[Path, Path]:
        """
        Extract input and output file paths from a config object.

        Args:
            config: Configuration object with input_file and output_file attributes

        Returns:
            Tuple of (input_file_path, output_file_path)

        Raises:
            AttributeError: If config doesn't have required attributes
            TypeError: If file paths are not Path objects

        """
        from pathlib import Path

        if not hasattr(config, "input_file") or not hasattr(config, "output_file"):
            msg = "Configuration object must have 'input_file' and 'output_file' attributes"
            raise AttributeError(msg)

        # Handle Pydantic computed fields and type casting
        input_file = cast("Path", config.input_file)
        output_file = cast("Path", config.output_file)

        if not isinstance(input_file, Path) or not isinstance(output_file, Path):
            msg = "Configuration file paths must be Path objects"
            raise TypeError(msg)

        return input_file, output_file


# END AI-GEN
