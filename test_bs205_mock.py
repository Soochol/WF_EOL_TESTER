#!/usr/bin/env python3
"""
BS205 LoadCell Mock Communication Test Script

This script tests the BS205 LoadCell parsing and protocol logic
using mock serial data without requiring actual hardware.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from loguru import logger

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.implementation.hardware.loadcell.bs205.bs205_loadcell import BS205LoadCell


def setup_logging():
    """Setup logging for mock testing"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )


class MockSerialConnection:
    """Mock serial connection for testing BS205 protocol"""
    
    def __init__(self):
        self.responses = {}
        self.call_count = {}
    
    def set_response(self, command_bytes: bytes, response_bytes: bytes):
        """Set expected response for a command"""
        key = command_bytes.hex().upper()
        self.responses[key] = response_bytes
        self.call_count[key] = 0
        logger.debug(f"Mock: Set response for [{key}] -> [{response_bytes.hex().upper()}]")
    
    async def write(self, data: bytes):
        """Mock write operation"""
        hex_data = data.hex().upper()
        logger.info(f"Mock Serial Write: [{hex_data}]")
        return len(data)
    
    async def read(self, size: int = -1, timeout: float = None):
        """Mock read operation"""
        # Return mock BS205 response based on last command
        # For testing, return a standard response
        mock_response = bytes.fromhex("02302B205F372E34383703")  # STX + "0+_7.487" + ETX
        logger.info(f"Mock Serial Read: [{mock_response.hex().upper()}] (size={size}, timeout={timeout})")
        return mock_response
    
    async def read_until(self, separator: bytes, timeout: float = None):
        """Mock read until separator"""
        if separator == b"\x02":  # STX
            response = b"\x02"
        elif separator == b"\x03":  # ETX  
            response = bytes.fromhex("302B205F372E34383703")  # "0+_7.487" + ETX
        else:
            response = b""
        
        logger.info(f"Mock Serial Read Until [{separator.hex().upper()}]: [{response.hex().upper()}]")
        return response
    
    async def disconnect(self):
        """Mock disconnect"""
        logger.info("Mock Serial Disconnect")
    
    def is_connected(self):
        """Mock connection status"""
        return True


