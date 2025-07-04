from __future__ import annotations

from dependency_injector import containers, providers

from kp_analysis_toolkit.core.services.excel_export import ExcelExportService


class ExcelExportContainer(containers.DeclarativeContainer):
    """Excel export and formatting services."""

    # Dependencies
    core = providers.DependenciesContainer()

    # Excel Components
    workbook_engine = providers.Factory(
        "kp_analysis_toolkit.utils.excel_utils.OpenpyxlEngine",
    )

    excel_formatter = providers.Factory(
        "kp_analysis_toolkit.utils.excel_utils.StandardExcelFormatter",
    )

    table_generator = providers.Factory(
        "kp_analysis_toolkit.utils.excel_utils.StandardTableGenerator",
    )

    # Main Service
    excel_export_service = providers.Factory(
        ExcelExportService,
        workbook_engine=workbook_engine,
        formatter=excel_formatter,
        table_generator=table_generator,
        rich_output=core.rich_output,
    )
