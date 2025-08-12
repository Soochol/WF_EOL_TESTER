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
    
    - Detects and activates Python virtual environment
    - Sets up required environment variables
    - Provides colored console output
    - Handles errors gracefully
    - Shows execution summary

REQUIREMENTS:
    - Windows PowerShell 5.1+ or PowerShell Core 6.0+
    - Python 3.8+ installed and in PATH
    - Virtual environment set up (run setup_windows.bat first)

========================================================================
"@
}

function Test-PythonInstallation {
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python command failed"
        }
        
        Write-ColoredOutput "Found Python: $pythonVersion" "SUCCESS"
        
        # Extract version numbers
        $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)"
        if ($versionMatch) {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                throw "Python version $major.$minor is too old. Please install Python 3.8 or newer."
            }
        }
        
        return $true
    }
    catch {
        Write-ColoredOutput "Python is not installed or not in PATH" "ERROR"
        Write-ColoredOutput "Please install Python 3.8+ from: https://www.python.org/downloads/" "ERROR"
        return $false
    }
}

function Test-VirtualEnvironment {
    $venvPath = Join-Path $PWD "venv"
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    Write-ColoredOutput "Checking for virtual environment..." "DEBUG"
    
    if (Test-Path $activateScript) {
        Write-ColoredOutput "Found virtual environment at: $venvPath" "SUCCESS"
        
        try {
            # Activate virtual environment
            Write-ColoredOutput "Activating virtual environment..." "DEBUG"
            & $activateScript
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColoredOutput "Virtual environment activated successfully" "SUCCESS"
                return $true
            } else {
                throw "Activation script failed with exit code $LASTEXITCODE"
            }
        }
        catch {
            Write-ColoredOutput "Failed to activate virtual environment: $_" "WARNING"
            Write-ColoredOutput "Continuing with system Python..." "WARNING"
            return $false
        }
    }
    else {
        Write-ColoredOutput "Virtual environment not found" "WARNING"
        Write-ColoredOutput "Expected location: $activateScript" "DEBUG"
        Write-ColoredOutput "Consider running setup_windows.bat first" "WARNING"
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
        
        # Execute main.py with proper error handling
        if ($Debug -or $Verbose) {
            & python -u main.py
        } else {
            & python main.py
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
        
        if (-not (Test-PythonInstallation)) {
            return 1
        }
        
        if (-not (Test-MainPyFile)) {
            return 1
        }
        
        # Try to set up virtual environment (non-critical)
        Test-VirtualEnvironment | Out-Null
        
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