"""
Hardware Control API Routes - WF EOL Tester

Provides REST endpoints for controlling and monitoring hardware components
organized by hardware test sequence:

1. System-wide control endpoints (status, connect, initialize)
2. Power supply control and monitoring
3. LoadCell monitoring and force measurement
4. MCU communication and temperature control
5. Robot movement and positioning
6. Digital I/O control and monitoring

Each hardware component follows consistent patterns:
- GET /{component}/status - Get component status
- POST /{component}/control - General control operations
- POST /{component}/connect - Connect to hardware
- POST /{component}/disconnect - Disconnect from hardware
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from application.services.configuration_service import ConfigurationService
from application.services.hardware_service_facade import HardwareServiceFacade
from infrastructure.containers import ApplicationContainer
from ui.api.models.hardware_models import (
    DigitalIORequest,
    DigitalIOResponse,
    HardwareConnectionRequest,
    HardwareInitializationRequest,
    HardwareStatusResponse,
    LoadCellResponse,
    MCUControlRequest,
    MCUStatusResponse,
    PowerControlRequest,
    PowerStatusResponse,
    RobotControlRequest,
    RobotStatusResponse,
)

router = APIRouter()

# =============================================================================
# SYSTEM-WIDE HARDWARE CONTROL ENDPOINTS
# =============================================================================


@router.get("/status", response_model=HardwareStatusResponse)
@inject
async def get_hardware_status(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get overall hardware connection status"""
    try:
        status_dict = await hardware_services.get_hardware_status()
        return HardwareStatusResponse.from_status_dict(status_dict)

    except Exception as e:
        logger.error(f"Failed to get hardware status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hardware status: {str(e)}",
        ) from e


