from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

if TYPE_CHECKING:
    from kp_analysis_toolkit.nipper_expander.protocols import (
        DataExpander,
        NipperExpanderService,
        NipperExporter,
    )


class NipperExpanderContainer(containers.DeclarativeContainer):
    """Services specific to the Nipper Expander module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()

    # Nipper Expander Internal Services
    data_expander_service: providers.Factory[DataExpander] = providers.Factory(
        "kp_analysis_toolkit.nipper_expander.services.data_expander.DataExpansionService",
        rich_output=core.rich_output,
        csv_processor=core.csv_processor_service,
    )

    nipper_exporter_service: providers.Factory[NipperExporter] = providers.Factory(
        "kp_analysis_toolkit.nipper_expander.services.nipper_exporter.NipperExporterService",
        excel_exporter=core.excel_exporter,
        rich_output=core.rich_output,
    )

    # Main Module Service - orchestrates everything
    nipper_expander_service: providers.Factory[NipperExpanderService] = (
        providers.Factory(
            "kp_analysis_toolkit.nipper_expander.service.NipperExpanderService",
            csv_processor=core.csv_processor_service,
            data_expander=data_expander_service,
            nipper_exporter=nipper_exporter_service,
            rich_output=core.rich_output,
        )
    )


# Module's global container instance
container = NipperExpanderContainer()


def wire_nipper_expander_container() -> None:
    """
    Wire the Nipper Expander container for dependency injection.

    This function should be called when the Nipper Expander module is initialized
    to ensure all dependencies are properly wired for injection.
    """
    container.wire(
        modules=[
            "kp_analysis_toolkit.nipper_expander.service",
            "kp_analysis_toolkit.nipper_expander.services.data_expander",
            "kp_analysis_toolkit.nipper_expander.services.nipper_exporter",
        ],
    )
