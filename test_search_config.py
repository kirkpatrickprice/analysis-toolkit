#!/usr/bin/env python3
"""Simple test script for search config service functionality."""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_basic_yaml_parsing():
    """Test basic YAML parsing without circular imports."""
    from kp_analysis_toolkit.process_scripts.services.search_config.yaml_parser import (
        PyYamlParser,
    )

    yaml_parser = PyYamlParser()
    config_file = Path(
        "src/kp_analysis_toolkit/process_scripts/conf.d/audit-windows-system.yaml"
    )

    print(f"Testing YAML parser with: {config_file}")
    print(f"File exists: {config_file.exists()}")

    if config_file.exists():
        try:
            data = yaml_parser.load_yaml(config_file)
            print(f"Successfully parsed YAML with {len(data)} top-level keys")
            print(f"Keys: {list(data.keys())}")

            # Test validation
            is_valid = yaml_parser.validate_yaml_structure(data)
            print(f"Structure validation: {is_valid}")

            # Check specific sections
            if "global" in data:
                print("Global section found")
                print(f"  Global config: {data['global']}")

            # Check for search configurations
            search_configs = [
                k for k in data.keys() if not k.startswith("include_") and k != "global"
            ]
            print(f"Found {len(search_configs)} search configurations")

            if search_configs:
                first_config = search_configs[0]
                config_data = data[first_config]
                print(f"First config '{first_config}':")
                print(f"  Has regex: {'regex' in config_data}")
                print(f"  Regex: {config_data.get('regex', 'N/A')[:50]}...")

            return True

        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
            return False

    return False


if __name__ == "__main__":
    print("=== Testing Search Config Service ===")
    success = test_basic_yaml_parsing()
    print(f"Test result: {'PASS' if success else 'FAIL'}")
