"""
Topic color management for Excel export formatting.

Provides consistent color coding for topics using a generic color palette
assigned alphabetically by topic name.
"""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class TopicColor:
    """Color configuration for a topic."""

    name: str
    hex_color: str
    rgb_color: tuple[int, int, int]
    fill_color: str  # For cell background
    font_color: str  # For text contrast
    tab_color: str  # For worksheet tab


class TopicColorManager:
    """Manages color assignments for audit topics using a generic palette."""

    # High-contrast color palette with distinct, easily distinguishable colors
    COLOR_PALETTE: ClassVar[list[TopicColor]] = [
        TopicColor(
            name="Color1",
            hex_color="DC143C",  # Crimson Red - vibrant red
            rgb_color=(220, 20, 60),
            fill_color="FFEBEE",
            font_color="FFFFFF",
            tab_color="DC143C",
        ),
        TopicColor(
            name="Color2",
            hex_color="1E90FF",  # Dodger Blue - bright blue
            rgb_color=(30, 144, 255),
            fill_color="E3F2FD",
            font_color="FFFFFF",
            tab_color="1E90FF",
        ),
        TopicColor(
            name="Color3",
            hex_color="32CD32",  # Lime Green - vivid green
            rgb_color=(50, 205, 50),
            fill_color="E8F5E8",
            font_color="FFFFFF",
            tab_color="32CD32",
        ),
        TopicColor(
            name="Color4",
            hex_color="FF8C00",  # Dark Orange - saturated orange
            rgb_color=(255, 140, 0),
            fill_color="FFF8E1",
            font_color="FFFFFF",
            tab_color="FF8C00",
        ),
        TopicColor(
            name="Color5",
            hex_color="8A2BE2",  # Blue Violet - distinct purple
            rgb_color=(138, 43, 226),
            fill_color="F3E5F5",
            font_color="FFFFFF",
            tab_color="8A2BE2",
        ),
        TopicColor(
            name="Color6",
            hex_color="20B2AA",  # Light Sea Green - unique teal
            rgb_color=(32, 178, 170),
            fill_color="E0F2F1",
            font_color="FFFFFF",
            tab_color="20B2AA",
        ),
        TopicColor(
            name="Color7",
            hex_color="FF1493",  # Deep Pink - magenta/pink
            rgb_color=(255, 20, 147),
            fill_color="FCE4EC",
            font_color="FFFFFF",
            tab_color="FF1493",
        ),
        TopicColor(
            name="Color8",
            hex_color="2F4F4F",  # Dark Slate Gray - deep gray
            rgb_color=(47, 79, 79),
            fill_color="ECEFF1",
            font_color="FFFFFF",
            tab_color="2F4F4F",
        ),
        TopicColor(
            name="Color9",
            hex_color="FFD700",  # Gold - bright yellow
            rgb_color=(255, 215, 0),
            fill_color="FFFDE7",
            font_color="000000",
            tab_color="FFD700",
        ),
        TopicColor(
            name="Color10",
            hex_color="8B4513",  # Saddle Brown - earth tone
            rgb_color=(139, 69, 19),
            fill_color="EFEBE9",
            font_color="FFFFFF",
            tab_color="8B4513",
        ),
        TopicColor(
            name="Color11",
            hex_color="4682B4",  # Steel Blue - medium blue
            rgb_color=(70, 130, 180),
            fill_color="E1F5FE",
            font_color="FFFFFF",
            tab_color="4682B4",
        ),
        TopicColor(
            name="Color12",
            hex_color="9ACD32",  # Yellow Green - lime
            rgb_color=(154, 205, 50),
            fill_color="F1F8E9",
            font_color="000000",
            tab_color="9ACD32",
        ),
    ]

    @classmethod
    def get_color_for_topic(cls, topic: str | None) -> TopicColor:
        """
        Get the color configuration for a specific topic.

        Colors are assigned alphabetically by topic name to ensure consistency.
        """
        if not topic:
            return cls.get_default_color()

        # Get list of all known topics and sort alphabetically
        all_topics = cls.get_sorted_topics_from_config()

        try:
            # Find the index of this topic in the sorted list
            topic_index = all_topics.index(topic)

            # Assign color based on index, cycling through palette if needed
            color_index = topic_index % len(cls.COLOR_PALETTE)

            # Create a copy with the topic name
            base_color = cls.COLOR_PALETTE[color_index]
            return TopicColor(
                name=topic,
                hex_color=base_color.hex_color,
                rgb_color=base_color.rgb_color,
                fill_color=base_color.fill_color,
                font_color=base_color.font_color,
                tab_color=base_color.tab_color,
            )

        except ValueError:
            # Topic not found in known topics, use default
            return cls.get_default_color()

    @classmethod
    def get_sorted_topics_from_config(cls) -> list[str]:
        """
        Get sorted list of topics from configuration files.

        This method would ideally read from the actual config files,
        but for now returns the known topics sorted alphabetically.
        """
        # Known topics from the configuration files
        known_topics = [
            "Crypto Policies",
            "Endpoint Protection & Security Software",
            "File System Security",
            "System Auditing & Logging",
            "Network Configuration",
            "Remote Management",
            "System Information & Asset Management",
            "System Services & Process Management",
            "Time Synchronization",
            "User Account Management & Authentication",
            "Vulnerability Management & Patch Status",
        ]

        return sorted(known_topics)

    @classmethod
    def get_all_topics(cls) -> list[str]:
        """Get a list of all available topics."""
        return cls.get_sorted_topics_from_config()

    @classmethod
    def get_default_color(cls) -> TopicColor:
        """Get a default color for unknown topics."""
        return TopicColor(
            name="Unknown",
            hex_color="95A5A6",  # Grey
            rgb_color=(149, 165, 166),
            fill_color="F5F5F5",
            font_color="000000",
            tab_color="95A5A6",
        )

    @classmethod
    def validate_topic(cls, topic: str) -> bool:
        """Validate if a topic is known."""
        return topic in cls.get_sorted_topics_from_config()

    @classmethod
    def get_color_assignment_map(cls) -> dict[str, TopicColor]:
        """Get a mapping of all topics to their assigned colors."""
        topics = cls.get_sorted_topics_from_config()
        return {topic: cls.get_color_for_topic(topic) for topic in topics}
