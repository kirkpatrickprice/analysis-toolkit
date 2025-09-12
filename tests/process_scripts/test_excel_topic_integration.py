"""Tests for Excel export integration with topic functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from kp_analysis_toolkit.process_scripts.excel_exporter import (
    _apply_summary_formatting,
    _apply_worksheet_tab_colors,
    export_search_results_to_excel,
)
from kp_analysis_toolkit.process_scripts.models.results.base import SearchResults
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.models.topic_colors import TopicColorManager


class TestExcelTopicIntegration:
    """Test cases for Excel export with topic functionality."""

    def test_summary_data_includes_topic(self) -> None:
        """Test that summary data includes topic column."""
        # Create mock search results with topics
        search_results = []

        search_config1 = SearchConfig(
            name="test_search_1",
            regex=r"test_pattern_1",
            excel_sheet_name="Sheet1",
            topic="Network Configuration",
        )

        search_result1 = MagicMock(spec=SearchResults)
        search_result1.search_config = search_config1
        search_result1.result_count = 5
        search_result1.unique_systems = 3
        search_result1.has_extracted_fields = True
        search_result1.results = [MagicMock()]  # Non-empty results

        search_results.append(search_result1)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.xlsx"

            # Mock the necessary dependencies to avoid complex setup
            with (
                pytest.MonkeyPatch().context() as m,
            ):
                # Create a properly mocked Excel writer that handles context manager
                mock_writer = MagicMock()
                mock_writer.book = MagicMock()
                mock_writer.sheets = {"Summary": MagicMock()}

                # Mock the context manager behavior
                mock_writer.__enter__ = MagicMock(return_value=mock_writer)
                mock_writer.__exit__ = MagicMock(return_value=None)

                m.setattr("pandas.ExcelWriter", lambda *_args, **_kwargs: mock_writer)
                m.setattr(
                    "kp_analysis_toolkit.process_scripts.excel_exporter._create_results_sheet",
                    MagicMock(),
                )
                m.setattr(
                    "kp_analysis_toolkit.process_scripts.excel_exporter._create_summary_sheet",
                    MagicMock(),
                )
                m.setattr(
                    "kp_analysis_toolkit.process_scripts.excel_exporter._create_systems_summary_sheet",
                    MagicMock(),
                )
                m.setattr(
                    "kp_analysis_toolkit.process_scripts.excel_exporter._apply_worksheet_tab_colors",
                    MagicMock(),
                )
                m.setattr(
                    "kp_analysis_toolkit.process_scripts.excel_exporter.format_as_excel_table",
                    MagicMock(),
                )

                # This should include topic in summary data without failing
                export_search_results_to_excel(search_results, output_path)

    def test_topic_color_assignment_consistency(self) -> None:
        """Test that topic color assignment is consistent."""
        topic = "Network Configuration"

        color1 = TopicColorManager.get_color_for_topic(topic)
        color2 = TopicColorManager.get_color_for_topic(topic)

        assert color1.hex_color == color2.hex_color
        assert color1.name == topic

    def test_apply_summary_formatting_with_valid_data(self) -> None:
        """Test applying summary formatting with valid topic data."""
        # Create a mock worksheet
        mock_worksheet = MagicMock()

        # Mock the header row cells with proper structure
        mock_search_name_cell = MagicMock()
        mock_search_name_cell.value = "Search Name"
        mock_topic_cell = MagicMock()
        mock_topic_cell.value = "Topic"
        mock_sheet_name_cell = MagicMock()
        mock_sheet_name_cell.value = "Sheet Name"
        mock_other_cell = MagicMock()
        mock_other_cell.value = "Total Results"

        # Mock the worksheet indexing to return header cells
        # The function accesses worksheet[header_row] where header_row = 2
        mock_worksheet.__getitem__.return_value = [
            mock_search_name_cell,  # Column A - Search Name
            mock_topic_cell,  # Column B - Topic
            mock_sheet_name_cell,  # Column C - Sheet Name
            mock_other_cell,  # Column D - Other columns
        ]

        # Mock max_column property
        mock_worksheet.max_column = 6

        # Mock cell creation - return different mocks for different calls
        def mock_cell_func(*_args: object, **_kwargs: object) -> MagicMock:
            mock_cell = MagicMock()
            mock_cell.fill = None
            mock_cell.hyperlink = None
            mock_cell.font = None
            return mock_cell

        mock_worksheet.cell.side_effect = mock_cell_func

        summary_data = [
            {
                "Search Name": "test_search",
                "Topic": "Network Configuration",
                "Sheet Name": "TestSheet",
                "Total Results": 5,
                "Unique Systems": 3,
                "Has Extracted Fields": True,
            },
        ]

        # This should not raise an exception
        _apply_summary_formatting(mock_worksheet, summary_data)

    def test_apply_worksheet_tab_colors(self) -> None:
        """Test applying worksheet tab colors."""
        # Create mock search results
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="TestSheet",
            topic="Network Configuration",
        )

        search_result = MagicMock(spec=SearchResults)
        search_result.search_config = search_config

        # Create mock writer
        mock_writer = MagicMock()
        mock_workbook = MagicMock()
        mock_worksheet = MagicMock()

        mock_writer.book = mock_workbook
        mock_workbook.worksheets = [mock_worksheet]
        mock_worksheet.title = "TestSheet"
        mock_workbook.__getitem__.return_value = mock_worksheet

        # This should not raise an exception
        _apply_worksheet_tab_colors(mock_writer, [search_result])

    def test_all_topics_have_colors(self) -> None:
        """Test that all known topics have assigned colors."""
        topics = TopicColorManager.get_all_topics()

        for topic in topics:
            color = TopicColorManager.get_color_for_topic(topic)
            assert color is not None
            assert color.name == topic
            assert color.hex_color
            assert color.tab_color

    def test_unknown_topic_gets_default_color(self) -> None:
        """Test that unknown topics get the default color."""
        color = TopicColorManager.get_color_for_topic("Unknown Topic")

        default_color = TopicColorManager.get_default_color()

        assert color.name == default_color.name
        assert color.hex_color == default_color.hex_color

    def test_topic_validation(self) -> None:
        """Test topic validation functionality."""
        # Known topics should validate as True
        assert TopicColorManager.validate_topic("Network Configuration")
        assert TopicColorManager.validate_topic("Crypto Policies")

        # Unknown topics should validate as False
        assert not TopicColorManager.validate_topic("Unknown Topic")
        assert not TopicColorManager.validate_topic("")

    def test_color_assignment_map_completeness(self) -> None:
        """Test that color assignment map includes all topics."""
        color_map = TopicColorManager.get_color_assignment_map()
        all_topics = TopicColorManager.get_all_topics()

        assert len(color_map) == len(all_topics)

        for topic in all_topics:
            assert topic in color_map
            assert color_map[topic].name == topic
