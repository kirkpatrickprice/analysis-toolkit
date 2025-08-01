"""Main application container that orchestrates all other containers."""

from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.containers.core import CoreContainer
from kp_analysis_toolkit.nipper_expander.container import NipperExpanderContainer
from kp_analysis_toolkit.process_scripts.container import ProcessScriptsContainer
from kp_analysis_toolkit.rtf_to_text.container import RtfToTextContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container that exposes all core services."""

    # Core container with all shared services
    core: providers.Container[CoreContainer] = providers.Container(CoreContainer)

    # Module containers
    rtf_to_text: providers.Container[RtfToTextContainer] = providers.Container(
        RtfToTextContainer,
        core=core,
    )
    nipper: providers.Container[NipperExpanderContainer] = providers.Container(
        NipperExpanderContainer,
        core=core,
    )

    # Lazy-initialized process_scripts container
    process_scripts: providers.Singleton[ProcessScriptsContainer] = providers.Singleton(
        ProcessScriptsContainer,
    )


# Global container instance
container = ApplicationContainer()


def configure_application_container(
    *,
    verbose: bool = False,
    quiet: bool = False,
    console_width: int = 120,
    force_terminal: bool = True,
    stderr_enabled: bool = True,
) -> None:
    """Configure the application container with core settings."""
    container.core().config.verbose.from_value(verbose)
    container.core().config.quiet.from_value(quiet)
    container.core().config.console_width.from_value(console_width)
    container.core().config.force_terminal.from_value(force_terminal)
    container.core().config.stderr_enabled.from_value(stderr_enabled)

    # Configure process_scripts container with dependencies
    container.process_scripts().core.override(container.core())


def wire_application_container() -> None:
    """Wire the main application container for CLI integration."""
    container.wire(
        modules=[
            "kp_analysis_toolkit.cli",
            "kp_analysis_toolkit.cli.commands.rtf_to_text",
            "kp_analysis_toolkit.cli.commands.nipper",
            "kp_analysis_toolkit.cli.commands.scripts",
        ],
    )

    # Wire command containers
    container.rtf_to_text().wire(
        modules=[
            "kp_analysis_toolkit.rtf_to_text.service",
            "kp_analysis_toolkit.rtf_to_text.services.rtf_converter",
        ],
    )
    container.nipper().wire(
        modules=[
            "kp_analysis_toolkit.nipper_expander.service",
            "kp_analysis_toolkit.nipper_expander.services.data_expander",
            "kp_analysis_toolkit.nipper_expander.services.nipper_exporter",
        ],
    )

    # Wire process_scripts container
    container.process_scripts().wire(
        modules=[
            "kp_analysis_toolkit.process_scripts.service",
            "kp_analysis_toolkit.process_scripts.services.system_detection",
        ],
    )


def wire_module_containers() -> None:
    """Wire core container for backward compatibility utilities."""
    # Wire file processing utilities for backward compatibility
    container.core().wire(
        modules=[
            "kp_analysis_toolkit.utils.get_file_encoding",
            "kp_analysis_toolkit.utils.hash_generator",
        ],
    )


def initialize_dependency_injection(
    *,
    verbose: bool = False,
    quiet: bool = False,
    console_width: int = 120,
    force_terminal: bool = True,
    stderr_enabled: bool = True,
) -> None:
    """Initialize dependency injection for all core services."""
    # 1. Configure the application container
    configure_application_container(
        verbose=verbose,
        quiet=quiet,
        console_width=console_width,
        force_terminal=force_terminal,
        stderr_enabled=stderr_enabled,
    )

    # 2. Wire the application container
    wire_application_container()

    # 3. Wire core container for backward compatibility utilities
    wire_module_containers()
