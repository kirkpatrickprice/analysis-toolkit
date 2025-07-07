# Test Directory Organization Analysis and Recommendations

## Current Test Directory Structure

The `tests/` directory currently follows a mixed organizational pattern with both module-specific subdirectories and root-level test files. Here's the current structure:

### Current Organization

```
tests/
├── __init__.py
├── test_cli_di_integration.py          # Integration test at root
├── test_cli_integration.py             # Integration test at root
├── test_help_intercept.py              # Utility test at root
├── test_integration.py                 # Generic integration test at root
├── test_option_groups.py               # CLI test at root
├── test_rich_output_di_comprehensive.py # Comprehensive test at root
├── test_rich_output_di_regression.py   # Regression test at root
├── cli/
│   ├── common/
│   │   └── test_file_selection.py
│   └── utils/
│       └── test_table_layouts.py
├── core/
│   ├── test_containers.py
│   └── test_rich_output_service.py
├── nipper_expander/
│   ├── test_cli.py
│   └── test_process_nipper.py
├── process_scripts/
│   ├── models/
│   │   ├── test_config_model.py
│   │   ├── test_enums.py
│   │   ├── test_enumstrmixin.py
│   │   ├── test_filemodel.py
│   │   ├── test_pathvalidationmixin.py
│   │   ├── test_programconfig.py
│   │   ├── test_search_configs.py
│   │   ├── test_stats_collector.py
│   │   ├── test_systems.py
│   │   └── test_validationmixin.py
│   ├── regex/
│   │   ├── linux/
│   │   ├── macos/
│   │   ├── windows/
│   │   ├── common_base.py
│   │   ├── dynamic_test_generator.py
│   │   └── test_all_platforms.py
│   ├── test_cli_functions.py
│   ├── test_excel_exporter.py
│   ├── test_process_systems.py
│   ├── test_search_engine.py
│   ├── test_search_engine_core.py
│   ├── test_search_multiline.py
│   ├── test_should_skip_line.py
│   └── test_yaml_config_fix.py
├── rtf_to_text/
│   ├── test_cli.py
│   └── test_process_rtf.py
└── utils/
    ├── test_excel_utils.py
    ├── test_get_file_encoding.py
    ├── test_utils_other.py
    └── test_version_checker.py
```

### Source Code Structure (for reference)

```
src/kp_analysis_toolkit/
├── cli/
├── core/
├── models/
├── nipper_expander/
├── process_scripts/
├── rtf_to_text/
└── utils/
```

## Issues with Current Organization

### 1. Mixed Test Types at Root Level
- Integration tests, regression tests, and utility tests are mixed at the root level
- No clear separation between different test purposes
- Difficult to run specific categories of tests efficiently

### 2. Inconsistent CLI Test Organization
CLI tests are scattered across multiple locations:
- Root level: `test_cli_di_integration.py`, `test_cli_integration.py`, `test_option_groups.py`
- Module directories: `nipper_expander/test_cli.py`, `rtf_to_text/test_cli.py`
- CLI subdirectory: `cli/common/`, `cli/utils/`

### 3. Unclear Test Categories
- No distinction between unit tests vs integration tests
- No dedicated regression test organization despite having regression tests
- Mixed naming conventions make test purpose unclear

### 4. Performance and Scalability Concerns
- All tests run together regardless of execution speed
- No separation for slow vs fast tests
- CI/CD pipeline cannot optimize test execution order

## Recommended Directory Organization

### Proposed Test Structure

