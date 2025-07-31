from pathlib import Path

from kp_analysis_toolkit.process_scripts.models.base import KPATBaseModel


class WorkflowStatisitics(KPATBaseModel):
    """Result of process scripts workflow execution."""

    systems_processed: int
    total_systems_by_os_type: dict[str, int]
    total_systems_by_distro: dict[str, int]
    searches_executed: int
    total_results: int
    exported_files: dict[str, Path]
    execution_time: float
    errors: list[str]


class SearchStatistics(KPATBaseModel):
    """Statistics about search execution."""

    unique_systems_found: int
    systems_with_matches: int
    total_matches: int
    searches_with_extracted_fields: int
