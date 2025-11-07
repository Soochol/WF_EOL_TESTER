"""
VISA Communication Constants

Constants for PyVISA-based instrument communication supporting
TCP/IP, USB-TMC, and GPIB interfaces.
"""

# VISA Interface Types
INTERFACE_TCP = "tcp"
INTERFACE_USB = "usb"
INTERFACE_GPIB = "gpib"

# Resource String Templates
TCPIP_SOCKET_TEMPLATE = "TCPIP::{host}::{port}::SOCKET"
TCPIP_INSTR_TEMPLATE = "TCPIP::{host}::INSTR"
USB_INSTR_TEMPLATE = "USB::{vendor_id}::{model_code}::{serial}::INSTR"
GPIB_INSTR_TEMPLATE = "GPIB{board}::{address}::INSTR"

# Yokogawa WT1800E USB Identifiers
YOKOGAWA_VENDOR_ID = "0x0B21"
WT1800E_MODEL_CODE = "0x0039"

# Communication Settings
DEFAULT_TIMEOUT_MS = 5000  # 5 seconds
DEFAULT_READ_TERMINATION = "\n"
DEFAULT_WRITE_TERMINATION = "\n"
DEFAULT_ENCODING = "ascii"

# Buffer Sizes
DEFAULT_CHUNK_SIZE = 20480  # 20KB read chunk size
