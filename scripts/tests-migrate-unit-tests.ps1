# scripts/tests-migrate-unit-tests.ps1
"""Migrate remaining unit tests to the new test structure."""

# Create unit test directories
$unitDirs = @(
    "tests\unit",
    "tests\unit\nipper_expander",
    "tests\unit\process_scripts", 
    "tests\unit\rtf_to_text",
    "tests\unit\utils"
)

foreach ($dir in $unitDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "Created $dir directory"
    }
}

# Move unit test files (excluding regex which was already migrated)
$testMoves = @{
    "tests\nipper_expander\*.py" = "tests\unit\nipper_expander\"
    "tests\process_scripts\*.py" = "tests\unit\process_scripts\"
    "tests\rtf_to_text\*.py" = "tests\unit\rtf_to_text\"
    "tests\utils\*.py" = "tests\unit\utils\"
}

foreach ($move in $testMoves.GetEnumerator()) {
    $sourcePattern = $move.Key
    $destination = $move.Value
    
    $files = Get-ChildItem -Path $sourcePattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        Move-Item -Path $file.FullName -Destination $destination -Force
        Write-Host "Moved $($file.Name) to $destination"
    }
}

# Move remaining files from tests root
$rootTestFiles = @(
    "test_cli_integration.py",
    "test_shared_funcs.py"
)

foreach ($test in $rootTestFiles) {
    if (Test-Path "tests\$test") {
        Move-Item -Path "tests\$test" -Destination "tests\unit\$test" -Force
        Write-Host "Moved $test to tests\unit\"
    }
}

# Move model test directories
$modelDirs = @(
    "tests\process_scripts\models",
    "tests\nipper_expander\models",
    "tests\rtf_to_text\models"
)

foreach ($modelDir in $modelDirs) {
    if (Test-Path $modelDir) {
        $destination = $modelDir -replace "tests\\", "tests\unit\"
        Move-Item -Path $modelDir -Destination $destination -Force
        Write-Host "Moved $modelDir to $destination"
    }
}

# Create __init__.py files
$initFiles = @(
    "tests\unit\__init__.py",
    "tests\unit\nipper_expander\__init__.py",
    "tests\unit\process_scripts\__init__.py",
    "tests\unit\rtf_to_text\__init__.py", 
    "tests\unit\utils\__init__.py"
)

foreach ($init in $initFiles) {
    if (-not (Test-Path $init)) {
        New-Item -ItemType File -Path $init -Force
        Write-Host "Created $init"
    }
}

Write-Host "Unit test migration complete!"
Write-Host "Note: Regex tests were previously migrated separately."
Write-Host "Remember to update any import paths in the migrated files if needed."
