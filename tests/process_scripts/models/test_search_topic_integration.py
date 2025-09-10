"""Tests for topic field functionality in search configurations."""

from kp_analysis_toolkit.process_scripts.models.search.base import (
    GlobalConfig,
    SearchConfig,
)


class TestTopicFieldMerging:
    """Test cases for topic field merging in search configurations."""

    def test_topic_inheritance_from_global(self) -> None:
        """Test that topic is inherited from global config when not set locally."""
        global_config = GlobalConfig(topic="Network Configuration")
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="Test Sheet",
        )

        merged_config = search_config.merge_global_config(global_config)

        assert merged_config.topic == "Network Configuration"

    def test_local_topic_precedence(self) -> None:
        """Test that local topic takes precedence over global topic."""
        global_config = GlobalConfig(topic="Network Configuration")
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="Test Sheet",
            topic="File System Security",
        )

        merged_config = search_config.merge_global_config(global_config)

        assert merged_config.topic == "File System Security"

    def test_no_topic_inheritance_when_local_exists(self) -> None:
        """Test that global topic is not applied when local topic exists."""
        global_config = GlobalConfig(topic="Network Configuration")
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="Test Sheet",
            topic="Crypto Policies",
        )

        merged_config = search_config.merge_global_config(global_config)

        assert merged_config.topic == "Crypto Policies"
        assert merged_config.topic != global_config.topic

    def test_no_global_topic(self) -> None:
        """Test behavior when global config has no topic."""
        global_config = GlobalConfig()
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="Test Sheet",
            topic="Time Synchronization",
        )

        merged_config = search_config.merge_global_config(global_config)

        assert merged_config.topic == "Time Synchronization"

    def test_no_topics_anywhere(self) -> None:
        """Test behavior when neither global nor local config has topic."""
        global_config = GlobalConfig()
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="Test Sheet",
        )

        merged_config = search_config.merge_global_config(global_config)

        assert merged_config.topic is None

    def test_empty_global_topic(self) -> None:
        """Test behavior when global topic is empty string."""
        global_config = GlobalConfig(topic="")
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="Test Sheet",
        )

        merged_config = search_config.merge_global_config(global_config)

        assert merged_config.topic is None

    def test_topic_with_other_global_configs(self) -> None:
        """Test that topic inheritance works alongside other global config inheritance."""
        global_config = GlobalConfig(
            topic="System Auditing & Logging",
            max_results=100,
            only_matching=True,
        )
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="Test Sheet",
        )

        merged_config = search_config.merge_global_config(global_config)

        assert merged_config.topic == "System Auditing & Logging"
        assert merged_config.max_results == 100
        assert merged_config.only_matching is True

    def test_topic_field_in_search_config_creation(self) -> None:
        """Test that topic field can be set directly in SearchConfig creation."""
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="Test Sheet",
            topic="Endpoint Protection & Security Software",
        )

        assert search_config.topic == "Endpoint Protection & Security Software"

    def test_topic_field_optional(self) -> None:
        """Test that topic field is optional in SearchConfig."""
        search_config = SearchConfig(
            name="test_search",
            regex=r"test_pattern",
            excel_sheet_name="Test Sheet",
        )

        assert search_config.topic is None

    def test_global_config_topic_field(self) -> None:
        """Test that topic field can be set in GlobalConfig."""
        global_config = GlobalConfig(topic="User Account Management & Authentication")

        assert global_config.topic == "User Account Management & Authentication"

    def test_global_config_topic_optional(self) -> None:
        """Test that topic field is optional in GlobalConfig."""
        global_config = GlobalConfig()

        assert global_config.topic is None
