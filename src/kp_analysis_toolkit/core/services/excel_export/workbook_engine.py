"""Workbook engine for Excel export: provides ExcelWriter creation and file output logic."""

from pathlib import Path
from typing import Literal

import pandas as pd


class WorkbookEngine:
    """
    Default implementation of the WorkbookEngine protocol for Excel export.

    Provides a context manager for creating a pandas ExcelWriter using openpyxl.
    """

    def __init__(
        self,
        engine: Literal["openpyxl", "odf", "xlsxwriter", "auto"] = "openpyxl",
    ) -> None:
        """
        Initialize the workbook engine.

        Supports multiple engines:
        - "openpyxl" (default)
        - "odf"
        - "xlsxwriter"
        - "auto"

        Args:
            engine: The Excel writer engine to use

        """
        self.engine: Literal["openpyxl", "odf", "xlsxwriter", "auto"] = engine

    def create_writer(self, output_path: Path) -> pd.ExcelWriter:
        """
        Create a pandas ExcelWriter for the given output path.

        Creates the parent directory if it does not exist.

        Args:
            output_path: Path to the Excel file to write

        Returns:
            A pandas ExcelWriter context manager

        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return pd.ExcelWriter(output_path, engine=self.engine)
