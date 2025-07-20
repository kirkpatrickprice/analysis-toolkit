"""End-to-end tests for CSV processing service through full application workflows."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from kp_analysis_toolkit.core.containers.application import (
    container,
    initialize_dependency_injection,
)

if TYPE_CHECKING:
    from pathlib import Path

    from kp_analysis_toolkit.core.services.csv_processing.protocols import CSVProcessor

# Test constants
SAMPLE_SALES_RECORDS = 5
EXPECTED_ELECTRONICS_QUANTITY = 50  # 10+25+15
EXPECTED_FURNITURE_QUANTITY = 13  # 5+8
ERROR_FILES_COUNT = 2
GOOD_FILE_RECORDS = 2


class TestCSVProcessingE2E:
    """End-to-end tests for CSV processing service in complete workflows."""

    def setup_method(self) -> None:
        """Set up the application container for each test."""
        initialize_dependency_injection()

    def test_csv_data_analysis_workflow_e2e(self, tmp_path: Path) -> None:
        """Test complete CSV data analysis workflow from file to insights."""
        # Create realistic dataset
        test_file: Path = tmp_path / "sales_data.csv"
        sales_data: list[str] = [
            "Product,Category,Price,Quantity,Revenue,Date",
            "Laptop,Electronics,999.99,10,9999.90,2024-01-15",
            "Phone,Electronics,699.99,25,17499.75,2024-01-16",
            "Desk,Furniture,299.99,5,1499.95,2024-01-17",
            "Chair,Furniture,199.99,8,1599.92,2024-01-18",
            "Tablet,Electronics,399.99,15,5999.85,2024-01-19",
        ]
        test_file.write_text("\n".join(sales_data))

        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Step 1: Load the data
        sales_data_df: pd.DataFrame = service.read_csv_file(test_file)

        # Step 2: Validate data structure
        assert isinstance(sales_data_df, pd.DataFrame)
        assert len(sales_data_df) == SAMPLE_SALES_RECORDS
        expected_columns: list[str] = [
            "Product",
            "Category",
            "Price",
            "Quantity",
            "Revenue",
            "Date",
        ]
        assert list(sales_data_df.columns) == expected_columns

        # Step 3: Data analysis workflow
        # Group by category and calculate totals
        category_summary: pd.DataFrame = (
            sales_data_df.groupby("Category")
            .agg(
                {
                    "Quantity": "sum",
                    "Revenue": "sum",
                },
            )
            .reset_index()
        )

        # Verify analysis results
        electronics_data: pd.DataFrame = category_summary[
            category_summary["Category"] == "Electronics"
        ]
        furniture_data: pd.DataFrame = category_summary[
            category_summary["Category"] == "Furniture"
        ]

        assert len(electronics_data) == 1
        assert len(furniture_data) == 1

        # Verify calculations
        electronics_qty: int = electronics_data.iloc[0]["Quantity"]
        furniture_qty: int = furniture_data.iloc[0]["Quantity"]

        # Electronics: 10+25+15 = 50, Furniture: 5+8 = 13
        assert electronics_qty == EXPECTED_ELECTRONICS_QUANTITY
        assert furniture_qty == EXPECTED_FURNITURE_QUANTITY

    def test_csv_error_recovery_workflow_e2e(self, tmp_path: Path) -> None:
        """Test error recovery workflow when processing problematic CSV files."""
        # Create a mix of good and problematic files
        good_file: Path = tmp_path / "good_data.csv"
        good_file.write_text("Name,Age,City\nJohn,25,NYC\nJane,30,LA")

        empty_file: Path = tmp_path / "empty_data.csv"
        empty_file.write_text("")

        malformed_file: Path = tmp_path / "malformed_data.csv"
        malformed_file.write_text("Name,Age,City\nJohn,25\nJane,30,LA,Extra,Field")

        files_to_process: list[Path] = [good_file, empty_file, malformed_file]

        # Get service from container
        service: CSVProcessor = container.core().csv_processor_service()

        # Process files with error handling
        successful_results: list[tuple[str, pd.DataFrame]] = []
        errors_encountered: list[tuple[str, str]] = []

        for file_path in files_to_process:
            try:
                file_data_df: pd.DataFrame = service.read_csv_file(file_path)
                successful_results.append((file_path.name, file_data_df))
            except (FileNotFoundError, ValueError) as e:
                errors_encountered.append((file_path.name, type(e).__name__))

        # Verify error recovery workflow
        assert len(successful_results) == 1  # Only good_file should succeed
        assert len(errors_encountered) == ERROR_FILES_COUNT  # Two files should fail

        # Verify successful result
        success_name, success_data_df = successful_results[0]
        assert success_name == "good_data.csv"
        assert len(success_data_df) == GOOD_FILE_RECORDS
        assert list(success_data_df.columns) == ["Name", "Age", "City"]

    def test_csv_service_integration_with_application_container_e2e(self) -> None:
        """Test CSV service integration with full application container lifecycle."""
        # Test service factory behavior
        service1: CSVProcessor = container.core().csv_processor_service()
        service2: CSVProcessor = container.core().csv_processor_service()

        # Verify factory creates new instances
        assert service1 is not service2
        assert type(service1).__name__ == "CSVProcessorService"
        assert type(service2).__name__ == "CSVProcessorService"

        # Test container reset and reinitialization
        original_container_id: int = id(container)

        # Reinitialize dependency injection
        initialize_dependency_injection()

        # Verify container still works after reinitialization
        service3: CSVProcessor = container.core().csv_processor_service()
        assert type(service3).__name__ == "CSVProcessorService"

        # Verify container identity remains consistent
        current_container_id: int = id(container)
        assert current_container_id == original_container_id
