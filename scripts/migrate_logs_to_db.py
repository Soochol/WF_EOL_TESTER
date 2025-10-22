"""
Log Files to Database Migration Script

Migrates existing JSON and CSV log files to the SQLite database.

Usage:
    python scripts/migrate_logs_to_db.py                 # Migrate all files
    python scripts/migrate_logs_to_db.py --dry-run       # Preview without saving
    python scripts/migrate_logs_to_db.py --json-only     # Only JSON files
    python scripts/migrate_logs_to_db.py --csv-only      # Only CSV files
"""

# Standard library imports
import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Third-party imports
from loguru import logger

# Local application imports
from infrastructure.database.db_manager import DatabaseManager
from infrastructure.implementation.repositories.sqlite_log_repository import (
    SqliteLogRepository,
)
from infrastructure.parsers.csv_log_parser import CsvLogParser
from infrastructure.parsers.json_log_parser import JsonLogParser


class LogMigrator:
    """Migrates log files to database"""

    def __init__(self, db_manager: DatabaseManager, dry_run: bool = False):
        """
        Initialize migrator

        Args:
            db_manager: Database manager instance
            dry_run: If True, don't actually save to database
        """
        self.db_manager = db_manager
        self.dry_run = dry_run
        self.repository = SqliteLogRepository(db_manager)

        # Statistics
        self.stats = {
            "json_files_found": 0,
            "json_files_parsed": 0,
            "json_files_imported": 0,
            "json_files_skipped": 0,
            "json_files_failed": 0,
            "csv_files_found": 0,
            "csv_files_parsed": 0,
            "csv_measurements_imported": 0,
            "csv_files_failed": 0,
        }

    async def migrate_all(
        self, json_dir: Path, csv_dir: Path, json_only: bool = False, csv_only: bool = False
    ) -> None:
        """
        Migrate all log files

        Args:
            json_dir: Directory containing JSON files
            csv_dir: Directory containing CSV files
            json_only: Only migrate JSON files
            csv_only: Only migrate CSV files
        """
        logger.info("=" * 80)
        logger.info("Log Files to Database Migration")
        logger.info("=" * 80)

        if self.dry_run:
            logger.warning("DRY-RUN MODE: No data will be saved to database")

        # Migrate JSON files
        if not csv_only:
            await self._migrate_json_files(json_dir)

        # Migrate CSV files
        if not json_only:
            await self._migrate_csv_files(csv_dir)

        # Print final statistics
        self._print_statistics()

    async def _migrate_json_files(self, json_dir: Path) -> None:
        """Migrate JSON test result files"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("Migrating JSON Test Results")
        logger.info("=" * 80)

        json_files = JsonLogParser.scan_directory(json_dir)
        self.stats["json_files_found"] = len(json_files)

        if not json_files:
            logger.warning("No JSON files found")
            return

        for idx, json_file in enumerate(json_files, 1):
            logger.info(f"[{idx}/{len(json_files)}] Processing: {json_file.name}")

            # Parse file
            test_data = JsonLogParser.parse_file(json_file)
            if not test_data:
                logger.error(f"  ✗ Failed to parse")
                self.stats["json_files_failed"] += 1
                continue

            self.stats["json_files_parsed"] += 1

            # Check if already exists
            test_id = test_data["test_id"]
            if not self.dry_run:
                existing = await self.repository.get_test_by_id(test_id)
                if existing:
                    logger.info(f"  → Skipped (already in database)")
                    self.stats["json_files_skipped"] += 1
                    continue

            # Import to database
            if not self.dry_run:
                try:
                    await self.repository.save_test_result(test_data)
                    logger.info(f"  ✓ Imported test_id={test_id}")
                    self.stats["json_files_imported"] += 1
                except Exception as e:
                    logger.error(f"  ✗ Failed to import: {e}")
                    self.stats["json_files_failed"] += 1
            else:
                logger.info(f"  ⚠ Would import test_id={test_id} (DRY-RUN)")
                self.stats["json_files_imported"] += 1

    async def _migrate_csv_files(self, csv_dir: Path) -> None:
        """Migrate CSV raw measurement files"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("Migrating CSV Raw Measurements")
        logger.info("=" * 80)

        csv_files = CsvLogParser.scan_directory(csv_dir)
        self.stats["csv_files_found"] = len(csv_files)

        if not csv_files:
            logger.warning("No CSV files found")
            return

        for idx, csv_file in enumerate(csv_files, 1):
            logger.info(f"[{idx}/{len(csv_files)}] Processing: {csv_file.name}")

            # Parse file
            csv_data = CsvLogParser.parse_file(csv_file)
            if not csv_data:
                logger.error(f"  ✗ Failed to parse")
                self.stats["csv_files_failed"] += 1
                continue

            self.stats["csv_files_parsed"] += 1
            measurements = csv_data["measurements"]

            # Import measurements
            if not self.dry_run:
                imported_count = 0
                for measurement in measurements:
                    try:
                        await self.repository.save_raw_measurement(**measurement)
                        imported_count += 1
                    except Exception as e:
                        logger.debug(f"  Failed to import measurement: {e}")

                logger.info(f"  ✓ Imported {imported_count}/{len(measurements)} measurements")
                self.stats["csv_measurements_imported"] += imported_count
            else:
                logger.info(
                    f"  ⚠ Would import {len(measurements)} measurements (DRY-RUN)"
                )
                self.stats["csv_measurements_imported"] += len(measurements)

    def _print_statistics(self) -> None:
        """Print migration statistics"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("Migration Statistics")
        logger.info("=" * 80)

        logger.info("")
        logger.info("JSON Test Results:")
        logger.info(f"  Files found:    {self.stats['json_files_found']}")
        logger.info(f"  Files parsed:   {self.stats['json_files_parsed']}")
        logger.info(f"  Files imported: {self.stats['json_files_imported']}")
        logger.info(f"  Files skipped:  {self.stats['json_files_skipped']}")
        logger.info(f"  Files failed:   {self.stats['json_files_failed']}")

        logger.info("")
        logger.info("CSV Raw Measurements:")
        logger.info(f"  Files found:         {self.stats['csv_files_found']}")
        logger.info(f"  Files parsed:        {self.stats['csv_files_parsed']}")
        logger.info(f"  Measurements imported: {self.stats['csv_measurements_imported']}")
        logger.info(f"  Files failed:        {self.stats['csv_files_failed']}")

        logger.info("")
        logger.info("=" * 80)


async def clear_database(db_manager: DatabaseManager) -> None:
    """
    Clear all data from database tables

    Args:
        db_manager: Database manager instance
    """
    from sqlalchemy import text

    logger.warning("Clearing all data from database tables...")

    async with db_manager.get_session() as session:
        # Delete in correct order (measurements first due to foreign key)
        await session.execute(text("DELETE FROM raw_measurements"))
        await session.execute(text("DELETE FROM test_results"))
        await session.commit()

    logger.success("Database cleared: all test results and measurements deleted")


async def main() -> None:
    """Main migration entry point"""
    parser = argparse.ArgumentParser(description="Migrate log files to database")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    parser.add_argument("--json-only", action="store_true", help="Only migrate JSON files")
    parser.add_argument("--csv-only", action="store_true", help="Only migrate CSV files")
    parser.add_argument(
        "--db",
        type=str,
        default="database/test_data.db",
        help="Database path (default: database/test_data.db)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before migration",
    )
    args = parser.parse_args()

    # Setup paths
    project_root = Path(__file__).parent.parent
    json_dir = project_root / "logs" / "test_results" / "json"
    csv_dir = project_root / "logs" / "EOL Force Test" / "raw_data"

    # Database path: support both absolute and relative paths
    if Path(args.db).is_absolute():
        db_path = Path(args.db)
    else:
        db_path = project_root / args.db

    logger.info(f"JSON directory: {json_dir}")
    logger.info(f"CSV directory:  {csv_dir}")
    logger.info(f"Database:       {db_path}")
    logger.info("")

    # Initialize database
    db_manager = DatabaseManager(str(db_path))
    await db_manager.initialize()

    # Clear database if requested
    if args.clear and not args.dry_run:
        await clear_database(db_manager)
        logger.info("")

    # Run migration
    migrator = LogMigrator(db_manager, dry_run=args.dry_run)
    await migrator.migrate_all(
        json_dir=json_dir,
        csv_dir=csv_dir,
        json_only=args.json_only,
        csv_only=args.csv_only,
    )

    # Close database
    await db_manager.close()

    logger.info("")
    if args.dry_run:
        logger.warning("DRY-RUN completed. No data was saved to database.")
    else:
        logger.info("Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
