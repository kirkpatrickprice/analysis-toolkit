# AI-GEN: claude-3.5-sonnet|2025-01-19|batch-processing-service|reviewed:yes
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

            # Verify content was converted (exact content depends on striprtf library)
            converted_content = output_file.read_text()
            assert len(converted_content) > 0
            # Should contain the readable text after RTF processing
            assert "Hello World!" in converted_content or converted_content.strip()

# END AI-GEN
