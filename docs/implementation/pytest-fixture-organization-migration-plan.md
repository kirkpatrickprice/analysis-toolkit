# Pytest Fixture Organization Migration Plan

## Overview

This document outlines the migration plan for reorganizing pytest fixtures in the KP Analysis Toolkit project. The current `tests/conftest.py` file has grown to 600+ lines with 16 fixtures and multiple utility functions, making it difficult to maintain and extend.

## Current State Analysis

### Fixture Inventory and Usage Patterns

Based on comprehensive analysis of fixture usage across the codebase, fixtures fall into distinct categories:

#### **Cross-Domain Fixtures** (Used across multiple test categories)

1. **`cli_runner`** - **CRITICAL CROSS-DOMAIN**
   - **Usage**: integration/cli (16 uses), e2e (4 uses), regression (3 uses)
   - **Scope**: function
   - **Dependencies**: None
   - **Impact**: High - Used across all CLI testing domains

2. **`isolated_cli_runner`** - **POTENTIAL CROSS-DOMAIN**
   - **Usage**: Not currently used but designed for isolation
   - **Scope**: function
   - **Dependencies**: `tmp_path` (pytest built-in)
   - **Impact**: Medium - Specialized CLI testing

3. **Rich Output Assertion Utilities** - **HIGH CROSS-DOMAIN**
   - `assert_rich_output_contains`: integration/cli (4 uses)
   - `assert_rich_help_output`: integration/cli (6 uses)
   - `assert_rich_version_output`: integration tests
   - **Impact**: High - Used across integration and CLI testing

4. **`isolated_console_env`** - **MODERATE CROSS-DOMAIN**
   - **Usage**: unit/core (1 use), integration/cli (3 uses)
   - **Scope**: function
   - **Impact**: Medium - Environment isolation for Rich console

5. **`assert_console_width_tolerant`** - **MODERATE CROSS-DOMAIN**
   - **Usage**: regression tests (4 uses)
   - **Impact**: Medium - CI environment compatibility

#### **Infrastructure Fixtures** (Foundation/Core)

6. **`testdata_dir`** - **SESSION INFRASTRUCTURE**
   - **Usage**: Referenced in docs, likely used indirectly
   - **Scope**: session
   - **Impact**: High - Foundation for test data access

7. **`temp_workspace`** - **SESSION INFRASTRUCTURE**
   - **Usage**: Referenced in docs, session-scoped workspace
   - **Scope**: session
   - **Impact**: High - Foundation for temporary test environments

#### **Domain-Specific Fixtures** (Limited cross-domain usage)

8. **System Mock Fixtures** - **UNIT TEST FOCUSED**
   - `mock_linux_system`: unit/process_scripts (22 uses)
   - `mock_windows_system`: unit/process_scripts (22 uses)
   - **Scope**: function
   - **Impact**: Medium - Process scripts testing only

9. **`mock_file_system`** - **UNIT TEST FOCUSED**
   - **Usage**: unit/process_scripts/models (21 uses)
   - **Scope**: function
   - **Impact**: Medium - File system operation mocking

10. **Dependency Injection Fixtures** - **SPECIALIZED**
    - `mock_di_container`: Not actively used
    - `mock_file_processing_service`: Not actively used
    - `real_core_container`: unit/core/containers (13 uses)
    - `mock_core_container`: Not actively used
    - `mock_di_state`: Not actively used
    - `isolated_di_env`: Not actively used
    - `di_initialized`: Not actively used
    - `container_initialized`: integration/core (2 uses)
    - **Impact**: Low to Medium - Specialized DI testing

#### **Test Utilities** (Helper functions)

11. **`assert_valid_encoding`** - **UTILITY**
    - **Usage**: Not currently used but designed for encoding tests
    - **Impact**: Low - Encoding validation helper

#### **Pytest Configuration**

12. **`pytest_collection_modifyitems`** - **PYTEST HOOK**
    - **Usage**: Automatic test marking by directory
    - **Impact**: High - Core pytest functionality

### New Test File Analysis

The `tests/unit/utils/test_file_encoding.py` file follows current patterns:
- Uses pytest's built-in `tmp_path` fixture (18 uses)
- No custom fixtures from conftest.py
- Self-contained unit test design
- Uses standard mocking patterns

## Migration Strategy

### Approach: Hybrid Shared + Hierarchical Organization

Based on the cross-domain usage analysis, we'll use a hybrid approach that keeps truly shared fixtures accessible while organizing domain-specific fixtures in specialized modules.

### Target Directory Structure

