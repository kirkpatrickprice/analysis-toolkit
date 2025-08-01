from enum import StrEnum

from kp_analysis_toolkit.process_scripts.models.mixins import EnumStrMixin


class ProducerType(EnumStrMixin, StrEnum):
    """Enum to define the types of producers."""

    KPNIXAUDIT = "KPNIXAUDIT"
    KPWINAUDIT = "KPWINAUDIT"
    KPMACAUDIT = "KPMACAUDIT"
    OTHER = "Other"
