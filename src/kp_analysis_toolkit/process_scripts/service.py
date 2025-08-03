# AI-GEN: CopilotChat|2025-07-31|KPAT-ListSystems|reviewed:no
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from kp_analysis_toolkit.process_scripts.models.results.system import Systems

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.process_scripts.models.results.system import Systems
    from kp_analysis_toolkit.process_scripts.services.system_detection import (
        SystemDetectionService,
    )
# END AI-GEN


# AI-GEN: CopilotChat|2025-07-31|KPAT-ListSystems|reviewed:no
class ProcessScriptsService:
    """Main service for the process scripts module."""

    def __init__(
        self,
        system_detection: SystemDetectionService,
        file_processing: FileProcessingService,
        rich_output: RichOutputService,
    ) -> None:
        self.system_detection: SystemDetectionService = system_detection
        self.file_processing: FileProcessingService = file_processing
        self.rich_output: RichOutputService = rich_output

    def list_systems(
        self,
        input_directory: Path,
        file_pattern: str = "*.txt",
    ) -> list[Systems]:
        """List all systems found in the specified files."""
        try:
            # Discover files matching the pattern
            discovered_files: list[Path] = (
                self.file_processing.discover_files_by_pattern(
                    base_path=input_directory,
                    pattern=file_pattern,
                    recursive=True,
                )
            )

            # Extract systems from each file
            systems: list[Systems] = []
            for file_path in discovered_files:
                file_systems: list[Systems] = (
                    self.system_detection.enumerate_systems_from_files(
                        [file_path],
                    )
                )
                systems.extend(file_systems)

        except Exception as e:
            self.rich_output.error(f"Failed to list systems: {e}")
            raise
        else:
            return systems


# END AI-GEN
