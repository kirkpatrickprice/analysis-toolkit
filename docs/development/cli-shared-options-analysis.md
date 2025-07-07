# CLI Shared Options Analysis (Updated)

## Analysis Date
July 6, 2025

## Overview

This document provides a comprehensive analysis of the CLI command patterns in the KP Analysis Toolkit to identify shared options that should be centralized as decorators in `cli.common.decorators`. The analysis examines the main CLI entry point and all command modules to identify common patterns, redundant options, and opportunities for standardization.

## Current CLI Structure

### Main CLI (cli.main.py)
- Global group-level options that apply to all commands
- Central initialization and dependency injection
- Legacy command support

### Commands Analyzed
1. `cli.commands.scripts` - Process collector script results
2. `cli.commands.nipper` - Process Nipper CSV files  
3. `cli.commands.rtf_to_text` - Convert RTF files to text

## Detailed Option Analysis

### Main CLI (`cli.main`)

**Global Options:**
```python
@click.option("--version", is_flag=True, expose_value=False, is_eager=True, callback=_version_callback, help="Show version information and exit.")
@click.option("--skip-update-check", is_flag=True, default=False, help="Skip checking for updates at startup.")
@click.option("--quiet", "-q", is_flag=True, default=False, help="Suppress non-essential output (errors still shown)")
```

### RTF-to-Text Command (`cli.commands.rtf_to_text`)

**Options:**
```python
@click.version_option(version=rtf_to_text_version, prog_name="kpat_cli rtf-to-text", message="%(prog)s version %(version)s")
@click.option("_infile", "--in-file", "-f", default=None, help="Input RTF file to process. If not specified, will search the current directory for RTF files.")
@click.option("source_files_path", "--start-dir", "-d", default="./", help="Default: the current working directory (./). Specify the path to start searching for files. Will walk the directory tree from this path.")
```

### Nipper Command (`cli.commands.nipper`)

**Options:**
```python
@click.version_option(version=nipper_expander_version, prog_name="kpat_cli scripts", message="%(prog)s version %(version)s")  # BUG: Wrong prog_name
@click.option("_infile", "--in-file", "-f", default=None, help="Input file to process. If not specified, will search the current directory for CSV files.")
@click.option("source_files_path", "--start-dir", "-d", default="./", help="Default: the current working directory (./). Specify the path to start searching for files.  Will walk the directory tree from this path.")
```

### Scripts Command (`cli.commands.scripts`)

**Options:**
```python
@click.version_option(version=process_scripts_version, prog_name="kpat_cli scripts", message="%(prog)s version %(version)s")
@click.option("audit_config_file", "--conf", "-c", default="audit-all.yaml", help="Default: audit-all.yaml. Provide a YAML configuration file to specify the options. If only a file name, assumes analysis-toolit/conf.d location. Forces quiet mode.")
@click.option("source_files_path", "--start-dir", "-d", default="./", help="Default: the current working directory (./). Specify the path to start searching for files.  Will walk the directory tree from this path.")
@click.option("source_files_spec", "--filespec", "-f", default="*.txt", help="Default: *.txt. Specify the file specification to match. This can be a glob pattern.")
@click.option("--list-audit-configs", help="List all available audit configuration files and then exit", is_flag=True)
@click.option("--list-sections", help="List all sections headers found in FILESPEC and then exit", is_flag=True)
@click.option("--list-source-files", help="List all files found in FILESPEC and then exit", is_flag=True)
@click.option("--list-systems", help="Print system details found in FILESPEC and then exit", is_flag=True)
@click.option("--out-path", "-o", default="results/", help="Default: results/. Specify the output directory for the results files.")
@click.option("--verbose", "-v", default=False, help="Be verbose", is_flag=True)
```

## Analysis Results

### 1. Shared Options Identified

#### A. Version Options - **HIGH PRIORITY**
**Pattern Found**: Every command has its own version option with slight variations

**Current Implementation:**
```python
# RTF command
@click.version_option(version=rtf_to_text_version, prog_name="kpat_cli rtf-to-text", message="%(prog)s version %(version)s")

# Nipper command - BUG: Wrong prog_name!
@click.version_option(version=nipper_expander_version, prog_name="kpat_cli scripts", message="%(prog)s version %(version)s")

# Scripts command
@click.version_option(version=process_scripts_version, prog_name="kpat_cli scripts", message="%(prog)s version %(version)s")
```

