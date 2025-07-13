"""Integration test for RTF to text DI services."""

import tempfile
from pathlib import Path

import pytest

from kp_analysis_toolkit.core.containers.application import (
    container,
    initialize_dependency_injection,
)


@pytest.mark.usefixtures("initialized_container")
class TestRtfToTextIntegration:
    """Integration tests for RTF to text using DI services."""

    def test_rtf_to_text_service_integration(self) -> None:
        """Test that the RTF to text service works end-to-end with DI."""
        # Get the service from the DI container
        rtf_service = container.rtf_to_text.rtf_to_text_service()

        assert rtf_service is not None
        assert hasattr(rtf_service, "convert_file")
        assert hasattr(rtf_service, "discover_rtf_files")

    def test_full_rtf_conversion_workflow(self) -> None:
        """Test a complete RTF conversion workflow using DI services."""
        # Initialize DI if not already done
        initialize_dependency_injection(verbose=False, quiet=True)

        # Get the service from the DI container
        rtf_service = container.rtf_to_text.rtf_to_text_service()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a test RTF file
            rtf_file = tmpdir_path / "test.rtf"
            rtf_content = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}} \f0\fs24 Hello World!}"
            rtf_file.write_text(rtf_content)

            # Define output file
            output_file = tmpdir_path / "test.txt"

            # Convert the file using the DI service
            rtf_service.convert_file(rtf_file, output_file)

            # Verify the output file was created
            assert output_file.exists()

            # Verify the content was converted (basic check)
            content = output_file.read_text(encoding="ascii", errors="ignore")
            assert len(content) > 0
            # Note: The exact content depends on the RTF parser implementation

    def test_rtf_file_discovery(self) -> None:
        """Test RTF file discovery functionality."""
        # Initialize DI if not already done
        initialize_dependency_injection(verbose=False, quiet=True)

        # Get the service from the DI container
        rtf_service = container.rtf_to_text.rtf_to_text_service()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create test files
            rtf_file1 = tmpdir_path / "test1.rtf"
            rtf_file2 = tmpdir_path / "subdir" / "test2.rtf"
            txt_file = tmpdir_path / "test.txt"

            rtf_file1.write_text(r"{\rtf1 content1}")
            rtf_file2.parent.mkdir(exist_ok=True)
            rtf_file2.write_text(r"{\rtf1 content2}")
            txt_file.write_text("not rtf")

            # Test directory discovery
            discovered_files = rtf_service.discover_rtf_files(tmpdir_path)

            expected_file_count = 2
            assert len(discovered_files) == expected_file_count
            assert rtf_file1 in discovered_files
            assert rtf_file2 in discovered_files
            assert txt_file not in list(discovered_files)

            # Test single file discovery
            single_file_result = rtf_service.discover_rtf_files(rtf_file1)
            assert single_file_result == [rtf_file1]