```
tests/
├── conftest.py                  # Cross-domain fixtures only
├── fixtures/
│   ├── __init__.py              # Fixture module exports
│   ├── di_fixtures.py           # Dependency injection fixtures
│   ├── mock_fixtures.py         # Domain mock objects
│   └── system_fixtures.py       # System/OS mock fixtures
├── unit/
│   └── conftest.py              # Unit-specific fixtures (if needed)
├── integration/
│   └── conftest.py              # Integration-specific fixtures (if needed)
├── e2e/
│   └── conftest.py              # E2E-specific fixtures (if needed)
└── regression/
    └── conftest.py              # Regression-specific fixtures (if needed)
```

## Detailed Migration Plan

### Phase 1: Create Fixture Module Structure

#### Step 1.1: Create Base Directories and Files

Create the following files:

**`tests/fixtures/__init__.py`**  **DONE**
```python
"""
Fixture modules for KP Analysis Toolkit tests.

This package organizes test fixtures by domain while maintaining
cross-domain accessibility through pytest's discovery mechanism.
"""

from tests.fixtures.di_fixtures import *  # noqa: F403
from tests.fixtures.mock_fixtures import *  # noqa: F403
from tests.fixtures.system_fixtures import *  # noqa: F403
```

#### Step 1.2: Create Domain-Specific Fixture Modules

**`tests/fixtures/system_fixtures.py`**
```python
"""System and OS mock fixtures for testing."""

import pytest
from unittest.mock import Mock

from kp_analysis_toolkit.process_scripts.models.enums import OSFamilyType, ProducerType
from kp_analysis_toolkit.process_scripts.models.systems import Systems

# Move the following fixtures from the original conftest.py

@pytest.fixture
def mock_linux_system() -> Systems:
    """Create a mock Linux Systems object for testing."""
    ...

@pytest.fixture
def mock_windows_system() -> Systems:
    """Create a mock Windows Systems object for testing."""
    ...
```

**`tests/fixtures/mock_fixtures.py`**
```python
"""General purpose mock fixtures for testing."""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Move the following fixtures from conftest.py

@pytest.fixture
def mock_file_system() -> Generator[dict[str, MagicMock], Any, None]:
    """
    Mock file system operations for testing.

    Returns a dictionary of mocked pathlib.Path methods:
    - exists: Mock for Path.exists()
    - is_file: Mock for Path.is_file()
    - is_dir: Mock for Path.is_dir()
    - mkdir: Mock for Path.mkdir()
    """
    ...
```

**`tests/fixtures/di_fixtures.py`**
```python
"""Dependency injection fixtures for testing."""

from collections.abc import Generator
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, Mock, patch

import pytest

if TYPE_CHECKING:
    from kp_analysis_toolkit.core.containers.core import CoreContainer

# Move the following fixtures from conftest.py

@pytest.fixture
def mock_di_container() -> MagicMock:
    """
    Mock dependency injection container for testing.

    Returns a mock container that can be used for testing DI functionality
    without requiring actual DI initialization.
    """
    ...


@pytest.fixture
def mock_file_processing_service() -> MagicMock:
    """Create a mock FileProcessingService for testing."""
    ...


@pytest.fixture
def isolated_di_env() -> Generator[None, Any, None]:
    """
    Isolate dependency injection state for testing.

    This fixture ensures that DI state changes in tests don't affect other tests
    by clearing any existing DI state before and after the test.
    """
    ...


@pytest.fixture
def mock_core_container() -> MagicMock:
    """Create a mock CoreContainer for testing file processing integration."""
    ...


@pytest.fixture
def real_core_container() -> "CoreContainer":
    """
    Create a real CoreContainer for dependency injection tests.

    This fixture provides a properly configured CoreContainer instance
    that can be used for testing actual DI behavior without mocks.
    """
    ...


@pytest.fixture
def mock_di_state() -> Generator[MagicMock, Any, None]:
    """
    Mock DI state for testing file processing service integration.

    This fixture provides a mock DI state that can be configured for different
    test scenarios involving dependency injection.
    """
    ...

@pytest.fixture
def di_initialized() -> Generator[None, Any, None]:
    """
    Initialize dependency injection for tests that need it.

    This fixture ensures DI is properly initialized and cleaned up.
    """
    ...


@pytest.fixture
def container_initialized() -> Generator[None, Any, None]:
    """
    Initialize DI container with proper configuration for container testing.

    This fixture is specifically for tests that need to examine container
    behavior, wiring, and configuration. It ensures the container is properly
    configured before testing container-specific functionality.
    """
    ...
```

#### Step 1.3: Update Root conftest.py
The following fixtures are used across test domains and should remain in the root `conftest.py` file.

