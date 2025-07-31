from enum import StrEnum

from kp_analysis_toolkit.process_scripts.models.base import EnumStrMixin


class DistroFamilyType(EnumStrMixin, StrEnum):
    """Enum to define the types of Linux families."""

    DEB = "deb"
    RPM = "rpm"
    APK = "apk"
    OTHER = "other"


class OSFamilyType(EnumStrMixin, StrEnum):
    """Enum to define the types of systems."""

    DARWIN = "Darwin"
    LINUX = "Linux"
    WINDOWS = "Windows"
    OTHER = "Other"
    UNDEFINED = "Undefined"
