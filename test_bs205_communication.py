#!/usr/bin/env python3
"""
BS205 LoadCell Communication Test Script

This script tests the BS205 LoadCell communication protocol
with detailed logging and error handling.
"""

import asyncio
import logging
import sys
import yaml
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.implementation.hardware.loadcell.bs205.bs205_loadcell import BS205LoadCell
from loguru import logger


def setup_logging():
    """Setup detailed logging for BS205 testing"""
    # Remove default handler
    logger.remove()
    
    # Add console handler with detailed format
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )
    
    # Add file handler for detailed logs
    logger.add(
        "bs205_test.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB"
    )


def load_hardware_config():
    """Load hardware configuration from YAML file"""
    try:
        config_path = Path("configuration/hardware.yaml")
        if not config_path.exists():
            logger.error(f"Hardware config file not found: {config_path}")
            return None
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        loadcell_config = config.get('hardware_config', {}).get('loadcell', {})
        logger.info(f"Loaded LoadCell config: {loadcell_config}")
        return loadcell_config
        
    except Exception as e:
        logger.error(f"Failed to load hardware config: {e}")
        return None


async def test_bs205_connection(config):
    """Test BS205 LoadCell connection"""
    logger.info("=" * 60)
    logger.info("BS205 LoadCell Connection Test")
    logger.info("=" * 60)
    
    loadcell = None
    try:
        # Create BS205 LoadCell instance
        logger.info("Creating BS205 LoadCell instance...")
        loadcell = BS205LoadCell(config)
        
        # Test connection
        logger.info("Testing connection...")
        await loadcell.connect()
        
        if await loadcell.is_connected():
            logger.success("✅ Connection successful!")
            return loadcell
        else:
            logger.error("❌ Connection failed - is_connected() returned False")
            return None
            
    except Exception as e:
        logger.error(f"❌ Connection failed with exception: {e}")
        return None


async def test_bs205_reading(loadcell):
    """Test BS205 LoadCell reading"""
    logger.info("=" * 60)
    logger.info("BS205 LoadCell Reading Test")
    logger.info("=" * 60)
    
    try:
        # Single reading test
        logger.info("Testing single force reading...")
        force_value = await loadcell.read_force()
        logger.success(f"✅ Force reading successful: {force_value.value} {force_value.unit.value}")
        
        # Multiple readings test
        logger.info("Testing multiple readings (3 samples)...")
        for i in range(3):
            try:
                force_value = await loadcell.read_force()
                logger.info(f"Reading {i+1}: {force_value.value} {force_value.unit.value}")
                await asyncio.sleep(0.5)  # Wait between readings
            except Exception as e:
                logger.error(f"Reading {i+1} failed: {e}")
        
        # Raw value test
        logger.info("Testing raw value reading...")
        raw_value = await loadcell.read_raw_value()
        logger.success(f"✅ Raw value reading successful: {raw_value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Reading test failed: {e}")
        return False


async def test_bs205_zero(loadcell):
    """Test BS205 LoadCell zero calibration"""
    logger.info("=" * 60)
    logger.info("BS205 LoadCell Zero Calibration Test")
    logger.info("=" * 60)
    
    try:
        logger.info("Testing zero calibration...")
        success = await loadcell.zero()
        
        if success:
            logger.success("✅ Zero calibration successful!")
            return True
        else:
            logger.warning("⚠️ Zero calibration returned False")
            return False
            
    except Exception as e:
        logger.error(f"❌ Zero calibration failed: {e}")
        return False


async def test_bs205_status(loadcell):
    """Test BS205 LoadCell status"""
    logger.info("=" * 60)
    logger.info("BS205 LoadCell Status Test")
    logger.info("=" * 60)
    
    try:
        logger.info("Getting device status...")
        status = await loadcell.get_status()
        
        logger.info("Device Status:")
        for key, value in status.items():
            logger.info(f"  {key}: {value}")
            
        logger.success("✅ Status retrieval successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Status test failed: {e}")
        return False


