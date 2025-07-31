# AI-GEN: gpt-4o|2025-01-30|system-detection-protocols-cleanup|reviewed:no
from collections.abc import Generator
from pathlib import Path
from typing import Protocol

from kp_analysis_toolkit.core.services.file_processing.protocols import ContentStreamer
from kp_analysis_toolkit.process_scripts.models.results.system import Systems
from kp_analysis_toolkit.process_scripts.models.search.filters import SystemFilter


class OSDetector(Protocol):
    """Protocol for operating system detection."""

    def detect_os(self, content_stream: ContentStreamer) -> str | None:
        """Detect OS using targeted content patterns."""
        ...

    def get_supported_os_types(self) -> list[str]:
        """Get list of supported OS types."""
        ...


class ProducerDetector(Protocol):
    """Protocol for detecting system/software producers."""

    def detect_producer(self, content_stream: ContentStreamer, file_path: Path) -> str | None:
        """Detect producer using early file content (typically first 10 lines)."""
        ...

    def get_known_producers(self) -> list[str]:
        """Get list of known producers."""
        ...


class DistroClassifier(Protocol):
    """Protocol for Linux distribution classification."""

    def classify_distribution(self, os_info: str, content_stream: ContentStreamer) -> str | None:
        """Classify Linux distribution using specific content patterns."""
        ...

    def get_supported_distributions(self) -> list[str]:
        """Get list of supported distributions."""
        ...


class SystemDetectionService(Protocol):
    """Service for detecting system information from configuration files."""

    def enumerate_systems_from_files(
        self,
        source_directory: Path,
        file_spec: str = "*.txt",
    ) -> Generator[Systems, None, None]:
        """Enumerate systems from files in a directory."""
        ...

    def analyze_system_file(self, file_path: Path) -> Systems:
        """Analyze a single system file."""
        ...

    def filter_systems_by_criteria(
        self,
        systems: list[Systems],
        filters: list[SystemFilter] | None,
    ) -> list[Systems]:
        """Filter systems based on criteria."""
        ...
# END AI-GEN
