from enum import Enum


class MessageType(Enum):
    """Types of messages for consistent styling."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    HEADER = "header"
    SUBHEADER = "subheader"
