#!/usr/bin/env python3
"""
Test suite for YAML configuration loading and processing.
"""

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import pytest
import yaml

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kp_analysis_toolkit.process_scripts.models.search.yaml import YamlConfig
from kp_analysis_toolkit.process_scripts.search_engine import (
    load_search_configs,
    process_includes,
)


class TestYamlConfigLoading:
    """Test cases for YAML configuration loading and processing."""

    def test_yaml_config_without_global_section(self) -> None:
        """Test that YAML config without global section doesn't raise UnboundLocalError."""
        yaml_content = {
            "test_search": {
                "pattern": r"test_pattern",
                "description": "Test search without global config",
            },
        }

        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as temp_file:
            yaml.dump(yaml_content, temp_file)
            temp_file.flush()

            try:
                # This should not raise UnboundLocalError
                configs = load_search_configs(Path(temp_file.name))

                # Verify we got the expected config
                assert len(configs) == 1
                assert configs[0].name == "test_search"
                assert configs[0].pattern == "test_pattern"
                assert configs[0].description == "Test search without global config"

            finally:
                Path(temp_file.name).unlink()

    def test_yaml_config_with_global_section(self) -> None:
        """Test that YAML config with global section works correctly."""
        yaml_content = {
            "global": {
                "max_results": 100,
                "full_scan": True,
            },
            "test_search": {
                "pattern": r"test_pattern",
                "description": "Test search with global config",
            },
        }

        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as temp_file:
            yaml.dump(yaml_content, temp_file)
            temp_file.flush()

            try:
                configs = load_search_configs(Path(temp_file.name))

                # Verify we got the expected config with global settings applied
                assert len(configs) == 1
                assert configs[0].name == "test_search"
                assert configs[0].pattern == "test_pattern"
                assert configs[0].max_results == 100
                assert configs[0].full_scan is True

            finally:
                Path(temp_file.name).unlink()

    def test_process_includes_without_global_config(self) -> None:
        """Test process_includes function directly without global config."""
        yaml_config = YamlConfig.from_dict(
            {
                "test_search": {
                    "pattern": r"test_pattern",
                    "description": "Test search config",
                },
            }
        )

        # This should not raise UnboundLocalError
        configs = process_includes(yaml_config, Path())

        assert len(configs) == 1
        assert configs[0].name == "test_search"
        assert configs[0].pattern == "test_pattern"

    def test_process_includes_with_global_config(self) -> None:
        """Test process_includes function directly with global config."""
        yaml_config = YamlConfig.from_dict(
            {
                "global": {
                    "max_results": 50,
                    "full_scan": False,
                },
                "test_search": {
                    "pattern": r"test_pattern",
                    "description": "Test search config",
                },
            }
        )

        configs = process_includes(yaml_config, Path())

        assert len(configs) == 1
        assert configs[0].name == "test_search"
        assert configs[0].pattern == "test_pattern"
        assert configs[0].max_results == 50
        assert configs[0].full_scan is False

    def test_empty_yaml_config(self) -> None:
        """Test handling of empty YAML config."""
        yaml_content: dict[str, Any] = {}

        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as temp_file:
            yaml.dump(yaml_content, temp_file)
            temp_file.flush()

            try:
                configs = load_search_configs(Path(temp_file.name))

                # Should return empty list for empty config
                assert len(configs) == 0

            finally:
                Path(temp_file.name).unlink()

    def test_multiple_search_configs_without_global(self) -> None:
        """Test multiple search configs without global section."""
        yaml_content = {
            "search1": {
                "pattern": r"pattern1",
                "description": "First search",
            },
            "search2": {
                "pattern": r"pattern2",
                "description": "Second search",
                "max_results": 25,
            },
        }

        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as temp_file:
            yaml.dump(yaml_content, temp_file)
            temp_file.flush()

            try:
                configs = load_search_configs(Path(temp_file.name))

                assert len(configs) == 2

                # Find each config by name
                config1 = next(c for c in configs if c.name == "search1")
                config2 = next(c for c in configs if c.name == "search2")

                assert config1.pattern == "pattern1"
                assert config1.description == "First search"

                assert config2.pattern == "pattern2"
                assert config2.description == "Second search"
                assert config2.max_results == 25

            finally:
                Path(temp_file.name).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