async def test_bs205_sampling(loadcell):
    """Test BS205 LoadCell multiple sampling"""
    logger.info("=" * 60)
    logger.info("BS205 LoadCell Multiple Sampling Test")
    logger.info("=" * 60)
    
    try:
        logger.info("Testing multiple sampling (5 samples, 200ms interval)...")
        samples = await loadcell.read_multiple_samples(count=5, interval_ms=200)
        
        logger.info(f"Collected {len(samples)} samples:")
        for i, sample in enumerate(samples):
            logger.info(f"  Sample {i+1}: {sample}")
            
        if samples:
            avg = sum(samples) / len(samples)
            logger.info(f"Average: {avg:.3f}")
            logger.success("✅ Multiple sampling successful!")
            return True
        else:
            logger.error("❌ No samples collected")
            return False
            
    except Exception as e:
        logger.error(f"❌ Multiple sampling failed: {e}")
        return False


async def run_full_test():
    """Run complete BS205 LoadCell test suite"""
    setup_logging()
    
    logger.info("Starting BS205 LoadCell Test Suite")
    logger.info("=" * 80)
    
    # Load configuration
    config = load_hardware_config()
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return False
    
    loadcell = None
    test_results = {
        'connection': False,
        'reading': False,
        'zero': False,
        'status': False,
        'sampling': False
    }
    
    try:
        # Test 1: Connection
        loadcell = await test_bs205_connection(config)
        test_results['connection'] = loadcell is not None
        
        if not loadcell:
            logger.error("Cannot proceed without connection. Exiting.")
            return False
        
        # Test 2: Reading
        test_results['reading'] = await test_bs205_reading(loadcell)
        
        # Test 3: Zero calibration
        test_results['zero'] = await test_bs205_zero(loadcell)
        
        # Test 4: Status
        test_results['status'] = await test_bs205_status(loadcell)
        
        # Test 5: Multiple sampling
        test_results['sampling'] = await test_bs205_sampling(loadcell)
        
    except Exception as e:
        logger.error(f"Test suite failed with exception: {e}")
    
    finally:
        # Cleanup
        if loadcell:
            try:
                await loadcell.disconnect()
                logger.info("LoadCell disconnected")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
    
    # Print test results summary
    logger.info("=" * 80)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name.upper():<12}: {status}")
    
    logger.info("-" * 40)
    logger.info(f"OVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.success("🎉 All tests passed!")
        return True
    else:
        logger.error(f"⚠️  {total_tests - passed_tests} test(s) failed")
        return False


async def interactive_test():
    """Interactive test mode for manual testing"""
    setup_logging()
    
    config = load_hardware_config()
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return
    
    loadcell = await test_bs205_connection(config)
    if not loadcell:
        logger.error("Connection failed. Exiting.")
        return
    
    logger.info("=" * 60)
    logger.info("Interactive BS205 Test Mode")
    logger.info("Commands: read, zero, status, hold, release, quit")
    logger.info("=" * 60)
    
    try:
        while True:
            try:
                cmd = input("\nEnter command: ").strip().lower()
                
                if cmd == 'quit' or cmd == 'q':
                    break
                elif cmd == 'read' or cmd == 'r':
                    force = await loadcell.read_force()
                    print(f"Force: {force.value} {force.unit.value}")
                elif cmd == 'zero' or cmd == 'z':
                    success = await loadcell.zero()
                    print(f"Zero calibration: {'Success' if success else 'Failed'}")
                elif cmd == 'status' or cmd == 's':
                    status = await loadcell.get_status()
                    for k, v in status.items():
                        print(f"  {k}: {v}")
                elif cmd == 'hold' or cmd == 'h':
                    success = await loadcell.hold()
                    print(f"Hold setting: {'Success' if success else 'Failed'}")
                elif cmd == 'release' or cmd == 'rel':
                    success = await loadcell.hold_release()
                    print(f"Hold release: {'Success' if success else 'Failed'}")
                else:
                    print("Unknown command. Available: read, zero, status, hold, release, quit")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Command failed: {e}")
    
    finally:
        await loadcell.disconnect()
        logger.info("Disconnected.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        asyncio.run(interactive_test())
    else:
        success = asyncio.run(run_full_test())
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()