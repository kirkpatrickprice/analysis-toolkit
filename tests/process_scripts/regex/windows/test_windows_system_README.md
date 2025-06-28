# Dynamic Windows System YAML Tests

This test suite dynamically creates unit tests for each regex pattern defined in `audit-windows-system.yaml`, testing them against real Windows system data from the testdata directory.

## Test Structure

### Main Test Class: `TestWindowsSystemPatterns`

#### Basic Validation Tests
- `test_yaml_file_loads_successfully()` - Ensures the YAML file loads without syntax errors
- `test_all_search_configs_have_required_fields()` - Validates all configs have required fields like 'regex'

#### Pattern-Specific Tests
- `test_specific_pattern_compilation()` - Parametrized test that verifies each regex pattern compiles correctly with appropriate flags
  - Tests 11 specific patterns from the YAML file
  - Handles multiline flag when specified in config
  - Provides clear error messages for compilation failures

#### Dynamic Pattern Validation
- `test_dynamic_pattern_validation()` - Core test that validates all patterns against real test data
  - Tests every pattern in the YAML file dynamically
  - Validates against all 4 Windows test data files
  - Checks field extraction when `only_matching` and `field_list` are specified
  - Handles optional patterns that might not match in all files (BitLocker, SNMP, etc.)

#### Parameter Effect Tests
- `test_max_results_parameter_effects()` - Validates that max_results properly limits output
  - Only tests configs that specify max_results
  - Simulates the limiting behavior
  - Ensures the parameter works as expected

- `test_multiline_parameter_effects()` - Tests multiline flag effects
  - Compares regex behavior with and without multiline flag
  - Validates that multiline patterns exist and are tested
  - Documents when differences are found (though differences aren't required)

#### Configuration Consistency Tests
- `test_field_list_consistency()` - Validates field_list matches regex named groups
  - Detects naming convention mismatches (camelCase vs snake_case)
  - Provides warnings for minor mismatches
  - Fails for major mismatches where no fields correspond
  - Found real issues like scheduled tasks field name mismatches

#### Performance Tests
- `test_pattern_performance()` - Ensures patterns execute within reasonable time limits
  - 5-second threshold per pattern per file
  - Helps identify potentially problematic regex patterns
  - Tests against all real-world data files

## Test Data Used

The tests use real Windows system audit data from:
- `testdata/process_scripts/windows/windows10pro-cb19044-kp0.4.7.txt` - Windows 10 Pro
- `testdata/process_scripts/windows/windows11-0.4.8.txt` - Windows 11
- `testdata/process_scripts/windows/windows2016-cb14393-kp0.4.4-1.txt` - Windows Server 2016
- `testdata/process_scripts/windows/windows2022-cb20348-kp0.4.7.txt` - Windows Server 2022

## Key Features

### Dynamic Test Generation
- Tests are created based on YAML content, not hard-coded
- New patterns added to the YAML will automatically be tested
- No manual test updates required when YAML changes

### Real-World Validation
- Uses actual system audit output from 4 different Windows versions
- Tests patterns against realistic, complex data
- Validates both successful matches and proper field extraction

### Comprehensive Parameter Testing
- Tests effect of `multiline` parameter on regex behavior
- Validates `max_results` limiting behavior
- Checks `field_list` consistency with named groups
- Validates `only_matching` field extraction

### Robust Error Handling
- Gracefully handles patterns that don't compile
- Provides detailed error messages with context
- Distinguishes between warnings and failures
- Handles optional patterns that may not match all files

## Issues Found

The tests have already identified several real issues:

1. **Field Name Mismatches**: `01_system_18_scheduled_tasks` has field_list names that don't match the regex named groups
2. **Minor Naming Issues**: `01_system_01_bios` has a case mismatch in `SMBios_version` vs `SMBIos_version`

## Running the Tests

```bash
# Run all Windows system tests
python -m pytest tests/process_scripts/regex/windows/test_windows_system.py -v

# Run specific test categories
python -m pytest tests/process_scripts/regex/windows/test_windows_system.py::TestWindowsSystemPatterns::test_dynamic_pattern_validation -v

# Run with detailed output
python -m pytest tests/process_scripts/regex/windows/test_windows_system.py -v -s
```

## Future Enhancements

This test structure can be extended to:
- Test other YAML files (users, network, security, logging)
- Add integration tests that use the actual search engine
- Validate merge_fields functionality
- Test sys_filter behavior
- Add performance benchmarks and regression testing

The dynamic nature means that as the YAML configurations evolve, the tests will automatically adapt to validate new patterns and parameters.
