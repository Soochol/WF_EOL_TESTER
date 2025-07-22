"""
TCP/IP Communication Driver

Generic TCP/IP communication driver for network-based devices.
Supports command/response protocols commonly used in test equipment.
"""

import socket
import time
from typing import Optional

from loguru import logger

from .constants import (
    DEFAULT_PORT, DEFAULT_TIMEOUT, CONNECT_TIMEOUT, 
    COMMAND_TERMINATOR, RESPONSE_TERMINATOR,
    COMMAND_BUFFER_SIZE, MAX_COMMAND_LENGTH,
    RECV_BUFFER_SIZE, FLUSH_TIMEOUT
)
from .exceptions import TCPError, TCPConnectionError, TCPCommunicationError, TCPTimeoutError


class TCPCommunication:
    """Generic TCP/IP communication handler for network devices"""
    
    def __init__(self, host: str, port: int = DEFAULT_PORT, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize TCP communication
        
        Args:
            host: IP address of device
            port: TCP port (default: 5025)
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.is_connected = False
        
    def connect(self) -> None:
        """
        Establish TCP connection
        
        Raises:
            TCPConnectionError: If connection fails
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(CONNECT_TIMEOUT)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(self.timeout)  # Set operational timeout
            self.is_connected = True
            logger.info(f"TCP connected to {self.host}:{self.port}")
            
        except socket.error as e:
            logger.error(f"TCP connection failed ({type(e).__name__}): {e}")
            self.is_connected = False
            raise TCPConnectionError(
                f"Failed to connect to {self.host}:{self.port}",
                host=self.host,
                port=self.port,
                details=str(e)
            )
    
    def disconnect(self) -> bool:
        """
        Close TCP connection
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
            self.is_connected = False
            logger.info(f"TCP disconnected from {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error during TCP disconnect: {e}")
            return False
    
    def send_command(self, command: str) -> None:
        """
        Send command to device
        
        Args:
            command: Command string
            
        Raises:
            TCPCommunicationError: If command send fails
        """
        if not self.is_connected or not self.socket:
            logger.error("TCP not connected to device")
            raise TCPConnectionError(
                "Not connected to device",
                host=self.host,
                port=self.port
            )
            
        try:
            # Add terminator if not present
            if not command.endswith(COMMAND_TERMINATOR):
                command += COMMAND_TERMINATOR
                
            # Check command length
            if len(command.encode()) > COMMAND_BUFFER_SIZE:
                logger.error(f"Command too long: {len(command.encode())} bytes (max {COMMAND_BUFFER_SIZE})")
                raise TCPCommunicationError(
                    f"Command too long: {len(command.encode())} bytes (max {COMMAND_BUFFER_SIZE})",
                    host=self.host,
                    port=self.port
                )
                
            self.socket.send(command.encode())
            logger.debug(f"TCP sent: {repr(command)}")
            
        except socket.error as e:
            logger.error(f"Failed to send TCP command '{command}': {e}")
            self.is_connected = False
            raise TCPCommunicationError(
                f"Failed to send command '{command}'",
                host=self.host,
                port=self.port,
                details=str(e)
            )
    
    def receive_response(self) -> str:
        """
        Receive response from device
        
        Returns:
            str: Response string
            
        Raises:
            TCPCommunicationError: If response reception fails
        """
        if not self.is_connected or not self.socket:
            logger.error("TCP not connected to device")
            raise TCPConnectionError(
                "Not connected to device",
                host=self.host,
                port=self.port
            )
            
        try:
            response_data = b""
            start_time = time.time()
            
            while time.time() - start_time < self.timeout:
                try:
                    data = self.socket.recv(RECV_BUFFER_SIZE)
                    if not data:
                        break
                        
                    response_data += data
                    
                    # Check if we have complete response
                    if RESPONSE_TERMINATOR.encode() in response_data:
                        break
                        
                except socket.timeout:
                    break
                    
            if response_data:
                response = response_data.decode().strip()
                logger.debug(f"TCP received: {repr(response)}")
                return response
            else:
                logger.warning("No TCP response received")
                raise TCPTimeoutError(
                    "No response received within timeout",
                    host=self.host,
                    port=self.port
                )
                
        except socket.error as e:
            logger.error(f"Failed to receive TCP response: {e}")
            self.is_connected = False
            raise TCPCommunicationError(
                "Failed to receive response",
                host=self.host,
                port=self.port,
                details=str(e)
            )
    
    def query(self, command: str) -> str:
        """
        Send command and receive response
        
        Args:
            command: Query command
            
        Returns:
            str: Response string
            
        Raises:
            TCPCommunicationError: If query fails
        """
        self.send_command(command)
        return self.receive_response()
    
    def flush_buffer(self) -> None:
        """Clear any pending data in receive buffer"""
        if not self.is_connected or not self.socket:
            return
            
        try:
            original_timeout = self.socket.gettimeout()
            self.socket.settimeout(FLUSH_TIMEOUT)
            
            while True:
                try:
                    data = self.socket.recv(RECV_BUFFER_SIZE)
                    if not data:
                        break
                except socket.timeout:
                    break
                    
        except Exception:
            pass
        finally:
            # Restore original timeout
            if self.socket:
                self.socket.settimeout(original_timeout)
    
    def test_connection(self) -> bool:
        """
        Test if connection is still alive
        
        Returns:
            bool: True if connection is working
        """
        if not self.is_connected:
            return False
            
        try:
            # Send identity query as connection test (common SCPI command)
            response = self.query("*IDN?")
            return True
            
        except Exception as e:
            logger.error(f"TCP connection test failed: {e}")
            self.is_connected = False
            return False
    
    def reconnect(self) -> None:
        """
        Attempt to reconnect
        
        Raises:
            TCPConnectionError: If reconnection fails
        """
        logger.info(f"Attempting to reconnect to {self.host}:{self.port}...")
        self.disconnect()
        time.sleep(1)  # Brief delay before reconnect
        self.connect()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False