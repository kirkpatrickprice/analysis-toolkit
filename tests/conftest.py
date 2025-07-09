"""Shared pytest configuration and fixtures."""

import os
import re
from collections.abc import Generator
from pathlib import Path
from re import Pattern
from typing import Any

import pytest
from click.testing import CliRunner

from tests.fixtures import *  # noqa: F403

# =============================================================================
# SESSION-SCOPED INFRASTRUCTURE FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def testdata_dir() -> Path:
    """Return the testdata directory path."""
    return Path(__file__).parent.parent / "testdata"


@pytest.fixture(scope="session")
def temp_workspace(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a temporary workspace for tests."""
    return tmp_path_factory.mktemp("test_workspace")


# =============================================================================
# CROSS-DOMAIN CLI FIXTURES
# =============================================================================


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


# =============================================================================
# CROSS-DOMAIN ASSERTION UTILITIES
# =============================================================================


def assert_console_width_tolerant(
    actual_width: int,
    expected_width: int,
    tolerance: int = 1,
) -> None:
    """
    Assert console width with tolerance for CI environment variations.

    GitHub Actions Windows runners sometimes report console width as 99 instead of 100,
    or 79 instead of 80, due to terminal detection quirks. This function provides a
    tolerant assertion that accounts for these CI environment variations.

    Args:
        actual_width: The actual console width reported
        expected_width: The expected console width
        tolerance: The allowed difference (default 1)

    Raises:
        AssertionError: If the width difference exceeds tolerance

    """
    width_diff: int = abs(actual_width - expected_width)
    assert width_diff <= tolerance, (
        f"Console width {actual_width} differs from expected {expected_width} "
        f"by {width_diff} (tolerance: {tolerance}). "
        f"This may be due to CI environment terminal detection quirks."
    )


def assert_valid_encoding(
    actual_encoding: str | None,
    expected_encodings: list[str] | str,
) -> None:
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
        # Try exact match first, then case-insensitive
        if item in clean_output:
            continue

        # Case-insensitive fallback
        if item.lower() in clean_output.lower():
            continue

        # If neither works, fail with helpful message
        pytest.fail(
            f"Expected '{item}' to be in CLI output. "
            f"Clean output was: {clean_output[:500]}...",
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
    # Strip ANSI codes
    ansi_escape: Pattern[str] = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    clean_output: str = ansi_escape.sub("", output)

    # Help output should contain Usage and command description
    assert "Usage:" in clean_output, (
        f"Expected 'Usage:' in help output. Got: {clean_output[:500]}..."
    )

    # Use case-insensitive search for command descriptions since Rich may change case
    # Also try partial word matching for more flexibility
    min_word_length = 3  # Only check meaningful words (avoid articles, etc.)
    description_found = command_description.lower() in clean_output.lower() or any(
        word.lower() in clean_output.lower()
        for word in command_description.split()
        if len(word) > min_word_length
    )

    assert description_found, (
        f"Expected command description related to '{command_description}' in help output. "
        f"Clean output was: {clean_output[:500]}..."
    )


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

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
            normalized_dir: str = relative_dir.replace("\\", "/")

            # Apply markers based on directory patterns
            for dir_pattern, markers in directory_markers.items():
                if _path_matches_pattern(normalized_dir, dir_pattern):
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


# Alternative implementation for exact directory matching (NOT CURRENTLY USED, but retained for possible future use):
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
