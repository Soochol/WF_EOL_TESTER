"""
WebSocket API routes

Provides WebSocket endpoints for real-time communication.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from ui.api.dependencies import get_container
from ui.api.models.websocket_models import (
    DigitalInputMessage,
    HardwareEventMessage,
    SystemStatusMessage,
    TestLogMessage,
    TestProgressMessage,
    WebSocketResponse,
)

router = APIRouter()

# WebSocket connection management
active_connections: Dict[str, Set[WebSocket]] = {
    "digital-input": set(),
    "test-logs": set(),
    "system-status": set(),
    "all": set(),
}

# Background tasks for periodic updates
background_tasks: Dict[str, asyncio.Task] = {}
last_digital_inputs: Dict[int, bool] = {}


class WebSocketManager:
    """Manages WebSocket connections and broadcasting"""

    @staticmethod
    async def connect(websocket: WebSocket, channel: str):
        """Accept WebSocket connection and add to channel"""
        await websocket.accept()
        active_connections[channel].add(websocket)
        active_connections["all"].add(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")

    @staticmethod
    def disconnect(websocket: WebSocket, channel: str):
        """Remove WebSocket from channel"""
        active_connections[channel].discard(websocket)
        active_connections["all"].discard(websocket)
        logger.info(f"WebSocket disconnected from channel: {channel}")

    @staticmethod
    async def send_personal_message(websocket: WebSocket, message: dict):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")

    @staticmethod
    async def broadcast_to_channel(channel: str, message: dict):
        """Broadcast message to all connections in a channel"""
        if channel not in active_connections:
            return

        disconnected = set()

        for connection in active_connections[channel].copy():
            try:
                await connection.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            active_connections[channel].discard(connection)
            active_connections["all"].discard(connection)


manager = WebSocketManager()


@router.websocket("/digital-input")
async def websocket_digital_input(websocket: WebSocket):
    """WebSocket endpoint for real-time digital input monitoring"""
    await manager.connect(websocket, "digital-input")

    # Start background task if not already running
    if "digital-input" not in background_tasks:
        background_tasks["digital-input"] = asyncio.create_task(digital_input_monitor())

    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle subscription management
                if message.get("type") == "subscription":
                    response = WebSocketResponse(
                        type="response",
                        timestamp=datetime.now().isoformat(),
                        success=True,
                        message="Subscription updated",
                        data=None,
                    )
                    await manager.send_personal_message(websocket, response.model_dump())

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from WebSocket: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, "digital-input")

        # Stop background task if no more connections
        if not active_connections["digital-input"] and "digital-input" in background_tasks:
            background_tasks["digital-input"].cancel()
            del background_tasks["digital-input"]


@router.websocket("/test-logs")
async def websocket_test_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time test execution logs"""
    await manager.connect(websocket, "test-logs")

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle test log subscriptions (filter by test_id, etc.)
                if message.get("type") == "subscription":
                    response = WebSocketResponse(
                        type="response",
                        timestamp=datetime.now().isoformat(),
                        success=True,
                        message="Test log subscription updated",
                        data=None,
                    )
                    await manager.send_personal_message(websocket, response.model_dump())

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from WebSocket: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, "test-logs")


@router.websocket("/system-status")
async def websocket_system_status(websocket: WebSocket):
    """WebSocket endpoint for real-time system status updates"""
    await manager.connect(websocket, "system-status")

    # Start background task if not already running
    if "system-status" not in background_tasks:
        background_tasks["system-status"] = asyncio.create_task(system_status_monitor())

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                if message.get("type") == "subscription":
                    response = WebSocketResponse(
                        type="response",
                        timestamp=datetime.now().isoformat(),
                        success=True,
                        message="System status subscription updated",
                        data=None,
                    )
                    await manager.send_personal_message(websocket, response.model_dump())

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from WebSocket: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, "system-status")

        # Stop background task if no more connections
        if not active_connections["system-status"] and "system-status" in background_tasks:
            background_tasks["system-status"].cancel()
            del background_tasks["system-status"]


