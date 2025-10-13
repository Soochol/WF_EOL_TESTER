"""
Test Result Parser Service

Parses test result JSON files and provides statistics.
"""

# Standard library imports
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Third-party imports
from loguru import logger


class TestResultStats:
    """Test result statistics"""

    def __init__(self):
        self.total_tests: int = 0
        self.passed_tests: int = 0
        self.failed_tests: int = 0
        self.pass_rate: float = 0.0
        self.recent_results: List[Dict] = []

    def calculate_pass_rate(self) -> None:
        """Calculate pass rate percentage"""
        if self.total_tests > 0:
            self.pass_rate = (self.passed_tests / self.total_tests) * 100.0
        else:
            self.pass_rate = 0.0


class TestResultParser:
    """Parser for test result JSON files"""

    def __init__(self, results_directory: str = "logs/test_results/json"):
        self.results_directory = Path(results_directory)
        if not self.results_directory.is_absolute():
            # Make it relative to project root
            self.results_directory = Path.cwd() / self.results_directory

    def parse_today_results(self) -> TestResultStats:
        """
        Parse test results from today

        Returns:
            TestResultStats with today's statistics
        """
        today = datetime.now().strftime("%Y%m%d")
        return self.parse_results_by_date(today)

    def parse_results_by_date(self, date_str: str) -> TestResultStats:
        """
        Parse test results for a specific date

        Args:
            date_str: Date string in YYYYMMDD format

        Returns:
            TestResultStats with statistics for the specified date
        """
        stats = TestResultStats()

        if not self.results_directory.exists():
            logger.warning(f"Results directory not found: {self.results_directory}")
            return stats

        # Find all JSON files matching the date
        pattern = f"*_{date_str}_*.json"
        json_files = list(self.results_directory.glob(pattern))

        logger.info(f"Found {len(json_files)} test results for date {date_str}")

        for json_file in json_files:
            try:
                result_data = self._parse_single_result(json_file)
                if result_data:
                    stats.total_tests += 1

                    # Check if test passed
                    if result_data.get("is_passed", False):
                        stats.passed_tests += 1
                    else:
                        stats.failed_tests += 1

                    # Add to recent results
                    stats.recent_results.append(result_data)

            except Exception as e:
                logger.error(f"Failed to parse {json_file}: {e}")
                continue

        # Sort recent results by timestamp (newest first)
        stats.recent_results.sort(
            key=lambda x: x.get("start_time", ""), reverse=True
        )

        # Calculate pass rate
        stats.calculate_pass_rate()

        logger.info(
            f"Statistics - Total: {stats.total_tests}, "
            f"Passed: {stats.passed_tests}, "
            f"Failed: {stats.failed_tests}, "
            f"Pass Rate: {stats.pass_rate:.1f}%"
        )

        return stats

    def parse_all_results(self, limit: Optional[int] = None) -> TestResultStats:
        """
        Parse all test results

        Args:
            limit: Maximum number of recent results to include (None = all)

        Returns:
            TestResultStats with overall statistics
        """
        stats = TestResultStats()

        if not self.results_directory.exists():
            logger.warning(f"Results directory not found: {self.results_directory}")
            return stats

        # Find all JSON files
        json_files = list(self.results_directory.glob("*.json"))

        logger.info(f"Found {len(json_files)} total test results")

        for json_file in json_files:
            try:
                result_data = self._parse_single_result(json_file)
                if result_data:
                    stats.total_tests += 1

                    # Check if test passed
                    if result_data.get("is_passed", False):
                        stats.passed_tests += 1
                    else:
                        stats.failed_tests += 1

                    # Add to recent results
                    stats.recent_results.append(result_data)

            except Exception as e:
                logger.error(f"Failed to parse {json_file}: {e}")
                continue

        # Sort recent results by timestamp (newest first)
        stats.recent_results.sort(
            key=lambda x: x.get("start_time", ""), reverse=True
        )

        # Limit results if specified
        if limit and len(stats.recent_results) > limit:
            stats.recent_results = stats.recent_results[:limit]

        # Calculate pass rate
        stats.calculate_pass_rate()

        logger.info(
            f"All Statistics - Total: {stats.total_tests}, "
            f"Passed: {stats.passed_tests}, "
            f"Failed: {stats.failed_tests}, "
            f"Pass Rate: {stats.pass_rate:.1f}%"
        )

        return stats

    def _parse_single_result(self, json_file: Path) -> Optional[Dict]:
        """
        Parse a single test result JSON file

        Args:
            json_file: Path to JSON file

        Returns:
            Dictionary with test result data or None if parsing failed
        """
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract key information
            test_result = data.get("test_result", {})
            actual_results = test_result.get("actual_results", {})
            measurements = actual_results.get("measurements", {})

            result_data = {
                "test_id": data.get("test_id", "Unknown"),
                "serial_number": data.get("dut", {}).get("serial_number", "N/A"),
                "operator_id": data.get("operator_id", "N/A"),
                "start_time": data.get("start_time", ""),
                "end_time": data.get("end_time", ""),
                "duration_seconds": data.get("duration_seconds", 0),
                "status": data.get("status", "unknown"),
                "is_passed": test_result.get("is_passed", False),
                "is_finished": test_result.get("is_finished", False),
                "error_message": test_result.get("error_message"),
                "measurement_count": len(test_result.get("measurement_ids", [])),
                "measurements": measurements,  # Include detailed measurements
            }

            return result_data

        except Exception as e:
            logger.error(f"Failed to parse {json_file}: {e}")
            return None

    def get_date_range(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get the date range of available test results

        Returns:
            Tuple of (earliest_date, latest_date) in YYYYMMDD format
        """
        if not self.results_directory.exists():
            return None, None

        json_files = list(self.results_directory.glob("*.json"))
        if not json_files:
            return None, None

        dates = []
        for json_file in json_files:
            # Extract date from filename pattern: *_YYYYMMDD_*.json
            parts = json_file.stem.split("_")
            if len(parts) >= 2:
                date_part = parts[-2]  # Second to last part
                if len(date_part) == 8 and date_part.isdigit():
                    dates.append(date_part)

        if not dates:
            return None, None

        dates.sort()
        return dates[0], dates[-1]
