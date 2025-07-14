# Troubleshooting - Common Issues

## All Tools

### No Files Found

Analysis toolkit searches the current folder for related files.  All of the tools in the toolkit can be pointed to a different folder, as follows

**Process Scripts**

List all detected files in another folder
```powershell
# Check file specification and directory
kpat_cli scripts --list-source-files --start-dir C:\Your\Folder
```

**Nipper Expander**

Find all CSV files in another folder
```powershell
kpat_cli nipper --start-dir C:\Your\Folder
```

**RTF to Text**

Find all source RTF files in another folder
```powershell
kpat_cli rtf-to-text --start-dir C:\Your\Folder
```

## Process Scripts

### System detection failures

Use the `--list-systems` and `--verbose` commands together to get a detailed list of what systems the tool thinks it's found:
```bash
# Check system information extraction
kpat_cli scripts --list-systems --verbose
```

**Exmplae Output**
```powershell
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ System Name                   ┃ File Hash           ┃ Details                                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ test_good_file                │ edea6c6661f25ac2... │ file: C:\Users\RandyBartels\Downloads\git ...             │
│                               │                     │ test_good_file.txt                                        │
│                               │                     │ encoding: utf_16                                          │
│                               │                     │ system_id: 0f51cf97-5199-4481-9798-e7fb9d7333ff           │
│                               │                     │ os_family: Linux                                          │
│                               │                     │ system_os: (none)                                         │
│                               │                     │ ... and 9 more                                            │
│ oracle9-0.6.21                │ 2ae1ce4b68b6c556... │ file: C:\Users\RandyBartels\Downloads\git ...             │
│                               │                     │ oracle9-0.6.21.txt                                        │
│                               │                     │ encoding: utf-8                                           │
│                               │                     │ system_id: 1c68a652-5a45-44fe-82ba-dccfc54add94           │
│                               │                     │ os_family: Linux                                          │
│                               │                     │ system_os: Oracle Linux Server 9.2                        │
│                               │                     │ ... and 9 more                                            │
```

Report any discrepancies at [GitHub Issues](https://github.com/kirkpatrickprice/analysis-toolkit/issues)

### Verbose Options

Enable verbose mode for detailed processing information:
```bash
kpat_cli scripts --verbose --conf your-config.yaml
```
