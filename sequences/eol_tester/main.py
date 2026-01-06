"""
EOL Force Test Sequence - CLI Entry Point

Usage:
    python -m sequences.eol_tester --start --config config.json
    python -m sequences.eol_tester --start --dry-run
    python -m sequences.eol_tester --stop
"""

from .sequence import EOLForceTestSequence

if __name__ == "__main__":
    exit(EOLForceTestSequence.run_from_cli())
