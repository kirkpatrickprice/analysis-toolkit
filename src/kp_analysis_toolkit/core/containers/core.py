"""Core container for shared services like RichOutput and ParallelProcessing."""

from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.models.rich_config import RichOutputConfig


class CoreContainer(containers.DeclarativeContainer):
    """Container for core shared services."""

    # Configuration
    config = providers.Configuration()

    # RichOutput Service
    rich_output: providers.Singleton[RichOutputService] = providers.Singleton(
        RichOutputService,
        config=providers.Factory(
            RichOutputConfig,
            verbose=config.verbose,
            quiet=config.quiet,
            console_width=config.console_width,
            force_terminal=config.force_terminal,
            stderr_enabled=config.stderr_enabled,
        ),
    )

    # NOTE: Parallel processing services will be added when implemented
    # For now, only Rich Output service is configured for DI
