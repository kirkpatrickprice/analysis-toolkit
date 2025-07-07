# Test Migration Script: Move Complex Regex Test Infrastructure
# This script moves tests/process_scripts/regex/ to tests/unit/process_scripts/regex/
# and updates all cross-test import dependencies

# Determine the repository root (parent directory of scripts/)
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Split-Path -Parent $ScriptPath
Set-Location $RepoRoot

Write-Host "Repository root: $RepoRoot"
Write-Host "Starting regex test infrastructure migration..."

# Step 3a: Create new regex subdirectory structure (preserving original layout)
New-Item -ItemType Directory -Path "tests\unit\process_scripts\regex" -Force
New-Item -ItemType Directory -Path "tests\unit\process_scripts\regex\linux" -Force
New-Item -ItemType Directory -Path "tests\unit\process_scripts\regex\macos" -Force
New-Item -ItemType Directory -Path "tests\unit\process_scripts\regex\windows" -Force

# Create __init__.py files
New-Item -ItemType File -Path "tests\unit\process_scripts\regex\__init__.py" -Force
New-Item -ItemType File -Path "tests\unit\process_scripts\regex\linux\__init__.py" -Force
New-Item -ItemType File -Path "tests\unit\process_scripts\regex\macos\__init__.py" -Force
New-Item -ItemType File -Path "tests\unit\process_scripts\regex\windows\__init__.py" -Force

# Step 3b: Move base infrastructure files (no import changes needed for these)
Move-Item "tests\process_scripts\regex\common_base.py" "tests\unit\process_scripts\regex\" -Force
Move-Item "tests\process_scripts\regex\README.md" "tests\unit\process_scripts\regex\" -Force -ErrorAction SilentlyContinue
Move-Item "tests\process_scripts\regex\MULTI_PLATFORM_EXPANSION_SUMMARY.md" "tests\unit\process_scripts\regex\" -Force -ErrorAction SilentlyContinue

# Step 3c: Move and update dynamic_test_generator.py
Move-Item "tests\process_scripts\regex\dynamic_test_generator.py" "tests\unit\process_scripts\regex\" -Force

# Update import in dynamic_test_generator.py
$dynamicGeneratorFile = "tests\unit\process_scripts\regex\dynamic_test_generator.py"
if (Test-Path $dynamicGeneratorFile) {
    $content = Get-Content $dynamicGeneratorFile -Raw
    $content = $content -replace "from tests\.process_scripts\.regex\.common_base import", "from tests.unit.process_scripts.regex.common_base import"
    Set-Content $dynamicGeneratorFile $content
    Write-Host "[SUCCESS] Updated imports in dynamic_test_generator.py"
}

# Step 3d: Move and update test_all_platforms.py
Move-Item "tests\process_scripts\regex\test_all_platforms.py" "tests\unit\process_scripts\regex\" -Force -ErrorAction SilentlyContinue

$testAllPlatformsFile = "tests\unit\process_scripts\regex\test_all_platforms.py"
if (Test-Path $testAllPlatformsFile) {
    $content = Get-Content $testAllPlatformsFile -Raw
    $content = $content -replace "from tests\.process_scripts\.regex\.", "from tests.unit.process_scripts.regex."
    Set-Content $testAllPlatformsFile $content
    Write-Host "[SUCCESS] Updated imports in test_all_platforms.py"
}

# Step 3e: Move Linux test files and update imports
Move-Item "tests\process_scripts\regex\linux\test_all_linux_dynamic.py" "tests\unit\process_scripts\regex\linux\" -Force

$linuxFile = "tests\unit\process_scripts\regex\linux\test_all_linux_dynamic.py"
if (Test-Path $linuxFile) {
    $content = Get-Content $linuxFile -Raw
    $content = $content -replace "from tests\.process_scripts\.regex\.dynamic_test_generator import", "from tests.unit.process_scripts.regex.dynamic_test_generator import"
    Set-Content $linuxFile $content
    Write-Host "[SUCCESS] Updated imports in Linux dynamic test file"
}

