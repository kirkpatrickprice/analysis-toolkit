#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Benchmark KPAT CLI performance to measure lazy initialization improvements.

.DESCRIPTION
    This script measures the execution time of `uv run kpat_cli` commands to help
    evaluate the performance impact of lazy initialization changes. It provides
    detailed timing information and can run multiple iterations for statistical analysis.

.PARAMETER Command
    The KPAT command and arguments to benchmark (e.g., "--help", "scripts --help")

.PARAMETER Iterations
    Number of times to run the command for averaging (default: 5)

.PARAMETER WarmupRuns
    Number of warmup runs before timing (default: 1)

.PARAMETER ShowDetails
    Show detailed timing information for each run

.PARAMETER CompareBaseline
    Compare against a baseline file (saves/loads timing data)

.PARAMETER BaselineFile
    File to save/load baseline timing data (default: baseline-timings.json)

.EXAMPLE
    .\benchmark-kpat-performance.ps1 --help
    Benchmark the help command

.EXAMPLE
    .\benchmark-kpat-performance.ps1 "scripts --help" -Iterations 10 -ShowDetails
    Benchmark scripts help with 10 iterations and detailed output

.EXAMPLE
    .\benchmark-kpat-performance.ps1 --help -CompareBaseline
    Compare current help performance against saved baseline

.NOTES
    File Name      : benchmark-kpat-performance.ps1
    Author         : KP Analysis Toolkit
    Prerequisite   : PowerShell 5.1+, uv package manager
    Created        : 2025-08-01
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Command = @("--help"),
    
    [Parameter(Mandatory = $false)]
    [int]$Iterations = 5,
    
    [Parameter(Mandatory = $false)]
    [int]$WarmupRuns = 1,
    
    [Parameter(Mandatory = $false)]
    [switch]$ShowDetails,
    
    [Parameter(Mandatory = $false)]
    [switch]$CompareBaseline,
    
    [Parameter(Mandatory = $false)]
    [string]$BaselineFile = "baseline-timings.json"
)

# Convert command array to single string if needed
if ($Command.Count -gt 1) {
    $CommandString = $Command -join " "
} elseif ($Command.Count -eq 1 -and $null -ne $Command[0]) {
    $CommandString = $Command[0]
} else {
    $CommandString = "--help"
}

# Ensure we're in the correct directory (project root)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Push-Location $ProjectRoot

