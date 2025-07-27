# Dependency Injection Architecture

The KP Analysis Toolkit uses a comprehensive dependency injection system to promote modularity, testability, and maintainability across all components.

## Overview

Our dependency injection architecture follows these key principles:

- **Service-based design**: Core functionality is organized into injectable services
- **Type safety**: Full type hint support with proper interface definitions  
- **Testability**: Easy mocking and testing through interface abstractions
- **Separation of concerns**: Clear boundaries between UI, business logic, and data layers

All DI functions are provided with the [`dependency-injector`](https://pypi.org/project/dependency-injector/) framework.

## Architecture Components

### [Core Service Pattern](di-core-service-pattern.md)
Learn about our service package organization and how services are structured and registered.

### [Command Service Pattern](di-command-pattern.md)
Describes how to implement a service for a new toolkit subcommand.

### [DI Service Types](di-service-type.md) 
Understand the different types of services in our system and their roles.

## Service Relationships

The dependency injection system organizes services into three main layers:

- **Application Services**: Assembly of all services within the application including `core` and `<per-command>` services
- **Core Services**: Fundamental services used across all commands (`core` package)
- **Command Services**: Command-specific business logic (`<per_command>` packages)

## Performance Considerations

The system uses lazy imports to improve load time performance, ensuring that command-specific services are only loaded when needed.

## Quick Start

For developers new to our DI system:

1. Start with the [Core Service Pattern](di-core-service-pattern.md) to understand the basic services that are available throughout the toolkit
2. Take a look at the implementations in `service.py` files in each sub scommand to see how they consume services from `core` while also providing their own services
3. Examine the integration through the `core.containers.application` module to see how all services are unified under one application context
4. If implementing a new service, review [DI Service Types](di-service-type.md) to understand use cases for singletons, factories, and other implementation types

## Implementation Details

The dependency injection system is built on Python's type system and uses protocols for interface definitions. Services are organized into packages with clear separation between interfaces and implementations.