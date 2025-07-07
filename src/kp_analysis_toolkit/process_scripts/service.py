from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.process_scripts.models.results.base import SearchResult
    from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
    from kp_analysis_toolkit.process_scripts.models.systems import Systems
    from kp_analysis_toolkit.process_scripts.services.enhanced_excel_export import (
        EnhancedExcelExportService,
    )
    from kp_analysis_toolkit.process_scripts.services.search_config import (
        SearchConfigService,
    )
    from kp_analysis_toolkit.process_scripts.services.search_engine import (
        SearchEngineService,
    )
    from kp_analysis_toolkit.process_scripts.services.system_detection import (
        SystemDetectionService,
    )
    from kp_analysis_toolkit.utils.rich_output import RichOutput


class ProcessScriptsService:
    """Main service for the process scripts module."""

    def __init__(  # noqa: PLR0913
        self,
        search_engine: SearchEngineService,
        system_detection: SystemDetectionService,
        excel_export: EnhancedExcelExportService,  # Use enhanced service
        file_processing: FileProcessingService,
        search_config: SearchConfigService,
        rich_output: RichOutput,
    ) -> None:
        self.search_engine: SearchEngineService = search_engine
        self.system_detection: SystemDetectionService = system_detection
        self.excel_export: EnhancedExcelExportService = excel_export
        self.file_processing: FileProcessingService = file_processing
        self.search_config: SearchConfigService = search_config
        self.rich_output: RichOutput = rich_output

    def execute(
        self,
        input_directory: Path,
        config_file: Path,
        output_path: Path,
        max_workers: int = 4,
    ) -> None:
        """Execute the complete process scripts workflow."""
        try:
            self.rich_output.header("Starting Process Scripts Analysis")

            # Load search configurations
            search_configs: list[SearchConfig] = self.search_config.load_search_configs(
                config_file,
            )

            # Discover and analyze system files
            system_files: list[Path] = self._discover_system_files(input_directory)
            systems: list[Systems] = self._analyze_systems(system_files)

            # Execute search configurations in parallel
            search_results = self.search_configs_with_processes(
                search_configs,
                systems,
                max_workers,
            )

            # Export results to Excel
            self._export_results(search_results, output_path)

            self.rich_output.success("Process Scripts analysis completed successfully")

        except Exception as e:
            self.rich_output.error(f"Process Scripts execution failed: {e}")
            raise

    def _discover_system_files(self, directory: Path) -> list[Path]:
        """Discover system configuration files in the input directory."""
        # Implementation would scan directory for supported file types

    def _analyze_systems(self, file_paths: list[Path]) -> list[Systems]:
        """Analyze system files to extract system information."""
        # Implementation would process files using system detection service

    def _export_results(self, results: list[SearchResult], output_path: Path) -> None:
        """Export search results to Excel format using enhanced capabilities."""
        try:
            # Use enhanced Excel export service with process scripts specific features
            self.excel_export.export_search_results(
                search_results=results,
                output_path=output_path,
                include_summary=True,  # Create summary sheet
                apply_formatting=True,  # Apply conditional formatting
            )

            # Also create a simplified version for quick review
            simplified_path = output_path.with_name(f"simplified_{output_path.name}")
            self.excel_export.base_excel_service.export_dataframe(
                data=self._create_simplified_dataframe(results),
                output_path=simplified_path,
                sheet_name="Quick View",
            )

        except Exception as e:
            self.rich_output.error(f"Failed to export results: {e}")
            raise
