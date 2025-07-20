# Pytest Fixture Organization

## Fixture Strategy

### Approach: Hybrid Shared + Hierarchical Organization

Based on the cross-domain usage analysis, we'll use a hybrid approach that keeps truly shared fixtures accessible while organizing domain-specific fixtures in specialized modules.

### Target Directory Structure

Refer to [Pytest Directory Structure](test-directory-organization.md)

All fixtures are to be created either in `conftest.py` for cross-domain fixtures or in one of the `tests/fixtures` domain-specific fixture files.  Fixtures are not to be created in the `unit`, `integration` or other test-specific directories.


