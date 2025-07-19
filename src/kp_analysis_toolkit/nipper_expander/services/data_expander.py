"""Service to expand data rows into one row per device."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from kp_analysis_toolkit.core.services.rich_output import RichOutputService
from kp_analysis_toolkit.nipper_expander.protocols import RowExpanderService

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.services.csv_processing import CSVProcessor
    from kp_analysis_toolkit.core.services.rich_output import RichOutputService
    from kp_analysis_toolkit.models.types import DisplayableValue


class DefaultRowExpander(RowExpanderService):
    """Service for expanding multi-value data fields into separate rows."""

    def __init__(
        self,
        rich_output: RichOutputService,
        csv_processor: CSVProcessor,
    ) -> None:
        """
        Initialize the DefaultRowExpander.

        Args:
            rich_output: Service for rich terminal output
            csv_processor: Service for processing CSV files

        """
        self.rich_output: RichOutputService = rich_output
        self.csv_processor: CSVProcessor = csv_processor

    def expand_device_rows(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """
        Expand rows with multi-line device data into individual rows.

        Args:
            data_frame: DataFrame containing the data to expand

        Returns:
            pd.DataFrame: DataFrame with expanded rows

        """
        expanded_rows: list[dict[str, DisplayableValue]] = []

        for _, row in data_frame.iterrows():
            devices_list: list[str] = self._split_devices(
                self._validate_devices(
                    row.get("Devices", ""),
                ),
            )

            if len(devices_list) > 1:
                # Create a new row for each device
                for device in devices_list:
                    new_row: dict[str, DisplayableValue] = self._create_expanded_row(
                        row,
                        device,
                    )
                    expanded_rows.append(new_row)
            elif devices_list:
                # If there's only one device, keep the original row
                expanded_rows.append(row)
            else:
                # If no devices, remove the row
                continue

        return pd.DataFrame(expanded_rows)

    def _validate_devices(
        self,
        devices: str,
    ) -> str:
        """
        Validate and clean a list of device names.

        Args:
            devices: String containing device names separated by line breaks

        Returns:
            str: Cleaned string of device names

        """
        if pd.isna(devices) or devices is None:
            return ""
        return str(devices).strip()

    def _split_devices(self, devices_str: str) -> list[str]:
        """Split device string by line breaks and clean whitespace."""
        return [self._clean_device(d) for d in devices_str.splitlines()]

    def _clean_device(
        self,
        device_str: str,
    ) -> str:
        """
        Clean the device string.

        Args:
            device_str: String containing a device name
        Returns:
            str: Cleaned device name

        """
        if not device_str:
            return ""
        return device_str.strip()

    def _create_expanded_row(
        self,
        original_row: pd.Series,
        device: str,
    ) -> dict[str, DisplayableValue]:
        """Create a new row for a single device."""
        new_row: dict[str, DisplayableValue] = original_row.to_dict()
        new_row["Devices"] = device
        return new_row
