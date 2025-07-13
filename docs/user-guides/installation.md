# Installing the KP Analysis Toolkit

## Requirements

### System Requirements
The toolkit is built on Python and supports cross-platform operation:
- **Primary development platform**: Windows
- **Supported platforms**: Windows, macOS, Linux
- **Testing coverage**: All platforms tested via CI/CD pipeline

### Prerequisites
- **Python 3.12 or higher**
- **pipx** (Python application installer)

### Recommended Tools
For Windows users, we recommend using the [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701) from the Microsoft Store for a better command-line experience.

## Installation
The easiest way to use the toolkit is to install Python's `pipx` package installer.  This utility will handle Python-specific details and install the toolkit from the official repository on [Python Package Index](https://pypi.org/project/kp-analysis-toolkit/)

### Installing pipx

**Windows and other platforms:**

```powershell
pip install pipx
pipx ensurepath
# Restart PowerShell to use the updated PATH
```

**Ubuntu and Debian-based systems:**

```bash
# Install pipx (if not already installed via package manager)
sudo apt install pipx  # or use the package manager appropriate to your OS (e.g. brew on MacOS)
pipx ensurepath
# Restart terminal to update PATH
```

### Installing the Toolkit

The toolkit is distributed via PyPI and can be installed using pipx:

**Windows PowerShell:**

```powershell
pipx install kp-analysis-toolkit
```

**Linux/macOS:**

```bash
pipx install kp-analysis-toolkit
```

### Test the installation
```bash
kpat_cli --version