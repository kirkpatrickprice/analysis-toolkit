# Development Documentation

Developer-focused documentation for contributing to and extending the toolkit.

## Contents

This directory contains:

- **Setup Guide** - Development environment setup
- **Contributing** - Guidelines for contributing code
- **Code Standards** - Coding conventions and standards
- **Testing** - Testing procedures and guidelines
- **Release Process** - How to create and manage releases

## Development Topics

### Getting Started
- Development environment setup
- Installing dependencies
- Running tests
- Code organization

### Contributing Guidelines
- Code review process
- Commit message standards
- Branch naming conventions
- Pull request guidelines

### Code Quality
- Linting and formatting
- Type checking
- Code documentation
- Performance considerations

### Testing
- Unit testing guidelines
- Integration testing
- Test data management
- Test coverage requirements
- [CLI Testing Standards](cli-testing-standards.md) - Standards for CLI component testing
- [Test Directory Organization](test-directory-organization.md) - Test structure and shared fixtures
- [GitHub Actions Pipeline Analysis](github-actions-pipeline-analysis.md) - CI/CD pipeline review and recommendations

## Completed Development Docs

- [x] [CLI Testing Standards](cli-testing-standards.md) - CLI testing best practices and shared fixtures
- [x] [Test Directory Organization](test-directory-organization.md) - Test structure analysis and implementation
- [x] [GitHub Actions Pipeline Analysis](github-actions-pipeline-analysis.md) - Pipeline improvements and Rich output testing

## Planned Development Docs

- [ ] Development environment setup
- [ ] Contributing guidelines
- [ ] Code style guide
- [ ] Testing strategy (comprehensive)
- [ ] Release process
- [ ] Debugging guide
- [ ] Performance profiling
- [ ] Adding new commands

## Development

### Development Environment
- **Primary development platform**: Windows
- **Testing**: Comprehensive CI testing on Windows, macOS, and Linux
- **Cross-platform compatibility**: Ensured through automated testing

While development is primarily conducted on Windows, the toolkit is designed to be cross-platform compatible. Continuous Integration (CI) testing is performed against all three major operating systems (Windows, macOS, and Linux) to ensure proper functionality across platforms.

### Running from Source
For development or testing purposes:

```bash
# Clone the repository
git clone https://github.com/kirkpatrickprice/analysis-toolkit.git
cd analysis-toolkit

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .

# Run directly
python -m kp_analysis_toolkit.cli --help
```

### Dependencies
The toolkit automatically installs required dependencies:
- **pandas** and **openpyxl** for Excel processing
- **PyYAML** for configuration files
- **click** for command-line interface
- **pydantic** for data validation
- **charset-normalizer** for encoding detection
- **striprtf** for RTF processing

### Publishing and Releases
The toolkit uses automated publishing to PyPI:
- **Cross-platform testing**: Full test suite runs on Windows, macOS, and Linux before publishing
- **Automatic publishing**: When the version in `src/kp_analysis_toolkit/__init__.py` is updated and pushed to the main branch
- **GitHub Actions**: Handles testing, building, and publishing automatically
- **GitHub Releases**: Automatically created with version tags and changelogs
- **Quality assurance**: Cross-platform tests must pass before publishing

📖 **[View Publishing Setup Guide](.github/PYPI_SETUP.md)** for maintainers

