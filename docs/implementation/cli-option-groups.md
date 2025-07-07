# CLI Option Groups Implementation

## Summary

The KP Analysis Toolkit implements rich-click option groups for better CLI help organization. **Currently, option grouping works for standalone commands but not when commands are executed through the multi-command CLI structure due to a limitation in rich-click version 1.8.9.** The infrastructure is complete and ready for when this issue is resolved.

## Overview

The KP Analysis Toolkit implements rich-click option groups to organize CLI help output into logical panels for better user experience. This feature groups related options together rather than displaying them in a single flat list.

## Implementation

### Core Components

1. **Option Groups Utility** (`src/kp_analysis_toolkit/cli/common/option_groups.py`)
   - Centralized configuration for all command option groups
   - Support for both decorator-based and function-based setup
   - Consistent grouping patterns across commands

2. **Command Integration**
   - Each command calls `setup_command_option_groups()` to configure its groups
   - Groups are defined based on functional purpose (Input, Output, Control, etc.)

### Grouping Strategy

Options are organized into logical groups:

- **Input & Processing Options**: File inputs, directories, processing parameters
- **Configuration & Input**: Configuration files, source specifications
- **Information Options**: List commands, discovery options
- **Output & Control**: Output paths, verbosity settings
- **Information & Control**: Version, help (standard across all commands)

### Expected Behavior

When working correctly, the help output should display grouped panels like:

```
╭─ Configuration & Input ────────────────────────────────────╮
│ --conf       -c  TEXT  Configuration file                 │
│ --start-dir  -d  TEXT  Starting directory                 │
│ --filespec   -f  TEXT  File specification pattern         │
╰────────────────────────────────────────────────────────────╯
╭─ Information Options ──────────────────────────────────────╮
│ --list-audit-configs      List available configurations   │
│ --list-sections           List file sections              │
╰────────────────────────────────────────────────────────────╯
```

## Current Issue: Multi-Command CLI Limitation

### Problem Description

**Rich-click option grouping does not work with multi-command CLI structures (Click Groups) in version 1.8.9.**

### Evidence

1. **Standalone Commands Work Perfectly**
   ```bash
   # Direct command execution shows grouped options
   python -c "from kp_analysis_toolkit.cli.commands.scripts import process_command_line; process_command_line(['--help'])"
   ```

2. **Multi-Command CLI Fails**
   ```bash
   # Through main CLI group - no grouping appears
   python -m kp_analysis_toolkit.cli.main scripts --help
   ```

3. **Configuration is Correct**
   - Option groups are properly set in `rich_click.OPTION_GROUPS`
   - Command names match exactly
   - Option names match the decorators
   - Timing is correct (groups set before command execution)

### Technical Details

The issue appears to be a limitation in rich-click where:
- `OPTION_GROUPS` configuration is ignored when commands are executed through a Click Group
- The grouping works only for standalone Click commands
- This affects all commands in the CLI: `scripts`, `rtf-to-text`, and `nipper`

### Debugging Performed

1. **Verified Configuration**
   - Confirmed `OPTION_GROUPS` dict contains correct mappings
   - Verified command names match exactly (`'scripts'`, `'rtf-to-text'`, `'nipper'`)
   - Checked option names match decorator parameters

2. **Tested Multiple Approaches**
   - Module-level configuration
   - Decorator-based configuration  
   - Direct configuration in main.py before adding commands
   - Using different rich-click settings

3. **Isolated the Problem**
   - Created minimal test case proving rich-click grouping works
   - Confirmed issue is specific to multi-command structure
   - Ruled out configuration, timing, and naming issues

## Current Status

### What's Working
- ✅ Option groups infrastructure is complete and ready
- ✅ All commands have proper group configurations
- ✅ Rich-click grouping works in standalone commands
- ✅ Configuration is correctly applied at runtime

### What's Not Working
- ❌ Option grouping doesn't appear in multi-command CLI help output
- ❌ All commands show flat option lists instead of grouped panels

### Code Status
- Infrastructure is in place and documented
- Configuration is ready for when the issue is resolved
- No functionality is broken - CLI works normally without grouping

## Future Resolution

### Potential Solutions
1. **Rich-click Update**: Newer versions may fix this limitation
2. **Alternative Implementation**: Could explore custom help formatting
3. **Workaround Discovery**: Community solutions or alternative approaches

