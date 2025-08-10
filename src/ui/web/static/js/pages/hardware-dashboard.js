/**
 * Hardware Dashboard Page Manager - WF EOL Tester Web Interface
 * 
 * This module manages the main hardware dashboard including:
 * - Overview of all hardware components status
 * - Quick access to individual control panels
 * - System-wide hardware health monitoring
 * - Emergency controls and safety features
 * - Real-time status indicators
 * - Coordinated hardware management
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

import { APIClient } from '../services/api-client.js';
import { WebSocketManager } from '../services/websocket-manager.js';
import { UIManager } from '../components/ui-manager.js';

/**
 * Hardware Dashboard Page Manager
 * 
 * Manages the main hardware control dashboard with real-time status updates
 * and coordination between all hardware components.
 */
export class HardwareDashboardPageManager {
    /**
     * Initialize Hardware Dashboard Page Manager
     * @param {APIClient} apiClient - API client instance
     * @param {UIManager} uiManager - UI manager instance
     * @param {WebSocketManager} wsManager - WebSocket manager instance
     */
    constructor(apiClient, uiManager, wsManager) {
        this.apiClient = apiClient;
        this.uiManager = uiManager;
        this.wsManager = wsManager;
        
        // Hardware status tracking
        this.hardwareStatus = {
            robot: { connected: false, status: {} },
            power: { connected: false, status: {} },
            mcu: { connected: false, status: {} },
            loadcell: { connected: false, status: {} }
        };
        
        // System status
        this.systemHealth = 'unknown';
        this.connectedCount = 0;
        this.emergencyStatus = 'normal';
        
        // Update intervals
        this.statusUpdateInterval = null;
        
        // System log
        this.systemLog = [];
        this.maxLogEntries = 100;
        
        console.log('🖥️ Hardware Dashboard Page Manager initialized');
    }

    /**
     * Initialize page when activated
     */
    async init() {
        try {
            console.log('🔧 Initializing Hardware Dashboard...');
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup WebSocket subscriptions
            this.setupWebSocketSubscriptions();
            
            // Load initial status for all hardware
            await this.refreshAllStatus();
            
            // Start periodic updates
            this.startPeriodicUpdates();
            
            this.addLogEntry('info', 'SYSTEM', 'Hardware Dashboard initialized');
            
            console.log('✅ Hardware Dashboard initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize Hardware Dashboard:', error);
            this.uiManager.showNotification('Failed to initialize Hardware Dashboard', 'error');
        }
    }

    /**
     * Cleanup when page is deactivated
     */
    cleanup() {
        console.log('🧹 Cleaning up Hardware Dashboard...');
        
        // Clear intervals
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
        
        // Remove WebSocket subscriptions
        this.wsManager.unsubscribe('hardware-status');
        this.wsManager.unsubscribe('system-health');
        
        // Remove event listeners
        this.removeEventListeners();
        
        console.log('✅ Hardware Dashboard cleanup complete');
    }

    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // System controls
        document.getElementById('refresh-all-status-btn')?.addEventListener('click', 
            this.refreshAllStatus.bind(this));
        document.getElementById('emergency-stop-all-btn')?.addEventListener('click', 
            this.handleEmergencyStopAll.bind(this));
        
        // Hardware card navigation
        document.querySelectorAll('.hardware-card .btn[data-page]').forEach(button => {
            button.addEventListener('click', (event) => {
                const page = event.target.closest('button').getAttribute('data-page');
                this.navigateToControlPanel(page);
            });
        });
        
        // Quick status buttons
        document.getElementById('robot-quick-status')?.addEventListener('click', 
            () => this.showQuickStatus('robot'));
        document.getElementById('power-quick-status')?.addEventListener('click', 
            () => this.showQuickStatus('power'));
        document.getElementById('mcu-quick-status')?.addEventListener('click', 
            () => this.showQuickStatus('mcu'));
        document.getElementById('loadcell-quick-status')?.addEventListener('click', 
            () => this.showQuickStatus('loadcell'));
        
