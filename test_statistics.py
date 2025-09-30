"""
Test script for Statistics page functionality
"""

import asyncio
from pathlib import Path
from src.infrastructure.implementation.repositories.json_result_repository import JsonResultRepository
from src.application.services.statistics.eol_statistics_service import EOLStatisticsService


async def test_statistics_service():
    """Test the statistics service with real data"""
    print("=" * 60)
    print("Testing EOL Statistics Service")
    print("=" * 60)

    # Initialize repository
    data_dir = Path("logs/test_results/json")
    print(f"\nData directory: {data_dir}")
    print(f"Data directory exists: {data_dir.exists()}")

    repository = JsonResultRepository(data_dir=str(data_dir), auto_save=False)

    # Initialize service
    service = EOLStatisticsService(repository=repository)

    # Test results are loaded automatically through repository
    print("\n1. Testing data access...")

    # Test overview statistics
    print("\n2. Getting overview statistics...")
    overview = await service.get_overview_statistics(filters={})
    print(f"   Total tests: {overview['total_tests']}")
    print(f"   Passed tests: {overview['passed_tests']}")
    print(f"   Failed tests: {overview['failed_tests']}")
    print(f"   Pass rate: {overview['pass_rate']}%")
    print(f"   Avg duration: {overview['avg_duration']}s")
    print(f"   Avg force: {overview['avg_max_force']}N")

    # Test force by temperature
    print("\n3. Getting force statistics by temperature...")
    temp_stats = await service.get_force_statistics_by_temperature(filters={})
    for temp, positions in sorted(temp_stats.items()):
        print(f"   Temperature {temp}°C:")
        for pos_key, stats in positions.items():
            print(f"     Position {pos_key}mm: avg={stats['avg']:.2f}N, std={stats['std']:.2f}N")

    # Test force by position
    print("\n4. Getting force statistics by position...")
    pos_stats = await service.get_force_statistics_by_position(filters={})
    for pos, temps in sorted(pos_stats.items()):
        print(f"   Position {pos}mm:")
        for temp, stats in temps.items():
            print(f"     Temperature {temp}°C: avg={stats['avg']:.2f}N, std={stats['std']:.2f}N")

    # Test heatmap data
    print("\n5. Getting heatmap data...")
    heatmap_data = await service.get_force_heatmap_data(filters={})
    print(f"   Heatmap data points: {len(heatmap_data)}")

    # Test 3D scatter data
    print("\n6. Getting 3D scatter data...")
    scatter_data = await service.get_3d_scatter_data(filters={})
    print(f"   Scatter data points: {len(scatter_data)}")

    # Test 4D scatter data
    print("\n7. Getting 4D scatter data...")
    scatter_4d_data = await service.get_4d_scatter_data(filters={})
    print(f"   4D scatter data points: {len(scatter_4d_data)}")

    print("\n" + "=" * 60)
    print("All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_statistics_service())