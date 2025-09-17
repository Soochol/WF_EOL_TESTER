"""
CSV Logger for Heating/Cooling Time Test

Logs each test cycle's heating and cooling data to a CSV file with summary statistics.
Creates CSV files in logs/Heating Cooling Test/cycle_data/ directory.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


class HeatingCoolingCSVLogger:
    """
    CSV logger for heating/cooling time test results
    
    logs each test cycle as a row in CSV format with heating time, heating temperatures,
    cooling time, cooling temperatures, and timestamp. Adds summary statistics at the end.
    """

    def __init__(self, test_id: str, repeat_count: int):
        """
        Initialize CSV logger
        
        Args:
            test_id: Unique test identifier
            repeat_count: Expected number of test cycles
        """
        self.test_id = test_id
        self.repeat_count = repeat_count
        
        # Create file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"HC_Test_{timestamp}_{test_id}.csv"
        
        self.log_dir = Path("logs/Heating Cooling Test/cycle_data")
        self.file_path = self.log_dir / filename
        
        # Track data for summary statistics
        self.cycle_data: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        
        # Track if file has been initialized
        self._file_initialized = False
        
        logger.debug(f"CSV logger initialized: {self.file_path}")

    def write_cycle_data(
        self, 
        cycle_number: int,
        heating_data: Dict[str, Any],
        cooling_data: Dict[str, Any]
    ) -> None:
        """
        Write cycle data to CSV file
        
        Args:
            cycle_number: Current cycle number (1-based)
            heating_data: Heating phase timing data from MCU
            cooling_data: Cooling phase timing data from MCU
        """
        try:
            # Create directory if it doesn't exist (project pattern)
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize file with header if first write
            if not self._file_initialized:
                self._initialize_csv_file()
                self._file_initialized = True
            
            # Extract relevant data
            heating_time_ms = heating_data.get("total_duration_ms", 0.0)
            heating_from_temp = heating_data.get("from_temperature", 0.0)
            heating_to_temp = heating_data.get("to_temperature", 0.0)
            
            cooling_time_ms = cooling_data.get("total_duration_ms", 0.0)
            cooling_from_temp = cooling_data.get("from_temperature", 0.0)
            cooling_to_temp = cooling_data.get("to_temperature", 0.0)
            
            # Use timestamp from data if available, otherwise current time
            timestamp = heating_data.get("timestamp", datetime.now().isoformat())
            
            # Convert milliseconds to seconds with 2 decimal places
            heating_time_s = heating_time_ms / 1000.0
            cooling_time_s = cooling_time_ms / 1000.0
            
            # Prepare row data
            row_data = {
                "Cycle": cycle_number,
                "Heating_Time_s": f"{heating_time_s:.2f}",
                "Heating_From_Temp": f"{heating_from_temp:.1f}",
                "Heating_To_Temp": f"{heating_to_temp:.1f}",
                "Cooling_Time_s": f"{cooling_time_s:.2f}",
                "Cooling_From_Temp": f"{cooling_from_temp:.1f}",
                "Cooling_To_Temp": f"{cooling_to_temp:.1f}",
                "Timestamp": timestamp
            }
            
            # Store for summary calculations
            self.cycle_data.append({
                "cycle": cycle_number,
                "heating_time_ms": heating_time_ms,
                "cooling_time_ms": cooling_time_ms,
                "timestamp": timestamp
            })
            
            # Append to CSV file
            with open(self.file_path, "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "Cycle", "Heating_Time_s", "Heating_From_Temp", "Heating_To_Temp",
                    "Cooling_Time_s", "Cooling_From_Temp", "Cooling_To_Temp", "Timestamp"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(row_data)
            
            logger.debug(f"Cycle {cycle_number} data written to CSV: {self.file_path}")
            
        except Exception as e:
            logger.error(f"Failed to write cycle {cycle_number} data to CSV: {e}")

    def write_summary(self, completed_cycles: Optional[int] = None) -> None:
        """
        Write summary statistics to CSV file
        
        Args:
            completed_cycles: Number of actually completed cycles (for partial tests)
        """
        try:
            if not self.cycle_data:
                logger.warning("No cycle data available for summary")
                return
            
            # Calculate statistics
            heating_times = [d["heating_time_ms"] for d in self.cycle_data]
            cooling_times = [d["cooling_time_ms"] for d in self.cycle_data]
            
            total_cycles = len(self.cycle_data)
            actual_completed = completed_cycles if completed_cycles is not None else total_cycles
            
            # Calculate total test time
            end_time = datetime.now()
            total_test_time_s = (end_time - self.start_time).total_seconds()
            
            # Prepare summary data
            summary_data = [
                [""],  # Empty line separator
                ["Summary"],
                ["Total_Cycles", str(actual_completed)],
                ["Requested_Cycles", str(self.repeat_count)],
                ["Total_Test_Time_s", f"{total_test_time_s:.1f}"],
                ["Test_Completed_At", end_time.isoformat()],
            ]
            
            # Add heating statistics (convert ms to seconds)
            if heating_times:
                avg_heating_s = sum(heating_times) / len(heating_times) / 1000.0
                min_heating_s = min(heating_times) / 1000.0
                max_heating_s = max(heating_times) / 1000.0
                summary_data.extend([
                    ["Average_Heating_Time_s", f"{avg_heating_s:.2f}"],
                    ["Min_Heating_Time_s", f"{min_heating_s:.2f}"],
                    ["Max_Heating_Time_s", f"{max_heating_s:.2f}"],
                ])
            
            # Add cooling statistics (convert ms to seconds)
            if cooling_times:
                avg_cooling_s = sum(cooling_times) / len(cooling_times) / 1000.0
                min_cooling_s = min(cooling_times) / 1000.0
                max_cooling_s = max(cooling_times) / 1000.0
                summary_data.extend([
                    ["Average_Cooling_Time_s", f"{avg_cooling_s:.2f}"],
                    ["Min_Cooling_Time_s", f"{min_cooling_s:.2f}"],
                    ["Max_Cooling_Time_s", f"{max_cooling_s:.2f}"],
                ])
            
            # Add completion status
            if actual_completed < self.repeat_count:
                completion_percentage = (actual_completed / self.repeat_count) * 100
                summary_data.append(["Completion_Percentage", f"{completion_percentage:.1f}%"])
                summary_data.append(["Status", "Partial_Completion"])
            else:
                summary_data.append(["Completion_Percentage", "100.0%"])
                summary_data.append(["Status", "Complete"])
            
            # Write summary to file
            with open(self.file_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(summary_data)
            
            logger.info(f"Summary written to CSV: {self.file_path}")
            logger.info(f"Test completed: {actual_completed}/{self.repeat_count} cycles in {total_test_time_s:.1f}s")
            
        except Exception as e:
            logger.error(f"Failed to write summary to CSV: {e}")

    def _initialize_csv_file(self) -> None:
        """Initialize CSV file with header"""
        try:
            with open(self.file_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "Cycle", "Heating_Time_s", "Heating_From_Temp", "Heating_To_Temp",
                    "Cooling_Time_s", "Cooling_From_Temp", "Cooling_To_Temp", "Timestamp"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            
            logger.info(f"CSV file initialized with header: {self.file_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CSV file: {e}")
            raise

    def get_file_path(self) -> Path:
        """Get the CSV file path"""
        return self.file_path