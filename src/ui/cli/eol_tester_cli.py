"""
EOL Tester CLI

Simplified command-line interface for EOL testing operations.
"""

from typing import Dict, Optional

from loguru import logger

from application.use_cases.eol_force_test import (
    EOLForceTestCommand,
    EOLForceTestUseCase,
)
from domain.value_objects.dut_command_info import (
    DUTCommandInfo,
)
from domain.value_objects.eol_test_result import (
    EOLTestResult,
)


class EOLTesterCLI:
    """EOL 테스터 CLI 인터페이스"""

    def __init__(self, use_case: EOLForceTestUseCase):
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

            print("\n" + "=" * 60)
            print("EOL Tester - Simplified Version".center(60))
            print("=" * 60)

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
        print("\n" + "-" * 60)
        print("Main Menu")
        print("-" * 60)
        print("1. Execute EOL Test")
        print("2. Check Hardware Status")
        print("3. Exit")
        print("-" * 60)

        try:
            choice = input("Select option (1-3): ").strip()

            if choice == "1":
                await self._execute_eol_test()
            elif choice == "2":
                await self._check_hardware_status()
            elif choice == "3":
                self._running = False
                print("Exiting...")
            else:
                print("Invalid option. Please select 1-3.")

        except (KeyboardInterrupt, EOFError):
            self._running = False
            print("\\nExiting...")

    async def _execute_eol_test(self) -> None:
        """EOL 테스트 실행"""
        print("\\n" + "=" * 60)
        print("EOL Test")
        print("=" * 60)

        # DUT 정보 입력
        dut_info = await self._get_dut_info()
        if not dut_info:
            return

        # DUTCommandInfo 생성
        dut_command_info = DUTCommandInfo(
            dut_id=dut_info["id"],
            model_number=dut_info["model"],
            serial_number=dut_info["serial"],
            manufacturer="Unknown",
        )

        # 테스트 명령 생성
        command = EOLForceTestCommand(
            dut_info=dut_command_info,
            operator_id=dut_info["operator"],
        )

        await self._execute_test(command)

    async def _get_dut_info(
        self,
    ) -> Optional[Dict[str, str]]:
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
                "id": dut_id,
                "model": dut_model,
                "serial": dut_serial,
                "operator": operator,
            }

        except (KeyboardInterrupt, EOFError):
            return None

    async def _execute_test(self, command: EOLForceTestCommand) -> None:
        """테스트 실행"""
        print(f"\\nExecuting test for DUT: {command.dut_info.dut_id}")
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
        print("\\n" + "=" * 60)
        print("Test Result")
        print("=" * 60)
        print(f"Test ID: {result.test_id}")
        print(f"Status: {result.test_status}")
        print(f"Result: {'PASSED' if result.is_passed else 'FAILED'}")
        duration_str = result.format_duration()
        print(f"Duration: {duration_str}")

        # Check if test_summary is available and process it
        if hasattr(result, "test_summary") and result.test_summary:
            print("\\nTest Summary:")
            if isinstance(result.test_summary, dict):
                for (
                    key,
                    value,
                ) in result.test_summary.items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.3f}")
                    else:
                        print(f"  {key}: {value}")

        if result.error_message:
            print(f"\\nError: {result.error_message}")

        print("=" * 60)

    async def _check_hardware_status(self) -> None:
        """하드웨어 상태 확인"""
        print("\\n" + "=" * 60)
        print("Hardware Status")
        print("=" * 60)

        try:
            print("Hardware Status Check:")
            print("  Hardware status monitoring is integrated into test execution")
            print("  Individual hardware status can be checked during EOL test run")
            print("  Connection status is validated automatically before each test")

        except Exception as e:
            print(f"Failed to display hardware status info: {e}")
            logger.error(f"Hardware status display error: {e}")

        input("\\nPress Enter to continue...")

    async def _shutdown(self) -> None:
        """종료 처리"""
        logger.info("Shutting down CLI")

        try:
            # Hardware cleanup is handled by the use case internally
            # CLI shutdown complete - resources will be cleaned up by garbage collection
            logger.debug("CLI shutdown initiated - hardware cleanup handled internally")

        except Exception as e:
            logger.warning(f"Error during shutdown: {e}")

        logger.info("CLI shutdown complete")
