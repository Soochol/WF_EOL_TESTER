#!/usr/bin/env python3
"""
DIO Monitoring Service Verification Tool

Standalone tool for testing and verifying DIOMonitoringService functionality.
This tool can be used to check button press flow without running the full EOL tester.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger
from application.services.button_monitoring_service import DIOMonitoringService
from application.services.configuration_service import ConfigurationService
from infrastructure.configuration.yaml_configuration import YamlConfiguration
from infrastructure.configuration.json_profile_preference import JsonProfilePreference
from infrastructure.factory import ServiceFactory


class DIOVerificationTool:
    """Tool for verifying DIOMonitoringService functionality"""
    
    def __init__(self):
        self.digital_io_service = None
        self.hardware_config = None
        self.dio_monitoring_service = None
        
    async def setup(self):
        """Setup services for testing"""
        logger.info("🔧 TOOL_SETUP: Setting up verification tool...")
        
        try:
            # Create configuration services
            yaml_configuration = YamlConfiguration()
            profile_preference = JsonProfilePreference()
            configuration_service = ConfigurationService(
                configuration=yaml_configuration,
                profile_preference=profile_preference,
            )
            
            # Load hardware configuration
            logger.info("🔧 TOOL_SETUP: Loading hardware configuration...")
            self.hardware_config = await configuration_service.load_hardware_config()
            
            # Load hardware model for digital I/O service creation
            hardware_model = await yaml_configuration.load_hardware_model()
            hw_model_dict = hardware_model.to_dict()
            
            # Create digital I/O service
            logger.info("🔧 TOOL_SETUP: Creating Digital I/O service...")
            self.digital_io_service = ServiceFactory.create_digital_io_service(
                {"model": hw_model_dict["digital_io"]}
            )
            
            # Try to connect
            if not await self.digital_io_service.is_connected():
                logger.info("🔧 TOOL_SETUP: Connecting Digital I/O service...")
                await self.digital_io_service.connect()
            
            logger.info("✅ TOOL_SETUP: Setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ TOOL_SETUP: Setup failed: {e}")
            return False
    
    async def create_dio_service(self):
        """Create DIOMonitoringService for testing"""
        logger.info("🔧 TOOL_DIO: Creating DIOMonitoringService...")
        
        try:
            # Create test callbacks
            async def test_callback():
                logger.info("🎯 TEST_CALLBACK: Test button callback executed!")
                logger.info("🎯 TEST_CALLBACK: This would normally start an EOL test")
            
            async def test_emergency_callback():
                logger.critical("🚨 TEST_EMERGENCY: Test emergency callback executed!")
                logger.critical("🚨 TEST_EMERGENCY: This would normally execute emergency stop")
            
            # Create DIOMonitoringService
            self.dio_monitoring_service = DIOMonitoringService(
                digital_io_service=self.digital_io_service,
                hardware_config=self.hardware_config,
                eol_use_case=None,  # No EOL use case for testing
                callback=test_callback,
                emergency_stop_callback=test_emergency_callback,
            )
            
            logger.info("✅ TOOL_DIO: DIOMonitoringService created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ TOOL_DIO: Failed to create DIOMonitoringService: {e}")
            return False
    
    async def run_verification_tests(self):
        """Run comprehensive verification tests"""
        logger.info("🔍 VERIFICATION_TESTS: Starting verification tests...")
        
        if not self.dio_monitoring_service:
            logger.error("❌ VERIFICATION_TESTS: DIOMonitoringService not available")
            return False
        
        try:
            # Test 1: Print initial verification report
            logger.info("📋 TEST 1: Initial verification report")
            await self.dio_monitoring_service.print_verification_report()
            
            # Test 2: Start monitoring
            logger.info("📋 TEST 2: Starting monitoring service")
            await self.dio_monitoring_service.start_monitoring()
            
            # Wait a moment for monitoring to initialize
            await asyncio.sleep(1.0)
            
            # Test 3: Print verification report while monitoring
            logger.info("📋 TEST 3: Verification report while monitoring")
            await self.dio_monitoring_service.print_verification_report()
            
            # Test 4: Monitor for button presses (30 seconds)
            logger.info("📋 TEST 4: Monitoring for button presses (30 seconds)")
            logger.info("🎯 INSTRUCTION: Press buttons to test callback execution")
            logger.info("🎯 INSTRUCTION: Try single button, dual button, and emergency stop")
            
            for i in range(30):
                logger.info(f"⏱️ Monitoring... {30-i} seconds remaining")
                await asyncio.sleep(1.0)
            
            # Test 5: Final verification report
            logger.info("📋 TEST 5: Final verification report")
            await self.dio_monitoring_service.print_verification_report()
            
            # Test 6: Stop monitoring
            logger.info("📋 TEST 6: Stopping monitoring service")
            await self.dio_monitoring_service.stop_monitoring()
            
            logger.info("✅ VERIFICATION_TESTS: All tests completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ VERIFICATION_TESTS: Tests failed: {e}")
            return False
    
    async def run_continuous_monitoring(self, duration_seconds=60):
        """Run continuous monitoring for specified duration"""
        logger.info(f"🔄 CONTINUOUS_MONITORING: Starting {duration_seconds}s monitoring session...")
        
        if not self.dio_monitoring_service:
            logger.error("❌ CONTINUOUS_MONITORING: DIOMonitoringService not available")
            return False
        
        try:
            # Start monitoring
            await self.dio_monitoring_service.start_monitoring()
            
            # Print status every 10 seconds
            for i in range(0, duration_seconds, 10):
                remaining = duration_seconds - i
                logger.info(f"⏱️ CONTINUOUS_MONITORING: {remaining} seconds remaining...")
                
                # Print brief status
                status = await self.dio_monitoring_service.get_detailed_status()
                if "dual_button_condition" in status:
                    dual = status["dual_button_condition"]
                    logger.info(f"🎯 Button Status: Left={dual['left_pressed']}, Right={dual['right_pressed']}, Dual={dual['both_pressed']}")
                
                if "safety_conditions" in status:
                    safety = status["safety_conditions"]
                    logger.info(f"🔒 Safety Status: All OK={safety['all_satisfied']} (Clamp={safety['clamp_ok']}, Chain={safety['chain_ok']}, Door={safety['door_ok']})")
                
                await asyncio.sleep(10)
            
            # Stop monitoring
            await self.dio_monitoring_service.stop_monitoring()
            
            logger.info("✅ CONTINUOUS_MONITORING: Monitoring session completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ CONTINUOUS_MONITORING: Monitoring failed: {e}")
            return False


async def main():
    """Main entry point"""
    logger.info("🚀 DIO VERIFICATION TOOL: Starting...")
    
    tool = DIOVerificationTool()
    
    # Setup
    if not await tool.setup():
        logger.error("❌ Setup failed, exiting")
        sys.exit(1)
    
    # Create DIO service
    if not await tool.create_dio_service():
        logger.error("❌ DIO service creation failed, exiting")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            await tool.run_verification_tests()
        elif command == "monitor":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            await tool.run_continuous_monitoring(duration)
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Usage: python dio_verification_tool.py [test|monitor] [duration]")
    else:
        # Default: run verification tests
        await tool.run_verification_tests()
    
    logger.info("🏁 DIO VERIFICATION TOOL: Completed")


if __name__ == "__main__":
    asyncio.run(main())