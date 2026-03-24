# Installation Guide

## Overview

Installing KPAT is very simple, but requires the `uv` [Python package and project manager](https://docs.astral.sh/uv/).  Once installed, this utility will handle installing, updating and maintaining the Toolkit.

[Installation Video](https://youtu.be/SX4-PQj_cfE)

## Prerequisites

### System Requirements
- Windows 10 or later (recommended: Windows 11)
- PowerShell 5.1 or later
- Astral UV

### Knowledge Requirements
- Basic Powershell navigation ([PowerShell Primer](powershell-primer.md))

### Required Files/Data
- None

## Getting Started

### First Steps -- UV Installation

**NOTE for KP users: All installation steps are already completed for KP laptops**

1. Install Astral's UV from [UV documentation](https://docs.astral.sh/uv/) if not already installed 
    **NOTE:** The UV documentation includes instructions for MacOS, Windows, and Linux.
2. Launch a terminal session
    **Windows** Windows Terminal (already installed on Windows 11)
    **MacOS/Linux** Open a terminal session
3. Run the following commands to install KP Analysis Toolkit

    ```powershell
    # Install KPAT using UV
    uv tool install kp-analysis-toolkit
    ```

This will download the installation packages from the official [Python Package Index](https://pypi.org/project/kp-analysis-toolkit/).

### Test the Installation
```powershell
# Test the installation
kpat_cli --version
```

![KPAT Version](../assets/kpat-version.png "KPAT Version")

***Note:*** The first attempt to run the command may take a bit longer as Windows Defender performs an AV scan on the program files.

### Basic Usage

#### Primary Command
The toolkit is available under one common command: `kpat_cli`.  Help is available throughout by appending `--help` to the end of any other command:

```powershell
# Access the help pages
kpat_cli --help
```

![Top-Level Help](../assets/kpat-help.png "Top-level Help")

## Related Documentation

- [Installation Guide](installation.md)
- [Processing Script Results](scripts.md)
- [Other Related Guides](index.md)

---
