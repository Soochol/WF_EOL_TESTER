#!/usr/bin/env python3
"""
ODA Power Supply Delimiter Test Script

This script tests the ODA Power Supply delimiter functionality
with mock TCP communication to verify proper SCPI command formatting.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from loguru import logger

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.implementation.hardware.power.oda.oda_power import OdaPower
from driver.tcp.exceptions import TCPError


def setup_logging():
    """Setup logging for delimiter testing"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )


class MockTCPCommunication:
    """Mock TCP communication for testing ODA power delimiter functionality"""
    
    def __init__(self, host: str, port: int, timeout: float):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.is_connected = False
        
        # Storage for captured commands
        self.sent_commands = []
        self.query_commands = []
        
        # Mock responses
        self.responses = {
            "*IDN?": "ODA Technologies,EX-Series,2.1-1.0-1.6",
            "OUTP?": "0",  # Output OFF
            "VOLT?": "12.345",
            "CURR?": "5.000"
        }
    
    async def connect(self):
        """Mock connection"""
        self.is_connected = True
        logger.info(f"Mock TCP connected to {self.host}:{self.port}")
    
    async def disconnect(self):
        """Mock disconnection"""
        self.is_connected = False
        logger.info(f"Mock TCP disconnected from {self.host}:{self.port}")
        return True
    
    async def send_command(self, command: str):
        """Mock command sending - captures commands for verification"""
        logger.debug(f"Mock TCP send_command: {repr(command)}")
        self.sent_commands.append(command)
        
        # Simulate command processing
        await asyncio.sleep(0.01)
    
    async def query(self, command: str) -> str:
        """Mock query - captures commands and returns mock responses"""
        logger.debug(f"Mock TCP query: {repr(command)}")
        self.query_commands.append(command)
        
        # Extract base command without terminator for response lookup
        base_command = command.strip()
        if base_command in self.responses:
            response = self.responses[base_command]
            logger.debug(f"Mock TCP response: {repr(response)}")
            return response
        else:
            logger.warning(f"No mock response for command: {repr(base_command)}")
            return "OK"
    
    def get_last_sent_command(self) -> str:
        """Get the last sent command for verification"""
        return self.sent_commands[-1] if self.sent_commands else ""
    
    def get_last_query_command(self) -> str:
        """Get the last query command for verification"""
        return self.query_commands[-1] if self.query_commands else ""
    
    def clear_commands(self):
        """Clear captured commands"""
        self.sent_commands.clear()
        self.query_commands.clear()


async def test_delimiter_default():
    """Test default LF delimiter functionality"""
    logger.info("=== Testing Default LF Delimiter ===")
    
    config = {
        'host': '192.168.1.100',
        'port': 5000,
        'timeout': 5.0,
        'channel': 1,
        # delimiter not specified - should use default "\n"
    }
    
    power = OdaPower(config)
    
    # Replace TCP communication with mock
    mock_tcp = MockTCPCommunication(config['host'], config['port'], config['timeout'])
    power._tcp_comm = mock_tcp
    power._is_connected = True
    
    # Mock the connect check to return True
    await mock_tcp.connect()
    
    try:
        # Test voltage setting
        await power.set_voltage(12.345)
        last_command = mock_tcp.get_last_sent_command()
        logger.info(f"Voltage command sent: {repr(last_command)}")
        
        # Verify command format
        expected = "VOLT 12.345\n"
        if last_command == expected:
            logger.success("✅ Default delimiter test PASSED")
            return True
        else:
            logger.error(f"❌ Default delimiter test FAILED: expected {repr(expected)}, got {repr(last_command)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Default delimiter test ERROR: {e}")
        return False


async def test_delimiter_custom():
    """Test custom CRLF delimiter functionality"""
    logger.info("=== Testing Custom CRLF Delimiter ===")
    
    config = {
        'host': '192.168.1.100',
        'port': 5000,
        'timeout': 5.0,
        'channel': 1,
        'delimiter': '\r\n'  # Custom CRLF delimiter
    }
    
    power = OdaPower(config)
    
    # Replace TCP communication with mock
    mock_tcp = MockTCPCommunication(config['host'], config['port'], config['timeout'])
    power._tcp_comm = mock_tcp
    power._is_connected = True
    
    # Mock the connect check to return True
    await mock_tcp.connect()
    
    try:
        # Test current setting
        await power.set_current_limit(5.000)
        last_command = mock_tcp.get_last_sent_command()
        logger.info(f"Current command sent: {repr(last_command)}")
        
        # Verify command format
        expected = "CURR 5.000\r\n"
        if last_command == expected:
            logger.success("✅ Custom delimiter test PASSED")
            return True
        else:
            logger.error(f"❌ Custom delimiter test FAILED: expected {repr(expected)}, got {repr(last_command)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Custom delimiter test ERROR: {e}")
        return False


async def test_delimiter_null():
    """Test null delimiter (TCP driver handles terminator)"""
    logger.info("=== Testing Null Delimiter (TCP Driver) ===")
    
    config = {
        'host': '192.168.1.100',
        'port': 5000,
        'timeout': 5.0,
        'channel': 1,
        'delimiter': None  # Let TCP driver handle terminator
    }
    
    power = OdaPower(config)
    
    # Replace TCP communication with mock
    mock_tcp = MockTCPCommunication(config['host'], config['port'], config['timeout'])
    power._tcp_comm = mock_tcp
    power._is_connected = True
    
    # Mock the connect check to return True
    await mock_tcp.connect()
    
    try:
        # Test output enable
        await power.enable_output()
        last_command = mock_tcp.get_last_sent_command()
        logger.info(f"Output enable command sent: {repr(last_command)}")
        
        # With null delimiter, ODA Power now adds default LF for SCPI compatibility
        # TCP driver no longer adds terminators automatically
        expected = "OUTP ON\n"
        if last_command == expected:
            logger.success("✅ Null delimiter test PASSED")
            return True
        else:
            logger.error(f"❌ Null delimiter test FAILED: expected {repr(expected)}, got {repr(last_command)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Null delimiter test ERROR: {e}")
        return False


