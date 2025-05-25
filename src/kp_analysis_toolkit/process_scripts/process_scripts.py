import hashlib
import re  # To handle regular expressions
import sys  # To handle command line arguments and usage
from pathlib import Path  # To handle file paths
from uuid import uuid4  # To generate unique identifiers

from chardet import UniversalDetector  # To detect file encoding

from kp_analysis_toolkit.process_scripts.data_models import (
    ProducerType,
    ProgramConfig,
    Systems,
    SystemType,
)

"""
Version History:
    0.1.0   Initial release
    0.1.1   Colorized the "no results found... deleting file" message in CSV mode
            Corrected the CSV file header line
    0.1.2   2022-11-04
            Fixed CSV export issue with non-printable characters in input files
    0.1.3   2022-11-11
            Added a short-circuit to stop processing files once we've moved beyond the interesting content.  Requires use of a "::" in the regex to identify the section we're looking for
    0.2.0   Rewrite to use OOP -- eases managing data and passing info around
            Export to Excel instad CSV files
            Unique columns whenever field_lists are provided
            Combine results from mulitple lines in the source files into a single row
            Apply filters to exclude systems by specific attributes (e.g. Windows vs Linux, Debian vs RPM, script version, os_version, etc)
    0.2.1   Fixed bug in short-circuit logic that was causing searches to bail out when a comment included the desired pattern
    0.2.2   Better error handling for UnicodeDecodeError message (e.g. when handling UTF-16 files)
    0.2.3   Changes to support building with pyinstaller
    0.2.4   2023-06-25: Fixed unprintable characters bug
    0.3.0   2023-06-30: Added capabilities to process MacOS Auditor result files
    0.3.1   2023-07-03: Added rs_delimiter search config option to handle cases where OS tools don't always print blank values (e.g. MacOS dscl . -readall...)
            See 'audit-macos-users.yaml' for example use case
    0.3.2   2025-01-25: Make changes to support /src layout and Pypi distribution
    0.3.3   2025-02-06: Add Mint as a detected debPattern (common.py)
    0.3.4   2025-02-07: Addressed issue with processing files from Oracle and Kali systems
    0.4.0   2025-05-19: Rewritten as part of the unified kpat CLI
"""


def get_config_files(config_path: Path) -> list[Path]:
    """
    Get the list of available configuration files.

    Args:
        path_type (PathType): The type of path to return (relative or absolute).

    Returns:
        list[Path]: A list of available configuration files as Path objects.

    """
    # This function should return a list of available configuration files

    config_files: list = [config_path / file for file in config_path.glob("*.yaml")]

    return config_files


def get_source_files(start_path: Path, file_spec: str) -> list[Path]:
    """
    Get the list of source files to process.

    Args:
        start_path (str): The starting path to search for files.
        file_spec (str): The file specification to match (e.g. *.txt).

    Returns:
        list[Path]: A list of source files as Path objects.

    """
    # This function should return a list of source files to process
    # For example, it will read the files in the specified directory

    p: Path = Path(start_path).absolute()
    return [file for file in p.rglob(file_spec)]


def load_systems_into_duckdb(
    config: ProgramConfig,
) -> None:
    """
    Load the systems from the configuration file.  Places all results in the DuckDB database located in the root of the out-path directory.

    The database is named 'kpat.ddb' and the table is named 'systems'.
    The table is created if it does not exist.  The table is dropped and recreated if it does exist.
    The table is created with the following columns:
        - system_id: INTEGER PRIMARY KEY
        - system_name: TEXT (derived from the file name)
        - system_type: TEXT (Darwin, Linux, Windows, etc.)
        - system_os: TEXT
        - producer: TEXT (KPNIXAUDIT, KPWINAUDIT, etc.)
        - producer_version: TEXT (Version of the producer)
        - file_hash: TEXT (SHA256 hash of the source file)
        - file: TEXT (Absolute path to the source file)

    Args:
        config (ProgramConfig): The program configuration.

    Returns:
        None

    """
    # This function should load the systems from the configuration file
    # For example, it will read the files in config.source_files
    # and load the systems into the DuckDB database


def enumerate_systems(
    program_config: ProgramConfig,
) -> list[Systems]:
    """
    Process the text files to enumerate the systems.

    Args:
        config (ProgramConfig): The program configuration.

    Returns:
        list[Systems]: A list of Systems objects.

    """
    # This function should enumerate the files to process
    # For example, it will read the files in config.source_files
    # and return a list of files to process list of SystemType objects

    results: list[Systems] = []
    for file in get_source_files(
        program_config.source_files_path,
        program_config.source_files_spec,
    ):
        # Process each file and add the results to the list

        encoding: str = get_file_encoding(file)
        producer, producer_version = get_producer_type(file, encoding)
        match producer:
            case ProducerType.KPNIXAUDIT:
                system_type: SystemType = SystemType.LINUX
            case ProducerType.KPWINAUDIT:
                system_type: SystemType = SystemType.WINDOWS
            case ProducerType.KPMACAUDIT:
                system_type: SystemType = SystemType.DARWIN
            case _:
                system_type: SystemType = SystemType.UNDEFINED
        system = Systems(
            system_id=uuid4().hex,
            system_name=file.name,
            file_encoding=encoding,
            system_type=system_type,
            system_os=None,
            producer=producer,
            producer_version=producer_version,
            file_hash=generate_file_hash(file),
            file=file.absolute(),
        )
        results.append(system)

    return results


def get_file_encoding(file_path: Path) -> str:
    """
    Get the file encoding using chardet.

    Args:
        file_path (Path): The path to the file.

    Returns:
        str: The detected file encoding.

    """
    # This function should detect the file encoding
    # For example, you can use chardet or other libraries to detect the encoding

    detector = UniversalDetector()
    with open(file_path, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result["encoding"] if detector.result else "unknown"


def get_producer_type(file_path: Path, encoding: str) -> tuple[ProducerType, str]:
    """
    Get the producer type based on the file path.  Uses regular expressions to identify the producer.

    Args:
        file_path (Path): The path to the file.

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
    with file_path.open("r", encoding=encoding) as f:
        for line in f:
            for producer, pattern in regex_patterns.items():
                regex_result = re.search(pattern, line, re.IGNORECASE)
                if regex_result:
                    # If a match is found, return the corresponding details
                    return (
                        ProducerType(producer),
                        regex_result.group("producer_version"),
                    )
    # If no match is found, return OTHER
    return ProducerType.OTHER


def generate_file_hash(file_path: Path) -> str:
    """Generate the file hash if not provided."""

    if file_path is None or not file_path.exists():
        raise ValueError(f"File path is required to generate the hash {file_path}.")

    # Generate the hash (SHA256) of the file
    sha256_hash: hashlib.HASH = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read and update hash in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (IOError, PermissionError) as e:
        raise ValueError(f"Error reading file {file_path}: {e}") from e


if __name__ == "__main__":
    print("process_scripts.py should be run as part of the kpat CLI")
    sys.exit(0)
