# SSF Tools - {Service/Component Name} Architecture

## Overview

{Provide a concise introduction to the service/component, its primary purpose, and its role within the SSF Tools ecosystem. Include any important notes about implementation status (MVP, planned features, etc.).}

{Brief description of what the architecture enables and key benefits it provides to the system.}

## Architectural Principles

### Design Goals
- **{Goal 1}**: {Description of the primary design goal}
- **{Goal 2}**: {Description of another key design goal}
- **{Goal 3}**: {Description of additional design goal}
- **{Goal 4}**: {Description of another design goal}
- **{Goal 5}**: {Description of final key goal}

### Key Benefits
- **{Benefit 1}**: {Description of primary benefit}
- **{Benefit 2}**: {Description of another benefit}
- **{Benefit 3}**: {Description of additional benefit}
- **{Benefit 4}**: {Description of another benefit}
- **{Benefit 5}**: {Description of final benefit}

## Architecture Overview

{Include a comprehensive Mermaid diagram showing the main components, their relationships, and data flow. Use consistent styling and grouping to show logical boundaries.}

```mermaid
graph TD
    %% Core Components
    {COMPONENT}[{Component Name}<br/>{Brief Description}]
    
    %% Sub-components or Categories
    subgraph {GROUP} ["{📁 Group Name}"]
        {SUB1}[{Sub-component 1}<br/>{Description}]
        {SUB2}[{Sub-component 2}<br/>{Description}]
    end
    
    %% Service Dependencies
    {COMPONENT} --> {GROUP}
    
    %% Integration Points
    subgraph {INTEGRATION} ["{🔌 Integration Points}"]
        {INT1}[{Integration 1}<br/>{Description}]
        {INT2}[{Integration 2}<br/>{Description}]
    end
    
    {INTEGRATION} --> {COMPONENT}
    
    %% CLI/External Interface
    {CLI}["{Interface Name}<br/>{Interface description}"]
    {CLI} --> {COMPONENT}
    
    %% Storage/Persistence (if applicable)
    subgraph {STORAGE} ["{💾 Storage/Persistence}"]
        {STORE1}[{Storage Type 1}<br/>{Description}]
        {STORE2}[{Storage Type 2}<br/>{Description}]
    end
    
    {COMPONENT} --> {STORAGE}
    
    %% Styling
    classDef coreService fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef protocol fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef component fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef integration fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef cli fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef storage fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef group fill:#f8f9fa,stroke:#6c757d,stroke-width:3px,stroke-dasharray: 5 5
    
    class {COMPONENT} coreService
    class {SUB1},{SUB2} component
    class {INT1},{INT2} integration
    class {CLI} cli
    class {STORE1},{STORE2} storage
    class {GROUP},{INTEGRATION},{STORAGE} group
```

## {Service/Component} Protocols

{Describe the protocol-based architecture if applicable. Include the main interfaces that define the contracts.}

### {Primary Protocol Name}

{Description of the main protocol and its purpose}

```python
from typing import Protocol, Any, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum

class {ProtocolName}(Protocol):
    """Protocol for {description of what this protocol defines}."""
    
    def {method_name}(self, {parameters}) -> {return_type}:
        """Brief description of what this method does."""
        
    def {another_method}(self, {parameters}) -> {return_type}:
        """Brief description of what this method does."""
```

### {Secondary Protocol Name} (if applicable)

{Description of secondary protocol}

```python
class {SecondaryProtocolName}(Protocol):
    """Protocol for {description}."""
    
    def {method_name}(self, {parameters}) -> {return_type}:
        """Brief description."""
```

## Configuration Models

{If the service uses configuration, describe the configuration structure and models}

### {Configuration Name}

```python
class {ConfigName}(BaseModel):
    """Configuration for {service/component}."""
    {field_name}: {type} = {default_value}  # Description
    {another_field}: {type} = {default_value}  # Description
    
    @field_validator('{field_name}')
    @classmethod
    def {validator_name}(cls, v: {type}) -> {type}:
        """Validation logic description."""
        return {validation_logic}
```

### Global Configuration Integration

{Show how the service integrates with the global configuration system}

```yaml
# In ssf-tools-config.yaml
global:
  {global_setting}: {value}                    # Description
  {another_setting}: {value}                   # Description
  
{service_name}:
  {service_setting}: {value}                   # Description
  {nested_config}:
    {nested_setting}: {value}                  # Description
```

## Service Implementation

### {Main Service Class}

{Description of the primary service implementation}

```python
class {ServiceName}:
    """Implementation description."""
    
    def __init__(
        self,
        {dependency}: {DependencyType},
        {another_dependency}: {AnotherType},
    ):
        self._{dependency} = {dependency}
        self._{another_dependency} = {another_dependency}
        self._initialize()
        
    def _initialize(self) -> None:
        """Private initialization logic."""
        # Implementation details
        
    def {public_method}(self, {parameters}) -> {return_type}:
        """Public method description."""
        # Implementation logic
```

## Container Integration

### {Container Name} Registration

{Show how the service is registered in the dependency injection container}