async def digital_input_monitor():
    """Background task to monitor digital inputs and broadcast changes"""
    global last_digital_inputs

    logger.info("Starting digital input monitor")

    try:
        # Get container for hardware access
        container = get_container()

        while active_connections["digital-input"]:
            try:
                hardware_services = container.hardware_service_facade()
                digital_io_service = hardware_services.digital_io_service

                # Check if digital I/O is connected
                if await digital_io_service.is_connected():
                    current_inputs = {}
                    changed_channels = []

                    # Read all 32 digital inputs
                    for channel in range(32):
                        try:
                            value = await digital_io_service.read_input(channel)
                            current_inputs[channel] = value

                            # Check for changes
                            if (
                                channel not in last_digital_inputs
                                or last_digital_inputs[channel] != value
                            ):
                                changed_channels.append(channel)

                        except Exception:
                            # If read fails, default to False
                            current_inputs[channel] = False
                            if (
                                channel not in last_digital_inputs
                                or last_digital_inputs[channel] is not False
                            ):
                                changed_channels.append(channel)

                    # Broadcast if there are changes
                    if changed_channels:
                        message = DigitalInputMessage(
                            type="digital_input",
                            timestamp=datetime.now().isoformat(),
                            inputs=current_inputs,
                            changed_channels=changed_channels,
                        )

                        await manager.broadcast_to_channel("digital-input", message.model_dump())
                        last_digital_inputs = current_inputs.copy()

                else:
                    # If not connected, send empty state
                    if last_digital_inputs:  # Only send if we previously had data
                        message = DigitalInputMessage(
                            type="digital_input",
                            timestamp=datetime.now().isoformat(),
                            inputs={i: False for i in range(32)},
                            changed_channels=list(range(32)),
                        )

                        await manager.broadcast_to_channel("digital-input", message.model_dump())
                        last_digital_inputs = {}

            except Exception as e:
                logger.error(f"Error in digital input monitor: {e}")

            # Wait before next poll
            await asyncio.sleep(0.1)  # 100ms polling rate

    except asyncio.CancelledError:
        logger.info("Digital input monitor cancelled")
    except Exception as e:
        logger.error(f"Digital input monitor error: {e}")


async def system_status_monitor():
    """Background task to monitor system status and broadcast changes"""
    logger.info("Starting system status monitor")

    last_status = None

    try:
        container = get_container()

        while active_connections["system-status"]:
            try:
                hardware_services = container.hardware_service_facade()
                hardware_status = await hardware_services.get_hardware_status()

                # Create system status message
                current_status = {
                    "hardware_status": hardware_status,
                    "test_running": False,  # This would be updated from actual test state
                    "emergency_stop": False,  # This would be updated from emergency stop state
                    "active_test_id": None,
                }

                # Only broadcast if status changed
                if current_status != last_status:
                    message = SystemStatusMessage(
                        type="system_status",
                        timestamp=datetime.now().isoformat(),
                        hardware_status=hardware_status,
                        test_running=current_status["test_running"],
                        emergency_stop=current_status["emergency_stop"],
                        active_test_id=current_status["active_test_id"],
                        system_load=None,
                    )

                    await manager.broadcast_to_channel("system-status", message.model_dump())
                    last_status = current_status.copy()

            except Exception as e:
                logger.error(f"Error in system status monitor: {e}")

            # Wait before next check
            await asyncio.sleep(2.0)  # 2 second polling rate

    except asyncio.CancelledError:
        logger.info("System status monitor cancelled")
    except Exception as e:
        logger.error(f"System status monitor error: {e}")


# Utility functions for broadcasting from other parts of the application


async def broadcast_test_log(
    test_id: str,
    level: str,
    message: str,
    component: Optional[str] = None,
    progress_percentage: Optional[float] = None,
):
    """Broadcast test log message to WebSocket clients"""
    log_message = TestLogMessage(
        type="test_log",
        timestamp=datetime.now().isoformat(),
        test_id=test_id,
        level=level,
        message=message,
        component=component,
        progress_percentage=progress_percentage,
    )

    await manager.broadcast_to_channel("test-logs", log_message.model_dump())


async def broadcast_test_progress(
    test_id: str,
    status: str,
    progress_percentage: float,
    current_step: str,
    measurements_completed: int,
    total_measurements: int,
    estimated_remaining_seconds: Optional[float] = None,
    current_temperature: Optional[float] = None,
    current_position: Optional[float] = None,
):
    """Broadcast test progress update to WebSocket clients"""
    progress_message = TestProgressMessage(
        type="test_progress",
        timestamp=datetime.now().isoformat(),
        test_id=test_id,
        status=status,
        progress_percentage=progress_percentage,
        current_step=current_step,
        measurements_completed=measurements_completed,
        total_measurements=total_measurements,
        estimated_remaining_seconds=estimated_remaining_seconds,
        current_temperature=current_temperature,
        current_position=current_position,
    )

    await manager.broadcast_to_channel("test-logs", progress_message.model_dump())


async def broadcast_hardware_event(
    hardware_type: str, event_type: str, message: str, data: Optional[dict] = None
):
    """Broadcast hardware event to WebSocket clients"""
    event_message = HardwareEventMessage(
        type="hardware_event",
        timestamp=datetime.now().isoformat(),
        hardware_type=hardware_type,
        event_type=event_type,
        message=message,
        data=data,
    )

    await manager.broadcast_to_channel("system-status", event_message.model_dump())
