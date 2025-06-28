import uuid

from pydantic import Field

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.base import (
    FileModel,
)
from kp_analysis_toolkit.process_scripts.models.enums import (
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
