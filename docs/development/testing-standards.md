# CLI Testing Standards

This document outlines the testing standards and best practices for components in the analysis toolkit.

## Shared Fixtures

All tests should use the shared pytest fixtures defined in `tests/conftest.py`. These fixtures provide consistent, reusable testing infrastructure.  Refer to this file for the latest implementations of all fixtures.  Create additional fixtures for any testing components that should be standardized for use across the test suite.

## 1. Testing Standards

- **Use Shared Fixtures** -- Do not create test infrastructure directly in the tests.  Create them in `tests/conftest.py`
- **Embrace DI** -- The future of this application uses the `dependency-injector` framework to create services that are reused in the business logic.  Tests will favor DI-based implementations with secondary tests for non-DI fall-back for interim backwards-compatability
- **Directory and Naming Standards** -- Standards for test names and the use of test directories are located in [`docs/development/test-directory-organization.md`](test-directory-organization.md)

### 2. Fixture Parameter Order
When using multiple fixtures and mocks, follow this parameter order:

1. Mocked objects (from `@patch` decorators)
2. Pytest fixtures (like `cli_runner`)

```python
# ✅ Correct parameter order
@patch('module.function')
def test_command(mock_function, cli_runner):
    result = cli_runner.invoke(command)

# ❌ Incorrect parameter order
@patch('module.function') 
def test_command(cli_runner, mock_function):  # Wrong order
    result = cli_runner.invoke(command)
```


### 4. Test Coverage Requirements
CLI tests should cover:
- Happy path scenarios
- Error conditions and validation
- Help text output
- Edge cases and boundary conditions
- Integration with other components

### 5. Special Testing Scenarios

#### Output Validation
When testing CLI output:
- Check exit codes
- Validate key output content using Rich-aware helpers
- Test error messages
- Verify file operations when applicable

```python
from tests.conftest import assert_rich_output_contains, assert_rich_help_output, assert_rich_version_output

def test_command_success(cli_runner):
    result = cli_runner.invoke(command, ['--valid-option'])
    assert result.exit_code == 0
    assert_rich_output_contains(result.output, 'Success')

def test_command_error(cli_runner):
    result = cli_runner.invoke(command, ['--invalid-option'])
    assert result.exit_code != 0
    assert_rich_output_contains(result.output, 'Error')

def test_version_output(cli_runner):
    result = cli_runner.invoke(command, ['--version'])
    assert result.exit_code == 0
    assert_rich_version_output(result.output)

def test_help_output(cli_runner):
    result = cli_runner.invoke(command, ['--help'])
    assert result.exit_code == 0
    assert_rich_help_output(result.output, "Expected command description")
```

#### Encoding Detection Testing
When testing file encoding detection, use the shared helper function to handle the fact that ASCII-compatible content can be legitimately detected as either 'ascii' or 'utf-8':

```python
from tests.conftest import assert_valid_encoding

def test_encoding_detection(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("ASCII compatible content", encoding="utf-8")
    
    encoding = detect_encoding(test_file)
    # Accept both ascii and utf-8 as valid for ASCII-compatible content
    assert_valid_encoding(encoding, "utf-8")
    
    # For content that should be specific encodings
    assert_valid_encoding(encoding, ["latin-1", "iso-8859-1", "ascii"])
```

#### Dependency Injection Testing
When testing components that use dependency injection, you need two different testing approaches depending on what you're validating:

**Mock-based testing** is used to test integration points and verify that DI services are called correctly without executing the actual business logic. This is faster and isolates the test from external dependencies.

**Real DI testing** is used to test end-to-end functionality with actual service implementations to ensure the entire DI stack works correctly and produces expected results.

##### Preventing Environment-Dependent Test Failures

CLI components often use `container.core.rich_output()` or other DI services. Tests that call these functions directly (not through CLI runners) require proper DI initialization to avoid validation errors in CI environments.

**For any new unit tests** that import and call functions from CLI modules, ensure you:

