"""
EOL Tester CLI

Simplified command-line interface for EOL testing operations.
"""

import asyncio
from typing import Optional
from loguru import logger

from application.use_cases.execute_eol_force_test import (
    ExecuteEOLTestUseCase, 
    ExecuteEOLTestCommand, 
    EOLTestResult
)
from domain.enums.test_types import TestType


class EOLTesterCLI:
    """EOL 테스터 CLI 인터페이스"""
    
    def __init__(self, use_case: ExecuteEOLTestUseCase):
        """
        초기화
        
        Args:
            use_case: EOL 테스트 실행 Use Case
        """
        self._use_case = use_case
        self._running = False
    
    async def run_interactive(self) -> None:
        """대화형 CLI 실행"""
        logger.info("Starting EOL Tester CLI")
        
        try:
            self._running = True
            
            print("\n" + "="*60)
            print("EOL Tester - Simplified Version".center(60))
            print("="*60)
            
            while self._running:
                await self._show_main_menu()
                
        except KeyboardInterrupt:
            print("\n\nExiting EOL Tester...")
            logger.info("CLI interrupted by user")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            logger.error(f"CLI error: {e}")
        finally:
            self._running = False
            await self._shutdown()
    
    async def _show_main_menu(self) -> None:
        """메인 메뉴 표시"""
        print("\n" + "-"*60)
        print("Main Menu")
        print("-"*60)
        print("1. Execute Force Test")
        print("2. Execute Electrical Test")
        print("3. Execute Comprehensive Test")
        print("4. Check Hardware Status")
        print("5. Exit")
        print("-"*60)
        
        try:
            choice = input("Select option (1-5): ").strip()
            
            if choice == "1":
                await self._execute_force_test()
            elif choice == "2":
                await self._execute_electrical_test()
            elif choice == "3":
                await self._execute_comprehensive_test()
            elif choice == "4":
                await self._check_hardware_status()
            elif choice == "5":
                self._running = False
                print("Exiting...")
            else:
                print("Invalid option. Please select 1-5.")
                
        except (KeyboardInterrupt, EOFError):
            self._running = False
            print("\\nExiting...")
    
    async def _execute_force_test(self) -> None:
        """힘 측정 테스트 실행"""
        print("\\n" + "="*60)
        print("Force Measurement Test")
        print("="*60)
        
        # DUT 정보 입력
        dut_info = await self._get_dut_info()
        if not dut_info:
            return
        
        # 테스트 명령 생성
        command = ExecuteEOLTestCommand(
            dut_id=dut_info['id'],
            dut_model=dut_info['model'],
            dut_serial=dut_info['serial'],
            test_type=TestType.FORCE_ONLY,
            operator_id=dut_info['operator'],
            pass_criteria={
                'force_min': 8.0,   # 최소 8N
                'force_max': 12.0   # 최대 12N
            }
        )
        
        await self._execute_test(command)
    
    async def _execute_electrical_test(self) -> None:
        """전기적 측정 테스트 실행"""
        print("\\n" + "="*60)
        print("Electrical Measurement Test")
        print("="*60)
        
        # DUT 정보 입력
        dut_info = await self._get_dut_info()
        if not dut_info:
            return
        
        # 전압/전류 설정 입력
        try:
            voltage = float(input("Target voltage (V) [12.0]: ") or "12.0")
            current = float(input("Current limit (A) [1.0]: ") or "1.0")
        except ValueError:
            print("Invalid voltage/current values")
            return
        
        # 테스트 명령 생성
        command = ExecuteEOLTestCommand(
            dut_id=dut_info['id'],
            dut_model=dut_info['model'],
            dut_serial=dut_info['serial'],
            test_type=TestType.ELECTRICAL_ONLY,
            operator_id=dut_info['operator'],
            test_config={
                'target_voltage': voltage,
                'current_limit': current
            },
            pass_criteria={
                'voltage_min': voltage * 0.95,  # ±5% 허용
                'voltage_max': voltage * 1.05,
                'current_max': current
            }
        )
        
        await self._execute_test(command)
    
    async def _execute_comprehensive_test(self) -> None:
        """종합 테스트 실행"""
        print("\\n" + "="*60)
        print("Comprehensive Test")
        print("="*60)
        
        # DUT 정보 입력
        dut_info = await self._get_dut_info()
        if not dut_info:
            return
        
        # 설정 입력
        try:
            voltage = float(input("Target voltage (V) [12.0]: ") or "12.0")
            current = float(input("Current limit (A) [1.0]: ") or "1.0")
        except ValueError:
            print("Invalid values")
            return
        
        # 테스트 명령 생성
        command = ExecuteEOLTestCommand(
            dut_id=dut_info['id'],
            dut_model=dut_info['model'],
            dut_serial=dut_info['serial'],
            test_type=TestType.COMPREHENSIVE,
            operator_id=dut_info['operator'],
            test_config={
                'target_voltage': voltage,
                'current_limit': current
            },
            pass_criteria={
                'force_min': 8.0,
                'force_max': 12.0,
                'voltage_min': voltage * 0.95,
                'voltage_max': voltage * 1.05,
                'current_max': current
            }
        )
        
        await self._execute_test(command)
    
    async def _get_dut_info(self) -> Optional[dict]:
        """DUT 정보 입력받기"""
        try:
            print("\\nEnter DUT Information:")
            dut_id = input("DUT ID: ").strip()
            if not dut_id:
                print("DUT ID is required")
                return None
            
            dut_model = input("DUT Model [Unknown]: ").strip() or "Unknown"
            dut_serial = input("DUT Serial [N/A]: ").strip() or "N/A"
            operator = input("Operator ID [Test]: ").strip() or "Test"
            
            return {
                'id': dut_id,
                'model': dut_model,
                'serial': dut_serial,
                'operator': operator
            }
            
        except (KeyboardInterrupt, EOFError):
            return None
    
    async def _execute_test(self, command: ExecuteEOLTestCommand) -> None:
        """테스트 실행"""
        print(f"\\nExecuting test for DUT: {command.dut_id}")
        print("Please wait...")
        
        try:
            # 테스트 실행
            result = await self._use_case.execute(command)
            
            # 결과 출력
            self._display_test_result(result)
            
        except Exception as e:
            print(f"\\nTest execution failed: {e}")
            logger.error(f"Test execution error: {e}")
        
        input("\\nPress Enter to continue...")
    
    def _display_test_result(self, result: EOLTestResult) -> None:
        """테스트 결과 출력"""
        print("\\n" + "="*60)
        print("Test Result")
        print("="*60)
        print(f"Test ID: {result.test_id}")
        print(f"Status: {result.status}")
        print(f"Result: {'PASSED' if result.passed else 'FAILED'}")
        print(f"Duration: {result.duration:.2f} seconds")
        
        if result.measurements:
            print("\\nMeasurements:")
            for key, value in result.measurements.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")
        
        if result.error_message:
            print(f"\\nError: {result.error_message}")
        
        print("="*60)
    
    async def _check_hardware_status(self) -> None:
        """하드웨어 상태 확인"""
        print("\\n" + "="*60)
        print("Hardware Status")
        print("="*60)
        
        try:
            # LoadCell 상태
            loadcell_status = await self._use_case._loadcell.get_status()
            print("LoadCell Status:")
            for key, value in loadcell_status.items():
                print(f"  {key}: {value}")
            
            print()
            
            # Power Supply 상태
            power_status = await self._use_case._power.get_status()
            print("Power Supply Status:")
            for key, value in power_status.items():
                print(f"  {key}: {value}")
                
        except Exception as e:
            print(f"Failed to get hardware status: {e}")
            logger.error(f"Hardware status error: {e}")
        
        input("\\nPress Enter to continue...")
    
    async def _shutdown(self) -> None:
        """종료 처리"""
        logger.info("Shutting down CLI")
        
        try:
            # 하드웨어 연결 해제
            if hasattr(self._use_case, '_loadcell'):
                await self._use_case._loadcell.disconnect()
            
            if hasattr(self._use_case, '_power'):
                await self._use_case._power.disconnect()
                
        except Exception as e:
            logger.warning(f"Error during shutdown: {e}")
        
        logger.info("CLI shutdown complete")