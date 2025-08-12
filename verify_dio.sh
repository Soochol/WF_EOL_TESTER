#!/usr/bin/env bash

# DIO Monitoring Service Verification Script
# This script helps verify that the DIOMonitoringService button callback flow works correctly
# Compatible with WSL2, Linux, Windows (Git Bash), and other Unix-like systems

echo "🔍 DIO Monitoring Service Verification Tool"
echo "=========================================="

# Detect platform for better compatibility
PLATFORM="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="windows"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
fi

echo "🖥️  Platform detected: $PLATFORM"

# Check for Python executable with cross-platform support
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.x"
    exit 1
fi

echo "🐍 Python command: $PYTHON_CMD"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    # Cross-platform virtual environment activation
    if [[ "$PLATFORM" == "windows" ]]; then
        # Windows Git Bash/MSYS2
        if [ -f "venv/Scripts/activate" ]; then
            # shellcheck source=/dev/null
            source venv/Scripts/activate
        elif [ -f "venv/bin/activate" ]; then
            # shellcheck source=/dev/null
            source venv/bin/activate
        fi
    else
        # Linux/macOS/WSL
        # shellcheck source=/dev/null
        source venv/bin/activate
    fi
else
    echo "⚠️  Virtual environment not found, using system Python"
fi

# Check if tools directory exists
if [ ! -d "tools" ]; then
    echo "❌ Tools directory not found"
    exit 11
fi

# Check if verification tool exists
if [ ! -f "tools/dio_verification_tool.py" ]; then
    echo "❌ DIO verification tool not found"
    exit 1
fi

# Parse command line arguments
COMMAND=${1:-"test"}
DURATION=${2:-"60"}

echo "🚀 Starting DIO verification..."
echo "   Command: $COMMAND"
if [ "$COMMAND" = "monitor" ]; then
    echo "   Duration: $DURATION seconds"
fi
echo ""

# Set PYTHONPATH to include src directory with cross-platform compatibility
CURRENT_DIR="$(pwd)"
if [[ "$PLATFORM" == "windows" ]]; then
    # Windows paths for Python (use forward slashes)
    export PYTHONPATH="${PYTHONPATH};${CURRENT_DIR}/src"
else
    # Unix-like systems
    export PYTHONPATH="${PYTHONPATH}:${CURRENT_DIR}/src"
fi

# Diagnostic information
echo "🔧 Environment diagnostics:"
echo "   Working directory: $CURRENT_DIR"
echo "   PYTHONPATH: $PYTHONPATH"

# Verify Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "   Python version: $PYTHON_VERSION"

# Check if required modules can be imported
echo "🔍 Checking Python dependencies..."
if ! $PYTHON_CMD -c "import asyncio; import yaml; import loguru" >/dev/null 2>&1; then
    echo "⚠️  Some Python dependencies may be missing. The script will still attempt to run."
    echo "   If you encounter import errors, please install dependencies with:"
    echo "   pip install -r requirements.txt"
else
    echo "✅ Core Python dependencies available"
fi

# Run the verification tool with cross-platform Python command and error handling
case $COMMAND in
    "test")
        echo "🧪 Running verification tests..."
        if $PYTHON_CMD tools/dio_verification_tool.py test; then
            echo ""
            echo "✅ DIO verification tests completed successfully"
        else
            EXIT_CODE=$?
            echo ""
            echo "❌ DIO verification tests failed with exit code: $EXIT_CODE"
            echo "💡 Troubleshooting suggestions:"
            echo "   1. Check that all configuration files exist in the configuration/ directory"
            echo "   2. Verify Python dependencies are installed: pip install -r requirements.txt"
            echo "   3. Ensure you're running from the project root directory"
            echo "   4. Try running directly: $PYTHON_CMD tools/dio_verification_tool.py test"
            exit $EXIT_CODE
        fi
        ;;
    "monitor")
        echo "👀 Running continuous monitoring for $DURATION seconds..."
        if $PYTHON_CMD tools/dio_verification_tool.py monitor "$DURATION"; then
            echo ""
            echo "✅ DIO monitoring completed successfully"
        else
            EXIT_CODE=$?
            echo ""
            echo "❌ DIO monitoring failed with exit code: $EXIT_CODE"
            echo "💡 Troubleshooting suggestions:"
            echo "   1. Check that all configuration files exist in the configuration/ directory"
            echo "   2. Verify Python dependencies are installed: pip install -r requirements.txt"
            echo "   3. Ensure you're running from the project root directory"
            echo "   4. Try running directly: $PYTHON_CMD tools/dio_verification_tool.py monitor $DURATION"
            exit $EXIT_CODE
        fi
        ;;
    "help")
        echo "Usage: ./verify_dio.sh [test|monitor|help] [duration]"
        echo ""
        echo "Commands:"
        echo "  test     - Run comprehensive verification tests (default)"
        echo "  monitor  - Run continuous monitoring for specified duration"
        echo "  help     - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./verify_dio.sh test                  # Run verification tests"
        echo "  ./verify_dio.sh monitor 120           # Monitor for 2 minutes"
        echo ""
        echo "Cross-platform compatibility:"
        echo "  ✅ WSL2 (Windows Subsystem for Linux)"
        echo "  ✅ Linux (Ubuntu, CentOS, etc.)"
        echo "  ✅ macOS"
        echo "  ✅ Windows (Git Bash, MSYS2)"
        echo ""
        echo "Requirements:"
        echo "  - Python 3.x"
        echo "  - Required packages: pip install -r requirements.txt"
        echo "  - Configuration files in configuration/ directory"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "Use './verify_dio.sh help' for usage information"
        exit 1
        ;;
esac

