"""
EOL Force Test Sequence - CLI Entry Point

Usage:
    python -m sequences.eol_tester --start --config config.json
    python -m sequences.eol_tester --start --dry-run
    python -m sequences.eol_tester --stop
"""

import asyncio
import sys
import traceback

print("[DEBUG] main.py: Starting...", file=sys.stderr, flush=True)

# Fix for Windows asyncio compatibility
# ProactorEventLoop doesn't support certain operations required by the sequence
if sys.platform == "win32":
    print("[DEBUG] main.py: Setting WindowsSelectorEventLoopPolicy", file=sys.stderr, flush=True)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print("[DEBUG] main.py: Importing EOLForceTestSequence...", file=sys.stderr, flush=True)
try:
    from .sequence import EOLForceTestSequence
    print("[DEBUG] main.py: Import successful", file=sys.stderr, flush=True)
except Exception as e:
    print(f"[DEBUG] main.py: Import failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    traceback.print_exc(file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    print("[DEBUG] main.py: Calling run_from_cli()", file=sys.stderr, flush=True)
    try:
        result = EOLForceTestSequence.run_from_cli()
        print(f"[DEBUG] main.py: run_from_cli() returned {result}", file=sys.stderr, flush=True)
        exit(result)
    except Exception as e:
        print(f"[DEBUG] main.py: run_from_cli() failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        exit(2)