**Issues Identified:**
- Nipper command has incorrect `prog_name` ("kpat_cli scripts" instead of "kpat_cli nipper")
- Code duplication across all commands
- Inconsistent version message formatting

**Recommendation**: 
Create a `@module_version_option` decorator:
```python
def module_version_option(module_version: str, command_name: str):
    """Standard version option decorator for CLI commands."""
    return click.version_option(
        version=module_version,
        prog_name=f"kpat_cli {command_name}",
        message="%(prog)s version %(version)s"
    )
```

#### B. File Input Options - **HIGH PRIORITY**
**Pattern Found**: Input file options with similar patterns across file-processing commands

**Current Implementation:**
```python
# Nipper command
@click.option("_infile", "--in-file", "-f", default=None, help="Input file to process. If not specified, will search the current directory for CSV files.")

# RTF command  
@click.option("_infile", "--in-file", "-f", default=None, help="Input RTF file to process. If not specified, will search the current directory for RTF files.")

# Scripts command - DIFFERENT PATTERN
@click.option("audit_config_file", "--conf", "-c", default="audit-all.yaml", help="Default: audit-all.yaml. Provide a YAML configuration file...")
```

**Issues Identified:**
- Identical parameter names and option patterns between nipper and RTF commands
- Scripts command uses different naming convention (`--conf/-c` vs `--in-file/-f`)
- Similar help text with only file type differences

**Recommendation**: 
Create an `@input_file_option` decorator:
```python
def input_file_option(
    param_name: str = "_infile",
    option_names: tuple[str, str] = ("--in-file", "-f"),
    file_type: str = "file",
    help_template: str = "Input {file_type} to process. If not specified, will search the current directory for {pattern} files.",
):
    """Standard input file option with customizable file type."""
```

#### C. Directory/Path Options - **HIGH PRIORITY**
**Pattern Found**: Start directory options with identical patterns

**Current Implementation:**
```python
# All three commands use identical options:
@click.option("source_files_path", "--start-dir", "-d", default="./", 
              help="Default: the current working directory (./). Specify the path to start searching for files. Will walk the directory tree from this path.")
```

**Issues Identified:**
- Exact code duplication across all commands
- Identical parameter names, defaults, and help text

**Recommendation**: 
Create a `@start_directory_option` decorator:
```python
def start_directory_option(
    param_name: str = "source_files_path",
    default: str = "./",
    help_text: str = "Default: the current working directory (./). Specify the path to start searching for files. Will walk the directory tree from this path.",
):
    """Standard start directory option."""
```

#### D. Output Path Options - **MEDIUM PRIORITY**
**Pattern Found**: Output directory specification (only in scripts command)

**Current Implementation:**
```python
# Scripts command only
@click.option("--out-path", "-o", default="results/", help="Default: results/. Specify the output directory for the results files.")
```

**Notes:**
- Only scripts command has explicit output path option
- Nipper and RTF commands handle output paths implicitly through their configuration
- Could be useful for other commands in the future

**Recommendation**: 
Create an `@output_directory_option` decorator for commands that need explicit output control:
```python
def output_directory_option(
    param_name: str = "out_path", 
    default: str = "results/",
    help_text: str = "Default: results/. Specify the output directory for the results files.",
):
    """Standard output directory option."""
```

#### E. Verbose Options - **MEDIUM PRIORITY**
**Pattern Found**: Command-specific verbose option (currently only in scripts command)

**Current Implementation:**
```python
# Scripts command only
@click.option("--verbose", "-v", default=False, help="Be verbose", is_flag=True)
```

**Notes:**
- Currently only scripts command has a local verbose option
- Could be useful for future commands that need verbose output control

**Recommendation**: 
Create a `@verbose_option` decorator for commands that need verbose output control:
```python
def verbose_option(
    param_name: str = "verbose",
    help_text: str = "Enable verbose output including debug messages",
):
    """Standard verbose option for commands that need detailed output control."""
    return click.option(
        "--verbose", "-v",
        param_name,
        is_flag=True,
        default=False,
        help=help_text
    )
```

### 2. Command-Specific Options (Should NOT be Centralized)

#### Scripts Command Unique Options
These are domain-specific and should remain as individual options:
- `--filespec/-f` - File specification pattern (conflicts with input file pattern)
- `--list-audit-configs` - List available audit configurations
- `--list-sections` - List section headers  
- `--list-source-files` - List discovered files
- `--list-systems` - List discovered systems

