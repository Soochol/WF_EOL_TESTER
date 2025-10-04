"""
Result Loader Utility

Loads test results from JSON files for GUI display.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from loguru import logger

from ui.gui.services.gui_state_manager import CycleData, TestResult


def load_today_results(json_dir: str) -> List[TestResult]:
    """
    Load all test results from today's JSON files.

    Args:
        json_dir: Directory containing JSON test result files

    Returns:
        List of TestResult objects from today's tests
    """
    results = []
    json_path = Path(json_dir)

    if not json_path.exists():
        logger.warning(f"JSON directory not found: {json_dir}")
        return results

    # Get today's date string (YYYYMMDD)
    today_str = datetime.now().strftime("%Y%m%d")

    # Find all JSON files from today
    pattern = f"*_{today_str}_*.json"
    today_files = list(json_path.glob(pattern))

    logger.info(f"Found {len(today_files)} test files from today ({today_str})")

    for file_path in today_files:
        try:
            file_results = _load_results_from_file(file_path)
            results.extend(file_results)
            logger.debug(f"Loaded {len(file_results)} results from {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to load results from {file_path.name}: {e}")

    logger.info(f"Total {len(results)} cycle results loaded from {len(today_files)} files")
    return results


def _load_results_from_file(file_path: Path) -> List[TestResult]:
    """
    Load test results from a single JSON file.

    Creates ONE TestResult per test file with individual cycle data.

    Args:
        file_path: Path to JSON file

    Returns:
        List containing single TestResult object with all cycle measurements
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract test metadata
    test_id = data.get('test_id', 'unknown')
    serial_number = data.get('dut', {}).get('serial_number', 'unknown')

    test_result_data = data.get('test_result', {})
    test_status = test_result_data.get('test_status', 'unknown')

    # Map test status to PASS/FAIL
    status_map = {
        'completed': 'PASS',
        'failed': 'FAIL',
        'error': 'FAIL',
        'unknown': 'FAIL'
    }
    status = status_map.get(test_status, 'FAIL')

    # Override with is_passed if available
    if test_result_data.get('is_passed') is True:
        status = 'PASS'
    elif test_result_data.get('is_passed') is False:
        status = 'FAIL'

    # Parse timestamp
    end_time_str = test_result_data.get('end_time') or data.get('end_time')
    try:
        timestamp = datetime.fromisoformat(end_time_str) if end_time_str else datetime.now()
    except (ValueError, TypeError):
        timestamp = datetime.now()

    # Get duration
    duration_seconds = test_result_data.get('duration_seconds', 0.0)

    # Extract timing data and measurements
    actual_results = test_result_data.get('actual_results', {})
    timing_data = actual_results.get('timing_data', {})
    measurements = actual_results.get('measurements', {})

    # Create CycleData objects for each cycle
    cycles = []
    cycle_number = 1

    # Process each cycle in timing_data
    for cycle_key in sorted(timing_data.keys()):
        cycle_timing = timing_data[cycle_key]

        try:
            # Parse temperature from key (e.g., "cycle_1_temp_38")
            parts = cycle_key.split('_')
            temperature = float(parts[3])

            # Get heating and cooling times
            heating_time = int(cycle_timing.get('heating_time_s', 0) * 1000)  # Convert to ms
            cooling_time = int(cycle_timing.get('cooling_time_s', 0) * 1000)  # Convert to ms

            # Find corresponding force measurement
            force = 0.0
            stroke = 0.0

            # Look for matching temperature measurement
            # Try both "38.0" and "38" formats
            temp_str_float = str(float(temperature))  # "38.0"
            temp_str_int = str(int(temperature))      # "38"

            temp_measurements = None
            if temp_str_float in measurements:
                temp_measurements = measurements[temp_str_float]
            elif temp_str_int in measurements:
                temp_measurements = measurements[temp_str_int]

            if temp_measurements:
                # Get the first stroke measurement (usually there's only one)
                stroke_key = list(temp_measurements.keys())[0]
                stroke = float(stroke_key) / 1000.0  # Convert pulse to mm (170000.0 -> 170.0)
                force = temp_measurements[stroke_key].get('force', 0.0)

            # Create CycleData
            cycle_data = CycleData(
                cycle=cycle_number,
                temperature=temperature,
                stroke=stroke,
                force=force,
                heating_time=heating_time,
                cooling_time=cooling_time,
                status='PASS' if force > 0 else 'FAIL'  # Simple status determination
            )
            cycles.append(cycle_data)
            cycle_number += 1

        except (ValueError, IndexError, KeyError) as e:
            logger.debug(f"Failed to parse cycle data from {cycle_key}: {e}")

    # Create TestResult with all cycle data
    result = TestResult(
        test_id=test_id,
        serial_number=serial_number,
        status=status,
        timestamp=timestamp,
        duration_seconds=duration_seconds,
        cycles=cycles,
    )

    return [result]  # Return list with single result
