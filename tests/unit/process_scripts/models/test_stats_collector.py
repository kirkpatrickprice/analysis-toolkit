import pytest  # noqa: F401

from kp_analysis_toolkit.process_scripts.models.base import StatsCollector


class TestStatsCollector:
    """Tests for the StatsCollector class."""

    def test_init(self) -> None:
        """Test that the StatsCollector initializes with empty dictionaries."""
        stats = StatsCollector()
        assert stats.counters == {}
        assert stats.timers == {}

    def test_increment_new_counter(self) -> None:
        """Test incrementing a new counter."""
        stats = StatsCollector()
        stats.increment("test_counter")
        assert stats.counters["test_counter"] == 1

    def test_increment_existing_counter(self) -> None:
        """Test incrementing an existing counter."""
        stats = StatsCollector()
        stats.increment("test_counter")
        stats.increment("test_counter")
        assert stats.counters["test_counter"] == 2  # noqa: PLR2004

    def test_increment_with_custom_value(self) -> None:
        """Test incrementing a counter with a custom value."""
        stats = StatsCollector()
        stats.increment("test_counter", 5)
        assert stats.counters["test_counter"] == 5  # noqa: PLR2004
        stats.increment("test_counter", 3)
        assert stats.counters["test_counter"] == 8  # noqa: PLR2004

    def test_get_existing_counter(self) -> None:
        """Test getting the value of an existing counter."""
        stats = StatsCollector()
        stats.increment("test_counter", 10)
        assert stats.get_counter("test_counter") == 10  # noqa: PLR2004

    def test_get_nonexistent_counter(self) -> None:
        """Test getting the value of a non-existent counter returns 0."""
        stats = StatsCollector()
        assert stats.get_counter("nonexistent_counter") == 0

    def test_record_time_new_timer(self) -> None:
        """Test recording time for a new timer."""
        stats = StatsCollector()
        stats.record_time("test_timer", 1.5)
        assert stats.timers["test_timer"] == 1.5  # noqa: PLR2004

    def test_record_time_existing_timer(self) -> None:
        """Test recording time for an existing timer."""
        stats = StatsCollector()
        stats.record_time("test_timer", 1.5)
        stats.record_time("test_timer", 2.5)
        assert stats.timers["test_timer"] == 4.0  # noqa: PLR2004

    def test_get_existing_timer(self) -> None:
        """Test getting the value of an existing timer."""
        stats = StatsCollector()
        stats.record_time("test_timer", 3.75)
        assert stats.get_timer("test_timer") == 3.75  # noqa: PLR2004

    def test_get_nonexistent_timer(self) -> None:
        """Test getting the value of a non-existent timer returns 0.0."""
        stats = StatsCollector()
        assert stats.get_timer("nonexistent_timer") == 0.0

    def test_multiple_counters_and_timers(self) -> None:
        """Test using multiple counters and timers simultaneously."""
        stats = StatsCollector()

        # Set up multiple counters
        stats.increment("counter_a", 5)
        stats.increment("counter_b", 3)
        stats.increment("counter_a", 2)

        # Set up multiple timers
        stats.record_time("timer_x", 1.1)
        stats.record_time("timer_y", 2.2)
        stats.record_time("timer_x", 3.3)

        # Verify all values are correct
        assert stats.get_counter("counter_a") == 7  # noqa: PLR2004
        assert stats.get_counter("counter_b") == 3  # noqa: PLR2004
        assert stats.get_timer("timer_x") == 4.4  # noqa: PLR2004
        assert stats.get_timer("timer_y") == 2.2  # noqa: PLR2004
