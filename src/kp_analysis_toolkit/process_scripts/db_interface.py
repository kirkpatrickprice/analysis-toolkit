from pathlib import Path

import duckdb

from kp_analysis_toolkit.process_scripts import GLOBALS
from kp_analysis_toolkit.process_scripts.data_models import ProgramConfig


def connection(program_config: ProgramConfig = None) -> duckdb.DuckDBPyConnection:
    """
    Create a connection to the DuckDB database.

    Returns:
        duckdb.DuckDBPyConnection: The DuckDB connection.
    """
    # DuckDB database file
    duckdb_path: Path = Path(program_config.db_path) / GLOBALS["DB_FILENAME"]

    # Create the DuckDB connection
    conn: duckdb.DuckDBPyConnection = duckdb.connect(duckdb_path)

    return conn