**`tests/conftest.py` (New Streamlined Version)**
```python
"""Shared pytest configuration and fixtures for cross-domain usage."""

import os
import re
from collections.abc import Generator
from pathlib import Path
from re import Pattern
from typing import Any

import pytest
from click.testing import CliRunner

from tests.fixtures import *  # noqa: F403


# =============================================================================
# SESSION-SCOPED INFRASTRUCTURE FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def testdata_dir() -> Path:
    """Return the testdata directory path."""
    ...


@pytest.fixture(scope="session")
def temp_workspace(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a temporary workspace for tests."""
    ...


# =============================================================================
# CROSS-DOMAIN CLI FIXTURES
# =============================================================================

@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI runner for testing CLI commands."""
    ...


@pytest.fixture
def isolated_cli_runner(tmp_path: Path) -> CliRunner:
    """Create an isolated CLI runner with temporary working directory."""
    ...


@pytest.fixture
def isolated_console_env() -> Generator[None, Any, None]:
    """
    Isolate console environment variables that could affect Rich Console width detection.

    This fixture ensures that tests involving console width settings are not affected
    by CI environment variables like COLUMNS, LINES, etc.
    """
    ...


# =============================================================================
# CROSS-DOMAIN ASSERTION UTILITIES
# =============================================================================

def assert_console_width_tolerant(actual_width: int, expected_width: int, tolerance: int = 1) -> None:
    """
    Assert console width with tolerance for CI environment variations.

    GitHub Actions Windows runners sometimes report console width as 99 instead of 100,
    or 79 instead of 80, due to terminal detection quirks. This function provides a
    tolerant assertion that accounts for these CI environment variations.

    Args:
        actual_width: The actual console width reported
        expected_width: The expected console width
        tolerance: The allowed difference (default 1)

    Raises:
        AssertionError: If the width difference exceeds tolerance
    """
    ...


def assert_valid_encoding(actual_encoding: str | None, expected_encodings: list[str] | str) -> None:
    """
    Assert that the actual encoding is one of the expected valid encodings.

    This helper function handles the fact that ASCII-compatible text can be
    legitimately detected as either 'ascii' or 'utf-8' by charset-normalizer.

    Args:
        actual_encoding: The encoding detected by the system
        expected_encodings: Either a single encoding string or list of valid encodings.
                          If a single string is provided and it's 'utf-8', both 'utf-8'
                          and 'ascii' will be considered valid.

    Example:
        # Accept both ascii and utf-8 for ASCII-compatible content
        assert_valid_encoding(result["encoding"], "utf-8")

        # Accept specific encodings
        assert_valid_encoding(result["encoding"], ["latin-1", "iso-8859-1"])
    """
    ...


def assert_rich_output_contains(output: str, expected_content: str | list[str]) -> None:
    """
    Assert that Rich-formatted CLI output contains expected content.

    This helper function strips ANSI codes and handles Rich formatting to test
    for content presence without being brittle to formatting changes.

    Args:
        output: The raw CLI output (may contain ANSI codes)
        expected_content: String or list of strings that should be present

    Example:
        # Test for single content
        assert_rich_output_contains(result.output, "KP Analysis Toolkit")

        # Test for multiple content items
        assert_rich_output_contains(result.output, [
            "KP Analysis Toolkit",
            "Version",
            "process-scripts"
        ])
    """
    ...


def assert_rich_version_output(output: str) -> None:
    """
    Assert that Rich-formatted version output contains expected elements.

    This helper specifically validates version command output which uses
    Rich panels and tables.

    Args:
        output: The raw CLI output from version command
    """
    ...


def assert_rich_help_output(output: str, command_description: str) -> None:
    """
    Assert that Rich-formatted help output contains expected elements.

    Args:
        output: The raw CLI output from help command
        command_description: The expected command description
    """
    ...


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_collection_modifyitems(
    config: pytest.Config,  # noqa: ARG001
    items: list[pytest.Item],
) -> None:
    """
    Automatically mark tests based on their directory structure.

    This function automatically applies pytest markers to tests based on their location
    within the test directory structure. It's designed to be easily extensible for
    future marking needs.

    Args:
        config: pytest configuration object (unused but required by pytest)
        items: list of collected test items

    """
    ...


def _path_matches_pattern(path: str, pattern: str) -> bool:
    """
    Check if a path matches a given pattern.

    This function supports exact matches and can be extended to support
    more sophisticated pattern matching in the future.

    Args:
        path: The path to check (e.g., "unit/process_scripts/regex/windows")
        pattern: The pattern to match against (e.g., "unit/process_scripts/regex")

    Returns:
        True if the path matches the pattern, False otherwise

    """
    ...
```

### Phase 2: Test Impact Assessment

#### Tests Requiring No Changes

1. **`tests/unit/utils/test_file_encoding.py`** - ✅ **NO CHANGES NEEDED**
   - Uses only pytest built-in `tmp_path` fixture
   - Self-contained unit test
   - No custom fixture dependencies

