from __future__ import annotations

from typing import TYPE_CHECKING

from kp_analysis_toolkit.core.services.excel_export import ExcelExportService

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.excel_export import ExcelExportService
    from kp_analysis_toolkit.process_scripts.models.results.base import SearchResults


class EnhancedExcelExportService:
    """Service for exporting search results to Excel with enhanced features."""

    def __init__(self, base_excel_service: ExcelExportService) -> None:
        self.base_excel_service: ExcelExportService = base_excel_service

    def export_search_results(
        self,
        search_results: list[SearchResults],
        output_path: Path,
        include_summary: bool = False,
        apply_formatting: bool = False,
    ) -> None:
        """Export search results to an Excel file with optional enhancements."""
        # Implementation would use self.base_excel_service to create the Excel file
