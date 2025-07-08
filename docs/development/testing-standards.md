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

## Best Practices

1. **Keep tests focused**: Each test should verify one specific behavior
2. **Use meaningful names**: Test names should clearly describe what's being tested
3. **Clean up properly**: Use fixtures and temporary directories (e.g. Pytest's `tmp_path`) for isolation
4. **Test both success and failure paths**: Ensure robust error handling
5. **Document test scenarios**: Add docstrings consistent with the test's complexity
6. **Use Pytest Markers** -- especially mark with `slow` and `performance` as appropriate

## Future Enhancements

Potential improvements to the CLI testing infrastructure:

- **Custom assertion helpers**: Helper functions for common assertion patterns
- **Mock service fixtures**: Shared fixtures for commonly mocked services
- **Performance testing**: Infrastructure for testing performance

## Related Documentation

- [Test Directory Organization](test-directory-organization.md) - Overall test structure
- [Shared Fixtures Analysis](test-directory-organization.md#shared-fixtures-analysis-summary) - Details on all shared fixtures
- [Development Standards](README.md) - General development guidelines