# Step 3f: Move macOS test files and update imports
Move-Item "tests\process_scripts\regex\macos\test_all_macos_dynamic.py" "tests\unit\process_scripts\regex\macos\" -Force

$macosFile = "tests\unit\process_scripts\regex\macos\test_all_macos_dynamic.py"
if (Test-Path $macosFile) {
    $content = Get-Content $macosFile -Raw
    $content = $content -replace "from tests\.process_scripts\.regex\.dynamic_test_generator import", "from tests.unit.process_scripts.regex.dynamic_test_generator import"
    Set-Content $macosFile $content
    Write-Host "[SUCCESS] Updated imports in macOS dynamic test file"
}

# Step 3g: Move Windows infrastructure files
Move-Item "tests\process_scripts\regex\windows\base.py" "tests\unit\process_scripts\regex\windows\" -Force -ErrorAction SilentlyContinue
Move-Item "tests\process_scripts\regex\windows\README.md" "tests\unit\process_scripts\regex\windows\" -Force -ErrorAction SilentlyContinue
Move-Item "tests\process_scripts\regex\windows\DYNAMIC_TESTS_SUMMARY.md" "tests\unit\process_scripts\regex\windows\" -Force -ErrorAction SilentlyContinue
Move-Item "tests\process_scripts\regex\windows\test_windows_system_README.md" "tests\unit\process_scripts\regex\windows\" -Force -ErrorAction SilentlyContinue

# Step 3h: Move and update Windows dynamic test file
Move-Item "tests\process_scripts\regex\windows\test_all_windows_dynamic.py" "tests\unit\process_scripts\regex\windows\" -Force

$windowsDynamicFile = "tests\unit\process_scripts\regex\windows\test_all_windows_dynamic.py"
if (Test-Path $windowsDynamicFile) {
    $content = Get-Content $windowsDynamicFile -Raw
    $content = $content -replace "from tests\.process_scripts\.regex\.dynamic_test_generator import", "from tests.unit.process_scripts.regex.dynamic_test_generator import"
    Set-Content $windowsDynamicFile $content
    Write-Host "[SUCCESS] Updated imports in Windows dynamic test file"
}

# Step 3i: Move individual Windows test files and update their imports
$windowsTestFiles = @(
    "test_windows_logging.py",
    "test_windows_network.py", 
    "test_windows_security_software.py",
    "test_windows_system.py",
    "test_windows_users.py"
)

foreach ($file in $windowsTestFiles) {
    $sourcePath = "tests\process_scripts\regex\windows\$file"
    $destPath = "tests\unit\process_scripts\regex\windows\$file"
    
    if (Test-Path $sourcePath) {
        Move-Item $sourcePath $destPath -Force
        
        # Update imports in each file
        $content = Get-Content $destPath -Raw
        $content = $content -replace "from tests\.process_scripts\.regex\.windows\.test_all_windows_dynamic import", "from tests.unit.process_scripts.regex.windows.test_all_windows_dynamic import"
        Set-Content $destPath $content
        Write-Host "[SUCCESS] Moved and updated imports in $file"
    }
}

# Step 3j: Clean up old directories (verify they're empty first)
$foldersToRemove = @(
    "tests\process_scripts\regex\windows",
    "tests\process_scripts\regex\linux", 
    "tests\process_scripts\regex\macos",
    "tests\process_scripts\regex"
)

foreach ($folder in $foldersToRemove) {
    if (Test-Path $folder) {
        $items = Get-ChildItem $folder -Recurse
        if ($items.Count -eq 0) {
            Remove-Item $folder -Recurse -Force
            Write-Host "[SUCCESS] Removed empty directory: $folder"
        } else {
            Write-Host "[WARNING] Directory not empty, manual cleanup needed: $folder"
            Write-Host "   Remaining items: $($items.Name -join ', ')"
        }
    }
}

Write-Host ""
Write-Host "[SUCCESS] Step 3 completed: Moved complex regex test infrastructure with updated imports"
Write-Host "[INFO] Preserved original file names and directory structure"
Write-Host "[INFO] Manual verification recommended for complex import patterns"
