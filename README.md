# analysis-toolkit

The analysis toolkit is a collection of scripts designed to assist auditors analyze the results of the KP system auditing scripts maintained at:
* [Linux](https://github.com/kirkpatrickprice/linux-audit-scripts) 
* [Windows](https://github.com/kirkpatrickprice/windows-audit-scripts)
* [MacOS](https://github.com/kirkpatrickprice/macos-auditor)

## Critical dependencies ##
* Shell: a recent version of `bash`
* Python: A recent release of version 3.  Both 3.10 (Ubuntu 22.04) and 3.12+ should be fine
* Misc. commands:   `grep` `echo` `awk` `sort`

The scripts have been tested and are usually used on Ubuntu distributions. They were developed on WSL instances of Ubuntu 20.04 and 22.04.  YMMV on other distributions or versions, but I don't foresee any problems, say, on a MacOS Terminal prompt.

For KP auditors, I strongly recommend following the [Getting started with WSL](https://kirkpatrickprice.atlassian.net/l/c/jP0AuG7j) and [Bashing Our Way to Efficient Audits](https://kirkpatrickprice.atlassian.net/l/c/6oaQWQpv) pages on Confluence.

I also recommend that you use the Windows Terminal app available from the Microsoft Store.  Among other numerous benefits, this will allow to click on hyperlinks created by some of the tools.

## Installation ##
Prequisites:
* A supported version of Python
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
Change to the analysis-toolkit directory

`pipx update kp-analysis-toolkit`

## Using the toolkit scripts ##
Each toolkit script includes a "help" function to explain the options.

`<script> -h`