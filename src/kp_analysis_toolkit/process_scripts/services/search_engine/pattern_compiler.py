"""Pattern compiler service implementation using dependency injection."""

from __future__ import annotations

import re


class DefaultPatternCompiler:
    """Service for compiling and managing regex patterns using DI services."""

    def compile_pattern(self, regex: str) -> re.Pattern[str]:
        """
        Compile a regex pattern with error handling.

        Args:
            regex: Regex pattern string to compile

        Returns:
            Compiled regex pattern

        Raises:
            ValueError: If the regex pattern is invalid

        """
        try:
            return re.compile(regex)
        except re.error as e:
            msg = f"Invalid regex pattern '{regex}': {e}"
            raise ValueError(msg) from e
