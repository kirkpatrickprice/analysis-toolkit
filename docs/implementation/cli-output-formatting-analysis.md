# CLI Output Formatting Implementation Analysis

## Overview

After reviewing the current CLI implementation, I've identified several output formatting patterns that should be centralized in `src/kp_analysis_toolkit/cli/common/output_formatting.py`. The file currently exists but is empty.

## Current State Analysis

### Existing Output Formatting Infrastructure

1. **Rich Output Service** (`src/kp_analysis_toolkit/core/services/rich_output.py`)
   - Comprehensive service with message types, styling, tables, banners
   - Configuration via `RichOutputConfig` model
   - Methods: `info()`, `success()`, `error()`, `warning()`, `debug()`, `header()`, `subheader()`
   - Advanced: `banner()`, `configuration_table()`, `format_value()`, `format_path()`

2. **Table Layouts Utility** (`src/kp_analysis_toolkit/cli/utils/table_layouts.py`)
   - Standardized table creation functions
   - Functions: `create_file_selection_table()`, `create_file_listing_table()`, `create_system_info_table()`, `create_config_display_table()`, `create_version_info_table()`

3. **Batch Processing Utility** (`src/kp_analysis_toolkit/cli/utils/batch_processing.py`)
   - Handles progress display and batch operation formatting
   - Success/error message formatting with customizable formatters

## Identified Output Formatting Patterns to Centralize

### 1. **Verbose Details Formatting**

**Current Implementation:** Scattered across commands
```python
# In scripts.py (appears multiple times)
details = []
for key, value in yaml_data.to_dict().items():
    details.append(f"{key}: {rich_output.format_value(value, 60)}")
details_text = "\n".join(details[:max_details_items])
if len(yaml_data.to_dict()) > max_details_items:
    details_text += f"\n... and {len(yaml_data.to_dict()) - max_details_items} more"
```

**Should Be Centralized:** This pattern appears at least 3 times in scripts.py alone.

### 2. **Hash Display Formatting**

**Current Implementation:**
```python
# In scripts.py
hash_display_length = 16  # Length of hash to display
system.file_hash[:hash_display_length] + "..."
```

**Should Be Centralized:** Pattern for truncating and displaying hash values.

### 3. **List Commands Output Formatting**

**Current Implementation:** Multiple similar patterns in scripts.py:
- `list_audit_configs()` - Custom table creation and population
- `list_source_files()` - Using standardized table but custom logic
- `list_systems()` - Custom detail formatting

**Should Be Centralized:** Common patterns for list command outputs.

### 4. **Command Help Table Formatting**

**Current Implementation:** In main.py `_show_enhanced_help()`
```python
table = console.table(
    title="📋 Available Commands",
    show_header=True,
    header_style="bold cyan",
    border_style="blue",
)
# Manual table creation and population
```

**Should Be Centralized:** Pattern for creating command help tables.

**🔗 IMPORTANT CONNECTION TO OPTION GROUPS ISSUE:**
This is directly related to our earlier rich-click option grouping problem! The CLI already uses custom help display instead of Click's native help system. This suggests we could potentially:
- Extend the custom help system to handle option grouping for individual commands
- Intercept `--help` requests for subcommands and apply custom formatting  
- Work around the rich-click multi-command limitation by implementing custom help display

### 5. **Version Display Formatting**

**Current Implementation:** In main.py `_version_callback()`
- Banner creation
- Version table display
- System information formatting

**Should Be Centralized:** Standardized version display format.

### 6. **Error Message Formatting for CLI**

**Current Implementation:** Using `handle_fatal_error()` but formatting is basic
```python
# In config_validation.py
console.print_error(f"{error_prefix}: {e}")
```

**Should Be Centralized:** More sophisticated error display with context.

### 7. **Configuration Display Formatting**

**Current Implementation:** Using `rich_output.configuration_table()` but pattern could be enhanced
```python
# In scripts.py
rich_output.configuration_table(
    config_dict=program_config.to_dict(),
    original_dict=cli_config,
    title="Program Configuration",
    force=True,
)
```

**Should Be Centralized:** Enhanced configuration display patterns.

## Proposed `output_formatting.py` Implementation

### Functions to Implement

#### 1. **Verbose Details Formatting**
```python
def format_verbose_details(
    rich_output: RichOutputService,
    data_dict: dict[str, Any],
    max_items: int = 3,
    max_value_length: int = 60,
) -> str:
    """Format dictionary data for verbose display with truncation."""
```

#### 2. **Hash Display Formatting**
```python
def format_hash_display(
    hash_value: str,
    display_length: int = 16,
    suffix: str = "...",
) -> str:
    """Format hash values for consistent display truncation."""
```

#### 3. **List Command Output Helpers**
```python
def create_list_command_header(
    rich_output: RichOutputService,
    title: str,
    icon: str = "📋",
) -> None:
    """Create standardized header for list commands."""

def handle_empty_list_result(
    rich_output: RichOutputService,
    item_type: str,
) -> None:
    """Display standard 'no items found' message."""

def display_list_summary(
    rich_output: RichOutputService,
    count: int,
    item_type: str,
) -> None:
    """Display standard summary for list commands."""
```

