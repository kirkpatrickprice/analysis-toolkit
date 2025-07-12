"""Core container for shared services like RichOutput and Excel Export."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.excel_export.protocols import (
        WorkbookEngine,
    )
    from kp_analysis_toolkit.core.services.file_processing.protocols import (
        EncodingDetector,
        FileValidator,
        HashGenerator,
    )

from kp_analysis_toolkit.core.services.excel_export.formatting import (
    DefaultColumnWidthAdjuster,
    DefaultDateFormatter,
    DefaultExcelFormatter,
    DefaultRowHeightAdjuster,
    DefaultTitleFormatter,
)
from kp_analysis_toolkit.core.services.excel_export.service import ExcelExportService
from kp_analysis_toolkit.core.services.excel_export.sheet_management import (
    DefaultSheetNameSanitizer,
)
from kp_analysis_toolkit.core.services.excel_export.table_generation import (
    DefaultTableGenerator,
)
from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.models.rich_config import RichOutputConfig


def _setup_utils_di_integration(
    file_processing_service: FileProcessingService,
) -> FileProcessingService:
    """Set up DI integration between file processing service and legacy utils."""
    from kp_analysis_toolkit.utils import get_file_encoding, hash_generator

    hash_generator.set_file_processing_service(file_processing_service)
    get_file_encoding.set_file_processing_service(file_processing_service)
    return file_processing_service


class CoreContainer(containers.DeclarativeContainer):
    """Container for core shared services."""

    # Configuration
    config = providers.Configuration()

    # RichOutput Service - Singleton because it maintains global console state
    # and configuration that should be consistent across the entire application
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

    # Excel Export Services - Using Factory providers for stateless services
    # and Singleton for the main service to ensure consistent formatting behavior

    # Sheet management services
    sheet_name_sanitizer = providers.Factory(DefaultSheetNameSanitizer)

    # Formatting services - Factory because they are stateless
    column_width_adjuster = providers.Factory(DefaultColumnWidthAdjuster)
    date_formatter = providers.Factory(DefaultDateFormatter)
    row_height_adjuster = providers.Factory(DefaultRowHeightAdjuster)
    title_formatter = providers.Factory(DefaultTitleFormatter)

    # Excel formatter with dependency injection
    excel_formatter = providers.Factory(
        DefaultExcelFormatter,
        column_width_adjuster=column_width_adjuster,
    )

    # Table generator with all required dependencies
    table_generator = providers.Factory(
        DefaultTableGenerator,
        formatter=excel_formatter,
        date_formatter=date_formatter,
        column_width_adjuster=column_width_adjuster,
        row_height_adjuster=row_height_adjuster,
        table_styler=providers.Factory(
            "kp_analysis_toolkit.core.services.excel_export.formatting.DefaultTableStyler",
        ),
    )

    # Workbook engine - Factory for flexibility with different engines
    workbook_engine: providers.Factory[WorkbookEngine] = providers.Factory(
        "kp_analysis_toolkit.core.services.excel_export.workbook_engine.WorkbookEngine",
    )

    # Excel Export Service - Singleton to ensure consistent behavior across the application
    # This service maintains formatting standards and should be consistent
    excel_export_service: providers.Singleton[ExcelExportService] = providers.Singleton(
        ExcelExportService,
        sheet_name_sanitizer=sheet_name_sanitizer,
        column_width_adjuster=column_width_adjuster,
        date_formatter=date_formatter,
        row_height_adjuster=row_height_adjuster,
        excel_formatter=excel_formatter,
        table_generator=table_generator,
        title_formatter=title_formatter,
        workbook_engine=workbook_engine,
    )

    # File Processing Services - Factory providers for stateless file operations
    # Each file operation should use fresh instances for isolation and parallel processing

    encoding_detector: providers.Factory[EncodingDetector] = providers.Factory(
        "kp_analysis_toolkit.core.services.file_processing.encoding.RobustEncodingDetector",
        rich_output=rich_output,
    )

    hash_generator: providers.Factory[HashGenerator] = providers.Factory(
        "kp_analysis_toolkit.core.services.file_processing.hashing.SHA384FileHashGenerator",
    )

    file_validator: providers.Factory[FileValidator] = providers.Factory(
        "kp_analysis_toolkit.utils.file_validator.PathLibFileValidator",
    )

    # File Processing Service with DI integration
    file_processing_service: providers.Factory[FileProcessingService] = (
        providers.Factory(
            _setup_utils_di_integration,
            file_processing_service=providers.Factory(
                FileProcessingService,
                rich_output=rich_output,
                encoding_detector=encoding_detector,
                hash_generator=hash_generator,
                file_validator=file_validator,
            ),
        )
    )
