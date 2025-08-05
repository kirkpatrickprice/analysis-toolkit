"""
File-centric search engine implementation.

This module provides a more efficient search approach by reading each file once
and applying all applicable search configurations against each line, rather than
reading each file multiple times (once per search configuration).
"""

import re

from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig
from kp_analysis_toolkit.process_scripts.models.results.base import (
    SearchResult,
    SearchResults,
)
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.process_scripts.search_engine import (
    _filter_excel_illegal_chars,
    filter_systems_by_criteria,
    merge_result_fields,
    should_skip_line,
)
from kp_analysis_toolkit.utils.rich_output import get_rich_output


class MultilineState:
    """Manages state for multiline search configurations."""

    def __init__(self, search_config: SearchConfig) -> None:
        self.search_config = search_config
        self.current_record: dict[str, str] = {}
        self.matching_lines: str = ""
        self.start_line_num: int = 0
        self.has_partial_match = False

    def reset(self) -> None:
        """Reset the multiline state for a new record."""
        self.current_record = {}
        self.matching_lines = ""
        self.start_line_num = 0
        self.has_partial_match = False

    def is_record_complete(self) -> bool:
        """Check if all required fields have been collected."""
        if not self.search_config.field_list:
            return False

        # Record is complete when all fields have been found
        return all(
            field in self.current_record for field in self.search_config.field_list
        )

    def should_emit_record(self, line: str) -> bool:
        """Determine if the current record should be emitted."""
        # If we have a record delimiter, check if we've hit it
        if self.search_config.rs_delimiter:
            return bool(re.search(self.search_config.rs_delimiter, line))

        # If no delimiter is specified, emit when all fields are collected
        return self.is_record_complete()


class SearchState:
    """Manages state for a single search configuration against a single system."""

    def __init__(self, search_config: SearchConfig, system: Systems) -> None:
        self.search_config = search_config
        self.system = system
        self.results: list[SearchResult] = []
        self.is_complete = False  # max_results reached
        self.seen_matches: set[str] = set()  # for unique filtering
        self.multiline_state = (
            MultilineState(search_config) if search_config.multiline else None
        )

        # Compile regex pattern once
        try:
            self.pattern = re.compile(search_config.regex, re.IGNORECASE)
        except re.error as e:
            rich_output = get_rich_output()
            rich_output.error(f"Invalid regex pattern in {search_config.name}: {e}")
            self.pattern = None

    def add_result(self, result: SearchResult) -> None:
        """Add a result, handling unique filtering and max_results."""
        if self.is_complete:
            return

        # Handle unique filtering
        if self.search_config.unique:
            dedup_key = result.matched_text.strip().lower()
            if dedup_key in self.seen_matches:
                return
            self.seen_matches.add(dedup_key)

        self.results.append(result)

        # Check if we've reached max_results
        if (
            self.search_config.max_results > 0
            and len(self.results) >= self.search_config.max_results
        ):
            self.is_complete = True

    def process_line(self, line: str, line_num: int) -> None:
        """Process a single line against this search configuration."""
        if self.is_complete or not self.pattern:
            return

        # Skip lines that should be ignored
        if should_skip_line(line):
            return

        if self.search_config.multiline:
            self._process_multiline(line, line_num)
        else:
            self._process_single_line(line, line_num)

    def _process_single_line(self, line: str, line_num: int) -> None:
        """Process a single line for non-multiline searches."""
        match = self.pattern.search(line)
        if not match:
            return

        # Create result based on configuration
        if self.search_config.only_matching and self.search_config.field_list:
            # Extract fields from named groups
            extracted_fields = {}
            for field in self.search_config.field_list:
                try:
                    field_value = match.group(field)
                    # Filter illegal characters from extracted field values
                    extracted_fields[field] = (
                        _filter_excel_illegal_chars(field_value) if field_value else ""
                    )
                except (IndexError, KeyError):
                    extracted_fields[field] = ""

            # Apply field merging if configured
            if self.search_config.merge_fields:
                extracted_fields = merge_result_fields(
                    extracted_fields,
                    self.search_config.merge_fields,
                )

            # Filter illegal characters from matched text
            matched_text = (
                match.group(0) if self.search_config.only_matching else line.strip()
            )
            matched_text = _filter_excel_illegal_chars(matched_text)

            result = SearchResult(
                system_name=self.system.system_name,
                line_number=line_num,
                matched_text=matched_text,
                extracted_fields=extracted_fields,
            )
        else:
            # Standard match
            matched_text = (
                match.group(0) if self.search_config.only_matching else line.strip()
            )
            matched_text = _filter_excel_illegal_chars(matched_text)

            result = SearchResult(
                system_name=self.system.system_name,
                line_number=line_num,
                matched_text=matched_text,
                extracted_fields=None,
            )

        self.add_result(result)

    def _process_multiline(self, line: str, line_num: int) -> None:
        """Process a line for multiline searches."""
        if not self.multiline_state:
            return

        # Check if this line matches the pattern
        match = self.pattern.search(line)
        if match:
            # If this is the first match for a new record, set the start line
            if not self.multiline_state.has_partial_match:
                self.multiline_state.start_line_num = line_num
                self.multiline_state.has_partial_match = True

            # Add matching line to the collection
            if self.multiline_state.matching_lines:
                self.multiline_state.matching_lines += "\n"
            self.multiline_state.matching_lines += line.strip()

            # Update current record with matched fields
            match_dict = match.groupdict()
            for key, value in match_dict.items():
                if value is not None:
                    self.multiline_state.current_record[key] = value

        # Check if we should emit the current record
        if (
            self.multiline_state.has_partial_match
            and self.multiline_state.should_emit_record(line)
        ):
            self._emit_multiline_record()

    def _emit_multiline_record(self) -> None:
        """Emit a completed multiline record."""
        if not self.multiline_state or not self.multiline_state.current_record:
            return

        # Create extracted fields if field_list is specified
        extracted_fields = None
        if self.search_config.field_list:
            extracted_fields = {}
            for field in self.search_config.field_list:
                field_value = self.multiline_state.current_record.get(field, "")
                # Filter illegal characters from extracted field values
                extracted_fields[field] = (
                    _filter_excel_illegal_chars(field_value) if field_value else ""
                )

            # Apply field merging if configured
            if self.search_config.merge_fields:
                extracted_fields = merge_result_fields(
                    extracted_fields,
                    self.search_config.merge_fields,
                )

        # Filter illegal characters
        matched_text = _filter_excel_illegal_chars(self.multiline_state.matching_lines)

        result = SearchResult(
            system_name=self.system.system_name,
            line_number=self.multiline_state.start_line_num,
            matched_text=matched_text,
            extracted_fields=extracted_fields,
        )

        self.add_result(result)
        self.multiline_state.reset()

    def finalize(self) -> None:
        """Finalize processing for this search state."""
        # Emit any pending multiline record
        if (
            self.multiline_state
            and self.multiline_state.has_partial_match
            and self.multiline_state.current_record
        ):
            self._emit_multiline_record()


