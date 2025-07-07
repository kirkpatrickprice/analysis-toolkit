# PowerShell script to update CLI test files to use shared fixtures
param(
    [string]$FilePath
)

# Read the file content
$content = Get-Content $FilePath -Raw

# Remove CliRunner import line
$content = $content -replace "from click\.testing import CliRunner`r?`n", ""

# Replace runner = CliRunner() with comment
$content = $content -replace "(\s+)runner = CliRunner\(\)", '$1# Using shared cli_runner fixture'

# Replace runner.invoke with cli_runner.invoke
$content = $content -replace "runner\.invoke", "cli_runner.invoke"

# Write back to file
Set-Content $FilePath $content -NoNewline

Write-Host "Updated $FilePath"
