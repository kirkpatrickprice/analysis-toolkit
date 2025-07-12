"""Sheet management utilities for Excel export."""

import re

from kp_analysis_toolkit.core.services.excel_export.protocols import SheetNameSanitizer


class DefaultSheetNameSanitizer(SheetNameSanitizer):
    """Default implementation for sheet name sanitization and column letter conversion."""

    def sanitize_sheet_name(self, name: str) -> str:
        """
        Sanitize a string to be used as an Excel sheet name.

        Args:
            name: The string to sanitize

        Returns:
            A string safe to use as an Excel sheet name

        """
        if not name:
            return "Unnamed_Sheet"

        sanitized: str = re.sub(r"[\\/*\[\]:?]", "_", name)
        sanitized = re.sub(r"\s+", "_", sanitized)
        sanitized = sanitized.strip("_")
        if not sanitized:
            sanitized = "Unnamed_Sheet"
        max_sheet_name_length = 31
        if len(sanitized) > max_sheet_name_length:
            sanitized = sanitized[: max_sheet_name_length - 3] + "..."
        return sanitized

    def get_column_letter(self, col_num: int) -> str:
        """
        Convert column number to Excel column letter.

        Args:
            col_num: Column number (1-indexed)

        Returns:
            Excel column letter(s)

        """
        result: str = ""
        while col_num > 0:
            col_num -= 1
            result = chr(col_num % 26 + ord("A")) + result
            col_num //= 26
        return result
