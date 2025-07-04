# GitHub Actions Workflows

This repository includes three automated workflows using the latest GitHub Actions. The workflows are optimized for efficient CI/CD with comprehensive cross-platform testing when needed and quick feedback during development.

## 📦 Publish Workflow (`publish.yml`)

**Triggers:**
- After `Cross-Platform Unit Tests` workflow completes successfully on `main` branch
- Manual trigger via GitHub web interface

**Features:**
- **Depends on cross-platform tests**: Only runs after test.yml passes on all platforms
- Automatically detects version changes in `src/kp_analysis_toolkit/__init__.py`
- Builds and publishes to PyPI using trusted publishing
- Creates GitHub releases with automatic changelogs
- Uses semantic versioning
- Provides detailed logging and notifications

**Requirements:**
- `PYPI_API_TOKEN` secret configured in repository settings
- Cross-platform tests must pass first
- Optional: GitHub environment named `pypi` for enhanced security (currently disabled)

**Process:**
1. Waits for `Cross-Platform Unit Tests` workflow to complete successfully
2. Monitors changes to `__version__` in `__init__.py`
3. Compares current version with previous commit
4. If version changed and tests passed, builds package using `uv build`
5. Publishes to PyPI using official PyPA action
6. Creates GitHub release with version tag
7. Provides success/failure notifications

**Manual Release:**
1. Update version in `src/kp_analysis_toolkit/__init__.py`
2. Commit and push to `main` branch
3. Cross-platform tests run automatically
4. If tests pass, publish workflow detects change and publishes

## 🧪 Cross-Platform Test Workflow (`test.yml`)

**Triggers:**
- Push to `main` branch only
- Pull requests to `main` 
- Manual trigger via GitHub web interface

**Features:**
- Tests on Windows, macOS, and Linux (comprehensive cross-platform support)
- Uses Python 3.12
- Runs all 460+ unit tests with pytest
- Includes syntax checking across all platforms
- Generates JUnit XML test reports
- Uploads test artifacts
- Publishes test results in PR comments
- **Required for publishing**: Publish workflow waits for this to complete successfully
- Uses latest GitHub Actions (checkout@v4, setup-python@v5, upload-artifact@v4)

**Manual Trigger:**
1. Go to the "Actions" tab in GitHub
2. Select "Cross-Platform Unit Tests" workflow
3. Click "Run workflow"
4. Choose the branch and click "Run workflow"

## ⚡ Quick Test Workflow (`quick-test.yml`)

**Triggers:**
- Push to feature branches (`feature/*`, `fix/*`, `hotfix/*`)
- Manual trigger via GitHub web interface

**Features:**
- Windows-only testing for faster feedback during development
- Fails fast on first error
- Includes syntax checking
- Optimized for development workflow
- Provides rapid feedback without consuming excessive CI resources

## 🎯 Testing Strategy

### **Optimized CI/CD Approach:**
- **Feature branches**: Use `quick-test.yml` for rapid feedback (Windows-only)
- **Main branch**: Full cross-platform testing with `test.yml` (Windows, macOS, Linux)
- **Publishing**: Depends on successful cross-platform tests
- **Pull requests**: Cross-platform tests run to ensure compatibility before merge

### **Resource Efficiency:**
- Avoid running expensive cross-platform tests on every feature push
- Use quick Windows-only tests for development iterations
- Reserve comprehensive testing for main branch and releases
- Balanced approach between thorough testing and CI resource usage

## 📊 Test Results

- Test results are displayed in the GitHub Actions interface
- JUnit XML files are uploaded as artifacts for detailed analysis
- Pull request comments show test status and results

## 🔧 Local Testing

To run the same tests locally (works on Windows, macOS, and Linux):

```bash
# Install dependencies
uv sync --dev

# Run all tests
uv run pytest tests/ -v

# Run tests with XML output (like CI)
uv run pytest tests/ -v --tb=short --junitxml=pytest-results.xml

# Quick test run
uv run pytest tests/ -v --tb=short --ff

# Syntax check
uv run python -c "import compileall; import sys; sys.exit(0 if compileall.compile_dir('src/kp_analysis_toolkit', quiet=1) else 1)"
```

## 🐛 Known Issues

**StopIteration in CI**: Some tests may fail in GitHub Actions with `StopIteration` errors due to mock exhaustion in pytest with Python 3.12+. This is typically caused by mocks with limited `side_effect` values. If you encounter this:

1. Check if mocks have enough return values for all expected calls
2. Consider using `unittest.mock.DEFAULT` or more values in `side_effect`
3. The same tests usually pass locally due to different execution contexts

**Windows Path Comparison**: On Windows, path comparisons may fail due to short/long filename differences (e.g., `RUNNER~1` vs `runneradmin`). To fix:

1. Use `path.resolve()` on both paths before comparison
2. Example: `assert result.resolve() == expected.resolve()`
3. This normalizes paths to their absolute, canonical form

**Windows Glob Patterns**: PowerShell doesn't handle Unix-style glob patterns (`**/*.py`) the same way. Use Python's `compileall` module instead:

1. Replace: `python -m py_compile src/**/*.py`
2. With: `python -c "import compileall; sys.exit(0 if compileall.compile_dir('src/module') else 1)"`
3. This provides cross-platform syntax checking
