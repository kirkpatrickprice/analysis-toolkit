from enum import StrEnum

from pydantic import field_validator

from kp_analysis_toolkit.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.base import EnumStrMixin
from kp_analysis_toolkit.process_scripts.models.types import SysFilterValueType


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


class SystemFilter(KPATBaseModel):
    """System filter configuration for limiting search applicability."""

    attr: SysFilterAttr
    comp: SysFilterComparisonOperators
    value: SysFilterValueType

    @field_validator("value")
    @classmethod
    def validate_value_for_operator(
        cls,
        value: SysFilterValueType,
        info: dict,
    ) -> SysFilterValueType:
        """Validate that the value type is appropriate for the comparison operator."""
        comp: str = info.data.get("comp")

        if comp == SysFilterComparisonOperators.IN:
            if not isinstance(value, list | set):
                message: str = "'in' operator requires a list or set value"
                raise ValueError(message)
        elif comp in [
            SysFilterComparisonOperators.GREATER_THAN,
            SysFilterComparisonOperators.LESS_THAN,
            SysFilterComparisonOperators.GREATER_EQUAL,
            SysFilterComparisonOperators.LESS_EQUAL,
        ] and isinstance(value, list | set):
            message: str = f"'{comp}' operator cannot be used with list or set values"
            raise ValueError(message)

        return value
