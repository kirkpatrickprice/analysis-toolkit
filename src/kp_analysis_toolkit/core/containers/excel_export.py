"""Excel export container for workbook creation, formatting, and table generation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector import containers, providers

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.excel_export.protocols import (
        ExcelFormatter,
        TableGenerator,
        WorkbookEngine,
    )

from kp_analysis_toolkit.core.services.excel_export import ExcelExportService


class ExcelExportContainer(containers.DeclarativeContainer):
    """Excel export and formatting services."""

    # Dependencies
    core = providers.DependenciesContainer()

    # Excel Components
    workbook_engine: providers.Factory[WorkbookEngine] = providers.Factory(
        "kp_analysis_toolkit.core.services.excel_export.workbook_engine.WorkbookEngine",
    )

    excel_formatter: providers.Factory[ExcelFormatter] = providers.Factory(
        "kp_analysis_toolkit.core.services.excel_export.formatting.DefaultExcelFormatter",
    )

    table_generator: providers.Factory[TableGenerator] = providers.Factory(
        "kp_analysis_toolkit.core.services.excel_export.table_generation.DefaultTableGenerator",
    )

    # Main Service
    excel_export_service = providers.Factory(
        ExcelExportService,
        rich_output=core.rich_output,
        workbook_engine=workbook_engine,
        excel_formatter=excel_formatter,
        table_generator=table_generator,
    )