        // Log controls
        document.getElementById('hardware-clear-log-btn')?.addEventListener('click', 
            this.handleClearLog.bind(this));
        document.getElementById('hardware-export-log-btn')?.addEventListener('click', 
            this.handleExportLog.bind(this));
    }

    /**
     * Remove event listeners
     * @private
     */
    removeEventListeners() {
        const buttons = [
            'refresh-all-status-btn', 'emergency-stop-all-btn',
            'robot-quick-status', 'power-quick-status', 
            'mcu-quick-status', 'loadcell-quick-status',
            'hardware-clear-log-btn', 'hardware-export-log-btn'
        ];
        
        buttons.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                const newElement = element.cloneNode(true);
                element.parentNode.replaceChild(newElement, element);
            }
        });
        
        // Remove navigation listeners
        document.querySelectorAll('.hardware-card .btn[data-page]').forEach(button => {
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
        });
    }

    /**
     * Setup WebSocket subscriptions
     * @private
     */
    setupWebSocketSubscriptions() {
        // Subscribe to hardware status updates
        this.wsManager.subscribe('hardware-status', (data) => {
            this.handleHardwareStatusUpdate(data);
        });
        
        // Subscribe to system health updates
        this.wsManager.subscribe('system-health', (data) => {
            this.handleSystemHealthUpdate(data);
        });
        
        // Subscribe to emergency status
        this.wsManager.subscribe('emergency-status', (data) => {
            this.handleEmergencyStatusUpdate(data);
        });
    }

    /**
     * Start periodic status updates
     * @private
     */
    startPeriodicUpdates() {
        // Status update every 10 seconds
        this.statusUpdateInterval = setInterval(() => {
            this.refreshAllStatus();
        }, 10000);
    }

    // =========================
    // Status Management
    // =========================

    /**
     * Refresh status for all hardware components
     */
    async refreshAllStatus() {
        try {
            this.uiManager.showElementLoading('#refresh-all-status-btn', 'Refreshing...');
            
            // Get status for all hardware components in parallel
            const promises = [
                this.refreshHardwareStatus('robot'),
                this.refreshHardwareStatus('power'),
                this.refreshHardwareStatus('mcu'),
                this.refreshHardwareStatus('loadcell')
            ];
            
            await Promise.all(promises);
            
            // Update system overview
            this.updateSystemOverview();
            
            // Update last update timestamp
            this.updateLastUpdateTimestamp();
            
            this.addLogEntry('info', 'SYSTEM', 'All hardware status refreshed');
            
        } catch (error) {
            console.error('Failed to refresh all status:', error);
            this.uiManager.showNotification('Failed to refresh all hardware status', 'error');
        } finally {
            this.uiManager.hideElementLoading('#refresh-all-status-btn');
        }
    }

    /**
     * Refresh status for specific hardware component
     * @private
     * @param {string} component - Hardware component name
     */
    async refreshHardwareStatus(component) {
        try {
            const response = await this.apiClient.get(`/hardware/${component}/status`);
            
            if (response.success && response.data) {
                this.hardwareStatus[component] = {
                    connected: response.data.connected || false,
                    status: response.data
                };
                
                this.updateHardwareCard(component, response.data);
            }
            
        } catch (error) {
            console.warn(`Failed to refresh ${component} status:`, error);
            this.hardwareStatus[component] = {
                connected: false,
                status: { error: error.message }
            };
            this.updateHardwareCard(component, { connected: false, error: error.message });
        }
    }

    /**
     * Update hardware card display
     * @private
     * @param {string} component - Hardware component name
     * @param {Object} status - Status data
     */
    updateHardwareCard(component, status) {
        const cardStatus = document.getElementById(`${component}-card-status`);
        
        if (cardStatus) {
            const statusDot = cardStatus.querySelector('.status-dot');
            const statusLabel = cardStatus.querySelector('.status-label');
            
            const connected = status.connected || false;
            statusDot.className = `status-dot status-${connected ? 'success' : 'error'}`;
            if (statusLabel) {
                statusLabel.textContent = connected ? 'Connected' : 'Disconnected';
            }
        }
        
        // Update component-specific information
        this.updateComponentInfo(component, status);
    }

    /**
     * Update component-specific information
     * @private
     * @param {string} component - Hardware component name
     * @param {Object} status - Status data
     */
    updateComponentInfo(component, status) {
        switch (component) {
            case 'robot':
                this.updateRobotInfo(status);
                break;
            case 'power':
                this.updatePowerInfo(status);
                break;
            case 'mcu':
                this.updateMCUInfo(status);
                break;
            case 'loadcell':
                this.updateLoadCellInfo(status);
                break;
        }
    }

    /**
     * Update robot information display
     * @private
     * @param {Object} status - Robot status
     */
    updateRobotInfo(status) {
        const positionElement = document.getElementById('robot-position');
        const servoElement = document.getElementById('robot-servo');
        const motionElement = document.getElementById('robot-motion');
        
        if (positionElement) {
            const valueSpan = positionElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.position !== undefined ? 
                    status.position.toFixed(3) : '---.---';
            }
        }
        
        if (servoElement) {
            const valueSpan = servoElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.servo_enabled ? 'Enabled' : 'Disabled';
            }
        }
        
        if (motionElement) {
            const valueSpan = motionElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.motion_status || 'Unknown';
            }
        }
    }

    /**
     * Update power information display
     * @private
     * @param {Object} status - Power status
     */
    updatePowerInfo(status) {
        const voltageElement = document.getElementById('power-voltage');
        const currentElement = document.getElementById('power-current');
        const outputElement = document.getElementById('power-output');
        
        if (voltageElement) {
            const valueSpan = voltageElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.voltage !== undefined ? 
                    status.voltage.toFixed(2) : '---.--';
            }
        }
        
        if (currentElement) {
            const valueSpan = currentElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.current !== undefined ? 
                    status.current.toFixed(2) : '---.--';
            }
        }
        
        if (outputElement) {
            const valueSpan = outputElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.output_enabled ? 'ENABLED ⚡' : 'DISABLED';
            }
        }
    }

    /**
     * Update MCU information display
     * @private
     * @param {Object} status - MCU status
     */
    updateMCUInfo(status) {
        const temperatureElement = document.getElementById('mcu-temperature');
        const testModeElement = document.getElementById('mcu-test-mode');
        const bootStatusElement = document.getElementById('mcu-boot-status');
        
        if (temperatureElement) {
            const valueSpan = temperatureElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.temperature !== undefined ? 
                    status.temperature.toFixed(2) : '---.--';
            }
        }
        
        if (testModeElement) {
            const valueSpan = testModeElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.test_mode || 'Normal';
            }
        }
        
        if (bootStatusElement) {
            const valueSpan = bootStatusElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.boot_complete ? 'Complete' : 'Pending';
            }
        }
    }

    /**
     * Update LoadCell information display
     * @private
     * @param {Object} status - LoadCell status
     */
    updateLoadCellInfo(status) {
        const forceElement = document.getElementById('loadcell-force');
        const calibrationElement = document.getElementById('loadcell-calibration');
        const qualityElement = document.getElementById('loadcell-quality');
        
        if (forceElement) {
            const valueSpan = forceElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.force !== undefined ? 
                    status.force.toFixed(3) : '---.---';
            }
        }
        
        if (calibrationElement) {
            const valueSpan = calibrationElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.last_calibration ? 'Calibrated' : 'Not Calibrated';
            }
        }
        
        if (qualityElement) {
            const valueSpan = qualityElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = status.signal_quality || 'Unknown';
            }
        }
    }

    /**
     * Update system overview
     * @private
     */
    updateSystemOverview() {
        // Count connected components
        this.connectedCount = Object.values(this.hardwareStatus)
            .reduce((count, hw) => count + (hw.connected ? 1 : 0), 0);
        
        // Determine system health
        if (this.connectedCount === 0) {
            this.systemHealth = 'critical';
        } else if (this.connectedCount < 4) {
            this.systemHealth = 'warning';
        } else {
            this.systemHealth = 'good';
        }
        
        // Update displays
        const connectedElement = document.getElementById('connected-components');
        const healthElement = document.getElementById('system-health');
        const systemStatusIndicator = document.getElementById('system-status-indicator');
        
        if (connectedElement) {
            const valueSpan = connectedElement.querySelector('.value');
            if (valueSpan) valueSpan.textContent = this.connectedCount;
        }
        
        if (healthElement) {
            const statusDot = healthElement.querySelector('.status-dot');
            const healthSpan = healthElement.querySelector('span');
            
            let healthText = 'Unknown';
            let healthClass = 'status-unknown';
            
            switch (this.systemHealth) {
                case 'good':
                    healthText = 'Excellent';
                    healthClass = 'status-success';
                    break;
                case 'warning':
                    healthText = 'Warning';
                    healthClass = 'status-warning';
                    break;
                case 'critical':
                    healthText = 'Critical';
                    healthClass = 'status-error';
                    break;
            }
            
            if (statusDot) statusDot.className = `status-dot ${healthClass}`;
            if (healthSpan) healthSpan.textContent = healthText;
        }
        
        // Update main system status indicator
        if (systemStatusIndicator) {
            const statusText = systemStatusIndicator.querySelector('#system-status-text');
            const pulseDot = systemStatusIndicator.querySelector('.pulse-dot');
            const pulseRing = systemStatusIndicator.querySelector('.pulse-ring');
            
            let statusMessage = 'Initializing...';
            let pulseColor = '#6b7280';
            
            switch (this.systemHealth) {
                case 'good':
                    statusMessage = 'All Systems Operational';
                    pulseColor = '#4ade80';
                    break;
                case 'warning':
                    statusMessage = 'System Warning Detected';
                    pulseColor = '#fbbf24';
                    break;
                case 'critical':
                    statusMessage = 'Critical System Issues';
                    pulseColor = '#ef4444';
                    break;
            }
            
            if (statusText) statusText.textContent = statusMessage;
            if (pulseDot) {
                pulseDot.style.background = pulseColor;
                pulseDot.style.boxShadow = `0 0 20px ${pulseColor}66`;
            }
            if (pulseRing) {
                pulseRing.style.borderColor = pulseColor;
            }
        }
    }

    /**
     * Update last update timestamp
     * @private
     */
    updateLastUpdateTimestamp() {
        const lastUpdateElement = document.getElementById('last-update');
        
        if (lastUpdateElement) {
            const timestampSpan = lastUpdateElement.querySelector('.timestamp');
            if (timestampSpan) {
                timestampSpan.textContent = new Date().toLocaleTimeString();
            }
        }
    }

    // =========================
    // Navigation
    // =========================

    /**
     * Navigate to specific control panel
     * @param {string} page - Page identifier
     */
    navigateToControlPanel(page) {
        console.log(`Navigating to ${page} control panel`);
        
        // Use the UI manager to switch pages
        if (window.wfEolApp && window.wfEolApp.uiManager) {
            window.wfEolApp.uiManager.switchPage(page);
        }
        
        this.addLogEntry('info', 'NAVIGATION', `Opened ${page} control panel`);
    }

    // =========================
    // Emergency Controls
    // =========================

    /**
     * Handle emergency stop all hardware
     */
    async handleEmergencyStopAll() {
        try {
            const result = await this.uiManager.showModal({
                title: '🚨 EMERGENCY STOP ALL HARDWARE',
                message: `
                    <p><strong>WARNING: This will immediately stop ALL hardware components!</strong></p>
                    <div class="emergency-warning">
                        <p>This action will:</p>
                        <ul>
                            <li>Execute emergency stop on Robot motion controller</li>
                            <li>Disable Power supply output</li>
                            <li>Stop MCU operations</li>
                            <li>Halt LoadCell monitoring</li>
                        </ul>
                        <p><strong>This cannot be undone and may require manual restart of operations.</strong></p>
                    </div>
                `,
                type: 'error',
                buttons: [
                    { text: 'Cancel', action: 'cancel', variant: 'secondary' },
                    { text: 'EMERGENCY STOP', action: 'confirm', variant: 'danger' }
                ]
            });
            
            if (result.action !== 'confirm') {
                return;
            }
            
            // Execute emergency stop for all hardware
            const stopPromises = [
                this.apiClient.post('/hardware/robot/emergency-stop'),
                this.apiClient.post('/hardware/power/disable-output'),
                this.apiClient.post('/hardware/mcu/emergency-stop').catch(() => {}), // May not be implemented
                this.apiClient.post('/hardware/loadcell/stop-monitoring').catch(() => {}) // May not be implemented
            ];
            
            await Promise.allSettled(stopPromises);
            
            this.emergencyStatus = 'emergency';
            this.updateEmergencyStatus();
            
            this.addLogEntry('warning', 'EMERGENCY', 'Emergency stop executed for all hardware');
            this.uiManager.showNotification('Emergency stop executed successfully', 'warning');
            
            // Refresh status after emergency stop
            setTimeout(() => this.refreshAllStatus(), 2000);
            
        } catch (error) {
            console.error('Emergency stop failed:', error);
            this.addLogEntry('error', 'EMERGENCY', `Emergency stop failed: ${error.message}`);
            this.uiManager.showNotification(`Emergency stop failed: ${error.message}`, 'error');
        }
    }

    /**
     * Update emergency status display
     * @private
     */
    updateEmergencyStatus() {
        const emergencyStatus = document.getElementById('emergency-status');
        
        if (emergencyStatus) {
            const statusDot = emergencyStatus.querySelector('.status-dot');
            const statusSpan = emergencyStatus.querySelector('span');
            
            if (this.emergencyStatus === 'emergency') {
                statusDot.className = 'status-dot status-error';
                statusSpan.textContent = 'Emergency Stop Active';
            } else {
                statusDot.className = 'status-dot status-success';
                statusSpan.textContent = 'System Normal';
            }
        }
    }

    // =========================
    // Quick Status
    // =========================

    /**
     * Show quick status for hardware component
     * @param {string} component - Hardware component name
     */
    async showQuickStatus(component) {
        try {
            const status = this.hardwareStatus[component];
            const componentName = component.charAt(0).toUpperCase() + component.slice(1);
            
            let statusHtml = `
                <div class="quick-status">
                    <h4>${componentName} Status</h4>
                    <div class="status-grid">
                        <div class="status-row">
                            <label>Connection:</label>
                            <span class="${status.connected ? 'status-success' : 'status-error'}">
                                ${status.connected ? 'Connected' : 'Disconnected'}
                            </span>
                        </div>
            `;
            
            // Add component-specific status information
            const statusData = status.status;
            for (const [key, value] of Object.entries(statusData)) {
                if (key !== 'connected' && key !== 'error') {
                    statusHtml += `
                        <div class="status-row">
                            <label>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</label>
                            <span>${value}</span>
                        </div>
                    `;
                }
            }
            
            if (statusData.error) {
                statusHtml += `
                    <div class="status-row error">
                        <label>Error:</label>
                        <span class="status-error">${statusData.error}</span>
                    </div>
                `;
            }
            
            statusHtml += '</div></div>';
            
            await this.uiManager.showModal({
                title: `${componentName} Quick Status`,
                message: statusHtml,
                type: 'info',
                buttons: [
                    { text: 'Close', action: 'close', variant: 'primary' }
                ]
            });
            
        } catch (error) {
            console.error(`Failed to show quick status for ${component}:`, error);
            this.uiManager.showNotification(`Failed to get ${component} status`, 'error');
        }
    }

    // =========================
    // WebSocket Event Handlers
    // =========================

    /**
     * Handle hardware status update from WebSocket
     * @private
     * @param {Object} data - Hardware status data
     */
    handleHardwareStatusUpdate(data) {
        if (data.component && this.hardwareStatus[data.component]) {
            this.hardwareStatus[data.component] = {
                connected: data.connected || false,
                status: data
            };
            
            this.updateHardwareCard(data.component, data);
            this.updateSystemOverview();
            
            this.addLogEntry('info', data.component.toUpperCase(), `Status updated: ${data.connected ? 'Connected' : 'Disconnected'}`);
        }
    }

    /**
     * Handle system health update from WebSocket
     * @private
     * @param {Object} data - System health data
     */
    handleSystemHealthUpdate(data) {
        this.systemHealth = data.health || 'unknown';
        this.connectedCount = data.connected_count || 0;
        
        this.updateSystemOverview();
    }

    /**
     * Handle emergency status update from WebSocket
     * @private
     * @param {Object} data - Emergency status data
     */
    handleEmergencyStatusUpdate(data) {
        this.emergencyStatus = data.status || 'normal';
        this.updateEmergencyStatus();
        
        if (data.status === 'emergency') {
            this.addLogEntry('warning', 'EMERGENCY', 'Emergency status activated');
        }
    }

    // =========================
    // System Log
    // =========================

    /**
     * Add entry to system log
     * @private
     * @param {string} level - Log level (info, success, warning, error)
     * @param {string} component - Component name
     * @param {string} message - Log message
     */
    addLogEntry(level, component, message) {
        const timestamp = new Date().toLocaleTimeString();
        const entry = { timestamp, level, component, message };
        
        this.systemLog.push(entry);
        
        // Limit log size
        if (this.systemLog.length > this.maxLogEntries) {
            this.systemLog.shift();
        }
        
        this.updateLogDisplay();
    }

    /**
     * Update log display
     * @private
     */
    updateLogDisplay() {
        const logViewer = document.getElementById('hardware-log-viewer');
        if (!logViewer) return;
        
        const logHtml = this.systemLog.map(entry => `
            <div class="log-entry">
                <div class="log-time">${entry.timestamp}</div>
                <div class="log-level ${entry.level}">${entry.level.toUpperCase()}</div>
                <div class="log-source">${entry.component}</div>
                <div class="log-message">${entry.message}</div>
            </div>
        `).join('');
        
        logViewer.innerHTML = logHtml;
        
        // Scroll to bottom
        logViewer.scrollTop = logViewer.scrollHeight;
    }

    /**
     * Handle clear log
     */
    handleClearLog() {
        this.systemLog = [];
        this.updateLogDisplay();
        this.addLogEntry('info', 'SYSTEM', 'System log cleared');
    }

    /**
     * Handle export log
     */
    handleExportLog() {
        const logText = this.systemLog.map(entry => 
            `[${entry.timestamp}] ${entry.level.toUpperCase()} ${entry.component}: ${entry.message}`
        ).join('\n');
        
        const blob = new Blob([logText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `hardware-system-log-${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addLogEntry('info', 'SYSTEM', 'System log exported');
    }
}

console.log('📝 Hardware Dashboard Page Manager loaded successfully');