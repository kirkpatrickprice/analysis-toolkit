import uuid
from pathlib import Path

from pydantic import Field, computed_field

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.base import (
    FileModel,
)
from kp_analysis_toolkit.process_scripts.models.enums import (
    LinuxFamilyType,
    ProducerType,
    SystemType,
)


class Systems(KPATBaseModel, FileModel):
    """
    Class to hold the systems configuration.

    Updated to include all the sys_filter attributes for proper filtering.
    """

    __tablename__ = "systems"

    system_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    system_name: str
    system_type: SystemType
    linux_family: LinuxFamilyType | None = None
    system_os: str | None = None
    producer: ProducerType
    producer_version: str

    # Additional fields for sys_filter support
    os_family: str | None = None  # Maps to system_type but as string for filtering
    kp_mac_version: str | None = None
    kp_nix_version: str | None = None
    kp_win_version: str | None = None
    product_name: str | None = None
    release_id: str | None = None
    current_build: str | None = None
    ubr: str | None = None
    distro_family: str | None = None  # Maps to linux_family but as string
    os_pretty_name: str | None = None
    rpm_pretty_name: str | None = None
    os_version: str | None = None

    @computed_field
    @property
    def os_family_computed(self) -> str:
        """Compute os_family from system_type for sys_filter compatibility."""
        return self.system_type.value if self.system_type else "Unknown"

    @computed_field
    @property
    def distro_family_computed(self) -> str:
        """Compute distro_family from linux_family for sys_filter compatibility."""
        return self.linux_family.value if self.linux_family else "unknown"

    @computed_field
    @property
    def producer_computed(self) -> str:
        """Compute producer string for sys_filter compatibility."""
        return self.producer.value if self.producer else "Unknown"

    class Config:
        arbitrary_types_allowed = True


class RawData(KPATBaseModel):
    """Base model for raw data processing."""

    data: str
    source_file: Path
    line_number: int | None = None
    timestamp: str | None = None

    class Config:
        arbitrary_types_allowed = True
