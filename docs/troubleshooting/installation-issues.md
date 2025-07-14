# Troubleshooting - Installation Issues

## Dependency Problems

`pipx` should handle all required dependencies, but if you receive any `ImportError` messages when using the toolkit, report them to [GitHub Issues](https://github.com/kirkpatrickprice/analysis-toolkit/issues).

## PIPX Command not Found

**Error Message**

```powershell
pipx ensurepath
pipx : The term pipx is not recognized as the name of a cmdlet, 
function, script file, or operable program. Check the spelling
of the name, or if a path was included, verify that the path
is correct and try again.
```

**Workaround**

```powershell
C:\Users\<YOUR_USERNAME_HERE>\Appdata\Roaming\Python\Python312\Scripts\pipx.exe ensurepath 
```

If this doesn't work, replace `Python312` with `Pyton313` and try again.  You might have a newer version of Python installed than when this guide was written.

**Explanation**

PIPX is installed under the `%APPDATA%\Python` folder, but this folder wasn't successfully added to the command search list for Powershell.  The workaround directly references the `pipx.exe` command in its expected location and fixes the command search path issue.