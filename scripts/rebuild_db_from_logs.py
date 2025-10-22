"""
Rebuild Database from Log Files

This script rebuilds the database from existing JSON and CSV log files,
ensuring proper Foreign Key relationships between test_results and raw_measurements.

Process:
1. Clear existing database
2. Match JSON files (test_results) with CSV files (raw_data) by prefix
3. Extract test_id from JSON
4. Parse CSV pivot table and convert to individual measurements
5. Save to database with proper Foreign Key relationships
"""

import asyncio
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.database.db_manager import DatabaseManager
from infrastructure.database.schema import RawMeasurement, TestResult


class LogFileParser:
    """Parser for JSON and CSV log files"""

    def __init__(self, json_dir: str, csv_dir: str):
        self.json_dir = Path(json_dir)
        self.csv_dir = Path(csv_dir)

    def find_file_pairs(self) -> List[Tuple[Path, Path]]:
        """
        Find matching JSON and CSV files by prefix

        Returns:
            List of (json_path, csv_path) tuples
        """
        json_files = list(self.json_dir.glob("*.json"))
        csv_files = list(self.csv_dir.glob("*.csv"))

        pairs = []

        # Match files by prefix (#13, #14, etc.)
        for json_file in json_files:
            # Extract prefix (e.g., "#13" from "#13_A10ML4S0H1A00C100005.json")
            match = re.match(r"(#\d+)_", json_file.name)
            if not match:
                print(f"[SKIP] No prefix found in JSON file: {json_file.name}")
                continue

            prefix = match.group(1)

            # Find matching CSV file
            matching_csv = None
            for csv_file in csv_files:
                if csv_file.name.startswith(prefix + "_"):
                    matching_csv = csv_file
                    break

            if matching_csv:
                pairs.append((json_file, matching_csv))
                print(f"[MATCH] {prefix}: {json_file.name} <-> {csv_file.name}")
            else:
                print(f"[SKIP] No matching CSV for JSON: {json_file.name}")

        print(f"\n[INFO] Found {len(pairs)} matching file pairs")
        return pairs

    def parse_json(self, json_path: Path) -> Optional[Dict]:
        """Parse JSON file and extract test_results data"""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract required fields
            test_data = {
                "test_id": data.get("test_id"),
                "dut_id": data.get("dut", {}).get("dut_id"),
                "serial_number": data.get("dut", {}).get("serial_number"),
                "operator_id": data.get("operator_id", "UNKNOWN"),
                "status": data.get("status", "unknown"),
                "created_at": self._parse_datetime(data.get("created_at")),
                "start_time": self._parse_datetime(data.get("start_time")),
                "end_time": self._parse_datetime(data.get("end_time")),
                "duration_seconds": data.get("duration_seconds"),
                "error_message": data.get("error_message"),
                "test_configuration": data.get("test_configuration"),
            }

            # Validation
            if not test_data["test_id"]:
                print(f"[ERROR] Missing test_id in {json_path.name}")
                return None
            if not test_data["dut_id"]:
                print(f"[WARN] Missing dut_id in {json_path.name}")
            if not test_data["serial_number"]:
                print(f"[WARN] Missing serial_number in {json_path.name}")

            return test_data

        except Exception as e:
            print(f"[ERROR] Failed to parse JSON {json_path.name}: {e}")
            return None

    def parse_csv(
        self, csv_path: Path, test_id: str, serial_number: str
    ) -> List[Dict]:
        """
        Parse CSV file and convert pivot table to individual measurements

        Args:
            csv_path: Path to CSV file
            test_id: Test ID from JSON (to replace CSV's Test_ID)
            serial_number: Serial number for validation

        Returns:
            List of measurement dictionaries
        """
        measurements = []

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    cycle_number = int(row["Cycle"])
                    csv_serial = row["Serial"]

                    # Validate serial number
                    if csv_serial != serial_number:
                        print(
                            f"[WARN] Serial mismatch in {csv_path.name}: "
                            f"CSV={csv_serial}, JSON={serial_number}"
                        )

                    # Parse timestamp from Date and Time columns
                    date_str = row["Date"]
                    time_str = row["Time"]
                    timestamp = datetime.strptime(
                        f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S"
                    )

                    # Extract temperature-position measurements (T38_P170, T42_P170, ...)
                    for col_name, force_str in row.items():
                        # Match pattern: T<temp>_P<position>
                        match = re.match(r"T(\d+)_P(\d+)", col_name)
                        if match:
                            temperature = float(match.group(1))
                            position = float(match.group(2)) * 1000  # P170 → 170000

                            # Parse force value
                            try:
                                force = float(force_str)
                            except (ValueError, TypeError):
                                print(
                                    f"[WARN] Invalid force value: {force_str} "
                                    f"in {csv_path.name}, cycle {cycle_number}"
                                )
                                force = 0.0

                            measurements.append(
                                {
                                    "test_id": test_id,  # Use JSON's test_id!
                                    "serial_number": serial_number,
                                    "cycle_number": cycle_number,
                                    "timestamp": timestamp,
                                    "temperature": temperature,
                                    "position": position,
                                    "force": force,
                                }
                            )

            print(
                f"[INFO] Parsed {len(measurements)} measurements from {csv_path.name}"
            )
            return measurements

        except Exception as e:
            print(f"[ERROR] Failed to parse CSV {csv_path.name}: {e}")
            return []

    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_string:
            return None

        try:
            # Handle ISO format
            return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None


