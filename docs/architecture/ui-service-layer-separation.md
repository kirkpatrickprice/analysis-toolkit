# UI-Service Layer Separation Concerns

## Overview

This document outlines architectural considerations for separating user interface concerns from business logic in the KP Analysis Toolkit, with particular focus on preparing for future GUI development while maintaining current CLI functionality.

## Current Architecture Issues

### The Problem

The service layers currently have direct dependencies on `RichOutputService` for user feedback:
- Status updates ("Processing file X...")
- Non-fatal warnings ("Skipping invalid entry...")
- Progress notifications
- Success/failure messages

This creates **tight coupling** between:
- **Business Logic** (what to process)
- **Presentation Logic** (how to show it)

### Current Code Example

```python
def process_rtf_file(config: ProgramConfig) -> None:
    rich_output = get_rich_output()
    rich_output.info(f"Processing {config.input_file}")
    
    # Business logic mixed with UI concerns
    if some_warning_condition:
        rich_output.warning("Non-standard format detected")
    
    # More processing...
    rich_output.success(f"Converted to {config.output_file}")
```

### Future Impact

When developing a GUI, this tight coupling will create:
- Rich console output doesn't translate to GUI widgets
- Different progress mechanisms (progress bars vs. status labels)
- Different error display patterns (console vs. dialog boxes)
- Threading considerations (GUI updates must be on main thread)

## Architectural Solutions

### Option 1: UI Abstraction Layer

Create an abstract interface that both CLI and GUI can implement.

```python
from abc import ABC, abstractmethod
from typing import Protocol

class UserInterface(Protocol):
    def show_info(self, message: str) -> None: ...
    def show_warning(self, message: str) -> None: ...
    def show_error(self, message: str) -> None: ...
    def show_progress(self, current: int, total: int, description: str) -> None: ...
    def show_success(self, message: str) -> None: ...

# Service layer becomes UI-agnostic
def process_rtf_file(config: ProgramConfig, ui: UserInterface) -> None:
    ui.show_info(f"Processing {config.input_file}")
    # ... business logic ...
    ui.show_success(f"Converted to {config.output_file}")
```

**Pros:**
- Service layer becomes UI-agnostic
- Easy to add new UI types
- Familiar dependency injection pattern

**Cons:**
- Still couples service to UI concerns
- Every service function needs UI parameter
- Complex for optional feedback scenarios

### Option 2: Event/Observer Pattern

Service layer emits events; UI layers subscribe to them.

```python
from typing import Callable, Any
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"
    SUCCESS = "success"

@dataclass
class ServiceEvent:
    type: EventType
    message: str
    data: dict[str, Any] = None

class EventEmitter:
    def __init__(self):
        self._handlers: list[Callable[[ServiceEvent], None]] = []
    
    def subscribe(self, handler: Callable[[ServiceEvent], None]) -> None:
        self._handlers.append(handler)
    
    def emit(self, event: ServiceEvent) -> None:
        for handler in self._handlers:
            handler(event)

# Service layer emits events
def process_rtf_file(config: ProgramConfig, emitter: EventEmitter) -> None:
    emitter.emit(ServiceEvent(EventType.INFO, f"Processing {config.input_file}"))
    # ... business logic ...
    emitter.emit(ServiceEvent(EventType.SUCCESS, f"Converted to {config.output_file}"))
```

**Pros:**
- True decoupling of service and UI
- Multiple UI consumers can listen
- Easy to add logging, metrics, etc.
- Flexible event data structure

**Cons:**
- More complex setup
- Harder to debug event flows
- Requires event emitter injection

### Option 3: Return-Based Reporting

Service layer returns structured results; callers handle presentation.

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ProcessingResult:
    success: bool
    input_file: Path
    output_file: Path | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    progress_steps: list[str] = field(default_factory=list)

def process_rtf_file(config: ProgramConfig) -> ProcessingResult:
    result = ProcessingResult(success=False, input_file=config.input_file)
    
    try:
        # ... business logic ...
        result.success = True
        result.output_file = config.output_file
        result.progress_steps.append("File parsed successfully")
        
        if some_minor_issue:
            result.warnings.append("Non-standard RTF format detected")
            
    except Exception as e:
        result.errors.append(str(e))
    
    return result
```

**Pros:**
- Complete separation of concerns
- Service layer is pure business logic
- Easy to test service logic
- Result objects are serializable (great for APIs)

**Cons:**
- No real-time progress updates
- CLI/GUI must handle all presentation logic
- More complex for streaming operations

### Option 4: Hybrid Approach with Optional Callbacks

Service layer accepts optional callback functions for UI integration.

```python
from typing import Callable, Optional, Protocol

class ProgressCallback(Protocol):
    def __call__(self, step: str, progress: float = None) -> None: ...

def process_rtf_file(
    config: ProgramConfig,
    progress_callback: Optional[ProgressCallback] = None,
    warning_callback: Optional[Callable[[str], None]] = None
) -> ProcessingResult:
    
    if progress_callback:
        progress_callback("Starting RTF processing", 0.0)
    
    # ... business logic ...
    
    if some_warning and warning_callback:
        warning_callback("Non-standard format detected")
    
    if progress_callback:
        progress_callback("Conversion complete", 1.0)
    
    return ProcessingResult(...)
