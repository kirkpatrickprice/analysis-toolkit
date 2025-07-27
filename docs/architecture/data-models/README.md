# Data Models Architecture

This directory contains comprehensive documentation for the data modeling architecture of the KP Analysis Toolkit.

## Documentation Overview

### Core Documentation

- **[Data Models Architecture](data-models-architecture.md)** - Complete guide to the Pydantic-based data modeling system, including base model patterns, validation strategies, and integration with core services

### Command-Specific Data Models

- **[Process Scripts Data Models](process-scripts-data-models.md)** - Data models for script processing operations including search configurations, system detection, YAML processing, and results handling
- **[RTF to Text Data Models](rtf-to-text-data-models.md)** - Models for RTF document conversion including file processing configuration, conversion results, and validation patterns
- **[Nipper Expander Data Models](nipper-expander-data-models.md)** - Models for network security audit processing including CSV handling, device expansion, and Excel export operations

### Configuration Documentation

- **[YAML Search Configuration](yaml-search-configuration.md)** - Specialized configuration format for search operations

## Architecture Highlights

### Base Model Foundation

All data models inherit from `KPATBaseModel`, providing:

- Consistent Pydantic configuration with support for `Path` objects
- Standardized validation patterns and error handling  
- Common serialization and deserialization behavior

### Model Categories

- **Configuration Models**: Application settings and user preferences
- **System Models**: Target system representation with OS detection
- **Processing Models**: Data transformation and workflow states
- **Data Transfer Models**: Inter-service communication structures

### Validation Architecture

- **Field Validation**: Individual field validation using Pydantic validators
- **Cross-Field Validation**: Complex validation logic spanning multiple fields
- **Path Validation Mixins**: Reusable file system validation patterns

## Integration Points

### Core Services Integration

Models integrate seamlessly with:

- Dependency injection container for service configuration
- Rich output service for validation error formatting
- File processing service for path validation
- CSV processing service for DataFrame validation

### Module Extensions

Modules extend base models for specialized requirements through:

- Service-specific configuration extensions
- Composition patterns for complex model structures
- Generic type support for reusable model containers

## Key Benefits

- **Type Safety**: Comprehensive type hints and runtime validation
- **Consistency**: Uniform patterns across all application modules
- **Extensibility**: Clear extension points for specialized requirements
- **Quality**: Robust error handling and validation reporting

## Navigation

### General Architecture

For implementation details and code examples of base patterns, see the [complete data models architecture documentation](data-models-architecture.md).

### Command-Specific Implementation

For detailed implementation guides for each command:

- **Process Scripts**: See [Process Scripts Data Models](process-scripts-data-models.md) for search configurations, system models, and YAML processing
- **RTF to Text**: See [RTF to Text Data Models](rtf-to-text-data-models.md) for file conversion models and result handling
- **Nipper Expander**: See [Nipper Expander Data Models](nipper-expander-data-models.md) for CSV processing and device expansion models
