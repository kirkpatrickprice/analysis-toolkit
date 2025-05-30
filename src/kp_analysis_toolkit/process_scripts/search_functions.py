import re
from pathlib import Path
from typing import Any

import click
import pandas as pd
import yaml
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.table import Table, TableStyleInfo

from .data_models import (
    ProgramConfig,
    SearchConfig,
    SearchResult,
    SearchResults,
    SysFilterAttr,
    SysFilterComp,
    SystemFilter,
    Systems,
    YamlConfig,
)


def load_yaml_config(config_file: Path) -> YamlConfig:
    """Load and parse YAML configuration file into structured data models."""
    try:
        with config_file.open("r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        if not yaml_data:
            raise ValueError(f"Empty YAML file: {config_file}")

        return YamlConfig.from_dict(yaml_data)

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML syntax in {config_file}: {e}")
    except Exception as e:
        raise ValueError(f"Error loading {config_file}: {e}")


def process_includes(yaml_config: YamlConfig, base_path: Path) -> list[SearchConfig]:
    """Process include configurations and recursively load included files."""
    all_configs = []

    # Add configs from current file
    for config in yaml_config.search_configs.values():
        # Apply global config if it exists
        if yaml_config.global_config:
            config = config.merge_global_config(yaml_config.global_config)
        all_configs.append(config)

    # Process includes
    for include_name, include_config in yaml_config.include_configs.items():
        for include_file in include_config.files:
            include_path = base_path / include_file
            if include_path.exists():
                try:
                    included_yaml = load_yaml_config(include_path)
                    included_configs = process_includes(
                        included_yaml, include_path.parent
                    )
                    all_configs.extend(included_configs)
                except Exception as e:
                    click.echo(
                        f"Warning: Failed to load include file {include_path}: {e}"
                    )
            else:
                click.echo(f"Warning: Include file not found: {include_path}")

    return all_configs


def load_search_configs(config_file: Path) -> list[SearchConfig]:
    """Load and parse search configurations from YAML file, handling includes."""
    yaml_config = load_yaml_config(config_file)
    return process_includes(yaml_config, config_file.parent)


def filter_systems_by_criteria(
    systems: list[Systems], filters: list[SystemFilter] | None
) -> list[Systems]:
    """Filter systems based on system filter criteria."""
    if not filters:
        return systems

    filtered = []
    for system in systems:
        if system_matches_all_filters(system, filters):
            filtered.append(system)

    return filtered


def system_matches_all_filters(system: Systems, filters: list[SystemFilter]) -> bool:
    """Check if a system matches all filter criteria."""
    for filter_config in filters:
        system_value = get_system_attribute_value(system, filter_config.attr)
        if not compare_values(system_value, filter_config.comp, filter_config.value):
            return False
    return True


def get_system_attribute_value(system: Systems, attr: SysFilterAttr) -> Any:
    """Get the appropriate system attribute value for filtering."""
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


def compare_values(
    system_value: Any, operator: SysFilterComp, filter_value: Any
) -> bool:
    """Compare system attribute value against filter value using specified operator."""
    if system_value is None:
        return False

    try:
        match operator:
            case SysFilterComp.EQUALS:
                return str(system_value).lower() == str(filter_value).lower()

            case SysFilterComp.GREATER_THAN:
                return _numeric_or_string_comparison(
                    system_value, filter_value, lambda x, y: x > y
                )

            case SysFilterComp.LESS_THAN:
                return _numeric_or_string_comparison(
                    system_value, filter_value, lambda x, y: x < y
                )

            case SysFilterComp.GREATER_EQUAL:
                return _numeric_or_string_comparison(
                    system_value, filter_value, lambda x, y: x >= y
                )

            case SysFilterComp.LESS_EQUAL:
                return _numeric_or_string_comparison(
                    system_value, filter_value, lambda x, y: x <= y
                )

            case SysFilterComp.IN:
                # Convert filter_value to list if it isn't already
                if not isinstance(filter_value, list):
                    filter_value = [filter_value]

                # Case-insensitive membership test
                system_str = str(system_value).lower()
                filter_list = [str(item).lower() for item in filter_value]
                return system_str in filter_list

            case _:
                return False

    except Exception:
        # If any comparison fails, return False
        return False


def _numeric_or_string_comparison(
    system_value: Any, filter_value: Any, comparison_func
) -> bool:
    """Try numeric comparison first, fall back to string comparison."""
    try:
        return comparison_func(float(system_value), float(filter_value))
    except (ValueError, TypeError):
        return comparison_func(str(system_value), str(filter_value))


def execute_search(config: SearchConfig, systems: list[Systems]) -> SearchResults:
    """Execute a search configuration against available systems."""
    # Filter systems based on sys_filter
    filtered_systems = filter_systems_by_criteria(systems, config.sys_filter)

    all_results = []

    for system in filtered_systems:
        system_results = search_single_system(config, system)
        all_results.extend(system_results)

        # Apply max_results limit if specified (per system)
        if config.max_results > 0 and len(system_results) >= config.max_results:
            # Truncate this system's results if needed
            system_results = system_results[: config.max_results]

    # Apply unique filter if specified
    if config.unique:
        all_results = deduplicate_results(all_results)

    # Apply global max_results if specified
    if config.max_results > 0:
        all_results = all_results[: config.max_results]

    return SearchResults(config=config, results=all_results)


def search_single_system(config: SearchConfig, system: Systems) -> list[SearchResult]:
    """Search a single system file for matches."""
    results = []

    try:
        pattern = re.compile(config.regex, re.IGNORECASE)
    except re.error as e:
        click.echo(f"Error: Invalid regex pattern in {config.name}: {e}")
        return results

    try:
        # Determine encoding
        encoding = system.file_encoding or "utf-8"

        with system.file.open("r", encoding=encoding, errors="replace") as f:
            if config.combine and config.rs_delimiter:
                results = search_with_recordset_delimiter(config, system, f, pattern)
            else:
                results = search_line_by_line(config, system, f, pattern)

    except (OSError, UnicodeDecodeError) as e:
        click.echo(f"Error processing {system.file}: {e}")

    return results


def search_line_by_line(
    config: SearchConfig, system: Systems, file_handle, pattern: re.Pattern
) -> list[SearchResult]:
    """Search file line by line for matches."""
    results = []

    for line_num, line in enumerate(file_handle, 1):
        line = line.strip()

        # Skip empty lines unless full_scan is enabled
        if not line and not config.full_scan:
            continue

        match = pattern.search(line)
        if match:
            result = create_search_result(config, system, line, line_num, match)
            results.append(result)

            # Check max_results per system
            if config.max_results > 0 and len(results) >= config.max_results:
                break

    return results


def search_with_recordset_delimiter(
    config: SearchConfig, system: Systems, file_handle, pattern: re.Pattern
) -> list[SearchResult]:
    """Search file using recordset delimiter for multi-line records."""
    results = []

    try:
        rs_pattern = re.compile(config.rs_delimiter, re.IGNORECASE)
    except re.error as e:
        click.echo(f"Error: Invalid recordset delimiter pattern in {config.name}: {e}")
        return results

    current_record = []
    record_start_line = 1

    for line_num, line in enumerate(file_handle, 1):
        line = line.strip()

        # Check if this line starts a new record
        if rs_pattern.search(line):
            # Process the previous record if it exists
            if current_record and config.combine:
                combined_text = "\n".join(current_record)
                match = pattern.search(combined_text)
                if match:
                    result = create_search_result(
                        config, system, combined_text, record_start_line, match
                    )
                    results.append(result)

            # Start new record
            current_record = [line]
            record_start_line = line_num
        else:
            current_record.append(line)

        # Check max_results per system
        if config.max_results > 0 and len(results) >= config.max_results:
            break

    # Process the last record
    if current_record and config.combine:
        combined_text = "\n".join(current_record)
        match = pattern.search(combined_text)
        if match:
            result = create_search_result(
                config, system, combined_text, record_start_line, match
            )
            results.append(result)

    return results


def create_search_result(
    config: SearchConfig, system: Systems, text: str, line_num: int, match: re.Match
) -> SearchResult:
    """Create a SearchResult object from a regex match."""
    # Extract fields if field_list is specified
    extracted_fields = None
    if config.field_list:
        extracted_fields = {}
        for field in config.field_list:
            try:
                extracted_fields[field] = match.group(field)
            except IndexError:
                # Field not found in match groups, add as empty string
                extracted_fields[field] = ""

        # If no named groups were found, add raw_data field
        if not any(extracted_fields.values()):
            extracted_fields["raw_data"] = match.group(0)

    # Use only matching text if specified
    matched_text = match.group(0) if config.only_matching else text

    return SearchResult(
        system_name=system.system_name,
        line_number=line_num,
        matched_text=matched_text,
        extracted_fields=extracted_fields,
    )


def deduplicate_results(results: list[SearchResult]) -> list[SearchResult]:
    """Remove duplicate results based on matched_text."""
    seen = set()
    unique_results = []

    for result in results:
        # Create a key for deduplication based on matched text
        dedup_key = result.matched_text.strip().lower()

        if dedup_key not in seen:
            seen.add(dedup_key)
            unique_results.append(result)

    return unique_results


def export_search_results_to_excel(
    search_results: list[SearchResults], output_path: Path
) -> None:
    """Export search results to Excel with each search as a separate worksheet."""
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for search_result in search_results:
            if not search_result.results:
                # Still create a sheet for searches with no results
                sheet_name = sanitize_sheet_name(search_result.config.name)
                empty_df = pd.DataFrame({"No Results": ["No matches found"]})
                empty_df.to_excel(
                    writer, sheet_name=sheet_name, index=False, startrow=2
                )

                # Add comment
                worksheet = writer.sheets[sheet_name]
                if search_result.config.comment:
                    worksheet["A1"] = search_result.config.comment
                continue

            # Create DataFrame from results
            df = create_dataframe_from_results(search_result)

            # Write to Excel with search name as sheet name
            sheet_name = sanitize_sheet_name(search_result.config.name)
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)

            # Get the worksheet and format it
            worksheet = writer.sheets[sheet_name]

            # Add comment at the top
            if search_result.config.comment:
                worksheet["A1"] = search_result.config.comment
                # Style the comment cell
                worksheet["A1"].font = Font(bold=True, size=12)
                worksheet["A1"].alignment = Alignment(wrap_text=True)

            # Format as Excel table
            if not df.empty:
                format_as_excel_table(worksheet, df, startrow=3)


