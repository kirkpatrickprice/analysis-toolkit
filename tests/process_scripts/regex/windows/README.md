# Windows YAML Regex Pattern Tests

This directory contains comprehensive unit tests for all Windows YAML configuration regex patterns used in the analysis toolkit.

## Structure

The tests are organized by Windows YAML configuration file:

- `base.py` - Base test utilities and fixtures shared across all Windows regex tests
- `test_all_windows_dynamic.py` - **Dynamic test generator** for all Windows YAML files ✨ NEW
- `test_windows_system.py` - **Dynamic tests** for `audit-windows-system.yaml` patterns ✨ UPDATED
- `test_windows_users.py` - **Dynamic tests** for `audit-windows-users.yaml` patterns ✨ NEW
- `test_windows_network.py` - **Dynamic tests** for `audit-windows-network.yaml` patterns ✨ NEW
- `test_windows_security_software.py` - **Dynamic tests** for `audit-windows-security-software.yaml` patterns ✨ NEW
- `test_windows_logging.py` - **Dynamic tests** for `audit-windows-logging.yaml` patterns ✨ NEW

### Dynamic Test Generation System

The entire test suite now features **comprehensive dynamic test generation**:

#### Core Architecture
- **`DynamicWindowsYamlTestMixin`** - Reusable mixin class providing all dynamic test methods
- **Automatic YAML Discovery** - Tests are generated for all `audit-windows-*.yaml` files
- **Shared Code Base** - All test files use the same underlying logic from the mixin
- **Individual Test Files** - Each YAML file has its own test file for targeted testing

#### Key Features
- **Zero Configuration** - New YAML files are automatically detected and tested
- **Consistent Test Coverage** - All YAML files get the same comprehensive test suite
- **Real-World Validation** - Tests run against actual Windows audit data from 4 systems
- **Parameter Testing** - Validates `multiline`, `max_results`, `field_list` behavior
- **Performance Monitoring** - Ensures patterns execute within reasonable time limits
- **Configuration Validation** - Checks field name consistency and pattern compilation

#### Individual Test Files Benefits
- Run tests for specific YAML files: `pytest test_windows_users.py -v`
- Faster iteration when working on specific configurations
- Clear separation of concerns for different audit areas
- Easy integration with CI/CD pipelines for targeted testing

See `test_windows_system_README.md` for detailed documentation of the dynamic testing approach.

## Test Data

All tests use real Windows system data from `testdata/process_scripts/windows/`:

- `windows10pro-cb19044-kp0.4.7.txt` - Windows 10 Professional system
- `windows11-0.4.8.txt` - Windows 11 system
- `windows2016-cb14393-kp0.4.4-1.txt` - Windows Server 2016 system  
- `windows2022-cb20348-kp0.4.7.txt` - Windows Server 2022 system

## Test Types

### Regex Pattern Tests
Each test class inherits from `WindowsRegexTestBase` and includes:

- **Individual Pattern Tests**: Test each regex pattern against real data
- **Field Extraction Tests**: Validate that expected named groups are extracted
- **Data Validation Tests**: Ensure extracted values meet expected format/type requirements
- **Cross-File Testing**: Test patterns against all available test data files

### Integration Tests
Test relationships between patterns and overall configuration consistency:

- **Pattern Consistency**: Ensure labeled and raw versions of patterns are consistent
- **Data Correlation**: Validate that related data fields show expected relationships
- **Coverage Tests**: Ensure patterns capture expected data across different Windows versions

## Key Features

### Base Test Class (`WindowsRegexTestBase`)
Provides shared functionality:

- **Multi-file fixtures**: Automatically loads all Windows test data files
- **Pattern validation**: Validates regex patterns with configurable expectations
- **Group extraction**: Extracts and validates named groups from matches
- **Field assertion**: Flexible validation of extracted field values
- **Cross-file testing**: Tests patterns against all available test data

### Test Coverage

The test suite covers all regex patterns from the following YAML files:

#### audit-windows-system.yaml
- KP Windows version detection
- BIOS information extraction
- OS version and build information
- BitLocker status
- Windows Update configuration
- Running processes and services
- RDP configuration
- Screensaver GPO settings
- Scheduled tasks
- System patching information

#### audit-windows-users.yaml
- Local administrator account details
- Local administrator group membership
- Password policy configuration
- Local user accounts (labeled and raw)
- Local groups (labeled and raw)

