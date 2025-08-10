"""
Test with actual JSON data from the system
"""

import asyncio
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

from application.services.repository_service import RepositoryService
from domain.entities.eol_test import EOLTest
from domain.entities.dut import DUT
from domain.entities.test_result import TestResult
from domain.enums.test_status import TestStatus
from domain.value_objects.identifiers import TestId, OperatorId, DUTId
from domain.value_objects.time_values import Timestamp


async def test_with_real_json():
    """Test using the latest JSON file from the system"""
    
    # Use the latest JSON file with force data
    json_file = Path("ResultsLog/DEFAULT001_20250810_115807_001.json")
    if not json_file.exists():
        print("❌ Test JSON file not found")
        return
    
    print(f"📄 Using JSON file: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # Create test entities
    test_id = TestId(test_data["test_id"])
    dut = DUT(
        dut_id=DUTId(test_data["dut"]["dut_id"]),
        model_number=test_data["dut"]["model_number"],
        serial_number=test_data["dut"]["serial_number"],
        manufacturer=test_data["dut"]["manufacturer"]
    )
    operator_id = OperatorId(test_data["operator_id"])
    
    # Create EOL test
    test = EOLTest(
        test_id=test_id,
        dut=dut,
        operator_id=operator_id
    )
    
    # Prepare and complete test with actual measurement data
    test.prepare_test(total_steps=1)
    test.start_execution()
    
    test_result = TestResult(
        test_id=test_id,
        test_status=TestStatus.COMPLETED,
        start_time=Timestamp.from_iso(test_data["test_result"]["start_time"]),
        end_time=Timestamp.from_iso(test_data["test_result"]["end_time"]),
        actual_results=test_data["test_result"]["actual_results"]
    )
    
    test.complete_test(test_result)
    
    # Show sample JSON data
    measurements = test_data["test_result"]["actual_results"]["measurements"]
    first_temp = list(measurements.keys())[0]
    first_pos = list(measurements[first_temp].keys())[0]
    sample_data = measurements[first_temp][first_pos]
    
    print(f"📊 Sample JSON data structure:")
    print(f"   Temperature: {first_temp}")
    print(f"   Position: {first_pos}")
    print(f"   Data: {sample_data}")
    print(f"   Force value: {sample_data.get('force', 'NOT FOUND')}")
    
    # Test the repository service
    repo_service = RepositoryService()
    
    try:
        # Clean up first
        if Path("TestResults").exists():
            import shutil
            shutil.rmtree("TestResults")
        
        print("🔧 Running CSV generation with enhanced debugging...")
        await repo_service._save_measurement_raw_data(test)
        
        # Check the generated CSV
        raw_files = list(Path("TestResults/raw_data").glob("*.csv"))
        if raw_files:
            csv_file = raw_files[0]
            print(f"✅ Generated CSV: {csv_file}")
            
            # Read and check CSV content
            with open(csv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Show first few data lines
            print("\n📊 CSV Content:")
            for i, line in enumerate(lines[:12]):
                print(f"{i+1:2d}: {line.rstrip()}")
            
            # Check for force data
            has_force_data = False
            force_count = 0
            for line in lines[8:]:  # Skip header
                if ',' in line and not line.startswith('#'):
                    values = line.strip().split(',')
                    if len(values) > 1:
                        force_values = [v.strip() for v in values[1:] if v.strip() and v.strip() != '']
                        if force_values:
                            has_force_data = True
                            force_count += len(force_values)
            
            print(f"\n📈 Results:")
            print(f"   Has force data: {'✅ YES' if has_force_data else '❌ NO'}")
            print(f"   Force values found: {force_count}")
            
        else:
            print("❌ No CSV file generated")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_with_real_json())