**Note**: The `--verbose/-v` option in scripts command should use the new `@verbose_option` decorator rather than being implemented directly.

#### Global Options (Correctly Positioned)
These should remain as global options:
- `--version` - Global version display
- `--skip-update-check` - Skip update checking  
- `--quiet/-q` - Global quiet mode

### 3. Option Naming and Default Patterns

#### Consistent Patterns Found
- **Short options**: `-f` (file), `-d` (directory), `-o` (output), `-v` (verbose), `-c` (config)
- **Long options**: `--in-file`, `--start-dir`, `--out-path`, `--verbose`, `--conf`
- **Default values**: `"./"` (directories), `"results/"` (output), `None` (input files)
- **Boolean flags**: `--list-*`, `--skip-*` patterns

#### Inconsistencies Found
1. **Scripts vs Others**: Uses `--conf/-c` instead of `--in-file/-f` for input
2. **Version bug**: Nipper command has incorrect `prog_name`
3. **Help text**: Minor variations in phrasing and formatting

### 4. Integration with Existing Utilities

The decorators should integrate with current shared utilities:
- `cli.common.config_validation.validate_program_config()` - Parameter validation
- `cli.common.config_validation.handle_fatal_error()` - Error handling  
- `cli.common.file_selection.get_input_file()` - File discovery logic
- `cli.utils.batch_processing` - Multi-file operations

## Recommendations for Implementation

### Phase 1: Core Decorators (High Priority)

1. **@module_version_option** - Fix version inconsistencies and reduce duplication
2. **@input_file_option** - Standardize file input patterns (careful with scripts command)
3. **@start_directory_option** - Eliminate exact code duplication

### Phase 2: Enhanced Options (Medium Priority)

1. **@output_directory_option** - For commands needing explicit output control
2. **@verbose_option** - For commands needing verbose output control (currently scripts)
3. **@file_listing_options** - Consider grouping scripts command's list options

### Phase 3: Validation and Documentation

1. Update all commands to use new decorators
2. Ensure backward compatibility maintained
3. Add comprehensive tests for decorator functionality
4. Update CLI documentation

## Current State Assessment

### Strengths
- Consistent error handling patterns across commands
- Good separation of CLI logic from business logic
- Effective use of shared utilities (config validation, file selection)
- Rich output formatting with good user experience

### Issues to Address
1. **Version bug** in nipper command (wrong prog_name)
2. **Code duplication** in option definitions
3. **Inconsistent patterns** between scripts and other commands

## Files Requiring Changes

### Implementation
- `src/kp_analysis_toolkit/cli/common/decorators.py` - New decorator implementations

### Command Updates  
- `src/kp_analysis_toolkit/cli/commands/scripts.py` - Apply decorators (including @verbose_option)
- `src/kp_analysis_toolkit/cli/commands/nipper.py` - Apply decorators, fix version bug
- `src/kp_analysis_toolkit/cli/commands/rtf_to_text.py` - Apply decorators

### Testing
- `tests/cli/common/test_decorators.py` - New comprehensive test module
- Update existing command tests to verify decorator behavior
- Test backward compatibility

## Conclusion

The analysis reveals significant opportunities for improvement through decorator centralization:

**Immediate Impact:**
- Fix the version display bug in nipper command
- Eliminate exact code duplication (especially start directory options)  
- Standardize file input patterns while respecting command-specific needs
- Provide reusable verbose option for commands that need detailed output control

**Long-term Benefits:**  
- Easier maintenance and consistency across commands
- Simplified addition of new commands with standard option patterns
- Better user experience through consistent interface
- Reusable components for future toolkit additions

