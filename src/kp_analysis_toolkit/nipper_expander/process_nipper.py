from typing import Any

import pandas as pd

from kp_analysis_toolkit.nipper_expander.models.nipper_row_data import NipperRowData
from kp_analysis_toolkit.nipper_expander.models.program_config import ProgramConfig
from kp_analysis_toolkit.utils.excel_utils import export_dataframe_to_excel


def process_nipper_csv(program_config: ProgramConfig) -> pd.DataFrame:
    """
    Process a nipper CSV file by expanding rows with multiple devices.

    Args:
        program_config: Configuration object with input_file and output_path properties

    Returns:
        pd.DataFrame: DataFrame containing the processed data

    """
    # Type assertion since validator ensures input_file is never None
    assert program_config.input_file is not None, "input_file is None"

    # Read the CSV file
    data_frame: pd.DataFrame = pd.read_csv(program_config.input_file)

    # Create a list to hold the expanded rows
    expanded_rows: list[dict[str, Any]] = []

    for _, row in data_frame.iterrows():
        # Validate and clean the devices data
        try:
            row_data = NipperRowData(devices=row.get("Devices", ""))
            devices_str: str = row_data.devices
        except Exception:  # noqa: BLE001
            # Handle invalid data gracefully
            devices_str: str = ""

        # Split the Devices column by any kind of line break
        devices: list[str] = devices_str.splitlines()
        devices = [d.strip() for d in devices if d.strip()]

        if len(devices) > 1:
            # Create a new row for each device
            for device in devices:
                new_row: dict[str, Any] = row.to_dict()
                new_row["Devices"] = device
                expanded_rows.append(new_row)
        else:
            # If there's only one device (or none), add the row as is
            row_dict: dict[str, Any] = row.to_dict()
            if devices:
                row_dict["Devices"] = devices[0]
            expanded_rows.append(row_dict)

    # Create a new DataFrame from the expanded rows
    result_data_frame: pd.DataFrame = pd.DataFrame(expanded_rows)

    # Write the result to an Excel file using the shared exporter
    export_dataframe_to_excel(
        result_data_frame,
        program_config.output_file,
        sheet_name="Expanded Nipper",
        title="Nipper Expanded Report - One row per device/finding",
        as_table=True,
    )

    return result_data_frame
