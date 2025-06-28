# PyPI Publishing Setup

This document describes how to set up automatic PyPI publishing for the KP Analysis Toolkit.

## Prerequisites

1. **PyPI Account**: You need a PyPI account with publishing permissions for the `kp-analysis-toolkit` package
2. **GitHub Repository**: Admin access to configure secrets and environments

## Setup Steps

### 1. Generate PyPI API Token

1. Log in to [PyPI](https://pypi.org/)
2. Go to Account Settings → API tokens
3. Click "Add API token"
4. Set the token name (e.g., "GitHub Actions - analysis-toolkit")
5. Set scope to "Entire account" or limit to specific project
6. Copy the generated token (starts with `pypi-`)

### 2. Configure GitHub Repository

#### Option A: Using Repository Secrets (Simple)

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value: Paste the PyPI API token
6. Click "Add secret"

#### Option B: Using Environments (Optional)

*Note: The workflow currently uses repository secrets for simplicity. You can optionally set up environments for enhanced security.*

1. Go to your GitHub repository
2. Navigate to Settings → Environments
3. Click "New environment"
4. Name: `pypi`
5. (Optional) Add protection rules:
   - Required reviewers
   - Wait timer
   - Deployment branches (e.g., only `main`)
6. Add environment secret:
   - Name: `PYPI_API_TOKEN`
   - Value: Paste the PyPI API token
7. Uncomment the `environment: pypi` line in `.github/workflows/publish.yml`

### 3. Test the Workflow

1. Update the version in `src/kp_analysis_toolkit/__init__.py`:
   ```python
   __version__ = "2.0.3"  # Increment from current version
   ```

2. Commit and push to the `main` branch:
   ```bash
   git add src/kp_analysis_toolkit/__init__.py
   git commit -m "Bump version to 2.0.3"
   git push origin main
   ```

3. Check the GitHub Actions tab to see the workflow running

## How It Works

### Version Detection
- The workflow monitors changes to `src/kp_analysis_toolkit/__init__.py`
- It compares the current `__version__` with the previous commit
- If the version changed, it triggers the publishing process

### Publishing Process
1. **Tests**: Runs the full test suite to ensure quality
2. **Build**: Creates both wheel and source distributions using `uv build`
3. **Verify**: Checks that build artifacts were created correctly
4. **Publish**: Uploads to PyPI using the official PyPA action
5. **Release**: Creates a GitHub release with the new version tag
6. **Notify**: Reports success or failure

### Security Features
- Uses GitHub's trusted publishing (no long-lived secrets)
- Optional environment protection rules
- Full audit trail in GitHub Actions logs
- Automatic artifact verification

## Troubleshooting

### Common Issues

**"Package already exists" error:**
- The version number hasn't changed, or
- The version was already published
- Check PyPI to see current published version

**"Invalid credentials" error:**
- PyPI API token is incorrect or expired
- Token doesn't have permission for this package
- Regenerate token and update GitHub secret

**Tests failing:**
- Fix test failures before the version will publish
- All tests must pass for publishing to proceed

**Build failures:**
- Check `pyproject.toml` configuration
- Ensure all required files are included
- Check for import errors or missing dependencies

### Manual Workflow Trigger

You can manually trigger the publish workflow:

1. Go to Actions tab in GitHub
2. Select "Publish to PyPI" workflow
3. Click "Run workflow"
4. Select the branch (usually `main`)
5. Click "Run workflow"

This will check if the version changed and publish if needed.

## Version Management

### Semantic Versioning
Follow [semantic versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., 2.1.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Workflow
1. Make your changes
2. Update `CHANGELOG.md` with changes
3. Bump version in `src/kp_analysis_toolkit/__init__.py`
4. Commit with message: "Bump version to X.Y.Z"
5. Push to `main` branch
6. Workflow automatically publishes

## Monitoring

### Check Publishing Status
- GitHub Actions tab shows workflow status
- PyPI shows published packages
- GitHub Releases tab shows created releases
- Users can update with: `pipx upgrade kp-analysis-toolkit`

### Rollback Process
If you need to rollback:
1. PyPI doesn't allow file replacement
2. Publish a new patch version with fixes
3. Consider yanking the problematic version on PyPI (if critical)
