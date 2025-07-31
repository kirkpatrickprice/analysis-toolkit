from collections.abc import Generator
from pathlib import Path

from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.process_scripts.models.results.system import Systems
from kp_analysis_toolkit.process_scripts.models.search.filters import SystemFilter
from kp_analysis_toolkit.process_scripts.services.system_detection.protocols import (
    DistroClassifier,
    OSDetector,
    ProducerDetector,
)


class SystemDetectionService:
    """Service for detecting and analyzing system configuration files."""

    def __init__(
        self,
        os_detector: OSDetector,
        producer_detector: ProducerDetector,
        distro_classifier: DistroClassifier,
        file_processing: FileProcessingService,
        rich_output: RichOutputService,
    ) -> None:
        """Initialize with injected dependencies including core services."""
        self.os_detector: OSDetector = os_detector
        self.producer_detector: ProducerDetector = producer_detector
        self.distro_classifier: DistroClassifier = distro_classifier
        self.file_processing: FileProcessingService = file_processing
        self.rich_output: RichOutputService = rich_output

    def enumerate_systems_from_files(
        self,
        source_directory: Path,
        file_spec: str = "*.txt",
    ) -> Generator[Systems, None, None]:
        """Discover and analyze system files in source directory."""
        # This function should enumerate the files to process
        # For example, it will read the files in config.source_files
        # and return a list of files to process list of OSFamilyType objects

        for file in self.file_processing.discover_files_by_pattern(
            base_path=source_directory, pattern=file_spec
        ):
            # Process each file and add the results to the list

            encoding: str | None = self.file_processing.detect_encoding(file)
            if encoding is None:
                # Skip files where encoding cannot be determined
                continue

            producer, producer_version = self.producer_detector.detect_producer(
                file, encoding
            )

            # Skip files where producer cannot be determined
            if producer == ProducerType.OTHER:
                warning(f"Skipping file due to unknown producer: {file}")
                continue

            distro_family: DistroFamilyType | None = None
            match producer:
                case ProducerType.KPNIXAUDIT:
                    os_family: OSFamilyType = OSFamilyType.LINUX
                    distro_family = get_distro_family(
                        file=file,
                        encoding=encoding,
                    )
                case ProducerType.KPWINAUDIT:
                    os_family: OSFamilyType = OSFamilyType.WINDOWS
                case ProducerType.KPMACAUDIT:
                    os_family: OSFamilyType = OSFamilyType.DARWIN
            system_os, os_details = get_system_details(
                file=file,
                encoding=encoding,
                producer=producer,
            )
            system_dict: dict[
                str, str | Path, OSFamilyType | DistroFamilyType | None
            ] = {
                "system_id": uuid4().hex,  # Generate a unique system ID
                "system_name": file.stem,  # Use the file name (without the extension) as the system name
                "file_hash": generate_file_hash(file),
                "file": file.absolute(),
                "system_os": system_os,
                "os_details": os_details,
                "encoding": encoding,
                "os_family": os_family,
                "distro_family": distro_family,
                "producer": producer,
                "producer_version": producer_version,
            }
            if os_details:
                system_dict.update(os_details)
            system = Systems(**system_dict)
            yield system

    def analyze_system_file(self, file_path: Path) -> Systems:
        """Analyze individual system file to extract system information."""
        # Use file_processing service for file reading and encoding detection
        # Implementation from current system analysis logic

    def filter_systems_by_criteria(
        self,
        systems: list[Systems],
        filters: list[SystemFilter] | None,
    ) -> list[Systems]:
        """Filter systems based on system filter criteria."""
        # Implementation from current filter_systems_by_criteria function
        # SystemFilter imported from: kp_analysis_toolkit.process_scripts.models.search.filters
