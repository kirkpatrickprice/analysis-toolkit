# Clean-PyCache.ps1
# PowerShell script to remove all __pycache__ directories from the workspace

<#
.SYNOPSIS
    Removes all __pycache__ directories and their contents from the current workspace.

.DESCRIPTION
    This script recursively searches for __pycache__ directories starting from the current
    working directory and removes them along with all their contents. This is useful for
    cleaning up Python bytecode cache files that can accumulate during development.

.PARAMETER Preview
    Shows what would be deleted without actually deleting anything.

.PARAMETER ShowDetails
    Shows detailed information about what is being processed.

.EXAMPLE
    .\clean-pycache.ps1
    Removes all __pycache__ directories from the current workspace.

.EXAMPLE
    .\clean-pycache.ps1 -Preview
    Shows what __pycache__ directories would be removed without actually removing them.

.EXAMPLE
    .\clean-pycache.ps1 -ShowDetails
    Removes __pycache__ directories with detailed output.
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [switch]$Preview,
    [switch]$ShowDetails
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to format file sizes
function Format-FileSize {
    param([long]$Size)
    
    $units = @("B", "KB", "MB", "GB", "TB")
    $index = 0
    $formattedSize = $Size
    
    while ($formattedSize -ge 1024 -and $index -lt $units.Length - 1) {
        $formattedSize = $formattedSize / 1024
        $index++
    }
    
    return "{0:N2} {1}" -f $formattedSize, $units[$index]
}

# Function to get directory size
function Get-DirectorySize {
    param([string]$Path)
    
    try {
        $files = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue
        $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
        return if ($totalSize) { $totalSize } else { 0 }
    }
    catch {
        return 0
    }
}

# Main script execution
try {
    Write-Host "Python Cache Cleaner" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan
    Write-Host ""
    
    # Get the current working directory
    $workspaceRoot = Get-Location
    Write-Host "Scanning workspace: $workspaceRoot" -ForegroundColor Green
    Write-Host ""
    
    # Find all __pycache__ directories
    Write-Host "Searching for __pycache__ directories..." -ForegroundColor Yellow
    
    $pycacheDirectories = Get-ChildItem -Path $workspaceRoot -Name "__pycache__" -Directory -Recurse -ErrorAction SilentlyContinue
    
    if ($pycacheDirectories.Count -eq 0) {
        Write-Host "No __pycache__ directories found. Workspace is already clean!" -ForegroundColor Green
        exit 0
    }
    
    Write-Host "Found $($pycacheDirectories.Count) __pycache__ director$(if ($pycacheDirectories.Count -ne 1) { 'ies' } else { 'y' })" -ForegroundColor Cyan
    Write-Host ""
    
    # Calculate total size and display details
    $totalSize = 0
    $processedCount = 0
    
    foreach ($dir in $pycacheDirectories) {
        $fullPath = Join-Path $workspaceRoot $dir
        $dirSize = Get-DirectorySize -Path $fullPath
        $totalSize += $dirSize
        
        $relativePath = Resolve-Path -Path $fullPath -Relative
        $formattedSize = Format-FileSize -Size $dirSize
        
        if ($ShowDetails) {
            Write-Host "   $relativePath ($formattedSize)" -ForegroundColor Gray
        }
        
        if ($Preview) {
            Write-Host "PREVIEW: Would remove $relativePath ($formattedSize)" -ForegroundColor Magenta
        }
        else {
            try {
                Remove-Item -Path $fullPath -Recurse -Force
                $processedCount++
                if ($ShowDetails) {
                    Write-Host "   Removed $relativePath ($formattedSize)" -ForegroundColor Green
                }
            }
            catch {
                Write-Warning "Failed to remove $relativePath : $($_.Exception.Message)"
            }
        }
    }
    
    # Summary
    Write-Host ""
    Write-Host "Summary:" -ForegroundColor Cyan
    Write-Host "   Total directories found: $($pycacheDirectories.Count)" -ForegroundColor White
    Write-Host "   Total size: $(Format-FileSize -Size $totalSize)" -ForegroundColor White
    
    if ($Preview) {
        Write-Host "   Status: Simulation mode (use without -Preview to actually delete)" -ForegroundColor Magenta
    }
    else {
        Write-Host "   Successfully removed: $processedCount" -ForegroundColor Green
        if ($processedCount -lt $pycacheDirectories.Count) {
            $failedCount = $pycacheDirectories.Count - $processedCount
            Write-Host "   Failed to remove: $failedCount" -ForegroundColor Red
        }
        
        if ($processedCount -gt 0) {
            Write-Host ""
            Write-Host "Cleanup completed! Freed up $(Format-FileSize -Size $totalSize) of disk space." -ForegroundColor Green
        }
    }
}
catch {
    Write-Error "An error occurred: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Host "Tip: You can run this script with -Preview to preview what would be deleted." -ForegroundColor DarkGray
Write-Host "Tip: Use -ShowDetails to see detailed information about each directory." -ForegroundColor DarkGray
