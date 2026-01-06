"""EOL Statistics Service

Provides statistical analysis and data aggregation for EOL Force Test results.
"""

# Standard library imports
from datetime import datetime
from typing import Any, Dict, List

# Third-party imports
import numpy as np
from loguru import logger

# Local application imports
from application.interfaces.repository.test_result_repository import TestResultRepository
from .unit_converter import PositionUnitConverter


class EOLStatisticsService:
    """
    EOL Force Test Statistics Service

    Provides comprehensive statistical analysis including:
    - Overview statistics (total tests, pass rate, duration)
    - Temperature-based Force statistics
    - Position-based Force statistics
    - 2D/3D/4D visualization data
    - Performance analysis
    - Test comparison
    """

    def __init__(self, repository: TestResultRepository):
        """
        Initialize EOL Statistics Service

        Args:
            repository: Test result repository for data access
        """
        self.repository = repository

    async def get_overview_statistics(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get overview statistics

        Args:
            filters: Filter criteria (date_range, status, etc.)

        Returns:
            Dictionary containing:
                - total_tests: Total number of tests
                - passed_tests: Number of passed tests
                - failed_tests: Number of failed tests
                - pass_rate: Pass rate percentage
                - avg_duration: Average test duration (seconds)
                - avg_max_force: Average maximum force (kgf)
                - force_range: [min_force, max_force]
        """
        try:
            # Get all tests from repository
            all_tests = await self.repository.get_all_tests()

            # Apply filters
            filtered_tests = self._apply_filters(all_tests, filters)

            if not filtered_tests:
                return self._empty_overview_statistics()

            # Calculate statistics
            total_tests = len(filtered_tests)
            passed_tests = sum(
                1 for test in filtered_tests if test.get("test_result", {}).get("is_passed", False)
            )
            failed_tests = total_tests - passed_tests
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0

            # Duration statistics
            durations = [
                test.get("duration_seconds", 0) for test in filtered_tests if "duration_seconds" in test
            ]
            avg_duration = float(np.mean(durations)) if durations else 0.0

            # Force statistics
            all_forces = []
            for test in filtered_tests:
                forces = self._extract_all_forces(test)
                all_forces.extend(forces)

            avg_max_force = float(np.mean(all_forces)) if all_forces else 0.0
            force_range = [float(np.min(all_forces)), float(np.max(all_forces))] if all_forces else [0.0, 0.0]

            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": round(pass_rate, 2),
                "avg_duration": round(avg_duration, 2),
                "avg_max_force": round(avg_max_force, 2),
                "force_range": [round(force_range[0], 2), round(force_range[1], 2)],
            }

        except Exception as e:
            logger.error(f"Error calculating overview statistics: {e}")
            return self._empty_overview_statistics()

    async def get_force_statistics_by_temperature(
        self, filters: Dict[str, Any], use_mm: bool = True
    ) -> Dict[float, Dict[str, Any]]:
        """
        Get Force statistics grouped by temperature

        Args:
            filters: Filter criteria
            use_mm: If True, convert position to mm; if False, keep μm

        Returns:
            Dictionary: {temperature: {position_key: {avg, std, min, max, count, position_mm, position_um}}}
            Example:
                {
                    38.0: {
                        "170.0": {
                            "avg": 11.52, "std": 0.45, "min": 10.85, "max": 12.18,
                            "count": 247, "position_mm": 170.0, "position_um": 170000.0
                        }
                    }
                }
        """
        try:
            all_tests = await self.repository.get_all_tests()
            filtered_tests = self._apply_filters(all_tests, filters)

            # Group by temperature
            temp_groups = {}

            for test in filtered_tests:
                measurements = test.get("test_result", {}).get("actual_results", {}).get("measurements", {})

                for temp_str, positions in measurements.items():
                    temp = float(temp_str)
                    if temp not in temp_groups:
                        temp_groups[temp] = {}

                    for position_str, data in positions.items():
                        position_um = float(position_str)
                        position_mm = PositionUnitConverter.um_to_mm(position_um)

                        # Create key based on use_mm
                        if use_mm:
                            key = f"{position_mm:.1f}"
                        else:
                            key = position_str

                        if key not in temp_groups[temp]:
                            temp_groups[temp][key] = {
                                "forces": [],
                                "position_um": position_um,
                                "position_mm": position_mm,
                            }

                        temp_groups[temp][key]["forces"].append(data["force"])

            # Calculate statistics
            statistics = {}
            for temp, positions in temp_groups.items():
                statistics[temp] = {}
                for key, data in positions.items():
                    forces = data["forces"]
                    statistics[temp][key] = {
                        "avg": float(np.mean(forces)),
                        "std": float(np.std(forces)),
                        "min": float(np.min(forces)),
                        "max": float(np.max(forces)),
                        "count": len(forces),
                        "position_mm": data["position_mm"],
                        "position_um": data["position_um"],
                    }

            return statistics

        except Exception as e:
            logger.error(f"Error calculating force statistics by temperature: {e}")
            return {}

    async def get_force_statistics_by_position(
        self, filters: Dict[str, Any], use_mm: bool = True
    ) -> Dict[float, Dict[str, Any]]:
        """
        Get Force statistics grouped by position

        Args:
            filters: Filter criteria
            use_mm: If True, use mm for keys; if False, use μm

        Returns:
            Dictionary: {position_mm: {temp_key: {avg, std, min, max, count}}}
        """
        try:
            all_tests = await self.repository.get_all_tests()
            filtered_tests = self._apply_filters(all_tests, filters)

            # Group by position
            position_groups = {}

            for test in filtered_tests:
                measurements = test.get("test_result", {}).get("actual_results", {}).get("measurements", {})

                for temp_str, positions in measurements.items():
                    for position_str, data in positions.items():
                        position_um = float(position_str)
                        position_mm = PositionUnitConverter.um_to_mm(position_um)

                        # Use mm as main key
                        if position_mm not in position_groups:
                            position_groups[position_mm] = {}

                        if temp_str not in position_groups[position_mm]:
                            position_groups[position_mm][temp_str] = []

                        position_groups[position_mm][temp_str].append(data["force"])

            # Calculate statistics
            statistics = {}
            for position_mm, temps in position_groups.items():
                statistics[position_mm] = {}
                for temp, forces in temps.items():
                    statistics[position_mm][temp] = {
                        "avg": float(np.mean(forces)),
                        "std": float(np.std(forces)),
                        "min": float(np.min(forces)),
                        "max": float(np.max(forces)),
                        "count": len(forces),
                    }

            return statistics

        except Exception as e:
            logger.error(f"Error calculating force statistics by position: {e}")
            return {}

    async def get_force_heatmap_data(
        self, filters: Dict[str, Any], use_mm: bool = True
    ) -> Dict[str, Any]:
        """
        Get data for Temperature × Position heat map

        Args:
            filters: Filter criteria
            use_mm: If True, positions in mm; if False, in μm

        Returns:
            Dictionary: {temperatures, positions_mm, positions_um, force_matrix}
        """
        try:
            stats_by_temp = await self.get_force_statistics_by_temperature(filters, use_mm)

            # Extract temperatures and positions
            temperatures = sorted(stats_by_temp.keys())

            # Collect all positions
            all_positions_data = []
            for temp_data in stats_by_temp.values():
                for pos_data in temp_data.values():
                    all_positions_data.append(
                        {"mm": pos_data["position_mm"], "um": pos_data["position_um"]}
                    )

            # Remove duplicates and sort
            unique_positions = {(p["mm"], p["um"]) for p in all_positions_data}
            sorted_positions = sorted(unique_positions, key=lambda x: x[0])

            positions_mm = [p[0] for p in sorted_positions]
            positions_um = [p[1] for p in sorted_positions]

            # Build force matrix
            force_matrix = []
            for temp in temperatures:
                row = []
                for pos_mm in positions_mm:
                    key = f"{pos_mm:.1f}"
                    if key in stats_by_temp[temp]:
                        row.append(stats_by_temp[temp][key]["avg"])
                    else:
                        row.append(None)
                force_matrix.append(row)

            return {
                "temperatures": temperatures,
                "positions_mm": positions_mm,
                "positions_um": positions_um,
                "force_matrix": force_matrix,
            }

        except Exception as e:
            logger.error(f"Error generating heat map data: {e}")
            return {
                "temperatures": [],
                "positions_mm": [],
                "positions_um": [],
                "force_matrix": [],
            }

    async def get_3d_scatter_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get 3D scatter plot data (all individual measurements)

        Returns:
            Dictionary: {temperatures, positions_mm, forces, test_ids}
        """
        try:
            all_tests = await self.repository.get_all_tests()
            filtered_tests = self._apply_filters(all_tests, filters)

            temperatures = []
            positions_mm = []
            forces = []
            test_ids = []

            for test in filtered_tests:
                test_id = test.get("test_id", "")
                measurements = test.get("test_result", {}).get("actual_results", {}).get("measurements", {})

                for temp_str, positions in measurements.items():
                    for position_str, data in positions.items():
                        temperatures.append(float(temp_str))
                        positions_mm.append(PositionUnitConverter.um_to_mm(float(position_str)))
                        forces.append(data["force"])
                        test_ids.append(test_id)

            return {
                "temperatures": temperatures,
                "positions_mm": positions_mm,
                "forces": forces,
                "test_ids": test_ids,
            }

        except Exception as e:
            logger.error(f"Error generating 3D scatter data: {e}")
            return {"temperatures": [], "positions_mm": [], "forces": [], "test_ids": []}

    async def get_4d_scatter_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get 4D scatter plot data (with time dimension)

        Returns:
            Dictionary: {temperatures, positions_mm, forces, timestamps, test_ids}
        """
        try:
            all_tests = await self.repository.get_all_tests()
            filtered_tests = self._apply_filters(all_tests, filters)

            temperatures = []
            positions_mm = []
            forces = []
            timestamps = []
            test_ids = []

            for test in filtered_tests:
                test_id = test.get("test_id", "")
                created_at_str = test.get("created_at", "")

                try:
                    created_at = datetime.fromisoformat(created_at_str)
                    timestamp = created_at.timestamp()
                except (ValueError, TypeError):
                    timestamp = 0.0

                measurements = test.get("test_result", {}).get("actual_results", {}).get("measurements", {})

                for temp_str, positions in measurements.items():
                    for position_str, data in positions.items():
                        temperatures.append(float(temp_str))
                        positions_mm.append(PositionUnitConverter.um_to_mm(float(position_str)))
                        forces.append(data["force"])
                        timestamps.append(timestamp)
                        test_ids.append(test_id)

            return {
                "temperatures": temperatures,
                "positions_mm": positions_mm,
                "forces": forces,
                "timestamps": timestamps,
                "test_ids": test_ids,
            }

        except Exception as e:
            logger.error(f"Error generating 4D scatter data: {e}")
            return {
                "temperatures": [],
                "positions_mm": [],
                "forces": [],
                "timestamps": [],
                "test_ids": [],
            }

    def _apply_filters(self, tests: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filter criteria to test list"""
        if not filters:
            return tests

        filtered = tests

        # Date range filter
        if "start_date" in filters and "end_date" in filters:
            try:
                start_date = datetime.fromisoformat(filters["start_date"])
                end_date = datetime.fromisoformat(filters["end_date"])

                filtered = [
                    test
                    for test in filtered
                    if start_date <= datetime.fromisoformat(test.get("created_at", "")) <= end_date
                ]
            except (ValueError, TypeError, KeyError):
                pass

        # Status filter
        if "status" in filters and filters["status"] != "All":
            status_filter = filters["status"].lower()
            filtered = [
                test
                for test in filtered
                if test.get("status", "").lower() == status_filter
            ]

        return filtered

    def _extract_all_forces(self, test: Dict[str, Any]) -> List[float]:
        """Extract all force values from a test"""
        forces = []
        measurements = test.get("test_result", {}).get("actual_results", {}).get("measurements", {})

        for temp_data in measurements.values():
            for position_data in temp_data.values():
                if "force" in position_data:
                    forces.append(position_data["force"])

        return forces

    def _empty_overview_statistics(self) -> Dict[str, Any]:
        """Return empty overview statistics"""
        return {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "pass_rate": 0.0,
            "avg_duration": 0.0,
            "avg_max_force": 0.0,
            "force_range": [0.0, 0.0],
        }
