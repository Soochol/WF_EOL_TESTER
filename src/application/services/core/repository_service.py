"""
Repository Service

Service layer that manages test result repository operations and data persistence.
Uses Exception First principles for error handling.
"""

# Standard library imports
import csv
from pathlib import Path

# Third-party imports
from loguru import logger

# Local application imports
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
        test_repository: TestResultRepository,
        raw_data_dir: str,
        summary_dir: str,
        summary_filename: str,
    ):
        self._test_repository = test_repository
        self._raw_data_dir = Path(raw_data_dir)
        self._summary_dir = Path(summary_dir)
        self._summary_filename = summary_filename

    @property
    def test_repository(self) -> TestResultRepository:
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
            raw_data_dir = self._raw_data_dir
            raw_data_dir.mkdir(parents=True, exist_ok=True)

            # Generate daily filename (date-based accumulation only)
            date_str = test.created_at.datetime.strftime("%Y%m%d")
            filename = f"raw_measurements_{date_str}.csv"
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
                csvfile.write(f"DUT Serial: {test.dut.serial_number or 'Unknown'}\n")
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
                            logger.debug(f"Position {pos} not found in temperature {temp}")
                            row.append("")  # Empty cell for missing measurements

                    writer.writerow(row)

            action = "created" if is_new_file else "appended to"
            serial_num = test.dut.serial_number or "Unknown"
            logger.info(f"Measurement raw data for {serial_num} {action} daily file: {filepath}")

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

    def _validate_csv_data(self, data_row: list, expected_columns: int) -> list:
        """
        Validate and sanitize CSV data row

        Args:
            data_row: List of data values to validate
            expected_columns: Expected number of columns

        Returns:
            Validated and sanitized data row
        """
        try:
            # Ensure we have the right number of columns
            if len(data_row) != expected_columns:
                logger.warning(
                    f"CSV row has {len(data_row)} columns, expected {expected_columns}. "
                    f"Data: {data_row}"
                )
                # Pad with empty strings or truncate as needed
                if len(data_row) < expected_columns:
                    data_row.extend([""] * (expected_columns - len(data_row)))
                else:
                    data_row = data_row[:expected_columns]

            # Sanitize each field
            sanitized_row = []
            for field in data_row:
                if field is None:
                    sanitized_field = ""
                else:
                    sanitized_field = str(field).strip()
                    # Remove any problematic characters that might break CSV
                    sanitized_field = sanitized_field.replace("\n", " ").replace("\r", " ")
                    # Limit field length to prevent extremely long fields
                    if len(sanitized_field) > 255:
                        sanitized_field = sanitized_field[:252] + "..."
                        logger.warning(f"Truncated long CSV field: {sanitized_field}")

                sanitized_row.append(sanitized_field)

            return sanitized_row

        except Exception as e:
            logger.error(f"Error validating CSV data: {e}")
            # Return safe fallback
            return ["Error"] * expected_columns

    def _read_existing_csv_data(self, csv_file: Path) -> tuple[list, dict]:
        """
        Read existing CSV data and create a lookup for serial numbers

        Args:
            csv_file: Path to the CSV file

        Returns:
            Tuple of (all_rows, serial_to_row_index_map)
        """
        if not csv_file.exists():
            return [], {}

        try:
            with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

            if not rows:
                return [], {}

            # Create mapping of serial number to row index (skip header)
            serial_map = {}
            for i, row in enumerate(rows[1:], start=1):  # start=1 because we skip header
                if len(row) >= 2:  # Ensure row has at least Test_ID and Serial_Number
                    serial_number = row[1].strip()  # Serial_Number is column index 1
                    if serial_number:
                        serial_map[serial_number] = i

            logger.debug(f"Read {len(rows)} rows from CSV, found {len(serial_map)} serial numbers")
            return rows, serial_map

        except Exception as e:
            logger.error(f"Failed to read existing CSV data: {e}")
            return [], {}

    def _write_csv_data(self, csv_file: Path, rows: list) -> None:
        """
        Write all CSV data to file

        Args:
            csv_file: Path to the CSV file
            rows: All rows including header to write
        """
        with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(
                csvfile,
                delimiter=",",
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
            )
            writer.writerows(rows)

    async def _update_test_summary(self, test: EOLTest) -> None:
        """
        Update test summary file with basic test information.
        Prevents duplicate entries for the same serial number by updating existing entries.

        Args:
            test: EOL test to add to summary
        """
        try:
            # Create directory if it doesn't exist
            test_results_dir = self._summary_dir
            test_results_dir.mkdir(parents=True, exist_ok=True)

            summary_file = test_results_dir / self._summary_filename

            # Read existing data
            existing_rows, serial_map = self._read_existing_csv_data(summary_file)

            # Prepare header if needed
            header = [
                "Test_ID",
                "Serial_Number",
                "Test_Date",
                "Status",
                "Duration_sec",
                "Operator_ID",
            ]

            # If no existing data, start with header
            if not existing_rows:
                existing_rows = [header]
                logger.debug(f"Creating new CSV file with header: {header}")

            # Prepare and validate test data
            serial_number = str(test.dut.serial_number or "Unknown").strip()
            test_date = test.created_at.datetime.strftime("%Y-%m-%d %H:%M:%S")
            status = "PASS" if test.test_result and test.test_result.is_passed() else "FAIL"
            test_duration = test.get_duration()
            duration = f"{test_duration.seconds:.2f}" if test_duration else "0.00"
            operator_id = str(test.operator_id).strip() if test.operator_id else "Unknown"

            # Validate data fields don't contain problematic characters
            test_id_str = str(test.test_id).strip()
            if not test_id_str:
                test_id_str = "Unknown"

            new_row = [
                test_id_str,
                serial_number,
                test_date,
                status,
                duration,
                operator_id,
            ]

            # Validate and sanitize the row data
            validated_row = self._validate_csv_data(new_row, 6)

            # Check if serial number already exists
            if serial_number in serial_map:
                row_index = serial_map[serial_number]
                logger.info(f"Updating existing entry for serial number: {serial_number}")
                existing_rows[row_index] = validated_row
            else:
                logger.info(f"Adding new entry for serial number: {serial_number}")
                existing_rows.append(validated_row)

            # Write all data back to file
            self._write_csv_data(summary_file, existing_rows)

            logger.debug(f"Test summary updated successfully for test {test.test_id}")

        except Exception as e:
            logger.error(f"Failed to update test summary: {e}")
            logger.error(
                f"Test data: ID={test.test_id}, DUT={test.dut.serial_number}, Operator={test.operator_id}"
            )
            # Don't raise exception as this is supplementary to main save operation

    def get_all_repositories(self) -> dict:
        """Get all repositories as a dictionary (for debugging/testing)"""
        return {"test_repository": self._test_repository}
