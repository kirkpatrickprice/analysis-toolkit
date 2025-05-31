"""
Search engine functionality for executing regex-based searches against system files.

Handles YAML configuration loading, system filtering, and search execution.
"""

import re
from pathlib import Path
from typing import IO, Any

import click
import yaml

from kp_analysis_toolkit.process_scripts import GLOBALS
from kp_analysis_toolkit.process_scripts.data_models import (
    ProgramConfig,
    SearchConfig,
    SearchResult,
    SearchResults,
    SysFilterAttr,
    SysFilterComparisonOperators,
    SysFilterValueType,
    SystemFilter,
    Systems,
    YamlConfig,
)


def load_yaml_config(config_file: Path) -> YamlConfig:
    """
    Load and parse YAML configuration file into structured data models.

    Args:
        config_file: Path to the YAML configuration file

    Returns:
        YamlConfig object containing parsed configuration

    Raises:
        ValueError: If file cannot be loaded or parsed

    """
    try:
        with config_file.open("r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        if not yaml_data:
            message = f"Empty YAML file: {config_file}"
            raise ValueError(message)  # noqa: TRY301

        return YamlConfig.from_dict(yaml_data)

    except yaml.YAMLError as e:
        message = f"Invalid YAML syntax in {config_file}: {e}"
        raise ValueError(message) from e
    except Exception as e:
        message = f"Error loading {config_file}: {e}"
        raise ValueError(message) from e


def process_includes(yaml_config: YamlConfig, base_path: Path) -> list[SearchConfig]:
    """
    Process include configurations and recursively load included files.

    Args:
        yaml_config: The main YAML configuration
        base_path: Base directory for resolving include paths

    Returns:
        List of all search configurations including those from included files

    """
    all_configs: list[YamlConfig] = []

    # Add configs from current file
    for _search_config in yaml_config.search_configs.values():
        # Apply global search_config if it exists
        if yaml_config.global_config:
            search_config: SearchConfig = _search_config.merge_global_config(
                yaml_config.global_config,
            )
        all_configs.append(search_config)

    # Process includes
    for _include_config in yaml_config.include_configs.values():
        for include_file in _include_config.files:
            include_path = base_path / include_file
            if include_path.exists():
                try:
                    included_yaml = load_yaml_config(include_path)
                    included_configs = process_includes(
                        included_yaml,
                        include_path.parent,
                    )
                    all_configs.extend(included_configs)
                except Exception as e:
                    message = f"Error loading include file {include_path}: {e}"
                    raise ValueError(message) from e
            else:
                message = f"Include file not found: {include_path}"
                raise FileNotFoundError(message)
    return all_configs


def load_search_configs(config_file: Path) -> list[SearchConfig]:
    """
    Load and parse search configurations from YAML file, handling includes.

    Args:
        config_file: Path to the main YAML configuration file

    Returns:
        List of SearchConfig objects ready for execution

    """
    yaml_config = load_yaml_config(config_file)
    return process_includes(yaml_config, config_file.parent)


def filter_systems_by_criteria(
    systems: list[Systems],
    filters: list[SystemFilter] | None,
) -> list[Systems]:
    """
    Filter systems based on system filter criteria.

    Args:
        systems: List of systems to filter
        filters: List of system filters to apply

    Returns:
        Filtered list of systems that match all criteria

    """
    if not filters:
        return systems

    filtered = []
    for system in systems:
        if system_matches_all_filters(system, filters):
            filtered.append(system)

    return filtered


def system_matches_all_filters(system: Systems, filters: list[SystemFilter]) -> bool:
    """
    Check if a system matches all filter criteria.

    Args:
        system: System to check
        filters: List of filters that must all match

    Returns:
        True if system matches all filters, False otherwise

    """
    for filter_config in filters:
        system_value = get_system_attribute_value(system, filter_config.attr)
        if not compare_values(system_value, filter_config.comp, filter_config.value):
            return False
    return True


def get_system_attribute_value(
    system: Systems,
    attr: SysFilterAttr,
) -> SysFilterValueType:
    """
    Get the appropriate system attribute value for filtering.

    Args:
        system: System object to extract attribute from
        attr: Attribute to extract

    Returns:
        Value of the specified attribute

    """
    match attr:
        case SysFilterAttr.OS_FAMILY:
            return system.os_family_computed
        case SysFilterAttr.DISTRO_FAMILY:
            return system.distro_family_computed
        case SysFilterAttr.PRODUCER:
            return system.producer_computed
        case _:
            # Use the enum value as the attribute name
            return getattr(system, attr.value, None)


def compare_values(  # noqa: PLR0911
    system_value: str | float,
    operator: SysFilterComparisonOperators,
    filter_value: SysFilterValueType,
) -> bool:
    """
    Compare system attribute value against filter value using specified operator.

    Args:
        system_value: Value from the system
        operator: Comparison operator to use
        filter_value: Value to compare against

    Returns:
        True if comparison matches, False otherwise

    """
    if system_value is None:
        return False

    try:
        match operator:
            case SysFilterComparisonOperators.EQUALS:
                return str(system_value).lower() == str(filter_value).lower()

            case SysFilterComparisonOperators.GREATER_THAN:
                return _numeric_or_string_comparison(
                    system_value,
                    filter_value,
                    lambda x, y: x > y,
                )

            case SysFilterComparisonOperators.LESS_THAN:
                return _numeric_or_string_comparison(
                    system_value,
                    filter_value,
                    lambda x, y: x < y,
                )

            case SysFilterComparisonOperators.GREATER_EQUAL:
                return _numeric_or_string_comparison(
                    system_value,
                    filter_value,
                    lambda x, y: x >= y,
                )

            case SysFilterComparisonOperators.LESS_EQUAL:
                return _numeric_or_string_comparison(
                    system_value,
                    filter_value,
                    lambda x, y: x <= y,
                )

            case SysFilterComparisonOperators.IN:
                # Convert filter_value to list if it isn't already
                if not isinstance(filter_value, list):
                    filter_value = [filter_value]

                # Case-insensitive membership test
                system_str = str(system_value).lower()
                filter_list = [str(item).lower() for item in filter_value]
                return system_str in filter_list

            case _:
                return False

    except Exception:  # noqa: BLE001
        # If any comparison fails, return False
        return False


def _numeric_or_string_comparison(
    system_value: str | float,
    filter_value: SysFilterValueType,
    comparison_func: callable,
) -> bool:
    """
    Try numeric comparison first, fall back to string comparison.

    Args:
        system_value: Value from system
        filter_value: Value to compare against
        comparison_func: Function to perform comparison

    Returns:
        Result of comparison

    """
    try:
        return comparison_func(float(system_value), float(filter_value))
    except (ValueError, TypeError):
        return comparison_func(str(system_value), str(filter_value))


def execute_search(
    search_config: SearchConfig,
    systems: list[Systems],
) -> SearchResults:
    """
    Execute a search configuration against available systems.

    Args:
        search_config: Search configuration to execute
        systems: List of systems to search

    Returns:
        SearchResults containing all matches found

    """
    # Filter systems based on sys_filter
    filtered_systems = filter_systems_by_criteria(systems, search_config.sys_filter)

    all_results = []

    for system in filtered_systems:
        system_results = search_single_system(search_config, system)
        all_results.extend(system_results)

        # Apply max_results limit if specified (per system)
        if (
            search_config.max_results > 0
            and len(system_results) >= search_config.max_results
        ):
            # Truncate this system's results if needed
            system_results = system_results[: search_config.max_results]

    # Apply unique filter if specified
    if search_config.unique:
        all_results = deduplicate_results(all_results)

    # Apply global max_results if specified
    if search_config.max_results > 0:
        all_results = all_results[: search_config.max_results]

    return SearchResults(search_config=search_config, results=all_results)


def search_single_system(
    search_config: SearchConfig,
    system: Systems,
) -> list[SearchResult]:
    """
    Search a single system file for matches.

    Args:
        search_config: Search configuration
        system: System to search

    Returns:
        List of search results for this system

    """
    results = []

    try:
        pattern = re.compile(search_config.regex, re.IGNORECASE)
    except re.error as e:
        click.echo(f"Error: Invalid regex pattern in {search_config.name}: {e}")
        return results

    try:
        # Determine encoding
        encoding = system.file_encoding or "utf-8"

        with system.file.open("r", encoding=encoding, errors="replace") as f:
            if search_config.combine and search_config.rs_delimiter:
                results = search_with_recordset_delimiter(
                    search_config,
                    system,
                    f,
                    pattern,
                )
            else:
                results = search_line_by_line(search_config, system, f, pattern)

    except (OSError, UnicodeDecodeError) as e:
        click.echo(f"Error processing {system.file}: {e}")

    return results


def search_line_by_line(
    search_config: SearchConfig,
    system: Systems,
    file_handle: IO[str],
    pattern: re.Pattern,
) -> list[SearchResult]:
    """
    Search file line by line for matches.

    Args:
        search_config: Search configuration
        system: System being searched
        file_handle: IO[str]
        pattern: Compiled regex pattern

    Returns:
        List of search results

    """
    results = []

    for line_num, _line in enumerate(file_handle, 1):
        line: str = _line.strip()

        # Skip empty lines unless full_scan is enabled
        if not line and not search_config.full_scan:
            continue

        match: re.Match[str] | None = pattern.search(line)
        if match:
            result: SearchResult = create_search_result(
                search_config,
                system,
                line,
                line_num,
                match,
            )
            results.append(result)

            # Check max_results per system
            if (
                search_config.max_results > 0
                and len(results) >= search_config.max_results
            ):
                break

    return results


def search_with_recordset_delimiter(
    search_config: SearchConfig,
    system: Systems,
    file_handle: IO[str],
    pattern: re.Pattern,
) -> list[SearchResult]:
    """
    Search file using recordset delimiter for multi-line records.

    Args:
        search_config: Search configuration with recordset delimiter
        system: System being searched
        file_handle: Open file handle
        pattern: Compiled regex pattern for matching

    Returns:
        List of search results from combined records

    """
    results = []

    try:
        rs_pattern = re.compile(search_config.rs_delimiter, re.IGNORECASE)
    except re.error as e:
        click.echo(
            f"Error: Invalid recordset delimiter pattern in {search_config.name}: {e}",
        )
        return results

    current_record = []
    record_start_line = 1

    for _line_num, _line in enumerate(file_handle, 1):
        line = _line.strip()

        # Check if this line starts a new record
        if rs_pattern.search(line):
            # Process the previous record if it exists
            if current_record and search_config.combine:
                combined_text = "\n".join(current_record)
                match: re.Match[str] | None = pattern.search(combined_text)
                if match:
                    result: SearchResult = create_search_result(
                        search_config,
                        system,
                        combined_text,
                        record_start_line,
                        match,
                    )
                    results.append(result)

            # Start new record
            current_record = [line]
            record_start_line = _line_num
        else:
            current_record.append(line)

        # Check max_results per system
        if search_config.max_results > 0 and len(results) >= search_config.max_results:
            break

    # Process the last record
    if current_record and search_config.combine:
        combined_text = "\n".join(current_record)
        match = pattern.search(combined_text)
        if match:
            result = create_search_result(
                search_config,
                system,
                combined_text,
                record_start_line,
                match,
            )
            results.append(result)

    return results


def create_search_result(
    search_config: SearchConfig,
    system: Systems,
    text: str,
    line_num: int,
    match: re.Match,
) -> SearchResult:
    """
    Create a SearchResult object from a regex match.

    Args:
        search_config: Search configuration
        system: System that was searched
        text: Full text that was matched against
        line_num: Line number where match occurred
        match: Regex match object

    Returns:
        SearchResult object

    """
    # Extract fields if field_list is specified
    extracted_fields = None
    if search_config.field_list:
        extracted_fields = {}
        for field in search_config.field_list:
            try:
                extracted_fields[field] = match.group(field)
            except IndexError:  # noqa: PERF203
                # Field not found in match groups, add as empty string
                extracted_fields[field] = ""

        # If no named groups were found, add raw_data field
        if not any(extracted_fields.values()):
            extracted_fields["raw_data"] = match.group(0)

    # Use only matching text if specified
    matched_text = match.group(0) if search_config.only_matching else text

    return SearchResult(
        system_name=system.system_name,
        line_number=line_num,
        matched_text=matched_text,
        extracted_fields=extracted_fields,
    )


def deduplicate_results(results: list[SearchResult]) -> list[SearchResult]:
    """
    Remove duplicate results based on matched_text.

    Args:
        results: List of search results that may contain duplicates

    Returns:
        List of unique search results

    """
    seen = set()
    unique_results = []

    for result in results:
        # Create a key for deduplication based on matched text
        dedup_key = result.matched_text.strip().lower()

        if dedup_key not in seen:
            seen.add(dedup_key)
            unique_results.append(result)

    return unique_results


def execute_all_searches(
    program_config: ProgramConfig,
    systems: list[Systems],
) -> list[SearchResults]:
    """
    Execute all search configurations against all systems.

    Args:
        program_config: Program configuration containing search settings
        systems: List of systems to search

    Returns:
        List of SearchResults for all executed searches

    Raises:
        ValueError: If no audit search_config file is specified

    """
    if not program_config.audit_config_file:
        message = "No audit search_config file specified in program configuration"
        raise ValueError(message)

    # Load search configurations
    search_configs: list[SearchConfig] = load_search_configs(
        program_config.audit_config_file,
    )

    if program_config.verbose:
        click.echo(f"Loaded {len(search_configs)} search configurations")

    # Execute searches
    all_results = []
    for search_config in search_configs:
        if program_config.verbose:
            click.echo(f"Executing search: {search_config.name}")

        results = execute_search(search_config, systems)
        all_results.append(results)

        if program_config.verbose:
            click.echo(
                f"  Found {results.result_count} matches across {results.unique_systems} systems",
            )

    return all_results


def get_search_statistics(search_results: list[SearchResults]) -> dict[str, Any]:
    """
    Generate statistics about search execution.

    Args:
        search_results: List of search results to analyze

    Returns:
        Dictionary containing search statistics

    """
    total_searches = len(search_results)
    total_matches = sum(result.result_count for result in search_results)
    searches_with_results = sum(
        1 for result in search_results if result.result_count > 0
    )

    # System coverage analysis
    all_systems = set()
    systems_with_matches = set()

    for search_result in search_results:
        for result in search_result.results:
            all_systems.add(result.system_name)
            systems_with_matches.add(result.system_name)

    # Search type analysis
    searches_with_extracted_fields = sum(
        1 for result in search_results if result.has_extracted_fields
    )

    # Top searches by result count
    top_searches = sorted(
        [(result.search_config.name, result.result_count) for result in search_results],
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    return {
        "total_searches": total_searches,
        "searches_with_results": searches_with_results,
        "searches_without_results": total_searches - searches_with_results,
        "total_matches": total_matches,
        "average_matches_per_search": total_matches / total_searches
        if total_searches > 0
        else 0,
        "unique_systems_found": len(all_systems),
        "systems_with_matches": len(systems_with_matches),
        "searches_with_extracted_fields": searches_with_extracted_fields,
        "top_searches_by_results": top_searches,
    }


def validate_search_configs(search_configs: list[SearchConfig]) -> list[str]:
    """
    Validate search configurations and return list of warnings/errors.

    Args:
        search_configs: List of search configurations to validate

    Returns:
        List of validation messages (warnings and errors)

    """
    validation_messages = []

    # Check for duplicate search names
    names = [search_config.name for search_config in search_configs]
    duplicates: set[str] = {name for name in names if names.count(name) > 1}

    if duplicates:
        validation_messages.append(
            f"Duplicate search names found: {', '.join(duplicates)}",
        )

    # Validate regex patterns
    for search_config in search_configs:
        try:
            re.compile(search_config.regex)
        except re.error as e:
            validation_messages.append(f"Invalid regex in '{search_config.name}': {e}")

        # Check for field_list without only_matching
        if search_config.field_list and not search_config.only_matching:
            validation_messages.append(
                f"Search '{search_config.name}' has field_list but only_matching is False",
            )

        # Check for combine without field_list
        if search_config.combine and not search_config.field_list:
            validation_messages.append(
                f"Search '{search_config.name}' has combine=True but no field_list specified",
            )

        # Check for rs_delimiter without combine
        if search_config.rs_delimiter and not search_config.combine:
            validation_messages.append(
                f"Search '{search_config.name}' has rs_delimiter but combine=False",
            )

    return validation_messages


def create_search_summary_report(
    search_results: list[SearchResults],
    output_path: Path,
) -> None:
    """
    Create a text summary report of search execution.

    Args:
        search_results: List of search results
        output_path: Path where to save the summary report

    """
    stats = get_search_statistics(search_results)

    with output_path.open("w", encoding="utf-8") as f:
        f.write("SEARCH EXECUTION SUMMARY REPORT\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"Total Searches Executed: {stats['total_searches']}\n")
        f.write(f"Searches with Results: {stats['searches_with_results']}\n")
        f.write(f"Searches without Results: {stats['searches_without_results']}\n")
        f.write(f"Total Matches Found: {stats['total_matches']}\n")
        f.write(
            f"Average Matches per Search: {stats['average_matches_per_search']:.2f}\n",
        )
        f.write(f"Unique Systems Processed: {stats['unique_systems_found']}\n")
        f.write(f"Systems with Matches: {stats['systems_with_matches']}\n")
        f.write(
            f"Searches with Extracted Fields: {stats['searches_with_extracted_fields']}\n\n",
        )

        f.write("TOP SEARCHES BY RESULT COUNT:\n")
        f.write("-" * 30 + "\n")
        for search_name, count in stats["top_searches_by_results"]:
            f.write(f"{search_name}: {count} matches\n")

        f.write("\n\nDETAILED SEARCH RESULTS:\n")
        f.write("-" * 30 + "\n")
        for search_result in search_results:
            f.write(f"\nSearch: {search_result.search_config.name}\n")
            f.write(f"  Results: {search_result.result_count}\n")
            f.write(f"  Unique Systems: {search_result.unique_systems}\n")
            f.write(f"  Has Extracted Fields: {search_result.has_extracted_fields}\n")
            if search_result.search_config.comment:
                max_results = GLOBALS.get("MAX_SUMMARY_REPORT_RESULTS", 100)
                f.write(
                    f"  Comment: {search_result.search_config.comment[:max_results]}{'...' if len(search_result.search_config.comment) > max_results else ''}\n",
                )


def process_search_workflow(program_config: ProgramConfig) -> None:
    """
    Main workflow function to process searches and export results.

    Args:
        program_config: Program configuration object

    Raises:
        Exception: If search processing fails

    """
    try:
        # Import here to avoid circular dependencies
        from . import process_scripts
        from .excel_exporter import export_search_results_to_excel

        click.echo("Processing source files...")

        # Load systems
        systems = list(
            process_scripts.enumerate_systems_from_source_files(program_config),
        )
        click.echo(f"Found {len(systems)} systems to process")

        if not systems:
            click.echo(
                "No systems found to process. Check source files path and specification.",
            )
            return

        # Execute all searches
        all_results = execute_all_searches(program_config, systems)

        # Validate search configurations
        search_configs = load_search_configs(program_config.audit_config_file)
        validation_messages = validate_search_configs(search_configs)

        if validation_messages:
            click.echo("\nValidation Warnings:")
            for message in validation_messages:
                click.echo(f"  - {message}")

        # Export to Excel
        output_file = program_config.results_path / "search_results.xlsx"
        export_search_results_to_excel(all_results, output_file)

        # Create summary report
        summary_file = program_config.results_path / "search_summary.txt"
        create_search_summary_report(all_results, summary_file)

        # Display summary
        stats = get_search_statistics(all_results)

        click.echo("\nSearch Summary:")
        click.echo(f"  Total searches executed: {stats['total_searches']}")
        click.echo(f"  Searches with results: {stats['searches_with_results']}")
        click.echo(f"  Total matches found: {stats['total_matches']}")
        click.echo(f"  Results exported to: {output_file}")
        click.echo(f"  Summary report: {summary_file}")

    except Exception as e:
        click.echo(f"Error during search processing: {e}")
        if program_config.verbose:
            import traceback

            traceback.print_exc()
        raise