**Key Success Factors:**
- Maintain backward compatibility
- Respect command-specific needs (like scripts' different input pattern)  
- Integrate with existing validation and error handling utilities
- Comprehensive testing of new decorators

The empty `cli.common.decorators` module is ready for implementation of these recommendations.

## Recommended Decorator Implementations

### High Priority Decorators

#### 1. Module Version Option
```python
def module_version_option(module_version: str, command_name: str):
    """Standard version option decorator for CLI commands.
    
    Args:
        module_version: Version string from the module's __version__
        command_name: Name of the command (e.g., "scripts", "nipper", "rtf-to-text")
        
    Returns:
        Click decorator for version option
    """
    return click.version_option(
        version=module_version,
        prog_name=f"kpat_cli {command_name}",
        message="%(prog)s version %(version)s"
    )

# Usage example:
# @module_version_option(rtf_to_text_version, "rtf-to-text")
```

#### 2. Start Directory Option  
```python
def start_directory_option(
    param_name: str = "source_files_path",
    default: str = "./",
    help_text: str = "Default: the current working directory (./). Specify the path to start searching for files. Will walk the directory tree from this path.",
):
    """Standard start directory option for file processing commands.
    
    Args:
        param_name: Parameter name for the option (default: "source_files_path")
        default: Default directory path (default: "./")
        help_text: Help text for the option
        
    Returns:
        Click decorator for start directory option
    """
    return click.option(
        "--start-dir", "-d",
        param_name,
        default=default,
        help=help_text
    )

# Usage example:
# @start_directory_option()
```

#### 3. Input File Option
```python
def input_file_option(
    param_name: str = "_infile",
    file_type: str = "file",
    file_extension: str = None,
    help_template: str = "Input {file_type} to process. If not specified, will search the current directory for {file_pattern} files.",
):
    """Standard input file option for file processing commands.
    
    Args:
        param_name: Parameter name for the option (default: "_infile")
        file_type: Type of file being processed (e.g., "RTF", "CSV")
        file_extension: File extension pattern (defaults to file_type if not provided)
        help_template: Template for help text with {file_type} and {file_pattern} placeholders
        
    Returns:
        Click decorator for input file option
    """
    file_pattern = file_extension or file_type
    help_text = help_template.format(file_type=file_type, file_pattern=file_pattern)
    
    return click.option(
        "--in-file", "-f",
        param_name,
        default=None,
        help=help_text
    )

# Usage examples:
# @input_file_option(file_type="RTF")
# @input_file_option(file_type="CSV") 
```

### Medium Priority Decorators

#### 4. Output Directory Option
```python
def output_directory_option(
    param_name: str = "out_path",
    default: str = "results/",
    help_text: str = "Default: results/. Specify the output directory for the results files.",
):
    """Standard output directory option for commands that need explicit output control.
    
    Args:
        param_name: Parameter name for the option (default: "out_path")
        default: Default output directory (default: "results/")
        help_text: Help text for the option
        
    Returns:
        Click decorator for output directory option
    """
    return click.option(
        "--out-path", "-o",
        param_name,
        default=default,
        help=help_text
    )

# Usage example:
# @output_directory_option()
```

#### 5. Verbose Option
```python
def verbose_option(
    param_name: str = "verbose",
    help_text: str = "Enable verbose output including debug messages",
):
    """Standard verbose option for commands that need detailed output control.
    
    Args:
        param_name: Parameter name for the option (default: "verbose")
        help_text: Help text for the option
        
    Returns:
        Click decorator for verbose option
    """
    return click.option(
        "--verbose", "-v",
        param_name,
        is_flag=True,
        default=False,
        help=help_text
    )

# Usage example:
# @verbose_option()
```

### Composite Decorators (Future Enhancement)

#### 6. File Processing Command (Potential Composite)
```python
def file_processing_command(
    module_version: str,
    command_name: str, 
    file_type: str,
    file_extension: str = None,
    include_output_option: bool = False,
    include_verbose_option: bool = False,
):
    """Composite decorator combining common file processing options.
    
    Args:
        module_version: Version string from the module's __version__
        command_name: Name of the command
        file_type: Type of file being processed  
        file_extension: File extension pattern (optional)
        include_output_option: Whether to include output directory option
        include_verbose_option: Whether to include verbose option
        
    Returns:
        Composite decorator applying multiple standard options
    """
    def decorator(func):
        # Apply decorators in reverse order (inner to outer)
        func = start_directory_option()(func)
        func = input_file_option(file_type=file_type, file_extension=file_extension)(func)
        func = module_version_option(module_version, command_name)(func)
        
        if include_output_option:
            func = output_directory_option()(func)
        if include_verbose_option:
            func = verbose_option()(func)
            
        return func
    return decorator

# Usage examples:
# @file_processing_command(rtf_to_text_version, "rtf-to-text", "RTF")
# @file_processing_command(process_scripts_version, "scripts", "configuration", "YAML", 
#                         include_output_option=True, include_verbose_option=True)
```
