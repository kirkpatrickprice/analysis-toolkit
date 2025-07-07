from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from kp_analysis_toolkit.core.services.parallel_processing import (
    ParallelProcessingService,
)
from kp_analysis_toolkit.utils.rich_output import RichOutput

if TYPE_CHECKING:
    import re
    from pathlib import Path

    from kp_analysis_toolkit.core.services.parallel_processing import (
        ParallelProcessingService,
    )
    from kp_analysis_toolkit.process_scripts.models.results.base import SearchResults
    from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
    from kp_analysis_toolkit.process_scripts.models.systems import Systems
    from kp_analysis_toolkit.utils.rich_output import RichOutput


class PatternCompiler(Protocol):
    """Protocol for regex pattern compilation."""

    def compile_pattern(self, pattern: str) -> re.Pattern[str]: ...
    def validate_pattern(self, pattern: str) -> bool: ...


class FieldExtractor(Protocol):
    """Protocol for field extraction from search results."""

    def extract_fields(self, line: str, config: SearchConfig) -> dict[str, str]: ...


class ResultProcessor(Protocol):
    """Protocol for processing search results."""

    def process_results(
        self,
        raw_results: list[dict[str, str]],
        config: SearchConfig,
    ) -> SearchResults: ...


class SearchEngineService:
    """Service for search engine operations."""

    def __init__(
        self,
        pattern_compiler: PatternCompiler,
        field_extractor: FieldExtractor,
        result_processor: ResultProcessor,
        parallel_processing: ParallelProcessingService,
        rich_output: RichOutput,
    ) -> None:
        self.pattern_compiler: PatternCompiler = pattern_compiler
        self.field_extractor: FieldExtractor = field_extractor
        self.result_processor: ResultProcessor = result_processor
        self.parallel_processing: ParallelProcessingService = parallel_processing
        self.rich_output: RichOutput = rich_output

    def search_file(
        self,
        file_path: Path,
        search_config: SearchConfig,
    ) -> SearchResults:
        """Search a file using the provided configuration."""
        # Implementation would handle file searching with pattern matching
        # and field extraction using injected dependencies

    def search_configs_in_parallel(
        self,
        search_configs: list[SearchConfig],
        systems: list[Systems],
        max_workers: int,
    ) -> list[SearchResults]:
        """Execute multiple search configurations in parallel using processes."""
        if not search_configs:
            return []

        # Engine now uses injected RichOutput instead of global singleton
        # Calculate the maximum width needed for search config names
        max_name_width = max(
            len(getattr(config, "name", "Unknown")) for config in search_configs
        )

        results: list[SearchResults] = []

        # Set up interrupt handling with injected RichOutput
        self.interrupt_handler.setup()

        try:
            with self.rich_output.progress(
                show_eta=True,
                show_percentage=True,
                show_time_elapsed=True,
            ) as progress:
                # Implementation details for parallel processing...
                pass

        finally:
            self.interrupt_handler.cleanup()

        return results
