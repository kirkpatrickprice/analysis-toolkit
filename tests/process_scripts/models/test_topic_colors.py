"""Tests for topic color management functionality."""

import pytest

from kp_analysis_toolkit.process_scripts.models.topic_colors import (
    TopicColor,
    TopicColorManager,
)


class TestTopicColor:
    """Test cases for TopicColor dataclass."""

    def test_topic_color_creation(self) -> None:
        """Test creating a TopicColor instance."""
        color = TopicColor(
            name="Test Topic",
            hex_color="FF0000",
            rgb_color=(255, 0, 0),
            fill_color="FFEBEE",
            font_color="FFFFFF",
            tab_color="FF0000",
        )

        assert color.name == "Test Topic"
        assert color.hex_color == "FF0000"
        assert color.rgb_color == (255, 0, 0)
        assert color.fill_color == "FFEBEE"
        assert color.font_color == "FFFFFF"
        assert color.tab_color == "FF0000"

    def test_topic_color_immutable(self) -> None:
        """Test that TopicColor is immutable (frozen)."""
        color = TopicColor(
            name="Test Topic",
            hex_color="FF0000",
            rgb_color=(255, 0, 0),
            fill_color="FFEBEE",
            font_color="FFFFFF",
            tab_color="FF0000",
        )

        with pytest.raises(AttributeError):
            color.name = "New Name"  # type: ignore  # noqa: PGH003


class TestTopicColorManager:
    """Test cases for TopicColorManager."""

    def test_get_color_for_topic_known(self) -> None:
        """Test getting color for a known topic."""
        # Use the first topic alphabetically
        topics = TopicColorManager.get_sorted_topics_from_config()
        first_topic = topics[0]

        color = TopicColorManager.get_color_for_topic(first_topic)

        assert color.name == first_topic
        assert color.hex_color
        assert color.rgb_color
        assert color.fill_color
        assert color.font_color
        assert color.tab_color

    def test_get_color_for_topic_unknown(self) -> None:
        """Test getting color for an unknown topic."""
        color = TopicColorManager.get_color_for_topic("Unknown Topic")

        assert color.name == "Unknown"
        assert color.hex_color == "95A5A6"

    def test_get_color_for_topic_none(self) -> None:
        """Test getting color for None topic."""
        color = TopicColorManager.get_color_for_topic(None)

        assert color.name == "Unknown"
        assert color.hex_color == "95A5A6"

    def test_get_sorted_topics_from_config(self) -> None:
        """Test getting sorted topics."""
        topics = TopicColorManager.get_sorted_topics_from_config()

        assert len(topics) == 11
        assert topics == sorted(topics)  # Should be alphabetically sorted
        assert "Crypto Policies" in topics
        assert "Network Configuration" in topics

    def test_get_all_topics(self) -> None:
        """Test getting all topics."""
        topics = TopicColorManager.get_all_topics()

        assert len(topics) == 11
        assert topics == sorted(topics)

    def test_validate_topic_known(self) -> None:
        """Test validating a known topic."""
        assert TopicColorManager.validate_topic("Crypto Policies")

    def test_validate_topic_unknown(self) -> None:
        """Test validating an unknown topic."""
        assert not TopicColorManager.validate_topic("Unknown Topic")

    def test_get_default_color(self) -> None:
        """Test getting default color."""
        color = TopicColorManager.get_default_color()

        assert color.name == "Unknown"
        assert color.hex_color == "95A5A6"
        assert color.rgb_color == (149, 165, 166)

    def test_get_color_assignment_map(self) -> None:
        """Test getting color assignment map."""
        color_map = TopicColorManager.get_color_assignment_map()

        topics = TopicColorManager.get_sorted_topics_from_config()
        assert len(color_map) == len(topics)

        for topic in topics:
            assert topic in color_map
            assert color_map[topic].name == topic

    def test_consistent_color_assignment(self) -> None:
        """Test that color assignment is consistent across calls."""
        topic = "Network Configuration"

        color1 = TopicColorManager.get_color_for_topic(topic)
        color2 = TopicColorManager.get_color_for_topic(topic)

        assert color1.hex_color == color2.hex_color
        assert color1.rgb_color == color2.rgb_color

    def test_different_topics_different_colors(self) -> None:
        """Test that different topics get different colors when possible."""
        topics = TopicColorManager.get_sorted_topics_from_config()

        # Get colors for first few topics
        colors = [TopicColorManager.get_color_for_topic(topic) for topic in topics[:5]]

        # Check that they have different hex colors
        hex_colors = [color.hex_color for color in colors]
        assert len(set(hex_colors)) == len(hex_colors)  # All unique

    def test_alphabetical_color_assignment(self) -> None:
        """Test that colors are assigned alphabetically."""
        topics = TopicColorManager.get_sorted_topics_from_config()

        # Get the first topic alphabetically
        first_topic = topics[0]
        first_color = TopicColorManager.get_color_for_topic(first_topic)

        # It should get the first color in the palette
        first_palette_color = TopicColorManager.COLOR_PALETTE[0]
        assert first_color.hex_color == first_palette_color.hex_color

    def test_color_cycling(self) -> None:
        """Test that colors cycle when there are more topics than colors."""
        # This test assumes we have more than 12 topics or tests the cycling logic
        palette_size = len(TopicColorManager.COLOR_PALETTE)

        # Get topics
        topics = TopicColorManager.get_sorted_topics_from_config()

        if len(topics) > palette_size:
            # Test that cycling works
            first_topic_color = TopicColorManager.get_color_for_topic(topics[0])
            cycled_topic_color = TopicColorManager.get_color_for_topic(
                topics[palette_size]
            )

            assert first_topic_color.hex_color == cycled_topic_color.hex_color
        else:
            # For now, we have 11 topics and 12 colors, so no cycling needed
            # Just ensure we don't have duplicates
            colors = [
                TopicColorManager.get_color_for_topic(topic).hex_color
                for topic in topics
            ]
            assert len(set(colors)) == len(colors)
