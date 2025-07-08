"""End-to-end tests for file processing dependency injection."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from kp_analysis_toolkit.cli import cli


class TestFileProcessingE2EIntegration:
    """End-to-end tests for file processing with DI in CLI workflows."""

    def test_cli_uses_file_processing_di_for_encoding_detection(
        self,
        tmp_path: Path,
        cli_runner: CliRunner,
    ) -> None:
        """Test that CLI commands use DI-enabled file processing for encoding detection."""
        # Create test files with different encodings
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, world!", encoding="utf-8")

        # Mock the file processing to verify DI is used
        with patch(
            "kp_analysis_toolkit.utils.get_file_encoding.get_di_state",
        ) as mock_di_state:
            # Return a mock container to simulate DI being enabled
            mock_di_state.return_value = (
                None,
                True,
            )  # DI enabled but no actual container

            # Test various CLI commands that might use encoding detection
            # Using --help to avoid running complex logic while testing DI integration
            result = cli_runner.invoke(cli, ["--help", "--skip-update-check"])

            # CLI should execute without error
            assert result.exit_code == 0

            # Verify DI state was checked (might be called multiple times)
            assert mock_di_state.called

    def test_cli_file_processing_backward_compatibility(
        self,
        tmp_path: Path,
        cli_runner: CliRunner,
    ) -> None:
        """Test backward compatibility when DI is not initialized."""
        # Create test files
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content", encoding="utf-8")

        # Mock DI state to return disabled
        with patch(
            "kp_analysis_toolkit.utils.get_file_encoding.get_di_state",
        ) as mock_di_state:
            mock_di_state.return_value = (None, False)  # DI not enabled

            # Test CLI command
            result = cli_runner.invoke(cli, ["--help", "--skip-update-check"])

            # Should still work with legacy implementation
            assert result.exit_code == 0

    def test_file_processing_services_integration_with_real_files(
        self,
        tmp_path: Path,
    ) -> None:
        """Test file processing services with real files through full DI stack."""
        # Create test files with various content
        utf8_file = tmp_path / "utf8.txt"
        utf8_file.write_text("Hello, UTF-8 world! 🌍", encoding="utf-8")

        latin1_file = tmp_path / "latin1.txt"
        latin1_file.write_bytes("Hello, Latin-1 world!".encode("latin-1"))

        # Initialize full DI stack
        from kp_analysis_toolkit.core.containers.application import (
            container,
            initialize_dependency_injection,
        )

        initialize_dependency_injection(verbose=False, quiet=True)

        # Get file processing service
        service = container.file_processing().file_processing_service()

        # Test UTF-8 file processing
        utf8_result = service.process_file(utf8_file)
        from tests.conftest import assert_valid_encoding
        assert_valid_encoding(utf8_result["encoding"], "utf-8")
        assert utf8_result["hash"]
        assert len(utf8_result["hash"]) > 0

        # Test Latin-1 file processing
        latin1_result = service.process_file(latin1_file)
        assert_valid_encoding(latin1_result["encoding"], ["latin-1", "iso-8859-1", "ascii"])  # ASCII is valid for ASCII-compatible Latin-1 content
        assert latin1_result["hash"]
        assert len(latin1_result["hash"]) > 0

        # Verify different files have different hashes
        assert utf8_result["hash"] != latin1_result["hash"]

    def test_utility_functions_work_with_di_enabled(self, tmp_path: Path) -> None:
        """Test that utility functions work correctly when DI is enabled."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content for utility functions", encoding="utf-8")

        # Initialize DI
        from kp_analysis_toolkit.core.containers.application import (
            initialize_dependency_injection,
        )

        initialize_dependency_injection()

        # Test encoding detection utility
        from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding

        encoding = detect_encoding(test_file)
        from tests.conftest import assert_valid_encoding
        assert_valid_encoding(encoding, "utf-8")

        # Test hash generation utility
        from kp_analysis_toolkit.utils.hash_generator import generate_file_hash

        file_hash = generate_file_hash(test_file)
        assert file_hash
        assert len(file_hash) > 0

    def test_error_handling_in_di_enabled_utilities(self, tmp_path: Path) -> None:
        """Test error handling in utilities when DI is enabled."""
        # Initialize DI
        from kp_analysis_toolkit.core.containers.application import (
            initialize_dependency_injection,
        )

        initialize_dependency_injection()

        # Test with non-existent file
        non_existent = tmp_path / "does_not_exist.txt"

        from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding
        from kp_analysis_toolkit.utils.hash_generator import generate_file_hash

        # Should handle errors gracefully
        encoding = detect_encoding(non_existent)
        assert encoding is None  # Should return None for non-existent files

        # Hash generator throws exception for non-existent files (by design)
        import pytest
        with pytest.raises(ValueError, match="File does not exist"):
            generate_file_hash(non_existent)

    def test_di_state_management_across_multiple_operations(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that DI state is properly managed across multiple operations."""
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Content 1", encoding="utf-8")
        file2.write_text("Content 2", encoding="utf-8")

        # Initialize DI
        from kp_analysis_toolkit.core.containers.application import (
            container,
            initialize_dependency_injection,
        )

        initialize_dependency_injection()

        # Get service and perform multiple operations
        service = container.file_processing().file_processing_service()

        # Multiple file processing operations
        result1 = service.process_file(file1)
        result2 = service.process_file(file2)

        # Verify both operations completed successfully
        from tests.conftest import assert_valid_encoding
        assert_valid_encoding(result1["encoding"], "utf-8")
        assert_valid_encoding(result2["encoding"], "utf-8")
        assert result1["hash"] != result2["hash"]  # Different files, different hashes

        # Test utility functions multiple times
        from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding
        from kp_analysis_toolkit.utils.hash_generator import generate_file_hash

        # Multiple utility calls
        enc1 = detect_encoding(file1)
        enc2 = detect_encoding(file2)
        hash1 = generate_file_hash(file1)
        hash2 = generate_file_hash(file2)

        from tests.conftest import assert_valid_encoding
        assert_valid_encoding(enc1, "utf-8")
        assert_valid_encoding(enc2, "utf-8")
        assert hash1 == result1["hash"]  # Should be consistent
        assert hash2 == result2["hash"]  # Should be consistent
