# Gradual MyPy Implementation Workflow

This document provides a practical workflow for implementing type hints and mypy checking in the KP Analysis Toolkit.

## Quick Start

### 1. Check Current Status
```powershell
# Check all modules with current gradual settings
.\scripts\type-check.ps1

# Check specific module
.\scripts\type-check.ps1 -Target models
```

### 2. Generate Coverage Report
```powershell
# Generate HTML report to see current type coverage
.\scripts\type-check.ps1 -Report
# Open mypy-report/index.html in browser
```

### 3. VS Code Integration
Use VS Code tasks for integrated type checking:
- `Ctrl+Shift+P` → "Tasks: Run Task" → "mypy_check_all"
- Or use the specific module tasks: `mypy_check_models_strict`, `mypy_check_utils`, etc.

## Implementation Phases

### Phase 1: Models (Already Complete)
The models module is already well-typed and uses strict checking:
- All Pydantic models inherit from `KPATBaseModel`
- Proper type annotations throughout
- Strict mypy settings enabled

**Status**: ✅ Complete

### Phase 2: Utils Module (High Priority)
Critical utility functions that are used throughout the codebase.

**Steps**:
1. Run `.\scripts\type-check.ps1 -Target utils` to see current issues
2. Add type hints to function signatures
3. Add return type annotations
4. Fix any mypy errors
5. Gradually increase strictness in mypy.ini

**Current Settings**: Medium strictness
**Target**: Strict mode (like models)

### Phase 3: Core Module (High Priority)  
Application core functionality including dependency injection.

**Steps**:
1. Run `.\scripts\type-check.ps1 -Target core`
2. Focus on public APIs first
3. Add type hints to container and service classes
4. Test with dependency injection framework

**Current Settings**: Medium strictness
**Target**: Strict mode

### Phase 4: CLI Module (Medium Priority)
Command-line interface and user-facing functionality.

**Steps**:
1. Run `.\scripts\type-check.ps1 -Target cli`
2. Add type hints to command functions
3. Handle Click decorator typing (use `# type: ignore` if needed)
4. Focus on data flow between commands

**Current Settings**: Basic strictness
**Target**: Medium strictness

### Phase 5: Process Scripts (Medium Priority)
Complex business logic for file processing.

**Steps**:
1. Run `.\scripts\type-check.ps1 -Target process_scripts`
2. Add type hints to main processing functions
3. Use predefined types from `kp_analysis_toolkit.models.types`
4. Focus on data transformation functions

**Current Settings**: Basic strictness
**Target**: Medium strictness

### Phase 6: Legacy Modules (Lower Priority)
Older modules that may require more extensive refactoring.

**Approach**:
- Use `# type: ignore` liberally during initial passes
- Add basic type hints to public interfaces
- Gradually improve internal implementations

## Daily Workflow

### Before Committing Code
```powershell
# Quick check of modules you've modified
.\scripts\type-check.ps1 -Target utils  # if you modified utils

# Full check before major commits
.\scripts\type-check.ps1
```

### Weekly Progress Review
```powershell
# Generate coverage report
.\scripts\type-check.ps1 -Report

# Check progress in mypy-report/index.html
# Focus on modules with low coverage
```

### When Adding New Code
1. **Always add type hints** to new functions and classes
2. **Use predefined types** from `kp_analysis_toolkit.models.types`
3. **Inherit from `KPATBaseModel`** for new data models
4. **Run type checking** on the specific module you're working on

## Common Patterns

### Function Signatures
```python
from pathlib import Path
from kp_analysis_toolkit.models.types import PathLike, ResultData

def process_file(file_path: PathLike, encoding: str = "utf-8") -> ResultData:
    """Process a file and return structured data."""
    pass
```

### Class Definitions
```python
from kp_analysis_toolkit.models.base import KPATBaseModel
from pydantic import Field

class ProcessingConfig(KPATBaseModel):
    """Configuration for file processing."""
    input_path: Path
    max_workers: int = Field(default=4, ge=1, le=16)
```

### Handling Legacy Code
```python
def legacy_function(data):  # type: ignore
    """Legacy function - add type hints gradually."""
    # For now, use type: ignore to avoid mypy errors
    # TODO: Add proper type hints in next refactoring
    pass
```

## Troubleshooting

### Common MyPy Errors

1. **"Function is missing a return type annotation"**
   - Add `-> None` for functions that don't return values
   - Add appropriate return type for functions that do

2. **"Untyped function definition"**
   - Add type hints to function parameters
   - Start with `Any` if unsure, refine later

3. **"Cannot determine type of expression"**
   - Use explicit type annotations for complex expressions
   - Consider using `cast()` for complex type assertions

### Getting Help
- Check the [Type Hints Requirements](./type-hints-requirements.md) document
- Use `mypy --help` for command-line options
- Reference the MyPy documentation: https://mypy.readthedocs.io/

## Progress Tracking

Use this checklist to track your progress:

- [ ] **Phase 1**: Models module (✅ Already complete)
- [ ] **Phase 2**: Utils module - basic type hints added
- [ ] **Phase 2**: Utils module - strict mode enabled
- [ ] **Phase 3**: Core module - basic type hints added  
- [ ] **Phase 3**: Core module - strict mode enabled
- [ ] **Phase 4**: CLI module - basic type hints added
- [ ] **Phase 4**: CLI module - medium strictness enabled
- [ ] **Phase 5**: Process Scripts - basic type hints added
- [ ] **Phase 5**: Process Scripts - medium strictness enabled
- [ ] **Phase 6**: Legacy modules - basic coverage achieved
- [ ] **Final**: Full strict mode enabled project-wide

## Benefits Realized

As you progress through the phases, you should notice:

1. **Better IDE Support**: Improved autocomplete and error detection
2. **Fewer Runtime Errors**: Type checking catches issues before runtime
3. **Improved Documentation**: Type hints serve as inline documentation
4. **Easier Refactoring**: Type system helps identify impact of changes
5. **Better Onboarding**: New developers can understand code faster
