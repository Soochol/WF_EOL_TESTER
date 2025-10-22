# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for WF EOL Tester
Builds a Windows GUI executable with all necessary dependencies
"""

import sys
from pathlib import Path

# Project root directory
root_dir = Path('.').absolute()
src_dir = root_dir / 'src'

# Data files to include in the build
datas = [
    # Configuration files
    ('configuration', 'configuration'),
    # UI resources (icons, images, etc.)
    ('src/ui/gui/resources/icons', 'ui/gui/resources/icons'),
    # AXL Driver library (64-bit)
    ('src/driver/ajinextek/AXL(Library)/Library/64Bit/AXL.dll', 'driver/AXL/'),
    ('src/driver/ajinextek/AXL(Library)/Library/64Bit/EzBasicAxl.dll', 'driver/AXL/'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    # PySide6 GUI framework
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',  # SVG support for icons
    # Third-party libraries
    'loguru',
    'yaml',
    'serial',
    'asyncio',
    'numpy',
    'scipy',
    'pandas',
    'matplotlib',
    'openpyxl',
    # dependency_injector and all its submodules
    'dependency_injector',
    'dependency_injector.containers',
    'dependency_injector.providers',
    'dependency_injector.errors',
    'dependency_injector.wiring',
    'dependency_injector.resources',
    'dependency_injector.schema',
    'dependency_injector._cwiring',
    # Application services (dynamically loaded by DI)
    'application.services.core',
    'application.services.core.configuration_service',
    'application.services.core.configuration_validator',
    'application.services.core.exception_handler',
    'application.services.core.repository_service',
    'application.services.hardware_facade',
    'application.services.hardware_facade.hardware_service_facade',
    'application.services.industrial',
    'application.services.industrial.industrial_system_manager',
    'application.services.industrial.safety_alert_service',
    'application.services.industrial.tower_lamp_service',
    'application.services.monitoring',
    'application.services.monitoring.button_monitoring_service',
    'application.services.monitoring.emergency_stop_service',
    'application.services.monitoring.power_monitor',
    'application.services.statistics',
    'application.services.statistics.eol_statistics_service',
    'application.services.statistics.unit_converter',
    'application.services.test',
    'application.services.test.test_result_evaluator',
    # Logging services (dynamically loaded by DI)
    'application.services.logging',
    'application.services.logging.db_logger_service',
    # Application use cases (dynamically loaded by DI)
    'application.use_cases.common',
    'application.use_cases.common.base_use_case',
    'application.use_cases.common.command_result_patterns',
    'application.use_cases.common.execution_context',
    'application.use_cases.eol_force_test',
    'application.use_cases.eol_force_test.configuration_loader',
    'application.use_cases.eol_force_test.constants',
    'application.use_cases.eol_force_test.hardware_test_executor',
    'application.use_cases.eol_force_test.main_use_case',
    'application.use_cases.eol_force_test.measurement_converter',
    'application.use_cases.eol_force_test.result_evaluator',
    'application.use_cases.eol_force_test.test_entity_factory',
    'application.use_cases.eol_force_test.test_state_manager',
    'application.use_cases.heating_cooling_time_test',
    'application.use_cases.heating_cooling_time_test.csv_logger',
    'application.use_cases.heating_cooling_time_test.hardware_setup_service',
    'application.use_cases.heating_cooling_time_test.input',
    'application.use_cases.heating_cooling_time_test.main_use_case',
    'application.use_cases.heating_cooling_time_test.result',
    'application.use_cases.heating_cooling_time_test.statistics_calculator',
    'application.use_cases.heating_cooling_time_test.test_cycle_executor',
    'application.use_cases.robot_operations',
    'application.use_cases.robot_operations.digital_io_setup_service',
    'application.use_cases.robot_operations.input',
    'application.use_cases.robot_operations.main_use_case',
    'application.use_cases.robot_operations.result',
    'application.use_cases.robot_operations.robot_connection_service',
    'application.use_cases.system_tests',
    'application.use_cases.system_tests.input',
    'application.use_cases.system_tests.main_use_case',
    'application.use_cases.system_tests.mcu_connection_service',
    'application.use_cases.system_tests.result',
    'application.use_cases.system_tests.test_sequence_executor',
    # Infrastructure implementations (dynamically loaded by DI)
    'infrastructure.factories',
    'infrastructure.factories.hardware_factory',
    'infrastructure.implementation.configuration',
    'infrastructure.implementation.configuration.yaml_configuration',
    'infrastructure.implementation.configuration.yaml_container_configuration',
    'infrastructure.implementation.repositories',
    'infrastructure.implementation.repositories.json_result_repository',
    'infrastructure.implementation.repositories.sqlite_log_repository',
    # Database (dynamically loaded by DI)
    'infrastructure.database',
    'infrastructure.database.db_manager',
    # Hardware implementations - Digital I/O
    'infrastructure.implementation.hardware.digital_io.ajinextek',
    'infrastructure.implementation.hardware.digital_io.ajinextek.ajinextek_dio',
    'infrastructure.implementation.hardware.digital_io.ajinextek.constants',
    'infrastructure.implementation.hardware.digital_io.ajinextek.error_codes',
    'infrastructure.implementation.hardware.digital_io.mock',
    'infrastructure.implementation.hardware.digital_io.mock.mock_dio',
    'infrastructure.implementation.hardware.digital_io.mock.mock_digital_io',
    # Hardware implementations - Loadcell
    'infrastructure.implementation.hardware.loadcell.bs205',
    'infrastructure.implementation.hardware.loadcell.bs205.bs205_loadcell',
    'infrastructure.implementation.hardware.loadcell.bs205.constants',
    'infrastructure.implementation.hardware.loadcell.bs205.error_codes',
    'infrastructure.implementation.hardware.loadcell.mock',
    'infrastructure.implementation.hardware.loadcell.mock.mock_loadcell',
    # Hardware implementations - MCU
    'infrastructure.implementation.hardware.mcu.lma',
    'infrastructure.implementation.hardware.mcu.lma.constants',
    'infrastructure.implementation.hardware.mcu.lma.error_codes',
    'infrastructure.implementation.hardware.mcu.lma.lma_mcu',
    'infrastructure.implementation.hardware.mcu.mock',
    'infrastructure.implementation.hardware.mcu.mock.mock_mcu',
    # Hardware implementations - Power Supply
    'infrastructure.implementation.hardware.power.oda',
    'infrastructure.implementation.hardware.power.oda.oda_power',
    'infrastructure.implementation.hardware.power.mock',
    'infrastructure.implementation.hardware.power.mock.mock_power',
    # Hardware implementations - Robot
    'infrastructure.implementation.hardware.robot.ajinextek',
    'infrastructure.implementation.hardware.robot.ajinextek.ajinextek_robot',
    'infrastructure.implementation.hardware.robot.ajinextek.axl_wrapper',
    'infrastructure.implementation.hardware.robot.ajinextek.constants',
    'infrastructure.implementation.hardware.robot.ajinextek.error_codes',
    'infrastructure.implementation.hardware.robot.mock',
    'infrastructure.implementation.hardware.robot.mock.mock_robot',
    # Hardware common
    'infrastructure.implementation.hardware.common',
    'infrastructure.implementation.hardware.common.disconnect_mixin',
    # UI widgets (dynamically loaded)
    'ui.gui.widgets.notifications',
    'ui.gui.widgets.notifications.toast_notification',
    'ui.gui.widgets.notifications.toast_manager',
    'ui.gui.widgets.notifications.toast_animations',
    # UI resources
    'ui.gui.resources',
]

# Analysis: Determine what to bundle
a = Analysis(
    ['src/main_gui.py'],
    pathex=[str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ: Compress Python bytecode
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE: Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WF_EOL_Tester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI mode (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='src/ui/gui/resources/icons/app.ico',  # Uncomment if icon exists
)

# COLLECT: Bundle everything into a directory
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WF_EOL_Tester',
)