2. **All tests using cross-domain fixtures** - ✅ **NO CHANGES NEEDED**
   - `cli_runner` users: integration/cli, e2e, regression tests
   - Rich assertion utility users: integration/cli tests
   - `isolated_console_env` users: unit/core, integration/cli tests

#### Tests Requiring Import Updates

**Tests using domain-specific fixtures will require NO changes** because pytest automatically discovers fixtures in:
- `tests/fixtures/conftest.py` (aggregates all fixture modules)
- Individual fixture modules via the conftest.py imports

**Import Strategy**: All fixture modules use absolute imports (e.g., `from tests.fixtures.di_fixtures import *`) for better clarity, IDE support, and to avoid potential import resolution issues.

**However, if any tests import fixtures directly (none found in current analysis), they would need:**

```python
# OLD (if any existed)
from tests.conftest import mock_linux_system

# NEW (if direct imports are needed)
from tests.fixtures.system_fixtures import mock_linux_system
```

### Phase 3: Implementation Steps

#### Step 3.1: Create New Structure (Safe - No Breaking Changes)
1. Create `tests/fixtures/` directory and subdirectories
2. Create all fixture module files
3. Test that pytest discovery works: `pytest --collect-only`

#### Step 3.2: Migrate Fixtures (Incremental)
1. Move fixtures to domain-specific modules
2. Update `tests/fixtures/conftest.py` imports
3. Run tests to verify no breakage: `pytest tests/unit/ -v`

#### Step 3.3: Update Root conftest.py
1. Remove migrated fixtures from root conftest.py
2. Keep only cross-domain fixtures and utilities
3. Run full test suite: `pytest`

#### Step 3.4: Validation
1. Run all test categories to ensure no fixture resolution failures
2. Verify imports work correctly
3. Check that new tests can use fixtures as expected

### Phase 4: Future Considerations

#### Domain-Specific conftest.py Files (Optional)

If specific test categories need specialized fixtures, create:

**`tests/unit/conftest.py`** (if unit-specific fixtures are needed)
```python
"""Unit test specific fixtures."""

import pytest

# Unit-specific fixtures can go here if needed
```

**`tests/integration/conftest.py`** (if integration-specific fixtures are needed)
```python
"""Integration test specific fixtures."""

import pytest

# Integration-specific fixtures can go here if needed
```

## Benefits of This Migration

### Maintainability
- **Reduced File Size**: Root conftest.py reduces from 600+ to ~200 lines
- **Clear Organization**: Domain-specific fixtures are logically grouped
- **Easier Navigation**: Fixtures are in predictable locations

### Extensibility
- **Easy to Add**: New fixtures go in appropriate domain modules
- **Clear Ownership**: Each domain owns its fixtures
- **Scalable**: Structure supports growing test suite

### Compatibility
- **Zero Breaking Changes**: All existing tests continue working
- **Pytest Native**: Uses standard pytest fixture discovery
- **Future-Proof**: Structure accommodates future fixture needs

## Risk Mitigation

### Low Risk Factors
- **No Test Changes**: Existing tests require no modifications
- **Pytest Discovery**: Automatic fixture resolution continues working
- **Incremental**: Changes can be made and tested incrementally

### Validation Strategy
1. **Incremental Testing**: Test each step before proceeding
2. **Comprehensive Test Runs**: Verify all test categories pass
3. **Fixture Resolution Verification**: Ensure pytest finds all fixtures
4. **Import Testing**: Verify direct imports work if needed

## Success Criteria

### Immediate Goals
- [ ] All 16 existing fixtures moved to appropriate modules
- [ ] Root conftest.py contains only cross-domain fixtures
- [ ] All tests pass without modification
- [ ] Pytest fixture discovery works correctly

### Long-term Goals
- [ ] New fixtures added to appropriate domain modules
- [ ] Fixture organization remains maintainable as test suite grows
- [ ] Clear fixture ownership and organization maintained

## Implementation Checklist

### Pre-Migration
- [ ] Create backup branch
- [ ] Document current test pass rate
- [ ] Verify pytest collection works: `pytest --collect-only`

### Migration Steps
- [ ] Create `tests/fixtures/` directory structure
- [ ] Create all fixture module files with content
- [ ] Create aggregate `tests/fixtures/conftest.py`
- [ ] Test fixture discovery: `pytest --collect-only`
- [ ] Run subset of tests: `pytest tests/unit/process_scripts/models/ -v`
- [ ] Update root `tests/conftest.py`
- [ ] Run full test suite: `pytest`
- [ ] Verify all test categories pass

### Post-Migration
- [ ] Update documentation references
- [ ] Create fixture location reference guide
- [ ] Train team on new fixture organization
- [ ] Monitor for any fixture resolution issues

This migration plan provides a safe, incremental approach to organizing pytest fixtures while maintaining full backward compatibility and improving maintainability for future development.
