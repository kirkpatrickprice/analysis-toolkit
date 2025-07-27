# Architecture Documentation

High-level system design and architectural decisions.

## Contents

This directory contains:

- **System Overview** - High-level architecture overview
- **Component Design** - Individual component architecture
- **Data Flow** - How data moves through the system
- **Integration Patterns** - How components interact
- **Design Decisions** - Architectural choices and rationale

## Architecture Topics

### System Architecture
- Overall system structure
- Module organization
- Dependency relationships
- Interface definitions

### Data Architecture
- Data models and schemas
- File format handling
- Configuration management
- Result processing

### CLI Architecture
- Command structure
- User interface patterns
- Error handling strategies
- Progress reporting
- Rich-Click integration patterns
- Custom help system design
- Option grouping architecture
- Decorator pattern implementation

### Concurrency Architecture
- Parallel processing system design
- Multi-stage interrupt handling
- Process and thread pool management
- Memory-efficient task batching
- Cross-platform signal handling
- Progress tracking integration
- Rich console output coordination

### Service Layer Architecture
- Business logic organization
- Service interfaces
- Processing workflows
- Extension points

## Planned Architecture Docs

- [ ] System architecture overview
- [x] CLI command architecture (see `cli/` subdirectory)
- [x] Concurrency architecture (see `concurrency/` subdirectory)
- [ ] Service layer design
- [ ] Data model architecture
- [ ] Error handling architecture
- [ ] Configuration system design
- [ ] Batch processing architecture
- [ ] Future extensibility considerations

## CLI Architecture Documentation

The CLI architecture is comprehensively documented in the `cli/` subdirectory:

- **[CLI Architecture Patterns](cli/cli-architecture-patterns.md)** - Main CLI architecture with Rich-Click integration, multi-command structure, and dependency injection patterns
- **[CLI Decorator Patterns](cli/cli-decorator-patterns.md)** - Shared option decorators for consistent CLI patterns across commands
- **[CLI Help System](cli/cli-help-system.md)** - Custom help system architecture addressing Rich-Click limitations with grouped option displays
- **[CLI Option Groups](cli/cli-option-groups.md)** - Option grouping strategies for organizing help displays by functional purpose

## Concurrency Architecture Documentation

The concurrency and parallel processing architecture is documented in the `concurrency/` subdirectory:

- **[Parallel Processing Architecture](concurrency/parallel-processing-architecture.md)** - Main parallel processing system with ProcessPoolExecutor/ThreadPoolExecutor patterns, dependency injection integration, and Rich console output coordination
- **[Interrupt Handling Architecture](concurrency/interrupt-handling.md)** - Multi-stage interrupt handling system for graceful cancellation with three escalating levels: graceful → urgent → immediate termination
