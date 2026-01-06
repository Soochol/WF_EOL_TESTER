"""
EOL Force Test Sequence

This sequence implements the End-of-Line force testing protocol.
Supports both standalone (mock hardware) and integrated (real hardware via main project) modes.

When station-service-sdk is available, it uses the SDK framework.
When running standalone without SDK, it provides its own minimal implementation.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from loguru import logger

# Try to import station-service-sdk (optional dependency)
_SDK_AVAILABLE = False
try:
    from station_service_sdk import (
        SequenceBase,
        RunResult,
        ExecutionContext,
        SetupError,
        TeardownError,
        StepError,
        HardwareConnectionError,
        register_sequence,
    )
    _SDK_AVAILABLE = True
except ImportError:
    # SDK not available - provide minimal standalone implementations
    from dataclasses import dataclass, field
    from typing import Callable

    RunResult = Dict[str, Any]

    @dataclass
    class ExecutionContext:
        """Minimal execution context for standalone mode."""
        execution_id: str = "standalone"
        serial_number: str = "UNKNOWN"
        wip_id: str = ""
        parameters: Dict[str, Any] = field(default_factory=dict)

    class SetupError(Exception):
        """Setup phase error."""
        pass

    class TeardownError(Exception):
        """Teardown phase error."""
        pass

    class StepError(Exception):
        """Step execution error."""
        def __init__(self, message: str, step_name: str = ""):
            super().__init__(message)
            self.step_name = step_name

    class HardwareConnectionError(Exception):
        """Hardware connection error."""
        pass

    class SequenceBase:
        """Minimal SequenceBase for standalone mode."""
        name = "sequence"
        version = "1.0.0"
        description = ""

        def __init__(self, context: ExecutionContext, **kwargs):
            self.context = context
            self._last_error: Optional[str] = None

        @property
        def last_error(self) -> Optional[str]:
            return self._last_error

        def get_parameter(self, name: str, default: Any = None) -> Any:
            return self.context.parameters.get(name, default)

        def check_abort(self) -> None:
            pass

        def emit_log(self, level: str, message: str) -> None:
            getattr(logger, level.lower(), logger.info)(message)

        def emit_error(self, code: str, message: str, recoverable: bool = False) -> None:
            logger.error(f"[{code}] {message}")
            self._last_error = message

        def emit_step_start(self, name: str, index: int, total: int, description: str = "") -> None:
            logger.info(f"Step {index}/{total}: {name} - {description}")

        def emit_step_complete(
            self,
            name: str,
            index: int,
            passed: bool,
            duration: float = 0.0,
            error: str = "",
            measurements: Dict[str, Any] = None,
            data: Dict[str, Any] = None,
        ) -> None:
            status = "PASS" if passed else "FAIL"
            logger.info(f"Step {index} {name}: {status} ({duration:.2f}s)")
            if error:
                logger.error(f"  Error: {error}")
            if measurements:
                for m_name, m_data in measurements.items():
                    logger.info(f"  Measurement {m_name}: {m_data}")

        def emit_measurement(self, name: str, value: float, unit: str = "", min_value: float = None, max_value: float = None) -> None:
            logger.info(f"Measurement {name}: {value} {unit}")

        async def _execute(self) -> RunResult:
            """Execute the full sequence lifecycle."""
            try:
                await self.setup()
                result = await self.run()
                await self.teardown()
                return result
            except Exception as e:
                self._last_error = str(e)
                try:
                    await self.teardown()
                except Exception:
                    pass
                raise

        async def setup(self) -> None:
            pass

        async def run(self) -> RunResult:
            return {"passed": True}

        async def teardown(self) -> None:
            pass

        @classmethod
        def run_from_cli(cls) -> int:
            """Run sequence from command line."""
            import asyncio
            context = ExecutionContext()
            sequence = cls(context)
            try:
                result = asyncio.run(sequence._execute())
                return 0 if result.get("passed", False) else 1
            except Exception as e:
                logger.error(f"Sequence failed: {e}")
                return 1

    def register_sequence(cls):
        """No-op decorator for standalone mode."""
        return cls

# Standalone imports (self-contained)
from .domain.value_objects import DUTCommandInfo, TestConfiguration, HardwareConfig

if TYPE_CHECKING:
    from .hardware_adapter import EOLHardwareAdapter


class EOLForceTestSequence(SequenceBase):
    """
    End-of-Line Force Test Sequence

    This sequence performs comprehensive force testing across multiple
    temperatures and stroke positions for wafer fabrication devices.

    Test Flow:
    1. Setup: Connect hardware, initialize, power on, MCU boot (auto-emitted by SDK)
    2. Run: Execute temperature/position matrix measurements
    3. Teardown: Safe shutdown and cleanup (auto-emitted by SDK)

    Note: SDK automatically handles setup/teardown step emissions.
    Total steps = run steps + 2 (setup at step 0, teardown at last)
    """

    name = "eol_force_test"
    version = "1.0.0"
    description = "End-of-Line force test sequence for WF devices"

    def __init__(
        self,
        context: ExecutionContext,
        hardware_adapter: Optional["EOLHardwareAdapter"] = None,
        **kwargs: Any,
    ):
        """
        Initialize the EOL Force Test sequence.

        Args:
            context: Execution context from station-service-sdk
            hardware_adapter: Pre-configured hardware adapter (optional)
            **kwargs: Additional arguments passed to SequenceBase
        """
        super().__init__(context, **kwargs)

        self._hardware: Optional["EOLHardwareAdapter"] = hardware_adapter
        self._dut_info: Optional["DUTCommandInfo"] = None
        self._test_passed = False
        self._measurements: Dict[str, Any] = {}
        self._cycle_results: List[Any] = []

        # Get parameters using SDK utility method
        self.stop_on_failure = self.get_parameter("stop_on_failure", True)

    @property
    def hardware(self) -> "EOLHardwareAdapter":
        """Get the hardware adapter (raises if not initialized)."""
        if self._hardware is None:
            raise SetupError("Hardware adapter not initialized")
        return self._hardware

    async def setup(self) -> None:
        """
        Setup phase: Initialize hardware and prepare for testing.

        Note: SDK automatically emits step_start/complete for setup (lifecycle: true).
        Do NOT manually emit steps here - just perform setup logic.
        """
        self.emit_log("info", "Starting EOL Force Test setup...")

        try:
            # Initialize hardware adapter if not provided
            if self._hardware is None:
                self.emit_log("info", "Initializing hardware adapter...")
                self._hardware = await self._create_hardware_adapter()
                self.emit_log("info", "Hardware adapter initialized")

            # Check for abort request
            self.check_abort()

            # Connect to hardware
            self.emit_log("info", "Connecting to hardware devices...")
            await self.hardware.connect()

            # Log hardware status
            status = await self.hardware.get_hardware_status()
            self.emit_log("info", f"Hardware status: {status}")

            # Check for abort request
            self.check_abort()

            # Initialize hardware
            self.emit_log("info", "Initializing hardware parameters...")
            await self.hardware.initialize()
            self.emit_log("info", "Hardware parameters initialized")

            # Check for abort request
            self.check_abort()

            # Setup test (power on, MCU boot, LMA standby)
            self.emit_log("info", "Setting up test environment...")
            await self.hardware.setup_test()
            self.emit_log("info", "Test environment setup complete")

            # Create DUT info from context
            self._dut_info = self._create_dut_info()
            self.emit_log("info", f"DUT: {self._dut_info.serial_number}")

            self.emit_log("info", "EOL Force Test setup completed successfully")

        except HardwareConnectionError as e:
            self.emit_error("HARDWARE_CONNECTION", str(e), recoverable=False)
            raise SetupError(f"Hardware connection failed: {e}") from e
        except Exception as e:
            self.emit_error("SETUP_ERROR", str(e), recoverable=False)
            raise SetupError(f"Setup failed: {e}") from e

    async def run(self) -> RunResult:
        """
        Run phase: Execute the force test sequence.

        Note: Run steps start from index 1 (setup is step 0, managed by SDK).
        Total run steps = 1 (force_test)
        """
        self.emit_log("info", "Starting EOL Force Test execution...")

        test_config = self.hardware.test_config
        total_temps = len(test_config.temperature_list)
        total_positions = len(test_config.stroke_positions)
        total_measurements = total_temps * total_positions
        repeat_count = test_config.repeat_count

        # Total run steps: 1 (force_test)
        total_run_steps = 1

        self.emit_log(
            "info",
            f"Test matrix: {total_temps} temps x {total_positions} positions x {repeat_count} repeats = {total_measurements * repeat_count} measurements",
        )

        try:
            # Check for abort request
            self.check_abort()

            # Step 1: Execute force test sequence
            self.emit_step_start(
                "force_test",
                1,
                total_run_steps,
                f"Executing force test ({total_measurements * repeat_count} measurements)",
            )

            try:
                measurements, cycle_results = await self.hardware.execute_force_test(
                    self._dut_info,
                )

                self._measurements = measurements.to_dict() if hasattr(measurements, 'to_dict') else {}
                self._cycle_results = cycle_results

                # Build step measurements for emit_step_complete
                step_measurements = self._build_step_measurements(measurements)

                # Emit measurement events
                await self._emit_test_measurements(measurements)

                # Evaluate results
                self._test_passed = self._evaluate_results(measurements)

                self.emit_step_complete(
                    "force_test",
                    1,
                    self._test_passed,
                    test_config.estimate_test_duration_seconds(),
                    measurements=step_measurements,
                )

            except Exception as e:
                self.emit_step_complete(
                    "force_test",
                    1,
                    False,
                    0.0,
                    error=str(e),
                )
                if self.stop_on_failure:
                    self.emit_log("warning", f"Force test failed, stopping: {e}")
                    return {
                        "passed": False,
                        "measurements": self._measurements,
                        "data": {"stopped_at": "force_test", "error": str(e)},
                    }
                raise

            self.emit_log(
                "info",
                f"Force test completed: {'PASS' if self._test_passed else 'FAIL'}",
            )

            return {
                "passed": self._test_passed,
                "measurements": self._measurements,
                "data": {
                    "cycle_count": len(cycle_results),
                    "temperature_count": total_temps,
                    "position_count": total_positions,
                    "repeat_count": repeat_count,
                },
            }

        except StepError:
            raise
        except Exception as e:
            self.emit_error("TEST_EXECUTION", str(e), recoverable=False)
            raise StepError(f"Force test execution failed: {e}", step_name="force_test") from e

    async def teardown(self) -> None:
        """
        Teardown phase: Safely shutdown hardware.

        Note: SDK automatically emits step_start/complete for teardown (lifecycle: true).
        Uses error accessors to check for previous errors and handle accordingly.
        """
        self.emit_log("info", "Starting EOL Force Test teardown...")

        # Check for errors in previous phases using SDK error accessors
        if self.last_error:
            self.emit_log("warning", f"Previous error detected: {self.last_error}")
            # Collect additional diagnostics on failure
            if self._hardware is not None:
                try:
                    status = await self.hardware.get_hardware_status()
                    self.emit_log("debug", f"Hardware status at teardown: {status}")
                except Exception as diag_error:
                    self.emit_log("debug", f"Failed to get diagnostics: {diag_error}")

        errors = []

        try:
            if self._hardware is not None:
                # Teardown test (return to safe state)
                try:
                    self.emit_log("info", "Tearing down test...")
                    await self.hardware.teardown_test()
                    self.emit_log("info", "Test teardown complete")
                except Exception as e:
                    errors.append(f"Teardown test failed: {e}")
                    self.emit_log("warning", f"Teardown test error: {e}")

                # Disconnect hardware
                try:
                    self.emit_log("info", "Disconnecting hardware...")
                    await self.hardware.disconnect()
                    self.emit_log("info", "Hardware disconnected")
                except Exception as e:
                    errors.append(f"Hardware disconnect failed: {e}")
                    self.emit_log("warning", f"Disconnect error: {e}")

            self.emit_log("info", "EOL Force Test teardown completed")

            if errors:
                raise TeardownError(f"Teardown completed with errors: {'; '.join(errors)}")

        except TeardownError:
            raise
        except Exception as e:
            self.emit_error("TEARDOWN_ERROR", str(e), recoverable=False)
            raise TeardownError(f"Teardown failed: {e}") from e

    async def _create_hardware_adapter(self) -> "EOLHardwareAdapter":
        """Create hardware adapter from local configuration."""
        from .hardware_adapter import create_standalone_hardware_adapter
        from .config import load_hardware_config

        # Collect parameter overrides
        overrides = self._collect_parameter_overrides()

        # Create default test config
        test_config = TestConfiguration()

        # Load hardware config from local config file (self-contained)
        hardware_config = load_hardware_config()

        # Apply overrides
        if overrides:
            test_config = test_config.with_overrides(**overrides)

        mode = "mock" if hardware_config.is_mock_mode() else "real hardware"
        logger.info(f"Creating hardware adapter ({mode} mode)")
        return create_standalone_hardware_adapter(
            test_config=test_config,
            hardware_config=hardware_config,
        )

    def _collect_parameter_overrides(self) -> Dict[str, Any]:
        """Collect parameter overrides from SDK get_parameter."""
        overrides: Dict[str, Any] = {}

        # Power settings
        voltage = self.get_parameter("voltage")
        if voltage is not None:
            overrides["voltage"] = voltage

        current = self.get_parameter("current")
        if current is not None:
            overrides["current"] = current

        # Temperature settings (comma-separated string -> list of floats)
        temperature_list_str = self.get_parameter("temperature_list")
        if temperature_list_str is not None:
            if isinstance(temperature_list_str, str):
                overrides["temperature_list"] = [float(t.strip()) for t in temperature_list_str.split(",")]
            elif isinstance(temperature_list_str, list):
                overrides["temperature_list"] = temperature_list_str

        standby_temperature = self.get_parameter("standby_temperature")
        if standby_temperature is not None:
            overrides["standby_temperature"] = standby_temperature

        activation_temperature = self.get_parameter("activation_temperature")
        if activation_temperature is not None:
            overrides["activation_temperature"] = activation_temperature

        # Position settings (comma-separated string -> list of floats)
        stroke_positions_str = self.get_parameter("stroke_positions")
        if stroke_positions_str is not None:
            if isinstance(stroke_positions_str, str):
                overrides["stroke_positions"] = [float(p.strip()) for p in stroke_positions_str.split(",")]
            elif isinstance(stroke_positions_str, list):
                overrides["stroke_positions"] = stroke_positions_str

        initial_position = self.get_parameter("initial_position")
        if initial_position is not None:
            overrides["initial_position"] = initial_position

        operating_position = self.get_parameter("operating_position")
        if operating_position is not None:
            overrides["operating_position"] = operating_position

        # Motion settings
        velocity = self.get_parameter("velocity")
        if velocity is not None:
            overrides["velocity"] = velocity

        acceleration = self.get_parameter("acceleration")
        if acceleration is not None:
            overrides["acceleration"] = acceleration

        # Execution settings
        repeat_count = self.get_parameter("repeat_count")
        if repeat_count is not None:
            overrides["repeat_count"] = repeat_count

        timeout_seconds = self.get_parameter("timeout_seconds")
        if timeout_seconds is not None:
            overrides["timeout_seconds"] = timeout_seconds

        return overrides

    def _create_dut_info(self) -> DUTCommandInfo:
        """Create DUT info from execution context."""
        serial_number = self.context.serial_number or "UNKNOWN"
        dut_id = self.context.wip_id or self.context.execution_id or "DUT001"
        model_number = self.get_parameter("model_number", "WF_EOL")

        return DUTCommandInfo(
            dut_id=dut_id,
            model_number=model_number,
            serial_number=serial_number,
        )

    def _build_step_measurements(self, measurements: Any) -> Dict[str, Any]:
        """Build measurements dict for emit_step_complete."""
        if not hasattr(measurements, 'to_dict'):
            return {}

        data = measurements.to_dict()
        test_config = self.hardware.test_config
        pass_criteria = test_config.pass_criteria

        # Get force limits from parameters or pass_criteria (ensure float type)
        force_limit_min = float(self.get_parameter("force_limit_min", pass_criteria.force_limit_min))
        force_limit_max = float(self.get_parameter("force_limit_max", pass_criteria.force_limit_max))

        result = {}
        for temp, positions in data.get('measurements', {}).items():
            for pos, measurement in positions.items():
                force = float(measurement.get('force', 0.0))

                # Convert temp/pos to int if whole number for cleaner names
                temp_str = int(temp) if float(temp) == int(temp) else temp
                pos_str = int(pos) if float(pos) == int(pos) else pos

                name = f"force_{temp_str}C_{pos_str}um"
                passed = force_limit_min <= force <= force_limit_max

                result[name] = {
                    "value": force,
                    "unit": "kgf",
                    "min": force_limit_min,
                    "max": force_limit_max,
                    "passed": passed,
                }

        return result

    async def _emit_test_measurements(self, measurements: Any) -> None:
        """Emit measurement events for each temperature/position."""
        step_measurements = self._build_step_measurements(measurements)

        for name, m_data in step_measurements.items():
            self.emit_measurement(
                name=name,
                value=m_data["value"],
                unit=m_data["unit"],
                min_value=m_data["min"],
                max_value=m_data["max"],
            )

    def _evaluate_results(self, measurements: Any) -> bool:
        """Evaluate test results against pass criteria."""
        if not hasattr(measurements, 'to_dict'):
            return False

        data = measurements.to_dict()
        test_config = self.hardware.test_config
        pass_criteria = test_config.pass_criteria

        # Get force limits from parameters or pass_criteria
        force_limit_min = self.get_parameter("force_limit_min", pass_criteria.force_limit_min)
        force_limit_max = self.get_parameter("force_limit_max", pass_criteria.force_limit_max)

        all_passed = True
        for temp, positions in data.get('measurements', {}).items():
            for pos, measurement in positions.items():
                force = measurement.get('force', 0.0)
                if not (force_limit_min <= force <= force_limit_max):
                    all_passed = False
                    logger.warning(
                        f"FAIL: Force {force:.2f}kgf at {temp}C/{pos}um "
                        f"outside limits [{force_limit_min}, {force_limit_max}]"
                    )

        return all_passed


# Register the sequence for discovery
register_sequence(EOLForceTestSequence)


# CLI entry point
if __name__ == "__main__":
    exit(EOLForceTestSequence.run_from_cli())
