from enum import Enum


class LinuxFamilyType(str, Enum):
    """Enum to define the types of Linux families."""

    DEB = "deb"
    RPM = "rpm"
    APK = "apk"
    OTHER = "other"


class ProducerType(str, Enum):
    """Enum to define the types of producers."""

    KPNIXAUDIT = "KPNIXAUDIT"
    KPWINAUDIT = "KPWINAUDIT"
    KPMACAUDIT = "KPMACAUDIT"
    OTHER = "Other"


class SysFilterAttr(str, Enum):
    """Enum for sys_filter attribute names."""

    OS_FAMILY = "os_family"
    PRODUCER = "producer"
    KP_MAC_VERSION = "kp_mac_version"
    KP_NIX_VERSION = "kp_nix_version"
    KP_WIN_VERSION = "kp_win_version"
    PRODUCT_NAME = "product_name"
    RELEASE_ID = "release_id"
    CURRENT_BUILD = "current_build"
    UBR = "ubr"
    DISTRO_FAMILY = "distro_family"
    OS_PRETTY_NAME = "os_pretty_name"
    RPM_PRETTY_NAME = "rpm_pretty_name"
    OS_VERSION = "os_version"


class SysFilterComparisonOperators(str, Enum):
    """Enum for sys_filter comparison operators."""

    EQUALS = "eq"  # Equals -- an exact comparison
    GREATER_THAN = "gt"  # Greater than -- compares numbers, strings, list members, etc
    LESS_THAN = "lt"  # Less than -- compares numbers, strings, list members, etc
    GREATER_EQUAL = "ge"  # Greater than or equals
    LESS_EQUAL = "le"  # Less than or equals
    IN = "in"  # Tests set membership


class SystemType(str, Enum):
    """Enum to define the types of systems."""

    DARWIN = "Darwin"
    LINUX = "Linux"
    WINDOWS = "Windows"
    OTHER = "Other"
    UNDEFINED = "Undefined"