try {
    Write-Host "KPAT CLI Performance Benchmark" -ForegroundColor Cyan
    Write-Host "===============================" -ForegroundColor Cyan
    Write-Host "Command: uv run kpat_cli $CommandString" -ForegroundColor Yellow
    Write-Host "Iterations: $Iterations (+ $WarmupRuns warmup)" -ForegroundColor Yellow
    Write-Host "Working Directory: $ProjectRoot" -ForegroundColor Yellow
    Write-Host ""

    # Verify uv is available
    try {
        $uvVersion = & uv --version 2>$null
        Write-Host "Found uv: $uvVersion" -ForegroundColor Green
    }
    catch {
        Write-Error "ERROR: 'uv' command not found. Please install uv package manager."
        exit 1
    }

    # Verify kpat_cli is available
    try {
        $null = & uv run kpat_cli --version 2>$null
        Write-Host "KPAT CLI is available" -ForegroundColor Green
    }
    catch {
        Write-Warning "WARNING: Could not verify kpat_cli availability. Continuing anyway..."
    }
    
    Write-Host ""

    # Initialize timing arrays
    $timings = @()
    $allTimes = @()

    # Warmup runs
    if ($WarmupRuns -gt 0) {
        $warmupLabel = if($WarmupRuns -gt 1) { "iterations" } else { "iteration" }
        Write-Host "Running $WarmupRuns warmup $warmupLabel..." -ForegroundColor Magenta
        for ($i = 1; $i -le $WarmupRuns; $i++) {
            $null = Measure-Command { 
                $null = & uv run kpat_cli $CommandString.Split(' ') 2>$null 
            }
            Write-Progress -Activity "Warmup" -Status "Run $i of $WarmupRuns" -PercentComplete (($i / $WarmupRuns) * 100)
        }
        Write-Progress -Activity "Warmup" -Completed
        Write-Host ""
    }

    # Benchmark runs
    $iterLabel = if($Iterations -gt 1) { "iterations" } else { "iteration" }
    Write-Host "Running $Iterations benchmark $iterLabel..." -ForegroundColor Magenta
    
    for ($i = 1; $i -le $Iterations; $i++) {
        # Measure execution time
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        
        try {
            $null = & uv run kpat_cli $CommandString.Split(' ') 2>&1
            $exitCode = $LASTEXITCODE
        }
        catch {
            Write-Error "ERROR: Error executing command: $_"
            continue
        }
        
        $stopwatch.Stop()
        $timeMs = $stopwatch.ElapsedMilliseconds
        $timings += $timeMs
        $allTimes += @{
            Run = $i
            TimeMs = $timeMs
            ExitCode = $exitCode
        }
        
        if ($ShowDetails) {
            $status = if ($exitCode -eq 0) { "SUCCESS" } else { "FAILED" }
            $statusColor = if ($exitCode -eq 0) { "Green" } else { "Red" }
            Write-Host "  Run ${i}: $timeMs ms [$status]" -ForegroundColor $statusColor
        }
        
        Write-Progress -Activity "Benchmarking" -Status "Run $i of $Iterations ($timeMs ms)" -PercentComplete (($i / $Iterations) * 100)
    }
    
    Write-Progress -Activity "Benchmarking" -Completed
    Write-Host ""

    # Calculate statistics
    if ($timings.Count -gt 0) {
        $validTimings = $timings | Where-Object { $_ -gt 0 }
        
        if ($validTimings.Count -gt 0) {
            $min = ($validTimings | Measure-Object -Minimum).Minimum
            $max = ($validTimings | Measure-Object -Maximum).Maximum
            $avg = [math]::Round(($validTimings | Measure-Object -Average).Average, 2)
            $median = if ($validTimings.Count % 2 -eq 1) {
                $sorted = $validTimings | Sort-Object
                $sorted[[math]::Floor($validTimings.Count / 2)]
            } else {
                $sorted = $validTimings | Sort-Object
                $mid1 = $sorted[[math]::Floor($validTimings.Count / 2) - 1]
                $mid2 = $sorted[[math]::Floor($validTimings.Count / 2)]
                [math]::Round(($mid1 + $mid2) / 2, 2)
            }
            
            # Calculate standard deviation
            $variance = ($validTimings | ForEach-Object { [math]::Pow($_ - $avg, 2) } | Measure-Object -Sum).Sum / $validTimings.Count
            $stdDev = [math]::Round([math]::Sqrt($variance), 2)
            
            Write-Host "Performance Results" -ForegroundColor Cyan
            Write-Host "===================" -ForegroundColor Cyan
            Write-Host "Successful runs: $($validTimings.Count)/$Iterations" -ForegroundColor White
            Write-Host "Average time:    $avg ms" -ForegroundColor White
            Write-Host "Median time:     $median ms" -ForegroundColor White
            Write-Host "Min time:        $min ms" -ForegroundColor Green
            Write-Host "Max time:        $max ms" -ForegroundColor Red
            Write-Host "Std deviation:   $stdDev ms" -ForegroundColor White
            
            # Performance categorization
            if ($avg -lt 500) {
                Write-Host "Performance:     EXCELLENT (< 500ms)" -ForegroundColor Green
            } elseif ($avg -lt 1000) {
                Write-Host "Performance:     GOOD (< 1s)" -ForegroundColor Yellow
            } elseif ($avg -lt 2000) {
                Write-Host "Performance:     ACCEPTABLE (< 2s)" -ForegroundColor DarkYellow
            } else {
                Write-Host "Performance:     SLOW (> 2s)" -ForegroundColor Red
            }
            
            Write-Host ""
            
            # Create result object
            $result = @{
                Command = "uv run kpat_cli $CommandString"
                Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                Iterations = $Iterations
                WarmupRuns = $WarmupRuns
                Statistics = @{
                    Average = $avg
                    Median = $median
                    Min = $min
                    Max = $max
                    StdDev = $stdDev
                    SuccessfulRuns = $validTimings.Count
                    TotalRuns = $Iterations
                }
                DetailedResults = $allTimes
            }
            
            # Handle baseline comparison
            if ($CompareBaseline) {
                $baselinePath = Join-Path $ProjectRoot $BaselineFile
                
                if (Test-Path $baselinePath) {
                    # Load and compare with baseline
                    try {
                        $baseline = Get-Content $baselinePath | ConvertFrom-Json
                        $baselineAvg = $baseline.Statistics.Average
                        $improvement = [math]::Round((($baselineAvg - $avg) / $baselineAvg) * 100, 2)
                        
                        Write-Host "Baseline Comparison" -ForegroundColor Cyan
                        Write-Host "===================" -ForegroundColor Cyan
                        Write-Host "Baseline average:    $baselineAvg ms" -ForegroundColor White
                        Write-Host "Current average:     $avg ms" -ForegroundColor White
                        
                        if ($improvement -gt 0) {
                            Write-Host "Improvement:         +$improvement% [FASTER]" -ForegroundColor Green
                        } elseif ($improvement -lt 0) {
                            $regression = [math]::Abs($improvement)
                            Write-Host "Regression:          -$regression% [SLOWER]" -ForegroundColor Red
                        } else {
                            Write-Host "Change:              No change" -ForegroundColor Yellow
                        }
                        Write-Host ""
                        
                        # Add comparison to result
                        $result.BaselineComparison = @{
                            BaselineAverage = $baselineAvg
                            CurrentAverage = $avg
                            ImprovementPercent = $improvement
                            BaselineTimestamp = $baseline.Timestamp
                        }
                    }
                    catch {
                        Write-Warning "WARNING: Could not read baseline file: $_"
                    }
                } else {
                    # Save as new baseline
                    Write-Host "Saving baseline to: $BaselineFile" -ForegroundColor Cyan
                    $result | ConvertTo-Json -Depth 10 | Set-Content $baselinePath
                    Write-Host "Baseline saved successfully" -ForegroundColor Green
                    Write-Host ""
                }
            }
            
            # Save detailed results
            $resultFile = "benchmark-results-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
            $scriptsDir = Join-Path $ProjectRoot "scripts"
            $resultPath = Join-Path $scriptsDir $resultFile
            $result | ConvertTo-Json -Depth 10 | Set-Content $resultPath
            Write-Host "Detailed results saved to: scripts/$resultFile" -ForegroundColor Cyan
            
        } else {
            Write-Error "ERROR: No valid timing results collected"
            exit 1
        }
    } else {
        Write-Error "ERROR: No timing results collected"
        exit 1
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Benchmark completed successfully!" -ForegroundColor Green
