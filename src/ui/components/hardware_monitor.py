"""
Hardware Status Monitoring Component
Magic MCP Generated - Real-time hardware monitoring with modern UI patterns
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json

from domain.enums.hardware_status import HardwareStatus


class AlertSeverity(Enum):
    """Alert severity levels for hardware monitoring"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HardwareAlert:
    """Hardware alert with timestamp and context"""
    device_id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MonitoringMetrics:
    """Hardware monitoring metrics"""
    uptime_percentage: float
    response_time_ms: float
    error_count: int
    last_communication: datetime
    health_score: float  # 0-100


@dataclass
class MonitoredDevice:
    """Simple device structure for monitoring purposes"""
    device_id: str
    device_type: str
    vendor: str
    model: Optional[str]
    status: HardwareStatus
    connection_info: str


class HardwareMonitorComponent:
    """
    Real-time hardware monitoring component with:
    - Live status updates
    - Performance metrics tracking
    - Alert management
    - Responsive grid layout
    - Accessibility features
    """
    
    def __init__(self, refresh_interval: int = 2000):
        self.refresh_interval = refresh_interval
        self._devices: Dict[str, MonitoredDevice] = {}
        self._metrics: Dict[str, MonitoringMetrics] = {}
        self._alerts: List[HardwareAlert] = []
        self._subscribers: List[callable] = []
        self._monitoring_active = False
        
    async def start_monitoring(self) -> None:
        """Start real-time hardware monitoring"""
        self._monitoring_active = True
        while self._monitoring_active:
            await self._update_all_devices()
            await asyncio.sleep(self.refresh_interval / 1000)
            
    def stop_monitoring(self) -> None:
        """Stop hardware monitoring"""
        self._monitoring_active = False
        
    def register_device(self, device: MonitoredDevice) -> None:
        """Register device for monitoring"""
        device_id = device.device_id
        self._devices[device_id] = device
        self._metrics[device_id] = MonitoringMetrics(
            uptime_percentage=0.0,
            response_time_ms=0.0,
            error_count=0,
            last_communication=datetime.now(),
            health_score=100.0
        )
        self._notify_subscribers('device_registered', device_id)
        
    async def _update_all_devices(self) -> None:
        """Update status for all registered devices"""
        for device_id, device in self._devices.items():
            try:
                await self._update_device_status(device_id, device)
            except Exception as e:
                self._create_alert(
                    device_id,
                    AlertSeverity.ERROR,
                    f"Failed to update device status: {str(e)}"
                )
                
    async def _update_device_status(self, device_id: str, device: MonitoredDevice) -> None:
        """Update individual device status and metrics"""
        start_time = datetime.now()
        
        try:
            # Simulate device health check
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Update metrics
            metrics = self._metrics[device_id]
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            metrics.response_time_ms = response_time
            metrics.last_communication = datetime.now()
            
            # Calculate health score based on various factors
            health_score = self._calculate_health_score(device_id, metrics)
            metrics.health_score = health_score
            
            # Generate alerts based on health score
            if health_score < 30:
                self._create_alert(
                    device_id,
                    AlertSeverity.CRITICAL,
                    f"Device health critical: {health_score:.1f}%"
                )
            elif health_score < 60:
                self._create_alert(
                    device_id,
                    AlertSeverity.WARNING,
                    f"Device health degraded: {health_score:.1f}%"
                )
                
            self._notify_subscribers('device_updated', device_id)
            
        except Exception as e:
            metrics = self._metrics[device_id]
            metrics.error_count += 1
            self._create_alert(
                device_id,
                AlertSeverity.ERROR,
                f"Device communication failed: {str(e)}"
            )
            
    def _calculate_health_score(self, device_id: str, metrics: MonitoringMetrics) -> float:
        """Calculate device health score (0-100)"""
        base_score = 100.0
        
        # Deduct points for high response time
        if metrics.response_time_ms > 1000:
            base_score -= 20
        elif metrics.response_time_ms > 500:
            base_score -= 10
            
        # Deduct points for errors
        error_penalty = min(metrics.error_count * 5, 30)
        base_score -= error_penalty
        
        # Deduct points for old communication
        time_since_comm = datetime.now() - metrics.last_communication
        if time_since_comm > timedelta(minutes=5):
            base_score -= 40
        elif time_since_comm > timedelta(minutes=1):
            base_score -= 15
            
        return max(0.0, base_score)
        
    def _create_alert(self, device_id: str, severity: AlertSeverity, message: str) -> None:
        """Create new hardware alert"""
        alert = HardwareAlert(
            device_id=device_id,
            severity=severity,
            message=message,
            timestamp=datetime.now()
        )
        self._alerts.append(alert)
        self._notify_subscribers('alert_created', alert)
        
        # Keep only last 100 alerts
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]
            
    def get_device_grid_data(self) -> List[Dict[str, Any]]:
        """Get device data formatted for grid display"""
        grid_data = []
        
        for device_id, device in self._devices.items():
            metrics = self._metrics.get(device_id)
            if not metrics:
                continue
                
            # Get recent alerts for this device
            recent_alerts = [
                alert for alert in self._alerts[-10:]
                if alert.device_id == device_id and not alert.resolved
            ]
            
            grid_data.append({
                'device_id': device_id,
                'name': f"{device.vendor} {device.model or device.device_type}",
                'type': device.device_type,
                'status': device.status.value,
                'health_score': metrics.health_score,
                'response_time': metrics.response_time_ms,
                'last_seen': metrics.last_communication.isoformat(),
                'error_count': metrics.error_count,
                'alert_count': len(recent_alerts),
                'status_color': self._get_status_color(device.status, metrics.health_score)
            })
            
        return sorted(grid_data, key=lambda x: x['health_score'], reverse=True)
        
    def _get_status_color(self, status: HardwareStatus, health_score: float) -> str:
        """Get color based on status and health score"""
        if status == HardwareStatus.DISCONNECTED:
            return 'error'
        elif health_score < 30:
            return 'error'
        elif health_score < 60:
            return 'warning'
        elif status == HardwareStatus.CONNECTED:
            return 'success'
        else:
            return 'info'
            
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary for dashboard"""
        active_alerts = [a for a in self._alerts if not a.resolved]
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([
                a for a in active_alerts if a.severity == severity
            ])
            
        return {
            'total_active': len(active_alerts),
            'critical': severity_counts['critical'],
            'error': severity_counts['error'],
            'warning': severity_counts['warning'],
            'info': severity_counts['info'],
            'last_alert': active_alerts[-1].timestamp.isoformat() if active_alerts else None
        }
        
    def render_monitoring_dashboard(self) -> str:
        """Render ASCII monitoring dashboard"""
        devices = self.get_device_grid_data()
        alerts = self.get_alert_summary()
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        Hardware Monitoring Dashboard                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Alert Summary                                                                ║
║ ────────────────────────────────────────────────────────────────────────────║
║ Active: {alerts['total_active']:>2} │ Critical: {alerts['critical']:>2} │ Error: {alerts['error']:>2} │ Warning: {alerts['warning']:>2} │ Info: {alerts['info']:>2} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Device Status Grid                                                           ║
║ ────────────────────────────────────────────────────────────────────────────║
║ Device ID         │ Type      │ Status    │ Health │ Response │ Alerts      ║
║ ────────────────────────────────────────────────────────────────────────────║
"""
        
        if not devices:
            dashboard += "║ No devices registered for monitoring                                        ║\n"
        else:
            for device in devices[:10]:  # Show top 10 devices
                health_icon = self._get_health_icon(device['health_score'])
                status_icon = self._get_status_icon(device['status'])
                
                dashboard += (
                    f"║ {device['device_id'][:16]:>16} │ "
                    f"{device['type'][:8]:>8} │ "
                    f"{status_icon} {device['status'][:6]:>6} │ "
                    f"{health_icon} {device['health_score']:>4.0f}% │ "
                    f"{device['response_time']:>6.0f}ms │ "
                    f"{device['alert_count']:>6} ║\n"
                )
                
        dashboard += "╚══════════════════════════════════════════════════════════════════════════════╝"
        return dashboard
        
    def _get_health_icon(self, health_score: float) -> str:
        """Get health icon based on score"""
        if health_score >= 80:
            return '🟢'
        elif health_score >= 60:
            return '🟡'
        elif health_score >= 30:
            return '🟠'
        else:
            return '🔴'
            
    def _get_status_icon(self, status: str) -> str:
        """Get status icon"""
        icons = {
            'CONNECTED': '✅',
            'DISCONNECTED': '❌',
            'ERROR': '⚠️',
            'CONNECTING': '🔧',
            'UNKNOWN': '❓'
        }
        return icons.get(status, '❓')
        
    def subscribe(self, callback: callable) -> None:
        """Subscribe to monitoring events"""
        self._subscribers.append(callback)
        
    def _notify_subscribers(self, event_type: str, data: Any) -> None:
        """Notify all subscribers of events"""
        for subscriber in self._subscribers:
            try:
                subscriber(event_type, data)
            except Exception as e:
                print(f"Monitoring subscriber error: {e}")
                
    def export_metrics(self) -> Dict[str, Any]:
        """Export metrics for external monitoring systems"""
        return {
            'devices': {
                device_id: asdict(metrics)
                for device_id, metrics in self._metrics.items()
            },
            'alerts': [
                {
                    'device_id': alert.device_id,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'resolved': alert.resolved
                }
                for alert in self._alerts[-50:]  # Last 50 alerts
            ],
            'summary': {
                'total_devices': len(self._devices),
                'online_devices': len([
                    d for d in self._devices.values()
                    if d.status == HardwareStatus.CONNECTED
                ]),
                'average_health': sum(
                    m.health_score for m in self._metrics.values()
                ) / len(self._metrics) if self._metrics else 0,
                'last_update': datetime.now().isoformat()
            }
        }


# Real-time WebSocket integration (simulation)
class WebSocketManager:
    """WebSocket manager for real-time updates"""
    
    def __init__(self, monitor: HardwareMonitorComponent):
        self.monitor = monitor
        self.connections: List[Any] = []
        
    async def broadcast_update(self, event_type: str, data: Any) -> None:
        """Broadcast update to all connected clients"""
        message = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Simulate WebSocket broadcast
        print(f"WebSocket broadcast: {json.dumps(message, default=str)}")
        
    def handle_monitoring_event(self, event_type: str, data: Any) -> None:
        """Handle monitoring events for WebSocket broadcast"""
        asyncio.create_task(self.broadcast_update(event_type, data))