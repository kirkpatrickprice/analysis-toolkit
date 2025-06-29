"""
Search engine functionality for executing regex-based searches against system files.

Handles YAML configuration loading, system filtering, and search execution.
"""

import re
from enum import Enum
from pathlib import Path
from typing import IO, Any, LiteralString

import yaml

from kp_analysis_toolkit.process_scripts import GLOBALS
from kp_analysis_toolkit.process_scripts.models.enums import (
    OSFamilyType,
)
from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig
from kp_analysis_toolkit.process_scripts.models.results.base import (
    SearchResult,
    SearchResults,
)
from kp_analysis_toolkit.process_scripts.models.search.base import (
    MergeFieldConfig,
    SearchConfig,
)
from kp_analysis_toolkit.process_scripts.models.search.sys_filters import (
    SysFilterAttr,
    SysFilterComparisonOperators,
    SystemFilter,
)
from kp_analysis_toolkit.process_scripts.models.search.yaml import YamlConfig
from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.process_scripts.models.types import SysFilterValueType
from kp_analysis_toolkit.utils.rich_output import get_rich_output


def should_skip_line(line: str) -> bool:
    """
    Check if a line should be skipped based on predefined patterns.

    Lines are skipped if they contain:
    1. "###[BEGIN]"
    2. "###Processing Command:"
    3. "###Running:"
    4. "###[END]"
    5. Any comments noted by "###" (noted by three or more hashes)

    Args:
        line: The line to check

    Returns:
        True if the line should be skipped, False otherwise

    """
    # Check for specific patterns first
    specific_patterns = [
        "###[BEGIN]",
        "###Processing Command:",
        "###Running:",
        "###[END]",
    ]

    for pattern in specific_patterns:
        if pattern in line:
            return True

    # Check for general ### comments (three or more hashes)
    # This will match ###, ####, #####, etc. at the beginning of lines
    return bool(re.search(r"###", line.strip()))


def compare_version(
    system_version: str | None,
    comp: SysFilterComparisonOperators,
    filter_version: str,
) -> bool:
    """Compare version strings using component-wise comparison."""
    if not system_version:
        system_components = [0, 0, 0]
    else:
        system_components = [int(x) for x in system_version.split(".")]

    value_components = [int(x) for x in filter_version.split(".")]

    if comp == SysFilterComparisonOperators.EQUALS:
        return system_components == value_components
    if comp == SysFilterComparisonOperators.GREATER_EQUAL:
        return system_components >= value_components
    if comp == SysFilterComparisonOperators.GREATER_THAN:
        return system_components > value_components
    if comp == SysFilterComparisonOperators.LESS_EQUAL:
        return system_components <= value_components
    if comp == SysFilterComparisonOperators.LESS_THAN:
        return system_components < value_components
    return False


def convert_to_enum_if_needed(value: str | Enum, enum_class: Enum) -> Enum:
    """Convert string value to enum if needed."""
    if isinstance(value, str):
        try:
            return enum_class(value)
        except ValueError:
            return value
    return value


def evaluate_system_filters(system: Systems, filters: list[SystemFilter]) -> bool:
    """Evaluate system filters against a system."""
    # If no filters, return True
    if not filters:
        return True

    for filter_item in filters:
        # Check if attribute is applicable to this OS
        if not is_attribute_applicable(system, filter_item.attr):
            return False

        # Get system value for the attribute
        system_value = get_system_attribute_value(system, filter_item.attr)

        # For producer version, handle with special comparison
        if filter_item.attr == SysFilterAttr.PRODUCER_VERSION and isinstance(
            filter_item.value,
            str,
        ):
            version_operators = [
                SysFilterComparisonOperators.EQUALS,
                SysFilterComparisonOperators.GREATER_EQUAL,
                SysFilterComparisonOperators.GREATER_THAN,
                SysFilterComparisonOperators.LESS_EQUAL,
                SysFilterComparisonOperators.LESS_THAN,
            ]
            if filter_item.comp in version_operators:
                if not compare_version(
                    system.producer_version,
                    filter_item.comp,
                    filter_item.value,
                ):
                    return False
                continue

        # Standard comparison for all other cases
        if not compare_values(system_value, filter_item.comp, filter_item.value):
            return False

    # All filters passed
    return True


