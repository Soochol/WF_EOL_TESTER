#!/usr/bin/env python3
"""
Clean Python cache files that might be causing import issues on Windows
"""

import shutil
from pathlib import Path

def clean_python_cache(directory):
    """Remove all __pycache__ directories and .pyc files"""
    directory = Path(directory)
    removed_count = 0
    
    print(f"Cleaning Python cache files in {directory}")
    
    # Remove __pycache__ directories
    for pycache_dir in directory.rglob("__pycache__"):
        if pycache_dir.is_dir():
            print(f"Removing: {pycache_dir}")
            shutil.rmtree(pycache_dir, ignore_errors=True)
            removed_count += 1
    
    # Remove .pyc files
    for pyc_file in directory.rglob("*.pyc"):
        if pyc_file.is_file():
            print(f"Removing: {pyc_file}")
            pyc_file.unlink(missing_ok=True)
            removed_count += 1
            
    print(f"Removed {removed_count} cache files/directories")
    return removed_count

if __name__ == "__main__":
    current_dir = Path(__file__).parent
    clean_python_cache(current_dir)
    print("✅ Cache cleanup complete!")