# RichOutput Singleton Pattern Review

## Current Implementation Analysis

### Global Singleton Pattern
The current `RichOutput` implementation uses a global singleton pattern with the following characteristics:

```python
# Global instance for convenience
_rich_output: RichOutput | None = None
_creation_lock = threading.Lock()

def get_rich_output(*, verbose: bool | None = None, quiet: bool | None = None) -> RichOutput:
    """Get or create the global RichOutput instance with thread-safe parameter updates."""
    global _rich_output
    # Double-checked locking pattern
    # ...
```

### Usage Patterns Throughout Codebase

1. **Direct getter calls**: Most code calls `get_rich_output()` to obtain the singleton
2. **Convenience functions**: Module-level functions like `info()`, `warning()`, `error()` that wrap the singleton
3. **Mixed patterns**: Some modules import `get_rich_output`, others import convenience functions
4. **Context passing**: The parallel engine passes the RichOutput instance through a `ProcessingContext`

### Current Issues

1. **Hidden global state**: The singleton creates implicit dependencies that are hard to test and reason about
2. **Import-time side effects**: Getting the singleton during import can cause ordering issues
3. **Testing complexity**: Requires special handling to reset/mock the global state in tests
4. **Thread safety complexity**: While implemented, adds complexity to what should be simple logging
5. **Mixed usage patterns**: Inconsistent use across the codebase (some use convenience functions, others use direct calls)

## Improvement Options

### Option 1: Dependency Injection (Recommended)
Replace the global singleton with explicit dependency injection:

```python
class KPATApplication:
    """Main application class that manages dependencies."""
    
    def __init__(self, *, verbose: bool = False, quiet: bool = False):
        self.rich_output = RichOutput(verbose=verbose, quiet=quiet)
    
    def process_scripts(self, ...):
        engine = ParallelEngine(rich_output=self.rich_output)
        # ...
```

**Benefits:**
- Explicit dependencies, easier to test
- No global state
- Clear ownership and lifecycle
- Type-safe

**Drawbacks:**
- Requires refactoring throughout codebase
- More verbose initialization

### Option 2: Context Manager Pattern
Use a context manager to establish the RichOutput scope:

```python
@contextmanager
def rich_output_context(*, verbose: bool = False, quiet: bool = False):
    """Context manager for RichOutput with automatic cleanup."""
    output = RichOutput(verbose=verbose, quiet=quiet)
    token = _rich_output_var.set(output)  # Using contextvars
    try:
        yield output
    finally:
        _rich_output_var.reset(token)

def get_rich_output() -> RichOutput:
    """Get the current context's RichOutput instance."""
    return _rich_output_var.get()
```

**Benefits:**
- Automatic scope management
- Thread-safe by design (contextvars)
- Backwards compatible API

**Drawbacks:**
- Still somewhat implicit
- Requires Python 3.7+ contextvars

### Option 3: Factory Pattern with Registry
Create a factory that manages multiple named instances:

```python
class RichOutputFactory:
    """Factory for managing RichOutput instances."""
    
    def __init__(self):
        self._instances: dict[str, RichOutput] = {}
        self._lock = threading.Lock()
    
    def get_instance(self, name: str = "default", **kwargs) -> RichOutput:
        """Get or create a named RichOutput instance."""
        with self._lock:
            if name not in self._instances:
                self._instances[name] = RichOutput(**kwargs)
            return self._instances[name]
    
    def configure_instance(self, name: str = "default", **kwargs) -> None:
        """Configure an existing instance."""
        if name in self._instances:
            self._instances[name].update_settings(**kwargs)

# Global factory (only one global instead of instance + locks)
_factory = RichOutputFactory()

def get_rich_output(name: str = "default", **kwargs) -> RichOutput:
    """Get a named RichOutput instance."""
    return _factory.get_instance(name, **kwargs)
```

**Benefits:**
- Multiple instances for different contexts
- Cleaner global state management
- Backwards compatible

**Drawbacks:**
- Still global state
- String-based naming can be error-prone

