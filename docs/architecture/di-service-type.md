# Dependency Injection: Factory vs Singleton Providers

## Overview

The dependency injection system uses two main provider types from the `dependency-injector` library:

- **Factory Provider**: Creates a new instance every time the dependency is resolved
- **Singleton Provider**: Creates a single instance that is reused across all dependency resolutions

## Current Container Configuration

### Core Container (`CoreContainer`)
- **RichOutputService**: `Singleton` provider
- **RichOutputConfig**: `Factory` provider (used by RichOutputService)

### File Processing Container (`FileProcessingContainer`)
- **EncodingDetector**: `Factory` provider
- **HashGenerator**: `Factory` provider  
- **FileValidator**: `Factory` provider
- **FileProcessingService**: `Factory` provider

## Decision Criteria: When to Use Each Provider Type

### Use Singleton Provider When:

1. **Stateful Services with Global Configuration**
   - Services that maintain configuration state that should be consistent across the application
   - Example: `RichOutputService` maintains console configuration (width, verbosity, styling) that should be consistent

2. **Resource-Heavy Services**
   - Services that are expensive to create (database connections, file handles, etc.)
   - Services that should share resources across the application

3. **Services with Side Effects**
   - Services that perform I/O operations where consistency matters
   - Logging services, output services, monitoring services

4. **Configuration Objects with Global Scope**
   - Application-wide settings that should be consistent
   - Note: While `RichOutputConfig` uses Factory, it's immediately consumed by the Singleton `RichOutputService`

### Use Factory Provider When:

1. **Stateless or Operation-Scoped Services**
   - Services that don't maintain state between operations
   - Services where each operation should have a fresh instance

2. **Data Processing Services**
   - Services that transform data without side effects
   - Example: `EncodingDetector`, `HashGenerator` - each file operation can use a fresh instance

3. **Validation Services**
   - Services that validate input without maintaining state
   - Example: `FileValidator` - each validation can use a fresh instance

4. **Services with Request/Operation Scope**
   - Services where isolation between operations is important
   - Services that might accumulate state that should be reset between uses

## Why RichOutputService is Singleton

```python
# Core Container Configuration
rich_output: providers.Singleton[RichOutputService] = providers.Singleton(
    RichOutputService,
    config=providers.Factory(RichOutputConfig, ...),
)
```

**Rationale:**
- **Consistent Output Formatting**: All parts of the application should use the same console width, verbosity settings, and styling
- **Shared Console State**: Rich Console objects maintain internal state for formatting that should be consistent
- **Performance**: Avoids recreating console objects and reconfiguring styling for every output operation
- **User Experience**: Ensures consistent behavior across all CLI commands and output operations

## Why File Processing Services are Factory

```python
# File Processing Container Configuration
encoding_detector: providers.Factory = providers.Factory(...)
hash_generator: providers.Factory = providers.Factory(...)
file_validator: providers.Factory = providers.Factory(...)
file_processing_service: providers.Factory = providers.Factory(...)
```

**Rationale:**
- **Stateless Operations**: Each file processing operation is independent and doesn't require shared state
- **Isolation**: Different file operations should not interfere with each other
- **Testing**: Easier to test when each operation gets fresh instances
- **Memory Management**: Instances can be garbage collected after each operation
- **Parallel Processing**: Fresh instances avoid potential threading issues when processing multiple files

### Testing Implications

### Singleton Services Testing
```python
def test_singleton_behavior(container_initialized):
    """Test that singleton services return the same instance."""
    service1 = container.core().rich_output()
    service2 = container.core().rich_output()
    assert service1 is service2  # Same instance
```

### Factory Services Testing
```python
def test_factory_behavior(container_initialized):
    """Test that factory services return new instances."""
    service1 = container.file_processing().encoding_detector()
    service2 = container.file_processing().encoding_detector()
    assert service1 is not service2  # Different instances
    assert type(service1) == type(service2)  # Same type
```

## Best Practices

1. **Default to Factory**: Unless you have a specific reason for shared state, use Factory providers
2. **Consider Lifecycle**: Think about whether the service needs to persist state across operations
3. **Test Both Behaviors**: Always test that your provider type matches your expectations
4. **Document Decisions**: Always document why a service is Singleton vs Factory in code comments
5. **Review Regularly**: Provider types should be reviewed when service responsibilities change

## Migration Considerations

When changing provider types:

1. **Factory to Singleton**: Ensure the service is thread-safe and state management is correct
2. **Singleton to Factory**: Ensure dependent code doesn't rely on shared state
3. **Test Thoroughly**: Provider type changes can have subtle effects on application behavior
4. **Update Documentation**: Always update container documentation when changing provider types
