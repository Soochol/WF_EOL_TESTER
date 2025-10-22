"""
Clean Empty Test Results Script

Deletes JSON test result files that have no measurement data.
A test result is considered empty if:
- measurement_ids field is empty ([])
- OR status is 'error' or 'cancelled'
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from loguru import logger


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON file and return dictionary

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary containing JSON data
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return {}


def is_empty_test_result(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if test result has no measurement data

    Args:
        data: Test result dictionary

    Returns:
        Tuple of (is_empty, reason)
    """
    # Check measurement_ids field
    measurement_ids = data.get("measurement_ids", [])
    if not measurement_ids or len(measurement_ids) == 0:
        return True, "No measurement_ids"

    # Check status
    status = data.get("status", "").lower()
    if status in ("error", "cancelled"):
        return True, f"Status is {status}"

    return False, "Has measurements"


def clean_empty_test_results(
    test_results_dir: str = "logs/test_results/json", dry_run: bool = False
) -> None:
    """
    Delete test result files with no measurement data

    Args:
        test_results_dir: Directory containing test result JSON files
        dry_run: If True, only show what would be deleted without actually deleting
    """
    results_path = Path(test_results_dir)

    if not results_path.exists():
        logger.error(f"Directory not found: {results_path}")
        return

    # Find all JSON files
    json_files = list(results_path.glob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files in {results_path}")

    empty_files: List[Tuple[Path, str]] = []
    valid_files: List[Path] = []

    # Check each file
    for json_file in json_files:
        data = load_json_file(json_file)
        if not data:
            logger.warning(f"Skipping invalid file: {json_file}")
            continue

        is_empty, reason = is_empty_test_result(data)
        if is_empty:
            empty_files.append((json_file, reason))
        else:
            valid_files.append(json_file)

    # Report findings
    logger.info(f"\n{'='*60}")
    logger.info(f"Scan Results:")
    logger.info(f"  Total files: {len(json_files)}")
    logger.info(f"  Valid files (with measurements): {len(valid_files)}")
    logger.info(f"  Empty files (no measurements): {len(empty_files)}")
    logger.info(f"{'='*60}\n")

    if not empty_files:
        logger.info("No empty test result files found. Nothing to delete.")
        return

    # Show files to be deleted
    logger.info("Empty test result files:")
    for file_path, reason in empty_files:
        logger.info(f"  - {file_path.name} ({reason})")

    if dry_run:
        logger.warning(f"\n[DRY RUN] Would delete {len(empty_files)} files")
        logger.warning("Run with --delete flag to actually delete files")
        return

    # Delete files
    deleted_count = 0
    failed_count = 0

    logger.info(f"\nDeleting {len(empty_files)} empty test result files...")
    for file_path, reason in empty_files:
        try:
            file_path.unlink()
            deleted_count += 1
            logger.debug(f"Deleted: {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to delete {file_path.name}: {e}")
            failed_count += 1

    # Final report
    logger.info(f"\n{'='*60}")
    logger.success(f"Cleanup completed!")
    logger.info(f"  Deleted: {deleted_count} files")
    if failed_count > 0:
        logger.warning(f"  Failed: {failed_count} files")
    logger.info(f"  Remaining valid files: {len(valid_files)}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean empty test result files (no measurement data)"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="logs/test_results/json",
        help="Directory containing test result JSON files (default: logs/test_results/json)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete files (default is dry-run mode)",
    )

    args = parser.parse_args()

    # Configure logger
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>\n",
        colorize=True,
    )

    # Run cleanup
    dry_run = not args.delete
    if dry_run:
        logger.info("Running in DRY RUN mode (no files will be deleted)")
        logger.info("Use --delete flag to actually delete files\n")

    clean_empty_test_results(test_results_dir=args.dir, dry_run=dry_run)