@router.post("/connect")
@inject
async def connect_hardware(
    request: HardwareConnectionRequest,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Connect to hardware components"""
    try:
        # Load hardware configuration
        hardware_config = await config_service.load_hardware_config()

        if request.operation == "connect":
            await hardware_services.connect_all_hardware(hardware_config)
            logger.info("Hardware connection initiated")
            return {"message": "Hardware connection initiated successfully"}

        elif request.operation == "disconnect":
            await hardware_services.shutdown_hardware(hardware_config)
            logger.info("Hardware disconnection initiated")
            return {"message": "Hardware disconnection initiated successfully"}

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid operation: {request.operation}",
            )

    except Exception as e:
        logger.error(f"Hardware connection operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hardware operation failed: {str(e)}",
        ) from e


@router.post("/initialize")
@inject
async def initialize_hardware(
    request: HardwareInitializationRequest,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Initialize hardware with configuration"""
    try:
        # Load configurations
        profile_name = request.profile_name or await config_service.get_active_profile_name()
        test_config = await config_service.load_configuration(profile_name)
        hardware_config = await config_service.load_hardware_config()

        # Connect hardware if needed
        if request.force_reconnect:
            await hardware_services.connect_all_hardware(hardware_config)

        # Initialize hardware
        await hardware_services.initialize_hardware(test_config, hardware_config)

        logger.info(f"Hardware initialized with profile: {profile_name}")
        return {"message": "Hardware initialized successfully", "profile_name": profile_name}

    except Exception as e:
        logger.error(f"Hardware initialization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hardware initialization failed: {str(e)}",
        ) from e


# =============================================================================
# POWER SUPPLY CONTROL ENDPOINTS
# =============================================================================
@router.get("/robot/status", response_model=RobotStatusResponse)
@inject
async def get_robot_status(
    axis_id: int = 0,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get robot status"""
    try:
        # hardware_services is already injected
        robot_service = hardware_services.robot_service

        connected = await robot_service.is_connected()

        if connected:
            status_info = await robot_service.get_status(axis_id=axis_id)
            # Try both position field names for compatibility
            position = status_info.get("current_position") or status_info.get("position")
            return RobotStatusResponse(
                connected=True,
                axis_id=axis_id,
                current_position=position,
                is_homed=status_info.get("is_homed"),
                servo_enabled=status_info.get("servo_enabled"),
                is_moving=status_info.get("is_moving"),
            )
        else:
            return RobotStatusResponse(
                connected=False,
                axis_id=axis_id,
                current_position=None,
                is_homed=None,
                servo_enabled=None,
                is_moving=None,
                error_message="Robot not connected",
            )

    except Exception as e:
        logger.error(f"Failed to get robot status: {e}")
        return RobotStatusResponse(
            connected=False,
            axis_id=axis_id,
            current_position=None,
            is_homed=None,
            servo_enabled=None,
            is_moving=None,
            error_message=str(e),
        )


@router.post("/robot/control")
@inject
async def control_robot(
    request: RobotControlRequest,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
    config_service: ConfigurationService = Provide[ApplicationContainer.configuration_service],
):
    """Control robot operations"""
    try:
        robot_service = hardware_services.robot_service

        # Load hardware configuration for parameters
        hardware_config = await config_service.load_hardware_config()
        axis_id = request.axis_id or hardware_config.robot.axis_id

        if request.operation == "home":
            await robot_service.home_axis(axis_id)
            message = f"Robot homing initiated for axis {axis_id}"

        elif request.operation == "move":
            if request.position is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Position is required for move operation",
                )

            # Validate and set default values for motion parameters
            velocity = request.velocity if request.velocity is not None else 1000.0
            acceleration = request.acceleration if request.acceleration is not None else 5000.0
            deceleration = request.deceleration if request.deceleration is not None else 5000.0

            await robot_service.move_absolute(
                position=request.position,
                axis_id=axis_id,
                velocity=velocity,
                acceleration=acceleration,
                deceleration=deceleration,
            )
            message = f"Robot move initiated to position {request.position}μm"

        elif request.operation == "enable":
            await robot_service.enable_servo(axis_id)
            message = f"Robot servo enabled for axis {axis_id}"

        elif request.operation == "disable":
            await robot_service.disable_servo(axis_id)
            message = f"Robot servo disabled for axis {axis_id}"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid robot operation: {request.operation}",
            )

        logger.info(message)
        return {"message": message}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Robot control operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Robot control failed: {str(e)}",
        ) from e


# =============================================================================
# LOADCELL MONITORING AND CONTROL ENDPOINTS
# =============================================================================
@router.get("/power/status", response_model=PowerStatusResponse)
@inject
async def get_power_status(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get power supply status"""
    try:
        # hardware_services is already injected
        power_service = hardware_services.power_service

        connected = await power_service.is_connected()

        if connected:
            status_info = await power_service.get_status()
            return PowerStatusResponse(
                connected=True,
                output_enabled=status_info.get("output_enabled", False),
                voltage=status_info.get("voltage"),
                current=status_info.get("current"),
                measured_voltage=status_info.get("measured_voltage"),
                measured_current=status_info.get("measured_current"),
            )
        else:
            return PowerStatusResponse(
                connected=False,
                output_enabled=False,
                voltage=None,
                current=None,
                measured_voltage=None,
                measured_current=None,
                error_message="Power supply not connected",
            )

    except Exception as e:
        logger.error(f"Failed to get power status: {e}")
        return PowerStatusResponse(
            connected=False,
            output_enabled=False,
            voltage=None,
            current=None,
            measured_voltage=None,
            measured_current=None,
            error_message=str(e),
        )


@router.post("/power/control")
@inject
async def control_power(
    request: PowerControlRequest,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Control power supply"""
    try:
        # hardware_services is already injected
        power_service = hardware_services.power_service

        if request.operation == "enable":
            await power_service.enable_output()
            message = "Power output enabled"

        elif request.operation == "disable":
            await power_service.disable_output()
            message = "Power output disabled"

        elif request.operation == "set_voltage":
            if request.voltage is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Voltage is required for set_voltage operation",
                )
            await power_service.set_voltage(request.voltage)
            message = f"Power voltage set to {request.voltage}V"

        elif request.operation == "set_current":
            if request.current is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current is required for set_current operation",
                )
            await power_service.set_current(request.current)
            message = f"Power current set to {request.current}A"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid power operation: {request.operation}",
            )

        logger.info(message)
        return {"message": message}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Power control operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Power control failed: {str(e)}",
        ) from e


# MCU endpoints
@router.get("/mcu/status", response_model=MCUStatusResponse)
@inject
async def get_mcu_status(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get MCU status"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        connected = await mcu_service.is_connected()

        if connected:
            status_info = await mcu_service.get_status()
            return MCUStatusResponse(
                connected=True,
                boot_complete=status_info.get("boot_complete"),
                current_temperature=status_info.get("temperature"),
                target_temperature=status_info.get("target_temperature"),
                fan_speed=status_info.get("fan_speed"),
                test_mode=status_info.get("test_mode"),
            )
        else:
            return MCUStatusResponse(
                connected=False,
                boot_complete=None,
                current_temperature=None,
                target_temperature=None,
                fan_speed=None,
                test_mode=None,
                error_message="MCU not connected",
            )

    except Exception as e:
        logger.error(f"Failed to get MCU status: {e}")
        return MCUStatusResponse(
            connected=False,
            boot_complete=None,
            current_temperature=None,
            target_temperature=None,
            fan_speed=None,
            test_mode=None,
            error_message=str(e),
        )


@router.post("/mcu/control")
@inject
async def control_mcu(
    request: MCUControlRequest,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Control MCU operations"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        if request.operation == "set_operating_temperature":
            if request.temperature is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Temperature is required for set_operating_temperature operation",
                )
            await mcu_service.set_operating_temperature(request.temperature)
            message = f"MCU operating temperature set to {request.temperature}°C"

        elif request.operation == "set_fan_speed":
            if request.fan_speed is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Fan speed is required for set_fan_speed operation",
                )
            await mcu_service.set_fan_speed(request.fan_speed)
            message = f"MCU fan speed set to {request.fan_speed}"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid MCU operation: {request.operation}",
            )

        logger.info(message)
        return {"message": message}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCU control operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MCU control failed: {str(e)}",
        ) from e


# Load cell endpoints
@router.get("/loadcell/status", response_model=LoadCellResponse)
@inject
async def get_loadcell_status(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get load cell status and reading"""
    try:
        # hardware_services is already injected
        loadcell_service = hardware_services.loadcell_service

        connected = await loadcell_service.is_connected()

        if connected:
            force_reading = await loadcell_service.read_force()
            return LoadCellResponse(
                connected=True,
                force_value=force_reading.value,
                unit=force_reading.unit.value,
                is_holding=False,  # Add hold status if available
            )
        else:
            return LoadCellResponse(
                connected=False,
                force_value=None,
                unit=None,
                is_holding=None,
                error_message="Load cell not connected",
            )

    except Exception as e:
        logger.error(f"Failed to get load cell status: {e}")
        return LoadCellResponse(
            connected=False, force_value=None, unit=None, is_holding=None, error_message=str(e)
        )


@router.post("/loadcell/zero")
@inject
async def zero_loadcell(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Zero the load cell"""
    try:
        # hardware_services is already injected
        loadcell_service = hardware_services.loadcell_service

        await loadcell_service.zero_calibration()

        logger.info("Load cell zeroed")
        return {"message": "Load cell zeroed successfully"}

    except Exception as e:
        logger.error(f"Load cell zero operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Load cell zero failed: {str(e)}",
        ) from e


# Digital I/O endpoints
@router.get("/digital-io/status", response_model=DigitalIOResponse)
@inject
async def get_digital_io_status(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get digital I/O status"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        connected = await digital_io_service.is_connected()

        if connected:
            # Read all inputs (32 channels)
            inputs = {}
            for channel in range(32):
                try:
                    value = await digital_io_service.read_input(channel)
                    inputs[channel] = value
                except Exception:
                    inputs[channel] = False  # Default to False if read fails

            return DigitalIOResponse(
                connected=True, inputs=inputs, outputs=None, channel_value=None
            )
        else:
            return DigitalIOResponse(
                connected=False,
                inputs=None,
                outputs=None,
                channel_value=None,
                error_message="Digital I/O not connected",
            )

    except Exception as e:
        logger.error(f"Failed to get digital I/O status: {e}")
        return DigitalIOResponse(
            connected=False, inputs=None, outputs=None, channel_value=None, error_message=str(e)
        )


@router.post("/digital-io/control", response_model=DigitalIOResponse)
@inject
async def control_digital_io(
    request: DigitalIORequest,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Control digital I/O operations"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        if request.operation == "read_input":
            if request.channel is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Channel is required for read_input operation",
                )
            value = await digital_io_service.read_input(request.channel)
            return DigitalIOResponse(connected=True, inputs=None, outputs=None, channel_value=value)

        elif request.operation == "write_output":
            if request.channel is None or request.value is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Channel and value are required for write_output operation",
                )
            await digital_io_service.write_output(request.channel, request.value)
            return DigitalIOResponse(
                connected=True, inputs=None, outputs=None, channel_value=request.value
            )

        elif request.operation == "read_all_inputs":
            inputs = {}
            for channel in range(32):
                try:
                    value = await digital_io_service.read_input(channel)
                    inputs[channel] = value
                except Exception:
                    inputs[channel] = False

            return DigitalIOResponse(
                connected=True, inputs=inputs, outputs=None, channel_value=None
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid digital I/O operation: {request.operation}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Digital I/O control operation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Digital I/O control failed: {str(e)}",
        ) from e


# Additional robot control endpoints for web interface compatibility
@router.post("/robot/connect")
@inject
async def connect_robot(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Connect to robot hardware"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        robot_service = hardware_services.robot_service

        axis_id = request.get("axis_id", 0)

        await robot_service.connect()
        message = f"Robot connected successfully to axis {axis_id}"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Robot connection failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/robot/disconnect")
@inject
async def disconnect_robot(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Disconnect from robot hardware"""
    try:
        # hardware_services is already injected
        robot_service = hardware_services.robot_service

        await robot_service.disconnect()
        message = "Robot disconnected successfully"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Robot disconnection failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/robot/servo/enable")
@inject
async def enable_robot_servo(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Enable robot servo"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        robot_service = hardware_services.robot_service

        axis_id = request.get("axis_id", 0)
        await robot_service.enable_servo(axis_id)
        message = f"Robot servo enabled for axis {axis_id}"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Robot servo enable failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/robot/servo/disable")
@inject
async def disable_robot_servo(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Disable robot servo"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        robot_service = hardware_services.robot_service

        axis_id = request.get("axis_id", 0)
        await robot_service.disable_servo(axis_id)
        message = f"Robot servo disabled for axis {axis_id}"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Robot servo disable failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/robot/home-axis")
@inject
async def home_robot_axis(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Home robot axis"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        robot_service = hardware_services.robot_service

        axis_id = request.get("axis_id", 0)
        await robot_service.home_axis(axis_id)
        message = f"Robot homing initiated for axis {axis_id}"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Robot homing failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/robot/move-absolute")
@inject
async def move_robot_absolute(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Move robot to absolute position"""
    try:
        robot_service = hardware_services.robot_service

        axis_id = request.get("axis_id", 0)
        position = request.get("position")

        # Use provided values (should be provided by client after loading from config)
        velocity = request.get("velocity")
        acceleration = request.get("acceleration")
        deceleration = request.get("deceleration")

        # Validate required motion parameters
        if velocity is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Velocity parameter is required"
            )
        if acceleration is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Acceleration parameter is required"
            )
        if deceleration is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Deceleration parameter is required"
            )

        velocity = float(velocity)
        acceleration = float(acceleration)
        deceleration = float(deceleration)

        if position is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Position is required"
            )

        await robot_service.move_absolute(
            position=position,
            axis_id=axis_id,
            velocity=velocity,
            acceleration=acceleration,
            deceleration=deceleration,
        )
        message = f"Robot move initiated to position {position}μm on axis {axis_id}"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Robot absolute move failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/robot/move-relative")
@inject
async def move_robot_relative(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Move robot by relative distance"""
    try:
        robot_service = hardware_services.robot_service

        axis_id = request.get("axis_id", 0)
        distance = request.get("distance")

        # Use provided values (should be provided by client after loading from config)
        velocity = request.get("velocity")
        acceleration = request.get("acceleration")
        deceleration = request.get("deceleration")

        # Validate required motion parameters
        if velocity is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Velocity parameter is required"
            )
        if acceleration is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Acceleration parameter is required"
            )
        if deceleration is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Deceleration parameter is required"
            )

        velocity = float(velocity)
        acceleration = float(acceleration)
        deceleration = float(deceleration)

        if distance is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Distance is required"
            )

        await robot_service.move_relative(
            distance=distance,
            axis_id=axis_id,
            velocity=velocity,
            acceleration=acceleration,
            deceleration=deceleration,
        )
        message = f"Robot move initiated by distance {distance}μm on axis {axis_id}"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Robot relative move failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/robot/emergency-stop")
@inject
async def emergency_stop_robot(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Emergency stop robot"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        robot_service = hardware_services.robot_service

        axis_id = request.get("axis_id", 0)
        await robot_service.emergency_stop(axis_id)
        message = f"Emergency stop executed for axis {axis_id}"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Robot emergency stop failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/robot/stop-motion")
@inject
async def stop_robot_motion(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Stop robot motion with deceleration"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        robot_service = hardware_services.robot_service

        axis_id = request.get("axis_id", 0)
        deceleration = request.get("deceleration", 1000.0)

        await robot_service.stop_motion(axis_id, deceleration)
        message = f"Robot motion stop initiated for axis {axis_id}"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Robot motion stop failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/robot/position")
@inject
async def get_robot_position(
    axis_id: int = 0,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get robot position"""
    try:
        # hardware_services is already injected
        robot_service = hardware_services.robot_service

        position = await robot_service.get_position(axis_id)

        return {"success": True, "data": {"position": position, "axis_id": axis_id}}

    except Exception as e:
        logger.error(f"Get robot position failed: {e}")
        return {"success": False, "error": str(e)}


# Power Control specific endpoints for web interface compatibility
@router.post("/power/connect")
@inject
async def connect_power(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Connect to power supply hardware"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        power_service = hardware_services.power_service

        host = request.get("host", "192.168.11.1")
        port = request.get("port", 5000)
        channel = request.get("channel", 1)

        await power_service.connect()

        # Get device identity if available
        device_identity = None
        try:
            power_status = await power_service.get_status()
            device_identity = power_status.get("device_identity")
        except Exception:
            pass

        message = f"Power supply connected to {host}:{port}"

        logger.info(message)
        return {
            "success": True,
            "message": message,
            "data": {
                "device_identity": device_identity,
                "host": host,
                "port": port,
                "channel": channel,
            },
        }

    except Exception as e:
        logger.error(f"Power connection failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/power/disconnect")
@inject
async def disconnect_power(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Disconnect from power supply hardware"""
    try:
        # hardware_services is already injected
        power_service = hardware_services.power_service

        await power_service.disconnect()
        message = "Power supply disconnected successfully"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Power disconnection failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/power/enable-output")
@inject
async def enable_power_output(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Enable power supply output"""
    try:
        # hardware_services is already injected
        power_service = hardware_services.power_service

        await power_service.enable_output()
        message = "Power output enabled"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Power output enable failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/power/disable-output")
@inject
async def disable_power_output(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Disable power supply output"""
    try:
        # hardware_services is already injected
        power_service = hardware_services.power_service

        await power_service.disable_output()
        message = "Power output disabled"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Power output disable failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/power/set-voltage")
@inject
async def set_power_voltage(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Set power supply voltage"""
    try:
        # hardware_services is already injected
        power_service = hardware_services.power_service

        voltage = request.get("voltage")
        if voltage is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Voltage is required"
            )

        await power_service.set_voltage(voltage)

        # Get actual voltage if available
        actual_voltage = voltage
        try:
            status_info = await power_service.get_status()
            actual_voltage = status_info.get("voltage", voltage)
        except Exception:
            pass

        message = f"Power voltage set to {actual_voltage}V"

        logger.info(message)
        return {"success": True, "message": message, "data": {"actual_voltage": actual_voltage}}

    except Exception as e:
        logger.error(f"Set voltage failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/power/set-current")
@inject
async def set_power_current(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Set power supply current"""
    try:
        # hardware_services is already injected
        power_service = hardware_services.power_service

        current = request.get("current")
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Current is required"
            )

        await power_service.set_current(current)

        # Get actual current if available
        actual_current = current
        try:
            status_info = await power_service.get_status()
            actual_current = status_info.get("current", current)
        except Exception:
            pass

        message = f"Power current set to {actual_current}A"

        logger.info(message)
        return {"success": True, "message": message, "data": {"actual_current": actual_current}}

    except Exception as e:
        logger.error(f"Set current failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/power/set-current-limit")
@inject
async def set_power_current_limit(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Set power supply current limit"""
    try:
        # hardware_services is already injected
        power_service = hardware_services.power_service

        current_limit = request.get("current_limit")
        if current_limit is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Current limit is required"
            )

        await power_service.set_current_limit(current_limit)

        # Get actual limit if available
        actual_limit = current_limit
        try:
            status_info = await power_service.get_status()
            actual_limit = status_info.get("current_limit", current_limit)
        except Exception:
            pass

        message = f"Power current limit set to {actual_limit}A"

        logger.info(message)
        return {"success": True, "message": message, "data": {"actual_limit": actual_limit}}

    except Exception as e:
        logger.error(f"Set current limit failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/power/readings")
@inject
async def get_power_readings(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get power supply real-time readings"""
    try:
        # hardware_services is already injected
        power_service = hardware_services.power_service

        status_info = await power_service.get_status()

        voltage = status_info.get("voltage", 0.0)
        current = status_info.get("current", 0.0)
        power = voltage * current  # Calculate power

        return {"success": True, "data": {"voltage": voltage, "current": current, "power": power}}

    except Exception as e:
        logger.error(f"Get power readings failed: {e}")
        return {"success": False, "error": str(e)}


# MCU Control specific endpoints for web interface compatibility
@router.post("/mcu/connect")
@inject
async def connect_mcu(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Connect to MCU hardware"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        port = request.get("port", "COM4")
        baudrate = request.get("baudrate", 115200)
        timeout = request.get("timeout", 5.0)

        await mcu_service.connect()

        message = f"MCU connected to {port} at {baudrate} baud"

        logger.info(message)
        return {
            "success": True,
            "message": message,
            "data": {"port": port, "baudrate": baudrate, "timeout": timeout},
        }

    except Exception as e:
        logger.error(f"MCU connection failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/mcu/disconnect")
@inject
async def disconnect_mcu(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Disconnect from MCU hardware"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        await mcu_service.disconnect()
        message = "MCU disconnected successfully"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"MCU disconnection failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/mcu/set-temperature")
@inject
async def set_mcu_temperature(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Set MCU target temperature"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        temperature = request.get("temperature")
        if temperature is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Temperature is required"
            )

        await mcu_service.set_operating_temperature(temperature)
        message = f"MCU operating temperature set to {temperature}°C"

        logger.info(message)
        return {"success": True, "message": message, "data": {"target_temperature": temperature}}

    except Exception as e:
        logger.error(f"Set MCU temperature failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/mcu/set-upper-temperature")
@inject
async def set_mcu_upper_temperature(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Set MCU upper temperature limit"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        upper_temperature = request.get("upper_temperature")
        if upper_temperature is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Upper temperature is required"
            )

        await mcu_service.set_upper_temperature(upper_temperature)
        message = f"MCU upper temperature limit set to {upper_temperature}°C"

        logger.info(message)
        return {
            "success": True,
            "message": message,
            "data": {"upper_temperature": upper_temperature},
        }

    except Exception as e:
        logger.error(f"Set MCU upper temperature failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/mcu/set-fan-speed")
@inject
async def set_mcu_fan_speed(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Set MCU fan speed level"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        fan_speed = request.get("fan_speed")
        if fan_speed is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Fan speed is required"
            )

        await mcu_service.set_fan_speed(fan_speed)
        message = f"MCU fan speed set to level {fan_speed}"

        logger.info(message)
        return {"success": True, "message": message, "data": {"fan_speed": fan_speed}}

    except Exception as e:
        logger.error(f"Set MCU fan speed failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/mcu/set-test-mode")
@inject
async def set_mcu_test_mode(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Set MCU test mode"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        from application.interfaces.hardware.mcu import TestMode

        test_mode = request.get("test_mode")
        if test_mode is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Test mode is required"
            )

        # Convert string to TestMode enum
        if isinstance(test_mode, str):
            try:
                mode_enum = TestMode(int(test_mode.replace("MODE_", "")))
            except (ValueError, AttributeError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid test mode: {test_mode}",
                ) from exc
        else:
            mode_enum = TestMode(test_mode)

        await mcu_service.set_test_mode(mode_enum)
        message = f"MCU test mode set to {mode_enum.name}"

        logger.info(message)
        return {
            "success": True,
            "message": message,
            "data": {"test_mode": mode_enum.value, "test_mode_name": mode_enum.name},
        }

    except Exception as e:
        logger.error(f"Set MCU test mode failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/mcu/start-standby-heating")
@inject
async def start_mcu_standby_heating(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Start MCU standby heating mode"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        operating_temp = request.get("operating_temp")
        standby_temp = request.get("standby_temp")

        if operating_temp is None or standby_temp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operating temperature and standby temperature are required",
            )

        hold_time_ms = request.get("hold_time_ms", 10000)

        await mcu_service.start_standby_heating(
            operating_temp=operating_temp, standby_temp=standby_temp, hold_time_ms=hold_time_ms
        )

        message = (
            f"MCU standby heating started: {operating_temp}°C operating, {standby_temp}°C standby"
        )

        logger.info(message)
        return {
            "success": True,
            "message": message,
            "data": {
                "operating_temp": operating_temp,
                "standby_temp": standby_temp,
                "hold_time_ms": hold_time_ms,
            },
        }

    except Exception as e:
        logger.error(f"Start MCU standby heating failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/mcu/start-standby-cooling")
@inject
async def start_mcu_standby_cooling(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Start MCU standby cooling mode"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        await mcu_service.start_standby_cooling()
        message = "MCU standby cooling started"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Start MCU standby cooling failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/mcu/wait-boot-complete")
@inject
async def wait_mcu_boot_complete(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Wait for MCU boot process to complete"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        await mcu_service.wait_boot_complete()
        message = "MCU boot process completed"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"Wait MCU boot complete failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/mcu/temperature")
@inject
async def get_mcu_temperature(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get MCU current temperature reading"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        temperature = await mcu_service.get_temperature()

        return {"success": True, "data": {"temperature": temperature}}

    except Exception as e:
        logger.error(f"Get MCU temperature failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/mcu/fan-speed")
@inject
async def get_mcu_fan_speed(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get MCU current fan speed"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        fan_speed = await mcu_service.get_fan_speed()

        return {"success": True, "data": {"fan_speed": fan_speed}}

    except Exception as e:
        logger.error(f"Get MCU fan speed failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/mcu/test-mode")
@inject
async def get_mcu_test_mode(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get MCU current test mode"""
    try:
        # hardware_services is already injected
        mcu_service = hardware_services.mcu_service

        test_mode = await mcu_service.get_test_mode()

        return {
            "success": True,
            "data": {"test_mode": test_mode.value, "test_mode_name": test_mode.name},
        }

    except Exception as e:
        logger.error(f"Get MCU test mode failed: {e}")
        return {"success": False, "error": str(e)}


# LoadCell Control specific endpoints for web interface compatibility
@router.post("/loadcell/connect")
@inject
async def connect_loadcell(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Connect to LoadCell hardware"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        loadcell_service = hardware_services.loadcell_service

        port = request.get("port", "COM3")
        baudrate = request.get("baudrate", 9600)
        timeout = request.get("timeout", 5.0)
        indicator_id = request.get("indicator_id", 1)

        # LoadCell service is configured via dependency injection in HardwareContainer
        # All connection parameters are provided through the constructor
        await loadcell_service.connect()

        message = "LoadCell connected successfully"

        logger.info(message)
        return {
            "success": True,
            "message": message,
            "data": {
                "port": port,
                "baudrate": baudrate,
                "timeout": timeout,
                "indicator_id": indicator_id,
            },
        }

    except Exception as e:
        logger.error(f"LoadCell connection failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/loadcell/disconnect")
@inject
async def disconnect_loadcell(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Disconnect from LoadCell hardware"""
    try:
        # hardware_services is already injected
        loadcell_service = hardware_services.loadcell_service

        await loadcell_service.disconnect()
        message = "LoadCell disconnected successfully"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"LoadCell disconnection failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/loadcell/zero-calibration")
@inject
async def zero_loadcell_calibration(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Perform LoadCell zero point calibration"""
    try:
        # hardware_services is already injected
        loadcell_service = hardware_services.loadcell_service

        await loadcell_service.zero_calibration()
        message = "LoadCell zero calibration completed"

        logger.info(message)
        return {"success": True, "message": message}

    except Exception as e:
        logger.error(f"LoadCell zero calibration failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/loadcell/hold")
@inject
async def hold_loadcell_measurement(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Hold LoadCell force measurement"""
    try:
        # hardware_services is already injected
        loadcell_service = hardware_services.loadcell_service

        result = await loadcell_service.hold()
        message = "LoadCell measurement held" if result else "LoadCell hold operation failed"

        logger.info(message)
        return {"success": result, "message": message, "data": {"holding": result}}

    except Exception as e:
        logger.error(f"LoadCell hold failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/loadcell/hold-release")
@inject
async def release_loadcell_hold(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Release LoadCell force measurement hold"""
    try:
        # hardware_services is already injected
        loadcell_service = hardware_services.loadcell_service

        result = await loadcell_service.hold_release()
        message = "LoadCell hold released" if result else "LoadCell release operation failed"

        logger.info(message)
        return {"success": result, "message": message, "data": {"holding": False}}

    except Exception as e:
        logger.error(f"LoadCell hold release failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/loadcell/force")
@inject
async def get_loadcell_force(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get LoadCell force measurement"""
    try:
        # hardware_services is already injected
        loadcell_service = hardware_services.loadcell_service

        force_value = await loadcell_service.read_force()

        return {
            "success": True,
            "data": {
                "force": force_value.value,
                "unit": force_value.unit.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Get LoadCell force failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/loadcell/raw-value")
@inject
async def get_loadcell_raw_value(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get LoadCell raw ADC value"""
    try:
        # hardware_services is already injected
        loadcell_service = hardware_services.loadcell_service

        raw_value = await loadcell_service.read_raw_value()

        return {"success": True, "data": {"raw_value": raw_value}}

    except Exception as e:
        logger.error(f"Get LoadCell raw value failed: {e}")
        return {"success": False, "error": str(e)}


# ========================================================================
# Digital I/O Control Routes
# ========================================================================


@router.post("/digital-io/connect")
@inject
async def connect_digital_io(
    request: Optional[Dict] = None,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Connect to Digital I/O hardware"""
    try:
        if request is None:
            request = {}
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        await digital_io_service.connect()

        logger.info("Digital I/O connected successfully")
        return {
            "success": True,
            "message": "Digital I/O connected successfully",
            "data": {"timestamp": datetime.now().isoformat()},
        }

    except Exception as e:
        logger.error(f"Digital I/O connection failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/digital-io/disconnect")
@inject
async def disconnect_digital_io(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Disconnect from Digital I/O hardware"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        await digital_io_service.disconnect()

        logger.info("Digital I/O disconnected successfully")
        return {
            "success": True,
            "message": "Digital I/O disconnected successfully",
            "data": {"timestamp": datetime.now().isoformat()},
        }

    except Exception as e:
        logger.error(f"Digital I/O disconnection failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/digital-io/info")
@inject
async def get_digital_io_info(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Get Digital I/O hardware information"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        is_connected = await digital_io_service.is_connected()
        input_count = await digital_io_service.get_input_count()
        output_count = await digital_io_service.get_output_count()

        logger.debug("Digital I/O status retrieved successfully")
        return {
            "success": True,
            "message": "Digital I/O status retrieved successfully",
            "data": {
                "connected": is_connected,
                "input_count": input_count,
                "output_count": output_count,
                "timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Digital I/O status retrieval failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/digital-io/read-input")
@inject
async def read_digital_input(
    channel: int,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Read digital input from specified channel"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        # Validate channel parameter
        if channel < 0:
            return {"success": False, "error": "Channel must be non-negative"}

        input_state = await digital_io_service.read_input(channel)

        logger.debug(f"Digital input channel {channel} read: {input_state}")
        return {
            "success": True,
            "message": f"Digital input channel {channel} read successfully",
            "data": {
                "channel": channel,
                "state": input_state,
                "level": "HIGH" if input_state else "LOW",
                "timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Digital input read failed for channel {channel}: {e}")
        return {"success": False, "error": str(e)}


@router.get("/digital-io/read-all-inputs")
@inject
async def read_all_digital_inputs(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Read all digital inputs"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        all_inputs = await digital_io_service.read_all_inputs()

        # Convert to more detailed format
        inputs_data = []
        for i, state in enumerate(all_inputs):
            inputs_data.append({"channel": i, "state": state, "level": "HIGH" if state else "LOW"})

        logger.debug(f"All digital inputs read: {len(all_inputs)} channels")
        return {
            "success": True,
            "message": f"All digital inputs read successfully ({len(all_inputs)} channels)",
            "data": {
                "inputs": inputs_data,
                "count": len(all_inputs),
                "timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"All digital inputs read failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/digital-io/write-output")
@inject
async def write_digital_output(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Write digital output to specified channel"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        # Extract parameters
        channel = request.get("channel")
        level = request.get("level")

        # Validate and convert parameters
        try:
            # Convert and validate channel
            if channel is None:
                return {"success": False, "error": "Channel parameter is required"}

            # Convert channel to int
            if isinstance(channel, str):
                try:
                    channel_int = int(channel)
                except ValueError:
                    return {"success": False, "error": "Channel must be a valid integer"}
            elif isinstance(channel, int):
                channel_int = channel
            else:
                return {"success": False, "error": "Channel must be an integer"}

            if channel_int < 0:
                return {"success": False, "error": "Channel must be a non-negative integer"}

            # Convert and validate level
            if level is None:
                return {"success": False, "error": "Level parameter is required"}

            # Convert level to bool
            if isinstance(level, bool):
                level_bool = level
            elif isinstance(level, str):
                level_bool = level.lower() in ("true", "1", "high", "on")
            elif isinstance(level, int):
                level_bool = bool(level)
            else:
                return {"success": False, "error": "Level must be a boolean value"}

        except Exception as e:
            return {"success": False, "error": f"Parameter validation error: {str(e)}"}

        success = await digital_io_service.write_output(channel_int, level_bool)

        if success:
            logger.info(f"Digital output channel {channel_int} set to {level_bool}")
            return {
                "success": True,
                "message": (
                    f"Digital output channel {channel_int} set to {'HIGH' if level_bool else 'LOW'}"
                ),
                "data": {
                    "channel": channel_int,
                    "level": level_bool,
                    "level_text": "HIGH" if level_bool else "LOW",
                    "timestamp": datetime.now().isoformat(),
                },
            }
        return {"success": False, "error": f"Failed to write to channel {channel_int}"}

    except Exception as e:
        logger.error(f"Digital output write failed: {e}")
        return {"success": False, "error": str(e)}


@router.get("/digital-io/read-output")
@inject
async def read_digital_output(
    channel: int,
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Read digital output state from specified channel"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        # Validate channel parameter
        if channel < 0:
            return {"success": False, "error": "Channel must be non-negative"}

        output_state = await digital_io_service.read_output(channel)

        logger.debug(f"Digital output channel {channel} state: {output_state}")
        return {
            "success": True,
            "message": f"Digital output channel {channel} state read successfully",
            "data": {
                "channel": channel,
                "state": output_state,
                "level": "HIGH" if output_state else "LOW",
                "timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Digital output read failed for channel {channel}: {e}")
        return {"success": False, "error": str(e)}


@router.get("/digital-io/read-all-outputs")
@inject
async def read_all_digital_outputs(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Read all digital outputs"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        all_outputs = await digital_io_service.read_all_outputs()

        # Convert to more detailed format
        outputs_data = []
        for i, state in enumerate(all_outputs):
            outputs_data.append({"channel": i, "state": state, "level": "HIGH" if state else "LOW"})

        logger.debug(f"All digital outputs read: {len(all_outputs)} channels")
        return {
            "success": True,
            "message": f"All digital outputs read successfully ({len(all_outputs)} channels)",
            "data": {
                "outputs": outputs_data,
                "count": len(all_outputs),
                "timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"All digital outputs read failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/digital-io/reset-all-outputs")
@inject
async def reset_all_digital_outputs(
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Reset all digital outputs to LOW"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        success = await digital_io_service.reset_all_outputs()

        if success:
            logger.info("All digital outputs reset to LOW")
            return {
                "success": True,
                "message": "All digital outputs reset to LOW successfully",
                "data": {"timestamp": datetime.now().isoformat()},
            }
        else:
            return {"success": False, "error": "Failed to reset all outputs"}

    except Exception as e:
        logger.error(f"Reset all digital outputs failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/digital-io/read-multiple-inputs")
@inject
async def read_multiple_digital_inputs(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Read multiple digital inputs"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        # Extract channel list
        channels = request.get("channels", [])

        if not isinstance(channels, list):
            return {"success": False, "error": "Channels must be a list of integers"}

        if not channels:
            return {"success": False, "error": "At least one channel must be specified"}

        # Validate all channels
        for channel in channels:
            if not isinstance(channel, int) or channel < 0:
                return {
                    "success": False,
                    "error": (
                        f"Invalid channel: {channel}. All channels must be non-negative integers"
                    ),
                }

        results = await digital_io_service.read_multiple_inputs(channels)

        # Convert to detailed format
        inputs_data = []
        for channel, state in results.items():
            inputs_data.append(
                {"channel": channel, "state": state, "level": "HIGH" if state else "LOW"}
            )

        # Sort by channel number
        inputs_data.sort(key=lambda x: x["channel"])

        logger.debug(f"Multiple digital inputs read: {len(channels)} channels")
        return {
            "success": True,
            "message": f"Multiple digital inputs read successfully ({len(channels)} channels)",
            "data": {
                "inputs": inputs_data,
                "count": len(channels),
                "timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Multiple digital inputs read failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/digital-io/write-multiple-outputs")
@inject
async def write_multiple_digital_outputs(
    request: Dict[str, Any],
    hardware_services: HardwareServiceFacade = Provide[
        ApplicationContainer.hardware_service_facade
    ],
):
    """Write multiple digital outputs"""
    try:
        # hardware_services is already injected
        digital_io_service = hardware_services.digital_io_service

        # Extract pin_values dictionary
        pin_values = request.get("pin_values", {})

        # Validate input parameters
        if not isinstance(pin_values, dict):
            error_msg = "pin_values must be a dictionary mapping channel numbers to boolean values"
        elif not pin_values:
            error_msg = "At least one channel value must be specified"
        else:
            error_msg = None

        if error_msg:
            return {"success": False, "error": error_msg}

        # Validate and convert pin_values
        validated_pin_values = {}
        for channel_str, level in pin_values.items():
            try:
                channel = int(channel_str)
                if channel < 0:
                    return {"success": False, "error": f"Channel {channel} must be non-negative"}

                # Convert level to boolean if needed
                if not isinstance(level, bool):
                    if isinstance(level, str):
                        level = level.lower() in ("true", "1", "high", "on")
                    elif isinstance(level, int):
                        level = bool(level)
                    else:
                        return {
                            "success": False,
                            "error": f"Invalid level for channel {channel}: must be boolean",
                        }

                validated_pin_values[channel] = level

            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid channel: {channel_str}. Must be an integer",
                }

        success = await digital_io_service.write_multiple_outputs(validated_pin_values)

        if success:
            # Create response data
            outputs_data = []
            for channel, level in validated_pin_values.items():
                outputs_data.append(
                    {"channel": channel, "level": level, "level_text": "HIGH" if level else "LOW"}
                )

            # Sort by channel number
            outputs_data.sort(key=lambda x: x["channel"])

            logger.info(f"Multiple digital outputs written: {len(validated_pin_values)} channels")
            return {
                "success": True,
                "message": (
                    f"Multiple digital outputs written successfully ({len(validated_pin_values)} channels)"
                ),
                "data": {
                    "outputs": outputs_data,
                    "count": len(validated_pin_values),
                    "timestamp": datetime.now().isoformat(),
                },
            }
        return {"success": False, "error": "Failed to write to one or more channels"}

    except Exception as e:
        logger.error(f"Multiple digital outputs write failed: {e}")
        return {"success": False, "error": str(e)}
