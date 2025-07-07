from kp_analysis_toolkit.cli.main import cli, main
from kp_analysis_toolkit.core.containers.application import (
    initialize_dependency_injection,
)
from kp_analysis_toolkit.utils.rich_output import get_rich_output
from kp_analysis_toolkit.utils.version_checker import check_and_prompt_update

__all__ = [
    "check_and_prompt_update",
    "cli",
    "get_rich_output",
    "initialize_dependency_injection",
    "main",
]
