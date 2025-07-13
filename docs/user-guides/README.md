# User Guides

Ready to start analyzing audit data? These guides provide step-by-step instructions for installing, configuring, and using each module of the toolkit.

## Getting Started

**New to the toolkit?** Start here:
- **[Installation](installation.md)** - Set up the toolkit on any system
- **[Updating](updating.md)** - Keep the toolkit current with latest features

## Module Guides

Pick the module that matches the data being analyzed:

### 🔍 Process Scripts
**Best for:** OS audit script output, system configuration files, log analysis
- **[Process Scripts Guide](process-scripts.md)** - Pattern searching and automated Excel reporting

### 🔧 Nipper Expander  
**Best for:** Network vulnerability scans, device security assessments
- **[Nipper Expander Guide](nipper-expander.md)** - Transform CSV exports for analysis

### 📄 RTF to Text Converter
**Best for:** Configuration files in RTF format, document standardization
- **[RTF to Text Guide](rtf-to-text.md)** - Convert documents to plain text

## Quick Reference

Get help anytime with built-in command assistance:

```bash
# Main help - see all available modules
kpat_cli --help

# Module-specific help with all options
kpat_cli scripts --help
kpat_cli nipper --help
kpat_cli rtf-to-text --help
```

## Typical Audit Workflows

**System Security Assessment:**
1. **Data Collection** → Run appropriate audit scripts on target systems
2. **Analysis** → Process collected files with Process Scripts module
3. **Reporting** → Review generated Excel workbooks for findings

**Network Security Assessment:**
1. **Scanning** → Generate Nipper vulnerability reports
2. **Processing** → Expand CSV exports with Nipper Expander module  
3. **Analysis** → Use Excel pivot tables for vulnerability analysis

**Configuration Review:**
1. **Collection** → Gather device configurations (often RTF format)
2. **Conversion** → Standardize files with RTF to Text module
3. **Analysis** → Search configuration files with Process Scripts

## Getting Help

**Having trouble?**
- Check the specific module guide for detailed instructions
- Review [Troubleshooting](../troubleshooting/README.md) for common problems
