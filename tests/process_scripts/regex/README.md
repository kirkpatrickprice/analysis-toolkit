# Multi-Platform Dynamic Regex Testing System

This directory contains a comprehensive, dynamic testing system for regex patterns across all supported platforms (Windows, Linux, and macOS). The system has been designed to maximize code reuse while allowing for platform-specific customizations.

## Architecture

### Common Components
- **`common_base.py`**: Shared base class `RegexTestBase` containing all common testing logic
- **`dynamic_test_generator.py`**: Generalized mixin `DynamicYamlTestMixin` and utilities for creating platform-specific test classes
- **`test_all_platforms.py`**: Comprehensive test runner for all platforms

### Platform-Specific Components
- **`windows/test_all_windows_dynamic.py`**: Windows-specific dynamic tests
- **`linux/test_all_linux_dynamic.py`**: Linux-specific dynamic tests  
- **`macos/test_all_macos_dynamic.py`**: macOS-specific dynamic tests

## Features

### Comprehensive Testing
Each platform's YAML files are tested for:
- **YAML Loading**: Validates that YAML files load without syntax errors
- **Required Fields**: Ensures all search configurations have required fields (regex patterns)
- **Pattern Compilation**: Verifies that all regex patterns compile successfully
- **Dynamic Pattern Validation**: Tests patterns against real-world test data
- **Max Results Parameter**: Validates that `max_results` limits work correctly
- **Multiline Parameter**: Tests that `multiline` flags affect regex behavior
- **Field List Consistency**: Ensures `field_list` matches named groups in patterns
- **Performance Testing**: Verifies patterns perform within acceptable time limits

### Platform Coverage
- **Windows**: 5 YAML files (system, users, network, security-software, logging)
- **Linux**: 8 YAML files (system, users, network, ssh, logging, services, sec-tools, worldfiles)
- **macOS**: 5 YAML files (system, users, network, logging, worldfiles)

### Real Test Data
The system uses actual test data files:
- **Windows**: `testdata/process_scripts/windows/*.txt`
- **Linux**: `testdata/process_scripts/linux/*.txt`
- **macOS**: `testdata/process_scripts/macos/*.txt`

## Usage

### Run Tests for a Specific Platform
```bash
# Windows only
python -m pytest tests/process_scripts/regex/windows/test_all_windows_dynamic.py -v

# Linux only  
python -m pytest tests/process_scripts/regex/linux/test_all_linux_dynamic.py -v

# macOS only
python -m pytest tests/process_scripts/regex/macos/test_all_macos_dynamic.py -v
```

### Run Tests for All Platforms
```bash
# Run comprehensive tests across all platforms
python -m pytest tests/process_scripts/regex/test_all_platforms.py -v

# Or run all platform-specific test files
python -m pytest tests/process_scripts/regex/*/test_all_*_dynamic.py -v
```

### Run Tests for Specific YAML Files
```bash
# Test only Windows system patterns
python -m pytest tests/process_scripts/regex/windows/test_all_windows_dynamic.py::TestWindowsSystemPatterns -v

# Test only Linux network patterns
python -m pytest tests/process_scripts/regex/linux/test_all_linux_dynamic.py::TestLinuxNetworkPatterns -v
```

## Adding New Platforms

To add support for a new platform:

1. **Create platform directory**: `tests/process_scripts/regex/newplatform/`
2. **Add test data**: Place test files in `testdata/process_scripts/newplatform/`
3. **Create dynamic test file**: `test_all_newplatform_dynamic.py` following the existing pattern
4. **Update comprehensive runner**: Add the new platform to `test_all_platforms.py`

## Code Reuse and Maintainability

### Benefits of the Current Architecture
- **~95% Code Reuse**: All testing logic is shared across platforms
- **Dynamic Discovery**: YAML files are automatically discovered, no manual lists
- **Consistent Testing**: All platforms use identical test methodologies
- **Easy Extension**: Adding new platforms or test types requires minimal code
- **Platform Flexibility**: Each platform can override behavior as needed

### Backward Compatibility
The refactored Windows tests maintain full backward compatibility:
- All existing test classes still exist (`TestWindowsSystemPatterns`, etc.)
- Test names and behavior remain identical
- Performance and coverage are preserved

## Migration from Old System

The Windows tests have been successfully migrated from the old system:
- **Before**: Platform-specific base class with duplicated logic
- **After**: Shared base classes with platform-specific mixins
- **Result**: Cleaner code, easier maintenance, consistent behavior across platforms

## Performance

The dynamic test system is optimized for performance:
- **Class-scoped fixtures**: YAML files are loaded once per test class
- **Efficient test data loading**: Test files are read once and cached
- **Pattern compilation caching**: Regex patterns are compiled once per test
- **Selective testing**: Patterns known not to match certain files are skipped

## Future Enhancements

Potential improvements to the system:
1. **Parallel test execution**: Run platform tests in parallel
2. **Performance benchmarking**: Track regex performance over time
3. **Pattern optimization suggestions**: Identify slow patterns automatically
4. **Coverage reporting**: Track which patterns match which test data
5. **Custom test data**: Allow platform-specific test data scenarios
