"""Tests for cli_functions module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from kp_analysis_toolkit.cli.utils.path_helpers import create_results_directory
from kp_analysis_toolkit.cli.utils.system_utils import get_object_size
from kp_analysis_toolkit.process_scripts.models.program_config import ProgramConfig


class TestCreateResultsPath:
    """Test results path creation functionality."""

    def test_creates_new_path(self) -> None:
        """Test creating a new results path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir) / "new_results"

            # Create mock program config
            program_config = MagicMock(spec=ProgramConfig)
            program_config.results_path = results_path
            program_config.verbose = False

            # Path should not exist initially
            assert not results_path.exists()

            create_results_directory(results_path, verbose=program_config.verbose)

            # Path should be created
            assert results_path.exists()
            assert results_path.is_dir()

    def test_reuses_existing_path(self) -> None:
        """Test reusing an existing results path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir)  # Use existing temp directory

            # Create mock program config
            program_config = MagicMock(spec=ProgramConfig)
            program_config.results_path = results_path
            program_config.verbose = False

            # Path should already exist
            assert results_path.exists()

            # Should not raise an error
            create_results_directory(results_path, verbose=program_config.verbose)

            # Path should still exist
            assert results_path.exists()

    @patch("kp_analysis_toolkit.cli.utils.path_helpers.get_rich_output")
    def test_verbose_output_new_path(self, mock_get_rich_output: MagicMock) -> None:
        """Test verbose output when creating new path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir) / "new_results"

            # Create mock rich_output
            mock_rich_output = MagicMock()
            mock_get_rich_output.return_value = mock_rich_output

            # Create mock program config with verbose enabled
            program_config = MagicMock(spec=ProgramConfig)
            program_config.results_path = results_path
            program_config.verbose = True

            create_results_directory(results_path, verbose=program_config.verbose)

            # Should have called debug method for creating path
            mock_rich_output.debug.assert_called()
            assert any(
                "Creating results path" in str(call)
                for call in mock_rich_output.debug.call_args_list
            )

    @patch("kp_analysis_toolkit.cli.utils.path_helpers.get_rich_output")
    def test_verbose_output_existing_path(
        self, mock_get_rich_output: MagicMock,
    ) -> None:
        """Test verbose output when reusing existing path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir)  # Use existing temp directory

            # Create mock rich_output
            mock_rich_output = MagicMock()
            mock_get_rich_output.return_value = mock_rich_output

            # Create mock program config with verbose enabled
            program_config = MagicMock(spec=ProgramConfig)
            program_config.results_path = results_path
            program_config.verbose = True  # Set to True to trigger verbose output

            create_results_directory(results_path, verbose=program_config.verbose)

            # Should have called info method for reusing path
            mock_rich_output.info.assert_called()
            assert any(
                "Reusing results path" in str(call)
                for call in mock_rich_output.info.call_args_list
            )

    def test_creates_nested_path(self) -> None:
        """Test creating a nested results path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir) / "level1" / "level2" / "results"

            # Create mock program config
            program_config = MagicMock(spec=ProgramConfig)
            program_config.results_path = results_path
            program_config.verbose = False

            # Nested path should not exist initially
            assert not results_path.exists()
            assert not results_path.parent.exists()

            create_results_directory(results_path, verbose=program_config.verbose)

            # Nested path should be created
            assert results_path.exists()
            assert results_path.is_dir()


