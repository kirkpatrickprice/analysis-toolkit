from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.containers.core import CoreContainer
    from kp_analysis_toolkit.core.containers.file_processing import (
        FileProcessingContainer,
    )


class RtfToTextContainer(containers.DeclarativeContainer):
    """Services specific to the RTF to text module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()

    # Module-specific services would go here
    # (Currently RTF to text only uses shared services)

    # Main Module Service
    rtf_to_text_service = providers.Factory(
        "kp_analysis_toolkit.rtf_to_text.service.RtfToTextService",
        file_processing=file_processing.file_processing_service,
        rich_output=core.rich_output,
    )


# Module's global container instance
container = RtfToTextContainer()


def wire_rtf_to_text_container() -> None:
    """
    Wire the RTF to text container for dependency injection.

    This function should be called when the RTF to text module is initialized
    to ensure all dependencies are properly wired for injection.
    """
    container.wire(
        modules=[
            "kp_analysis_toolkit.rtf_to_text.cli",
            "kp_analysis_toolkit.rtf_to_text.service",
            "kp_analysis_toolkit.rtf_to_text.process_rtf",
        ],
    )


def configure_rtf_to_text_container(
    core_container: CoreContainer,
    file_processing_container: FileProcessingContainer,
) -> None:
    """
    Configure the RTF to text container with its dependencies.

    Args:
        core_container: The core services container
        file_processing_container: The file processing container

    """
    container.core.override(core_container)
    container.file_processing.override(file_processing_container)
