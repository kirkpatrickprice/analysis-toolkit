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


class FileSelectionResult(Enum):
    """Results from file selection operations."""

    PROCESS_ALL_FILES = "process_all_files"
