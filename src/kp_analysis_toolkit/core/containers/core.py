from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.utils.rich_output import RichOutput


class CoreContainer(containers.DeclarativeContainer):
    """Core services shared across all modules."""

    # Configuration
    config = providers.Configuration()

    # Core Services
    rich_output = providers.Singleton(
        RichOutput,
        verbose=config.verbose,
        quiet=config.quiet,
    )

    # # Parallel Processing Services (global, available to all modules)
    # executor_factory = providers.Factory(
    #     "kp_analysis_toolkit.core.parallel_engine.ProcessPoolExecutorFactory",
    #     max_workers=config.max_workers.provided,
    # )

    # progress_tracker = providers.Factory(
    #     "kp_analysis_toolkit.core.parallel_engine.ProgressTracker",
    #     rich_output=rich_output,
    # )

    # interrupt_handler = providers.Factory(
    #     "kp_analysis_toolkit.core.parallel_engine.InterruptHandler",
    #     rich_output=rich_output,
    # )

    # parallel_processing_service = providers.Factory(
    #     ParallelProcessingService,
    #     executor_factory=executor_factory,
    #     progress_tracker=progress_tracker,
    #     interrupt_handler=interrupt_handler,
    #     rich_output=rich_output,
    # )
