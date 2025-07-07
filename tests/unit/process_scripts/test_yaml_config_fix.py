#!/usr/bin/env python3
"""
Test suite for YAML configuration loading and processing.
"""

from pathlib import Path

import pytest
import yaml

from kp_analysis_toolkit.process_scripts.models.search.yaml import YamlConfig
from kp_analysis_toolkit.process_scripts.search_engine import (
    load_search_configs,
    process_includes,
)


class TestYamlConfigLoading:
    """Test cases for YAML configuration loading and processing."""

    def test_yaml_config_without_global_section(self, tmp_path: Path) -> None:
        """Test that YAML config without global section doesn't raise UnboundLocalError."""
        yaml_content = {
            "test_search": {
                "regex": r"test_pattern",
                "comment": "Test search without global config",
            },
        }

        test_file = tmp_path / "test_config.yaml"
        with test_file.open("w") as f:
            yaml.dump(yaml_content, f)

        # This should not raise UnboundLocalError
        configs = load_search_configs(test_file)

        # Verify we got the expected config
        assert len(configs) == 1
        assert configs[0].name == "test_search"
        assert configs[0].regex == "test_pattern"
        assert configs[0].comment == "Test search without global config"

    def test_yaml_config_with_global_section(self, tmp_path: Path) -> None:
        """Test that YAML config with global section works correctly."""
        yaml_content = {
            "global": {
                "max_results": 100,
                "full_scan": True,
            },
            "test_search": {
                "regex": r"test_pattern",
                "comment": "Test search with global config",
            },
        }

        test_file = tmp_path / "test_config.yaml"
        with test_file.open("w") as f:
            yaml.dump(yaml_content, f)

        configs = load_search_configs(test_file)

        # Verify we got the expected config with global settings applied
        assert len(configs) == 1
        assert configs[0].name == "test_search"
        assert configs[0].regex == "test_pattern"
        assert configs[0].max_results == 100
        assert configs[0].full_scan is True

    def test_process_includes_without_global_config(self) -> None:
        """Test process_includes function directly without global config."""
        yaml_config = YamlConfig.from_dict(
            {
                "test_search": {
                    "regex": r"test_pattern",
                    "comment": "Test search config",
                },
            },
        )

        # This should not raise UnboundLocalError
        configs = process_includes(yaml_config, Path())

        assert len(configs) == 1
        assert configs[0].name == "test_search"
        assert configs[0].regex == "test_pattern"

    def test_process_includes_with_global_config(self) -> None:
        """Test process_includes function directly with global config."""
        yaml_config = YamlConfig.from_dict(
            {
                "global": {
                    "max_results": 50,
                    "full_scan": False,
                },
                "test_search": {
                    "regex": r"test_pattern",
                    "comment": "Test search config",
                },
            },
        )

        configs = process_includes(yaml_config, Path())

        assert len(configs) == 1
        assert configs[0].name == "test_search"
        assert configs[0].regex == "test_pattern"
        assert configs[0].max_results == 50
        assert configs[0].full_scan is False

    def test_empty_yaml_config(self, tmp_path: Path) -> None:
        """Test handling of empty YAML config."""
        yaml_content = {"global": {}}  # Minimal valid YAML

        test_file = tmp_path / "test_config.yaml"
        with test_file.open("w") as f:
            yaml.dump(yaml_content, f)

        configs = load_search_configs(test_file)

        # Should return empty list for config with no searches
        assert len(configs) == 0

    def test_multiple_search_configs_without_global(self, tmp_path: Path) -> None:
        """Test multiple search configs without global section."""
        yaml_content = {
            "search1": {
                "regex": r"pattern1",
                "comment": "First search",
            },
            "search2": {
                "regex": r"pattern2",
                "comment": "Second search",
                "max_results": 25,
            },
        }

        test_file = tmp_path / "test_config.yaml"
        with test_file.open("w") as f:
            yaml.dump(yaml_content, f)

        configs = load_search_configs(test_file)

        assert len(configs) == 2

        # Find each config by name
        config1 = next(c for c in configs if c.name == "search1")
        config2 = next(c for c in configs if c.name == "search2")

        assert config1.regex == "pattern1"
        assert config1.comment == "First search"

        assert config2.regex == "pattern2"
        assert config2.comment == "Second search"
        assert config2.max_results == 25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
