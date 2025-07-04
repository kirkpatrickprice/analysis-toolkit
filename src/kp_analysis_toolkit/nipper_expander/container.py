from __future__ import annotations

from dependency_injector import containers, providers


class NipperExpanderContainer(containers.DeclarativeContainer):
    """Services specific to the nipper expander module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()
    excel_export = providers.DependenciesContainer()

    # Module-specific services would go here
    # (Currently nipper expander only uses shared services)

    # Main Module Service
    nipper_expander_service = providers.Factory(
        "kp_analysis_toolkit.nipper_expander.service.NipperExpanderService",
        excel_export=excel_export.excel_export_service,
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
    excel_export_container: ExcelExportContainer,
) -> None:
    """
    Configure the nipper expander container with its dependencies.

    Args:
        core_container: The core services container
        file_processing_container: The file processing container
        excel_export_container: The excel export container

    """
    container.core.override(core_container)
    container.file_processing.override(file_processing_container)
    container.excel_export.override(excel_export_container)
