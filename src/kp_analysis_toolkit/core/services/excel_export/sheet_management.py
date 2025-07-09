"""Sheet management implementations for the Excel export service."""

from __future__ import annotations

import re

from kp_analysis_toolkit.core.services.excel_export.protocols import (
    ExcelUtilities,
    SheetNameSanitizer,
)


class StandardSheetNameSanitizer(SheetNameSanitizer):
    """Standard implementation for Excel sheet name sanitization."""

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

        # Remove invalid characters and replace with underscores
        sanitized: str = re.sub(r"[\\/*\[\]:?]", "_", name)

        # Remove extra spaces and replace with underscores
        sanitized = re.sub(r"\s+", "_", sanitized)

        # Remove leading/trailing underscores
        sanitized = sanitized.strip("_")

        # Ensure we have something
        if not sanitized:
            sanitized = "Unnamed_Sheet"

        # Limit to 31 characters (Excel limitation)
        max_sheet_name_length = 31
        if len(sanitized) > max_sheet_name_length:
            sanitized = sanitized[: max_sheet_name_length - 3] + "..."

        return sanitized


class StandardExcelUtilities(ExcelUtilities):
    """Standard implementation for Excel utility functions."""

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

    def set_table_alignment(self, worksheet, table_range: str) -> None:
        # Implementation should be provided elsewhere if needed
        raise NotImplementedError(
            "set_table_alignment is not implemented in StandardExcelUtilities.",
        )
