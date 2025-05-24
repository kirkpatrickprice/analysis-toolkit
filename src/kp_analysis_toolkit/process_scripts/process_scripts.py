import sys  # To handle command line arguments and usage
from enum import Enum  # To define enumerations
from pathlib import Path  # To handle file paths

import duckdb  # To handle DuckDB database operations
from pydantic import BaseModel

from kp_analysis_toolkit.process_scripts import (
    GLOBALS,
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


class ProgramConfig(BaseModel):
    """Class to hold the program configuration."""

    audit_config_file: str
    source_files: str
    yaml_conf_file: str


class PathType(str, Enum):
    """Enum to define the type of path."""

    RELATIVE = "relative"
    ABSOLUTE = "absolute"


def get_config_files(path_type: PathType = PathType.RELATIVE) -> list[Path]:
    """
    Get the list of available configuration files.

    Args:
        path_type (PathType): The type of path to return (relative or absolute).

    Returns:
        list[Path]: A list of available configuration files as Path objects.

    """
    # This function should return a list of available configuration files

    conf_d_path: Path = get_program_base_path() / GLOBALS["CONF_PATH"]
    if path_type == PathType.RELATIVE:
        config_files: Path = [
            Path(conf_d_path / file).relative_to(conf_d_path)
            for file in conf_d_path.glob("*.yaml")
        ]
    else:
        config_files = [conf_d_path / file for file in conf_d_path.glob("*.yaml")]

    return config_files


def get_source_files(start_path: str, file_spec: str) -> list[Path]:
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
    return [file.relative_to(p) for file in p.rglob(file_spec)]


def get_program_base_path() -> Path:
    """Get the base path for the application."""
    # This function should return the base path for the application
    # For example, it could return the path to the directory where the script is located
    return Path(__file__).parent


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

    # Create the output directory if it does not exist
    out_path: Path = Path(config.out_path)
    out_path.mkdir(parents=True, exist_ok=True)

    # DuckDB database file
    duckdb_path: Path = out_path / "kpat.ddb"

    # DuckDB table name
    duckdb_table: str = "systems"

    # DuckDB connection
    duckdb_conn = duckdb.connect(duckdb_path)

    # Create the table if it does not exist
    duckdb_conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {duckdb_table} (
            system_id INTEGER PRIMARY KEY,
            system_name TEXT,
            system_type TEXT,
            system_os TEXT,
            producer TEXT,
            producer_version TEXT
        )
        """,
    )


if __name__ == "__main__":
    print("process_scripts.py should be run as part of the kpat CLI")
    sys.exit(0)