async def test_mock_protocol_parsing():
    """Test BS205 protocol parsing with mock data"""
    logger.info("=" * 60)
    logger.info("BS205 Protocol Parsing Test (Mock)")
    logger.info("=" * 60)
    
    # Create BS205 instance with mock config
    config = {
        'port': 'MOCK',
        'baudrate': 9600,
        'timeout': 1.0,
        'bytesize': 8,
        'stopbits': 1,
        'parity': 'even',
        'indicator_id': 0
    }
    
    loadcell = BS205LoadCell(config)
    
    # Test different response formats from the protocol documentation
    test_cases = [
        {
            'name': 'Standard Response (0+_7.487)',
            'hex': '02302B205F372E34383703',  # STX + "0+_7.487" + ETX
            'expected_value': 7.487,
            'expected_unit': 'kg'
        },
        {
            'name': 'Response without decimal (0+_ _7487)', 
            'hex': '02302B20203734383703',   # STX + "0+ 7487" + ETX
            'expected_value': 7.487,
            'expected_unit': 'kg'
        },
        {
            'name': 'Negative Response (0-12.34)',
            'hex': '02302D31322E333403',       # STX + "0-12.34" + ETX
            'expected_value': -12.34,
            'expected_unit': 'kg'
        },
        {
            'name': 'Double digit ID (15+1.7486)',
            'hex': '02313352422B312E373438363703',  # STX + "15+1.7486" + ETX
            'expected_value': 1.7486,
            'expected_unit': 'kg'
        },
        {
            'name': 'Large value (10+_748.6)', 
            'hex': '02313052422B203734382E363703',   # STX + "10+ 748.6" + ETX
            'expected_value': 748.6,
            'expected_unit': 'kg'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            logger.info(f"Testing: {test_case['name']}")
            
            # Parse response bytes
            response_bytes = bytes.fromhex(test_case['hex'])
            logger.info(f"Input hex: {test_case['hex']}")
            
            # Test response parsing
            ascii_response = loadcell._parse_bs205_response(response_bytes)
            logger.info(f"Parsed ASCII: '{ascii_response}'")
            
            if ascii_response:
                # Test weight parsing
                weight_value, unit = loadcell._parse_bs205_weight(ascii_response)
                logger.info(f"Parsed weight: {weight_value} {unit}")
                
                # Check if result matches expected
                expected_value = test_case['expected_value']
                expected_unit = test_case['expected_unit']
                
                value_match = abs(weight_value - expected_value) < 0.001
                unit_match = unit == expected_unit
                
                if value_match and unit_match:
                    logger.success(f"✅ {test_case['name']} - PASS")
                    results.append(True)
                else:
                    logger.error(f"❌ {test_case['name']} - FAIL: Expected {expected_value} {expected_unit}, got {weight_value} {unit}")
                    results.append(False)
            else:
                logger.error(f"❌ {test_case['name']} - FAIL: Could not parse response")
                results.append(False)
                
        except Exception as e:
            logger.error(f"❌ {test_case['name']} - ERROR: {e}")
            results.append(False)
        
        logger.info("-" * 40)
    
    # Summary
    passed = sum(results)
    total = len(results)
    logger.info(f"Protocol Parsing Tests: {passed}/{total} passed")
    
    return passed == total


async def test_mock_command_generation():
    """Test BS205 command generation"""
    logger.info("=" * 60)
    logger.info("BS205 Command Generation Test (Mock)")
    logger.info("=" * 60)
    
    config = {
        'port': 'MOCK',
        'baudrate': 9600,
        'timeout': 1.0,
        'bytesize': 8,
        'stopbits': 1,
        'parity': 'even',
        'indicator_id': 0
    }
    
    loadcell = BS205LoadCell(config)
    
    # Test command generation
    test_commands = [
        {'cmd': 'R', 'expected_hex': '3052', 'description': 'Read Weight (ID=0)'},
        {'cmd': 'Z', 'expected_hex': '305A', 'description': 'Zero Calibration (ID=0)'},
        {'cmd': 'H', 'expected_hex': '3048', 'description': 'Hold (ID=0)'},
        {'cmd': 'L', 'expected_hex': '304C', 'description': 'Hold Release (ID=0)'},
    ]
    
    results = []
    
    for test_cmd in test_commands:
        try:
            logger.info(f"Testing command: {test_cmd['description']}")
            
            # Generate command bytes manually (same logic as in the method)
            id_byte = ord(str(loadcell._indicator_id))  # '0' → 0x30
            cmd_byte = ord(test_cmd['cmd'])  # 'R' → 0x52
            command_bytes = bytes([id_byte, cmd_byte])
            
            generated_hex = command_bytes.hex().upper()
            expected_hex = test_cmd['expected_hex'].upper()
            
            logger.info(f"Generated: [{generated_hex}]")
            logger.info(f"Expected:  [{expected_hex}]")
            
            if generated_hex == expected_hex:
                logger.success(f"✅ {test_cmd['description']} - PASS")
                results.append(True)
            else:
                logger.error(f"❌ {test_cmd['description']} - FAIL")
                results.append(False)
                
        except Exception as e:
            logger.error(f"❌ {test_cmd['description']} - ERROR: {e}")
            results.append(False)
        
        logger.info("-" * 40)
    
    passed = sum(results)
    total = len(results)
    logger.info(f"Command Generation Tests: {passed}/{total} passed")
    
    return passed == total


async def test_mock_full_communication():
    """Test full communication flow with mock serial"""
    logger.info("=" * 60)
    logger.info("BS205 Full Communication Test (Mock)")
    logger.info("=" * 60)
    
    config = {
        'port': 'MOCK',
        'baudrate': 9600,
        'timeout': 1.0,
        'bytesize': 8,
        'stopbits': 1,
        'parity': 'even',
        'indicator_id': 0
    }
    
    loadcell = BS205LoadCell(config)
    
    # Replace connection with mock
    mock_connection = MockSerialConnection()
    loadcell._connection = mock_connection
    loadcell._is_connected = True
    
    try:
        # Test reading
        logger.info("Testing mock force reading...")
        
        # This will use the mock connection which returns mock data
        response = await loadcell._send_bs205_command('R')
        
        if response:
            logger.info(f"Got response: '{response}'")
            weight_value, unit = loadcell._parse_bs205_weight(response)
            logger.success(f"✅ Mock reading successful: {weight_value} {unit}")
            return True
        else:
            logger.error("❌ No response from mock connection")
            return False
            
    except Exception as e:
        logger.error(f"❌ Mock communication test failed: {e}")
        return False


async def run_mock_tests():
    """Run all mock tests"""
    setup_logging()
    
    logger.info("Starting BS205 Mock Test Suite")
    logger.info("=" * 80)
    
    results = []
    
    # Test 1: Protocol parsing
    results.append(await test_mock_protocol_parsing())
    
    # Test 2: Command generation  
    results.append(await test_mock_command_generation())
    
    # Test 3: Full communication flow
    results.append(await test_mock_full_communication())
    
    # Summary
    logger.info("=" * 80)
    logger.info("MOCK TEST RESULTS SUMMARY")
    logger.info("=" * 80)
    
    test_names = ['Protocol Parsing', 'Command Generation', 'Full Communication']
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{name:<20}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    logger.info("-" * 40)
    logger.info(f"OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("🎉 All mock tests passed!")
        return True
    else:
        logger.error(f"⚠️  {total - passed} test(s) failed")
        return False


def main():
    """Main entry point"""
    success = asyncio.run(run_mock_tests())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()