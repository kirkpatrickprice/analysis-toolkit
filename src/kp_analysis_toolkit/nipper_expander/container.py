from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.containers.core import CoreContainer
    from kp_analysis_toolkit.core.containers.file_processing import (
        FileProcessingContainer,
    )


class NipperExpanderContainer(containers.DeclarativeContainer):
    """Services specific to the nipper expander module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()

    # Module-specific services would go here
    # (Currently nipper expander only uses shared services)

    # Main Module Service
    nipper_expander_service: providers.Factory = providers.Factory(
        "kp_analysis_toolkit.nipper_expander.service.NipperExpanderService",
        excel_export=core.excel_export_service,
        file_processing=file_processing.file_processing_service,
        rich_output=core.rich_output,
    )


# Module's global container instance
container = NipperExpanderContainer()


def wire_nipper_expander_container() -> None:
    """
    Wire the nipper expander container for dependency injection.

    This function should be called when the nipper expander module is initialized
    to ensure all dependencies are properly wired for injection.
    """
    container.wire(
        modules=[
            "kp_analysis_toolkit.nipper_expander.cli",
            "kp_analysis_toolkit.nipper_expander.service",
            "kp_analysis_toolkit.nipper_expander.process_nipper",
        ],
    )


def configure_nipper_expander_container(
    core_container: CoreContainer,
    file_processing_container: FileProcessingContainer,
) -> None:
    """
    Configure the nipper expander container with its dependencies.

    Args:
        core_container: The core services container (includes Excel export services)
        file_processing_container: The file processing container

    """
    container.core.override(core_container)
    container.file_processing.override(file_processing_container)