```
tests/
├── __init__.py
├── conftest.py                         # Shared pytest fixtures and configuration
├── unit/                               # Fast, isolated unit tests
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── test_nipper_commands.py
│   │   │   ├── test_process_scripts_commands.py
│   │   │   └── test_rtf_commands.py
│   │   ├── common/
│   │   │   ├── __init__.py
│   │   │   ├── test_file_selection.py
│   │   │   ├── test_help_intercept.py
│   │   │   └── test_option_groups.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── test_table_layouts.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── test_containers.py
│   │   └── test_rich_output_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── test_base_models.py
│   ├── nipper_expander/
│   │   ├── __init__.py
│   │   └── test_processor.py
│   ├── process_scripts/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── test_config_model.py
│   │   │   ├── test_enums.py
│   │   │   ├── test_enumstrmixin.py
│   │   │   ├── test_filemodel.py
│   │   │   ├── test_pathvalidationmixin.py
│   │   │   ├── test_programconfig.py
│   │   │   ├── test_search_configs.py
│   │   │   ├── test_stats_collector.py
│   │   │   ├── test_systems.py
│   │   │   └── test_validationmixin.py
│   │   ├── regex/
│   │   │   ├── __init__.py
│   │   │   ├── platforms/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_linux_patterns.py
│   │   │   │   ├── test_macos_patterns.py
│   │   │   │   └── test_windows_patterns.py
│   │   │   ├── test_pattern_base.py
│   │   │   └── test_dynamic_generator.py
│   │   ├── test_excel_exporter.py
│   │   ├── test_search_engine.py
│   │   ├── test_search_engine_core.py
│   │   ├── test_search_multiline.py
│   │   ├── test_should_skip_line.py
│   │   └── test_yaml_config_fix.py
│   ├── rtf_to_text/
│   │   ├── __init__.py
│   │   └── test_processor.py
│   └── utils/
│       ├── __init__.py
│       ├── test_excel_utils.py
│       ├── test_file_encoding.py
│       ├── test_other_utilities.py
│       └── test_version_checker.py
├── integration/                        # Multi-component interaction tests
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── test_cli_dependency_injection.py
│   │   ├── test_cli_workflow_integration.py
│   │   ├── test_nipper_cli_integration.py
│   │   ├── test_process_scripts_cli_integration.py
│   │   └── test_rtf_cli_integration.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── test_rich_output_integration.py
│   └── workflows/
│       ├── __init__.py
│       ├── test_nipper_processing_workflow.py
│       ├── test_process_scripts_workflow.py
│       └── test_rtf_processing_workflow.py
├── e2e/                               # End-to-end system tests
│   ├── __init__.py
│   ├── test_complete_nipper_workflow.py
│   ├── test_complete_process_scripts_workflow.py
│   └── test_complete_rtf_workflow.py
├── regression/                        # Regression and bug prevention tests
│   ├── __init__.py
│   ├── test_rich_output_di_regression.py
│   └── test_known_issues_regression.py
└── performance/                       # Performance and load tests
    ├── __init__.py
    ├── test_large_file_processing.py
    └── test_regex_performance.py
```

## Test Categories and Guidelines

### Unit Tests (`tests/unit/`)
**Purpose**: Test individual functions, classes, and methods in isolation

**Characteristics**:
- Fast execution (< 1 second per test)
- No external dependencies (files, network, databases)
- Use mocks for all dependencies
- Focus on single units of functionality

**Guidelines**:
- Mirror the source code structure
- One test file per source module
- Use descriptive test names
- High code coverage focus

### Integration Tests (`tests/integration/`)
**Purpose**: Test interactions between multiple components

**Characteristics**:
- Test real component interactions
- May use temporary files or test data
- Moderate execution time (1-10 seconds per test)
- Focus on interface contracts between components

**Guidelines**:
- Test workflows that span multiple modules
- Use real objects where possible, mocks for external dependencies
- Focus on data flow and component integration

### End-to-End Tests (`tests/e2e/`)
**Purpose**: Test complete user workflows from input to output

**Characteristics**:
- Test the full system as a user would use it
- Use real files and data from `testdata/`
- Longer execution time (10+ seconds per test)
- Focus on user scenarios and business requirements

**Guidelines**:
- Test complete command-line workflows
- Use actual input files from `testdata/`
- Verify final output files and formats

### Regression Tests (`tests/regression/`)
**Purpose**: Prevent previously fixed bugs from reoccurring

**Characteristics**:
- Test specific bug scenarios and edge cases
- Include detailed documentation of the original issue
- May be slow but comprehensive
- Focus on previously problematic areas

**Guidelines**:
- Include issue references in test documentation
- Test exact scenarios that caused original bugs
- Maintain these tests even if code changes