#### 4. **Command Help Formatting**
```python
def create_commands_help_table(
    rich_output: RichOutputService,
    commands: list[tuple[str, str]],  # (command, description)
    title: str = "📋 Available Commands",
) -> Table | None:
    """Create standardized table for command help display."""
```

#### 5. **Version Display Formatting**
```python
def display_version_information(
    rich_output: RichOutputService,
    app_name: str,
    version: str,
    subtitle: str | None = None,
    modules: list[tuple[str, str, str]] | None = None,
    show_system_info: bool = True,
) -> None:
    """Display comprehensive version information with banner and tables."""
```

#### 6. **Enhanced Error Display**
```python
def display_cli_error(
    rich_output: RichOutputService,
    error: Exception,
    context: str | None = None,
    suggestions: list[str] | None = None,
    exit_code: int = 1,
) -> None:
    """Display enhanced error information with context and suggestions."""
```

#### 7. **Progress and Status Formatters**
```python
def create_processing_status_formatter(
    operation_name: str,
) -> Callable[[Path, Any], str]:
    """Create standardized status message formatter for batch operations."""

def format_success_rate_summary(
    total: int,
    successful: int,
    failed: int,
) -> str:
    """Format success rate summary message."""
```

#### 8. **Common Display Patterns**
```python
def display_section_divider(
    rich_output: RichOutputService,
    title: str | None = None,
) -> None:
    """Display section divider with optional title."""

def format_file_size_display(file_path: Path) -> str:
    """Format file size for consistent display."""

def create_emoji_title(base_title: str, emoji: str) -> str:
    """Create consistent emoji-prefixed titles."""
```

## 🔗 Connection to Option Groups Issue

### **Discovery: Custom Help System Already Exists**

During analysis, we discovered that **Command Help Table Formatting (#4) is directly connected to the rich-click option grouping issue** we encountered earlier:

#### **The Problem Context:**
- Rich-click's `OPTION_GROUPS` don't work with multi-command CLI structures (Click Groups)
- We proved option grouping works for standalone commands but fails in multi-command CLIs
- Current solution: Option groups are configured but not displayed

#### **The Connection:**
The CLI **already implements custom help display** that bypasses Click's native help:

```python
# In main.py
def cli(ctx: click.Context, *, skip_update_check: bool, quiet: bool) -> None:
    """Command line interface for the KP Analysis Toolkit."""
    # ... initialization code ...
    
    # If no subcommand was invoked and no help was requested, show help
    if ctx.invoked_subcommand is None:
        console = get_rich_output()
        _show_enhanced_help(console)  # CUSTOM HELP DISPLAY
```

#### **The Opportunity:**
Since we're already using custom help display, we could potentially:

1. **Extend the custom help system** to handle individual command help requests
2. **Intercept `--help` for subcommands** and format them with our option groups  
3. **Implement a help callback system** that applies our configured option groups
4. **Work around the rich-click limitation** entirely with custom formatting

#### **Implementation Strategy:**
Instead of relying on rich-click's broken option grouping, we could:
- Create custom help formatters in `output_formatting.py`
- Use Click's callback system to intercept help requests
- Apply our option group configurations manually
- Display properly grouped help output using our Rich formatting

This would solve both issues:
- ✅ Centralized command help formatting  
- ✅ Working option groups for all commands

## Benefits of Centralization

### 1. **Consistency**
- Standardized formatting across all commands
- Consistent emoji usage and styling
- Uniform error and success message patterns

### 2. **Maintainability**
- Single place to update formatting logic
- Easier to modify display styles globally
- Reduced code duplication

### 3. **Testability**
- Centralized functions can be unit tested
- Easier to verify consistent output formatting
- Mock-friendly for testing CLI behavior

### 4. **Developer Experience**
- Clear patterns for new command development
- Reusable components for common tasks
- Documentation of formatting standards

## Implementation Priority

### High Priority
1. **Verbose Details Formatting** - Used extensively in scripts command
2. **List Command Helpers** - Reduce duplication in scripts.py
3. **Hash Display Formatting** - Simple but used multiple times

### Medium Priority  
4. **Enhanced Error Display** - Improve user experience
5. **Version Display Formatting** - Standardize version output
6. **Command Help Formatting** - Clean up main.py

### Low Priority
7. **Progress Formatters** - Nice-to-have for consistency
8. **Common Display Patterns** - Future-proofing and consistency

## Code Location Strategy

Since `output_formatting.py` is in `cli/common/`, it should:
- Focus on CLI-specific formatting patterns
- Complement (not duplicate) the core `RichOutputService`
- Import and use `RichOutputService` for actual output
- Provide higher-level, CLI-specific formatting functions

## Migration Strategy

1. **Implement core functions** in `output_formatting.py`
2. **Update scripts.py** to use centralized functions (highest impact)
3. **Update main.py** version display
4. **Update other commands** as needed
5. **Add unit tests** for formatting functions
6. **Document patterns** for future developers

## Notes

- The `table_layouts.py` utility already handles table creation well
- Focus should be on formatting logic and display patterns, not table creation
- Integration with existing `RichOutputService` is essential
- Maintain backward compatibility during migration
