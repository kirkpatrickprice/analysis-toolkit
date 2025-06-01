from kp_analysis_toolkit.process_scripts.models.base import KPATBaseModel


class SearchStatistics(KPATBaseModel):
    """Statistics about search execution."""

    total_searches: int
    searches_with_results: int
    searches_without_results: int
    total_matches: int
    average_matches_per_search: float
    unique_systems_found: int
    systems_with_matches: int
    searches_with_extracted_fields: int
    top_searches_by_results: list[tuple[str, int]]
