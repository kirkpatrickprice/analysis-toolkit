from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

from kp_analysis_toolkit.process_scripts.services.search_config import (
    SearchConfigService,
)
from kp_analysis_toolkit.process_scripts.services.system_detection import (
    SystemDetectionService,
)

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.containers.core import CoreContainer
    from kp_analysis_toolkit.core.containers.file_processing import (
        FileProcessingContainer,
    )


class ProcessScriptsContainer(containers.DeclarativeContainer):
    """Services specific to the process scripts module."""

    # Dependencies from core containers
    core = providers.DependenciesContainer()
    file_processing = providers.DependenciesContainer()

    # Search Configuration Services (process_scripts specific)
    yaml_parser = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.search_config.PyYamlParser",
    )

    file_resolver = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.search_config.StandardFileResolver",
    )

    include_processor = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.search_config.StandardIncludeProcessor",
        yaml_parser=yaml_parser,
        file_resolver=file_resolver,
    )

    search_config_service = providers.Factory(
        SearchConfigService,
        yaml_parser=yaml_parser,
        file_resolver=file_resolver,
        include_processor=include_processor,
        rich_output=core.rich_output,
    )

    # System Detection Services (process_scripts specific)
    os_detector = providers.Factory(
        "kp_analysis_toolkit.process_scripts.utils.os_detection.RegexOSDetector",
    )

    producer_detector = providers.Factory(
        "kp_analysis_toolkit.process_scripts.utils.producer_detection.SignatureProducerDetector",
    )

    distro_classifier = providers.Factory(
        "kp_analysis_toolkit.process_scripts.utils.distro_classification.PatternDistroClassifier",
    )

    system_detection_service = providers.Factory(
        SystemDetectionService,
        os_detector=os_detector,
        producer_detector=producer_detector,
        distro_classifier=distro_classifier,
        rich_output=core.rich_output,
    )

    # Search Engine Services (process_scripts specific)
    pattern_compiler = providers.Factory(
        "kp_analysis_toolkit.process_scripts.search_engine_core.RegexPatternCompiler",
    )

    field_extractor = providers.Factory(
        "kp_analysis_toolkit.process_scripts.search_engine_core.StandardFieldExtractor",
    )

    result_processor = providers.Factory(
        "kp_analysis_toolkit.process_scripts.search_engine_core.StandardResultProcessor",
    )

    search_engine_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.search_engine.SearchEngineService",
        pattern_compiler=pattern_compiler,
        field_extractor=field_extractor,
        result_processor=result_processor,
        parallel_processing=core.parallel_processing,
        rich_output=core.rich_output,
    )

    # Enhanced Excel Export Services (process_scripts specific)
    advanced_worksheet_builder = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.AdvancedWorksheetBuilder",
        base_workbook_engine=core.workbook_engine,
        rich_output=core.rich_output,
    )

    multi_sheet_formatter = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.MultiSheetFormatter",
        base_formatter=core.excel_formatter,
    )

    conditional_formatting_engine = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.ConditionalFormattingEngine",
    )

    data_validation_engine = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.DataValidationEngine",
    )

    enhanced_excel_export_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.services.excel_export.EnhancedExcelExportService",
        base_excel_service=core.excel_export_service,
        worksheet_builder=advanced_worksheet_builder,
        multi_sheet_formatter=multi_sheet_formatter,
        conditional_formatter=conditional_formatting_engine,
        data_validator=data_validation_engine,
        rich_output=core.rich_output,
    )

    # Main Module Service
    process_scripts_service = providers.Factory(
        "kp_analysis_toolkit.process_scripts.service.ProcessScriptsService",
        search_engine=search_engine_service,
        parallel_processing=core.parallel_processing_service,
        system_detection=system_detection_service,
        excel_export=enhanced_excel_export_service,  # Use enhanced service instead of base
        file_processing=file_processing.file_processing_service,
        search_config=search_config_service,
        rich_output=core.rich_output,
    )


# Module's global container instance
container = ProcessScriptsContainer()


def wire_process_scripts_container() -> None:
    """
    Wire the process scripts container for dependency injection.

    This function should be called when the process scripts module is initialized
    to ensure all dependencies are properly wired for injection.
    """
    container.wire(
        modules=[
            "kp_analysis_toolkit.process_scripts.cli",
            "kp_analysis_toolkit.process_scripts.service",
            "kp_analysis_toolkit.process_scripts.cli_functions",
            "kp_analysis_toolkit.process_scripts.process_systems",
            "kp_analysis_toolkit.process_scripts.search_engine",
            "kp_analysis_toolkit.process_scripts.excel_exporter",
        ],
    )


def configure_process_scripts_container(
    core_container: CoreContainer,
    file_processing_container: FileProcessingContainer,
) -> None:
    """
    Configure the process scripts container with its dependencies.

    Args:
        core_container: The core services container (includes Excel export services)
        file_processing_container: The file processing container
        file_processing_container: The file processing container

    """
    container.core.override(core_container)
    container.file_processing.override(file_processing_container)
