# Architecture Documentation Instructions

This document provides detailed guidance for creating and maintaining architecture documentation for SSF Tools services and components.

## Template Usage

Use the `docs/templates/architecture-document-template.md` template for all new architecture documents. Replace all placeholder text in `{curly braces}` with appropriate content for your specific service or component.

## Document Structure Requirements

### Overview Section
- **Purpose**: Start with a clear, concise explanation of what the service/component does
- **Context**: Explain how it fits within the broader SSF Tools ecosystem
- **Status**: Include implementation status (MVP, planned, in-development)
- **Scope**: Define what is and isn't covered in the document

### Architectural Principles
- **Design Goals**: 5 key goals that drive the architecture decisions
- **Key Benefits**: 5 primary benefits the architecture provides
- Use **bold formatting** for goal/benefit names followed by clear descriptions
- Focus on business value and technical value

### Architecture Overview Diagram
- **Required**: Include a comprehensive Mermaid diagram
- **Components**: Show all major components and their relationships
- **Grouping**: Use subgraphs to show logical boundaries
- **Styling**: Apply consistent CSS classes for visual coherence
- **Flow**: Show data flow and dependencies clearly

#### Mermaid Diagram Standards
- Use descriptive node labels with brief descriptions
- Group related components in subgraphs with emoji icons
- Apply consistent CSS styling classes:
  - `coreService`: Core infrastructure services
  - `protocol`: Protocol interfaces  
  - `component`: Service components
  - `integration`: Integration points
  - `cli`: CLI interfaces
  - `storage`: Storage/persistence
  - `group`: Subgraph styling

### Protocols Section
- **When Required**: Include for all services that implement protocol-based interfaces
- **Code Examples**: Provide complete, runnable protocol definitions
- **Type Hints**: Use modern Python type hints (no `typing.Union`, `Optional`)
- **Documentation**: Include comprehensive docstrings for all methods

### Configuration Models
- **When Required**: Include for all services that use configuration
- **Pydantic Models**: Show complete model definitions with field descriptions
- **Validation**: Include field validators where applicable
- **Global Integration**: Show how service config integrates with global config
- **YAML Examples**: Provide realistic configuration file examples

### Service Implementation
- **Core Class**: Show the main service class implementation
- **Dependencies**: Demonstrate dependency injection patterns
- **Key Methods**: Include primary public methods with implementations
- **Error Handling**: Show error handling patterns

### Container Integration
- **DI Configuration**: Show complete dependency injection setup
- **Provider Types**: Use appropriate provider types (Factory, Singleton, etc.)
- **Configuration Binding**: Show how configuration is injected
- **Service Aggregates**: Include service aggregates where applicable

### CLI Integration
- **Command Structure**: Show complete CLI command implementations
- **Click Decorators**: Use appropriate Click decorators and options
- **Dependency Injection**: Demonstrate proper DI usage in CLI commands
- **Error Handling**: Include proper error handling and user feedback
- **Registration**: Show how commands are registered in main CLI

### Service Integration Patterns
- **Cross-Service Usage**: Show how the service integrates with other services
- **Common Patterns**: Demonstrate typical usage patterns
- **Protocol Compliance**: Show protocol-based integration

### Usage Examples
- **CLI Examples**: Provide realistic command-line usage examples
- **Code Examples**: Show programmatic usage within other commands
- **Multiple Scenarios**: Cover basic and advanced usage patterns

### Performance Considerations
- **Three Categories**: Organize into 3 distinct performance areas
- **Specific Strategies**: Provide concrete optimization strategies
- **Measurable Impact**: Focus on performance aspects that matter

### Testing Patterns
- **Mock Services**: Show how to create proper mock services
- **Integration Tests**: Demonstrate integration testing approaches
- **Fixtures**: Provide reusable test fixtures
- **Coverage**: Cover both unit and integration testing patterns

### Implementation Roadmap
- **Four Phases**: Organize implementation into 4 logical phases
- **Checkboxes**: Use checkbox format for trackable tasks
- **Dependencies**: Order phases based on dependencies
- **Scope**: Each phase should represent meaningful deliverable units

## Content Guidelines

### Writing Style
- Use present tense for current functionality
- Use "will" for future/planned features
- Avoid: "ensure", "comprehensive", "strict", "rigorous", "well-defined", "effective"
- Keep sentences under 25 words
- Use active voice

### Code Standards
- Python 3.13+ with modern type hints
- No legacy typing imports (`typing.Union`, `Optional`, `Any`)
- Use absolute imports only
- Include complete, runnable code examples
- Add meaningful docstrings to all examples

### Technical Accuracy
- All code examples must be syntactically correct
- Test code snippets before including
- Use realistic parameter names and values
- Include proper error handling

### Visual Elements
- Use emoji sparingly in diagram subgraph titles (📁, 🔌, 💾, etc.)
- Apply consistent Mermaid styling across all diagrams
- Include meaningful alt text for accessibility
- Use tables for structured comparisons

## File Naming and Location

### Architecture Documents
- Location: `docs/architecture/{domain}/{service-name}.md`
- Naming: Use kebab-case for file names
- Example: `docs/architecture/core/cache-service-interface.md`

### Cross-References
- Link to related architecture documents
- Reference user guides where applicable
- Include links to implementation files
- Use relative paths for internal links

## Review Checklist

Before finalizing any architecture document, verify:

- [ ] All template placeholders `{like this}` have been replaced
- [ ] Mermaid diagram renders correctly and is visually clear
- [ ] All code examples are syntactically correct
- [ ] Protocol definitions include comprehensive type hints
- [ ] Configuration examples are realistic and complete
- [ ] CLI examples use correct command structure
- [ ] Performance considerations are specific and actionable
- [ ] Testing patterns are complete and demonstrate best practices
- [ ] Implementation roadmap is logical and achievable
- [ ] Document follows SSF Tools documentation standards
- [ ] All cross-references link correctly
- [ ] File is located in correct directory with proper naming

## Integration with Documentation Instructions

This template extends the general documentation instructions found in `.github/instructions/docs.instructions.md`. When conflicts arise, these architecture-specific guidelines take precedence for architecture documents.

### Key Differences from General Docs
- More structured template with specific sections
- Required Mermaid diagrams with specific styling
- Emphasis on protocol-based design patterns
- Mandatory code examples with type hints
- Specific performance and testing section requirements
- Four-phase implementation roadmap structure

## Maintenance

### Updates
- Review architecture documents quarterly for accuracy
- Update implementation roadmaps as features are completed
- Refresh code examples when APIs change
- Update Mermaid diagrams when architecture evolves

### Deprecation
- Mark deprecated sections clearly
- Provide migration guidance
- Maintain historical context for reference
- Archive outdated documents in `docs/archive/`

This template and guidance ensure consistent, comprehensive, and maintainable architecture documentation across all SSF Tools services and components.
