from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kp_analysis_toolkit.core.services.file_processing.service import (
    FileProcessingService,
)
from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.process_scripts.services.search_config.service import (
    SearchConfigService,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.protocols import (
    SearchEngineService,
)
from kp_analysis_toolkit.process_scripts.services.system_detection.service import (
    SystemDetectionService,
)

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.process_scripts.models.results.search import SearchResults
    from kp_analysis_toolkit.process_scripts.models.results.system import Systems
    from kp_analysis_toolkit.process_scripts.models.search.configs import (
        GlobalConfig,
        SearchConfig,
        YamlConfig,
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

# Type aliases for this module
type TreeNode = dict[str, str | list[Any]]
type StatsDict = dict[str, int | dict[str, int] | set[str]]


# AI-GEN: CopilotChat|2025-07-31|KPAT-ListSystems|reviewed:no
class ProcessScriptsService:
    """Main service for the process scripts module."""

    def __init__(
        self,
        system_detection: SystemDetectionService,
        file_processing: FileProcessingService,
        search_config: SearchConfigService,
        search_engine: SearchEngineService,
        rich_output: RichOutputService,
    ) -> None:
        self.system_detection: SystemDetectionService = system_detection
        self.file_processing: FileProcessingService = file_processing
        self.search_config: SearchConfigService = search_config
        self.search_engine: SearchEngineService = search_engine
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
        try:
            self.rich_output.debug(f"Generating hierarchy report for: {config_file}")

            # Initialize statistics collection
            search_stats: StatsDict = {
                "total_searches": 0,
                "searches_by_os_family": {},
                "files_processed": 0,
                "error_count": 0,
                "all_keywords": set(),
            }

            # Build the tree and collect statistics
            tree: TreeNode = self._build_config_tree(
                config_file,
                visited_files=set(),
                stats=search_stats,
            )

        except (FileNotFoundError, ValueError, OSError) as e:
            self.rich_output.error(f"Failed to generate config hierarchy: {e}")
            return {"error": str(e)}
        else:
            # Return both tree and statistics
            return {
                "tree": tree,
                "statistics": search_stats,
            }

    def _build_config_tree(
        self,
        config_file: Path,
        visited_files: set[Path],
        indent_level: int = 0,
        stats: StatsDict | None = None,
    ) -> TreeNode:
        """
        Recursively build the configuration tree structure.

        Args:
            config_file: Current configuration file to process
            visited_files: Set of already visited files to prevent infinite loops
            indent_level: Current indentation level for display
            stats: Dictionary to collect statistics (optional)

        Returns:
            Dictionary representing this file's configuration structure

        """
        if config_file in visited_files:
            error_msg = f"Circular include detected: {config_file}"
            if stats is not None:
                error_count = stats["error_count"]
                if isinstance(error_count, int):
                    stats["error_count"] = error_count + 1
            return {"error": error_msg}

        visited_files.add(config_file)

        try:
            # Load the YAML configuration directly
            yaml_config: YamlConfig = self.search_config.load_yaml_config(config_file)

            # Collect statistics if provided
            if stats is not None:
                files_processed = stats["files_processed"]
                if isinstance(files_processed, int):
                    stats["files_processed"] = files_processed + 1

            tree_node: TreeNode = {
                "file": config_file.name,
                "path": str(config_file),
                "children": [],
            }

            # Process different sections using helper methods
            self._process_global_config(yaml_config, tree_node)
            self._process_include_configs(
                yaml_config,
                tree_node,
                config_file,
                visited_files,
                indent_level,
                stats,
            )
            self._process_search_configs(yaml_config, tree_node, stats)

        except (FileNotFoundError, ValueError, OSError) as e:
            error_msg = f"Failed to process {config_file}: {e}"
            if stats is not None:
                error_count = stats["error_count"]
                if isinstance(error_count, int):
                    stats["error_count"] = error_count + 1
            return {"error": error_msg}
        else:
            return tree_node
        finally:
            visited_files.discard(config_file)

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

    def _extract_os_family(self, yaml_config: YamlConfig) -> str:
        """Extract OS family from global config for statistics."""
        if yaml_config.global_config and yaml_config.global_config.sys_filter:
            for filter_item in yaml_config.global_config.sys_filter:
                if filter_item.attr.value == "os_family":
                    return str(filter_item.value)
        return "unspecified"

    def _process_global_config(
        self,
        yaml_config: YamlConfig,
        tree_node: TreeNode,
    ) -> None:
        """Process global configuration and add to tree node."""
        if yaml_config.global_config:
            global_summary = self._format_global_config(yaml_config.global_config)
            children = tree_node["children"]
            if isinstance(children, list):
                children.append(
                    {
                        "type": "global",
                        "summary": global_summary,
                    },
                )

    def _process_include_configs(  # noqa: PLR0913
        self,
        yaml_config: YamlConfig,
        tree_node: TreeNode,
        config_file: Path,
        visited_files: set[Path],
        indent_level: int,
        stats: StatsDict | None,
    ) -> None:
        """Process include configurations and add to tree node."""
        for include_name, include_config in yaml_config.include_configs.items():
            include_node: TreeNode = {
                "type": "include",
                "name": include_name,
                "children": [],
            }

            # Process each file in the include
            for include_file in include_config.files:
                include_path: Path = self.search_config.file_resolver.resolve_path(
                    config_file.parent,
                    include_file,
                )
                if include_path.exists():
                    child_tree: TreeNode = self._build_config_tree(
                        include_path,
                        visited_files.copy(),
                        indent_level + 1,
                        stats,
                    )
                    children = include_node["children"]
                    if isinstance(children, list):
                        children.append(child_tree)
                else:
                    error_msg = f"File not found: {include_path}"
                    if stats is not None:
                        error_count = stats["error_count"]
                        if isinstance(error_count, int):
                            stats["error_count"] = error_count + 1
                    children = include_node["children"]
                    if isinstance(children, list):
                        children.append(
                            {
                                "error": error_msg,
                            },
                        )

            tree_children = tree_node["children"]
            if isinstance(tree_children, list):
                tree_children.append(include_node)

    def _process_search_configs(
        self,
        yaml_config: YamlConfig,
        tree_node: TreeNode,
        stats: StatsDict | None,
    ) -> None:
        """Process search configurations and add to tree node."""
        if not yaml_config.search_configs:
            return

        # Extract OS family for statistics
        os_family: str = self._extract_os_family(yaml_config)

        searches_node: TreeNode = {
            "type": "searches",
            "children": [],
        }

        # Count searches and categorize by OS family
        search_count: int = len(yaml_config.search_configs)
        if stats is not None:
            total_searches = stats["total_searches"]
            if isinstance(total_searches, int):
                stats["total_searches"] = total_searches + search_count

            searches_by_os = stats["searches_by_os_family"]
            if isinstance(searches_by_os, dict):
                if os_family not in searches_by_os:
                    searches_by_os[os_family] = 0
                current_count = searches_by_os[os_family]
                if isinstance(current_count, int):
                    searches_by_os[os_family] = current_count + search_count

        for search_name, search_config in yaml_config.search_configs.items():
            # Use excel_sheet_name if available, otherwise use the search name
            display_name: str = search_config.excel_sheet_name or search_name

            # Collect keywords if present
            if (
                stats is not None
                and hasattr(search_config, "keywords")
                and search_config.keywords
                and isinstance(search_config.keywords, list)
            ):
                all_keywords = stats["all_keywords"]
                if isinstance(all_keywords, set):
                    all_keywords.update(search_config.keywords)

            searches_children = searches_node["children"]
            if isinstance(searches_children, list):
                searches_children.append(
                    {
                        "type": "search",
                        "name": display_name,
                        "original_name": search_name,
                    },
                )

        tree_children = tree_node["children"]
        if isinstance(tree_children, list):
            tree_children.append(searches_node)

    def _format_global_config(self, global_config: GlobalConfig) -> str:
        """
        Format global configuration into a summary string.

        Args:
            global_config: GlobalConfig object to format

        Returns:
            Formatted summary string

        """
        parts: list[str] = []

        if global_config.sys_filter:
            for filter_item in global_config.sys_filter:
                filter_str: str = f"sys_filter {filter_item.attr.value} {filter_item.comp.value} {filter_item.value}"
                parts.append(filter_str)

        if global_config.max_results is not None:
            parts.append(f"max_results {global_config.max_results}")

        if global_config.only_matching is not None:
            parts.append(f"only_matching {global_config.only_matching}")

        if global_config.unique is not None:
            parts.append(f"unique {global_config.unique}")

        if global_config.full_scan is not None:
            parts.append(f"full_scan {global_config.full_scan}")

        return "global: " + ", ".join(parts) if parts else "global: (empty)"
