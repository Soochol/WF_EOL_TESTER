"""
System status API routes

Provides REST endpoints for system status and health monitoring.
"""

import os
from datetime import datetime

import psutil
from fastapi import APIRouter, Depends
from loguru import logger

from src.ui.api.dependencies import DIContainer, get_container

router = APIRouter()


@router.get("/health")
async def get_health_status():
    """Get basic health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "WF EOL Tester API",
        "version": "1.0.0",
    }


@router.get("/system")
async def get_system_status():
    """Get detailed system status"""
    try:
        # CPU and memory info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Process info
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()

        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                },
            },
            "process": {
                "pid": os.getpid(),
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return {"timestamp": datetime.now().isoformat(), "error": str(e), "status": "error"}


@router.get("/hardware")
async def get_hardware_system_status(container: DIContainer = Depends(get_container)):
    """Get hardware system status"""
    try:
        hardware_services = container.hardware_service_facade()
        hardware_status = await hardware_services.get_hardware_status()

        # Calculate overall status
        all_connected = all(hardware_status.values())
        any_connected = any(hardware_status.values())

        overall_status = (
            "fully_connected"
            if all_connected
            else "partially_connected" if any_connected else "disconnected"
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "hardware_status": hardware_status,
            "overall_status": overall_status,
            "connected_count": sum(hardware_status.values()),
            "total_count": len(hardware_status),
        }

    except Exception as e:
        logger.error(f"Failed to get hardware system status: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "hardware_status": {},
            "overall_status": "error",
        }


@router.get("/configuration")
async def get_configuration_status(container: DIContainer = Depends(get_container)):
    """Get configuration system status"""
    try:
        config_service = container.configuration_service()

        # Get profile information
        current_profile = await config_service.get_active_profile_name()
        available_profiles = await config_service.list_available_profiles()
        usage_info = await config_service.get_profile_usage_info()

        # Try to load current configuration to verify it's valid
        config_valid = True
        config_error = None

        try:
            _ = await config_service.load_configuration(current_profile)
            _ = await config_service.load_hardware_config()
        except Exception as e:
            config_valid = False
            config_error = str(e)

        return {
            "timestamp": datetime.now().isoformat(),
            "current_profile": current_profile,
            "available_profiles": available_profiles,
            "profile_count": len(available_profiles),
            "configuration_valid": config_valid,
            "configuration_error": config_error,
            "usage_info": usage_info,
        }

    except Exception as e:
        logger.error(f"Failed to get configuration status: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "configuration_valid": False,
        }


@router.get("/services")
async def get_services_status(container: DIContainer = Depends(get_container)):
    """Get application services status"""
    try:
        services_status = {}

        # Test hardware service facade
        try:
            _ = container.hardware_service_facade()
            services_status["hardware_service_facade"] = "available"
        except Exception as e:
            services_status["hardware_service_facade"] = f"error: {str(e)}"

        # Test configuration service
        try:
            _ = container.configuration_service()
            services_status["configuration_service"] = "available"
        except Exception as e:
            services_status["configuration_service"] = f"error: {str(e)}"

        # Test use cases
        try:
            _ = container.eol_force_test_use_case()
            services_status["eol_force_test_use_case"] = "available"
        except Exception as e:
            services_status["eol_force_test_use_case"] = f"error: {str(e)}"

        try:
            _ = container.robot_home_use_case()
            services_status["robot_home_use_case"] = "available"
        except Exception as e:
            services_status["robot_home_use_case"] = f"error: {str(e)}"

        # Calculate overall services health
        available_services = sum(1 for status in services_status.values() if status == "available")
        total_services = len(services_status)
        services_health = (
            "healthy"
            if available_services == total_services
            else "degraded" if available_services > 0 else "unhealthy"
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "services": services_status,
            "services_health": services_health,
            "available_services": available_services,
            "total_services": total_services,
        }

    except Exception as e:
        logger.error(f"Failed to get services status: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "services_health": "error",
        }


@router.get("/comprehensive")
async def get_comprehensive_status(container: DIContainer = Depends(get_container)):
    """Get comprehensive system status"""
    try:
        # Get all status information
        system_status = await get_system_status()
        hardware_status = await get_hardware_system_status(container)
        config_status = await get_configuration_status(container)
        services_status = await get_services_status(container)

        # Calculate overall health
        health_indicators = [
            system_status.get("status") != "error",
            hardware_status.get("overall_status") != "error",
            config_status.get("configuration_valid", False),
            services_status.get("services_health") == "healthy",
        ]

        healthy_count = sum(health_indicators)
        total_indicators = len(health_indicators)

        if healthy_count == total_indicators:
            overall_health = "healthy"
        elif healthy_count >= total_indicators // 2:
            overall_health = "degraded"
        else:
            overall_health = "unhealthy"

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": overall_health,
            "health_score": f"{healthy_count}/{total_indicators}",
            "system": system_status,
            "hardware": hardware_status,
            "configuration": config_status,
            "services": services_status,
        }

    except Exception as e:
        logger.error(f"Failed to get comprehensive status: {e}")
        return {"timestamp": datetime.now().isoformat(), "overall_health": "error", "error": str(e)}