class DatabaseRebuilder:
    """Rebuild database from log files"""

    def __init__(self, db_path: str):
        self.db_manager = DatabaseManager(db_path)

    async def rebuild(
        self, test_data_list: List[Dict], measurements_list: List[List[Dict]]
    ):
        """
        Rebuild database with proper Foreign Key relationships

        Args:
            test_data_list: List of test_results data
            measurements_list: List of raw_measurements data (one list per test)
        """
        try:
            # Initialize database
            await self.db_manager.initialize()

            # Step 1: Clear existing data
            print("\n[STEP 1] Clearing existing database...")
            await self._clear_database()

            # Step 2: Save test_results (parent table)
            print("\n[STEP 2] Saving test_results...")
            await self._save_test_results(test_data_list)

            # Step 3: Save raw_measurements (child table)
            print("\n[STEP 3] Saving raw_measurements...")
            await self._save_raw_measurements(measurements_list)

            # Step 4: Verify Foreign Key relationships
            print("\n[STEP 4] Verifying Foreign Key relationships...")
            await self._verify_relationships()

            print("\n[SUCCESS] Database rebuild complete!")

        finally:
            await self.db_manager.close()

    async def _clear_database(self):
        """Clear all data from database"""
        async with self.db_manager.get_session() as session:
            # Delete raw_measurements first (child table)
            from sqlalchemy import delete

            await session.execute(delete(RawMeasurement))
            await session.commit()

            # Delete test_results (parent table)
            await session.execute(delete(TestResult))
            await session.commit()

            print("[OK] Database cleared")

    async def _save_test_results(self, test_data_list: List[Dict]):
        """Save test_results to database"""
        async with self.db_manager.get_session() as session:
            for test_data in test_data_list:
                test_result = TestResult(
                    test_id=test_data["test_id"],
                    dut_id=test_data["dut_id"] or "UNKNOWN",
                    serial_number=test_data["serial_number"],
                    operator_id=test_data["operator_id"],
                    status=test_data["status"],
                    created_at=test_data["created_at"] or datetime.now(),
                    start_time=test_data["start_time"],
                    end_time=test_data["end_time"],
                    duration_seconds=test_data["duration_seconds"],
                    error_message=test_data["error_message"],
                    test_configuration=test_data["test_configuration"],
                )
                session.add(test_result)

            await session.commit()
            print(f"[OK] Saved {len(test_data_list)} test_results")

    async def _save_raw_measurements(self, measurements_list: List[List[Dict]]):
        """Save raw_measurements to database"""
        total_count = 0

        async with self.db_manager.get_session() as session:
            for measurements in measurements_list:
                for meas_data in measurements:
                    raw_measurement = RawMeasurement(
                        test_id=meas_data["test_id"],
                        serial_number=meas_data["serial_number"],
                        cycle_number=meas_data["cycle_number"],
                        timestamp=meas_data["timestamp"],
                        temperature=meas_data["temperature"],
                        position=meas_data["position"],
                        force=meas_data["force"],
                    )
                    session.add(raw_measurement)
                    total_count += 1

            await session.commit()
            print(f"[OK] Saved {total_count} raw_measurements")

    async def _verify_relationships(self):
        """Verify Foreign Key relationships"""
        from sqlalchemy import select, text

        async with self.db_manager.get_session() as session:
            # Check orphaned raw_measurements
            result = await session.execute(
                text("""
                    SELECT COUNT(DISTINCT rm.test_id)
                    FROM raw_measurements rm
                    LEFT JOIN test_results tr ON rm.test_id = tr.test_id
                    WHERE tr.test_id IS NULL
                """)
            )
            orphan_count = result.scalar()

            if orphan_count == 0:
                print("[OK] No orphaned raw_measurements found")
            else:
                print(
                    f"[ERROR] Found {orphan_count} orphaned raw_measurements!"
                )

            # Check test_results count
            result = await session.execute(select(TestResult))
            test_count = len(result.scalars().all())

            # Check raw_measurements count
            result = await session.execute(select(RawMeasurement))
            meas_count = len(result.scalars().all())

            print(f"[INFO] Total test_results: {test_count}")
            print(f"[INFO] Total raw_measurements: {meas_count}")


async def main():
    """Main function"""
    print("=" * 80)
    print("REBUILD DATABASE FROM LOG FILES")
    print("=" * 80)

    # Paths
    json_dir = "logs/test_results/json"
    csv_dir = "logs/EOL Force Test/raw_data"
    db_path = "database/test_data.db"

    # Parse log files
    parser = LogFileParser(json_dir, csv_dir)

    print("\n[STEP 1] Finding matching files...")
    file_pairs = parser.find_file_pairs()

    if not file_pairs:
        print("[ERROR] No matching files found!")
        return

    # Parse all files
    print("\n[STEP 2] Parsing files...")
    test_data_list = []
    measurements_list = []

    for json_path, csv_path in file_pairs:
        # Parse JSON
        test_data = parser.parse_json(json_path)
        if not test_data:
            continue

        # Parse CSV
        measurements = parser.parse_csv(
            csv_path, test_data["test_id"], test_data["serial_number"]
        )

        test_data_list.append(test_data)
        measurements_list.append(measurements)

    print(f"\n[INFO] Parsed {len(test_data_list)} tests successfully")

    # Rebuild database
    print("\n[STEP 3] Rebuilding database...")
    rebuilder = DatabaseRebuilder(db_path)
    await rebuilder.rebuild(test_data_list, measurements_list)

    print("\n" + "=" * 80)
    print("[DONE] Database rebuild complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
