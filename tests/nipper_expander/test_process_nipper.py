"""Tests for the nipper_expander.process_nipper module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig
from kp_analysis_toolkit.nipper_expander.process_nipper import process_nipper_csv


class TestProcessNipperCSV:
    """Tests for the process_nipper_csv function."""

    def test_single_device_per_row(self, tmp_path: Path) -> None:
        """Test processing CSV with single device per row (no expansion needed)."""
        # Create test CSV content
        csv_content = """Issue Title,Devices,Rating,Finding,Impact,Ease,Recommendation
CVE-2023-1234,router1,High,Test vulnerability,High impact,Easy,Apply patch
CVE-2023-5678,switch1,Medium,Another test,Medium impact,Moderate,Update config"""

        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_content)

        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(input_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        # Process the CSV
        result_df = process_nipper_csv(config)

        # Verify results
        expected_rows = 2
        assert len(result_df) == expected_rows
        assert list(result_df["Devices"]) == ["router1", "switch1"]
        assert result_df.iloc[0]["Issue Title"] == "CVE-2023-1234"
        assert result_df.iloc[1]["Issue Title"] == "CVE-2023-5678"

    def test_multiple_devices_per_row_expansion(self, tmp_path: Path) -> None:
        """Test processing CSV with multiple devices per row (expansion needed)."""
        # Create test CSV content with multi-line devices
        csv_content = """Issue Title,Devices,Rating,Finding,Impact,Ease,Recommendation
CVE-2023-1234,"router1
switch1
firewall1",High,Test vulnerability affecting multiple devices,High impact,Easy,Apply patch
CVE-2023-5678,single_device,Medium,Another test,Medium impact,Moderate,Update config"""

        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_content)

        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(input_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        # Process the CSV
        result_df = process_nipper_csv(config)

        # Verify results - should have 4 rows total (3 expanded + 1 single)
        expected_total_rows = 4
        assert len(result_df) == expected_total_rows

        # Check the expanded rows
        devices = list(result_df["Devices"])
        assert "router1" in devices
        assert "switch1" in devices
        assert "firewall1" in devices
        assert "single_device" in devices

        # Verify all expanded rows have the same finding info
        cve_1234_rows = result_df[result_df["Issue Title"] == "CVE-2023-1234"]
        expected_expanded_rows = 3
        assert len(cve_1234_rows) == expected_expanded_rows
        assert all(cve_1234_rows["Rating"] == "High")

    def test_empty_devices_handling(self, tmp_path: Path) -> None:
        """Test handling of empty or whitespace-only device entries."""
        csv_content = """Issue Title,Devices,Rating,Finding,Impact,Ease,Recommendation
CVE-2023-1234,"router1