def is_attribute_applicable(system: Systems, attr: SysFilterAttr) -> bool:
    """
    Check if an attribute is applicable to the system's OS family.

    Args:
        system: System object containing OS family information
        attr: SysFilterAttr to check

    Returns:
        True if the attribute is applicable to the system's OS family, False otherwise

    """
    windows_only_attrs = [
        SysFilterAttr.PRODUCT_NAME,
        SysFilterAttr.RELEASE_ID,
        SysFilterAttr.CURRENT_BUILD,
        SysFilterAttr.UBR,
    ]

    linux_only_attrs = [
        SysFilterAttr.DISTRO_FAMILY,
        SysFilterAttr.OS_PRETTY_NAME,
    ]

    if system.os_family != OSFamilyType.WINDOWS and attr in windows_only_attrs:
        return False

    return not (system.os_family != OSFamilyType.LINUX and attr in linux_only_attrs)


def load_yaml_config(config_file: Path) -> YamlConfig:
    """
    Load and parse YAML configuration file into structured data models.

    Args:
        config_file: ConfigFile object of YAML configuration file

    Returns:
        YamlConfig object containing parsed configuration

    Raises:
        ValueError: If file cannot be loaded or parsed

    """
    try:
        with config_file.open("r") as f:
            yaml_data: dict = yaml.safe_load(f)

        if not yaml_data:
            message: str = f"Empty YAML file: {config_file}"
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
    all_configs: list[SearchConfig] = []

    # Add configs from current file
    for _search_config in yaml_config.search_configs.values():
        # Apply global search_config if it exists
        if yaml_config.global_config:
            search_config: SearchConfig = _search_config.merge_global_config(
                yaml_config.global_config,
            )
        else:
            # Use the search config as-is when no global config exists
            search_config = _search_config

        all_configs.append(search_config)

    # Process includes
    for _include_config in yaml_config.include_configs.values():
        for include_file in _include_config.files:
            include_path = base_path / include_file
            if include_path.exists():
                try:
                    included_yaml: YamlConfig = load_yaml_config(include_path)
                    included_configs: list[SearchConfig] = process_includes(
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
    yaml_config: YamlConfig = load_yaml_config(config_file)
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
            return getattr(system, "os_family", None)
        case SysFilterAttr.DISTRO_FAMILY:
            return getattr(system, "distro_family", None)
        case SysFilterAttr.PRODUCER:
            return getattr(system, "producer", None)
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
    if system_value is None or filter_value is None:
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
        system_results: list[SearchResult] = search_single_system(search_config, system)
        all_results.extend(system_results)
        # Note: max_results is already handled per-file within search_single_system

    # Apply unique filter if specified
    if search_config.unique:
        all_results: list[SearchResult] = deduplicate_results(all_results)

    return SearchResults(search_config=search_config, results=all_results)


def merge_result_fields(
    extracted_fields: dict[str, Any],
    merge_fields_config: list[MergeFieldConfig],
) -> dict[str, Any]:
    """
    Merge fields according to configuration.

    Args:
        extracted_fields: Dictionary of extracted fields
        merge_fields_config: List of MergeFieldConfig objects

    Returns:
        Updated dictionary with merged fields

    """
    if not merge_fields_config or not extracted_fields:
        return extracted_fields

    result: dict[str, Any] = extracted_fields.copy()
    columns_to_remove: set[str] = set()

    for merge_config in merge_fields_config:
        source_columns = merge_config.source_columns
        dest_column = merge_config.dest_column

        # Find the first non-empty value from source columns
        merged_value = None
        for col in source_columns:
            if extracted_fields.get(col):
                merged_value = extracted_fields[col]
                break

        # Add the merged column to the results
        if merged_value is not None:
            result[dest_column] = merged_value

        columns_to_remove.update(source_columns)

    # Remove all source columns after merging
    for column in columns_to_remove:
        result.pop(column, None)

    return result


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
        pattern: re.Pattern[str] = re.compile(search_config.regex, re.IGNORECASE)
    except re.error as e:
        rich_output = get_rich_output()
        rich_output.error(f"Invalid regex pattern in {search_config.name}: {e}")
        return results

    try:
        # Determine encoding
        encoding: str | LiteralString = system.encoding or "utf-8"

        with system.file.open("r", encoding=encoding, errors="replace") as f:
            if search_config.multiline:
                results: list[SearchResult] = search_multiline(
                    search_config,
                    system,
                    f,
                    pattern,
                )
            else:
                results = search_line_by_line(search_config, system, f, pattern)

    except (OSError, UnicodeDecodeError) as e:
        rich_output = get_rich_output()
        rich_output.error(f"Error processing {system.file}: {e}")

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
        line: str = _filter_excel_illegal_chars(_line.strip())

        # Skip lines that match predefined patterns
        if should_skip_line(line):
            continue

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


def _filter_excel_illegal_chars(text: str) -> str:
    """
    Remove characters that are illegal in Excel spreadsheets.

    Excel cannot handle control characters (ASCII 0-31) except for:
    - Tab (ASCII 9)
    - Line feed (ASCII 10)
    - Carriage return (ASCII 13)

    Args:
        text: String that may contain illegal Excel characters

    Returns:
        String with illegal characters removed

    """
    # Create a translation table that maps illegal characters to None
    illegal_chars: list[str] = [chr(i) for i in range(32) if i not in (9, 10, 13)]
    trans_table: dict[int, Any | None] = str.maketrans(dict.fromkeys(illegal_chars))

    # Apply the translation table to remove illegal characters
    return text.translate(trans_table)


def search_multiline(  # Ruff complains about complexity, but I couldn't find any other ways to simplify this function without losing functionality  # noqa: C901
    search_config: SearchConfig,
    system: Systems,
    file_handle: IO[str],
    pattern: re.Pattern,
) -> list[SearchResult]:
    """
    Search file using recordset delimiter for multi-line records.

    This function processes matches across multiple lines and combines them into
    single record entries. If rs_delimiter is provided, it separates records.
    If no delimiter is provided, records are considered complete when all fields
    in field_list have been populated.

    Args:
        search_config: Search configuration
        system: System being searched
        file_handle: IO[str] file handle to read from
        pattern: Compiled regex pattern to search for

    """
    results: list[SearchResult] = []
    current_record: dict[str, str] = {}
    start_line_num: int = 0
    matching_lines: str = ""

    # Define clear helper functions with single responsibilities
    def reset_record_state() -> None:
        """Reset the state for a new record."""
        nonlocal current_record, matching_lines, start_line_num
        current_record = {}
        matching_lines = ""
        start_line_num = 0

    def add_record() -> None:
        """Add the current record to results and reset state."""
        nonlocal current_record, matching_lines, start_line_num
        if not current_record:
            return

        result: SearchResult = create_search_result(
            search_config,
            system,
            matching_lines,
            start_line_num,
            current_record,
        )
        results.append(result)
        reset_record_state()

    def reached_max_results() -> bool:
        """Check if the maximum results limit has been reached."""
        return (
            search_config.max_results > 0 and len(results) >= search_config.max_results
        )

    # Process file content line by line
    file_content: str = file_handle.read()
    for line_num, _line in enumerate(file_content.split("\n"), 1):
        line: str = _filter_excel_illegal_chars(_line.strip())

        # Check if we reached the maximum results limit
        if reached_max_results():
            break

        # Skip lines that match predefined patterns
        if should_skip_line(line):
            continue

        # Skip empty lines
        if not line:
            continue

        # Handle record delimiter if configured
        if search_config.rs_delimiter and re.search(search_config.rs_delimiter, line):
            add_record()
            continue

        # Process matches in the current line
        matches: list[re.Match[str]] = list(pattern.finditer(line))
        if matches:
            # Add line to matching lines
            if matching_lines:
                matching_lines += "\n"
            matching_lines += line

            # Set start line number if this is the first match in the record
            if not start_line_num:
                start_line_num = line_num

            # Process all matches in the line
            for match in matches:
                # Add match fields to current record
                current_record.update(
                    {
                        field: value
                        for field, value in match.groupdict().items()
                        if value is not None
                    },
                )

        # Check if record is complete based on field list
        if (
            not search_config.rs_delimiter
            and search_config.field_list
            and all(field in current_record for field in search_config.field_list)
        ):
            add_record()

    # Add the final record if it exists
    add_record()  # add_record includes a check for empty records

    return results


def create_search_result(
    search_config: SearchConfig,
    system: Systems,
    text: str,
    line_num: int,
    matching_dict: dict[str, str | Any],
) -> SearchResult:
    """
    Create a SearchResult object from a regex match.

    Args:
        search_config: Search configuration
        system: System that was searched
        text: Full text that was matched against
        line_num: Line number where match occurred
        matching_dict: Regex match object OR match.groupdict() dictionary

    Returns:
        SearchResult object

    """
    # Extract fields if field_list is specified
    extracted_fields = None
    if search_config.field_list:
        if type(matching_dict) is re.Match:
            # If matching_dict is a Match object, convert to groupdict
            matching_dict = matching_dict.groupdict()
        extracted_fields: dict = {}
        for field in search_config.field_list:
            try:
                extracted_fields[field] = matching_dict.get(field)
            except IndexError:
                # Field not found in match groups, add as empty string
                extracted_fields[field] = ""

        # Apply field merging and remove merged fields if configured
        if search_config.merge_fields:
            extracted_fields = merge_result_fields(
                extracted_fields,
                search_config.merge_fields,
            )

    return SearchResult(
        system_name=system.system_name,
        line_number=line_num,
        matched_text=text.strip(),
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
        rich_output = get_rich_output()
        rich_output.info(f"Loaded {len(search_configs)} search configurations")

    # Execute searches
    all_results = []
    for search_config in search_configs:
        if program_config.verbose:
            rich_output = get_rich_output()
            rich_output.debug(f"Executing search: {search_config.name}")

        results = execute_search(search_config, systems)
        all_results.append(results)

        if program_config.verbose:
            rich_output = get_rich_output()
            rich_output.debug(
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

        # Check for multiline without field_list
        if search_config.multiline and not search_config.field_list:
            validation_messages.append(
                f"Search '{search_config.name}' has multiline=True but no field_list specified",
            )

        # Check for rs_delimiter without multiline
        if search_config.rs_delimiter and not search_config.multiline:
            validation_messages.append(
                f"Search '{search_config.name}' has rs_delimiter but multiline=False",
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
        from . import process_systems
        from .excel_exporter import export_search_results_to_excel

        rich_output = get_rich_output()
        rich_output.header("Processing Source Files")

        # Load systems
        systems = list(
            process_systems.enumerate_systems_from_source_files(program_config),
        )
        rich_output.info(f"Found {len(systems)} systems to process")

        if not systems:
            rich_output.warning(
                "No systems found to process. Check source files path and specification.",
            )
            return

        # Execute all searches
        all_results = execute_all_searches(program_config, systems)

        # Validate search configurations
        search_configs = load_search_configs(program_config.audit_config_file)
        validation_messages = validate_search_configs(search_configs)

        if validation_messages:
            rich_output.subheader("Validation Warnings")
            for message in validation_messages:
                rich_output.warning(f"  - {message}")

        # Export to Excel
        output_file = program_config.results_path / "search_results.xlsx"
        export_search_results_to_excel(all_results, output_file, systems)

        # Create summary report
        summary_file = program_config.results_path / "search_summary.txt"
        create_search_summary_report(all_results, summary_file)

        # Display summary
        stats = get_search_statistics(all_results)

        rich_output.subheader("Search Summary")
        rich_output.info(f"  Total searches executed: {stats['total_searches']}")
        rich_output.info(f"  Searches with results: {stats['searches_with_results']}")
        rich_output.info(f"  Total matches found: {stats['total_matches']}")
        rich_output.success(f"  Results exported to: {output_file}")
        rich_output.success(f"  Summary report: {summary_file}")

    except Exception as e:
        rich_output = get_rich_output()
        rich_output.error(f"Error during search processing: {e}")
        if program_config.verbose:
            import traceback

            traceback.print_exc()
        raise
