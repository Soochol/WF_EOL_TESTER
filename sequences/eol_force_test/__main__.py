"""
EOL Force Test Sequence - Module Entry Point

Usage:
    python -m eol_tester --start
    python -m eol_tester --help
"""

from .sequence import EOLForceTestSequence

if __name__ == "__main__":
    exit(EOLForceTestSequence.run_from_cli())
