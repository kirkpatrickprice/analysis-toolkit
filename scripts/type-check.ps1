#!/usr/bin/env pwsh
# PowerShell script for gradual mypy type checking

param(
    [string]$Target = "all",
    [switch]$Strict = $false,
    [switch]$Report = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "MyPy Type Checking Script for KP Analysis Toolkit" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\scripts\type-check.ps1 [OPTIONS]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Target <module>    Target module to check (all, models, utils, cli, core, process_scripts)" -ForegroundColor Cyan
    Write-Host "  -Strict            Enable strict mode for the target" -ForegroundColor Cyan
    Write-Host "  -Report            Generate HTML coverage report" -ForegroundColor Cyan
    Write-Host "  -Help              Show this help message" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\scripts\type-check.ps1                      # Check all modules with gradual settings"
    Write-Host "  .\scripts\type-check.ps1 -Target models       # Check only models module"
    Write-Host "  .\scripts\type-check.ps1 -Target utils -Strict # Check utils with strict mode"
    Write-Host "  .\scripts\type-check.ps1 -Report              # Generate coverage report"
    exit 0
}

Write-Host "KP Analysis Toolkit - MyPy Type Checking" -ForegroundColor Green
Write-Host "Target: $Target" -ForegroundColor Yellow

$srcPath = "src/kp_analysis_toolkit"
$baseArgs = @("run", "mypy")

if ($Report) {
    Write-Host "Generating HTML coverage report..." -ForegroundColor Blue
    $reportArgs = $baseArgs + @("--html-report", "mypy-report", "$srcPath/")
    uv @reportArgs
    Write-Host "Report generated in mypy-report/" -ForegroundColor Green
    exit $LASTEXITCODE
}

switch ($Target.ToLower()) {
    "all" {
        Write-Host "Checking all modules with gradual settings..." -ForegroundColor Blue
        $targetPath = @("$srcPath/", "tests/")
    }
    "models" {
        Write-Host "Checking models module..." -ForegroundColor Blue
        $targetPath = @("$srcPath/models/")
    }
    "utils" {
        Write-Host "Checking utils module..." -ForegroundColor Blue  
        $targetPath = @("$srcPath/utils/")
    }
    "cli" {
        Write-Host "Checking CLI module..." -ForegroundColor Blue
        $targetPath = @("$srcPath/cli/")
    }
    "core" {
        Write-Host "Checking core module..." -ForegroundColor Blue
        $targetPath = @("$srcPath/core/")
    }
    "process_scripts" {
        Write-Host "Checking process_scripts module..." -ForegroundColor Blue
        $targetPath = @("$srcPath/process_scripts/")
    }
    default {
        Write-Host "Unknown target: $Target" -ForegroundColor Red
        Write-Host "Valid targets: all, models, utils, cli, core, process_scripts" -ForegroundColor Yellow
        exit 1
    }
}

$mypyArgs = $baseArgs + $targetPath

if ($Strict) {
    Write-Host "Using strict mode..." -ForegroundColor Yellow
    $mypyArgs += "--strict"
}

Write-Host "Running: uv $($mypyArgs -join ' ')" -ForegroundColor Gray
uv @mypyArgs

$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "Type checking completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Type checking found issues (exit code: $exitCode)" -ForegroundColor Red
}

exit $exitCode
