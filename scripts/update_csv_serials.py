"""
Update CSV Serial Numbers from Filename

Extracts serial numbers (starting with A10) from CSV filenames
and updates the Serial column in the CSV files.
"""

import csv
import re
from pathlib import Path
from typing import List, Optional
from loguru import logger


# Serial number pattern (starts with A10)
SERIAL_PATTERN = re.compile(r'A10[A-Z0-9]+')


def extract_serial_from_filename(filename: str) -> Optional[str]:
    """
    Extract serial number from filename

    Args:
        filename: CSV filename (e.g., "#13_A10ML4S0H1A00C100005.csv")

    Returns:
        Serial number (e.g., "A10ML4S0H1A00C100005") or None
    """
    match = SERIAL_PATTERN.search(filename)
    return match.group() if match else None


def update_csv_serial(csv_path: Path, new_serial: str, dry_run: bool = False) -> bool:
    """
    Update Serial column in CSV file

    Args:
        csv_path: Path to CSV file
        new_serial: New serial number to set
        dry_run: If True, only show what would be changed

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        if len(rows) < 2:
            logger.warning(f"Skipping {csv_path.name}: No data rows")
            return False

        # Check header
        header = rows[0]
        if len(header) < 3 or header[2].lower() != 'serial':
            logger.warning(f"Skipping {csv_path.name}: Serial column not found at index 2")
            return False

        # Count changes
        old_serials = set()
        changed_rows = 0

        # Update Serial column (index 2) for all data rows
        for i in range(1, len(rows)):
            if len(rows[i]) > 2:
                old_serials.add(rows[i][2])
                if rows[i][2] != new_serial:
                    rows[i][2] = new_serial
                    changed_rows += 1

        if dry_run:
            logger.info(
                f"[DRY RUN] {csv_path.name}: "
                f"Would change {changed_rows} rows "
                f"(old: {', '.join(old_serials)} → new: {new_serial})"
            )
            return True

        # Write updated CSV
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        logger.success(
            f"Updated {csv_path.name}: "
            f"{changed_rows} rows changed "
            f"(old: {', '.join(old_serials)} → new: {new_serial})"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to update {csv_path.name}: {e}")
        return False


def process_csv_files(
    csv_dir: str = "logs/EOL Force Test/raw_data",
    pattern: str = "#*_A10*.csv",
    dry_run: bool = False
) -> None:
    """
    Process all CSV files matching pattern

    Args:
        csv_dir: Directory containing CSV files
        pattern: Glob pattern to match files
        dry_run: If True, only show what would be changed
    """
    csv_path = Path(csv_dir)

    if not csv_path.exists():
        logger.error(f"Directory not found: {csv_path}")
        return

    # Find matching CSV files
    csv_files = list(csv_path.glob(pattern))
    logger.info(f"Found {len(csv_files)} CSV files matching pattern '{pattern}'")

    if not csv_files:
        logger.warning("No files to process")
        return

    # Process each file
    success_count = 0
    failed_count = 0
    skipped_count = 0

    for csv_file in sorted(csv_files):
        logger.info(f"\nProcessing: {csv_file.name}")

        # Extract serial from filename
        serial = extract_serial_from_filename(csv_file.name)
        if not serial:
            logger.warning(f"Skipping {csv_file.name}: No serial number found in filename")
            skipped_count += 1
            continue

        logger.info(f"  Extracted serial: {serial}")

        # Update CSV file
        if update_csv_serial(csv_file, serial, dry_run):
            success_count += 1
        else:
            failed_count += 1

    # Summary
    logger.info(f"\n{'='*60}")
    if dry_run:
        logger.info("DRY RUN SUMMARY:")
    else:
        logger.success("UPDATE SUMMARY:")
    logger.info(f"  Total files: {len(csv_files)}")
    logger.info(f"  Successful: {success_count}")
    if failed_count > 0:
        logger.warning(f"  Failed: {failed_count}")
    if skipped_count > 0:
        logger.warning(f"  Skipped: {skipped_count}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Update CSV Serial numbers from filenames"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="logs/EOL Force Test/raw_data",
        help="Directory containing CSV files",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="#*_A10*.csv",
        help="Glob pattern to match files (default: #*_A10*.csv)",
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

    process_csv_files(csv_dir=args.dir, pattern=args.pattern, dry_run=dry_run)
