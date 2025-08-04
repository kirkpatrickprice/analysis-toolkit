"""Protocol definitions for search engine services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    import re
    from typing import Any

    from kp_analysis_toolkit.process_scripts.models.results.search import (
        SearchResult,
        SearchResults,
    )
    from kp_analysis_toolkit.process_scripts.models.results.system import Systems
    from kp_analysis_toolkit.process_scripts.models.search.configs import SearchConfig
    from kp_analysis_toolkit.process_scripts.models.search.filters import SystemFilter


@runtime_checkable
class SystemFilterService(Protocol):
    """Protocol for filtering systems based on system filter criteria."""

    def filter_systems_by_criteria(
        self,
        systems: list[Systems],
        filters: list[SystemFilter] | None,
    ) -> list[Systems]:
        """Filter systems based on system filter criteria."""
        ...

    def evaluate_system_filters(
        self,
        system: Systems,
        filters: list[SystemFilter],
    ) -> bool:
        """Evaluate if a system matches all filter criteria."""
        ...


@runtime_checkable
class PatternCompiler(Protocol):
    """Protocol for compiling and managing regex patterns."""

    def compile_pattern(self, regex: str) -> re.Pattern[str]:
        """Compile a regex pattern with error handling."""
        ...


@runtime_checkable
class FieldExtractor(Protocol):
    """Protocol for extracting fields from search matches."""

    def extract_fields_from_match(
        self,
        match: re.Match[str],
        field_list: list[str] | None,
    ) -> dict[str, str | None | float]:
        """Extract named group fields from a regex match."""
        ...

    def merge_result_fields(
        self,
        extracted_fields: dict[str, Any],
        merge_fields_config: list[Any],
    ) -> dict[str, Any]:
        """Merge multiple source fields into destination fields."""
        ...


@runtime_checkable
class ResultProcessor(Protocol):
    """Protocol for processing and managing search results."""

    def create_search_result(
        self,
        search_config: SearchConfig,
        system: Systems,
        text: str,
        line_num: int,
        matching_dict: dict[str, str | Any],
    ) -> SearchResult:
        """Create a SearchResult object from search data."""
        ...

    def deduplicate_results(self, results: list[SearchResult]) -> list[SearchResult]:
        """Remove duplicate results based on unique criteria."""
        ...

    def should_skip_line(self, line: str) -> bool:
        """Check if a line should be skipped during processing."""
        ...

    def filter_excel_illegal_chars(self, text: str) -> str:
        """Filter out characters that are illegal in Excel."""
        ...


@runtime_checkable
class SearchEngineService(Protocol):
    """Protocol for the main search engine service orchestration."""

    def filter_applicable_searches(
        self,
        search_configs: list[SearchConfig],
        systems: list[Systems],
    ) -> list[SearchConfig]:
        """Filter search configs to only include those applicable to available systems."""
        ...

    def execute_search(
        self,
        search_config: SearchConfig,
        systems: list[Systems],
    ) -> SearchResults:
        """Execute a single search configuration against systems."""
        ...

    def execute_all_searches(
        self,
        search_configs: list[SearchConfig],
        systems: list[Systems],
    ) -> list[SearchResults]:
        """Execute all search configurations against systems."""
        ...

    def search_single_system(
        self,
        search_config: SearchConfig,
        system: Systems,
    ) -> list[SearchResult]:
        """Execute a search against a single system."""
        ...
