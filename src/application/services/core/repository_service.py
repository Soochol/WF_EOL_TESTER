"""
Repository Service

Service layer that manages test result repository operations and data persistence.
Uses Exception First principles for error handling.
"""

# Standard library imports
import csv
from pathlib import Path
import re

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
        Save measurement raw data as pivot table CSV file

        Args:
            test: EOL test containing measurement data
        """
        try:
            # Create directory if it doesn't exist
            raw_data_dir = self._raw_data_dir
            raw_data_dir.mkdir(parents=True, exist_ok=True)

            # Generate test-session-based filename (each test session creates new file)
            # Priority 1: Use session_timestamp if available (for repeat_count tests)
            if test.session_timestamp:
                date_time_str = test.session_timestamp
            else:
                # Priority 2: Extract timestamp from test_id (format: DEFAULT001_20250918_012300)
                test_id_str = str(test.test_id)
                test_id_parts = test_id_str.split("_")

                if len(test_id_parts) >= 3:
                    # Use test ID timestamp for filename (test session based)
                    date_time_str = f"{test_id_parts[-2]}_{test_id_parts[-1]}"
                else:
                    # Fallback: use test creation time
                    date_time_str = test.created_at.datetime.strftime("%Y%m%d_%H%M%S")

            filename = f"raw_measurements_{date_time_str}.csv"
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

            # Extract clean serial number
            full_serial = str(test.dut.serial_number or "Unknown").strip()
            serial_number = self._extract_serial_number(full_serial)

            # Get all unique temperatures and positions
            temperatures = sorted([float(temp) for temp in measurements_dict.keys()])
            all_positions = set()
            for temp_data in measurements_dict.values():
                all_positions.update(temp_data.keys())
            positions = sorted([float(pos) for pos in all_positions])

            # Generate dynamic headers
            headers = ["Test_ID", "Serial", "Date", "Time", "Status"]
            for temp in temperatures:
                for pos in positions:
                    # Convert position from micrometers to millimeters for header
                    pos_mm = self._convert_micrometers_to_millimeters(pos)
                    headers.append(f"T{int(temp)}_P{int(pos_mm)}")

            # Check if file exists and if headers match
            is_new_file = not filepath.exists()

            # Prepare row data
            test_date = test.created_at.datetime.strftime("%Y-%m-%d")
            test_time = test.created_at.datetime.strftime("%H:%M:%S")
            status = "PASS" if test.test_result.is_passed() else "FAIL"

            row_data = [str(test.test_id), serial_number, test_date, test_time, status]

            # Add force values for each temperature/position combination
            for temp in temperatures:
                # measurements_dict now uses float keys, so use temp directly
                temp_measurements = measurements_dict.get(temp, {})

                for pos in positions:
                    # measurements_dict now uses float keys, so use pos directly
                    if pos in temp_measurements:
                        position_data = temp_measurements[pos]
                        force_value = self._extract_force_value(
                            position_data, str(int(temp)), str(int(pos))
                        )
                        if force_value is not None and isinstance(force_value, (int, float)):
                            row_data.append(f"{force_value:.3f}")
                        else:
                            row_data.append("")
                    else:
                        row_data.append("")  # Empty cell for missing measurements

            # Write to CSV file
            with open(
                filepath, "a" if not is_new_file else "w", newline="", encoding="utf-8"
            ) as csvfile:
                writer = csv.writer(
                    csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
                )

                # Write header only for new files
                if is_new_file:
                    writer.writerow(headers)

                # Write data row
                writer.writerow(row_data)

            action = "created" if is_new_file else "appended to"
            logger.info(f"Measurement raw data for {serial_number} {action} daily file: {filepath}")

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

    def _convert_micrometers_to_millimeters(self, value_um: float) -> float:
        """
        Convert micrometers to millimeters for CSV display

        Args:
            value_um: Value in micrometers (μm)

        Returns:
            Value in millimeters (mm)
        """
        return value_um / 1000.0

    def _extract_serial_number(self, full_serial: str) -> str:
        """
        Extract short serial number from full DUT serial

        Args:
            full_serial: Full serial like 'DEFAULT001_C001'

        Returns:
            Short serial like 'C001', or the original if pattern not found
        """
        try:
            # Pattern to match _C### at the end of the string
            match = re.search(r"_([C]\d{3})$", full_serial)
            if match:
                return match.group(1)  # Return just the C001 part

            # If no pattern match, return the original
            logger.debug(f"No serial pattern found in '{full_serial}', using as-is")
            return full_serial

        except Exception as e:
            logger.warning(f"Error extracting serial number from '{full_serial}': {e}")
            return full_serial  # Safe fallback

    def _validate_csv_data(self, data_row: list, expected_columns: int) -> list:
        """
        Validate and sanitize CSV data row with enhanced validation

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

            # Enhanced sanitization for each field
            sanitized_row = []
            for i, field in enumerate(data_row):
                if field is None:
                    sanitized_field = ""
                else:
                    sanitized_field = str(field).strip()

                    # Remove problematic characters that break CSV
                    sanitized_field = (
                        sanitized_field.replace("\n", " ")
                        .replace("\r", " ")
                        .replace("\t", " ")
                        .replace('"', "'")  # Replace quotes to avoid CSV escaping issues
                    )

                    # Collapse multiple spaces
                    sanitized_field = " ".join(sanitized_field.split())

                    # Field-specific validation
                    if i == 1:  # Serial_Number column
                        # Ensure serial number is alphanumeric
                        sanitized_field = "".join(c for c in sanitized_field if c.isalnum())
                        if not sanitized_field:
                            sanitized_field = "Unknown"

                    # Limit field length to prevent extremely long fields
                    if len(sanitized_field) > 100:  # Reduced from 255
                        sanitized_field = sanitized_field[:97] + "..."
                        logger.warning(f"Truncated long CSV field: {sanitized_field}")

                sanitized_row.append(sanitized_field)

            return sanitized_row

        except Exception as e:
            logger.error(f"Error validating CSV data: {e}")
            # Return safe fallback with proper column count (7 columns)
            return ["Error", "Unknown", "1970-01-01", "00:00:00", "FAIL", "0.00", "Unknown"]

    def _read_existing_csv_rows(self, csv_file: Path) -> list:
        """
        Read existing CSV rows (no duplicate checking needed)

        Args:
            csv_file: Path to the CSV file

        Returns:
            List of existing rows (including header if present)
        """
        if not csv_file.exists():
            return []

        try:
            with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

            logger.debug(f"Read {len(rows)} existing rows from CSV file")
            return rows

        except Exception as e:
            logger.error(f"Failed to read existing CSV data: {e}")
            # Return empty list to start fresh on error
            return []

    def _write_csv_data(self, csv_file: Path, rows: list) -> None:
        """
        Write all CSV data to file with enhanced settings

        Args:
            csv_file: Path to the CSV file
            rows: All rows including header to write
        """
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(
                    csvfile,
                    delimiter=",",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                    lineterminator="\n",
                    escapechar=None,  # Use quoting instead of escaping
                )
                writer.writerows(rows)

            logger.debug(f"Successfully wrote {len(rows)} rows to CSV file: {csv_file}")

        except Exception as e:
            logger.error(f"Failed to write CSV data to {csv_file}: {e}")
            raise

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

            # Read existing data (no need for serial mapping since we don't check duplicates)
            existing_rows = self._read_existing_csv_rows(summary_file)

            # Prepare header if needed
            header = [
                "Test_ID",
                "Serial_Number",
                "Test_Date",
                "Test_Time",
                "Status",
                "Duration_sec",
                "Operator_ID",
            ]

            # If no existing data, start with header
            if not existing_rows:
                existing_rows = [header]
                logger.debug(f"Creating new CSV file with header: {header}")

            # Prepare and validate test data
            # Use original serial number as entered by user (no extraction)
            serial_number = str(test.dut.serial_number or "Unknown").strip()

            # Separate date and time for proper CSV column alignment
            test_date = test.created_at.datetime.strftime("%Y-%m-%d")
            test_time = test.created_at.datetime.strftime("%H:%M:%S")
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
                test_time,
                status,
                duration,
                operator_id,
            ]

            # Validate and sanitize the row data
            validated_row = self._validate_csv_data(new_row, 7)

            # Always add as new row - each test is unique by Test_ID
            logger.info(f"Adding new test entry: {test_id_str} for serial {serial_number}")
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