#### audit-windows-security-software.yaml
- Antivirus status from Windows Security Center
- Windows Defender specific configurations
- Security software state and configuration

#### audit-windows-network.yaml
- Network connectivity tests
- IP address configuration (labeled and raw)
- DNS nameserver configuration
- Listening network services (labeled and raw)
- SMB/LanManager server and client configuration

#### audit-windows-logging.yaml
- Audit policy configuration (labeled and raw)
- File system audit configuration
- Event log configuration
- Event log samples from Application, Security, and System logs

## Running Tests

### Run All Windows Regex Tests
```bash
# Run all Windows YAML pattern tests
python -m pytest tests/process_scripts/regex/windows/ -v

# Run the comprehensive dynamic test generator
python -m pytest tests/process_scripts/regex/windows/test_all_windows_dynamic.py -v
```

### Run Tests for Specific YAML Files
```bash
# Individual YAML test files (recommended for focused testing)
python -m pytest tests/process_scripts/regex/windows/test_windows_system.py -v
python -m pytest tests/process_scripts/regex/windows/test_windows_users.py -v
python -m pytest tests/process_scripts/regex/windows/test_windows_network.py -v
python -m pytest tests/process_scripts/regex/windows/test_windows_security_software.py -v
python -m pytest tests/process_scripts/regex/windows/test_windows_logging.py -v
```

### Run Specific Test Types
```bash
# Test only pattern compilation across all YAML files
python -m pytest tests/process_scripts/regex/windows/ -k "test_pattern_compilation" -v

# Test only field list consistency
python -m pytest tests/process_scripts/regex/windows/ -k "test_field_list_consistency" -v

# Test multiline parameter effects
python -m pytest tests/process_scripts/regex/windows/ -k "test_multiline_parameter_effects" -v

# Test max_results parameter effects  
python -m pytest tests/process_scripts/regex/windows/ -k "test_max_results_parameter_effects" -v
```

### Performance and Debugging
```bash
# Run with detailed output to see warnings and info
python -m pytest tests/process_scripts/regex/windows/ -v -s

# Test performance only
python -m pytest tests/process_scripts/regex/windows/ -k "test_pattern_performance" -v

# Quick smoke test - just check YAML files load
python -m pytest tests/process_scripts/regex/windows/ -k "test_yaml_file_loads_successfully" -v
```

### Run Tests with Verbose Output
```bash
python -m pytest tests/process_scripts/regex/ -v
```

## Test Design Principles

### Real Data Testing
All tests use actual Windows system output rather than synthetic test data. This ensures:
- Patterns work with real-world data variations
- Edge cases in actual system output are discovered
- Confidence that patterns will work in production

### Comprehensive Coverage
Each regex pattern is tested for:
- Basic pattern matching functionality
- Named group extraction
- Data type and format validation
- Error handling and edge cases

### Maintainable Structure
- Shared base class reduces code duplication
- Clear separation between pattern-specific and integration tests
- Fixtures handle test data loading and management
- Consistent naming and organization

### Flexible Validation
Tests accommodate the reality that:
- Not all patterns will match in all test files
- Some Windows features may not be present in all systems
- Data formats may vary between Windows versions
- Empty or missing data should be handled gracefully

## Adding New Tests

When adding new regex patterns to YAML files:

1. Add the test to the appropriate test file (e.g., `test_windows_system.py`)
2. Use the base class fixtures and utilities
3. Test against all available test data files
4. Validate expected named groups and data types
5. Handle cases where the pattern may not match in all test files

### Example Test Structure
```python
def test_new_pattern_regex(self, all_windows_test_data: dict[str, str]) -> None:
    """Test new_pattern regex pattern."""
    pattern = re.compile(r"YourPattern::(?P<field>\w+)")
    
    expected_groups = ["field"]
    
    all_matches = self.test_pattern_against_all_files(
        pattern=pattern,
        all_test_data=all_windows_test_data,
        expected_groups=expected_groups,
    )
    
    # Validate extracted data
    for matches in all_matches.values():
        if matches:
            extracted_data = self.extract_named_groups(matches)
            
            self.assert_field_values(
                extracted_data=extracted_data,
                field_name="field",
                expected_type=str,
            )
            break
```

This comprehensive test suite ensures that all Windows YAML regex patterns are thoroughly validated against real Windows system data, providing confidence in the accuracy and reliability of the analysis toolkit's pattern matching capabilities.
