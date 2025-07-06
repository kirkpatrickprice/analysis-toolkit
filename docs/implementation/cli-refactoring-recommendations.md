# CLI Refactoring Recommendations

## Overview
This document outlines opportunities to improve code reuse and consistency across CLI commands by leveraging common functions recently implemented in `cli.common` and `cli.utils` packages.

## Analysis Date
July 6, 2025

## Scope
Analysis focused on `cli.commands.rtf_to_text.py` and `cli.commands.scripts.py` to identify patterns that could benefit from shared utilities.

---

## 1. Configuration Validation Patterns

### Current State
Multiple CLI commands implement their own try/catch blocks for configuration validation:

```python
# Pattern found in rtf_to_text.py (occurs twice)
try:
    program_config: ProgramConfig = ProgramConfig(
        input_file=selected_file,
        source_files_path=source_files_path,
    )
except ValueError as e:
    console.error(f"Error validating configuration: {e}")
    sys.exit(1)
```

### Recommendation
**Replace with standardized functions from `cli.common.config_validation`:**

- Use `validate_program_config()` for consistent validation
- Use `handle_config_error()` for standardized error handling
- Benefits: Consistent error messaging, reduced code duplication, centralized error handling logic

### Implementation Priority
**High** - Immediate benefit with minimal refactoring effort

---

## 2. Error Handling Standardization

### Current State
Inconsistent error handling patterns across commands:

```python
# RTF command example
try:
    selected_file = get_input_file(...)
except ValueError as e:
    console.error(f"Error finding input files: {e}")
    sys.exit(1)

# Similar patterns with slight variations exist in multiple locations
```

### Recommendation
**Standardize using `cli.common.config_validation.handle_config_error()`:**

- Single point of control for error message formatting
- Consistent exit behavior
- Easier to modify error handling behavior globally

### Implementation Priority
**High** - Improves user experience consistency

---

## 3. Text Utility Functions

### Current State
`summarize_text()` function in `cli.commands.scripts.py`:

```python
def summarize_text(
    text: str,
    *,
    first_x_chars: int = 10,
    max_length: int = 50,
    replace_with: str = "...",
) -> str:
    """Summarize text to a maximum length."""
    # Implementation details...
```

### Recommendation
**Move to `cli.utils.text_utils.py` (new file):**

- Create dedicated text processing utilities module
- Make function available to all CLI commands
- Follow established pattern of utility organization
- Alternative: Remove if unused and leverage existing `RichOutputService.format_value()`

### Implementation Priority
**Medium** - Organizational improvement, future-proofing

---

## 4. Batch Processing Patterns

### Current State
`_process_all_files()` function in RTF command implements batch processing with progress tracking:

```python
def _process_all_files(file_list: list[Path]) -> None:
    """Process all RTF files in the list."""
    # Progress tracking, success/failure counting, summary reporting
```

### Recommendation
**Extract to reusable utility in `cli.utils.batch_processing.py` (new file):**

- Create generic batch processor that accepts:
  - File list
  - Processing function
  - Progress description
  - Error handling strategy
- Benefits: Reusable across commands, consistent progress reporting, standardized batch operation UX

### Implementation Priority
**Medium** - Future commands will likely need similar functionality

---

## 5. Results Display Formatting

### Current State
Ad-hoc success/failure message formatting:

```python
console.success(f"Converted: {file_path.name} -> {program_config.output_file.name}")
console.error(f"Failed to convert {file_path.name}: {e}")
console.info(f"Processing complete: {successful} successful, {failed} failed")
```

### Recommendation
**Add batch results table layout to `cli.utils.table_layouts.py`:**

- Create `create_batch_results_table()` function
- Standardize success/failure/summary display
- Consistent formatting across all batch operations

### Implementation Priority
**Low** - Nice-to-have for visual consistency

---

## 6. File Validation Enhancement

### Current State
Basic file pattern matching in `get_input_file()`:

```python
get_input_file(
    _infile,
    source_files_path,
    file_pattern="*.rtf",
    file_type_description="RTF",
    include_process_all_option=True,
)
```

### Recommendation
**Enhance with `cli.common.config_validation.validate_input_file()`:**

- Add extension validation: `required_extensions=['.rtf']`
- Centralized file validation logic
- More robust error messaging

### Implementation Priority
**Low** - Current implementation is adequate

---

## Implementation Plan

### Phase 1: High Priority (Immediate)
1. **Configuration Validation Standardization**
   - Import and use `validate_program_config()` and `handle_config_error()`
   - Update all CLI commands to use standardized patterns
   - Remove duplicate error handling code

2. **Error Handling Consistency**
   - Replace all manual error handling with `handle_config_error()`
   - Ensure consistent error message formatting

### Phase 2: Medium Priority (Next Sprint)
3. **Text Utilities Organization**
   - Create `cli.utils.text_utils.py`
   - Move `summarize_text()` or remove if unused
   - Document text utility functions

4. **Batch Processing Abstraction**
   - Create `cli.utils.batch_processing.py`
   - Extract common batch processing patterns
   - Update RTF command to use new utility

### Phase 3: Low Priority (Future)
5. **Results Display Enhancement**
   - Add batch results table layouts
   - Standardize success/failure formatting

6. **File Validation Enhancement**
   - Integrate more robust file validation where beneficial

---

## Benefits Summary

### Code Quality
- **Reduced Duplication**: Eliminate repeated try/catch patterns
- **Consistency**: Standardized error handling and messaging
- **Maintainability**: Single point of control for common functionality

### User Experience
- **Consistent Interface**: Same error messages and formatting across commands
- **Professional Polish**: Standardized progress reporting and results display

### Developer Experience
- **Faster Development**: Reusable patterns for new CLI commands
- **Easier Testing**: Centralized functions are easier to unit test
- **Better Organization**: Clear separation of concerns between command logic and utilities

---

## Notes

- The RTF command already effectively uses `cli.common.file_selection` utilities
- Most recommendations involve moving existing patterns to shared utilities rather than creating new functionality
- Implementation can be done incrementally without breaking existing functionality
- Consider creating migration guide for developers working on other CLI commands
