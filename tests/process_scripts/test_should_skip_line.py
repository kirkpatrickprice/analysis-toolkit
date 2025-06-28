#!/usr/bin/env python3
"""Test suite for the should_skip_line function using pytest."""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pytest

from kp_analysis_toolkit.process_scripts.search_engine import should_skip_line


class TestShouldSkipLine:
    """Test cases for the should_skip_line function."""

    def test_should_skip_specific_patterns(self) -> None:
        """Test that specific ### patterns are skipped."""
        lines_to_skip = [
            "###[BEGIN]: System_VersionInformation",
            "###Processing Command: some command",
            "###Running: uname -a",
            "###[END]: System_VersionInformation",
            "Some line with ###[BEGIN] in the middle",
            "Line with ###Processing Command: embedded",
            "Text ###Running: embedded command",
            "End line ###[END] marker",
        ]

        for line in lines_to_skip:
            assert should_skip_line(line), f"Expected to skip: {line}"

    def test_should_skip_general_hash_comments(self) -> None:
        """Test that any line with three or more hashes is skipped."""
        lines_to_skip = [
            "### This is a comment",
            "#### Four hashes comment",
            "##### Five hashes comment",
            "Comment ### line",
            "Start ### middle ### end",
            "#### (four hashes but no specific pattern)",
        ]

        for line in lines_to_skip:
            assert should_skip_line(line), f"Expected to skip: {line}"

    def test_should_not_skip_normal_lines(self) -> None:
        """Test that normal lines without ### patterns are not skipped."""
        lines_not_to_skip = [
            "System_VersionInformation::Linux olorin 5.15.0-139-generic",
            "Normal line without patterns",
            "Line with ## (only two hashes)",
            "Some text with BEGIN inside",
            "Regular log entry Processing Command: xyz",
            "Command Running: something",
            "END of file marker",
            "[BEGIN] without hashes",
            "Processing Command: without hashes",
            "Running: without hashes",
            "[END] without hashes",
        ]

        for line in lines_not_to_skip:
            assert not should_skip_line(line), f"Expected NOT to skip: {line}"

    def test_edge_cases(self) -> None:
        """Test edge cases for the skip function."""
        # Empty line
        assert not should_skip_line("")

        # Just two hashes
        assert not should_skip_line("##")

        # Exactly three hashes
        assert should_skip_line("###")

        # Whitespace around hashes
        assert should_skip_line("   ###   ")
        assert should_skip_line("\t###\t")

    def test_real_world_examples(self) -> None:
        """Test with real examples from the test data."""
        # These should be skipped (from actual test data)
        skip_examples = [
            "###Collecting some basic information about the system.",
            "###Running: uname -a",
            "###System Type:",
            "###Node:",
            "###Machine:",
        ]

        for line in skip_examples:
            assert should_skip_line(line), f"Expected to skip real example: {line}"

        # These should not be skipped (from actual test data)
        no_skip_examples = [
            "System_VersionInformation::Linux olorin 5.15.0-139-generic",
            "System Report for olorin",
            "This report was generated Sun May 25 08:08:06 AM EDT 2025",
            "KPNIXVERSION: 0.6.22",
        ]

        for line in no_skip_examples:
            assert not should_skip_line(line), (
                f"Expected NOT to skip real example: {line}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
