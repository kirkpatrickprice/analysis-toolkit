# Data Architecture Overview

This directory contains comprehensive documentation for the data handling architecture of the KP Analysis Toolkit, covering both data modeling patterns and data processing workflows.

## Architecture Components

### Data Models (`data-models/`)

The data models architecture defines the foundational data structures and validation patterns used throughout the application:

- **Base Model System**: `KPATBaseModel` inheritance providing consistent Pydantic configuration
- **Validation Architecture**: Field validators, cross-field validation, and path validation mixins
- **Model Categories**: Configuration, system, processing, and data transfer models
- **Type Safety**: Comprehensive type hints and runtime validation

**Key Documentation**: [Data Models Architecture](data-models/data-models-architecture.md)

### Data Flows (`data-flows/`)

The data flows architecture defines how data moves through the system via pipeline-based processing:

- **Core Flow Patterns**: File processing, CSV processing, Excel export, and batch processing pipelines
- **Service Orchestration**: Multi-service coordination through dependency injection
- **Module-Specific Flows**: Process scripts, Nipper expander, and RTF conversion workflows
- **Performance Optimization**: Stream processing, lazy evaluation, and parallel coordination

**Key Documentation**: [Data Flows Architecture](data-flows/data-flows-architecture.md)

## Integration Highlights

### Pydantic Foundation

Both data models and data flows leverage Pydantic for:

- Type safety with comprehensive validation
- Structured error reporting and user-friendly messaging
- Configuration management with runtime validation
- Service integration through validated parameters

### Dependency Injection Integration

The data architecture integrates seamlessly with the DI container:

- Service configuration through model validation
- Protocol-based service interfaces for data processing
- Runtime composition of processing pipelines
- Module-specific extensions of core capabilities

### Core Services Coordination

Data architecture coordinates multiple core services:

- **File Processing Service**: Validation, encoding detection, hash generation
- **CSV Processing Service**: DataFrame operations with schema validation
- **Excel Export Service**: Multi-sheet workbook generation and formatting
- **Rich Output Service**: Progress reporting and error display

## Architectural Benefits

### Type Safety and Validation

- Runtime type checking with Pydantic models
- Field-level and cross-field validation rules
- Structured error reporting with rich context
- Path validation for file system operations

### Scalability and Performance

- Stream processing for large datasets
- Lazy evaluation for expensive operations
- Parallel processing coordination
- Memory-efficient batch operations

### Maintainability and Testing

- Clear separation of data concerns
- Protocol-based interfaces for easy mocking
- Comprehensive validation test coverage
- Service-level testing with clear boundaries

### Extensibility

- Plugin architecture support through model registration
- Module-specific model extensions
- Dynamic workflow composition
- External service integration capabilities

## Navigation

- **[Data Models](data-models/)** - Comprehensive data modeling documentation
- **[Data Flows](data-flows/)** - Pipeline-based processing workflow documentation

For the complete picture of how data models and flows work together, review both subdirectories as they complement each other to form the complete data architecture.
