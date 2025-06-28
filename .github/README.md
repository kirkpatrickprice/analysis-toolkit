# GitHub Actions Workflows

This repository includes two automated testing workflows using the latest GitHub Actions.

## 🧪 Main Test Workflow (`test.yml`)

**Triggers:**
- Push to any branch except `main`
- Pull requests to `main` 
- Manual trigger via GitHub web interface

**Features:**
- Tests on Windows (officially supported OS)
- Uses Python 3.12
- Runs all 460+ unit tests with pytest
- Generates JUnit XML test reports
- Uploads test artifacts
- Publishes test results in PR comments
- Uses latest GitHub Actions (checkout@v4, setup-python@v5, upload-artifact@v4)

**Manual Trigger:**
1. Go to the "Actions" tab in GitHub
2. Select "Run Unit Tests" workflow
3. Click "Run workflow"
4. Choose the branch and click "Run workflow"

## ⚡ Quick Test Workflow (`quick-test.yml`)

**Triggers:**
- Push to feature branches (`feature/*`, `fix/*`, `hotfix/*`)
- Manual trigger via GitHub web interface

**Features:**
- Windows-only testing for faster feedback
- Fails fast on first error
- Includes syntax checking
- Optimized for development workflow

## 📊 Test Results

- Test results are displayed in the GitHub Actions interface
- JUnit XML files are uploaded as artifacts for detailed analysis
- Pull request comments show test status and results

## 🔧 Local Testing

To run the same tests locally on Windows:

```powershell
# Install dependencies
uv sync --dev

# Run all tests
uv run pytest tests/ -v

# Run tests with XML output (like CI)
uv run pytest tests/ -v --tb=short --junitxml=pytest-results.xml

# Quick test run
uv run pytest tests/ -v --tb=short --ff
```

## 🐛 Known Issues

**StopIteration in CI**: Some tests may fail in GitHub Actions with `StopIteration` errors due to mock exhaustion in pytest with Python 3.12+. This is typically caused by mocks with limited `side_effect` values. If you encounter this:

1. Check if mocks have enough return values for all expected calls
2. Consider using `unittest.mock.DEFAULT` or more values in `side_effect`
3. The same tests usually pass locally due to different execution contexts
