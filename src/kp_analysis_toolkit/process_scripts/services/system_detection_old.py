from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from kp_analysis_toolkit.process_scripts.models.results.system import Systems

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.utils.rich_output import RichOutput


class OSDetector(Protocol):
    """Protocol for operating system detection."""

    def detect_os(self, file_content: str) -> str | None: ...
    def get_supported_os_types(self) -> list[str]: ...


class ProducerDetector(Protocol):
    """Protocol for detecting system/software producers."""

    def detect_producer(self, file_content: str, file_path: Path) -> str | None: ...
    def get_known_producers(self) -> list[str]: ...


class DistroClassifier(Protocol):
    """Protocol for Linux distribution classification."""

    def classify_distribution(self, os_info: str, file_content: str) -> str | None: ...
    def get_supported_distributions(self) -> list[str]: ...


class SystemDetectionService:
    """Service for detecting system information from configuration files."""

    def __init__(
        self,
        os_detector: OSDetector,
        producer_detector: ProducerDetector,
        distro_classifier: DistroClassifier,
        rich_output: RichOutput,
    ) -> None:
        self.os_detector: OSDetector = os_detector
        self.producer_detector: ProducerDetector = producer_detector
        self.distro_classifier: DistroClassifier = distro_classifier
        self.rich_output: RichOutput = rich_output

    def analyze_system_file(self, file_path: Path, file_content: str) -> Systems:
        """Analyze a system file and extract system information."""
        try:
            # Detect operating system
            detected_os = self.os_detector.detect_os(file_content)
            if detected_os is None:
                self.rich_output.warning(f"Could not detect OS for: {file_path}")
                detected_os = "Unknown"

            # Detect producer/vendor
            producer = self.producer_detector.detect_producer(file_content, file_path)
            if producer is None:
                self.rich_output.warning(f"Could not detect producer for: {file_path}")
                producer = "Unknown"

            # Classify distribution (for Linux systems)
            distribution = None
            if detected_os.lower() == "linux":
                distribution = self.distro_classifier.classify_distribution(
                    detected_os,
                    file_content,
                )

            return Systems(
                file_path=str(file_path),
                operating_system=detected_os,
                producer=producer,
                distribution=distribution,
                file_hash=None,  # Would be populated by file processing service
            )

        except Exception as e:
            self.rich_output.error(f"Failed to analyze system file {file_path}: {e}")
            raise
