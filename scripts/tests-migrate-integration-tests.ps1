# scripts/tests-migrate-integration-tests.ps1
"""Migrate integration tests to the new test structure."""

# Create the integration test directory
if (-not (Test-Path "tests\integration")) {
    New-Item -ItemType Directory -Path "tests\integration" -Force
    Write-Host "Created tests\integration directory"
}

# Move integration tests (these are at the root level)
$integrationTests = @(
    "test_integration.py"
)

foreach ($test in $integrationTests) {
    if (Test-Path $test) {
        Move-Item -Path $test -Destination "tests\integration\$test" -Force
        Write-Host "Moved $test to tests\integration\"
    }
}

# Create integration test __init__.py
if (-not (Test-Path "tests\integration\__init__.py")) {
    New-Item -ItemType File -Path "tests\integration\__init__.py" -Force
    Write-Host "Created tests\integration\__init__.py"
}

Write-Host "Integration test migration complete!"
Write-Host "Remember to update any import paths in the migrated files if needed."