def create_dataframe_from_results(search_results: SearchResults) -> pd.DataFrame:
    """Convert search results to pandas DataFrame."""
    if not search_results.results:
        return pd.DataFrame()

    # Start with basic columns
    data = []

    for result in search_results.results:
        row = {
            "System Name": result.system_name,
            "Line Number": result.line_number,
            "Matched Text": result.matched_text,
        }

        # Add extracted fields if they exist
        if result.extracted_fields:
            row.update(result.extracted_fields)

        data.append(row)

    return pd.DataFrame(data)


def sanitize_sheet_name(name: str) -> str:
    """Sanitize sheet name for Excel compatibility."""
    # Excel sheet names can't contain: / \ ? * [ ] :
    # Also limit to 31 characters
    invalid_chars = ["/", "\\", "?", "*", "[", "]", ":"]

    sanitized = name
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    # Limit to 31 characters
    if len(sanitized) > 31:
        sanitized = sanitized[:28] + "..."

    return sanitized


def format_as_excel_table(worksheet, df: pd.DataFrame, startrow: int = 1) -> None:
    """Format DataFrame as an Excel table with proper styling."""
    if df.empty:
        return

    # Calculate table range
    end_row = startrow + len(df)
    end_col_letter = chr(ord("A") + len(df.columns) - 1)
    table_range = f"A{startrow}:{end_col_letter}{end_row}"

    # Create table
    table = Table(displayName=f"Table{startrow}", ref=table_range)

    # Add style
    style = TableStyleInfo(
        name="TableStyleMedium9",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=True,
    )
    table.tableStyleInfo = style

    # Add table to worksheet
    worksheet.add_table(table)

    # Auto-adjust column widths
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except:
                pass

        adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
        worksheet.column_dimensions[column_letter].width = adjusted_width