### Performance Tests (`tests/performance/`)
**Purpose**: Ensure system performance meets requirements

**Characteristics**:
- Test with large datasets and files
- Measure execution time and memory usage
- May be slow and resource-intensive
- Run separately from other test categories

**Guidelines**:
- Use realistic large datasets
- Set performance benchmarks
- Monitor for performance regressions

## Test Naming Conventions

### File Naming
- Unit tests: `test_<module_name>.py`
- Integration tests: `test_<feature>_integration.py`
- CLI tests: `test_<command>_cli.py`
- Workflow tests: `test_<workflow>_workflow.py`
- Regression tests: `test_<issue_description>_regression.py`

### Class Naming
- Unit test classes: `Test<ClassName>` or `Test<ModuleName>`
- Integration test classes: `Test<Feature>Integration`
- CLI test classes: `Test<Command>CLI`
- Workflow test classes: `Test<Workflow>Workflow`

### Method Naming
- Use descriptive names that explain the test scenario
- Follow pattern: `test_<action>_when_<condition>_then_<expected_result>`
- Examples:
  - `test_should_process_csv_when_valid_input_provided`
  - `test_raises_error_when_file_not_found`
  - `test_creates_excel_output_when_processing_succeeds`

## Implementation Strategy

### Phase 1: Create New Structure
1. Create the new directory hierarchy
2. Add `__init__.py` files to all test directories
3. Create `conftest.py` with shared fixtures

### Phase 2: Migrate Existing Tests
1. **Root-level tests**: Move to appropriate categories
   - `test_cli_di_integration.py` → `integration/cli/test_cli_dependency_injection.py`
   - `test_rich_output_di_regression.py` → `regression/test_rich_output_di_regression.py`
   - `test_option_groups.py` → `unit/cli/common/test_option_groups.py`

2. **Module-specific CLI tests**: Move to integration
   - `nipper_expander/test_cli.py` → `integration/cli/test_nipper_cli_integration.py`
   - `rtf_to_text/test_cli.py` → `integration/cli/test_rtf_cli_integration.py`

3. **Processor tests**: Move to unit tests
   - `nipper_expander/test_process_nipper.py` → `unit/nipper_expander/test_processor.py`
   - `rtf_to_text/test_process_rtf.py` → `unit/rtf_to_text/test_processor.py`

### Phase 3: Add Test Markers
Configure pytest markers in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Fast unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests", 
    "regression: Regression tests",
    "performance: Performance tests",
    "slow: Tests that take longer to run",
    "cli: CLI-related tests"
]
```

### Phase 4: Update CI/CD Pipeline
Configure different test stages:
1. **Fast feedback**: Unit tests only
2. **Integration validation**: Unit + Integration tests
3. **Full validation**: All tests except performance
4. **Performance monitoring**: Performance tests separately

## Benefits of Recommended Organization

### 1. Development Velocity
- Fast unit test feedback loop during development
- Selective test execution based on change scope
- Clear test categories for focused testing

### 2. CI/CD Optimization
- Parallel test execution by category
- Early failure detection with fast tests
- Staged testing approach for different pipeline phases

### 3. Maintainability
- Clear test purpose and location
- Easy to find tests for specific functionality
- Consistent naming and organization patterns

### 4. Scalability
- Structure supports project growth
- Easy to add new test categories
- Modular organization allows team specialization

### 5. Quality Assurance
- Comprehensive test coverage across all categories
- Regression prevention through dedicated tests
- Performance monitoring and benchmarking

## Common Test Commands

```bash
# Development workflow - fast feedback
pytest tests/unit/ -v

# Pre-commit validation
pytest tests/unit/ tests/integration/ -v

# Full test suite (excluding performance)
pytest tests/ --ignore=tests/performance/ -v

# Specific module testing
pytest tests/unit/nipper_expander/ -v

# CLI tests only
pytest tests/ -k "cli" -v

# Run by markers
pytest tests/ -m "unit" -v
pytest tests/ -m "not slow" -v

