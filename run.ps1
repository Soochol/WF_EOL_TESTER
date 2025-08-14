# ========================================================================
# WF EOL Tester - PowerShell Launcher
# ========================================================================
# This PowerShell script provides enhanced execution capabilities for the
# EOL Tester on Windows systems with better error handling and logging.
# ========================================================================

param(
    [switch]$Debug,
    [switch]$Verbose,
    [switch]$Help
)

# Set error handling
$ErrorActionPreference = "Stop"

# Script information
$ScriptName = "WF EOL Tester PowerShell Launcher"
$Version = "1.0.0"

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    switch ($Type) {
        "ERROR" { 
            Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red 
        }
        "WARNING" { 
            Write-Host "[$timestamp] [WARNING] $Message" -ForegroundColor Yellow 
        }
        "SUCCESS" { 
            Write-Host "[$timestamp] [SUCCESS] $Message" -ForegroundColor Green 
        }
        "DEBUG" { 
            if ($Debug -or $Verbose) {
                Write-Host "[$timestamp] [DEBUG] $Message" -ForegroundColor Cyan 
            }
        }
        default { 
            Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor White 
        }
    }
}

function Show-Help {
    Write-Host @"
========================================================================
$ScriptName v$Version
========================================================================

USAGE:
    .\run.ps1 [options]

OPTIONS:
    -Debug      Run in debug mode with verbose logging
    -Verbose    Show detailed execution information
    -Help       Show this help message

EXAMPLES:
    .\run.ps1                 # Normal execution
    .\run.ps1 -Debug          # Debug mode
    .\run.ps1 -Verbose        # Verbose mode
    .\run.ps1 -Debug -Verbose # Debug + Verbose mode

DESCRIPTION:
    This script launches the WF EOL Tester application with proper
    environment setup and error handling. It automatically:
    
    - Uses uv for fast dependency management
    - Syncs project dependencies automatically
    - Sets up required environment variables
    - Provides colored console output
    - Handles errors gracefully
    - Shows execution summary

REQUIREMENTS:
    - Windows PowerShell 5.1+ or PowerShell Core 6.0+
    - uv package manager installed and in PATH
    - Project dependencies defined in pyproject.toml

========================================================================
"@
}

function Test-UvInstallation {
    try {
        $uvVersion = & uv --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "uv command failed"
        }
        
        Write-ColoredOutput "Found uv: $uvVersion" "SUCCESS"
        return $true
    }
    catch {
        Write-ColoredOutput "uv is not installed or not in PATH" "ERROR"
        Write-ColoredOutput "Please install uv from: https://docs.astral.sh/uv/getting-started/installation/" "ERROR"
        Write-ColoredOutput "Or install with pip: pip install uv" "ERROR"
        return $false
    }
}

function Initialize-UvEnvironment {
    Write-ColoredOutput "Initializing uv environment..." "DEBUG"
    
    try {
        Write-ColoredOutput "Syncing dependencies with uv..." "INFO"
        & uv sync --dev
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "Dependencies synced successfully" "SUCCESS"
            return $true
        } else {
            throw "uv sync failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-ColoredOutput "Failed to sync dependencies: $_" "ERROR"
        return $false
    }
}

function Test-MainPyFile {
    $mainPy = Join-Path $PWD "main.py"
    
    if (Test-Path $mainPy) {
        $fileInfo = Get-Item $mainPy
        Write-ColoredOutput "Found main.py (Size: $($fileInfo.Length) bytes, Modified: $($fileInfo.LastWriteTime))" "SUCCESS"
        return $true
    }
    else {
        Write-ColoredOutput "main.py not found in current directory" "ERROR"
        Write-ColoredOutput "Current directory: $PWD" "DEBUG"
        return $false
    }
}

function Set-EnvironmentVariables {
    Write-ColoredOutput "Setting up environment variables..." "DEBUG"
    
    if ($Debug) {
        $env:DEBUG_MODE = "1"
        $env:LOGLEVEL = "DEBUG"
        Write-ColoredOutput "Debug environment variables set" "DEBUG"
    }
    
    Write-ColoredOutput "Environment setup complete (using installed package)" "SUCCESS"
}

function Start-Application {
    try {
        Write-ColoredOutput "Starting WF EOL Tester application..." "SUCCESS"
        Write-ColoredOutput "Working directory: $PWD" "DEBUG"
        Write-ColoredOutput "Press Ctrl+C to stop the application" "INFO"
        
        Write-Host "`n========================================================================"
        Write-Host "WF EOL Tester Application Starting..." -ForegroundColor Green
        Write-Host "========================================================================`n"
        
        # Execute main.py with proper error handling using uv
        if ($Debug -or $Verbose) {
            & uv run python -u main.py
        } else {
            & uv run python main.py
        }
        
        $exitCode = $LASTEXITCODE
        
        Write-Host "`n========================================================================"
        if ($exitCode -eq 0) {
            Write-ColoredOutput "Application completed successfully" "SUCCESS"
        } else {
            Write-ColoredOutput "Application exited with code: $exitCode" "ERROR"
        }
        Write-Host "========================================================================`n"
        
        return $exitCode
    }
    catch {
        Write-ColoredOutput "Failed to start application: $_" "ERROR"
        return 1
    }
}

function Main {
    # Show help if requested
    if ($Help) {
        Show-Help
        return 0
    }
    
    # Set console title
    $Host.UI.RawUI.WindowTitle = "WF EOL Tester"
    if ($Debug) {
        $Host.UI.RawUI.WindowTitle += " - DEBUG MODE"
    }
    
    # Display header
    Write-Host "========================================================================" -ForegroundColor Green
    Write-Host "$ScriptName v$Version" -ForegroundColor Green
    Write-Host "========================================================================" -ForegroundColor Green
    
    if ($Debug) {
        Write-ColoredOutput "Running in DEBUG mode" "DEBUG"
    }
    if ($Verbose) {
        Write-ColoredOutput "Verbose output enabled" "DEBUG"
    }
    
    Write-Host ""
    
    try {
        # Change to script directory
        $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
        if ($scriptDir) {
            Set-Location $scriptDir
            Write-ColoredOutput "Changed to script directory: $scriptDir" "DEBUG"
        }
        
        # Perform pre-flight checks
        Write-ColoredOutput "Performing pre-flight checks..." "INFO"
        
        if (-not (Test-UvInstallation)) {
            return 1
        }
        
        if (-not (Test-MainPyFile)) {
            return 1
        }
        
        # Initialize uv environment
        if (-not (Initialize-UvEnvironment)) {
            return 1
        }
        
        # Set environment variables
        Set-EnvironmentVariables
        
        # Run the application
        $exitCode = Start-Application
        
        return $exitCode
    }
    catch {
        Write-ColoredOutput "Unexpected error occurred: $_" "ERROR"
        Write-ColoredOutput "Stack trace:" "DEBUG"
        Write-ColoredOutput $_.ScriptStackTrace "DEBUG"
        return 1
    }
    finally {
        Write-ColoredOutput "PowerShell launcher session complete" "INFO"
    }
}

# Execute main function and handle exit
try {
    $exitCode = Main
    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit $exitCode
}
catch {
    Write-Host "Critical error in PowerShell launcher: $_" -ForegroundColor Red
    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}