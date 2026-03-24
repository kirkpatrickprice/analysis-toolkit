"""Tests for MultilineState and SearchState in file_centric_search.py."""
from pathlib import Path

import pytest

from kp_analysis_toolkit.process_scripts.file_centric_search import (
    MultilineState,
    SearchState,
)
from kp_analysis_toolkit.process_scripts.models.enums import OSFamilyType, ProducerType
from kp_analysis_toolkit.process_scripts.models.results.base import SearchResult
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.models.systems import Systems

win_file = Path("testdata/process_scripts/windows/windows10pro-cb19044-kp0.4.7.txt")


def _make_multiline_config(**kwargs) -> SearchConfig:
    """Create a minimal multiline-capable SearchConfig."""
    defaults = dict(
        name="test",
        regex=r"(?P<field1>\w+)",
        excel_sheet_name="Sheet1",
        field_list=["field1"],
        multiline=True,
    )
    defaults.update(kwargs)
    return SearchConfig(**defaults)


def _make_config(**kwargs) -> SearchConfig:
    """Create a minimal non-multiline SearchConfig."""
    defaults = dict(name="test", regex=r"\w+", excel_sheet_name="Sheet1")
    defaults.update(kwargs)
    return SearchConfig(**defaults)


def _make_system() -> Systems:
    return Systems(
        system_name="test-system",
        os_family=OSFamilyType.WINDOWS,
        producer=ProducerType.KPWINAUDIT,
        file=win_file,
        producer_version="1.0.0",
    )


def _make_result(text: str, line_num: int = 1) -> SearchResult:
    return SearchResult(
        system_name="test-system",
        line_number=line_num,
        matched_text=text,
        extracted_fields=None,
    )


class TestMultilineState:
    """Tests for MultilineState."""

    def test_reset_clears_all_state(self) -> None:
        """reset() restores every mutable attribute to its initial blank value."""
        config = _make_multiline_config()
        state = MultilineState(config)
        state.current_record = {"field1": "value1"}
        state.matching_lines = "some line"
        state.start_line_num = 5
        state.has_partial_match = True

        state.reset()

        assert state.current_record == {}
        assert state.matching_lines == ""
        assert state.start_line_num == 0
        assert state.has_partial_match is False

    def test_is_record_complete_false_when_no_fields_collected(self) -> None:
        """is_record_complete() returns False when current_record is empty."""
        config = _make_multiline_config(
            field_list=["field1", "field2"],
            regex=r"(?P<field1>\w+)|(?P<field2>\w+)",
        )
        state = MultilineState(config)
        assert state.is_record_complete() is False

    def test_is_record_complete_false_when_only_partial_fields(self) -> None:
        """is_record_complete() returns False when only some required fields are collected."""
        config = _make_multiline_config(
            field_list=["field1", "field2"],
            regex=r"(?P<field1>\w+)|(?P<field2>\w+)",
        )
        state = MultilineState(config)
        state.current_record = {"field1": "v1"}  # field2 still missing
        assert state.is_record_complete() is False

    def test_is_record_complete_true_when_all_fields_present(self) -> None:
        """is_record_complete() returns True when every field_list entry is in current_record."""
        config = _make_multiline_config(
            field_list=["field1", "field2"],
            regex=r"(?P<field1>\w+)|(?P<field2>\w+)",
        )
        state = MultilineState(config)
        state.current_record = {"field1": "v1", "field2": "v2"}
        assert state.is_record_complete() is True

    def test_should_emit_record_true_when_rs_delimiter_matches(self) -> None:
        """should_emit_record() returns True when the line matches rs_delimiter."""
        config = _make_multiline_config(rs_delimiter=r"---")
        state = MultilineState(config)
        assert state.should_emit_record("--- separator ---") is True

    def test_should_emit_record_false_when_rs_delimiter_does_not_match(self) -> None:
        """should_emit_record() returns False when the line does not match rs_delimiter."""
        config = _make_multiline_config(rs_delimiter=r"---")
        state = MultilineState(config)
        assert state.should_emit_record("normal line with no separator") is False

    def test_should_emit_record_true_when_no_delimiter_and_record_complete(self) -> None:
        """Without rs_delimiter, should_emit_record() delegates to is_record_complete()."""
        config = _make_multiline_config(field_list=["field1"])
        state = MultilineState(config)
        state.current_record = {"field1": "value"}
        assert state.should_emit_record("any line") is True

    def test_should_emit_record_false_when_no_delimiter_and_record_incomplete(self) -> None:
        """Without rs_delimiter, should_emit_record() is False until all fields collected."""
        config = _make_multiline_config(
            field_list=["field1", "field2"],
            regex=r"(?P<field1>\w+)|(?P<field2>\w+)",
        )
        state = MultilineState(config)
        state.current_record = {"field1": "value"}  # field2 still missing
        assert state.should_emit_record("any line") is False


