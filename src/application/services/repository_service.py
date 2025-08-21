"""
Repository Service

Service layer that manages test result repository operations and data persistence.
Uses Exception First principles for error handling.
"""

import csv
from pathlib import Path
from typing import Optional

from loguru import logger

from application.interfaces.repository.test_result_repository import (
    TestResultRepository,
)
from domain.entities.eol_test import EOLTest
from domain.exceptions import RepositoryAccessError


class RepositoryService:
    """
    Service for managing test result repository operations

    This service centralizes test result repository operations and provides
    a unified interface for test data persistence. Additionally generates
    CSV files for measurement raw data and test summaries.
    """

    def __init__(
        self,
        test_repository: Optional[TestResultRepository] = None,
    ):
        self._test_repository = test_repository

    @property
    def test_repository(
        self,
    ) -> Optional[TestResultRepository]:
        """Get the test repository"""
        return self._test_repository

    async def save_test_result(self, test: EOLTest) -> None:
        """
        Save test result to repository and generate data files

        Args:
            test: EOL test to save

        Raises:
            RepositoryAccessError: If saving fails
        """
        # Save to original JSON repository
        if not self._test_repository:
            logger.warning("No test repository configured, skipping test result save")
            return

        try:
            await self._test_repository.save(test)
            logger.debug("Test result saved successfully")

            # Generate additional data files
            await self._save_measurement_raw_data(test)
            await self._update_test_summary(test)

        except Exception as e:
            logger.error(f"Failed to save test result: {e}")
            raise RepositoryAccessError(operation="save_test_result", reason=str(e)) from e

    async def _save_measurement_raw_data(self, test: EOLTest) -> None:
        """
        Save measurement raw data as CSV file

        Args:
            test: EOL test containing measurement data
        """
        try:
            # Create directory if it doesn't exist
            raw_data_dir = Path("TestResults/raw_data")
            raw_data_dir.mkdir(parents=True, exist_ok=True)

            # Generate daily filename (date-based accumulation)
            serial_number = test.dut.serial_number or "Unknown"
            date_str = test.created_at.datetime.strftime("%Y%m%d")
            filename = f"{serial_number}_{date_str}.csv"
            filepath = raw_data_dir / filename

            # Extract measurement data
            if not test.test_result or not test.test_result.actual_results:
                logger.warning(f"No measurement data found for test {test.test_id}")
                return

            measurements_dict = test.test_result.actual_results.get("measurements", {})
            if not measurements_dict:
                logger.warning(f"No measurements data found for test {test.test_id}")
                return

            logger.debug(f"Extracting force data for test {test.test_id}")

            # Determine write mode: append if file exists, create new if not
            is_new_file = not filepath.exists()
            write_mode = "w" if is_new_file else "a"
            
            # Write CSV file
            with open(filepath, write_mode, newline="", encoding="utf-8") as csvfile:
                # Add blank line separator if appending to existing file
                if not is_new_file:
                    csvfile.write("\n\n")
                # Write test information header
                csvfile.write("# Test Information\n")
                csvfile.write(f"Test ID: {test.test_id}\n")
                csvfile.write(f"DUT Serial: {serial_number}\n")
                csvfile.write(
                    f"Test Date: {test.created_at.datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                csvfile.write(f"Status: {'PASS' if test.test_result.is_passed() else 'FAIL'}\n")
                csvfile.write("\n")
                csvfile.write(
                    "# Raw Measurement Data (Temperature[°C] vs Distance[mm] → Force[kgf])\n"
                )

                # Get all unique positions (distances) across all temperatures
                all_positions = set()
                for temp_data in measurements_dict.values():
                    all_positions.update(temp_data.keys())
                sorted_positions = sorted(all_positions, key=float)

                # Write CSV header
                writer = csv.writer(csvfile)
                header = ["Temperature"] + [str(pos) for pos in sorted_positions]
                writer.writerow(header)

                # Write measurement data
                for temp in sorted(measurements_dict.keys(), key=float):
                    row = [temp]
                    temp_measurements = measurements_dict[temp]

                    for pos in sorted_positions:
                        if pos in temp_measurements:
                            position_data = temp_measurements[pos]
                            # Extract force value using multiple strategies
                            force_value = self._extract_force_value(position_data, temp, str(pos))

                            # Add force value to row
                            if force_value is not None and isinstance(force_value, (int, float)):
                                row.append(f"{force_value:.3f}")
                            else:
                                row.append("")
                        else:
                            logger.debug(f"Position {pos_str} not found in temperature {temp}")
                            row.append("")  # Empty cell for missing measurements

                    writer.writerow(row)

            action = "created" if is_new_file else "appended to"
            logger.info(f"Measurement raw data {action} daily file: {filepath}")

        except Exception as e:
            logger.error(f"Failed to save measurement raw data: {e}")
            # Don't raise exception as this is supplementary to main save operation

    def _extract_force_value(self, position_data, temp: str, pos_str: str):
        """
        Extract force value from position data using multiple fallback strategies

        Args:
            position_data: Data from measurements for specific position
            temp: Temperature string for logging
            pos_str: Position string for logging

        Returns:
            Force value or None if extraction fails
        """
        # Strategy 1: Standard dictionary with 'force' key
        if isinstance(position_data, dict) and "force" in position_data:
            return position_data["force"]

        # Strategy 2: Position data might be the force value directly
        if isinstance(position_data, (int, float)):
            return position_data

        # Strategy 3: Check for alternative key names
        if isinstance(position_data, dict):
            # Try common alternative key names
            for key in ["Force", "FORCE", "value", "measurement"]:
                if key in position_data:
                    return position_data[key]

        # Strategy 4: If it's a string that can be converted to float
        if isinstance(position_data, str):
            try:
                return float(position_data)
            except (ValueError, TypeError):
                pass

        # Log warning if no valid force data found
        logger.warning(
            "No valid force data found for temp %s, pos %s: %s (type: %s)",
            temp,
            pos_str,
            position_data,
            type(position_data),
        )
        return None

    async def _update_test_summary(self, test: EOLTest) -> None:
        """
        Update test summary file with basic test information

        Args:
            test: EOL test to add to summary
        """
        try:
            # Create directory if it doesn't exist
            test_results_dir = Path("TestResults")
            test_results_dir.mkdir(parents=True, exist_ok=True)

            summary_file = test_results_dir / "test_summary.csv"

            # Check if file exists and create header if needed
            file_exists = summary_file.exists()

            with open(summary_file, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header if file is new
                if not file_exists:
                    header = [
                        "Test_ID",
                        "Serial_Number",
                        "Test_Date",
                        "Status",
                        "Duration_sec",
                        "Operator_ID",
                    ]
                    writer.writerow(header)

                # Write test data
                serial_number = test.dut.serial_number or "Unknown"
                test_date = test.created_at.datetime.strftime("%Y-%m-%d %H:%M:%S")
                status = "PASS" if test.test_result and test.test_result.is_passed() else "FAIL"
                test_duration = test.get_duration()
                duration = test_duration.seconds if test_duration else 0

                row = [
                    str(test.test_id),
                    serial_number,
                    test_date,
                    status,
                    f"{duration:.2f}",
                    str(test.operator_id),
                ]
                writer.writerow(row)

            logger.debug(f"Test summary updated for test {test.test_id}")

        except Exception as e:
            logger.error(f"Failed to update test summary: {e}")
            # Don't raise exception as this is supplementary to main save operation

    def get_all_repositories(self) -> dict:
        """Get all repositories as a dictionary (for debugging/testing)"""
        return {"test_repository": self._test_repository}