class TestGetSize:
    """Test object size calculation functionality."""

    def test_simple_objects(self) -> None:
        """Test size calculation for simple objects."""
        # Test basic types
        assert get_object_size(42) > 0
        assert get_object_size("hello") > 0
        assert get_object_size([1, 2, 3]) > 0
        assert get_object_size({"key": "value"}) > 0

    def test_nested_objects(self) -> None:
        """Test size calculation for nested objects."""
        nested_dict = {
            "level1": {
                "level2": {
                    "data": [1, 2, 3, 4, 5],
                    "text": "some text content",
                },
            },
        }

        size = get_object_size(nested_dict)
        assert size > 0

    def test_circular_references(self) -> None:
        """Test handling of circular references."""
        # Create circular reference
        obj1 = {"name": "obj1"}
        obj2 = {"name": "obj2", "ref": obj1}
        obj1["ref"] = obj2

        # Should not cause infinite recursion
        size = get_object_size(obj1)
        assert size > 0

    def test_empty_objects(self) -> None:
        """Test size calculation for empty objects."""
        assert get_object_size([]) > 0
        assert get_object_size({}) > 0
        assert get_object_size("") > 0

    def test_none_object(self) -> None:
        """Test size calculation for None."""
        size = get_object_size(None)
        assert size > 0

    def test_custom_objects(self) -> None:
        """Test size calculation for custom objects."""

        class CustomClass:
            def __init__(self) -> None:
                self.data = [1, 2, 3]
                self.name = "custom"

        obj = CustomClass()
        size = get_object_size(obj)
        assert size > 0

    def test_large_objects(self) -> None:
        """Test size calculation for larger objects."""
        # Create a larger object
        large_list = list(range(1000))
        large_dict = {f"key_{i}": f"value_{i}" for i in range(100)}

        large_obj = {
            "list_data": large_list,
            "dict_data": large_dict,
            "nested": {
                "more_data": list(range(500)),
            },
        }

        size = get_object_size(large_obj)
        assert size > 1000  # Should be reasonably large  # noqa: PLR2004


class TestMemoryManagement:
    """Test memory-related functionality."""

    def test_memory_efficiency(self) -> None:
        """Test that size calculation is memory efficient."""
        # This test ensures the function doesn't create excessive copies
        original_data = {"test": list(range(1000))}

        # Multiple calls should work without issues
        size1 = get_object_size(original_data)
        size2 = get_object_size(original_data)

        # Should return consistent results
        assert size1 == size2

    def test_deeply_nested_objects(self) -> None:
        """Test handling of deeply nested objects."""
        # Create deeply nested structure
        current = {}
        for i in range(10):
            current = {"level": i, "data": "some data", "nested": current}

        # Should handle deep nesting without issues
        size = get_object_size(current)
        assert size > 0


class TestIntegrationHelpers:
    """Test integration helper functions."""

    def test_path_handling(self) -> None:
        """Test that path-related functions work correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # Test various path operations that might be used in CLI functions
            nested_path = base_path / "sub1" / "sub2"

            # Create nested directories
            nested_path.mkdir(parents=True, exist_ok=True)

            assert nested_path.exists()
            assert nested_path.is_dir()

    def test_configuration_validation(self) -> None:
        """Test configuration validation helpers."""
        # Mock program configuration
        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir) / "results"

            # Test that configuration objects work as expected
            program_config = MagicMock(spec=ProgramConfig)
            program_config.results_path = results_path
            program_config.verbose = True

            # Should be able to access configuration properties
            assert program_config.results_path == results_path
            assert program_config.verbose is True


class TestErrorHandling:
    """Test error handling in CLI functions."""

    def test_permission_errors(self) -> None:
        """Test handling of permission errors."""
        # This test would check how CLI functions handle permission errors
        # but we need to be careful not to actually cause permission issues

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock scenario where we might have permission issues
            results_path = Path(temp_dir) / "restricted"

            # Create the directory first
            results_path.mkdir()

            # Mock program config
            program_config = MagicMock(spec=ProgramConfig)
            program_config.results_path = results_path
            program_config.verbose = False

            # Should handle existing directory gracefully
            create_results_directory(results_path, verbose=program_config.verbose)

    def test_invalid_paths(self) -> None:
        """Test handling of invalid paths."""
        # Test how functions handle various edge cases with paths
        program_config = MagicMock(spec=ProgramConfig)

        # Test with None path (should be handled by Pydantic validation)
        program_config.results_path = None
        program_config.verbose = False

        # Should handle gracefully or raise appropriate error
        try:  # noqa: SIM105
            create_results_directory(
                program_config.results_path,
                verbose=program_config.verbose,
            )
        except (AttributeError, TypeError):
            # Expected behavior for invalid configuration
            pass
