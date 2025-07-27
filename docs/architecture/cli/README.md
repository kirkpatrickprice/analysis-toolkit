# CLI Architecture Documentation

This directory contains comprehensive architecture documentation for the KP Analysis Toolkit's Command Line Interface (CLI) implementation.

## Overview

The CLI architecture is built on Rich-Click (enhanced Click framework) with custom solutions to address Rich-Click's limitations in multi-command CLI structures. The system provides consistent user experience through shared decorators, grouped help displays, and integrated Rich output formatting.

## Architecture Documents

### 🏗️ [CLI Architecture Patterns](cli-architecture-patterns.md)
**Main CLI architecture documentation covering:**

- Rich-Click integration with Click 8.x framework
- Multi-command group structure and routing
- Dependency injection integration with application container
- Rich output service integration for consistent formatting
- Command pattern implementation with shared utilities

**Key Topics:** Multi-command CLI, Rich-Click configuration, dependency injection, command patterns

### 🆘 [CLI Help System](cli-help-system.md)
**Custom help system architecture addressing Rich-Click limitations:**

- Callback-based help interception working around Rich-Click multi-command issues
- Custom grouped help display with Rich panels
- Option group configuration and display patterns
- Fallback mechanisms when option groups aren't configured

**Key Topics:** Help callbacks, Rich panel display, option group matching, fallback systems

### 📋 [CLI Option Groups](cli-option-groups.md)
**Option grouping architecture for organizing CLI help displays:**

- Logical grouping strategies by functional purpose
- Standard group patterns across commands
- Command-specific group configurations
- Hierarchical organization from most to least commonly used options

**Key Topics:** Functional grouping, consistency patterns, group configuration, user experience

### 🎨 [CLI Decorator Patterns](cli-decorator-patterns.md)
**Shared decorator patterns for consistent CLI options:**

- Reusable option decorators reducing code duplication
- Parameterized decorators for customization while maintaining consistency
- Decorator composition patterns for building complete command interfaces
- Integration with help system and option grouping

**Key Topics:** Decorator factories, composition patterns, consistency enforcement, parameterization

## Implementation Overview

### Current Architecture Stack

- **Click 8.x** - Core CLI framework
- **Rich-Click 1.8.x** - Enhanced CLI with Rich formatting
- **Rich Library** - Professional terminal output and formatting
- **Custom Help System** - Workaround for Rich-Click multi-command limitations
- **Dependency Injection** - Application container for service access through `core.services.rich_output`

### Key Design Patterns

1. **Multi-Command CLI Group** - Root command orchestrating all sub-commands
2. **Custom Help Callbacks** - Intercept --help requests for grouped displays
3. **Shared Option Decorators** - Consistent option patterns across commands
4. **Rich Output Integration** - Professional formatting through DI container
5. **Option Group Configuration** - Centralized grouping for better UX

### Current User-Accessible Commands

- **`scripts`** - Process collector script results (complex option groups)
- **`rtf-to-text`** - Convert RTF files to text (simple option groups)
- **`nipper`** - Process Nipper CSV exports (simple option groups)

## Rich-Click Limitations and Workarounds

### Known Issues

- **Rich-Click 1.8.9** doesn't support option groups in Click Group structures
- Multi-command CLI help displays don't automatically group options
- Standard Rich-Click configuration ignored in group contexts

### Current Solutions

- **Custom Help System** using Click callbacks to intercept `--help` requests
- **Manual Rich Panel Rendering** for grouped option displays
- **Centralized Option Group Configuration** stored in click.rich_click.OPTION_GROUPS
- **Fallback Display System** when option groups aren't configured

## Future Evolution

### Planned Enhancements

- **Rich-Click Upgrade** when multi-command option grouping is supported
- **Dynamic Option Group Detection** based on command introspection
- **Plugin System** for custom help formatters and option patterns
- **Command Template System** for rapid new command development

### Extension Points

- **New Command Integration** following established decorator patterns
- **Custom Option Groups** for specialized command requirements
- **Enhanced Help Formatting** with additional Rich components
- **Automated Option Discovery** for reduced configuration overhead

## Quick Navigation

- **New CLI Developer**: Start with [Architecture Patterns](cli-architecture-patterns.md)
- **Help System Issues**: See [Help System](cli-help-system.md)
- **Option Organization**: Check [Option Groups](cli-option-groups.md)
- **Consistent Options**: Review [Decorator Patterns](cli-decorator-patterns.md)

## Related Documentation

- **[Concurrency Architecture](../concurrency/README.md)** - Parallel processing integration with CLI commands
- **[Development Standards](../../development/README.md)** - Code standards and testing procedures
- **[Implementation Plans](../../implementation/README.md)** - CLI refactoring and migration plans
- **[User Guides](../../user-guides/README.md)** - End-user CLI documentation
