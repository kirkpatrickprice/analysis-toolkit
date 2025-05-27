import json
from pathlib import Path
from typing import Any, Dict, List, LiteralString, Optional, Union

import duckdb


class DuckDBConnection:
    """
    A DuckDB connection manager that provides a context manager interface
    and methods for creating tables and inserting data from JSON.
    """

    def __init__(self, db_path: Union[str, Path]):
        """
        Initialize the DuckDB connection.

        Args:
            db_path: Path to the DuckDB database file
        """
        self.db_path: Path = Path(db_path) if isinstance(db_path, str) else db_path
        self.connection = None

    def __enter__(self):
        """Context manager entry method that connects to the database."""
        # Create parent directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Connect to the database
        self.connection = duckdb.connect(str(self.db_path))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method that closes the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_table(self, table_name: str, schema: Union[str, Dict[str, Any]]) -> None:
        """
        Create a table based on a JSON schema.

        Args:
            table_name: Name of the table to create
            schema: JSON schema as a string or dictionary. Format should be:
                   {"column1": "TYPE", "column2": "TYPE", ...}
                   One column can be marked as primary key with "PRIMARY KEY" after the type.

        Raises:
            ValueError: If connection isn't established or invalid schema
        """
        if not self.connection:
            raise ValueError("Database connection not established")

        # Parse schema if it's a string
        if isinstance(schema, str):
            try:
                schema = json.loads(schema)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON schema format")

        # Build the SQL CREATE TABLE statement
        columns = []
        for column_name, column_type in schema.items():
            columns.append(f"{column_name} {column_type}")

        column_definitions = ", ".join(columns)
        create_statement = (
            f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
        )

        # Execute the statement
        self.connection.execute(create_statement)

    def drop_table(self, table_name: str) -> None:
        """
        Drop a table if it exists.

        Args:
            table_name: Name of the table to drop

        Raises:
            ValueError: If connection isn't established
        """
        if not self.connection:
            raise ValueError("Database connection not established")

        self.connection.execute(f"DROP TABLE IF EXISTS {table_name}")

    def insert_records(
        self, table_name: str, records: Union[str, List[Dict[str, Any]]]
    ) -> None:
        """
        Insert records from JSON into a table.

        Args:
            table_name: Name of the table to insert into
            records: JSON records as a string or list of dictionaries

        Raises:
            ValueError: If connection isn't established or invalid records format
        """
        if not self.connection:
            raise ValueError("Database connection not established")

        # Parse records if it's a string
        if isinstance(records, str):
            try:
                records = json.loads(records)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON records format")

        # Make sure we have a list of dictionaries
        if not isinstance(records, list):
            records = [records]

        if not records:
            return

        # Get column names from the first record
        columns = list(records[0].keys())
        column_str: str = ", ".join(columns)

        # Generate placeholders for prepared statement
        placeholders: LiteralString = ", ".join(["?" for _ in columns])

        # Prepare the SQL statement
        insert_statement = (
            f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
        )

        # Insert the records
        for record in records:
            values = [record.get(column) for column in columns]
            self.connection.execute(insert_statement, values)

    def execute(
        self, query: str, params: Optional[tuple] = None
    ) -> duckdb.DuckDBPyRelation:
        """
        Execute a raw SQL query.

        Args:
            query: SQL query to execute
            params: Optional parameters for the query

        Returns:
            DuckDB result relation

        Raises:
            ValueError: If connection isn't established
        """
        if not self.connection:
            raise ValueError("Database connection not established")

        if params:
            return self.connection.execute(query, params)
        return self.connection.execute(query)


def get_db_schema_from_model(model_class) -> Dict[str, str]:
    """
    Generate a DuckDB schema dictionary from a Pydantic model.

    Args:
        model_class: The Pydantic model class

    Returns:
        Dictionary with column names as keys and SQL types as values
    """
    # Get JSON schema from Pydantic model
    json_schema = model_class.model_json_schema()
    properties = json_schema.get("properties", {})

    # Map Python/JSON types to SQL types
    type_mapping: Dict[str, str] = {
        "string": "VARCHAR",
        "integer": "INTEGER",
        "number": "DOUBLE",
        "boolean": "BOOLEAN",
        "UUID": "UUID",
        "path": "VARCHAR",  # Path objects become strings
    }

    schema: dict = {}
    for field_name, field_info in properties.items():
        field_type = field_info.get("type", "string")

        # Handle special cases
        if field_name == "system_id" and model_class.__name__ == "Systems":
            schema[field_name] = "UUID PRIMARY KEY"
        elif field_name == "file":
            schema["file"] = "VARCHAR"
        else:
            # Get SQL type from mapping, default to VARCHAR
            if field_type == "string" and "format" in field_info:
                # Handle special formats like UUID
                format_type = field_info["format"].upper()
                sql_type = type_mapping.get(format_type, "VARCHAR")
            else:
                sql_type = type_mapping.get(field_type, "VARCHAR")

            schema[field_name] = sql_type

    return schema
