"""
Result Loader Utility

Loads test results from JSON files for GUI display.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from loguru import logger

from ui.gui.services.gui_state_manager import TestResult


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

    Args:
        file_path: Path to JSON file

    Returns:
        List of TestResult objects from this file
    """
    results = []

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract test metadata
    test_status = data.get('test_result', {}).get('test_status', 'unknown')
    status_map = {
        'completed': 'PASS',
        'failed': 'FAIL',
        'error': 'FAIL',
        'unknown': 'FAIL'
    }
    default_status = status_map.get(test_status, 'FAIL')

    # Extract timing data (contains cycle information)
    timing_data = data.get('test_result', {}).get('actual_results', {}).get('timing_data', {})

    # Extract measurements (contains force values)
    measurements = data.get('test_result', {}).get('actual_results', {}).get('measurements', {})

    # Process each cycle
    for cycle_key, cycle_data in timing_data.items():
        # Parse cycle number and temperature from key (e.g., "cycle_1_temp_38")
        try:
            parts = cycle_key.split('_')
            cycle = int(parts[1])
            temperature = float(parts[3])

            # Get heating and cooling times
            heating_time = int(cycle_data.get('heating_time_s', 0) * 1000)  # Convert to ms
            cooling_time = int(cycle_data.get('cooling_time_s', 0) * 1000)  # Convert to ms

            # Find matching force measurement
            force = 0.0
            stroke = 0.0

            # Measurements are organized by temperature
            temp_key = str(float(temperature))
            if temp_key in measurements:
                temp_measurements = measurements[temp_key]
                # Usually there's only one stroke position
                if temp_measurements:
                    stroke_key = list(temp_measurements.keys())[0]
                    stroke = float(stroke_key)
                    force = temp_measurements[stroke_key].get('force', 0.0)

            # Create TestResult
            result = TestResult(
                cycle=cycle,
                temperature=temperature,
                stroke=stroke,
                force=force,
                heating_time=heating_time,
                cooling_time=cooling_time,
                status=default_status,
                timestamp=datetime.now()  # Use current time as we don't have exact cycle time
            )
            results.append(result)

        except (ValueError, IndexError, KeyError) as e:
            logger.debug(f"Failed to parse cycle data from {cycle_key}: {e}")
            continue

    return results
