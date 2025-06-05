from pydantic import Field, computed_field

from kp_analysis_toolkit.process_scripts.models.base import KPATBaseModel
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig


class SearchResult(KPATBaseModel):
    """Individual search result."""

    system_name: str
    line_number: int
    matched_text: str
    extracted_fields: dict[str, str | None | float] | None = None

    line_number: int = Field(gt=0, description="Line number must be a positive integer")


class SearchResults(KPATBaseModel):
    """Collection of results for a search configuration."""

    search_config: SearchConfig
    results: list[SearchResult]

    @computed_field
    @property
    def result_count(self) -> int:
        """Return the number of results."""
        return len(self.results)

    @computed_field
    @property
    def unique_systems(self) -> int:
        """Return the number of unique systems that had matches."""
        return len({result.system_name for result in self.results})

    @computed_field
    @property
    def has_extracted_fields(self) -> bool:
        """Check if any results have extracted fields."""
        return any(result.extracted_fields for result in self.results)