# Performance testing
pytest tests/performance/ -v --benchmark-only
```

This organizational structure provides a robust foundation for maintaining high code quality while supporting efficient development workflows and comprehensive testing strategies.

## Analysis: Impact of Test Reorganization

### Overview

After analyzing the existing test files in the `tests/` directory, the reorganization will require both **file moves** and **import path updates** for certain test files. The changes fall into three categories:

1. **Simple moves** (no changes needed)
2. **Import path updates** (relative imports between test files)
3. **Fixture and utility sharing** (common test infrastructure)

### Category 1: Simple Moves (No Changes Required)

These files can be moved without any internal modifications:

#### Unit Tests (move to `tests/unit/`)
```
tests/core/test_containers.py → tests/unit/core/test_containers.py
tests/core/test_rich_output_service.py → tests/unit/core/test_rich_output_service.py
tests/utils/test_excel_utils.py → tests/unit/utils/test_excel_utils.py
tests/utils/test_get_file_encoding.py → tests/unit/utils/test_file_encoding.py
tests/utils/test_utils_other.py → tests/unit/utils/test_other_utilities.py
tests/utils/test_version_checker.py → tests/unit/utils/test_version_checker.py
tests/cli/common/test_file_selection.py → tests/unit/cli/common/test_file_selection.py
tests/cli/utils/test_table_layouts.py → tests/unit/cli/utils/test_table_layouts.py
```

#### Module-specific Unit Tests (move to `tests/unit/`)
```
tests/process_scripts/test_excel_exporter.py → tests/unit/process_scripts/test_excel_exporter.py
tests/process_scripts/test_search_engine.py → tests/unit/process_scripts/test_search_engine.py
tests/process_scripts/test_search_engine_core.py → tests/unit/process_scripts/test_search_engine_core.py
tests/process_scripts/test_search_multiline.py → tests/unit/process_scripts/test_search_multiline.py
tests/process_scripts/test_should_skip_line.py → tests/unit/process_scripts/test_should_skip_line.py
tests/process_scripts/test_yaml_config_fix.py → tests/unit/process_scripts/test_yaml_config_fix.py
tests/process_scripts/models/* → tests/unit/process_scripts/models/
```

**Analysis**: These files use absolute imports (`from kp_analysis_toolkit...`) and don't reference other test files, so they can be moved without modification.

### Category 2: Import Path Updates Required

These files reference other test files and will need import path updates:

#### Process Scripts Regex Tests
**Files requiring changes:**
- `tests/process_scripts/regex/dynamic_test_generator.py`
- `tests/process_scripts/regex/test_all_platforms.py`
- `tests/process_scripts/regex/windows/test_all_windows_dynamic.py`
- `tests/process_scripts/regex/windows/test_windows_*.py` (multiple files)
- `tests/process_scripts/regex/linux/test_all_linux_dynamic.py`
- `tests/process_scripts/regex/macos/test_all_macos_dynamic.py`

**Current problematic imports:**
```python
# In dynamic_test_generator.py
from tests.process_scripts.regex.common_base import RegexTestBase

# In test_all_windows_dynamic.py
from tests.process_scripts.regex.dynamic_test_generator import (
    DynamicYamlTestMixin,
    discover_yaml_files,
)

# In individual Windows test files
from tests.process_scripts.regex.windows.test_all_windows_dynamic import (
    WindowsYamlTestMixin,
)
```

**Required changes after move to `tests/unit/process_scripts/regex/`:**
```python
# Updated imports
from tests.unit.process_scripts.regex.common_base import RegexTestBase
from tests.unit.process_scripts.regex.dynamic_test_generator import (
    DynamicYamlTestMixin,
    discover_yaml_files,
)
from tests.unit.process_scripts.regex.windows.test_all_windows_dynamic import (
    WindowsYamlTestMixin,
)
```

### Category 3: Integration and CLI Tests (Move + Categorize)

These files need to be moved to appropriate categories and may need slight modifications:

#### Integration Tests (move to `tests/integration/`)
```
tests/test_cli_di_integration.py → tests/integration/cli/test_cli_dependency_injection.py
tests/test_cli_integration.py → tests/integration/cli/test_cli_workflow_integration.py
tests/nipper_expander/test_cli.py → tests/integration/cli/test_nipper_cli_integration.py
tests/rtf_to_text/test_cli.py → tests/integration/cli/test_rtf_cli_integration.py
tests/test_integration.py → tests/integration/workflows/test_general_integration.py
```

#### Regression Tests (move to `tests/regression/`)
```
tests/test_rich_output_di_regression.py → tests/regression/test_rich_output_di_regression.py
tests/test_rich_output_di_comprehensive.py → tests/regression/test_rich_output_comprehensive.py
```

#### Unit Tests (move to `tests/unit/`)
```
tests/test_help_intercept.py → tests/unit/cli/common/test_help_intercept.py
tests/test_option_groups.py → tests/unit/cli/common/test_option_groups.py (currently empty)
tests/nipper_expander/test_process_nipper.py → tests/unit/nipper_expander/test_processor.py
tests/rtf_to_text/test_process_rtf.py → tests/unit/rtf_to_text/test_processor.py
tests/process_scripts/test_cli_functions.py → tests/unit/process_scripts/test_cli_functions.py
tests/process_scripts/test_process_systems.py → tests/unit/process_scripts/test_process_systems.py
```

**Analysis**: These files use absolute imports primarily, so they should move without significant changes.

### Category 4: Shared Test Infrastructure

Several files provide shared testing infrastructure that will need special handling:

#### Test Base Classes and Mixins
```
tests/process_scripts/regex/common_base.py → tests/unit/process_scripts/regex/test_pattern_base.py
tests/process_scripts/regex/dynamic_test_generator.py → tests/unit/process_scripts/regex/test_dynamic_generator.py
```

**Analysis**: These files contain base classes and mixins used by multiple test files. They'll need import path updates in all dependent files.

### Required Implementation Steps

#### Step 1: Create New Directory Structure
```powershell
# Create the complete new directory structure
New-Item -ItemType Directory -Path "tests\unit" -Force
New-Item -ItemType Directory -Path "tests\integration" -Force
New-Item -ItemType Directory -Path "tests\e2e" -Force
New-Item -ItemType Directory -Path "tests\regression" -Force
New-Item -ItemType Directory -Path "tests\performance" -Force

# Create unit test subdirectories
New-Item -ItemType Directory -Path "tests\unit\cli" -Force
New-Item -ItemType Directory -Path "tests\unit\core" -Force
New-Item -ItemType Directory -Path "tests\unit\models" -Force
New-Item -ItemType Directory -Path "tests\unit\nipper_expander" -Force
New-Item -ItemType Directory -Path "tests\unit\process_scripts" -Force
New-Item -ItemType Directory -Path "tests\unit\rtf_to_text" -Force
New-Item -ItemType Directory -Path "tests\unit\utils" -Force

# Create CLI test subdirectories
New-Item -ItemType Directory -Path "tests\unit\cli\commands" -Force
New-Item -ItemType Directory -Path "tests\unit\cli\common" -Force
New-Item -ItemType Directory -Path "tests\unit\cli\utils" -Force

# Create process scripts test subdirectories
New-Item -ItemType Directory -Path "tests\unit\process_scripts\models" -Force
New-Item -ItemType Directory -Path "tests\unit\process_scripts\regex" -Force
New-Item -ItemType Directory -Path "tests\unit\process_scripts\regex\platforms" -Force

# Create integration test subdirectories
New-Item -ItemType Directory -Path "tests\integration\cli" -Force
New-Item -ItemType Directory -Path "tests\integration\core" -Force
New-Item -ItemType Directory -Path "tests\integration\workflows" -Force

# Create __init__.py files for all directories
$directories = @(
    "tests\unit",
    "tests\unit\cli",
    "tests\unit\cli\commands",
    "tests\unit\cli\common", 
    "tests\unit\cli\utils",
    "tests\unit\core",
    "tests\unit\models",
    "tests\unit\nipper_expander",
    "tests\unit\process_scripts",
    "tests\unit\process_scripts\models",
    "tests\unit\process_scripts\regex",
    "tests\unit\process_scripts\regex\platforms",
    "tests\unit\rtf_to_text",
    "tests\unit\utils",
    "tests\integration",
    "tests\integration\cli",
    "tests\integration\core",
    "tests\integration\workflows",
    "tests\e2e",
    "tests\regression",
    "tests\performance"
)

foreach ($dir in $directories) {
    New-Item -ItemType File -Path "$dir\__init__.py" -Force
}
```

#### Step 2: Move Simple Files (No Changes)
Move files that use only absolute imports - these require no internal changes.

```powershell
# Move core unit tests
Move-Item "tests\core\test_containers.py" "tests\unit\core\test_containers.py" -Force
Move-Item "tests\core\test_rich_output_service.py" "tests\unit\core\test_rich_output_service.py" -Force

# Move utils unit tests
Move-Item "tests\utils\test_excel_utils.py" "tests\unit\utils\test_excel_utils.py" -Force
Move-Item "tests\utils\test_get_file_encoding.py" "tests\unit\utils\test_file_encoding.py" -Force
Move-Item "tests\utils\test_utils_other.py" "tests\unit\utils\test_other_utilities.py" -Force
Move-Item "tests\utils\test_version_checker.py" "tests\unit\utils\test_version_checker.py" -Force

# Move CLI unit tests
Move-Item "tests\cli\common\test_file_selection.py" "tests\unit\cli\common\test_file_selection.py" -Force
Move-Item "tests\cli\utils\test_table_layouts.py" "tests\unit\cli\utils\test_table_layouts.py" -Force

# Move process scripts unit tests
Move-Item "tests\process_scripts\test_excel_exporter.py" "tests\unit\process_scripts\test_excel_exporter.py" -Force
Move-Item "tests\process_scripts\test_search_engine.py" "tests\unit\process_scripts\test_search_engine.py" -Force
Move-Item "tests\process_scripts\test_search_engine_core.py" "tests\unit\process_scripts\test_search_engine_core.py" -Force
Move-Item "tests\process_scripts\test_search_multiline.py" "tests\unit\process_scripts\test_search_multiline.py" -Force
Move-Item "tests\process_scripts\test_should_skip_line.py" "tests\unit\process_scripts\test_should_skip_line.py" -Force
Move-Item "tests\process_scripts\test_yaml_config_fix.py" "tests\unit\process_scripts\test_yaml_config_fix.py" -Force
Move-Item "tests\process_scripts\test_cli_functions.py" "tests\unit\process_scripts\test_cli_functions.py" -Force
Move-Item "tests\process_scripts\test_process_systems.py" "tests\unit\process_scripts\test_process_systems.py" -Force

# Move process scripts model tests (all files in models directory)
Get-ChildItem "tests\process_scripts\models\*.py" | ForEach-Object {
    Move-Item $_.FullName "tests\unit\process_scripts\models\$($_.Name)" -Force
}

# Move integration tests to appropriate locations
Move-Item "tests\test_cli_di_integration.py" "tests\integration\cli\test_cli_dependency_injection.py" -Force
Move-Item "tests\test_cli_integration.py" "tests\integration\cli\test_cli_workflow_integration.py" -Force
Move-Item "tests\nipper_expander\test_cli.py" "tests\integration\cli\test_nipper_cli_integration.py" -Force
Move-Item "tests\rtf_to_text\test_cli.py" "tests\integration\cli\test_rtf_cli_integration.py" -Force
Move-Item "tests\test_integration.py" "tests\integration\workflows\test_general_integration.py" -Force

# Move regression tests
Move-Item "tests\test_rich_output_di_regression.py" "tests\regression\test_rich_output_di_regression.py" -Force
Move-Item "tests\test_rich_output_di_comprehensive.py" "tests\regression\test_rich_output_comprehensive.py" -Force

# Move remaining unit tests
Move-Item "tests\test_help_intercept.py" "tests\unit\cli\common\test_help_intercept.py" -Force
Move-Item "tests\test_option_groups.py" "tests\unit\cli\common\test_option_groups.py" -Force
Move-Item "tests\nipper_expander\test_process_nipper.py" "tests\unit\nipper_expander\test_processor.py" -Force
Move-Item "tests\rtf_to_text\test_process_rtf.py" "tests\unit\rtf_to_text\test_processor.py" -Force

# Clean up empty directories (optional)
Remove-Item "tests\core" -Force -ErrorAction SilentlyContinue
Remove-Item "tests\utils" -Force -ErrorAction SilentlyContinue
Remove-Item "tests\cli\common" -Force -ErrorAction SilentlyContinue
Remove-Item "tests\cli\utils" -Force -ErrorAction SilentlyContinue
Remove-Item "tests\cli" -Force -ErrorAction SilentlyContinue
Remove-Item "tests\process_scripts\models" -Force -ErrorAction SilentlyContinue
Remove-Item "tests\nipper_expander" -Force -ErrorAction SilentlyContinue
Remove-Item "tests\rtf_to_text" -Force -ErrorAction SilentlyContinue
```

#### Step 3: Update Cross-Test Imports
Update the import statements in the regex test files:

**Example changes needed in `dynamic_test_generator.py`:**
```python
# Before:
from tests.process_scripts.regex.common_base import RegexTestBase

# After:
from tests.unit.process_scripts.regex.test_pattern_base import RegexTestBase
```

**Example changes needed in `test_all_windows_dynamic.py`:**
```python
# Before:
from tests.process_scripts.regex.dynamic_test_generator import (
    DynamicYamlTestMixin,
    discover_yaml_files,
)

# After:
from tests.unit.process_scripts.regex.test_dynamic_generator import (
    DynamicYamlTestMixin,
    discover_yaml_files,
)
```

#### Step 4: Create Shared conftest.py
Create a shared `tests/conftest.py` file for common fixtures and configuration:

```python
# tests/conftest.py
"""Shared pytest configuration and fixtures."""

import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def testdata_dir():
    """Return the testdata directory path."""
    return Path(__file__).parent.parent / "testdata"

@pytest.fixture(scope="session") 
def temp_workspace(tmp_path_factory):
    """Create a temporary workspace for tests."""
    return tmp_path_factory.mktemp("test_workspace")

# Add other shared fixtures as needed
```

#### Step 5: Update pytest Configuration
Update `pyproject.toml` to handle the new structure:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_paths = ["src", "tests"]
markers = [
    "unit: Fast unit tests",
    "integration: Integration tests", 
    "e2e: End-to-end tests",
    "regression: Regression tests",
    "performance: Performance tests",
    "slow: Tests that take longer to run",
]
```

### Impact Assessment

#### Low Risk Changes (85% of files)
- Simple file moves with no internal modifications
- Files using only absolute imports to source code
- Self-contained unit tests

#### Medium Risk Changes (10% of files)
- Files with cross-test imports (regex test infrastructure)
- CLI integration tests that may need categorization review
- Tests that might benefit from shared fixtures

#### High Risk Changes (5% of files)
- Complex test infrastructure (regex dynamic test generator)
- Tests with intricate dependency chains
- Files that might expose missing test isolation

### Validation Strategy

#### After Reorganization:
1. **Run test discovery**: `pytest --collect-only` to ensure all tests are found
2. **Run fast tests**: `pytest tests/unit/ -v` to validate unit tests
3. **Run integration tests**: `pytest tests/integration/ -v`
4. **Check import resolution**: Look for import errors in test output
5. **Validate test categorization**: Ensure tests are in appropriate categories

#### Test Commands to Verify:
```bash
# All tests should still pass
pytest tests/ -v

# Category-specific runs should work
pytest tests/unit/ -v --disable-warnings
pytest tests/integration/ -v
pytest tests/regression/ -v

# Cross-imports should resolve correctly
pytest tests/unit/process_scripts/regex/ -v
```

### Summary

The test reorganization will require:
- **85% of files**: Simple moves with no changes
- **10% of files**: Import path updates for cross-test dependencies  
- **5% of files**: Potential restructuring of complex test infrastructure

The main complexity is in the `process_scripts/regex/` test hierarchy, which has a sophisticated dynamic test generation system with cross-file dependencies. All other tests can be moved with minimal or no changes.

The reorganization is **feasible and low-risk** overall, with most changes being simple file moves and import path updates.