### Option 4: Enhanced Current Pattern
Improve the current singleton pattern while maintaining compatibility:

```python
import threading
from typing import Any, ClassVar
import contextvars

class RichOutputManager:
    """Thread-safe manager for RichOutput instances."""
    
    _default_instance: ClassVar[RichOutput | None] = None
    _creation_lock: ClassVar[threading.Lock] = threading.Lock()
    _context_var: ClassVar[contextvars.ContextVar[RichOutput]] = contextvars.ContextVar('rich_output')
    
    @classmethod
    def get_instance(cls, *, verbose: bool | None = None, quiet: bool | None = None) -> RichOutput:
        """Get RichOutput instance, preferring context-local then global."""
        # Try context-local first
        try:
            instance = cls._context_var.get()
            if verbose is not None or quiet is not None:
                instance.update_settings(verbose=verbose, quiet=quiet)
            return instance
        except LookupError:
            pass
        
        # Fall back to global singleton with double-checked locking
        if cls._default_instance is not None:
            if verbose is not None or quiet is not None:
                cls._default_instance.update_settings(verbose=verbose, quiet=quiet)
            return cls._default_instance
        
        with cls._creation_lock:
            if cls._default_instance is None:
                cls._default_instance = RichOutput(
                    verbose=verbose if verbose is not None else False,
                    quiet=quiet if quiet is not None else False,
                )
            elif verbose is not None or quiet is not None:
                cls._default_instance.update_settings(verbose=verbose, quiet=quiet)
        
        return cls._default_instance
    
    @classmethod
    def set_context_instance(cls, instance: RichOutput) -> contextvars.Token[RichOutput]:
        """Set a context-local RichOutput instance."""
        return cls._context_var.set(instance)
    
    @classmethod
    def reset_context(cls, token: contextvars.Token[RichOutput]) -> None:
        """Reset context to previous value."""
        cls._context_var.reset(token)

# Backwards compatible API
def get_rich_output(*, verbose: bool | None = None, quiet: bool | None = None) -> RichOutput:
    """Get or create the RichOutput instance."""
    return RichOutputManager.get_instance(verbose=verbose, quiet=quiet)
```

**Benefits:**
- Backwards compatible
- Better organization of singleton logic
- Context-local override capability
- Easier testing

**Drawbacks:**
- Still global state as fallback
- More complex implementation

## Recommendations

### Short Term (Minimal Changes)
Implement **Option 4** (Enhanced Current Pattern):
- Consolidate singleton logic into a manager class
- Add context-local override capability for testing
- Maintain full backwards compatibility
- Improve code organization

### Medium Term (Moderate Refactoring)
Move toward **Option 1** (Dependency Injection) for new code:
- Create an `Application` or `ToolkitContext` class that manages dependencies
- Gradually refactor modules to accept RichOutput as a parameter
- Keep backwards compatibility during transition

### Long Term (Full Refactoring)
Complete migration to **Option 1**:
- Remove global singleton entirely
- Use dependency injection throughout
- Cleaner, more testable architecture

## Implementation Plan

### Phase 1: Enhanced Singleton (Low Risk)
1. Create `RichOutputManager` class
2. Add context-local capability
3. Update tests to use context override
4. Maintain all existing APIs

### Phase 2: Gradual Migration (Medium Risk)
1. Create `KPATApplication` class with managed dependencies
2. Refactor CLI entry points to use application class
3. Update parallel engine to accept RichOutput parameter
4. Keep convenience functions for backwards compatibility

### Phase 3: Complete Migration (High Risk)
1. Remove global singleton entirely
2. Update all modules to use dependency injection
3. Remove convenience functions
4. Update documentation and examples

## Testing Considerations

For any option chosen, ensure:
- Easy mocking/stubbing in tests
- Isolated test environments
- Clear lifecycle management
- Thread-safe testing patterns

The enhanced singleton (Option 4) provides the best short-term improvement with minimal risk, while dependency injection (Option 1) offers the best long-term architecture.
