# CLI Testing Standards

This document outlines the testing standards and best practices for CLI components in the analysis toolkit.

## Shared Fixtures

All CLI tests should use the shared pytest fixtures defined in `tests/conftest.py`. These fixtures provide consistent, reusable testing infrastructure.

### Available CLI Fixtures

#### `cli_runner`
Basic Click CLI runner for testing CLI commands.

```python
def test_my_command(cli_runner):
    """Test example showing fixture usage."""
    result = cli_runner.invoke(my_command, ['--help'])
    assert result.exit_code == 0
```

#### `isolated_cli_runner` 
CLI runner with isolated temporary environment for tests that need filesystem isolation.

```python
def test_my_command_with_files(isolated_cli_runner, tmp_path):
    """Test example showing isolated runner usage."""
    result = isolated_cli_runner.invoke(my_command, ['--input', str(tmp_path)])
    assert result.exit_code == 0
```

## Testing Standards

### 1. Use Shared Fixtures
- ✅ **DO**: Use `cli_runner` or `isolated_cli_runner` fixtures
- ❌ **DON'T**: Instantiate `CliRunner()` directly in tests

```python
# ✅ Correct
def test_command(cli_runner):
    result = cli_runner.invoke(command)

# ❌ Incorrect  
def test_command():
    runner = CliRunner()
    result = runner.invoke(command)
```

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

### 3. Test Organization
- Place CLI tests in `tests/integration/cli/` for integration tests
- Place CLI unit tests in `tests/unit/` following the module structure
- Use descriptive test file names: `test_{module}_cli_integration.py`

### 4. Test Coverage Requirements
CLI tests should cover:
- Happy path scenarios
- Error conditions and validation
- Help text output
- Edge cases and boundary conditions
- Integration with other components

### 5. Output Validation
When testing CLI output:
- Check exit codes
- Validate key output content
- Test error messages
- Verify file operations when applicable

```python
def test_command_success(cli_runner):
    result = cli_runner.invoke(command, ['--valid-option'])
    assert result.exit_code == 0
    assert 'Success' in result.output

def test_command_error(cli_runner):
    result = cli_runner.invoke(command, ['--invalid-option'])
    assert result.exit_code != 0
    assert 'Error' in result.output
```

## Migration Status

✅ **COMPLETED**: All CLI tests have been migrated to use shared fixtures

### Migrated Test Files
- `tests/integration/cli/test_cli_dependency_injection.py`
- `tests/integration/cli/test_cli_workflow_integration.py` 
- `tests/integration/cli/test_nipper_cli_integration.py`
- `tests/integration/cli/test_rtf_cli_integration.py`
- `tests/regression/test_rich_output_di_regression.py`

### Benefits Achieved
- **Consistency**: All CLI tests now use the same testing infrastructure
- **Maintainability**: Changes to CLI testing setup only need to be made in one place
- **Reliability**: Standardized fixture implementation reduces test flakiness
- **Developer Experience**: Clear patterns for writing new CLI tests

## Best Practices

1. **Keep tests focused**: Each test should verify one specific behavior
2. **Use meaningful names**: Test names should clearly describe what's being tested
3. **Clean up properly**: Use fixtures and temporary directories for isolation
4. **Test both success and failure paths**: Ensure robust error handling
5. **Document complex test scenarios**: Add docstrings for non-obvious test logic

## Future Enhancements

Potential improvements to the CLI testing infrastructure:

- **Custom assertion helpers**: Helper functions for common CLI assertion patterns
- **Mock service fixtures**: Shared fixtures for commonly mocked services
- **Test data fixtures**: Standardized test data for CLI command testing
- **Performance testing**: Infrastructure for testing CLI command performance

## Related Documentation

- [Test Directory Organization](test-directory-organization.md) - Overall test structure
- [Shared Fixtures Analysis](test-directory-organization.md#shared-fixtures-analysis-summary) - Details on all shared fixtures
- [Development Standards](README.md) - General development guidelines
