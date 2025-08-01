# AI-GEN: gpt-4o|2025-01-30|system-detection-protocols-cleanup|reviewed:no
from collections.abc import Generator
from pathlib import Path
from typing import Protocol

from kp_analysis_toolkit.core.services.file_processing.protocols import ContentStreamer
from kp_analysis_toolkit.process_scripts.models.results.system import Systems
from kp_analysis_toolkit.process_scripts.models.search.filters import SystemFilter
from kp_analysis_toolkit.process_scripts.models.types import (
    DistroFamilyType,
    OSFamilyType,
    ProducerType,
)


class OSDetector(Protocol):
    """Protocol for operating system detection."""

    def detect_os(
        self,
        content_stream: ContentStreamer,
        producer_type: ProducerType,
    ) -> dict[str, str | None]:
        """Detect OS details using targeted content patterns."""
        ...

    def get_supported_os_types(self) -> list[OSFamilyType]:
        """Get list of supported OS types."""
        ...


class ProducerDetector(Protocol):
    """Protocol for detecting system/software producers."""

    def detect_producer(
        self,
        content_stream: ContentStreamer,
    ) -> tuple[ProducerType, str] | None:
        """Detect producer and version using early file content (typically first 20 lines)."""
        ...

    def get_known_producers(self) -> list[str]:
        """Get list of known producers."""
        ...


class DistroClassifier(Protocol):
    """Protocol for Linux distribution classification."""

    def classify_distribution(
        self,
        content_stream: ContentStreamer,
        os_info: str,
    ) -> DistroFamilyType:
        """Classify Linux distribution using specific content patterns."""
        ...

    def get_supported_distributions(self) -> list[DistroFamilyType]:
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
