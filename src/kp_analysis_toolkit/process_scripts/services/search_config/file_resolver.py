# AI-GEN: GitHub Copilot|2025-07-29|fix/di/scripts-migration|reviewed:yes
from pathlib import Path

from kp_analysis_toolkit.core.services.file_processing import FileProcessingService


class StandardFileResolver:
    """Standard implementation for resolving YAML configuration file paths."""

    def __init__(self, file_processing: FileProcessingService) -> None:
        """Initialize with core file processing service."""
        self.file_processing = file_processing

    def resolve_path(self, base_path: Path, relative_path: str) -> Path:
        """Resolve relative path against base path - YAML-specific logic."""
        # This is domain-specific YAML include resolution logic
        # Should NOT be in core service
        resolved: Path = base_path.parent / relative_path
        return resolved.resolve()

    def find_include_files(self, config_dir: Path, pattern: str) -> list[Path]:
        """Find include files - delegates to core service."""
        # This delegates to core service for file discovery
        return self.file_processing.discover_files_by_pattern(
            config_dir,
            pattern,
            recursive=False,
        )


# END AI-GEN
