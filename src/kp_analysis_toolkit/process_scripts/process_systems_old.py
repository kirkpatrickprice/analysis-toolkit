import re  # To handle regular expressions
import sys  # To handle command line arguments and usage
from pathlib import Path  # To handle file paths

from kp_analysis_toolkit.process_scripts.models.base import RegexPatterns
from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig
from kp_analysis_toolkit.process_scripts.models.types import (
    ProducerType,
)
from kp_analysis_toolkit.utils.hash_generator import hash_file


def _extract_regex_data_with_raw(
    file: Path,
    encoding: str,
    patterns: RegexPatterns,
) -> tuple[str | None, dict[str, str] | None]:
    """
    Extract data using regex patterns and return both the formatted result and the raw matching data.

    Args:
        file: Path to the file to process
        encoding: File encoding
        patterns: Regex extraction configuration

    Returns:
        Formatted string or None if extraction fails

    """
    extracted_data: dict[str, str] = {}
    required_keys = set(patterns.patterns.keys())

    try:
        with file.open("r", encoding=encoding) as f:
            for line in f:
                usable_text: str = line.strip()
                if not usable_text:
                    continue

                # Check each pattern that hasn't been matched yet
                for key, pattern in patterns.patterns.items():
                    if key not in extracted_data:  # Skip if already found
                        match: re.Match[str] | None = re.search(
                            pattern,
                            usable_text,
                            re.IGNORECASE,
                        )
                        if match:
                            extracted_data[key] = match.group(key).strip()

                            # Early exit if we have all required data
                            if len(extracted_data) == len(required_keys):
                                return patterns.formatter(
                                    extracted_data,
                                ), extracted_data
    except (OSError, UnicodeDecodeError):
        return None, None

    # Return formatted result if we have all required data
    if len(extracted_data) == len(required_keys):
        return patterns.formatter(extracted_data), extracted_data

    return None, None


def generate_file_hash(file: Path) -> str:
    """Generate the file hash if not provided."""
    if file is None or not file.exists():
        message: str = f"File path is required to generate the hash {file}."
        raise ValueError(message)

    # Generate the hash (SHA256) of the file
    try:
        return hash_file(file)
    except ValueError as e:
        message: str = f"Error generating hash for file {file}: {e}"
        raise ValueError(message) from e


def get_config_files(config_path: Path) -> list[Path]:
    """
    Get the list of available configuration files.

    Args:
        config_path (Path): The path to the directory containing configuration files.

    Returns:
        list[ConfigFile]: A list of available configuration files as Path objects.

    """
    # This function should return a list of available configuration files

    config_files: list[Path] = [
        Path(config_path / f) for f in config_path.glob("*.yaml")
    ]

    return config_files


def get_source_files(program_config: ProgramConfig) -> list[Path]:
    """
    Get the list of source files to process.

    Args:
        program_config (ProgramConfig): The program configuration object.

    Returns:
        list[Path]: A list of source files as Path objects.

    """
    # This function should return a list of source files to process
    # For example, it will read the files in the specified directory

    p: Path = program_config.source_files_path.absolute()
    return list(p.rglob(program_config.source_files_spec))


def get_producer_type(file: Path, encoding: str) -> tuple[ProducerType, str]:
    """
    Get the producer type based on the file path.  Uses regular expressions to identify the producer.

    Args:
        file (Path): The path to the file.
        encoding (str): The file encoding.

    Returns:
        ProducerType: The producer type.

    """
    # This function should determine the producer type based on the file path
    # For example, you can use regex or string matching to identify the producer

    """
    Windows: System_PSDetails::KPWINVERSION: 0.4.8
    Linux  : KPNIXVERSION: 0.6.22
    MacOS  : KPMACVERSION: 0.1.0
    """

    regex_patterns: dict[str, str] = {
        "KPNIXAUDIT": r"^(?P<producer_type>KPNIXVERSION): (?P<producer_version>[0-9.]+)",
        "KPWINAUDIT": r"^System_PSDetails::(?P<producer_type>KPWINVERSION): (?P<producer_version>[0-9.]+)",
        "KPMACAUDIT": r"^(?P<producer_type>KPMACVERSION): (?P<producer_version>[0-9.]+)",
    }
    with file.open("r", encoding=encoding) as f:
        for line in f:
            for producer, pattern in regex_patterns.items():
                regex_result: re.Match[str] | None = re.search(
                    pattern,
                    line,
                    re.IGNORECASE,
                )
                if regex_result:
                    # If a match is found, return the corresponding details
                    return (
                        ProducerType(producer),
                        regex_result.group("producer_version"),
                    )
    # If no match is found, return OTHER with unknown version
    return ProducerType.OTHER, "Unknown"


def get_system_details(
    file: Path,
    encoding: str,
    producer: ProducerType,
) -> tuple[str | None, dict[str, str] | None]:
    """
    Get the system OS based from the source file.

    Args:
        file (Path): The Path object of the file.
        encoding (str): The file encoding.
        producer (ProducerType): The producer (e.g. KPNIXAudit, KPWinAudit, etc) of the file.

    Returns:
        tuple[str | None, dict[str, str] | None]: A tuple containing:
            - The formatted system OS (e.g. Windows 11, Ubuntu 22.04, Redhat 8.6, MacOS 13.4.1) or None
            - A dictionary of OS-specific variables or None if they couldn't be determined.

    """


if __name__ == "__main__":
    print("process_scripts.py should be run as part of the kpat CLI")
    sys.exit(0)
