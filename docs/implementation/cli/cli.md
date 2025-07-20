```
src/kp_analysis_toolkit/
├── cli/
│   ├── __init__.py                    # Main CLI entry point and command group
│   ├── main.py                        # Main CLI command definitions
│   ├── common/
│   │   ├── __init__.py               # Common utilities exports
│   │   ├── file_selection.py         # File discovery and selection logic
│   │   ├── config_validation.py      # Configuration validation helpers
│   │   ├── output_formatting.py      # Rich output formatting utilities
│   │   ├── decorators.py             # Common CLI decorators and options
│   │   ├── progress.py               # Progress tracking and summary display
│   │   └── types.py                  # CLI-specific type definitions
│   ├── commands/
│   │   ├── __init__.py               # Command registration
│   │   ├── nipper.py                 # Nipper-specific command (migrated)
│   │   ├── scripts.py                # Process scripts command (migrated)
│   │   └── rtf_to_text.py           # RTF conversion command (migrated)
│   └── utils/
│       ├── __init__.py               # CLI utility exports
│       ├── path_helpers.py           # Directory and path utilities
│       └── interactive.py            # User interaction helpers
```