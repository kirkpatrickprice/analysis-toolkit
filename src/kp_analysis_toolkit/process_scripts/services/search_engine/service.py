"""Main search engine service implementation using dependency injection."""

from __future__ import annotations

from typing import IO, TYPE_CHECKING

from kp_analysis_toolkit.process_scripts.models.results.system import Systems
from kp_analysis_toolkit.process_scripts.services.search_engine.field_extractor import (
    DefaultFieldExtractor,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.pattern_compiler import (
    DefaultPatternCompiler,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.protocols import (
    SearchEngineService,
)
from kp_analysis_toolkit.process_scripts.services.search_engine.system_filter import (
    DefaultSystemFilterService,
)

if TYPE_CHECKING:
    import re

    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.process_scripts.models.results.search import (
        SearchResult,
        SearchResults,
    )
    from kp_analysis_toolkit.process_scripts.models.results.system import Systems
    from kp_analysis_toolkit.process_scripts.models.search.configs import SearchConfig
    from kp_analysis_toolkit.process_scripts.services.search_engine.field_extractor import (
        DefaultFieldExtractor,
    )
    from kp_analysis_toolkit.process_scripts.services.search_engine.pattern_compiler import (
        DefaultPatternCompiler,
    )
    from kp_analysis_toolkit.process_scripts.services.search_engine.result_processor import (
        DefaultResultProcessor,
    )
    from kp_analysis_toolkit.process_scripts.services.search_engine.system_filter import (
        DefaultSystemFilterService,
    )


class DefaultSearchEngineService(SearchEngineService):
    """Main service for search engine operations using DI services."""

    def __init__(  # noqa: PLR0913
        self,
        system_filter: DefaultSystemFilterService,
        pattern_compiler: DefaultPatternCompiler,
        field_extractor: DefaultFieldExtractor,
        result_processor: DefaultResultProcessor,
        file_processing: FileProcessingService,
        rich_output: RichOutputService,
    ) -> None:
        """
        Initialize the search engine service with injected dependencies.

        Args:
            system_filter: Service for filtering systems
            pattern_compiler: Service for compiling regex patterns
            field_extractor: Service for extracting fields from matches
            result_processor: Service for processing search results
            file_processing: Core file processing service
            rich_output: Core rich output service

        """
        self.system_filter: DefaultSystemFilterService = system_filter
        self.pattern_compiler: DefaultPatternCompiler = pattern_compiler
        self.field_extractor: DefaultFieldExtractor = field_extractor
        self.result_processor: DefaultResultProcessor = result_processor
        self.file_processing: FileProcessingService = file_processing
        self.rich_output: RichOutputService = rich_output

    def filter_applicable_searches(
        self,
        search_configs: list[SearchConfig],
        systems: list[Systems],
    ) -> list[SearchConfig]:
        """
        Filter search configs to only include those applicable to available systems.

        This implements the requirement to filter searches before progress bar statistics
        so that only searches that can actually find results are included in the count.

        Args:
            search_configs: List of all search configurations
            systems: List of available systems

        Returns:
            List of search configurations that are applicable to at least one system

        """
        if not search_configs or not systems:
            return []

        applicable_searches: list[SearchConfig] = []

        for search_config in search_configs:
            # Check if this search config applies to any of the available systems
            if search_config.sys_filter:
                filtered_systems: list[Systems] = (
                    self.system_filter.filter_systems_by_criteria(
                        systems,
                        search_config.sys_filter,
                    )
                )
            else:
                filtered_systems = systems

            # If the search applies to at least one system, include it
            if filtered_systems:
                applicable_searches.append(search_config)

        self.rich_output.debug(
            f"Filtered {len(search_configs)} searches down to {len(applicable_searches)} "
            f"applicable searches for {len(systems)} systems",
        )

        return applicable_searches

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
        # Filter systems based on sys_filter
        if search_config.sys_filter:
            filtered_systems: list[Systems] = (
                self.system_filter.filter_systems_by_criteria(
                    systems,
                    search_config.sys_filter,
                )
            )
        else:
            filtered_systems = systems

        all_results = []

        for system in filtered_systems:
            system_results: list[SearchResult] = self.search_single_system(
                search_config,
                system,
            )
            all_results.extend(system_results)

        # Apply unique filter if specified
        if search_config.unique:
            all_results = self.result_processor.deduplicate_results(all_results)

        # Import here to avoid circular imports
        from kp_analysis_toolkit.process_scripts.models.results.search import (
            SearchResults,
        )

        return SearchResults(search_config=search_config, results=all_results)

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
        all_search_results = []

        for search_config in search_configs:
            try:
                results = self.execute_search(search_config, systems)
                all_search_results.append(results)
            except (FileNotFoundError, ValueError, OSError) as e:
                self.rich_output.error(
                    f"Error executing search '{search_config.name}': {e}",
                )
                # Continue with other searches even if one fails

        return all_search_results

    def search_single_system(
        self,
        search_config: SearchConfig,
        system: Systems,
    ) -> list[SearchResult]:
        """
        Execute a search against a single system.

        Args:
            search_config: Search configuration to execute
            system: System to search

        Returns:
            List of SearchResult objects for this system

        """
        # Check if system file exists
        if not system.file.exists():
            self.rich_output.debug(f"System file not found: {system.file}")
            return []

        try:
            # Compile the regex pattern
            pattern = self.pattern_compiler.compile_pattern(search_config.regex)

            # Open and search the file
            with system.file.open("r", encoding="utf-8") as file_handle:
                if search_config.multiline:
                    return self._search_multiline(
                        search_config,
                        system,
                        file_handle,
                        pattern,
                    )

                return self._search_line_by_line(
                    search_config,
                    system,
                    file_handle,
                    pattern,
                )

        except (FileNotFoundError, ValueError, OSError) as e:
            self.rich_output.error(
                f"Error searching system '{system.system_name}': {e}",
            )
            return []

    def _search_line_by_line(
        self,
        search_config: SearchConfig,
        system: Systems,
        file_handle: IO[str],
        pattern: re.Pattern[str],
    ) -> list[SearchResult]:
        """
        Search file line by line for matches.

        Args:
            search_config: Search configuration
            system: System being searched
            file_handle: Open file handle
            pattern: Compiled regex pattern

        Returns:
            List of search results

        """
        results = []
        line_num = 0

        for line in file_handle:
            line_num += 1

            # Skip lines that should be ignored
            if self.result_processor.should_skip_line(line):
                continue

            # Search for pattern in line
            match = pattern.search(line)
            if match:
                # Extract fields from the match
                extracted_fields = self.field_extractor.extract_fields_from_match(
                    match,
                    search_config.field_list,
                )

                # Apply field merging if configured
                if search_config.merge_fields:
                    extracted_fields = self.field_extractor.merge_result_fields(
                        extracted_fields,
                        search_config.merge_fields,
                    )

                # Create search result
                result = self.result_processor.create_search_result(
                    search_config,
                    system,
                    line.strip(),
                    line_num,
                    extracted_fields,
                )
                results.append(result)

                # Check max_results limit
                if (
                    search_config.max_results > 0
                    and len(results) >= search_config.max_results
                ):
                    break

        return results

    def _search_multiline(
        self,
        search_config: SearchConfig,
        system: Systems,
        file_handle: IO[str],
        pattern: re.Pattern[str],
    ) -> list[SearchResult]:
        """
        Search file in multiline mode.

        Args:
            search_config: Search configuration
            system: System being searched
            file_handle: Open file handle
            pattern: Compiled regex pattern

        Returns:
            List of search results

        """
        results = []

        # Read entire file content for multiline search
        try:
            full_content = file_handle.read()
        except (OSError, UnicodeDecodeError) as e:
            self.rich_output.error(f"Error reading file content: {e}")
            return []

        # Split content by record separator if specified
        if search_config.rs_delimiter:
            content_sections = full_content.split(search_config.rs_delimiter)
        else:
            content_sections = [full_content]

        for section_idx, section in enumerate(content_sections):
            if not section.strip():
                continue

            # Search for pattern in section
            match = pattern.search(section)
            if match:
                # Extract fields from the match
                extracted_fields = self.field_extractor.extract_fields_from_match(
                    match,
                    search_config.field_list,
                )

                # Apply field merging if configured
                if search_config.merge_fields:
                    extracted_fields = self.field_extractor.merge_result_fields(
                        extracted_fields,
                        search_config.merge_fields,
                    )

                # For multiline, use section index as line number
                line_num = section_idx + 1

                # Create search result
                result = self.result_processor.create_search_result(
                    search_config,
                    system,
                    section.strip(),
                    line_num,
                    extracted_fields,
                )
                results.append(result)

                # Check max_results limit
                if (
                    search_config.max_results > 0
                    and len(results) >= search_config.max_results
                ):
                    break

        return results
