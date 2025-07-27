# Dependency Injection Architecture

The KP Analysis Toolkit uses a comprehensive dependency injection system to promote modularity, testability, and maintainability across all components.

## Overview

Our dependency injection architecture follows these key principles:

- **Service-based design**: Core functionality is organized into injectable services
- **Type safety**: Full type hint support with proper interface definitions  
- **Testability**: Easy mocking and testing through interface abstractions
- **Separation of concerns**: Clear boundaries between UI, business logic, and data layers

## Architecture Components

### [Service Package Pattern](service-package-pattern.md)
Learn about our service package organization and how services are structured and registered.

### [DI Service Types](di-service-type.md) 
Understand the different types of services in our system and their roles.

### [UI Service Layer Separation](ui-service-layer-separation.md)
Explore how we separate user interface concerns from business logic through dependency injection.

## Service Relationships

The dependency injection system organizes services into three main layers:

- **Core Services**: Fundamental services used across all commands (`core` package)
- **Application Services**: Command-agnostic application logic (`application` package)  
- **Command Services**: Command-specific business logic (`<per_command>` packages)

## Performance Considerations

The system uses lazy imports to improve load time performance, ensuring that command-specific services are only loaded when needed.

## Quick Start

For developers new to our DI system:

1. Start with the [Service Package Pattern](service-package-pattern.md) to understand basic organization
2. Review [DI Service Types](di-service-type.md) to understand available abstractions
3. Explore [UI Service Layer Separation](ui-service-layer-separation.md) for practical implementation patterns

## Implementation Details

The dependency injection system is built on Python's type system and uses protocols for interface definitions. Services are organized into packages with clear separation between interfaces and implementations.