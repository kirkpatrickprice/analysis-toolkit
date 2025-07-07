#!/usr/bin/env python3
"""Script to update CLI test files to use the shared cli_runner fixture."""

import re
from pathlib import Path

def update_cli_test_file(file_path: Path) -> None:
    """Update a CLI test file to use the shared cli_runner fixture."""
    print(f"Updating {file_path}")
    
    content = file_path.read_text()
    
    # Pattern to match test method definitions
    method_pattern = r'(def test_[^(]*\([^)]*)(self)([^)]*)\) -> None:'
    
    # Replace method signatures to add cli_runner parameter
    def replace_method_sig(match):
        prefix = match.group(1)
        self_param = match.group(2)
        rest_params = match.group(3)
        
        if 'cli_runner' not in prefix + rest_params:
            if rest_params.strip():
                # There are other parameters after self
                return f"{prefix}{self_param}, cli_runner: CliRunner{rest_params}) -> None:"
            else:
                # Only self parameter
                return f"{prefix}{self_param}, cli_runner: CliRunner) -> None:"
        else:
            # cli_runner already present
            return match.group(0)
    
    # Update method signatures
    content = re.sub(method_pattern, replace_method_sig, content)
    
    # Replace runner = CliRunner() with using the fixture
    content = re.sub(r'(\s+)runner = CliRunner\(\)', r'\1# Using shared cli_runner fixture', content)
    
    # Replace runner.invoke with cli_runner.invoke
    content = re.sub(r'runner\.invoke', 'cli_runner.invoke', content)
    
    # Write the updated content
    file_path.write_text(content)
    print(f"Updated {file_path}")

def main():
    """Update all CLI test files."""
    files_to_update = [
        "tests/integration/cli/test_nipper_cli_integration.py",
        "tests/regression/test_rich_output_di_regression.py",
    ]
    
    for file_path in files_to_update:
        path = Path(file_path)
        if path.exists():
            update_cli_test_file(path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
