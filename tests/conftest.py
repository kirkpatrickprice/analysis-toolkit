# tests/conftest.py
"""Shared pytest configuration and fixtures."""

import os
from collections.abc import Generator
from pathlib import Path
from re import Pattern
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from kp_analysis_toolkit.process_scripts.models.enums import OSFamilyType, ProducerType
from kp_analysis_toolkit.process_scripts.models.systems import Systems

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.containers.core import CoreContainer


@pytest.fixture(scope="session")
def testdata_dir() -> Path:
    """Return the testdata directory path."""
    return Path(__file__).parent.parent / "testdata"


@pytest.fixture(scope="session")
def temp_workspace(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a temporary workspace for tests."""
    return tmp_path_factory.mktemp("test_workspace")


@pytest.fixture
def mock_file_system() -> Generator[dict[str, MagicMock], Any, None]:
    """
    Mock file system operations for testing.

    Returns a dictionary of mocked pathlib.Path methods:
    - exists: Mock for Path.exists()
    - is_file: Mock for Path.is_file()
    - is_dir: Mock for Path.is_dir()
    - mkdir: Mock for Path.mkdir()
    """
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("pathlib.Path.is_file") as mock_is_file,
        patch("pathlib.Path.is_dir") as mock_is_dir,
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        # Default behavior - everything exists
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_is_dir.return_value = True
        mock_mkdir.return_value = None

        yield {
            "exists": mock_exists,
            "is_file": mock_is_file,
            "is_dir": mock_is_dir,
            "mkdir": mock_mkdir,
        }


@pytest.fixture
def mock_linux_system() -> Systems:
    """Create a mock Linux Systems object for testing."""
    system: Systems = Mock(spec=Systems)
    system.system_name = "test-linux-system"
    system.os_family = OSFamilyType.LINUX
    system.producer = ProducerType.KPNIXAUDIT
    system.producer_version = "1.0.0"
    system.file = Mock()
    system.file.name = "test-system.log"
    return system


@pytest.fixture
def mock_windows_system() -> Systems:
    """Create a mock Windows Systems object for testing."""
    system: Systems = Mock(spec=Systems)
    system.system_name = "test-windows-system"
    system.os_family = OSFamilyType.WINDOWS
    system.producer = ProducerType.KPWINAUDIT
    system.producer_version = "1.0.0"
    system.file = Mock()
    system.file.name = "test-system.log"
    return system


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI runner for testing CLI commands."""
    return CliRunner()


@pytest.fixture
def isolated_cli_runner(tmp_path: Path) -> CliRunner:
    """Create an isolated CLI runner with temporary working directory."""
    return CliRunner(env={"HOME": str(tmp_path)})


@pytest.fixture
def isolated_console_env() -> Generator[None, Any, None]:
    """
    Isolate console environment variables that could affect Rich Console width detection.

    This fixture ensures that tests involving console width settings are not affected
    by CI environment variables like COLUMNS, LINES, etc.
    """
    # Environment variables that could affect console behavior
    console_env_vars = ["COLUMNS", "LINES", "TERM", "FORCE_COLOR", "NO_COLOR"]

    # Store original values
    original_values = {}
    for var in console_env_vars:
        if var in os.environ:
            original_values[var] = os.environ[var]
            del os.environ[var]

    try:
        yield
    finally:
        # Restore original values
        for var, value in original_values.items():
            os.environ[var] = value


@pytest.fixture
def mock_di_container() -> MagicMock:
    """
    Mock dependency injection container for testing.

    Returns a mock container that can be used for testing DI functionality
    without requiring actual DI initialization.
    """
    mock_container = MagicMock()
    mock_service = MagicMock()

    # Setup default behavior
    mock_container.file_processing_service.return_value = mock_service
    mock_container.encoding_detector.return_value = MagicMock()
    mock_container.hash_generator.return_value = MagicMock()
    mock_container.file_validator.return_value = MagicMock()

    return mock_container


@pytest.fixture
def mock_file_processing_service() -> MagicMock:
    """Create a mock FileProcessingService for testing."""
    from kp_analysis_toolkit.core.services.file_processing import FileProcessingService

    service = Mock(spec=FileProcessingService)

    # Setup default behaviors
    service.process_file.return_value = {
        "encoding": "utf-8",
        "hash": "mock_hash_value",
    }
    service.detect_encoding.return_value = "utf-8"
    service.generate_hash.return_value = "mock_hash_value"

    return service


@pytest.fixture
def isolated_di_env() -> Generator[None, Any, None]:
    """
    Isolate dependency injection state for testing.

    This fixture ensures that DI state changes in tests don't affect other tests
    by clearing any existing DI state before and after the test.
    """
    # Clear any existing DI state before test
    try:
        from kp_analysis_toolkit.utils.di_state import clear_di_state

        clear_di_state()
    except (ImportError, AttributeError):
        # DI state utilities may not be fully implemented yet
        pass

    try:
        yield
    finally:
        # Clear DI state after test
        try:
            from kp_analysis_toolkit.utils.di_state import clear_di_state

            clear_di_state()
        except (ImportError, AttributeError):
            # DI state utilities may not be fully implemented yet
            pass


@pytest.fixture
def mock_core_container() -> MagicMock:
    """Create a mock CoreContainer for testing file processing integration."""
    from kp_analysis_toolkit.core.containers.core import CoreContainer

    container = Mock(spec=CoreContainer)
    mock_config = MagicMock()
    mock_rich_output = MagicMock()

    # Setup configuration mock
    mock_config.verbose.from_value = Mock()
    mock_config.quiet.from_value = Mock()
    mock_config.console_width.from_value = Mock()
    mock_config.force_terminal.from_value = Mock()
    mock_config.stderr_enabled.from_value = Mock()

    # Setup property access
    mock_config.verbose.return_value = False
    mock_config.quiet.return_value = False
    mock_config.console_width.return_value = 120
    mock_config.force_terminal.return_value = True
    mock_config.stderr_enabled.return_value = True

    # Setup rich output
    mock_rich_output.verbose = False
    mock_rich_output.quiet = False

    container.config = mock_config
    container.rich_output.return_value = mock_rich_output

    return container


@pytest.fixture
def real_core_container() -> "CoreContainer":
    """
    Create a real CoreContainer for dependency injection tests.

    This fixture provides a properly configured CoreContainer instance
    that can be used for testing actual DI behavior without mocks.
    """
    from kp_analysis_toolkit.core.containers.core import CoreContainer

    container = CoreContainer()

    # Configure with sensible defaults for testing
    container.config.verbose.from_value(False)
    container.config.quiet.from_value(False)
    container.config.console_width.from_value(120)
    container.config.force_terminal.from_value(True)
    container.config.stderr_enabled.from_value(True)

    return container


@pytest.fixture
def mock_di_state() -> Generator[MagicMock, Any, None]:
    """
    Mock DI state for testing file processing service integration.

    This fixture provides a mock DI state that can be configured for different
    test scenarios involving dependency injection.
    """
    # Create a mock service
    mock_service = MagicMock()
    mock_service.detect_encoding.return_value = "utf-8"
    mock_service.generate_hash.return_value = "mock_hash_value"
    mock_service.process_file.return_value = {
        "encoding": "utf-8",
        "hash": "mock_hash_value",
        "path": "mock_path",
    }

    # Mock the DI state getter functions
    with (
        patch("kp_analysis_toolkit.utils.get_file_encoding._get_file_processing_service") as mock_encoding_getter,
        patch("kp_analysis_toolkit.utils.hash_generator._get_file_processing_service") as mock_hash_getter,
    ):
        # Configure mocks to return the service
        mock_encoding_getter.return_value = mock_service
        mock_hash_getter.return_value = mock_service

        yield {
            "service": mock_service,
            "encoding_getter": mock_encoding_getter,
            "hash_getter": mock_hash_getter,
        }


@pytest.fixture
def di_initialized() -> Generator[None, Any, None]:
    """
    Initialize dependency injection for tests that need it.

    This fixture ensures DI is properly initialized and cleaned up.
    """
    from kp_analysis_toolkit.core.containers.application import initialize_dependency_injection

    # Initialize DI with test-friendly settings
    initialize_dependency_injection(verbose=False, quiet=True)

    try:
        yield
    finally:
        # Clean up DI state if needed
        try:
            from kp_analysis_toolkit.core.containers.application import container

            # Reset container state
            container.reset_singletons()
        except (ImportError, AttributeError):
            # Container reset may not be available
            pass


@pytest.fixture
def container_initialized() -> Generator[None, Any, None]:
    """
    Initialize DI container with proper configuration for container testing.

    This fixture is specifically for tests that need to examine container
    behavior, wiring, and configuration. It ensures the container is properly
    configured before testing container-specific functionality.
    """
    from kp_analysis_toolkit.core.containers.application import initialize_dependency_injection

    # Initialize with explicit configuration for container testing
    initialize_dependency_injection(
        verbose=False,
        quiet=True,
        console_width=120,
        force_terminal=True,
        stderr_enabled=True,
    )

    try:
        yield
    finally:
        # Clean up container state
        try:
            from kp_analysis_toolkit.core.containers.application import container

            container.reset_singletons()
        except (ImportError, AttributeError):
            pass


# Automatic test marking based on directory structure


def pytest_collection_modifyitems(
    config: pytest.Config,  # noqa: ARG001
    items: list[pytest.Item],
) -> None:
    """
    Automatically mark tests based on their directory structure.

    This function automatically applies pytest markers to tests based on their location
    within the test directory structure. It's designed to be easily extensible for
    future marking needs.

    Args:
        config: pytest configuration object (unused but required by pytest)
        items: list of collected test items

    """
    # Define directory-based marking rules
    # Each entry maps a directory path pattern to a list of markers to apply
    directory_markers: dict[str, list[str]] = {
        # Mark all regex tests as slow (they take ~54 seconds for 169 tests)
        "unit/process_scripts/regex": ["slow"],
        # Future extensions can be added here:
        # "integration/workflows": ["integration", "slow"],
        # "e2e": ["e2e", "slow"],
        # "performance": ["performance", "slow"],
        # "unit/large_datasets": ["slow"],
    }

    # Process each test item
    for item in items:
        # Get the test file path relative to the tests directory
        test_file_path = Path(item.fspath)
        tests_dir: Path = Path(__file__).parent  # This is the tests/ directory

        try:
            # Get relative path from tests/ directory
            relative_path: Path = test_file_path.relative_to(tests_dir)
            relative_dir = str(relative_path.parent)

            # Normalize path separators for cross-platform compatibility
            relative_dir: str = relative_dir.replace("\\", "/")

            # Apply markers based on directory patterns
            for dir_pattern, markers in directory_markers.items():
                if _path_matches_pattern(relative_dir, dir_pattern):
                    for marker_name in markers:
                        # Add the marker to the test item
                        marker = getattr(pytest.mark, marker_name)
                        item.add_marker(marker)

        except ValueError:
            # Path is not relative to tests directory - skip marking
            continue


def _path_matches_pattern(path: str, pattern: str) -> bool:
    """
    Check if a path matches a given pattern.

    This function supports exact matches and can be extended to support
    more sophisticated pattern matching in the future.

    Args:
        path: The path to check (e.g., "unit/process_scripts/regex/windows")
        pattern: The pattern to match against (e.g., "unit/process_scripts/regex")

    Returns:
        True if the path matches the pattern, False otherwise

    """
    # For now, use startswith for directory matching
    # This allows subdirectories to inherit markers from parent directories
    return path.startswith(pattern)


# Alternative implementation for exact directory matching:
def _path_matches_pattern_exact(path: str, pattern: str) -> bool:
    """
    Check if a path exactly matches a pattern or is a subdirectory of it.

    This is an alternative implementation that can be used if more precise
    control over directory matching is needed.
    """
    path_parts: list[str] = path.split("/")
    pattern_parts: list[str] = pattern.split("/")

    # Pattern must be shorter or equal length to path
    if len(pattern_parts) > len(path_parts):
        return False

    # All pattern parts must match the beginning of the path
    return path_parts[: len(pattern_parts)] == pattern_parts


def assert_valid_encoding(actual_encoding: str | None, expected_encodings: list[str] | str) -> None:
    """
    Assert that the actual encoding is one of the expected valid encodings.

    This helper function handles the fact that ASCII-compatible text can be
    legitimately detected as either 'ascii' or 'utf-8' by charset-normalizer.

    Args:
        actual_encoding: The encoding detected by the system
        expected_encodings: Either a single encoding string or list of valid encodings.
                          If a single string is provided and it's 'utf-8', both 'utf-8'
                          and 'ascii' will be considered valid.

    Example:
        # Accept both ascii and utf-8 for ASCII-compatible content
        assert_valid_encoding(result["encoding"], "utf-8")

        # Accept specific encodings
        assert_valid_encoding(result["encoding"], ["latin-1", "iso-8859-1"])
    """
    if isinstance(expected_encodings, str):
        if expected_encodings == "utf-8":
            # For UTF-8, also accept ASCII as valid since ASCII-compatible text
            # can be legitimately detected as either encoding
            valid_encodings: list[str] = ["utf-8", "ascii"]
        else:
            valid_encodings = [expected_encodings]
    else:
        valid_encodings = expected_encodings

    assert actual_encoding in valid_encodings, (
        f"Expected encoding to be one of {valid_encodings}, but got {actual_encoding!r}"
    )


def assert_rich_output_contains(output: str, expected_content: str | list[str]) -> None:
    """
    Assert that Rich-formatted CLI output contains expected content.

    This helper function strips ANSI codes and handles Rich formatting to test
    for content presence without being brittle to formatting changes.

    Args:
        output: The raw CLI output (may contain ANSI codes)
        expected_content: String or list of strings that should be present

    Example:
        # Test for single content
        assert_rich_output_contains(result.output, "KP Analysis Toolkit")

        # Test for multiple content items
        assert_rich_output_contains(result.output, [
            "KP Analysis Toolkit",
            "Version",
            "process-scripts"
        ])
    """
    import re

    # Strip ANSI escape sequences from the output
    ansi_escape: Pattern[str] = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    clean_output: str = ansi_escape.sub("", output)

    # Normalize whitespace for more reliable matching
    clean_output = " ".join(clean_output.split())

    if isinstance(expected_content, str):
        expected_items: list[str] = [expected_content]
    else:
        expected_items = expected_content

    for item in expected_items:
        assert item in clean_output, (
            f"Expected '{item}' to be in CLI output. "
            f"Clean output was: {clean_output[:200]}..."
        )


def assert_rich_version_output(output: str) -> None:
    """
    Assert that Rich-formatted version output contains expected elements.

    This helper specifically validates version command output which uses
    Rich panels and tables.

    Args:
        output: The raw CLI output from version command
    """
    # Check for key version output elements
    assert_rich_output_contains(
        output,
        [
            "KP Analysis Toolkit",
            "Version",
            "process-scripts",
            "nipper-expander",
            "rtf-to-text",
        ],
    )


def assert_rich_help_output(output: str, command_description: str) -> None:
    """
    Assert that Rich-formatted help output contains expected elements.

    Args:
        output: The raw CLI output from help command
        command_description: The expected command description
    """
    import re

    # Strip ANSI codes
    ansi_escape: Pattern[str] = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    clean_output: str = ansi_escape.sub("", output)

    # Help output should contain Usage and command description
    assert "Usage:" in clean_output
    # Use case-insensitive search for command descriptions since Rich may change case
    assert (
        command_description.lower() in clean_output.lower()
    ) or any(
        word in clean_output.lower() for word in command_description.lower().split()
    ), f"Expected command description related to '{command_description}' in help output"
