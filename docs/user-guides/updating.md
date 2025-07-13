# Updating the KP Analysis Toolkit

## Automatic Update Checking
Starting with version 2.0, the toolkit automatically checks for updates on PyPI each time you run it. If a newer version is available, the toolkit will display upgrade instructions and exit.  You can bypass the version check with `--skip-update-check`.

The message will be similar to this:

```
📦 Update Available

┌─ Upgrade Instructions ──────────────────────────────────┐
│ Current version: 2.0.5                                  │
│ Latest version:  2.1.0                                  │
│                                                         │
│ To upgrade, run:                                        │
│ pipx upgrade kp-analysis-toolkit                        │
│                                                         │
│ Or if you want to skip this check in the future:        │
│ kpat_cli --skip-update-check                            │
└─────────────────────────────────────────────────────────┘

The application will now exit. Please run the upgrade command above 
and then run your command again.

Note: Upgrade checks can be disabled using the --skip-update-check option.
```

**Why does the toolkit exit instead of upgrading automatically?**
- **File locking**: When Python applications upgrade themselves while running, file locks can cause upgrade failures
- **Reliability**: Manual upgrades using `pipx upgrade` are more reliable and consistent
- **User control**: You have full control over when and how upgrades happen
- **Error handling**: `pipx` provides better error messages and troubleshooting information

## Manual Updates
Update manually using `pipx`:
```bash
pipx upgrade kp-analysis-toolkit
```

## Disabling Update Checks
Skip update checks for automated scripts or when you don't want to be prompted:
```bash
kpat_cli --skip-update-check scripts --help
```

**Note:** Update checking requires a network connection. Without network access, you may see a brief warning but the program continues normally.
