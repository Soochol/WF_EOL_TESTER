"""
JSON Log Parser

Parses JSON test result files for database import.
"""

# Standard library imports
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Third-party imports
from loguru import logger


class JsonLogParser:
    """Parser for JSON test result log files"""

    @staticmethod
    def parse_file(file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse JSON log file into database format

        Args:
            file_path: Path to JSON log file

        Returns:
            Dictionary ready for database insertion, or None if parsing fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract test result data
            test_result = {
                "test_id": data.get("test_id"),
                "dut_id": data.get("dut", {}).get("dut_id", "UNKNOWN"),
                "serial_number": data.get("dut", {}).get("serial_number"),
                "operator_id": data.get("operator_id", "UNKNOWN"),
                "status": data.get("status", "unknown"),
                "created_at": JsonLogParser._parse_datetime(data.get("created_at")),
                "start_time": JsonLogParser._parse_datetime(data.get("start_time")),
                "end_time": JsonLogParser._parse_datetime(data.get("end_time")),
                "duration_seconds": data.get("duration_seconds"),
                "error_message": data.get("error_message"),
                "test_configuration": data.get("test_configuration"),
            }

            logger.debug(f"Parsed JSON file: {file_path.name} → test_id={test_result['test_id']}")
            return test_result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}")
            return None

    @staticmethod
    def _parse_datetime(dt_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_string:
            return None

        try:
            # Handle ISO format datetime strings
            return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse datetime: {dt_string}")
            return None

    @staticmethod
    def scan_directory(directory: Path) -> list[Path]:
        """
        Scan directory for JSON log files

        Args:
            directory: Directory to scan

        Returns:
            List of JSON file paths
        """
        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return []

        json_files = list(directory.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files in {directory}")
        return json_files