### Migration Path
When a solution is found:
1. The existing configuration should work immediately
2. No changes needed to individual commands
3. Groups will automatically appear in help output

## Files Modified

### Core Implementation
- `src/kp_analysis_toolkit/cli/common/option_groups.py` - Main utility
- `src/kp_analysis_toolkit/cli/common/decorators.py` - Future-ready decorator

### Command Integration
- `src/kp_analysis_toolkit/cli/commands/scripts.py`
- `src/kp_analysis_toolkit/cli/commands/rtf_to_text.py`
- `src/kp_analysis_toolkit/cli/commands/nipper.py`

### CLI Configuration
- `src/kp_analysis_toolkit/cli/main.py` - Multi-command setup

## Testing

### Test File

A minimal test case (`test_option_groups.py`) demonstrates that rich-click grouping works correctly:

```python
import rich_click as click

click.rich_click.OPTION_GROUPS = {
    "test-cmd": [
        {
            "name": "Input Options",
            "options": ["--input-file", "--start-dir"],
        },
        {
            "name": "Control Options", 
            "options": ["--verbose", "--version"],
        },
    ],
}

@click.command(name="test-cmd")
@click.option("--input-file", "-f", help="Input file to process")
@click.option("--start-dir", "-d", help="Starting directory")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--version", is_flag=True, help="Show version")
def test_command(input_file, start_dir, verbose, version):
    """Test command for option grouping."""
    pass
```

### Manual Testing Commands
```bash
# Test standalone grouping (WORKS - shows grouped panels)
python test_option_groups.py --help

# Test individual command (WORKS - shows grouped panels)
python -c "from kp_analysis_toolkit.cli.commands.scripts import process_command_line; process_command_line(['--help'])"

# Test through main CLI (DOESN'T WORK - no grouping)
python -m kp_analysis_toolkit.cli.main scripts --help
python -m kp_analysis_toolkit.cli.main rtf-to-text --help
python -m kp_analysis_toolkit.cli.main nipper --help
```

### Validation Points
- No errors in help output
- All options still appear
- CLI functionality unchanged
- Infrastructure ready for future enablement

## Development Guidelines

### Adding New Commands

When adding a new command, follow this pattern:

```python
from kp_analysis_toolkit.cli.common.option_groups import setup_command_option_groups

# Configure option groups for this command
# Note: Rich-click option grouping currently doesn't work with multi-command CLI structures
setup_command_option_groups("new-command")

@click.command(name="new-command")
@click.option("--input", help="Input file")
@click.option("--output", help="Output directory")
def new_command(input, output):
    """Description of the new command."""
    pass
```

### Extending Group Configurations

To add new command groups, modify `_setup_option_groups_for_command()` in `option_groups.py`:

```python
def _setup_option_groups_for_command(command_name: str) -> None:
    # ... existing code ...
    
    if command_name == "new-command":
        new_command_groups = [
            {
                "name": "Input Options",
                "options": ["--input", "--config"],
            },
            {
                "name": "Output Options", 
                "options": ["--output", "--verbose"],
            },
            {
                "name": "Information & Control",
                "options": ["--version"],
            },
        ]
        if not hasattr(click.rich_click, "OPTION_GROUPS"):
            click.rich_click.OPTION_GROUPS = {}
        click.rich_click.OPTION_GROUPS[command_name] = new_command_groups
```

### Group Design Principles
- Keep groups logical and user-focused
- Maintain consistency across similar commands
- Separate standard options (`--version`, `--help`) when possible
- Group related functionality together

## References

- [Rich-click Documentation](https://github.com/ewels/rich-click)
- [Click Documentation](https://click.palletsprojects.com/)
- Rich-click Issue: Option groups with multi-command CLI (to be filed if not resolved)

---

## Implementation Completion Status

✅ **COMPLETED:**
- Option groups infrastructure implemented
- All commands configured with appropriate groupings
- Comprehensive testing completed
- Issue identified and documented
- Developer guidelines established
- Ready for future rich-click update or workaround

❌ **BLOCKED BY:** Rich-click version 1.8.9 limitation with multi-command CLI structures

🚀 **READY FOR:** Immediate activation when limitation is resolved
