# User Guides

Welcome to the KP Analysis Toolkit user guides! These guides provide step-by-step instructions for installing, configuring, and using each module of the toolkit.

## Getting Started

- **[Installation](installation.md)** - How to install the toolkit on your system
- **[Updating](updating.md)** - Keeping the toolkit up to date

## Module Guides

### 🔍 Process Scripts
- **[Process Scripts Guide](process-scripts.md)** - Comprehensive guide for analyzing OS audit data

### 🔧 Nipper Expander  
- **[Nipper Expander Guide](nipper-expander.md)** - Processing Nipper CSV exports

### 📄 RTF to Text Converter
- **[RTF to Text Guide](rtf-to-text.md)** - Converting RTF files to plain text

## Quick Reference

Each module can be run with `--help` to see all available options:

```bash
# Main help
kpat_cli --help

# Module-specific help
kpat_cli scripts --help
kpat_cli nipper --help
kpat_cli rtf-to-text --help
```

## Common Workflows

Most audit workflows follow this pattern:

1. **Data Collection** - Use the appropriate audit scripts to collect system data
2. **Processing** - Use Process Scripts to analyze the collected data
3. **Network Analysis** - Use Nipper Expander for network device findings
4. **Format Conversion** - Use RTF to Text for document format issues
5. **Reporting** - Generate Excel reports for analysis and findings

## Need Help?

- Check the specific module guide for detailed instructions
- Review [Troubleshooting](../troubleshooting/README.md) for common issues
- Consult the [API Reference](../api/README.md) for programmatic usage