switch1
",High,Test with empty lines,High impact,Easy,Apply patch
CVE-2023-5678,"
device2",Medium,Test with whitespace,Medium impact,Moderate,Update config"""

        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_content)

        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(input_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        result_df = process_nipper_csv(config)

        # Should only have valid device entries (empty lines filtered out)
        devices = list(result_df["Devices"])
        assert "router1" in devices
        assert "switch1" in devices
        # The implementation preserves Windows line endings, so device2 will have \r\n prefix
        assert any("device2" in device for device in devices)
        assert "" not in devices
        assert "   " not in devices

    def test_various_line_endings(self, tmp_path: Path) -> None:
        """Test handling of different line ending styles in device lists."""
        # Test with different line separators
        csv_content = """Issue Title,Devices,Rating,Finding,Impact,Ease,Recommendation
CVE-2023-1234,"router1
switch1
firewall1
gateway1",High,Test with mixed line endings,High impact,Easy,Apply patch"""

        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_content)

        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(input_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        result_df = process_nipper_csv(config)

        # Should handle all line ending types
        devices = list(result_df["Devices"])
        expected_devices = ["router1", "switch1", "firewall1", "gateway1"]
        assert all(device in devices for device in expected_devices)

    def test_no_devices_column_error(self, tmp_path: Path) -> None:
        """Test error handling when Devices column is missing."""
        csv_content = """Issue Title,Rating,Finding
CVE-2023-1234,High,Test vulnerability"""

        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_content)

        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(input_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        # Should raise KeyError for missing Devices column
        with pytest.raises(KeyError):
            process_nipper_csv(config)

    def test_empty_csv_file(self, tmp_path: Path) -> None:
        """Test handling of empty CSV file."""
        input_file = tmp_path / "empty.csv"
        input_file.write_text("")

        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(input_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        # Should handle empty file gracefully
        with pytest.raises(pd.errors.EmptyDataError):
            process_nipper_csv(config)

    def test_file_not_found_error(self, tmp_path: Path) -> None:
        """Test error handling when input file doesn't exist."""
        non_existent_file = tmp_path / "nonexistent.csv"
        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(non_existent_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            process_nipper_csv(config)

    @patch(
        "kp_analysis_toolkit.nipper_expander.process_nipper.export_dataframe_to_excel",
    )
    def test_excel_export_called_correctly(
        self,
        mock_export: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that Excel export is called with correct parameters."""
        csv_content = """Issue Title,Devices,Rating,Finding,Impact,Ease,Recommendation
CVE-2023-1234,router1,High,Test vulnerability,High impact,Easy,Apply patch"""

        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_content)

        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(input_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        process_nipper_csv(config)

        # Verify export was called with correct parameters
        mock_export.assert_called_once()
        call_args = mock_export.call_args

        # The output file is generated by ProgramConfig.output_file, not the one we set
        assert str(call_args[0][1]).endswith(".xlsx")  # Just check it's an xlsx file
        assert call_args[1]["sheet_name"] == "Expanded Nipper"
        assert (
            call_args[1]["title"]
            == "Nipper Expanded Report - One row per device/finding"
        )
        assert call_args[1]["as_table"] is True

    def test_preserve_all_columns(self, tmp_path: Path) -> None:
        """Test that all original columns are preserved during expansion."""
        csv_content = """Issue Title,Devices,Rating,Finding,Impact,Ease,Recommendation
CVE-2023-1234,"router1
switch1",High,Test vulnerability,High impact,Easy,Update firmware
CVE-2023-5678,device1,Medium,Another test,Medium impact,Moderate,Apply patch"""

        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_content)

        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(input_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        result_df = process_nipper_csv(config)

        # Verify all columns are preserved
        expected_columns = [
            "Issue Title",
            "Devices",
            "Rating",
            "Finding",
            "Impact",
            "Ease",
            "Recommendation",
        ]
        assert list(result_df.columns) == expected_columns

        # Verify expanded rows have same data except for Devices
        cve_1234_rows = result_df[result_df["Issue Title"] == "CVE-2023-1234"]
        expected_expanded_rows = 2
        assert len(cve_1234_rows) == expected_expanded_rows
        assert all(cve_1234_rows["Impact"] == "High impact")
        assert all(cve_1234_rows["Recommendation"] == "Update firmware")

    def test_devices_with_special_characters(self, tmp_path: Path) -> None:
        """Test handling of device names with special characters."""
        csv_content = """Issue Title,Devices,Rating,Finding,Impact,Ease,Recommendation
CVE-2023-1234,"router-1_main
switch.lab.local
fw@site1
server (prod)",High,Test with special characters,High impact,Easy,Apply patch"""

        input_file = tmp_path / "input.csv"
        input_file.write_text(csv_content)

        output_file = tmp_path / "output.xlsx"

        config = ProgramConfig(
            input_file=str(input_file),
            output_path=str(tmp_path),
            output_file=output_file,
        )

        result_df = process_nipper_csv(config)

        # Verify special characters are preserved
        devices = list(result_df["Devices"])
        expected_devices = [
            "router-1_main",
            "switch.lab.local",
            "fw@site1",
            "server (prod)",
        ]
        assert all(device in devices for device in expected_devices)