class TestSearchState:
    """Tests for SearchState."""

    def test_add_result_deduplicates_when_unique_is_true(self) -> None:
        """add_result() drops duplicates (case-insensitive) when unique=True."""
        config = _make_config(unique=True)
        state = SearchState(config, _make_system())
        state.add_result(_make_result("Hello World"))
        state.add_result(_make_result("hello world"))  # same, different case
        assert len(state.results) == 1

    def test_add_result_allows_duplicates_when_unique_is_false(self) -> None:
        """add_result() keeps duplicates when unique=False."""
        config = _make_config(unique=False)
        state = SearchState(config, _make_system())
        state.add_result(_make_result("Hello World"))
        state.add_result(_make_result("hello world"))
        assert len(state.results) == 2  # noqa: PLR2004

    def test_add_result_stops_at_max_results(self) -> None:
        """add_result() stops accepting results once max_results is reached."""
        config = _make_config(max_results=2)
        state = SearchState(config, _make_system())
        for i in range(5):
            state.add_result(_make_result(f"unique line {i}"))
        assert len(state.results) == 2  # noqa: PLR2004
        assert state.is_complete is True

    def test_add_result_unlimited_when_max_results_is_negative_one(self) -> None:
        """add_result() never marks is_complete when max_results=-1."""
        config = _make_config(max_results=-1)
        state = SearchState(config, _make_system())
        for i in range(10):
            state.add_result(_make_result(f"unique line {i}"))
        assert len(state.results) == 10  # noqa: PLR2004
        assert state.is_complete is False

    def test_add_result_ignored_when_already_complete(self) -> None:
        """add_result() is a no-op once is_complete is True."""
        config = _make_config(max_results=1)
        state = SearchState(config, _make_system())
        state.add_result(_make_result("first"))
        assert state.is_complete is True
        state.add_result(_make_result("second"))
        assert len(state.results) == 1

    def test_process_line_skips_hash_comment_lines(self) -> None:
        """process_line() produces no results for lines matching should_skip_line()."""
        config = _make_config(regex=r"\w+")
        state = SearchState(config, _make_system())
        state.process_line("###[BEGIN] this is a comment", 1)
        assert len(state.results) == 0

    def test_process_line_produces_result_for_matching_line(self) -> None:
        """process_line() adds a result when the pattern matches a normal line."""
        config = _make_config(regex=r"hello")
        state = SearchState(config, _make_system())
        state.process_line("hello world", 1)
        assert len(state.results) == 1

    def test_process_line_produces_no_result_for_non_matching_line(self) -> None:
        """process_line() adds nothing when the pattern does not match."""
        config = _make_config(regex=r"nomatch_xyz")
        state = SearchState(config, _make_system())
        state.process_line("hello world", 1)
        assert len(state.results) == 0

    def test_process_line_is_noop_when_pattern_is_none(self) -> None:
        """process_line() returns immediately (no results) when self.pattern is None.

        The code path `if self.is_complete or not self.pattern: return` guards against
        operating without a compiled pattern. We exercise this guard directly.
        """
        config = _make_config(regex=r"\w+")
        state = SearchState(config, _make_system())
        state.pattern = None  # simulate failed compilation
        state.process_line("hello world", 1)
        assert len(state.results) == 0
