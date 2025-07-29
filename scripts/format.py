#!/usr/bin/env python3
"""
Professional Code Formatting Script

Runs all code quality tools in the correct order for enterprise-grade formatting.
"""

import subprocess
import sys


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False


def main():
    """Run all formatting and quality checks."""
    print("🚀 Starting professional code formatting...\n")

    
    commands = [
        (["black", "."], "Black code formatting"),
        (["isort", "."], "Import organization with isort"),
        (["pylint", "main.py", "src/"], "Pylint static analysis"),
    ]
    
    success_count = 0
    total_commands = len(commands)
    
    for cmd, description in commands:
        if run_command(cmd, description):
            success_count += 1
        print()  # Empty line for readability
    
    # Summary
    print("=" * 60)
    print(f"📊 Summary: {success_count}/{total_commands} tools completed successfully")
    
    if success_count == total_commands:
        print("🎉 All formatting and quality checks passed!")
        print("💡 Your code is now enterprise-ready!")
        return 0
    
    print("⚠️  Some tools reported issues. Please review and fix.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
