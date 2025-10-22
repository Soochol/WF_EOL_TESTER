"""
Update JSON Serial Numbers from Filename

Extracts serial numbers (starting with A10) from JSON filenames
and updates the serial_number field in the JSON files.
"""

import json
import re
from pathlib import Path
from typing import Optional
from loguru import logger


# Serial number pattern (starts with A10)
SERIAL_PATTERN = re.compile(r'A10[A-Z0-9]+')


def extract_serial_from_filename(filename: str) -> Optional[str]:
    """
    Extract serial number from filename

    Args:
        filename: JSON filename (e.g., "#13_A10ML4S0H1A00C100005.json")

    Returns:
        Serial number (e.g., "A10ML4S0H1A00C100005") or None
    """
    match = SERIAL_PATTERN.search(filename)
    return match.group() if match else None


def update_json_serial(json_path: Path, new_serial: str, dry_run: bool = False) -> bool:
    """
    Update serial_number field in JSON file

    Args:
        json_path: Path to JSON file
        new_serial: New serial number to set
        dry_run: If True, only show what would be changed

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Find serial_number field in dut section
        if 'dut' not in data:
            logger.warning(f"Skipping {json_path.name}: 'dut' section not found")
            return False

        if 'serial_number' not in data['dut']:
            logger.warning(f"Skipping {json_path.name}: 'serial_number' field not found")
            return False

        old_serial = data['dut']['serial_number']

        if old_serial == new_serial:
            logger.info(f"{json_path.name}: Already has correct serial ({new_serial})")
            return True

        if dry_run:
            logger.info(
                f"[DRY RUN] {json_path.name}: "
                f"Would change serial_number: {old_serial} → {new_serial}"
            )
            return True

        # Update serial_number
        data['dut']['serial_number'] = new_serial

        # Also update dut_id to match serial
        data['dut']['dut_id'] = f"DUT_{new_serial}"

        # Write updated JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.success(
            f"Updated {json_path.name}: "
            f"serial_number: {old_serial} → {new_serial}"
        )
        return True

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {json_path.name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to update {json_path.name}: {e}")
        return False


def process_json_files(
    json_dir: str = "logs/test_results/json",
    pattern: str = "#*_A10*.json",
    dry_run: bool = False
) -> None:
    """
    Process all JSON files matching pattern

    Args:
        json_dir: Directory containing JSON files
        pattern: Glob pattern to match files
        dry_run: If True, only show what would be changed
    """
    json_path = Path(json_dir)

    if not json_path.exists():
        logger.error(f"Directory not found: {json_path}")
        return

    # Find matching JSON files
    json_files = list(json_path.glob(pattern))
    logger.info(f"Found {len(json_files)} JSON files matching pattern '{pattern}'")

    if not json_files:
        logger.warning("No files to process")
        return

    # Process each file
    success_count = 0
    failed_count = 0
    skipped_count = 0

    for json_file in sorted(json_files):
        logger.info(f"\nProcessing: {json_file.name}")

        # Extract serial from filename
        serial = extract_serial_from_filename(json_file.name)
        if not serial:
            logger.warning(f"Skipping {json_file.name}: No serial number found in filename")
            skipped_count += 1
            continue

        logger.info(f"  Extracted serial: {serial}")

        # Update JSON file
        if update_json_serial(json_file, serial, dry_run):
            success_count += 1
        else:
            failed_count += 1

    # Summary
    logger.info(f"\n{'='*60}")
    if dry_run:
        logger.info("DRY RUN SUMMARY:")
    else:
        logger.success("UPDATE SUMMARY:")
    logger.info(f"  Total files: {len(json_files)}")
    logger.info(f"  Successful: {success_count}")
    if failed_count > 0:
        logger.warning(f"  Failed: {failed_count}")
    if skipped_count > 0:
        logger.warning(f"  Skipped: {skipped_count}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Update JSON Serial numbers from filenames"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="logs/test_results/json",
        help="Directory containing JSON files",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="#*_A10*.json",
        help="Glob pattern to match files (default: #*_A10*.json)",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Actually update files (default is dry-run mode)",
    )

    args = parser.parse_args()

    # Configure logger
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>\n",
        colorize=True,
    )

    # Run update
    dry_run = not args.update
    if dry_run:
        logger.info("Running in DRY RUN mode (no files will be modified)")
        logger.info("Use --update flag to actually update files\n")

    process_json_files(json_dir=args.dir, pattern=args.pattern, dry_run=dry_run)
