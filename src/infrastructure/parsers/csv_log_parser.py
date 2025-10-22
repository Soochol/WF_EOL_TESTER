"""
CSV Log Parser

Parses CSV raw measurement files for database import.
"""

# Standard library imports
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports
from loguru import logger


class CsvLogParser:
    """Parser for CSV raw measurement log files"""

    # Pattern to extract temperature and position from column names (e.g., T38_P170)
    COLUMN_PATTERN = re.compile(r"T(\d+(?:\.\d+)?)_P(\d+(?:\.\d+)?)")

    # Pattern to extract parent test_id from cycle test_id (e.g., CYCLE_1_OF_2_20251020_142702)
    # This extracts serial and timestamp: test1_20251020_142702
    CYCLE_TEST_ID_PATTERN = re.compile(r"CYCLE_\d+_OF_\d+_(\d{8}_\d{6})")

    @staticmethod
    def parse_file(file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse CSV log file into database format

        Args:
            file_path: Path to CSV log file

        Returns:
            Dictionary with parsed measurements, or None if parsing fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                logger.warning(f"Empty CSV file: {file_path}")
                return None

            # Parse all measurement rows
            measurements = []
            for row in rows:
                parsed_row = CsvLogParser._parse_row(row)
                if parsed_row:
                    measurements.extend(parsed_row)

            if not measurements:
                logger.warning(f"No valid measurements in {file_path}")
                return None

            result = {
                "file_path": str(file_path),
                "measurements": measurements,
                "total_measurements": len(measurements),
            }

            logger.debug(
                f"Parsed CSV file: {file_path.name} → {len(measurements)} measurements"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to parse CSV file {file_path}: {e}")
            return None

    @staticmethod
    def _parse_row(row: Dict[str, str]) -> Optional[List[Dict[str, Any]]]:
        """
        Parse single CSV row into measurements

        Args:
            row: CSV row dictionary

        Returns:
            List of measurement dictionaries
        """
        try:
            # Extract metadata
            cycle = int(row.get("Cycle", 0))
            test_id_raw = row.get("Test_ID", "")
            serial = row.get("Serial", "")
            date_str = row.get("Date", "")
            time_str = row.get("Time", "")
            status = row.get("Status", "UNKNOWN")

            # Extract parent test_id from cycle test_id
            # Convert "CYCLE_1_OF_2_20251020_142702" to "test1_20251020_142702"
            # (Use serial number + timestamp for consistency with JSON test_ids)
            match = CsvLogParser.CYCLE_TEST_ID_PATTERN.match(test_id_raw)
            if match and serial:
                # Extract timestamp from cycle test_id
                timestamp_str = match.group(1)
                # Construct parent test_id: serial_timestamp
                test_id = f"{serial}_{timestamp_str}"
            else:
                # Fallback: use raw test_id if pattern doesn't match
                test_id = test_id_raw
                logger.debug(f"Could not extract parent test_id from: {test_id_raw}, using as-is")

            # Parse timestamp
            timestamp = None
            if date_str and time_str:
                try:
                    timestamp = datetime.strptime(
                        f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    logger.debug(f"Could not parse timestamp: {date_str} {time_str}")

            # Extract temperature-position-force measurements
            measurements = []
            for column_name, force_str in row.items():
                match = CsvLogParser.COLUMN_PATTERN.match(column_name)
                if match:
                    temperature = float(match.group(1))
                    position = float(match.group(2)) * 1000  # Convert to encoder units

                    try:
                        force = float(force_str) if force_str else None
                    except ValueError:
                        force = None

                    if force is not None:
                        measurements.append(
                            {
                                "test_id": test_id,
                                "serial_number": serial,
                                "cycle_number": cycle,
                                "timestamp": timestamp or datetime.now(),
                                "temperature": temperature,
                                "position": position,
                                "force": force,
                            }
                        )

            return measurements if measurements else None

        except Exception as e:
            logger.debug(f"Failed to parse CSV row: {e}")
            return None

    @staticmethod
    def scan_directory(directory: Path) -> List[Path]:
        """
        Scan directory for CSV log files

        Args:
            directory: Directory to scan

        Returns:
            List of CSV file paths
        """
        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return []

        csv_files = list(directory.glob("*.csv"))
        # Filter out summary files
        csv_files = [f for f in csv_files if "summary" not in f.name.lower()]

        logger.info(f"Found {len(csv_files)} CSV files in {directory}")
        return csv_files
