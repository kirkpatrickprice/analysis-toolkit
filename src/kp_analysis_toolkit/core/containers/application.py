from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.containers.core import CoreContainer
from kp_analysis_toolkit.core.containers.excel_export import ExcelExportContainer
from kp_analysis_toolkit.core.containers.file_processing import FileProcessingContainer
from kp_analysis_toolkit.nipper_expander.container import NipperExpanderContainer
from kp_analysis_toolkit.process_scripts.container import ProcessScriptsContainer
from kp_analysis_toolkit.rtf_to_text.container import RtfToTextContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container that wires all module containers together."""

    # Core containers
    core: providers.Container[CoreContainer] = providers.Container(CoreContainer)

    file_processing: providers.Container[FileProcessingContainer] = providers.Container(
        FileProcessingContainer,
        core=core,
    )

    excel_export: providers.Container[ExcelExportContainer] = providers.Container(
        ExcelExportContainer,
        core=core,
    )

    # Module containers
    process_scripts: providers.Container[ProcessScriptsContainer] = providers.Container(
        ProcessScriptsContainer,
        core=core,
        file_processing=file_processing,
        excel_export=excel_export,
    )

    nipper_expander: providers.Container[NipperExpanderContainer] = providers.Container(
        NipperExpanderContainer,
        core=core,
        file_processing=file_processing,
        excel_export=excel_export,
    )

    rtf_to_text: providers.Container[RtfToTextContainer] = providers.Container(
        RtfToTextContainer,
        core=core,
        file_processing=file_processing,
    )


# Global container instance
container = ApplicationContainer()


def wire_application_container() -> None:
    """
    Wire the main application container and all module containers.

    This function orchestrates the wiring of all containers in the application.
    It ensures that the core containers are wired first, followed by module containers.
    """
    # Wire the main application container for CLI integration
    container.wire(
        modules=[
            "kp_analysis_toolkit.cli",
        ],
    )


def wire_module_containers() -> None:
    """
    Wire all module containers using their respective wiring functions.

    This function coordinates the wiring of individual module containers,
    demonstrating Distributed Wiring where each module is responsible
    for its own dependency wiring.
    """
    from kp_analysis_toolkit.nipper_expander.container import (
        configure_nipper_expander_container,
        wire_nipper_expander_container,
    )
    from kp_analysis_toolkit.process_scripts.container import (
        configure_process_scripts_container,
        wire_process_scripts_container,
    )
    from kp_analysis_toolkit.rtf_to_text.container import (
        configure_rtf_to_text_container,
        wire_rtf_to_text_container,
    )

    # Configure module containers with their dependencies
    configure_process_scripts_container(
        core_container=container.core(),
        file_processing_container=container.file_processing(),
        excel_export_container=container.excel_export(),
    )

    configure_nipper_expander_container(
        core_container=container.core(),
        file_processing_container=container.file_processing(),
        excel_export_container=container.excel_export(),
    )

    configure_rtf_to_text_container(
        core_container=container.core(),
        file_processing_container=container.file_processing(),
    )

    # Wire each module container
    wire_process_scripts_container()
    wire_nipper_expander_container()
    wire_rtf_to_text_container()


def configure_application_container(
    *,  # Require keyword arguments for clarity
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """
    Configure the application container with runtime settings.

    Args:
        verbose: Enable verbose output
        quiet: Enable quiet mode
        max_workers: Maximum number of worker processes

    """
    container.core().config.verbose.from_value(verbose)
    container.core().config.quiet.from_value(quiet)
    container.core().config.max_workers.from_value(max_workers or 4)


def initialize_dependency_injection(
    *,  # Require keyword arguments for clarity
    verbose: bool = False,
    quiet: bool = False,
    max_workers: int | None = None,
) -> None:
    """
    Initialize the complete dependency injection system.

    This is the main entry point for setting up DI throughout the application.
    It configures and wires all containers in the correct order.

    Args:
        verbose: Enable verbose output
        quiet: Enable quiet mode
        max_workers: Maximum number of worker processes

    """
    # 1. Configure the application container
    configure_application_container(
        verbose=verbose, quiet=quiet, max_workers=max_workers
    )

    # 2. Wire the application container
    wire_application_container()

    # 3. Wire all module containers
    wire_module_containers()
