from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.process_scripts.models.results.search import SearchResults
    from kp_analysis_toolkit.process_scripts.models.results.system import Systems
    from kp_analysis_toolkit.process_scripts.models.search.configs import (
        SearchConfig,
    )
    from kp_analysis_toolkit.process_scripts.services.report_generator import (
        ReportGeneratorService,
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


# AI-GEN: CopilotChat|2025-07-31|KPAT-ListSystems|reviewed:no
class ProcessScriptsService:
    """Main service for the process scripts module."""

    def __init__(
        self,
        system_detection: SystemDetectionService,
        file_processing: FileProcessingService,
        search_config: SearchConfigService,
        search_engine: SearchEngineService,
        report_generator: ReportGeneratorService,
        rich_output: RichOutputService,
    ) -> None:
        self.system_detection: SystemDetectionService = system_detection
        self.file_processing: FileProcessingService = file_processing
        self.search_config: SearchConfigService = search_config
        self.search_engine: SearchEngineService = search_engine
        self.report_generator: ReportGeneratorService = report_generator
        self.rich_output: RichOutputService = rich_output

    def list_systems(
        self,
        input_directory: Path,
        file_pattern: str = "*.txt",
    ) -> list[Systems]:
        """List all systems found in the specified files."""
        try:
            # Discover files matching the pattern
            discovered_files: list[Path] = (
                self.file_processing.discover_files_by_pattern(
                    base_path=input_directory,
                    pattern=file_pattern,
                    recursive=True,
                )
            )

            # Extract systems from each file
            systems: list[Systems] = []
            for file_path in discovered_files:
                file_systems: list[Systems] = (
                    self.system_detection.enumerate_systems_from_files(
                        [file_path],
                    )
                )
                systems.extend(file_systems)

        except Exception as e:
            self.rich_output.error(f"Failed to list systems: {e}")
            raise
        else:
            return systems

    def list_audit_configs(
        self,
        config_path: Path,
    ) -> list[Path]:
        """
        List the available audit configurations (*.yaml) from the program's configuration directory.

        Args:
            config_path: Folder to list the files from

        Returns:
            list[path]: A list of path objects for each discovered entry

        """
        file_processing_service: FileProcessingService = self.file_processing

        return file_processing_service.discover_files_by_pattern(
            pattern="*.yaml",
            base_path=config_path,
        )

    def load_search_configurations(
        self,
        config_file: Path,
    ) -> list[SearchConfig]:
        """
        Load search configurations from a YAML file.

        Args:
            config_file: Path to the YAML configuration file

        Returns:
            List of SearchConfig objects ready for execution

        Raises:
            ValueError: If configuration file cannot be loaded or parsed
            FileNotFoundError: If configuration file doesn't exist

        """
        try:
            self.rich_output.info(f"Loading search configurations from: {config_file}")
            search_configs = self.search_config.load_search_configs(config_file)
            self.rich_output.success(
                f"Loaded {len(search_configs)} search configurations",
            )
        except Exception as e:
            self.rich_output.error(f"Failed to load search configurations: {e}")
            raise
        else:
            return search_configs

    def validate_search_configuration(
        self,
        config_file: Path,
    ) -> list[str]:
        """
        Validate a search configuration file.

        Args:
            config_file: Path to the configuration file to validate

        Returns:
            List of validation error messages, empty if valid

        """
        try:
            return self.search_config.validate_config_file(config_file)
        except (FileNotFoundError, ValueError, OSError) as e:
            return [f"Failed to validate configuration: {e}"]

    def generate_config_hierarchy_report(
        self,
        config_file: Path,
    ) -> dict[str, Any]:
        """
        Generate a hierarchical report of search configurations.

        Args:
            config_file: Path to the root configuration file

        Returns:
            Dictionary representing the hierarchical structure with statistics

        """
        return self.report_generator.generate_config_hierarchy_report(config_file)

    def filter_applicable_searches(
        self,
        search_configs: list[SearchConfig],
        systems: list[Systems],
    ) -> list[SearchConfig]:
        """
        Filter search configs to only include those applicable to available systems.

        This method filters out searches that would not apply to any of the available
        systems, ensuring that progress bars and statistics only reflect searches
        that can actually produce results.

        Args:
            search_configs: List of all search configurations
            systems: List of available systems

        Returns:
            List of search configurations that are applicable to at least one system

        """
        return self.search_engine.filter_applicable_searches(search_configs, systems)

    def execute_search(
        self,
        search_config: SearchConfig,
        systems: list[Systems],
    ) -> SearchResults:
        """
        Execute a single search configuration against systems.

        Args:
            search_config: Search configuration to execute
            systems: List of systems to search

        Returns:
            SearchResults containing all matches found

        """
        return self.search_engine.execute_search(search_config, systems)

    def execute_all_searches(
        self,
        search_configs: list[SearchConfig],
        systems: list[Systems],
    ) -> list[SearchResults]:
        """
        Execute all search configurations against systems.

        Args:
            search_configs: List of search configurations to execute
            systems: List of systems to search

        Returns:
            List of SearchResults for all executed searches

        """
        return self.search_engine.execute_all_searches(search_configs, systems)