1. **Add DI fixtures**: Use `@pytest.mark.usefixtures("initialized_container")` for test classes that call CLI functions
2. **Check function signatures**: Functions that don't take `rich_output` as a parameter likely use the DI container internally
3. **Prefer integration tests**: Use integration tests with CLI runners for testing complete CLI commands
4. **Mock when appropriate**: Use mocking for unit tests to avoid DI dependencies when testing isolated logic

```python
# ✅ Correct - Unit test with DI fixture for CLI function calls
@pytest.mark.usefixtures("initialized_container")
class TestFileSelection:
    def test_get_input_file_behavior(self):
        # This function uses container.core.rich_output() internally
        result = get_input_file(None, tmpdir, file_pattern="*.csv")
        assert result is not None

# ✅ Correct - Integration test using CLI runner (DI auto-initialized)
def test_cli_command(cli_runner):
    result = cli_runner.invoke(command, ['--option'])
    assert result.exit_code == 0

# ✅ Correct - Unit test with mocked services (no DI dependency)
def test_table_creation():
    mock_rich_output = Mock()
    result = create_file_selection_table(mock_rich_output, "Files")
    assert result is not None
```

Use the provided fixtures and follow these patterns:

```python
from tests.conftest import mock_di_state, di_initialized

def test_with_mocked_di_services(mock_di_state):
    """Test using mocked DI services - verifies integration points."""
    # The mock_di_state fixture provides a configured mock service
    service = mock_di_state["service"]
    
    # Test your functionality - the service calls will be mocked
    result = some_function_that_uses_di()
    
    # Verify the mock service was called as expected
    service.detect_encoding.assert_called_once()

def test_with_real_di_initialization(di_initialized, tmp_path):
    """Test with real DI initialization - verifies end-to-end functionality."""
    # The di_initialized fixture sets up real DI
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    
    # Test functionality with real DI services
    from kp_analysis_toolkit.utils.get_file_encoding import detect_encoding
    encoding = detect_encoding(test_file)
    assert_valid_encoding(encoding, "utf-8")

def test_di_service_integration():
    """Test DI service integration directly - manual container testing."""
    from kp_analysis_toolkit.core.containers.application import (
        container, initialize_dependency_injection
    )
    
    # Initialize DI
    initialize_dependency_injection(verbose=False, quiet=True)
    
    # Get service through container
    service = container.file_processing().file_processing_service()
    
    # Test service functionality
    assert service is not None
    assert hasattr(service, 'detect_encoding')
```

#### Container Configuration Testing
When testing DI container behavior, configuration, and wiring:

```python
from tests.conftest import container_initialized

def test_container_behavior(container_initialized):
    """Test container behavior with proper initialization."""
    from kp_analysis_toolkit.core.containers.application import container
    
    # Container is properly initialized by the fixture
    service = container.file_processing().file_processing_service()
    assert service is not None
    
    # Test that container instances are consistent
    container1 = container.file_processing()
    container2 = container.file_processing() 
    assert container1 is container2

def test_service_instance_behavior(container_initialized):
    """Test service instance creation behavior."""
    from kp_analysis_toolkit.core.containers.application import container
    
    # Most services use Factory providers (create new instances each time)
    service1 = container.file_processing().file_processing_service()
    service2 = container.file_processing().file_processing_service()
    
    # Expect different instances for Factory providers
    assert service1 is not service2
    
    # But they should have the same configuration
    assert service1.rich_output.verbose == service2.rich_output.verbose
```


## Future Enhancements

Potential improvements to the CLI testing infrastructure:

- **Custom assertion helpers**: Helper functions for common assertion patterns
- **Mock service fixtures**: Shared fixtures for commonly mocked services
- **Performance testing**: Infrastructure for testing performance

## Related Documentation

- [Test Directory Organization](test-directory-organization.md) - Overall test structure
- [Shared Fixtures Analysis](test-directory-organization.md#shared-fixtures-analysis-summary) - Details on all shared fixtures
- [Development Standards](README.md) - General development guidelines
