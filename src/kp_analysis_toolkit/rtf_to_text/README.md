# RTF to Text Converter

The RTF to Text converter is a subcommand of the KP Analysis Toolkit that converts Rich Text Format (RTF) files to plain text files using ASCII encoding.  A common-enough use case is when a customer provides a router/firewall configuration as an RTF document instead of as a plaintext file.

## Usage

### Basic Usage

Convert a specific RTF file:
```bash
kpat_cli rtf-to-text -f document.rtf
```

### Directory Scanning

Scan the current directory for RTF files:
```bash
kpat_cli rtf-to-text
```

Scan a specific directory:
```bash
kpat_cli rtf-to-text -d /path/to/directory
```

### Interactive Mode

When multiple RTF files are found in a directory, the tool will present an interactive menu:

1. Select a specific file by number
2. Choose "Process all files" to convert all RTF files in the directory
3. Press CTRL-C to quit

## Output

- Output files are created in the same directory as the input files
- Output file naming convention: `original_filename_converted-<timestamp>.txt`
- Files are encoded using ASCII encoding with error handling for non-ASCII characters

## Features

- **Automatic file discovery**: Scans directories for RTF files if no specific file is provided
- **Batch processing**: Option to process all RTF files in a directory at once
- **Error handling**: Graceful handling of invalid files and encoding issues
- **ASCII output**: Ensures compatibility with text processing tools
- **Pydantic validation**: Input validation using the project's standard data models

## Dependencies

- `striprtf`: Primary RTF parsing library (automatically installed)
- `charset-normalizer`: Used for intelligent encoding detection (already a project dependency)
- Fallback parser: Basic RTF parsing when striprtf is not available

## Examples

```bash
# Convert single file
kpat_cli rtf-to-text -f router_config.rtf

# Scan current directory and choose interactively
kpat_cli rtf-to-text

# Scan specific directory
kpat_cli rtf-to-text -d /documents/rtf_files

# Show help
kpat_cli rtf-to-text --help
```
