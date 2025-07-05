"""Main application container that orchestrates all other containers."""

from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.containers.core import CoreContainer


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container - Rich Output DI only for now."""

    # Core containers - only what's needed for Rich Output
    core: providers.Container[CoreContainer] = providers.Container(CoreContainer)


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
    """Configure the application container with Rich Output settings only."""
    container.core().config.verbose.from_value(verbose)
    container.core().config.quiet.from_value(quiet)
    container.core().config.console_width.from_value(console_width)
    container.core().config.force_terminal.from_value(force_terminal)
    container.core().config.stderr_enabled.from_value(stderr_enabled)


def wire_application_container() -> None:
    """Wire the main application container for CLI integration."""
    container.wire(
        modules=[
            "kp_analysis_toolkit.cli",
        ],
    )


def wire_module_containers() -> None:
    """Wire module containers - currently no modules use DI yet."""
    # TODO @flyguy62n: Add module container wiring as modules are migrated to DI  # noqa: FIX002, TD003
    pass  # noqa: PIE790


def initialize_dependency_injection(
    *,
    verbose: bool = False,
    quiet: bool = False,
    console_width: int = 120,
    force_terminal: bool = True,
    stderr_enabled: bool = True,
) -> None:
    """Initialize dependency injection for Rich Output only."""
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

    # 3. Module containers - not implemented yet
    # wire_module_containers()  # Skip for now