```python
# In src/kp_ssf_tools/containers/{container_name}.py
class {ContainerName}(containers.DeclarativeContainer):
    """Container for {container description}."""
    
    # Configuration injection
    config = providers.Configuration()
    
    # Service configuration
    {service_name}_config: providers.Factory[{ConfigType}] = providers.Factory(
        {ConfigType},
        {config_field}=config.{config_path},
        {another_field}=config.{another_path}.as_(int),
    )
    
    # Primary service
    {service_name}: providers.Singleton[{ServiceType}] = providers.Singleton(
        {ServiceType},
        config={service_name}_config,
        {dependency}={dependency_reference},
    )
    
    # Service aggregate (if applicable)
    {aggregate_name} = providers.Aggregate(
        {service_name}={service_name},
        # ... other services
    )
```

## CLI Integration

### {Command Group} Commands

{Describe the CLI commands that interact with this service}

```python
# src/kp_ssf_tools/cli/commands/{command_name}.py
import click
from dependency_injector.wiring import inject, Provide
from kp_ssf_tools.containers import ApplicationContainer

@click.group()
def {command_group}():
    """{Command group description}."""
    pass

@click.command()
@click.option("--{option-name}", help="{Option description}")
@inject
def {command_name}(
    {option_name}: {type},
    {service_name}=Provide[ApplicationContainer.{container}.{service}],
    output=Provide[ApplicationContainer.core.rich_output],
):
    """{Command description}."""
    try:
        # Command logic
        result = {service_name}.{method_name}({parameters})
        
        # Output formatting
        output.success(f"{Success message}: {result}")
        
    except Exception as e:
        output.error(f"Error message: {e}")
        raise click.ClickException(str(e))

# Register commands
{command_group}.add_command({command_name})
```

### CLI Command Registration

{Show how commands are registered in the main CLI}

```python
# In src/kp_ssf_tools/cli/main.py
def register_commands() -> None:
    """Register all CLI commands."""
    from kp_ssf_tools.cli.commands.{command_name} import {command_group}
    # ... other imports
    
    cli.add_command({command_group})
    # ... other commands
```

## Service Integration Patterns

### {Integration Service} Integration

{Show how this service integrates with other services in the system}

```python
class {IntegrationService}:
    """{Integration service description}."""
    
    def __init__(
        self,
        {this_service}: {ThisServiceProtocol},
        {other_service}: {OtherServiceProtocol},
        output: RichOutputProtocol,
    ):
        self._{this_service} = {this_service}
        self._{other_service} = {other_service}
        self._output = output
        
    def {integration_method}(self, {parameters}) -> {return_type}:
        """Integration method description."""
        # Show how services work together
        result = self._{this_service}.{method}({params})
        processed = self._{other_service}.{process}(result)
        return processed
```

## Usage Examples

### Basic Operations

{Provide command-line examples of common operations}

```bash
# Basic usage example
ssf_tools {command} {subcommand} {arguments}

# Example with options
ssf_tools {command} {subcommand} --{option} {value}

# Complex example
ssf_tools {command} {subcommand} --{option1} {value1} --{option2} {value2}
```

### Service Usage in Commands

{Show how the service is used programmatically within other commands}

```python
@inject
def {command_function}(
    {parameter}: {type},
    {service_name}=Provide[ApplicationContainer.{container}.{service}],
):
    """{Command description}."""
    
    # Service usage example
    result = {service_name}.{method}({parameters})
    
    # Process result
    processed = process_result(result)
    return processed
```

## Performance Considerations

### {Performance Aspect 1}

{Description of performance considerations and optimizations}

- **{Optimization 1}**: {Description}
- **{Optimization 2}**: {Description}
- **{Optimization 3}**: {Description}

### {Performance Aspect 2}

{Description of another performance area}

- **{Strategy 1}**: {Description}
- **{Strategy 2}**: {Description}
- **{Strategy 3}**: {Description}

### {Performance Aspect 3}

{Description of third performance area}

- **{Approach 1}**: {Description}
- **{Approach 2}**: {Description}
- **{Approach 3}**: {Description}

## Testing Patterns

### Mock {Service Name}

{Show how to create mock services for testing}

```python
@pytest.fixture
def mock_{service_name}():
    """Mock {service name} for testing."""
    mock_{service} = Mock(spec={ServiceProtocol})
    mock_{service}.{method}.return_value = {expected_return}
    return mock_{service}

def test_{functionality}_with_{service}(mock_{service_name}):
    """Test {functionality} with mocked {service}."""
    # Test logic with mocked service
    pass
```

### Integration Testing

{Show integration testing patterns}

```python
def test_{service_name}_integration():
    """Test {service name} with real dependencies."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {ConfigType}({config_params})
        {service_name} = {ServiceType}(config, mock_dependencies)
        
        # Test service operations
        result = {service_name}.{method}({parameters})
        assert result.{property} == {expected_value}
```

## Implementation Roadmap

### Phase 1: {Phase Name}
- [ ] {Task 1 description}
- [ ] {Task 2 description}
- [ ] {Task 3 description}
- [ ] {Task 4 description}

### Phase 2: {Phase Name}
- [ ] {Task 1 description}
- [ ] {Task 2 description}
- [ ] {Task 3 description}
- [ ] {Task 4 description}

### Phase 3: {Phase Name}
- [ ] {Task 1 description}
- [ ] {Task 2 description}
- [ ] {Task 3 description}
- [ ] {Task 4 description}

### Phase 4: {Phase Name}
- [ ] {Task 1 description}
- [ ] {Task 2 description}
- [ ] {Task 3 description}

{Concluding statement about the architecture and its benefits to the SSF Tools ecosystem.}
