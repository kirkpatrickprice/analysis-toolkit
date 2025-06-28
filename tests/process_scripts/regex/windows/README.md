# Windows YAML Regex Pattern Tests

This directory contains comprehensive unit tests for all Windows YAML configuration regex patterns used in the analysis toolkit.

## Structure

The tests are organized by Windows YAML configuration file:

- `base.py` - Base test utilities and fixtures shared across all Windows regex tests
- `test_windows_system.py` - **Dynamic tests** for `audit-windows-system.yaml` patterns ✨ NEW
- `test_windows_users.py` - Tests for `audit-windows-users.yaml` patterns  
- `test_windows_security_software.py` - Tests for `audit-windows-security-software.yaml` patterns
- `test_windows_network.py` - Tests for `audit-windows-network.yaml` patterns
- `test_windows_logging.py` - Tests for `audit-windows-logging.yaml` patterns
- `test_all_windows.py` - Imports all tests for easy discovery

### Dynamic Test Generation

The `test_windows_system.py` file features **dynamic test generation** that:
- Automatically creates tests for each regex pattern in the YAML file
- Tests patterns against real Windows audit data from 4 different systems
- Validates `multiline` and `max_results` parameter effects
- Checks field name consistency between `field_list` and regex named groups
- Requires no manual updates when YAML patterns change
- Provides detailed diagnostics for pattern issues

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
python -m pytest tests/process_scripts/regex/
```

### Run Tests for Specific YAML
```bash
python -m pytest tests/process_scripts/regex/test_windows_system.py
python -m pytest tests/process_scripts/regex/test_windows_users.py
python -m pytest tests/process_scripts/regex/test_windows_network.py
python -m pytest tests/process_scripts/regex/test_windows_security_software.py
python -m pytest tests/process_scripts/regex/test_windows_logging.py
```

### Run Only Pattern Tests (Skip Integration Tests)
```bash
python -m pytest tests/process_scripts/regex/ -k "not Integration"
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
