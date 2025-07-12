"""End-to-end tests for Excel export dependency injection."""

import tempfile
from pathlib import Path

import pandas as pd

from kp_analysis_toolkit.core import ApplicationContainer
from kp_analysis_toolkit.utils.excel_utils import (
    clear_excel_export_service,
    export_dataframe_to_excel,
    sanitize_sheet_name,
    set_excel_export_service,
)

# Constants
MAX_SHEET_NAME_LENGTH = 31


class TestExcelExportE2E:
    """End-to-end tests for complete Excel export workflow."""

    def setup_method(self) -> None:
        """Set up test environment."""
        # Clear any existing service
        clear_excel_export_service()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        # Clear service after each test
        clear_excel_export_service()

    def test_complete_workflow_with_di(self) -> None:
        """Test complete workflow from container setup to Excel export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup DI container
            container = ApplicationContainer()
            container.core().config.verbose.from_value(False)
            container.core().config.quiet.from_value(False)
            container.core().config.console_width.from_value(120)
            container.core().config.force_terminal.from_value(True)
            container.core().config.stderr_enabled.from_value(True)
            container.wire(modules=["kp_analysis_toolkit.utils.excel_utils"])

            try:
                # Get and configure Excel service
                excel_service = container.core().excel_export_service()
                set_excel_export_service(excel_service)

                # Create comprehensive test data
                test_data = pd.DataFrame(
                    {
                        "Name": [
                            "Alice Smith",
                            "Bob Johnson",
                            "Charlie Brown",
                            "Diana Prince",
                        ],
                        "Age": [25, 30, 35, 28],
                        "Department": ["Engineering", "Marketing", "Sales", "HR"],
                        "Start Date": [
                            "2023-01-15",
                            "2022-06-01",
                            "2021-03-12",
                            "2023-05-20",
                        ],
                        "Salary": [75000, 65000, 55000, 68000],
                        "Notes": [
                            "Excellent performance\nPromotion candidate",
                            "Strong team player",
                            "Top performer in Q3",
                            "New hire\nOnboarding in progress",
                        ],
                    },
                )

                # Test multiple scenarios
                test_scenarios = [
                    {
                        "filename": "employee_report.xlsx",
                        "sheet_name": "Employee Data",
                        "title": "Employee Report 2023",
                        "as_table": True,
                    },
                    {
                        "filename": "simple_export.xlsx",
                        "sheet_name": "Data",
                        "title": None,
                        "as_table": False,
                    },
                    {
                        "filename": "special_chars.xlsx",
                        "sheet_name": "Test/Sheet\\With*Invalid[:?]Chars",
                        "title": "Special Characters Test",
                        "as_table": True,
                    },
                ]

                for scenario in test_scenarios:
                    output_path = Path(temp_dir) / scenario["filename"]

                    # Export using DI service
                    export_dataframe_to_excel(
                        test_data,
                        output_path,
                        sheet_name=scenario["sheet_name"],
                        title=scenario["title"],
                        as_table=scenario["as_table"],
                    )

                    # Verify file was created
                    assert output_path.exists()

                    # Verify content by reading back
                    with pd.ExcelFile(output_path) as excel_file:
                        # Check that sheet exists (possibly with sanitized name)
                        assert len(excel_file.sheet_names) == 1
                        sheet_name = excel_file.sheet_names[0]

                        # Verify data integrity - skip title row if present
                        if scenario["title"]:
                            # Title is in row 1, headers start at row 2 (0-indexed: 1)
                            result_data = pd.read_excel(
                                output_path, sheet_name=sheet_name, header=1
                            )
                        else:
                            # No title, headers start at row 1 (0-indexed: 0)
                            result_data = pd.read_excel(
                                output_path, sheet_name=sheet_name
                            )

                        assert len(result_data) == len(test_data)
                        assert set(result_data.columns) == set(test_data.columns)

                        # Verify data types are preserved reasonably
                        assert result_data["Name"].dtype == "object"
                        assert result_data["Age"].dtype in ["int64", "Int64"]

            finally:
                # Clean up
                container.unwire()

    def test_workflow_without_di_fallback(self) -> None:
        """Test workflow falls back to direct implementation when no DI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Ensure no DI service is configured
            clear_excel_export_service()

            # Create test data
            test_data = pd.DataFrame(
                {
                    "Product": ["Widget A", "Widget B", "Widget C"],
                    "Price": [10.99, 25.50, 15.75],
                    "Stock": [100, 50, 75],
                },
            )

            output_path = Path(temp_dir) / "fallback_test.xlsx"

            # Export using fallback implementation
            export_dataframe_to_excel(
                test_data,
                output_path,
                sheet_name="Products",
                title="Product Inventory",
                as_table=True,
            )

            # Verify file was created
            assert output_path.exists()

            # Verify content - skip title row since title is provided
            result_data = pd.read_excel(output_path, sheet_name="Products", header=1)
            assert len(result_data) == len(test_data)
            assert list(result_data.columns) == list(test_data.columns)

    def test_sheet_name_sanitization_e2e(self) -> None:
        """Test end-to-end sheet name sanitization."""
        # Test both with and without DI
        problematic_names = [
            "Sheet/With\\Slashes",
            "Sheet*With:Special?Chars[Test]",
            "Very_Long_Sheet_Name_That_Exceeds_Excel_Limit_And_Should_Be_Truncated",
            "",
            "   ",
        ]

        # Test with DI
        container = ApplicationContainer()
        container.wire(modules=["kp_analysis_toolkit.utils.excel_utils"])

        try:
            excel_service = container.core().excel_export_service()
            set_excel_export_service(excel_service)

            di_results = [sanitize_sheet_name(name) for name in problematic_names]

        finally:
            container.unwire()
            clear_excel_export_service()

        # Test without DI (fallback)
        fallback_results = [sanitize_sheet_name(name) for name in problematic_names]

        # Both should produce valid sheet names
        for di_result, fallback_result in zip(
            di_results,
            fallback_results,
            strict=True,
        ):
            # Both should be strings
            assert isinstance(di_result, str)
            assert isinstance(fallback_result, str)

            # Both should be non-empty
            assert di_result.strip()
            assert fallback_result.strip()

            # Both should be within Excel limits
            assert len(di_result) <= MAX_SHEET_NAME_LENGTH
            assert len(fallback_result) <= MAX_SHEET_NAME_LENGTH

            # Both should not contain invalid characters
            invalid_chars = "/\\*[:?]"
            for char in invalid_chars:
                assert char not in di_result
                assert char not in fallback_result
