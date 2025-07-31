import io
import re
from typing import IO, TYPE_CHECKING
from unittest.mock import Mock

import pytest

from kp_analysis_toolkit.process_scripts.models.search.merge_fields import SearchConfig
from kp_analysis_toolkit.process_scripts.models.results.system import Systems
from kp_analysis_toolkit.process_scripts.search_engine import search_multiline

if TYPE_CHECKING:
    from kp_analysis_toolkit.process_scripts.models.results.search import SearchResult


class TestSearchMultiline:
    """Tests for the search_multiline function."""

    @pytest.fixture
    def mock_file_content(self) -> IO[str]:
        """Create a mock file handle with test content."""
        content: str = (
            "START RECORD 1\n"
            "User: user1\n"
            "ID: 12345\n"
            "END RECORD\n"
            "START RECORD 2\n"
            "User: user2\n"
            "ID: 67890\n"
            "END RECORD\n"
        )
        return io.StringIO(content)

    def test_basic_multiline_search(
        self,
        mock_linux_system: Systems,
        mock_file_content: IO[str],
    ) -> None:
        """Test basic multiline search with field extraction."""
        # Setup
        search_config: SearchConfig = Mock(spec=SearchConfig)
        search_config.name = "test-search"
        search_config.multiline = True
        search_config.rs_delimiter = "END RECORD"
        search_config.field_list = ["user", "id"]
        search_config.max_results = 0
        search_config.merge_fields = []

        pattern: re.Pattern[str] = re.compile(
            r"User: (?P<user>\w+)|ID: (?P<id>\d+)",
            re.IGNORECASE,
        )

        # Execute
        results: list[SearchResult] = search_multiline(
            search_config,
            mock_linux_system,
            mock_file_content,
            pattern,
        )

        # Verify
        assert len(results) == 2, "Should find two records"  # noqa: PLR2004

        # First record
        assert results[0].system_name == "test-linux-system"
        assert "User: user1" in results[0].matched_text
        assert "ID: 12345" in results[0].matched_text
        assert results[0].extracted_fields is not None
        assert results[0].extracted_fields.get("user") == "user1"
        assert results[0].extracted_fields.get("id") == "12345"

        # Second record
        assert results[1].system_name == "test-linux-system"
        assert "User: user2" in results[1].matched_text
        assert "ID: 67890" in results[1].matched_text
        assert results[1].extracted_fields is not None
        assert results[1].extracted_fields.get("user") == "user2"
        assert results[1].extracted_fields.get("id") == "67890"

    def test_field_list_completion(self, mock_linux_system: Systems) -> None:
        """Test multiline search that completes when all fields are found."""
        # Setup
        search_config: SearchConfig = Mock(spec=SearchConfig)
        search_config.name = "field-completion-test"
        search_config.multiline = True
        search_config.rs_delimiter = None  # No delimiter, rely on field completion
        search_config.field_list = ["user", "id"]
        search_config.max_results = 0
        search_config.merge_fields = []

        # Create content where records are not explicitly delimited
        content: str = (
            "Some header info\n"
            "User: user1\n"
            "Other information\n"
            "ID: 12345\n"
            "Separator line\n"
            "User: user2\n"
            "More text\n"
            "ID: 67890\n"
        )
        file_handle: IO[str] = io.StringIO(content)

        pattern: re.Pattern[str] = re.compile(
            r"User: (?P<user>\w+)|ID: (?P<id>\d+)",
            re.IGNORECASE,
        )

        # Execute
        results: list[SearchResult] = search_multiline(
            search_config,
            mock_linux_system,
            file_handle,
            pattern,
        )

        # Verify
        assert len(results) == 2, "Should find two complete records"  # noqa: PLR2004
        assert results[0].extracted_fields.get("user") == "user1"
        assert results[0].extracted_fields.get("id") == "12345"
        assert results[1].extracted_fields.get("user") == "user2"
        assert results[1].extracted_fields.get("id") == "67890"

    def test_max_results_limit(
        self,
        mock_linux_system: Systems,
        mock_file_content: IO[str],
    ) -> None:
        """Test that max_results properly limits the number of results."""
        # Setup
        search_config: SearchConfig = Mock(spec=SearchConfig)
        search_config.name = "max-results-test"
        search_config.multiline = True
        search_config.rs_delimiter = "END RECORD"
        search_config.field_list = ["user", "id"]
        search_config.max_results = 1  # Only return one result
        search_config.merge_fields = []

        pattern: re.Pattern[str] = re.compile(
            r"User: (?P<user>\w+)|ID: (?P<id>\d+)",
            re.IGNORECASE,
        )

        # Execute
        results: list[SearchResult] = search_multiline(
            search_config,
            mock_linux_system,
            mock_file_content,
            pattern,
        )

        # Verify
        assert len(results) == 1, "Should find only one record due to max_results"
        assert results[0].extracted_fields.get("user") == "user1"
        assert results[0].extracted_fields.get("id") == "12345"

    def test_no_matches(self, mock_linux_system: Systems) -> None:
        """Test behavior when no matches are found."""
        # Setup
        search_config: SearchConfig = Mock(spec=SearchConfig)
        search_config.name = "no-matches-test"
        search_config.multiline = True
        search_config.rs_delimiter = "END RECORD"
        search_config.field_list = ["user", "id"]
        search_config.max_results = 0
        search_config.merge_fields = []

        content: str = (
            "This content has no matching patterns\nSecond line with no matches"
        )
        file_handle: IO[str] = io.StringIO(content)

        pattern: re.Pattern[str] = re.compile(
            r"User: (?P<user>\w+)|ID: (?P<id>\d+)",
            re.IGNORECASE,
        )

        # Execute
        results: list[SearchResult] = search_multiline(
            search_config,
            mock_linux_system,
            file_handle,
            pattern,
        )

        # Verify
        assert len(results) == 0, "Should find no records"
