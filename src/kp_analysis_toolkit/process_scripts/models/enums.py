from enum import StrEnum

from kp_analysis_toolkit.process_scripts.models.base import EnumStrMixin


class DistroFamilyType(EnumStrMixin, StrEnum):
    """Enum to define the types of Linux families."""

    DEB = "deb"
    RPM = "rpm"
    APK = "apk"
    OTHER = "other"


class ProducerType(EnumStrMixin, StrEnum):
    """Enum to define the types of producers."""

    KPNIXAUDIT = "KPNIXAUDIT"
    KPWINAUDIT = "KPWINAUDIT"
    KPMACAUDIT = "KPMACAUDIT"
    OTHER = "Other"


class SysFilterAttr(EnumStrMixin, StrEnum):
    """System attributes that can be used in filters."""

    OS_FAMILY = "os_family"  # Matches OSFamilyType
    DISTRO_FAMILY = "distro_family"  # Matches DistroFamilyType
    PRODUCER = "producer"  # Matches ProducerType
    PRODUCER_VERSION = "producer_version"

    # OS-specific attributes
    PRODUCT_NAME = "product_name"
    RELEASE_ID = "release_id"
    CURRENT_BUILD = "current_build"
    UBR = "ubr"
    OS_PRETTY_NAME = "os_pretty_name"
    OS_VERSION = "os_version"


class SysFilterComparisonOperators(EnumStrMixin, StrEnum):
    """Enum for sys_filter comparison operators."""

    EQUALS = "eq"  # Equals -- an exact comparison
    GREATER_THAN = "gt"  # Greater than -- compares numbers, strings, list members, etc
    LESS_THAN = "lt"  # Less than -- compares numbers, strings, list members, etc
    GREATER_EQUAL = "ge"  # Greater than or equals
    LESS_EQUAL = "le"  # Less than or equals
    IN = "in"  # Tests set membership


class OSFamilyType(EnumStrMixin, StrEnum):
    """Enum to define the types of systems."""

    DARWIN = "Darwin"
    LINUX = "Linux"
    WINDOWS = "Windows"
    OTHER = "Other"
    UNDEFINED = "Undefined"
