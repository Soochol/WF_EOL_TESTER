#!/usr/bin/env python3
"""
ODA Power Supply Real Hardware Command Format Test

This script tests only command format validity with real ODA hardware.
Focuses on verifying that commands are properly formatted and accepted.
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.implementation.hardware.power.oda.oda_power import OdaPower


def setup_logging():
    """Setup detailed logging for command format verification"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )


async def test_oda_command_format():
    """Test ODA Power Supply command format validity with real hardware"""
    setup_logging()
    
    logger.info("=== ODA Power Command Format Test (Real Hardware) ===")
    logger.info("This test only verifies command format validity, not functionality")
    
    # Use actual hardware configuration
    config = {
        'host': '192.168.11.1',  # Real ODA IP
        'port': 5000,
        'timeout': 5.0,
        'channel': 1,
        'delimiter': '\n'  # LF delimiter
    }
    
    power = OdaPower(config)
    
    try:
        logger.info("Connecting to real ODA Power Supply...")
        
        # Test connection and basic commands
        await power.connect()
        logger.success("✅ Connection successful - command format accepted")
        
        # Test basic command format validity
        logger.info("Testing command format validity...")
        
        # Test 1: Get current status (read-only, safe)
        try:
            identity = await power.get_device_identity()
            logger.info(f"Device Identity: {identity}")
            logger.success("✅ *IDN? command format valid")
        except Exception as e:
            logger.error(f"❌ *IDN? command format issue: {e}")
        
        # Test 2: Check output status (read-only, safe)
        try:
            output_status = await power.is_output_enabled()
            logger.info(f"Output Status: {output_status}")
            logger.success("✅ OUTP? command format valid")
        except Exception as e:
            logger.error(f"❌ OUTP? command format issue: {e}")
        
        # Test 3: Get voltage (read-only, safe)
        try:
            voltage = await power.get_voltage()
            logger.info(f"Current Voltage: {voltage}V")
            logger.success("✅ MEAS:VOLT? command format valid")
        except Exception as e:
            logger.error(f"❌ MEAS:VOLT? command format issue: {e}")
        
        # Test 4: Get current (read-only, safe)
        try:
            current = await power.get_current()
            logger.info(f"Current: {current}A")
            logger.success("✅ MEAS:CURR? command format valid")
        except Exception as e:
            logger.error(f"❌ MEAS:CURR? command format issue: {e}")
        
        # Test 5: Safe voltage setting (minimal value)
        try:
            logger.info("Testing voltage setting command format (1V - safe value)...")
            await power.set_voltage(1.0)  # Very safe, low voltage
            logger.success("✅ VOLT command format valid")
        except Exception as e:
            logger.error(f"❌ VOLT command format issue: {e}")
        
        # Test 6: Safe current setting (minimal value)
        try:
            logger.info("Testing current setting command format (0.1A - safe value)...")
            await power.set_current_limit(0.1)  # Very safe, low current
            logger.success("✅ CURR command format valid")
        except Exception as e:
            logger.error(f"❌ CURR command format issue: {e}")
        
        logger.info("=== Command Format Test Results ===")
        logger.info("All command formats have been tested with real ODA hardware")
        logger.info("Check above logs for any format validation issues")
        
    except Exception as e:
        logger.error(f"Connection or command format error: {e}")
        return False
    
    finally:
        try:
            await power.disconnect()
            logger.info("Disconnected from ODA Power Supply")
        except Exception as e:
            logger.warning(f"Disconnect error: {e}")
    
    return True


async def main():
    """Main test execution"""
    logger.info("Starting ODA Power Supply Command Format Validation")
    logger.info("=" * 60)
    
    success = await test_oda_command_format()
    
    logger.info("=" * 60)
    if success:
        logger.success("Command format test completed - check logs for details")
    else:
        logger.error("Command format test failed - check connection and settings")
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)