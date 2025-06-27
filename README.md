# analysis-toolkit

The analysis toolkit is a Python application designed to assist auditors with analyzing the data we work with.  The toolkit currently includes:
* `scripts` -- Formerly known as `adv-searchfor`, this processes the results created by our OS-specific collection scripts
    * [Linux](https://github.com/kirkpatrickprice/linux-audit-scripts) 
    * [Windows](https://github.com/kirkpatrickprice/windows-audit-scripts)
    * [MacOS](https://github.com/kirkpatrickprice/macos-auditor)
* `nipper` -- Expands Nipper CSV files into a more usable format and saves them as a formatted Excel workbook.

## Critical dependencies ##
The Toolkit is built on Python and all development and testing was performed on Windows.  You can also run it on MacOS and Linux if that's your preference.

I also recommend that you use the Windows Terminal app available from the Microsoft Store.  This is a much better way of working at the command prompt than the terrible Console app that's built into Windows.

## Installation ##
Prequisites:
* A supported version of Python (>=3.12)
* Python's PIPX
    * Windows (and others where PIPX isn't installed by the OS package manager): `pip install pipx`
    * Ubuntu (and for other distro's where it's provided as an OS package): `sudo apt install pipx`

Installation is as simple as using Python's `PIPX` to install the package from PyPI.

### Windows PowerShell ### 
Assuming Python is already installed:
```
pip install pipx
pipx ensurepath
# Restart PowerShell window to get new PATH
pipx install kp-analysis-toolkit
```

### Ubuntu ### 
Or others where PIPX is provided by the OS package manager -- replace `apt` with other package manager as needed:
```
sudo apt install pipx
pipx ensurepath
# Restart shell prompt window to get new PATH
pipx install kp-analysis-toolkit
```

## Updating the toolkit ##

### Automatic Update Checking ###
Starting with version 2.0, the toolkit automatically checks for updates on PyPI each time you run it. If a newer version is available, you'll be prompted to upgrade:

```
📦 Update available: 2.0.0 → 2.0.1
Current version: 2.0.0
Latest version:  2.0.1

Would you like to upgrade now? [y/N]:
```

If you choose to upgrade:
- The toolkit will use `pipx` to upgrade the package automatically
- After a successful upgrade, the application will restart with the new version
- If the upgrade fails, you'll see an error message and can continue with the current version

### Manual Update ###
You can also update manually using pipx:

```bash
pipx upgrade kp-analysis-toolkit
```

### Disabling Update Checks ###
If you want to skip the update check (e.g., in automated scripts), use the `--skip-update-check` flag:

```bash
kpat_cli --skip-update-check scripts --help
```

**Note:** Update checking requires a network connection. If no network is available, you'll see a warning message but the program will continue normally.

## Using the toolkit scripts ##
After it's installed, you'll have a `kpat_cli.exe` command on Windows or just `kpat_cli` for MacOS/Linux.

To get help, just append `--help` to the end of the command.

```Powershell
kpat_cli.exe --help
```

While the defaults are usually good, you can adjust some parameters:

```bash
kpat_cli.exe scripts --help
```

... and so on