"""
Health monitoring implementation for serial connections.

Provides comprehensive health assessment and auto-recovery capabilities.
Focuses solely on monitoring connection health and suggesting improvements.
"""

import time
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from ..core.interfaces import IHealthMonitor, ISerialTransport, ISerialBuffer, ISerialReader
from ..exceptions import SerialCommunicationError


class HealthMonitor(IHealthMonitor):
    """Comprehensive health monitoring for serial communication."""
    
    def __init__(self, transport: ISerialTransport, buffer: ISerialBuffer, 
                 reader: Optional[ISerialReader] = None):
        """
        Initialize health monitor.
        
        Args:
            transport: Serial transport to monitor
            buffer: Buffer to monitor
            reader: Optional reader to monitor
        """
        self._transport = transport
        self._buffer = buffer
        self._reader = reader
        
        # Health thresholds
        self._max_idle_time = 30.0  # seconds
        self._max_buffer_utilization = 80.0  # percent
        self._min_success_rate = 90.0  # percent
        self._max_error_rate = 5.0  # errors per minute
        
        # Health callback
        self._health_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        
        # Health history
        self._last_health_check = time.time()
        self._health_history: List[Dict[str, Any]] = []
        self._max_history_size = 100
        
        # Recovery attempts
        self._recovery_attempts = 0
        self._last_recovery_time = None
        self._max_recovery_attempts = 3
        self._recovery_cooldown = 60.0  # seconds
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status.
        
        Returns:
            Dict with health information and recommendations
        """
        current_time = time.time()
        
        # Basic connectivity
        connected = self._transport.is_connected()
        
        # Transport stats
        transport_stats = self._transport.get_stats()
        last_activity = transport_stats.get('last_activity', 0)
        time_since_activity = current_time - last_activity if last_activity > 0 else float('inf')
        
        # Buffer stats
        buffer_stats = self._buffer.get_stats()
        buffer_utilization = buffer_stats.get('utilization_percent', 0)
        
        # Reader stats (if available)
        reader_stats = {}
        reader_alive = False
        if self._reader:
            reader_stats = self._reader.get_stats()
            reader_alive = reader_stats.get('running', False)
        
        # Calculate health scores
        connectivity_score = self._calculate_connectivity_score(connected, time_since_activity)
        performance_score = self._calculate_performance_score(transport_stats, buffer_stats, reader_stats)
        reliability_score = self._calculate_reliability_score(transport_stats, reader_stats)
        
        # Overall health score (weighted average)
        overall_score = (
            connectivity_score * 0.4 +
            performance_score * 0.3 +
            reliability_score * 0.3
        )
        
        # Determine health status
        if overall_score >= 90:
            health_status = "excellent"
        elif overall_score >= 75:
            health_status = "good"
        elif overall_score >= 50:
            health_status = "fair"
        elif overall_score >= 25:
            health_status = "poor"
        else:
            health_status = "critical"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            connected, time_since_activity, buffer_utilization,
            transport_stats, reader_stats
        )
        
        # Build status report
        status = {
            'timestamp': current_time,
            'healthy': overall_score >= 75,
            'health_status': health_status,
            'overall_score': overall_score,
            'scores': {
                'connectivity': connectivity_score,
                'performance': performance_score,
                'reliability': reliability_score
            },
            'connection': {
                'connected': connected,
                'port': transport_stats.get('port', 'unknown'),
                'baudrate': transport_stats.get('baudrate', 0),
                'time_since_last_activity': time_since_activity
            },
            'buffer': {
                'utilization_percent': buffer_utilization,
                'current_size': buffer_stats.get('current_size', 0),
                'max_size': buffer_stats.get('max_size', 0),
                'overflow_count': buffer_stats.get('overflow_count', 0)
            },
            'reader': {
                'active': reader_alive,
                'error_count': reader_stats.get('error_count', 0),
                'read_rate': reader_stats.get('read_rate_per_second', 0),
                'byte_rate': reader_stats.get('byte_rate_per_second', 0)
            },
            'transport': {
                'bytes_sent': transport_stats.get('bytes_sent', 0),
                'bytes_received': transport_stats.get('bytes_received', 0),
                'connection_count': transport_stats.get('connection_count', 0)
            },
            'recommendations': recommendations,
            'recovery': {
                'attempts': self._recovery_attempts,
                'last_attempt': self._last_recovery_time,
                'can_recover': self._can_attempt_recovery()
            }
        }
        
        # Store in history
        self._store_health_record(status)
        
        # Call health callback if status changed significantly
        if self._health_callback:
            try:
                self._health_callback(status)
            except Exception as e:
                logger.error(f"Error in health callback: {e}")
        
        self._last_health_check = current_time
        return status
    
    def auto_recover(self) -> bool:
        """
        Attempt automatic recovery from connection issues.
        
        Returns:
            bool: True if recovery was successful
        """
        if not self._can_attempt_recovery():
            logger.warning("Cannot attempt recovery: cooldown period or max attempts reached")
            return False
        
        self._recovery_attempts += 1
        self._last_recovery_time = time.time()
        
        logger.info(f"Attempting auto-recovery (attempt {self._recovery_attempts})")
        
        try:
            # Step 1: Stop reader if running
            if self._reader and self._reader.is_reading():
                logger.debug("Stopping reader for recovery")
                self._reader.stop_reading()
                time.sleep(0.1)
            
            # Step 2: Clear buffers
            if hasattr(self._transport, 'flush_buffers'):
                logger.debug("Flushing transport buffers")
                self._transport.flush_buffers()
            
            self._buffer.clear()
            logger.debug("Cleared data buffer")
            
            # Step 3: Reconnect if not connected
            if not self._transport.is_connected():
                logger.debug("Attempting to reconnect transport")
                
                # Disconnect first to ensure clean state
                self._transport.disconnect()
                time.sleep(0.5)
                
                # Get last known configuration
                stats = self._transport.get_stats()
                config = stats.get('config', {})
                
                if config.get('port'):
                    self._transport.connect(**config)
                    
                    if self._transport.is_connected():
                        logger.info("Transport reconnected successfully")
                    else:
                        logger.error("Failed to reconnect transport")
                        return False
                else:
                    logger.error("No configuration available for reconnection")
                    return False
            
            # Step 4: Restart reader if available
            if self._reader and self._transport.is_connected():
                logger.debug("Restarting reader")
                self._reader.start_reading()
                time.sleep(0.1)
                
                if not self._reader.is_reading():
                    logger.warning("Failed to restart reader")
            
            # Step 5: Verify recovery
            time.sleep(1.0)  # Give time for stabilization
            
            status = self.get_status()
            recovery_successful = (
                status['connection']['connected'] and
                status['overall_score'] > 50
            )
            
            if recovery_successful:
                logger.info("Auto-recovery completed successfully")
                return True
            else:
                logger.warning("Auto-recovery failed: connection still unhealthy")
                return False
        
        except Exception as e:
            logger.error(f"Auto-recovery failed with exception: {e}")
            return False
    
    def set_health_callback(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        """
        Set callback for health status changes.
        
        Args:
            callback: Function called when health status changes
        """
        self._health_callback = callback
        logger.debug(f"Health callback {'set' if callback else 'cleared'}")
    
    def configure_thresholds(self, max_idle_time: Optional[float] = None,
                           max_buffer_utilization: Optional[float] = None,
                           min_success_rate: Optional[float] = None,
                           max_error_rate: Optional[float] = None) -> None:
        """
        Configure health monitoring thresholds.
        
        Args:
            max_idle_time: Maximum idle time before warning (seconds)
            max_buffer_utilization: Maximum buffer utilization before warning (percent)
            min_success_rate: Minimum success rate before warning (percent)
            max_error_rate: Maximum error rate before warning (errors per minute)
        """
        if max_idle_time is not None:
            self._max_idle_time = max(0, max_idle_time)
        if max_buffer_utilization is not None:
            self._max_buffer_utilization = max(0, min(100, max_buffer_utilization))
        if min_success_rate is not None:
            self._min_success_rate = max(0, min(100, min_success_rate))
        if max_error_rate is not None:
            self._max_error_rate = max(0, max_error_rate)
        
        logger.info("Health monitoring thresholds updated")
    
    def get_health_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get health monitoring history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of health status records
        """
        if limit is None:
            return self._health_history.copy()
        else:
            return self._health_history[-limit:].copy()
    
    def _calculate_connectivity_score(self, connected: bool, time_since_activity: float) -> float:
        """Calculate connectivity health score (0-100)."""
        if not connected:
            return 0.0
        
        if time_since_activity <= self._max_idle_time:
            return 100.0
        elif time_since_activity <= self._max_idle_time * 2:
            return 75.0
        elif time_since_activity <= self._max_idle_time * 5:
            return 50.0
        else:
            return 25.0
    
    def _calculate_performance_score(self, transport_stats: dict, 
                                   buffer_stats: dict, reader_stats: dict) -> float:
        """Calculate performance health score (0-100)."""
        score = 100.0
        
        # Buffer utilization penalty
        buffer_util = buffer_stats.get('utilization_percent', 0)
        if buffer_util > self._max_buffer_utilization:
            score -= min(30, (buffer_util - self._max_buffer_utilization) * 0.5)
        
        # Buffer overflow penalty
        overflow_count = buffer_stats.get('overflow_count', 0)
        if overflow_count > 0:
            score -= min(20, overflow_count * 2)
        
        # Reader performance
        if reader_stats:
            error_rate = reader_stats.get('error_rate_per_second', 0) * 60  # per minute
            if error_rate > self._max_error_rate:
                score -= min(25, (error_rate - self._max_error_rate) * 2)
        
        return max(0.0, score)
    
    def _calculate_reliability_score(self, transport_stats: dict, reader_stats: dict) -> float:
        """Calculate reliability health score (0-100)."""
        score = 100.0
        
        # Connection stability
        connection_count = transport_stats.get('connection_count', 1)
        if connection_count > 1:
            score -= min(20, (connection_count - 1) * 5)
        
        # Reader reliability
        if reader_stats:
            if not reader_stats.get('running', False):
                score -= 30
            
            error_count = reader_stats.get('error_count', 0)
            if error_count > 0:
                score -= min(25, error_count * 3)
        
        return max(0.0, score)
    
    def _generate_recommendations(self, connected: bool, time_since_activity: float,
                                buffer_utilization: float, transport_stats: dict,
                                reader_stats: dict) -> List[str]:
        """Generate health improvement recommendations."""
        recommendations = []
        
        if not connected:
            recommendations.append("Reconnect to serial port")
            recommendations.append("Check cable connections and port availability")
        
        if time_since_activity > self._max_idle_time:
            recommendations.append("Check if device is sending data")
            recommendations.append("Verify communication protocol")
        
        if buffer_utilization > self._max_buffer_utilization:
            recommendations.append("Increase buffer size or improve data processing speed")
            recommendations.append("Check for buffer overflow issues")
        
        overflow_count = self._buffer.get_stats().get('overflow_count', 0)
        if overflow_count > 0:
            recommendations.append("Data loss detected due to buffer overflow")
            recommendations.append("Consider increasing buffer size or processing data faster")
        
        if reader_stats:
            if not reader_stats.get('running', False):
                recommendations.append("Start background reader for continuous data collection")
            
            error_rate = reader_stats.get('error_rate_per_second', 0) * 60
            if error_rate > self._max_error_rate:
                recommendations.append("High error rate detected in reader")
                recommendations.append("Check connection stability and cable quality")
        
        connection_count = transport_stats.get('connection_count', 1)
        if connection_count > 3:
            recommendations.append("Multiple reconnections detected")
            recommendations.append("Investigate connection stability issues")
        
        if not recommendations:
            recommendations.append("All systems operating normally")
        
        return recommendations
    
    def _can_attempt_recovery(self) -> bool:
        """Check if auto-recovery can be attempted."""
        if self._recovery_attempts >= self._max_recovery_attempts:
            return False
        
        if self._last_recovery_time is None:
            return True
        
        time_since_recovery = time.time() - self._last_recovery_time
        return time_since_recovery >= self._recovery_cooldown
    
    def _store_health_record(self, status: Dict[str, Any]) -> None:
        """Store health status in history."""
        # Keep only essential data for history
        record = {
            'timestamp': status['timestamp'],
            'health_status': status['health_status'],
            'overall_score': status['overall_score'],
            'connected': status['connection']['connected'],
            'buffer_utilization': status['buffer']['utilization_percent']
        }
        
        self._health_history.append(record)
        
        # Trim history if too large
        if len(self._health_history) > self._max_history_size:
            self._health_history = self._health_history[-self._max_history_size:]