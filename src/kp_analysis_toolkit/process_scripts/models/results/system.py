import uuid
from pathlib import Path

from pydantic import Field

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.base import (
    FileModel,
)
from kp_analysis_toolkit.process_scripts.models.types import (
    DistroFamilyType,
    OSFamilyType,
    ProducerType,
)


class Systems(KPATBaseModel, FileModel):
    """
    Class to hold the systems configuration.

    Updated to include all the sys_filter attributes for proper filtering.
    """

    # Basic system attributes
    system_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    system_name: str
    os_family: OSFamilyType | None
    system_os: str | None = None

    # Collector script metadata
    producer: ProducerType
    producer_version: str

    # Windows-specific attributes
    product_name: str | None = None
    release_id: str | None = None
    current_build: str | None = None
    ubr: str | None = None

    # Linux-specific attributes
    distro_family: DistroFamilyType | None = None
    os_pretty_name: str | None = None
    os_version: str | None = None

    @property
    def version_components(self) -> list[int]:
        """Parse producer_version into components for comparison."""
        if not self.producer_version:
            return [0, 0, 0]
        return [int(x) for x in self.producer_version.split(".")]

    def is_windows(self) -> bool:
        """Check if the system is Windows."""
        return self.os_family == OSFamilyType.WINDOWS

    def is_linux(self) -> bool:
        """Check if the system is Linux."""
        return self.os_family == OSFamilyType.LINUX

    def is_mac(self) -> bool:
        """Check if the system is Darwin (macOS)."""
        return self.os_family == OSFamilyType.DARWIN

    def get_relative_file_path(self, base_directory: Path | None = None) -> str:
        """
        Get a display-friendly relative file path.

        Args:
            base_directory: Base directory to calculate relative path from

        Returns:
            Relative path string if base_directory provided, otherwise filename

        """
        if base_directory:
            try:
                relative_path = self.file.relative_to(base_directory)
                return str(relative_path)
            except ValueError:
                # If file is not relative to base_directory, use just the filename
                return self.file.name
        return self.file.name