def execute_all_searches(
    program_config: ProgramConfig, systems: list[Systems]
) -> list[SearchResults]:
    """Execute all search configurations against all systems."""
    if not program_config.audit_config_file:
        raise ValueError("No audit config file specified")

    # Load search configurations
    search_configs = load_search_configs(program_config.audit_config_file)

    if program_config.verbose:
        click.echo(f"Loaded {len(search_configs)} search configurations")

    # Execute searches
    all_results = []
    for config in search_configs:
        if program_config.verbose:
            click.echo(f"Executing search: {config.name}")

        results = execute_search(config, systems)
        all_results.append(results)

        if program_config.verbose:
            click.echo(
                f"  Found {results.result_count} matches across {results.unique_systems} systems"
            )

    return all_results


def process_search_workflow(program_config: ProgramConfig) -> None:
    """Main workflow function to process searches and export results."""
    try:
        # Import here to avoid circular dependencies
        from . import process_scripts

        click.echo("Processing source files...")

        # Load systems
        systems = list(
            process_scripts.enumerate_systems_from_source_files(program_config)
        )
        click.echo(f"Found {len(systems)} systems to process")

        if not systems:
            click.echo(
                "No systems found to process. Check source files path and specification."
            )
            return

        # Execute all searches
        all_results = execute_all_searches(program_config, systems)

        # Export to Excel
        output_file = program_config.results_path / "search_results.xlsx"
        export_search_results_to_excel(all_results, output_file)

        # Summary
        total_matches = sum(result.result_count for result in all_results)
        searches_with_results = sum(
            1 for result in all_results if result.result_count > 0
        )

        click.echo("\nSearch Summary:")
        click.echo(f"  Total searches executed: {len(all_results)}")
        click.echo(f"  Searches with results: {searches_with_results}")
        click.echo(f"  Total matches found: {total_matches}")
        click.echo(f"  Results exported to: {output_file}")

    except Exception as e:
        click.echo(f"Error during search processing: {e}")
        if program_config.verbose:
            import traceback

            traceback.print_exc()
        raise
