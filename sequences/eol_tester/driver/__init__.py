"""
Driver package for EOL Tester standalone hardware communication.

Provides:
- Serial communication (LoadCell, MCU)
- TCP communication (Power Supply)
- Ajinextek AXL wrapper (Robot, Digital I/O) - Windows only
"""

from __future__ import annotations

__all__ = [
    "serial",
    "tcp",
    "ajinextek",
]
