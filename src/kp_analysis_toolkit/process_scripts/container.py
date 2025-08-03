# AI-GEN: CopilotChat|2025-07-31|KPAT-ListSystems|reviewed:no
"""Simplified container for process scripts module - list-systems functionality only."""

from __future__ import annotations

from typing import Any

from dependency_injector import containers, providers

from kp_analysis_toolkit.process_scripts.services.system_detection import (
    SystemDetectionService,
)


class ProcessScriptsContainer(containers.DeclarativeContainer):
    """Services specific to the process scripts module."""

    # Dependencies from core containers
    core: providers.DependenciesContainer = providers.DependenciesContainer()

    # Search Configuration Services (process_scripts specific)
    yaml_parser: providers.Singleton[Any] = providers.Singleton(
        "kp_analysis_toolkit.process_scripts.services.search_config.yaml_parser.PyYamlParser",
        file_processing=core.file_processing_service,
    )

    file_resolver: providers.Singleton[Any] = providers.Singleton(
        "kp_analysis_toolkit.process_scripts.services.search_config.file_resolver.StandardFileResolver",
        file_processing=core.file_processing_service,
    )

    search_config_service: providers.Singleton[Any] = providers.Singleton(
        "kp_analysis_toolkit.process_scripts.services.search_config.service.SearchConfigService",
        yaml_parser=yaml_parser,
        file_resolver=file_resolver,
        rich_output=core.rich_output,
    )

    # System Detection Services (process_scripts specific)
    producer_detector: providers.Singleton[Any] = providers.Singleton(
        "kp_analysis_toolkit.process_scripts.services.system_detection.producer_detection.SignatureProducerDetector",
    )

    os_detector: providers.Singleton[Any] = providers.Singleton(
        "kp_analysis_toolkit.process_scripts.services.system_detection.os_detection.RegexOSDetector",
    )

    distro_classifier: providers.Singleton[Any] = providers.Singleton(
        "kp_analysis_toolkit.process_scripts.services.system_detection.distro_classification.DefaultDistroFamilyClassifier",
    )

    system_detection_service: providers.Singleton[Any] = providers.Singleton(
        SystemDetectionService,
        producer_detector=producer_detector,
        os_detector=os_detector,
        distro_classifier=distro_classifier,
        file_processing=core.file_processing_service,
        rich_output=core.rich_output,
    )

    # Main Module Service
    process_scripts_service: providers.Singleton[Any] = providers.Singleton(
        "kp_analysis_toolkit.process_scripts.service.ProcessScriptsService",
        system_detection=system_detection_service,
        file_processing=core.file_processing_service,
        search_config=search_config_service,
        rich_output=core.rich_output,
    )


# Module's global container instance
container: ProcessScriptsContainer = ProcessScriptsContainer()


def wire_process_scripts_container() -> None:
    """
    Wire the process scripts container for dependency injection.

    This function sets up dependency injection for the process scripts module
    by wiring the container with the necessary modules.
    """
    container.wire(
        modules=[
            "kp_analysis_toolkit.process_scripts.service",
            "kp_analysis_toolkit.process_scripts.services.system_detection",
            "kp_analysis_toolkit.process_scripts.services.search_config",
        ],
    )
