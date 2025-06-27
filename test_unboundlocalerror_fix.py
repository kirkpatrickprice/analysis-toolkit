#!/usr/bin/env python3
"""
Simple test to verify the UnboundLocalError fix for YAML configs without global section.
"""

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kp_analysis_toolkit.process_scripts.search_engine import load_search_configs


def test_yaml_without_global_section():
    """Test that UnboundLocalError is fixed when YAML has no global section."""
    # Create a YAML config without global section (like the pattern in real files)
    yaml_content = {
        "test_search_config": {
            "regex": r"System_VersionInformation::(?P<system_info>.*)",
            "excel_sheet_name": "Test Results",
            "max_results": 1,
            "only_matching": True,
            "field_list": ["system_info"],
            "comment": "Test search configuration without global section",
        },
    }

    with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as temp_file:
        yaml.dump(yaml_content, temp_file)
        temp_file.flush()

        try:
            # This should NOT raise UnboundLocalError anymore
            configs = load_search_configs(Path(temp_file.name))

            print(
                f"✓ Successfully loaded {len(configs)} config(s) without UnboundLocalError"
            )

            # Verify the config was loaded correctly
            assert len(configs) == 1
            config = configs[0]
            assert config.name == "test_search_config"
            assert config.regex == r"System_VersionInformation::(?P<system_info>.*)"
            assert config.excel_sheet_name == "Test Results"
            assert config.max_results == 1
            assert config.only_matching is True

            print("✓ Config loaded with correct attributes")

        except Exception as e:
            print(f"✗ Error: {e}")
            raise
        finally:
            Path(temp_file.name).unlink(missing_ok=True)


def test_yaml_with_global_section():
    """Test that configs with global section still work correctly."""
    yaml_content = {
        "global": {
            "max_results": 10,
            "full_scan": True,
        },
        "test_search_config": {
            "regex": r"Test_Pattern::(?P<test_data>.*)",
            "excel_sheet_name": "Global Test Results",
            "only_matching": True,
            "field_list": ["test_data"],
            "comment": "Test search configuration with global section",
        },
    }

    with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as temp_file:
        yaml.dump(yaml_content, temp_file)
        temp_file.flush()

        try:
            configs = load_search_configs(Path(temp_file.name))

            print(f"✓ Successfully loaded {len(configs)} config(s) with global section")

            # Verify the config was loaded correctly and global settings applied
            assert len(configs) == 1
            config = configs[0]
            assert config.name == "test_search_config"
            assert config.regex == r"Test_Pattern::(?P<test_data>.*)"
            assert config.max_results == 10  # From global
            assert config.full_scan is True  # From global
            assert config.only_matching is True  # From individual config

            print("✓ Config loaded with global settings applied correctly")

        except Exception as e:
            print(f"✗ Error: {e}")
            raise
        finally:
            Path(temp_file.name).unlink(missing_ok=True)


if __name__ == "__main__":
    print("Testing UnboundLocalError fix for YAML configs...")
    print("=" * 60)

    try:
        test_yaml_without_global_section()
        print()
        test_yaml_with_global_section()
        print()
        print("=" * 60)
        print("✓ All tests passed! UnboundLocalError has been fixed.")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        exit(1)
