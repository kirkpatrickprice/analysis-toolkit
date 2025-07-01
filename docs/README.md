# KP Analysis Toolkit Documentation

This directory contains comprehensive documentation for the KP Analysis Toolkit, organized by category for easy navigation.

## 📁 Documentation Structure

### `/architecture/`
High-level architectural decisions, design patterns, and system overviews.
- System architecture diagrams
- Component interaction patterns
- Design philosophy and principles

### `/implementation/`
Detailed implementation notes, refactoring summaries, and technical deep-dives.
- **`parallel-engine-refactor.md`** - Complete refactor from threads to processes
- **`interrupt-handling-enhancement.md`** - Enhanced CTRL-C handling implementation
- **`progress-bar-improvements.md`** - Fixed-width progress bar formatting
- **`rich-output-thread-safety.md`** - Thread-safe singleton implementation

### `/development/`
Developer guides, coding standards, and development workflow documentation.
- Coding guidelines and best practices
- Testing strategies and frameworks
- CI/CD pipeline documentation
- Contributing guidelines

## 📋 Quick Reference

### Recent Major Changes
- **Parallel Engine Refactor** (2025-06): Moved from ThreadPoolExecutor to ProcessPoolExecutor-only
- **Interrupt Handling Enhancement** (2025-06): Two-level CTRL-C handling with graceful cancellation
- **Progress Bar Improvements** (2025-06): Fixed-width formatting for stable UI
- **Thread Safety Improvements** (2025-06): Process-safe RichOutput singleton

### Key Implementation Notes
- All parallel execution uses ProcessPoolExecutor for better isolation
- Interrupt handling provides immediate feedback with optional force termination
- Progress bars use fixed-width formatting for consistent display
- RichOutput singleton is process-safe with atomic property updates

## 🔗 Related Files
- `README.md` - General project overview and usage
- `CHANGELOG.md` - Version history and release notes
- `tests/` - Comprehensive test suite
- `src/` - Source code with inline documentation