```

**Pros:**
- Service remains usable without UI
- Real-time feedback when needed
- Gradual migration path
- Maintains current functionality

**Cons:**
- Multiple callback parameters can be messy
- Still some coupling to UI concepts

### Option 5: Logging + Result Pattern

Use structured logging for informational messages, return results for decisions.

```python
import logging
from typing import NamedTuple

logger = logging.getLogger(__name__)

class ProcessingMetrics(NamedTuple):
    files_processed: int
    warnings: list[str]
    processing_time: float

def process_rtf_file(config: ProgramConfig) -> ProcessingResult:
    logger.info("Starting RTF processing", extra={"file": config.input_file})
    
    result = ProcessingResult(success=False, input_file=config.input_file)
    
    try:
        # ... business logic ...
        logger.info("RTF parsing complete")
        
        if some_minor_issue:
            warning_msg = "Non-standard RTF format detected"
            logger.warning(warning_msg, extra={"file": config.input_file})
            result.warnings.append(warning_msg)
        
        result.success = True
        result.output_file = config.output_file
        logger.info("RTF conversion successful", extra={"output": config.output_file})
        
    except Exception as e:
        logger.error("RTF processing failed", exc_info=True)
        result.errors.append(str(e))
    
    return result
```

**Pros:**
- Clean separation of concerns
- Rich logging ecosystem (handlers, formatters, levels)
- Easy to redirect to different outputs
- Industry standard approach

**Cons:**
- Less direct control over UI updates
- Requires logging infrastructure setup
- Progress updates via logging feel awkward

## Recommended Approach: Hybrid Strategy

### Phase 1: Immediate (Backward Compatible)

1. **Keep current Rich integration** for CLI scenarios
2. **Add optional callback parameters** to service functions
3. **Return structured result objects** with comprehensive data

```python
from typing import Optional
from kp_analysis_toolkit.models.ui import UICallbacks
from kp_analysis_toolkit.utils.rich_output import RichUICallbacks

def process_rtf_file(
    config: ProgramConfig,
    ui_callbacks: Optional[UICallbacks] = None
) -> ProcessingResult:
    # Use Rich if no callbacks provided (backward compatibility)
    if ui_callbacks is None:
        ui_callbacks = RichUICallbacks()
    
    ui_callbacks.show_info(f"Processing {config.input_file}")
    
    # ... processing logic ...
    
    result = ProcessingResult(success=True, input_file=config.input_file)
    ui_callbacks.show_success(f"Converted to {config.output_file}")
    
    return result
```

### Phase 2: Future (GUI Development)

1. **Implement GUI callback handlers** that update GUI widgets
2. **Gradually migrate CLI** to use the callback system
3. **Remove direct Rich dependencies** from service layer

### Phase 3: Long-term (Clean Architecture)

1. **Pure service layer** returns only business results
2. **UI adapters** handle all presentation logic
3. **Event system** for complex inter-component communication

## Implementation Guidelines

### Immediate Steps

1. Create a `UICallbacks` protocol in `src/kp_analysis_toolkit/models/ui.py`
2. Add optional callback parameters to key service functions
3. Implement `RichUICallbacks` wrapper for current functionality
4. Test with existing CLI commands

### Design Principles

- **Backward Compatibility**: Existing code continues to work
- **Gradual Migration**: No big bang refactoring required
- **Testability**: Service logic can be tested without UI dependencies
- **Flexibility**: Support CLI, GUI, API, and testing scenarios
- **Future-Proof**: Foundation for any UI technology

### Benefits

- **Zero breaking changes** to existing code
- **Gradual migration path** - implement when convenient
- **Clean testing** - services can be tested in isolation
- **UI flexibility** - support multiple interface types
- **Maintainability** - clear separation of concerns

## Current Batch Processing Integration

The existing batch processing utility already demonstrates some of these patterns:

```python
class BatchProcessingConfig(KPATBaseModel):
    success_message_formatter: Callable[[Path, Any], str] | None = None
    rich_output: RichOutputService | None = None
```

This shows how UI concerns can be made optional and configurable, providing a foundation for the recommended hybrid approach.

## Future Considerations

### GUI Development

When implementing a GUI:
- Create GUI-specific callback implementations
- Handle threading concerns (GUI updates on main thread)
- Implement appropriate progress widgets
- Design error dialog patterns

### API Development

When creating APIs:
- Use return-based results exclusively
- Implement structured logging for operational visibility
- Provide webhook/callback mechanisms for async operations
- Return JSON-serializable result objects

### Testing

The separation enables:
- Pure unit testing of business logic
- UI testing separate from business logic
- Mock callbacks for integration testing
- Performance testing without UI overhead

## Conclusion

The hybrid approach provides the best balance of maintaining current functionality while preparing for future UI developments. It acknowledges that working code exists today while establishing patterns for clean architecture evolution.

The key insight is that UI concerns and business logic serve different purposes and should be designed as separate, composable layers that can work together when needed but remain independent when appropriate.
