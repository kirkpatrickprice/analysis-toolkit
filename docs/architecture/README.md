# Architecture Documentation

Comprehensive system design and architectural documentation for the KP Analysis Toolkit.

## Quick Navigation

### 🏗️ **[Dependency Injection](dependency-injection/README.md)**
Service-based architecture with type-safe dependency injection, promoting modularity and testability.

### 🖥️ **[CLI Architecture](cli/README.md)**  
Rich-Click based command line interface with custom help systems, option grouping, and decorator patterns.

### ⚡ **[Concurrency](concurrency/README.md)**
Multi-core parallel processing with graceful interrupt handling and Rich console integration.

### 📊 **[Data Architecture](data-models/README.md)**
Pydantic-based data models with comprehensive validation and command-specific schemas.

### ⚡ **[Performance Architecture](performance/README.md)**
Content streaming patterns and performance optimization strategies for efficient file processing.

## System Overview

The KP Analysis Toolkit follows a modular, service-oriented architecture built on these core principles:

- **Type Safety**: Comprehensive type hints and Pydantic validation throughout
- **Dependency Injection**: Clean separation of concerns through injectable services  
- **Parallel Processing**: Efficient multi-core utilization for large dataset processing
- **Rich User Experience**: Modern CLI with progress indicators and formatted output
- **Testability**: Interface-based design enabling comprehensive testing strategies

## Architecture Overview

The system is organized into several key architectural layers:

### Core Services Layer
Foundation services used across all commands:
- File processing and validation
- Configuration management  
- Error handling and logging
- Progress tracking and reporting

### Application Services Layer  
Command-agnostic business logic:
- Search and filtering operations
- Data transformation pipelines
- Output formatting and export
- Parallel processing orchestration

### Command Services Layer
Command-specific implementations:
- Process Scripts: PowerShell/Bash script analysis
- RTF to Text: Rich Text Format conversion  
- Nipper Expander: Network configuration processing

## Data Flow Architecture

### Service Layer Architecture
- Business logic organization
- Service interfaces
- Processing workflows
- Extension points

## Planned Architecture Docs

- [ ] System architecture overview
- [x] CLI command architecture (see `cli/` subdirectory)
- [x] Concurrency architecture (see `concurrency/` subdirectory)
- [x] Data models architecture (see `data-models/` subdirectory)
- [x] Data flows architecture (see `data-flows/` subdirectory)
- [ ] Service layer design
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

## Data Architecture Documentation

The data modeling and processing architecture is comprehensively documented with an overview and specialized subdirectories:

- **[Data Architecture Overview](data-architecture.md)** - High-level overview of data modeling and processing architecture integration

### Data Models Architecture

The `data-models/` subdirectory contains comprehensive documentation for the Pydantic-based data modeling system:

- **[Data Models Architecture](data-models/data-models-architecture.md)** - Complete guide to the data modeling system including KPATBaseModel inheritance patterns, validation strategies, field validators, cross-field validation, and integration with core services

### Data Flows Architecture

The `data-flows/` subdirectory contains comprehensive documentation for data processing workflows:

- **[Data Flows Architecture](data-flows/data-flows-architecture.md)** - Complete guide to pipeline-based data processing including file processing flows, CSV processing pipelines, Excel export coordination, batch processing patterns, and service orchestration through dependency injection
