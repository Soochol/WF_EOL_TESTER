"""
Hardware Verification Service

Provides hardware verification and validation operations.
Extracted from HardwareServiceFacade for single responsibility compliance.
"""

import asyncio

from loguru import logger

from application.interfaces.hardware.mcu import MCUService
from domain.exceptions.eol_exceptions import HardwareOperationError
from domain.exceptions.hardware_exceptions import HardwareConnectionException
from domain.value_objects.test_configuration import TestConfiguration


class HardwareVerificationService:
    """
    Manages hardware verification and validation operations
    
    Provides verification services for hardware components, primarily temperature verification.
    """
    
    def __init__(
        self,
        mcu_service: MCUService,
    ):
        self._mcu = mcu_service

    async def verify_mcu_temperature(
        self, expected_temp: float, test_config: TestConfiguration
    ) -> None:
        """
        Verify MCU temperature is within acceptable range of expected value

        Uses MCU get_temperature() to read actual temperature and compares
        against expected value with configurable tolerance range.
        Includes retry logic: 10 additional attempts with 1-second delays if initial verification fails.

        Args:
            expected_temp: Expected temperature value (°C)
            test_config: Test configuration containing tolerance settings

        Raises:
            HardwareOperationError: If temperature verification fails after all retries
            HardwareConnectionException: If MCU temperature read fails consistently
        """
        logger.info(
            f"Verifying MCU temperature - Expected: {expected_temp}°C (±{test_config.temperature_tolerance}°C)"
        )

        max_retries = 10
        retry_delay = 1.0

        for attempt in range(max_retries + 1):  # 0-10 (11 total attempts)
            try:
                # Read actual temperature from MCU
                actual_temp = await self._mcu.get_temperature()

                # Calculate temperature difference
                temp_diff = abs(actual_temp - expected_temp)

                # Check if within tolerance
                is_within_tolerance = temp_diff <= test_config.temperature_tolerance

                if is_within_tolerance:
                    if attempt == 0:
                        logger.info(
                            f"✅ Temperature verification PASSED on first attempt - Actual: {actual_temp:.1f}°C, Expected: {expected_temp:.1f}°C, Diff: {temp_diff:.1f}°C (≤{test_config.temperature_tolerance:.1f}°C)"
                        )
                    else:
                        logger.info(
                            f"✅ Temperature verification PASSED on attempt {attempt + 1}/{max_retries + 1} - Actual: {actual_temp:.1f}°C, Expected: {expected_temp:.1f}°C, Diff: {temp_diff:.1f}°C (≤{test_config.temperature_tolerance:.1f}°C)"
                        )
                    return
                else:
                    if attempt < max_retries:
                        logger.warning(
                            f"❌ Temperature verification attempt {attempt + 1}/{max_retries + 1} failed - Actual: {actual_temp:.1f}°C, Expected: {expected_temp:.1f}°C, Diff: {temp_diff:.1f}°C (>{test_config.temperature_tolerance:.1f}°C) - Retrying in {retry_delay}s..."
                        )
                        await asyncio.sleep(retry_delay)
                    else:
                        # Final failure after all retries
                        error_msg = f"Temperature verification failed after {max_retries + 1} attempts - Final: {actual_temp:.1f}°C, Expected: {expected_temp:.1f}°C, Diff: {temp_diff:.1f}°C (>{test_config.temperature_tolerance:.1f}°C)"
                        logger.error(f"❌ {error_msg}")
                        raise HardwareOperationError(
                            device="mcu", operation="verify_temperature", reason=error_msg
                        )

            except HardwareOperationError:
                # Re-raise our own temperature verification failures
                raise
            except Exception as e:
                # Handle MCU communication errors
                if attempt < max_retries:
                    logger.warning(
                        f"⚠️  MCU communication error on attempt {attempt + 1}/{max_retries + 1} - {str(e)} - Retrying in {retry_delay}s..."
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    # Final communication failure after all retries
                    error_msg = f"MCU temperature verification failed after {max_retries + 1} attempts due to communication errors: {str(e)}"
                    logger.error(error_msg)
                    raise HardwareConnectionException(
                        error_msg,
                        details={
                            "expected_temp": expected_temp,
                            "tolerance": test_config.temperature_tolerance,
                            "final_error": str(e),
                            "attempts_made": max_retries + 1,
                        },
                    ) from e