"""Tests for parallel execution engine."""

from unittest.mock import Mock, patch

from kp_analysis_toolkit.process_scripts.models.results.base import (
    SearchResult,
    SearchResults,
)
from kp_analysis_toolkit.process_scripts.models.search.base import SearchConfig
from kp_analysis_toolkit.process_scripts.models.systems import Systems
from kp_analysis_toolkit.process_scripts.parallel_engine import (
    benchmark_parallel_execution,
    benchmark_sequential_execution,
    get_optimal_worker_count,
)


class TestParallelEngine:
    """Tests for parallel execution engine functions."""

    def test_get_optimal_worker_count_io(self) -> None:
        """Test optimal worker count calculation for I/O-bound tasks."""
        import multiprocessing as mp

        count = get_optimal_worker_count(10, "io")
        expected_max = mp.cpu_count() * 2
        assert count == min(10, expected_max)

    def test_get_optimal_worker_count_cpu(self) -> None:
        """Test optimal worker count calculation for CPU-bound tasks."""
        import multiprocessing as mp

        count = get_optimal_worker_count(10, "cpu")
        expected_max = mp.cpu_count()
        assert count == min(10, expected_max)

    def test_get_optimal_worker_count_mixed(self) -> None:
        """Test optimal worker count calculation for mixed tasks."""
        import multiprocessing as mp

        count = get_optimal_worker_count(10, "mixed")
        expected_max = mp.cpu_count()
        assert count == min(10, expected_max)

    def test_get_optimal_worker_count_fewer_tasks(self) -> None:
        """Test optimal worker count when there are fewer tasks than cores."""
        count = get_optimal_worker_count(2, "cpu")
        assert count == 2  # noqa: PLR2004

    def test_benchmark_sequential_execution(self) -> None:
        """Test sequential execution benchmarking."""
        # Create mock search configs and systems
        search_configs = [Mock(spec=SearchConfig) for _ in range(2)]
        systems = [Mock(spec=Systems) for _ in range(3)]

        # Mock the execute_search function in the search_engine module
        with patch(
            "kp_analysis_toolkit.process_scripts.search_engine.execute_search",
        ) as mock_execute:
            mock_result = Mock(spec=SearchResults)
            mock_result.results = [Mock(spec=SearchResult) for _ in range(5)]
            mock_execute.return_value = mock_result

            benchmark_result = benchmark_sequential_execution(search_configs, systems)

            assert "execution_time" in benchmark_result
            assert "total_systems" in benchmark_result
            assert "total_searches" in benchmark_result
            assert "total_matches" in benchmark_result
            assert "matches_per_second" in benchmark_result
            assert "parallel_execution" in benchmark_result
            assert "max_workers" in benchmark_result

            assert benchmark_result["total_systems"] == 3  # noqa: PLR2004
            assert benchmark_result["total_searches"] == 2  # noqa: PLR2004
            assert (
                benchmark_result["total_matches"] == 10
            )  # 2 configs * 5 results each  # noqa: PLR2004
            assert benchmark_result["parallel_execution"] is False
            assert benchmark_result["max_workers"] == 1

    def test_benchmark_parallel_execution_processes(self) -> None:
        """Test parallel execution benchmarking with processes."""
        search_configs = [Mock(spec=SearchConfig) for _ in range(2)]
        systems = [Mock(spec=Systems) for _ in range(3)]

        with patch(
            "kp_analysis_toolkit.process_scripts.parallel_engine.search_configs_with_processes",
        ) as mock_search:
            mock_result = Mock(spec=SearchResults)
            mock_result.results = [Mock(spec=SearchResult) for _ in range(5)]
            mock_search.return_value = [mock_result, mock_result]

            benchmark_result = benchmark_parallel_execution(
                search_configs,
                systems,
                max_workers=4,
            )

            assert benchmark_result["parallel_execution"] is True
            assert benchmark_result["execution_mode"] == "processes"
            assert benchmark_result["max_workers"] == 4  # noqa: PLR2004
