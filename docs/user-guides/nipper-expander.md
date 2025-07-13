# Nipper Expander

The Nipper Expander module is a specialized tool for processing Nipper CSV export files to create more detailed and analysis-friendly reports. It transforms Nipper's compact CSV format (where multiple devices may be listed in a single row) into an expanded format with one row per device per finding, making it easier to analyze vulnerabilities and findings using Excel pivot tables and other analysis tools.

## Overview

Nipper is a network security auditing tool that analyzes firewall and network device configurations to identify security vulnerabilities and configuration issues. Nipper's CSV export format often contains multiple affected devices on a single row, separated by line breaks. The Nipper Expander processes these files to create a more detailed format suitable for comprehensive analysis.

### What Nipper Expander Does

- **Expands multi-device findings** - Converts single rows with multiple devices into separate rows for each device
- **Preserves all finding data** - Maintains all original vulnerability information (Title, Rating, Finding, Impact, Ease, Recommendation)
- **Enables detailed analysis** - Creates Excel-friendly format perfect for pivot tables and filtering
- **Provides formatted output** - Generates professionally formatted Excel workbooks with proper headers and table formatting

## Usage

### Basic Usage

Scan the current directory for CSV files:
```bash
kpat_cli nipper
```

Process a specific Nipper CSV file:
```bash
kpat_cli nipper --in-file nipper-report.csv
```

Scan a specific directory:
```bash
kpat_cli nipper --start-dir /path/to/nipper/reports
```

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--in-file` | `-f` | Specific CSV file to process | Auto-detect |
| `--start-dir` | `-d` | Directory to search for CSV files | `./` |
| `--version` | | Show version information | |
| `--help` | | Show help message | |

### Interactive File Selection

When multiple CSV files are found in a directory, the tool provides an interactive menu:

```
Multiple CSV files found. Use the "--in-file <filename>" option to specify the input file or choose from below.
1 - /path/to/nipper-report1.csv
2 - /path/to/nipper-report2.csv

Choose a file or press CTRL-C to quit:
```

## Input Format

### Expected CSV Structure

Nipper Expander expects CSV files with the following columns:

- **Issue Title** - Name/title of the security finding
- **Devices** - Affected devices (may contain multiple devices separated by line breaks)
- **Rating** - Severity rating (Critical, High, Medium, Low)
- **Finding** - Detailed description of the vulnerability
- **Impact** - Description of potential security impact
- **Ease** - Assessment of exploitation difficulty
- **Recommendation** - Suggested remediation steps

### Sample Input Format

```csv
Issue Title,Devices,Rating,Finding,Impact,Ease,Recommendation
"2.3 Interfaces With No Filtering","firewall1
firewall2",Critical,"Network filtering rule lists can be assigned...","The network traffic from an attacker...","The network traffic would not be subjected...","KirkpatrickPrice recommends that all..."
```

## Output Format

### Excel Workbook Features

The expanded report is saved as an Excel workbook (.xlsx) with:

- **Professional formatting** - Formatted headers with freeze panes
- **Table structure** - Data organized as an Excel table for easy filtering
- **One row per device** - Each affected device gets its own row
- **Complete vulnerability data** - All original finding information preserved
- **Timestamped filename** - Output files include creation timestamp

### File Naming Convention

Output files follow the pattern:
```
<original_filename>_expanded-<timestamp>.xlsx
```

Examples:

- `nipper-report_expanded-20250628-143022.xlsx`
- `firewall-audit_expanded-20250628-143022.xlsx`

### Sample Output Structure

| Issue Title | Devices | Rating | Finding | Impact | Ease | Recommendation |
|------------|---------|--------|---------|--------|------|----------------|
| 2.3 Interfaces With No Filtering | firewall1 | Critical | Network filtering rule lists... | The network traffic from... | The network traffic would... | KirkpatrickPrice recommends... |
| 2.3 Interfaces With No Filtering | firewall2 | Critical | Network filtering rule lists... | The network traffic from... | The network traffic would... | KirkpatrickPrice recommends... |

## Data Processing Logic

### Expansion Algorithm

1. **Read CSV file** - Loads the original Nipper CSV export
2. **Parse device lists** - Identifies multiple devices in the "Devices" column
3. **Split by line breaks** - Separates devices that are on different lines
4. **Create individual rows** - Generates a new row for each device/finding combination
5. **Preserve all data** - Maintains all original vulnerability information
6. **Export to Excel** - Creates formatted Excel workbook with expanded data

### Handling Edge Cases

- **Single device findings** - Preserved as-is without modification
- **Empty device fields** - Handled gracefully without creating empty rows
- **Large CSV files** - Memory-efficient processing for large datasets
- **Special characters** - Proper encoding handling for international characters

## Analysis Benefits

### Excel Analysis Features

The expanded format enables powerful analysis capabilities:

- **Pivot Tables** - Analyze findings by device, severity, or finding type
- **Filtering** - Quick filtering by device names, ratings, or keywords
- **Sorting** - Order findings by severity, device, or any other criteria
- **Charts and Graphs** - Visual representation of vulnerability distribution

### Use Cases

- **Device-specific remediation** - Focus on vulnerabilities affecting specific devices
- **Severity analysis** - Prioritize critical and high-severity findings
- **Compliance reporting** - Generate reports showing vulnerability status by device
- **Trend analysis** - Track remediation progress over time
- **Risk assessment** - Evaluate overall security posture by device or network segment

## Integration with Audit Workflows

### Typical Workflow

1. **Run Nipper audit** on network devices
2. **Export results** to CSV format from Nipper
3. **Process with Nipper Expander** to create detailed Excel report
4. **Analyze findings** using Excel pivot tables and filtering
5. **Generate remediation reports** for specific devices or finding types

### Compatibility

- **Nipper versions** - Compatible with CSV exports from various Nipper versions
- **CSV formats** - Handles standard CSV with quoted fields and line breaks
- **Excel versions** - Output compatible with Excel 2010 and newer
- **Operating systems** - Cross-platform support (Windows, macOS, Linux)

## Examples

### Process Single File

```bash
# Process a specific Nipper CSV file
kpat_cli nipper --in-file network-audit-2025.csv
```

### Auto-detect in Directory

```bash
# Let the tool find and process CSV files in current directory
kpat_cli nipper
```

### Scan Different Directory

```bash
# Look for CSV files in a specific directory
kpat_cli nipper --start-dir /audit-reports/2025/Q1
```

### Check Version

```bash
# Show version information
kpat_cli nipper --version
```

## Troubleshooting

### Common Issues

**No CSV files found:**
```bash
# Verify CSV files exist in the directory
ls *.csv
```

**File processing errors:**
```bash
# Check CSV file format and encoding
file your-nipper-file.csv
```

### Error Messages

- **"No CSV files found"** - No CSV files in the specified directory
- **"Error validating configuration"** - Invalid file path or permissions
- **"Error processing CSV file"** - Malformed CSV or unexpected format

## Related Tools

- **Nipper** - Network security auditing tool that generates the source CSV files
- **Process Scripts** - For analyzing other types of audit data
- **Excel** - For advanced analysis of the expanded reports
