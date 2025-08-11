#!/usr/bin/env python3
"""
Test script for retry logic in Mock MCU
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from loguru import logger
from infrastructure.implementation.hardware.mcu.mock.mock_mcu import MockMCU

async def test_mock_mcu_retry():
    """Test the Mock MCU retry logic simulation"""
    logger.info("🧪 Testing Mock MCU timeout simulation and retry logic")
    
    # Create Mock MCU instance
    mock_mcu = MockMCU()
    
    try:
        # Connect to Mock MCU
        logger.info("Connecting to Mock MCU...")
        await mock_mcu.connect(
            port="COM9",
            baudrate=115200,
            timeout=10.0,
            bytesize=8,
            stopbits=1,
            parity=None
        )
        logger.info("✓ Mock MCU connected successfully")
        
        # Test start_standby_heating - first call should timeout
        logger.info("\n--- Testing start_standby_heating timeout simulation ---")
        
        for attempt in range(3):
            try:
                logger.info(f"\n🔄 Attempt {attempt + 1}: Calling start_standby_heating...")
                await mock_mcu.start_standby_heating(
                    operating_temp=60.0,
                    standby_temp=40.0,
                    hold_time_ms=10000
                )
                logger.info(f"✓ Attempt {attempt + 1}: SUCCESS - start_standby_heating completed")
                break
            except asyncio.TimeoutError as e:
                logger.error(f"❌ Attempt {attempt + 1}: TIMEOUT - {e}")
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1}: ERROR - {e}")
        
        logger.info("\n--- Test completed ---")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        # Cleanup
        if await mock_mcu.is_connected():
            await mock_mcu.disconnect()
            logger.info("Mock MCU disconnected")

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="DEBUG", format="{time:HH:mm:ss} | {level:8} | {name}:{function}:{line} - {message}")
    
    # Run the test
    asyncio.run(test_mock_mcu_retry())