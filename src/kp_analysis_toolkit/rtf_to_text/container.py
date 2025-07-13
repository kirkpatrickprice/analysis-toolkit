from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

if TYPE_CHECKING:
    from kp_analysis_toolkit.rtf_to_text.service import RtfToTextService
    from kp_analysis_toolkit.rtf_to_text.services.rtf_converter import (
        RtfConverterService,
    )


class RtfToTextContainer(containers.DeclarativeContainer):
    """Services specific to the RTF to text module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()

    # RTF Processing Services
    rtf_converter_service: providers.Factory[RtfConverterService] = providers.Factory(
        "kp_analysis_toolkit.rtf_to_text.services.rtf_converter.RtfConverterService",
        rich_output=core.rich_output,
        file_processing=core.file_processing_service,
    )

    # Main Module Service
    rtf_to_text_service: providers.Factory[RtfToTextService] = providers.Factory(
        "kp_analysis_toolkit.rtf_to_text.service.RtfToTextService",
        rtf_converter=rtf_converter_service,
        rich_output=core.rich_output,
        file_processing=core.file_processing_service,
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
            "kp_analysis_toolkit.rtf_to_text.service",
            "kp_analysis_toolkit.rtf_to_text.services.rtf_converter",
        ],
    )