class FileCentricSearchEngine:
    """File-centric search engine that reads each file once and applies all searches."""

    def __init__(self, program_config: ProgramConfig) -> None:
        self.program_config = program_config
        self.rich_output = get_rich_output()

    def execute_searches(
        self,
        systems: list[Systems],
        search_configs: list[SearchConfig],
    ) -> list[SearchResults]:
        """
        Execute all search configurations against all systems using file-centric approach.

        Args:
            systems: List of systems to search
            search_configs: List of search configurations to apply

        Returns:
            List of SearchResults for all executed searches

        """
        # Initialize result collectors for each search config
        result_collectors: dict[str, list[SearchResult]] = {
            config.name: [] for config in search_configs
        }

        # Process each system file
        total_systems = len(systems)
        if self.program_config.verbose:
            self.rich_output.subheader("File-Centric Search Processing")
            for i, system in enumerate(systems, 1):
                self.rich_output.debug(
                    f"Processing system {i}/{total_systems}: {system.system_name}",
                )
                self._process_system_file(system, search_configs, result_collectors)
        else:
            # Use custom progress bar for non-verbose mode to show current filename
            with self.rich_output.progress(
                show_eta=True,
                show_percentage=True,
            ) as progress:
                task = progress.add_task("Processing systems", total=total_systems)

                for system in systems:
                    # Update progress bar with fixed-width filename field
                    try:
                        # Get relative path from source_files_path
                        relative_path = system.file.relative_to(
                            self.program_config.source_files_path,
                        )
                        filename_display = str(relative_path)
                    except ValueError:
                        # Fallback to system name if relative path fails
                        filename_display = system.system_name

                    # Use fixed-width field (40 chars) with right justification to show
                    # the most significant part of the filename
                    fixed_width_filename = filename_display[-40:].rjust(40)
                    current_desc = f"Processing: {fixed_width_filename}"

                    progress.update(task, description=current_desc)
                    self._process_system_file(system, search_configs, result_collectors)
                    progress.advance(task)

        # Convert results to SearchResults objects
        search_results = []
        for config in search_configs:
            config_results = result_collectors[config.name]

            # Handle show_missing feature
            if config.show_missing:
                config_results = self._add_missing_system_results(
                    config,
                    config_results,
                    systems,
                )

            results = SearchResults(
                search_config=config,
                results=config_results,
            )
            search_results.append(results)

        return search_results

    def _process_system_file(
        self,
        system: Systems,
        search_configs: list[SearchConfig],
        result_collectors: dict[str, list[SearchResult]],
    ) -> None:
        """Process a single system file against all applicable search configurations."""
        # Filter search configs that apply to this system
        applicable_configs = self._get_applicable_configs(system, search_configs)
        if not applicable_configs:
            return

        # Create search states for applicable configs
        search_states = [SearchState(config, system) for config in applicable_configs]

        try:
            self._process_file_lines(system, search_states)
            self._finalize_and_collect_results(search_states, result_collectors)

        except (OSError, UnicodeDecodeError, PermissionError) as e:
            self.rich_output.error(f"Error processing {system.file}: {e}")
            if self.program_config.verbose:
                import traceback

                traceback.print_exc()

    def _get_applicable_configs(
        self,
        system: Systems,
        search_configs: list[SearchConfig],
    ) -> list[SearchConfig]:
        """Get search configurations that apply to the given system."""
        applicable_configs = []
        for config in search_configs:
            filtered_systems = filter_systems_by_criteria([system], config.sys_filter)
            if filtered_systems:  # If system passes the filter
                applicable_configs.append(config)
        return applicable_configs

    def _process_file_lines(
        self,
        system: Systems,
        search_states: list[SearchState],
    ) -> None:
        """Process file lines with all search states."""
        # Determine encoding
        encoding = system.encoding or "utf-8"

        # Process file line by line
        with system.file.open("r", encoding=encoding, errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                # Apply each search state to this line
                for state in search_states:
                    if not state.is_complete:
                        state.process_line(line, line_num)

                # Early termination if all searches are complete and not full_scan
                if self._should_terminate_early(search_states):
                    break

    def _should_terminate_early(self, search_states: list[SearchState]) -> bool:
        """Check if processing should terminate early."""
        all_complete_or_full_scan = all(
            state.is_complete or state.search_config.full_scan
            for state in search_states
        )
        no_full_scan_required = not any(
            state.search_config.full_scan for state in search_states
        )
        return all_complete_or_full_scan and no_full_scan_required

    def _finalize_and_collect_results(
        self,
        search_states: list[SearchState],
        result_collectors: dict[str, list[SearchResult]],
    ) -> None:
        """Finalize search states and collect results."""
        # Finalize all search states (handles pending multiline records)
        for state in search_states:
            state.finalize()

        # Collect results
        for state in search_states:
            result_collectors[state.search_config.name].extend(state.results)

    def _add_missing_system_results(
        self,
        config: SearchConfig,
        existing_results: list[SearchResult],
        all_systems: list[Systems],
    ) -> list[SearchResult]:
        """
        Add 'NO RESULTS FOUND' entries for systems that don't have results when show_missing is enabled.

        Args:
            config: Search configuration
            existing_results: Results that were already found
            all_systems: All systems that were processed

        Returns:
            Combined list with existing results plus missing system entries

        """
        # Get systems that already have results
        systems_with_results = {result.system_name for result in existing_results}

        # Filter systems that apply to this search config (using same logic as _get_applicable_configs)
        applicable_systems = []
        for system in all_systems:
            if self._is_system_applicable(system, config):
                applicable_systems.append(system)

        # Create "NO RESULTS FOUND" entries for systems without results
        missing_results = []
        for system in applicable_systems:
            if system.system_name not in systems_with_results:
                # Create a SearchResult indicating no matches were found
                no_results_entry = SearchResult(
                    system_name=system.system_name,
                    line_number=1,  # Use line 1 as placeholder
                    matched_text="NO RESULTS FOUND",
                    extracted_fields=None,
                )
                missing_results.append(no_results_entry)

        # Combine existing results with missing entries
        # Sort by system name for consistent ordering
        combined_results = existing_results + missing_results
        combined_results.sort(key=lambda r: r.system_name)

        return combined_results

    def _is_system_applicable(self, system: Systems, config: SearchConfig) -> bool:
        """
        Check if a search configuration applies to a given system.

        Args:
            system: System to check
            config: Search configuration

        Returns:
            True if the search config should be applied to this system

        """
        # Use the same filtering logic as in _get_applicable_configs
        from kp_analysis_toolkit.process_scripts.search_engine import (
            filter_systems_by_criteria,
        )

        if config.sys_filter:
            filtered_systems = filter_systems_by_criteria([system], config.sys_filter)
            return len(filtered_systems) > 0

        return True


def execute_file_centric_search(
    search_configs: list[SearchConfig],
    systems: list[Systems],
    program_config: ProgramConfig,
) -> list[SearchResults]:
    """
    Execute searches using the file-centric approach.

    Args:
        search_configs: List of search configurations to execute
        systems: List of systems to search
        program_config: Program configuration

    Returns:
        List of SearchResults containing all matches found

    """
    engine = FileCentricSearchEngine(program_config)
    return engine.execute_searches(systems, search_configs)


def validate_file_centric_compatibility(
    search_configs: list[SearchConfig],
) -> list[str]:
    """
    Validate that search configurations are compatible with file-centric processing.

    Args:
        search_configs: List of search configurations to validate

    Returns:
        List of warning messages for any incompatible configurations

    """
    warnings = []

    for _config in search_configs:
        # All current features should be compatible with file-centric approach
        # This function is a placeholder for future compatibility checks
        pass

    return warnings
