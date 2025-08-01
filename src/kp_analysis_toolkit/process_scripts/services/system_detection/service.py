"""System detection service for analyzing system configuration files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kp_analysis_toolkit.process_scripts.models.results.system import Systems
from kp_analysis_toolkit.process_scripts.models.types import (
    OSFamilyType,
    ProducerType,
)
from kp_analysis_toolkit.process_scripts.services.system_detection.protocols import (
    OSDetector,
    ProducerDetector,
)

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing.service import (
        FileProcessingService,
    )
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.process_scripts.services.system_detection.protocols import (
        DistroClassifier,
        OSDetector,
        ProducerDetector,
    )


class SystemDetectionService:
    """Service for detecting and analyzing systems from configuration files."""

    def __init__(
        self,
        producer_detector: ProducerDetector,
        os_detector: OSDetector,
        distro_classifier: DistroClassifier,
        file_processing: FileProcessingService,
        rich_output: RichOutputService,
    ) -> None:
        """
        Initialize the system detection service.

        Args:
            producer_detector: Service for detecting producers
            os_detector: Service for detecting OS details
            distro_classifier: Service for classifying Linux distributions
            file_processing: Service for file processing operations
            rich_output: Service for rich console output

        """
        self.producer_detector: ProducerDetector = producer_detector
        self.os_detector: OSDetector = os_detector
        self.distro_classifier: DistroClassifier = distro_classifier
        self.file_processing: FileProcessingService = file_processing
        self.rich_output: RichOutputService = rich_output

    def enumerate_systems_from_files(self, file_paths: list[Path]) -> list[Systems]:
        """
        Analyze multiple files to extract system information.

        Args:
            file_paths: List of file paths to analyze

        Returns:
            List of Systems objects containing detected system information

        """
        systems: list[Systems] = []
        for file_path in file_paths:
            system: Systems | None = self._analyze_system_file(file_path)
            if system:
                systems.append(system)
        return systems

    def _analyze_system_file(self, file_path: Path) -> Systems | None:
        """
        Analyze a single file to extract system information.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Systems object if system information is found, None otherwise

        """
        try:
            # Create content streamer to efficiently read file
            streamer = self.file_processing.create_content_streamer(file_path)

            # Detect producer information
            producer_info = self.producer_detector.detect_producer(streamer)
            if not producer_info:
                self.rich_output.warning(
                    f"No producer information found in {file_path}",
                )
                return None

            producer_type, producer_version = producer_info
            os_family = self._get_os_family_from_producer(producer_type)

            # Get OS-specific details
            os_details = self.os_detector.detect_os(streamer, producer_type)

            # For Linux systems, classify the distribution
            if os_family == OSFamilyType.LINUX:
                os_name = (
                    os_details.get("os_pretty_name")
                    or os_details.get("system_os")
                    or ""
                )
                distro_family = self.distro_classifier.classify_distribution(
                    streamer,
                    os_name,
                )
                os_details["distro_family"] = distro_family

            # Generate file hash
            file_hash = self.file_processing.generate_hash(file_path)

            return Systems(
                system_name=file_path.stem,
                os_family=os_family,
                producer=producer_type,
                producer_version=producer_version,
                file=file_path,
                file_hash=file_hash,
                **os_details,
            )

        except (OSError, ValueError) as e:
            self.rich_output.warning(f"Error analyzing file {file_path}: {e}")
            return None

    def _get_os_family_from_producer(self, producer_type: ProducerType) -> OSFamilyType:
        """
        Determine OS family from producer type.

        Args:
            producer_type: The detected producer type

        Returns:
            Corresponding OS family type

        """
        producer_to_os_map = {
            ProducerType.KPWINAUDIT: OSFamilyType.WINDOWS,
            ProducerType.KPNIXAUDIT: OSFamilyType.LINUX,
            ProducerType.KPMACAUDIT: OSFamilyType.DARWIN,
        }
        return producer_to_os_map.get(producer_type, OSFamilyType.OTHER)