async def test_query_commands():
    """Test query commands with delimiters"""
    logger.info("=== Testing Query Commands ===")
    
    config = {
        'host': '192.168.1.100',
        'port': 5000,
        'timeout': 5.0,
        'channel': 1,
        'delimiter': '\n'  # Default LF
    }
    
    power = OdaPower(config)
    
    # Replace TCP communication with mock
    mock_tcp = MockTCPCommunication(config['host'], config['port'], config['timeout'])
    power._tcp_comm = mock_tcp
    power._is_connected = True
    
    # Mock the connect check to return True
    await mock_tcp.connect()
    
    results = []
    
    try:
        # Set the device identity first (normally set during connect)
        power._device_identity = "ODA Technologies,EX-Series,2.1-1.0-1.6"
        
        # Test IDN query (get_device_identity just returns stored value)
        identity = await power.get_device_identity()
        logger.info(f"IDN response: {identity}")
        
        # Since get_device_identity returns stored value, test direct command instead
        await power._send_command("*IDN?")
        last_query = mock_tcp.get_last_query_command()
        logger.info(f"IDN query sent: {repr(last_query)}")
        
        expected = "*IDN?\n"
        if last_query == expected:
            logger.success("✅ IDN query test PASSED")
            results.append(True)
        else:
            logger.error(f"❌ IDN query test FAILED: expected {repr(expected)}, got {repr(last_query)}")
            results.append(False)
        
        # Test output status query
        mock_tcp.clear_commands()
        is_enabled = await power.is_output_enabled()
        last_query = mock_tcp.get_last_query_command()
        logger.info(f"OUTP query sent: {repr(last_query)}")
        logger.info(f"Output enabled: {is_enabled}")
        
        expected = "OUTP?\n"
        if last_query == expected:
            logger.success("✅ OUTP query test PASSED")
            results.append(True)
        else:
            logger.error(f"❌ OUTP query test FAILED: expected {repr(expected)}, got {repr(last_query)}")
            results.append(False)
        
        return all(results)
        
    except Exception as e:
        logger.error(f"❌ Query commands test ERROR: {e}")
        return False


async def test_all_scpi_commands():
    """Test all major SCPI commands with proper formatting"""
    logger.info("=== Testing All SCPI Commands ===")
    
    config = {
        'host': '192.168.1.100',
        'port': 5000,
        'timeout': 5.0,
        'channel': 1,
        'delimiter': '\n'
    }
    
    power = OdaPower(config)
    
    # Replace TCP communication with mock
    mock_tcp = MockTCPCommunication(config['host'], config['port'], config['timeout'])
    power._tcp_comm = mock_tcp
    power._is_connected = True
    
    # Mock the connect check to return True
    await mock_tcp.connect()
    
    test_cases = [
        ("set_voltage(24.5)", "VOLT 24.500\n"),
        ("set_current_limit(3.2)", "CURR 3.200\n"),
        ("enable_output()", "OUTP ON\n"),
        ("disable_output()", "OUTP OFF\n"),
    ]
    
    results = []
    
    for test_name, expected_command in test_cases:
        try:
            mock_tcp.clear_commands()
            
            # Execute the command
            if "set_voltage" in test_name:
                await power.set_voltage(24.5)
            elif "set_current_limit" in test_name:
                await power.set_current_limit(3.2)
            elif "enable_output" in test_name:
                await power.enable_output()
            elif "disable_output" in test_name:
                await power.disable_output()
            
            last_command = mock_tcp.get_last_sent_command()
            logger.info(f"{test_name} sent: {repr(last_command)}")
            
            if last_command == expected_command:
                logger.success(f"✅ {test_name} PASSED")
                results.append(True)
            else:
                logger.error(f"❌ {test_name} FAILED: expected {repr(expected_command)}, got {repr(last_command)}")
                results.append(False)
                
        except Exception as e:
            logger.error(f"❌ {test_name} ERROR: {e}")
            results.append(False)
    
    return all(results)


async def run_all_tests():
    """Run complete delimiter test suite"""
    setup_logging()
    
    logger.info("Starting ODA Power Delimiter Test Suite")
    logger.info("=" * 60)
    
    test_results = []
    
    # Run all test cases
    test_results.append(await test_delimiter_default())
    test_results.append(await test_delimiter_custom())
    test_results.append(await test_delimiter_null())
    test_results.append(await test_query_commands())
    test_results.append(await test_all_scpi_commands())
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    test_names = [
        'Default LF Delimiter',
        'Custom CRLF Delimiter', 
        'Null Delimiter',
        'Query Commands',
        'All SCPI Commands'
    ]
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{name:<25}: {status}")
    
    passed = sum(test_results)
    total = len(test_results)
    
    logger.info("-" * 40)
    logger.info(f"OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("🎉 All delimiter tests passed!")
        return True
    else:
        logger.error(f"⚠️  {total - passed} test(s) failed")
        return False


def main():
    """Main entry point"""
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()