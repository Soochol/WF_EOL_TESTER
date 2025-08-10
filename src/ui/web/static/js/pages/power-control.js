/**
 * Power Control Page Manager - WF EOL Tester Web Interface
 * 
 * This module manages the Power hardware control panel including:
 * - Connection management with host/port settings
 * - Output control (Enable/Disable) with safety warnings
 * - Voltage/Current setting with real-time feedback
 * - Current limit configuration
 * - Live readings display (voltage, current, power)
 * - Safety confirmation dialogs for high voltage operations
 * - Status monitoring with connection health
 * - Real-time WebSocket updates
 * - Chart visualization of power readings
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

import { APIClient } from '../services/api-client.js';
import { WebSocketManager } from '../services/websocket-manager.js';
import { UIManager } from '../components/ui-manager.js';

/**
 * Power Control Page Manager
 * 
 * Manages all power supply control functionality with real-time status updates,
 * safety features, and comprehensive error handling.
 */
export class PowerControlPageManager {
    /**
     * Initialize Power Control Page Manager
     * @param {APIClient} apiClient - API client instance
     * @param {UIManager} uiManager - UI manager instance
     * @param {WebSocketManager} wsManager - WebSocket manager instance
     */
    constructor(apiClient, uiManager, wsManager) {
        this.apiClient = apiClient;
        this.uiManager = uiManager;
        this.wsManager = wsManager;
        
        // Component state
        this.isConnected = false;
        this.outputEnabled = false;
        this.currentVoltage = 0.0;
        this.currentCurrent = 0.0;
        this.currentLimit = 0.0;
        this.currentPower = 0.0;
        
        // Configuration
        this.host = '192.168.11.1';
        this.port = 5000;
        this.channel = 1;
        this.timeout = 5.0;
        this.deviceIdentity = null;
        
        // Update intervals
        this.readingsUpdateInterval = null;
        
        // Operation log
        this.operationLog = [];
        this.maxLogEntries = 100;
        
        // Safety settings
        this.requireSafetyConfirmations = true;
        this.highVoltageThreshold = 12.0; // V
        this.highCurrentThreshold = 5.0;  // A
        
        // Chart for readings visualization
        this.readingsChart = null;
        this.readingsHistory = {
            timestamps: [],
            voltage: [],
            current: [],
            power: []
        };
        this.maxHistoryPoints = 50;
        
        console.log('⚡ Power Control Page Manager initialized');
    }

    /**
     * Initialize page when activated
     */
    async init() {
        try {
            console.log('🔧 Initializing Power Control Page...');
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup WebSocket subscriptions
            this.setupWebSocketSubscriptions();
            
            // Setup tabs
            this.setupTabs();
            
            // Setup presets
            this.setupPresets();
            
            // Initialize chart
            this.initializeChart();
            
            // Load initial status
            await this.refreshStatus();
            
            // Start periodic updates
            this.startPeriodicUpdates();
            
            this.addLogEntry('info', 'Power Control Panel initialized');
            
            console.log('✅ Power Control Page initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize Power Control Page:', error);
            this.uiManager.showNotification('Failed to initialize Power Control Panel', 'error');
        }
    }

    /**
     * Cleanup when page is deactivated
     */
    cleanup() {
        console.log('🧹 Cleaning up Power Control Page...');
        
        // Clear intervals
        if (this.readingsUpdateInterval) {
            clearInterval(this.readingsUpdateInterval);
        }
        
        // Remove WebSocket subscriptions
        this.wsManager.unsubscribe('power-status');
        this.wsManager.unsubscribe('power-readings');
        
        // Remove event listeners
        this.removeEventListeners();
        
        // Cleanup chart
        if (this.readingsChart) {
            this.readingsChart.destroy();
            this.readingsChart = null;
        }
        
        console.log('✅ Power Control Page cleanup complete');
    }

    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Connection controls
        document.getElementById('power-connect-btn')?.addEventListener('click', 
            this.handleConnect.bind(this));
        document.getElementById('power-disconnect-btn')?.addEventListener('click', 
            this.handleDisconnect.bind(this));
        
        // Output controls
        document.getElementById('power-enable-output-btn')?.addEventListener('click', 
            this.handleEnableOutput.bind(this));
        document.getElementById('power-disable-output-btn')?.addEventListener('click', 
            this.handleDisableOutput.bind(this));
        
        // Voltage controls
        document.getElementById('power-set-voltage-btn')?.addEventListener('click', 
            this.handleSetVoltage.bind(this));
        
        // Current controls
        document.getElementById('power-set-current-btn')?.addEventListener('click', 
            this.handleSetCurrent.bind(this));
        document.getElementById('power-set-current-limit-btn')?.addEventListener('click', 
            this.handleSetCurrentLimit.bind(this));
        
        // Readings controls
        document.getElementById('power-refresh-readings-btn')?.addEventListener('click', 
            this.refreshReadings.bind(this));
        
        // Log controls
        document.getElementById('power-clear-log-btn')?.addEventListener('click', 
            this.handleClearLog.bind(this));
        document.getElementById('power-export-log-btn')?.addEventListener('click', 
            this.handleExportLog.bind(this));
    }

    /**
     * Remove event listeners
     * @private
     */
    removeEventListeners() {
        const buttons = [
            'power-connect-btn', 'power-disconnect-btn',
            'power-enable-output-btn', 'power-disable-output-btn',
            'power-set-voltage-btn', 'power-set-current-btn', 'power-set-current-limit-btn',
            'power-refresh-readings-btn', 'power-clear-log-btn', 'power-export-log-btn'
        ];
        
        buttons.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                const newElement = element.cloneNode(true);
                element.parentNode.replaceChild(newElement, element);
            }
        });
    }

    /**
     * Setup WebSocket subscriptions
     * @private
     */
    setupWebSocketSubscriptions() {
        // Subscribe to power status updates
        this.wsManager.subscribe('power-status', (data) => {
            this.handleStatusUpdate(data);
        });
        
        // Subscribe to power readings updates
        this.wsManager.subscribe('power-readings', (data) => {
            this.handleReadingsUpdate(data);
        });
        
        // Subscribe to power errors
        this.wsManager.subscribe('power-error', (data) => {
            this.handleErrorUpdate(data);
        });
    }

    /**
     * Setup tab navigation
     * @private
     */
    setupTabs() {
        const tabButtons = document.querySelectorAll('.current-control-panel .tab-btn');
        const tabContents = document.querySelectorAll('.current-control-panel .tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.getAttribute('data-tab');
                
                // Update active tab button
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update active tab content
                tabContents.forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(`${tabName}-tab`).classList.add('active');
            });
        });
    }

    /**
     * Setup voltage presets
     * @private
     */
    setupPresets() {
        const presetButtons = document.querySelectorAll('.preset-btn');
        
        presetButtons.forEach(button => {
            button.addEventListener('click', () => {
                const voltage = parseFloat(button.getAttribute('data-voltage'));
                const voltageInput = document.getElementById('voltage-setpoint');
                if (voltageInput) {
                    voltageInput.value = voltage;
                    
                    // Visual feedback
                    button.classList.add('active');
                    setTimeout(() => button.classList.remove('active'), 200);
                }
            });
        });
    }

    /**
     * Initialize readings chart
     * @private
     */
    initializeChart() {
        const chartContainer = document.getElementById('power-readings-chart');
        if (!chartContainer) return;

        // Create chart using Chart.js (if available)
        if (typeof Chart !== 'undefined') {
            const ctx = chartContainer.getContext('2d');
            this.readingsChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Voltage (V)',
                            data: [],
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            yAxisID: 'y'
                        },
                        {
                            label: 'Current (A)',
                            data: [],
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            yAxisID: 'y1'
                        },
                        {
                            label: 'Power (W)',
                            data: [],
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            yAxisID: 'y2'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Voltage (V)'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Current (A)'
                            },
                            grid: {
                                drawOnChartArea: false,
                            },
                        },
                        y2: {
                            type: 'linear',
                            display: false,
                            position: 'right',
                        }
                    }
                }
            });
        } else {
            // Fallback to simple text display
            chartContainer.innerHTML = '<div class="chart-placeholder">Chart.js not loaded - showing text readings only</div>';
        }
    }

    /**
     * Start periodic readings updates
     * @private
     */
    startPeriodicUpdates() {
        // Readings update every 2 seconds when connected
        this.readingsUpdateInterval = setInterval(() => {
            if (this.isConnected) {
                this.refreshReadings();
            }
        }, 2000);
    }

    // =========================
    // Connection Management
    // =========================

    /**
     * Handle power supply connection
     */
    async handleConnect() {
        try {
            this.uiManager.showElementLoading('#power-connect-btn', 'Connecting...');
            
            const response = await this.apiClient.post('/hardware/power/connect', {
                host: this.host,
                port: this.port,
                timeout: this.timeout,
                channel: this.channel
            });
            
            if (response.success) {
                this.isConnected = true;
                this.deviceIdentity = response.data?.device_identity || null;
                this.updateConnectionStatus(true);
                this.addLogEntry('success', 'Power supply connected successfully');
                this.uiManager.showNotification('Power supply connected successfully', 'success');
            } else {
                throw new Error(response.error || 'Connection failed');
            }
            
        } catch (error) {
            console.error('Power connection failed:', error);
            this.addLogEntry('error', `Connection failed: ${error.message}`);
            this.uiManager.showNotification(`Power connection failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#power-connect-btn');
        }
    }

    /**
     * Handle power supply disconnection
     */
    async handleDisconnect() {
        try {
            this.uiManager.showElementLoading('#power-disconnect-btn', 'Disconnecting...');
            
            const response = await this.apiClient.post('/hardware/power/disconnect');
            
            if (response.success) {
                this.isConnected = false;
                this.outputEnabled = false;
                this.updateConnectionStatus(false);
                this.updateOutputStatus(false);
                this.addLogEntry('info', 'Power supply disconnected successfully');
                this.uiManager.showNotification('Power supply disconnected successfully', 'info');
            } else {
                throw new Error(response.error || 'Disconnection failed');
            }
            
        } catch (error) {
            console.error('Power disconnection failed:', error);
            this.addLogEntry('error', `Disconnection failed: ${error.message}`);
            this.uiManager.showNotification(`Power disconnection failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#power-disconnect-btn');
        }
    }

    /**
     * Update connection status display
     * @private
     * @param {boolean} connected - Connection state
     */
    updateConnectionStatus(connected) {
        const statusBadge = document.getElementById('power-status-badge');
        const connectionStatus = document.getElementById('power-connection-status');
        const connectBtn = document.getElementById('power-connect-btn');
        const disconnectBtn = document.getElementById('power-disconnect-btn');
        const deviceIdentitySpan = document.getElementById('power-device-identity');
        
        if (statusBadge) {
            const statusLight = statusBadge.querySelector('.status-light');
            const statusText = statusBadge.querySelector('.status-text');
            
            statusLight.className = `status-light status-${connected ? 'success' : 'unknown'}`;
            statusText.textContent = connected ? 'Connected' : 'Disconnected';
        }
        
        if (connectionStatus) {
            const statusDot = connectionStatus.querySelector('.status-dot');
            const statusSpan = connectionStatus.querySelector('span');
            
            statusDot.className = `status-dot status-${connected ? 'success' : 'unknown'}`;
            statusSpan.textContent = connected ? 'Connected' : 'Disconnected';
        }
        
        // Update device identity
        if (deviceIdentitySpan) {
            deviceIdentitySpan.textContent = this.deviceIdentity || '--';
        }
        
        // Update button states
        if (connectBtn) connectBtn.disabled = connected;
        if (disconnectBtn) disconnectBtn.disabled = !connected;
        
        // Update control button states
        this.updateControlButtonStates(connected);
    }

    /**
     * Update control button states based on connection
     * @private
     * @param {boolean} connected - Connection state
     */
    updateControlButtonStates(connected) {
        const buttons = [
            'power-enable-output-btn', 'power-disable-output-btn',
            'power-set-voltage-btn', 'power-set-current-btn', 'power-set-current-limit-btn',
            'power-refresh-readings-btn'
        ];
        
        buttons.forEach(id => {
            const button = document.getElementById(id);
            if (button) {
                button.disabled = !connected;
            }
        });
    }

    // =========================
    // Output Control
    // =========================

    /**
     * Handle output enable with safety confirmation
     */
    async handleEnableOutput() {
        try {
            // Get current settings for safety warning
            let voltageWarning = 'Unknown voltage';
            let currentWarning = 'Unknown current';
            
            try {
                await this.refreshReadings();
                voltageWarning = `${this.currentVoltage.toFixed(2)} V`;
                currentWarning = `${this.currentCurrent.toFixed(2)} A`;
            } catch {
                // Use default warnings if readings fail
            }
            
            // Check for high voltage/current conditions
            const isHighVoltage = this.currentVoltage > this.highVoltageThreshold;
            const isHighCurrent = this.currentCurrent > this.highCurrentThreshold;
            
            if (this.requireSafetyConfirmations) {
                let warningLevel = 'warning';
                let warningTitle = '⚠️ Enable Power Output';
                let additionalWarnings = '';
                
                if (isHighVoltage || isHighCurrent) {
                    warningLevel = 'error';
                    warningTitle = '🚨 HIGH VOLTAGE/CURRENT WARNING';
                    additionalWarnings = `
                        <div class="high-voltage-alert">
                            ${isHighVoltage ? `<div class="alert-item">⚡ HIGH VOLTAGE: ${voltageWarning}</div>` : ''}
                            ${isHighCurrent ? `<div class="alert-item">⚡ HIGH CURRENT: ${currentWarning}</div>` : ''}
                        </div>
                    `;
                }
                
                const result = await this.uiManager.showModal({
                    title: warningTitle,
                    message: `
                        <p><strong>WARNING: This will enable power output!</strong></p>
                        <div class="power-settings">
                            <div><strong>Current Settings:</strong></div>
                            <ul>
                                <li>Voltage: ${voltageWarning}</li>
                                <li>Current: ${currentWarning}</li>
                                <li>Channel: ${this.channel}</li>
                            </ul>
                        </div>
                        ${additionalWarnings}
                        <p><strong>Safety Checklist:</strong></p>
                        <ul>
                            <li>All connections are secure and properly insulated</li>
                            <li>Load is connected and rated for these levels</li>
                            <li>Emergency stop is easily accessible</li>
                            <li>Personnel are clear of hazardous areas</li>
                        </ul>
                    `,
                    type: warningLevel,
                    buttons: [
                        { text: 'Cancel', action: 'cancel', variant: 'secondary' },
                        { text: 'Enable Output', action: 'confirm', variant: 'danger' }
                    ]
                });
                
                if (result.action !== 'confirm') {
                    return;
                }
            }
            
            this.uiManager.showElementLoading('#power-enable-output-btn', 'Enabling...');
            
            const response = await this.apiClient.post('/hardware/power/enable-output');
            
            if (response.success) {
                this.outputEnabled = true;
                this.updateOutputStatus(true);
                this.addLogEntry('warning', `Power output enabled - ${voltageWarning}, ${currentWarning}`);
                this.uiManager.showNotification('Power output enabled successfully', 'warning');
            } else {
                throw new Error(response.error || 'Output enable failed');
            }
            
        } catch (error) {
            console.error('Output enable failed:', error);
            this.addLogEntry('error', `Output enable failed: ${error.message}`);
            this.uiManager.showNotification(`Output enable failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#power-enable-output-btn');
        }
    }

    /**
     * Handle output disable
     */
    async handleDisableOutput() {
        try {
            this.uiManager.showElementLoading('#power-disable-output-btn', 'Disabling...');
            
            const response = await this.apiClient.post('/hardware/power/disable-output');
            
            if (response.success) {
                this.outputEnabled = false;
                this.updateOutputStatus(false);
                this.addLogEntry('info', 'Power output disabled');
                this.uiManager.showNotification('Power output disabled successfully', 'info');
            } else {
                throw new Error(response.error || 'Output disable failed');
            }
            
        } catch (error) {
            console.error('Output disable failed:', error);
            this.addLogEntry('error', `Output disable failed: ${error.message}`);
            this.uiManager.showNotification(`Output disable failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#power-disable-output-btn');
        }
    }

    /**
     * Update output status display
     * @private
     * @param {boolean} enabled - Output state
     */
    updateOutputStatus(enabled) {
        const outputStatus = document.getElementById('power-output-status');
        
        if (outputStatus) {
            const statusDot = outputStatus.querySelector('.status-dot');
            const statusSpan = outputStatus.querySelector('span');
            
            statusDot.className = `status-dot status-${enabled ? 'error' : 'success'}`;
            statusSpan.textContent = enabled ? 'ENABLED ⚡' : 'DISABLED';
        }
    }

    // =========================
    // Voltage Control
    // =========================

    /**
     * Handle voltage setting
     */
    async handleSetVoltage() {
        try {
            const voltageInput = document.getElementById('voltage-setpoint');
            const voltage = parseFloat(voltageInput.value);
            
            // Validate input
            if (!this.validateVoltage(voltage)) {
                return;
            }
            
            this.uiManager.showElementLoading('#power-set-voltage-btn', 'Setting...');
            
            const response = await this.apiClient.post('/hardware/power/set-voltage', {
                voltage: voltage
            });
            
            if (response.success) {
                const actualVoltage = response.data?.actual_voltage || voltage;
                this.currentVoltage = actualVoltage;
                this.updateVoltageDisplay(actualVoltage);
                this.addLogEntry('info', `Voltage set to ${actualVoltage.toFixed(2)} V`);
                this.uiManager.showNotification(`Voltage set to ${actualVoltage.toFixed(2)} V`, 'success');
                
                // Clear input
                voltageInput.value = '';
            } else {
                throw new Error(response.error || 'Voltage setting failed');
            }
            
        } catch (error) {
            console.error('Voltage setting failed:', error);
            this.addLogEntry('error', `Voltage setting failed: ${error.message}`);
            this.uiManager.showNotification(`Voltage setting failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#power-set-voltage-btn');
        }
    }

    /**
     * Validate voltage input
     * @private
     * @param {number} voltage - Voltage value
     * @returns {boolean} True if valid
     */
    validateVoltage(voltage) {
        if (isNaN(voltage)) {
            this.uiManager.showNotification('Please enter a valid voltage value', 'error');
            return false;
        }
        
        if (voltage < 0 || voltage > 50) {
            this.uiManager.showNotification('Voltage must be between 0.00 and 50.00 V', 'error');
            return false;
        }
        
        return true;
    }

    /**
     * Update voltage display
     * @private
     * @param {number} voltage - Voltage value
     */
    updateVoltageDisplay(voltage) {
        const voltageSetting = document.getElementById('power-voltage-setting');
        const voltageReading = document.getElementById('power-voltage-reading');
        
        if (voltageSetting) {
            const span = voltageSetting.querySelector('span');
            if (span) {
                span.textContent = `${voltage.toFixed(2)} V`;
            }
        }
        
        if (voltageReading) {
            const valueSpan = voltageReading.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = voltage.toFixed(2);
            }
        }
    }

    // =========================
    // Current Control
    // =========================

    /**
     * Handle current setting
     */
    async handleSetCurrent() {
        try {
            const currentInput = document.getElementById('current-setpoint');
            const current = parseFloat(currentInput.value);
            
            // Validate input
            if (!this.validateCurrent(current)) {
                return;
            }
            
            this.uiManager.showElementLoading('#power-set-current-btn', 'Setting...');
            
            const response = await this.apiClient.post('/hardware/power/set-current', {
                current: current
            });
            
            if (response.success) {
                const actualCurrent = response.data?.actual_current || current;
                this.currentCurrent = actualCurrent;
                this.updateCurrentDisplay(actualCurrent);
                this.addLogEntry('info', `Current set to ${actualCurrent.toFixed(2)} A`);
                this.uiManager.showNotification(`Current set to ${actualCurrent.toFixed(2)} A`, 'success');
                
                // Clear input
                currentInput.value = '';
            } else {
                throw new Error(response.error || 'Current setting failed');
            }
            
        } catch (error) {
            console.error('Current setting failed:', error);
            this.addLogEntry('error', `Current setting failed: ${error.message}`);
            this.uiManager.showNotification(`Current setting failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#power-set-current-btn');
        }
    }

    /**
     * Handle current limit setting
     */
    async handleSetCurrentLimit() {
        try {
            const limitInput = document.getElementById('current-limit-setpoint');
            const limit = parseFloat(limitInput.value);
            
            // Validate input
            if (!this.validateCurrent(limit)) {
                return;
            }
            
            this.uiManager.showElementLoading('#power-set-current-limit-btn', 'Setting...');
            
            const response = await this.apiClient.post('/hardware/power/set-current-limit', {
                current_limit: limit
            });
            
            if (response.success) {
                const actualLimit = response.data?.actual_limit || limit;
                this.currentLimit = actualLimit;
                this.updateCurrentLimitDisplay(actualLimit);
                this.addLogEntry('info', `Current limit set to ${actualLimit.toFixed(2)} A`);
                this.uiManager.showNotification(`Current limit set to ${actualLimit.toFixed(2)} A`, 'success');
                
                // Clear input
                limitInput.value = '';
            } else {
                throw new Error(response.error || 'Current limit setting failed');
            }
            
        } catch (error) {
            console.error('Current limit setting failed:', error);
            this.addLogEntry('error', `Current limit setting failed: ${error.message}`);
            this.uiManager.showNotification(`Current limit setting failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#power-set-current-limit-btn');
        }
    }

    /**
     * Validate current input
     * @private
     * @param {number} current - Current value
     * @returns {boolean} True if valid
     */
    validateCurrent(current) {
        if (isNaN(current)) {
            this.uiManager.showNotification('Please enter a valid current value', 'error');
            return false;
        }
        
        if (current < 0 || current > 50) {
            this.uiManager.showNotification('Current must be between 0.00 and 50.00 A', 'error');
            return false;
        }
        
        return true;
    }

    /**
     * Update current display
     * @private
     * @param {number} current - Current value
     */
    updateCurrentDisplay(current) {
        const currentSetting = document.getElementById('power-current-setting');
        const currentReading = document.getElementById('power-current-reading');
        
        if (currentSetting) {
            const span = currentSetting.querySelector('span');
            if (span) {
                span.textContent = `${current.toFixed(2)} A`;
            }
        }
        
        if (currentReading) {
            const valueSpan = currentReading.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = current.toFixed(2);
            }
        }
    }

    /**
     * Update current limit display
     * @private
     * @param {number} limit - Current limit value
     */
    updateCurrentLimitDisplay(limit) {
        const limitSetting = document.getElementById('power-current-limit-setting');
        
        if (limitSetting) {
            const span = limitSetting.querySelector('span');
            if (span) {
                span.textContent = `${limit.toFixed(2)} A`;
            }
        }
    }

    // =========================
    // Readings and Monitoring
    // =========================

    /**
     * Refresh power readings
     */
    async refreshReadings() {
        try {
            const response = await this.apiClient.get('/hardware/power/readings');
            
            if (response.success && response.data) {
                const readings = response.data;
                
                this.currentVoltage = readings.voltage || 0.0;
                this.currentCurrent = readings.current || 0.0;
                this.currentPower = readings.power || (this.currentVoltage * this.currentCurrent);
                
                this.updateReadingsDisplay(this.currentVoltage, this.currentCurrent, this.currentPower);
                this.updateReadingsHistory(this.currentVoltage, this.currentCurrent, this.currentPower);
            }
            
        } catch (error) {
            console.warn('Readings refresh failed:', error);
            // Don't show error for background updates
        }
    }

    /**
     * Update readings display
     * @private
     * @param {number} voltage - Voltage reading
     * @param {number} current - Current reading
     * @param {number} power - Power reading
     */
    updateReadingsDisplay(voltage, current, power) {
        // Update voltage
        const voltageReading = document.getElementById('power-voltage-reading');
        if (voltageReading) {
            const valueSpan = voltageReading.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = voltage.toFixed(2);
            }
        }
        
        // Update current
        const currentReading = document.getElementById('power-current-reading');
        if (currentReading) {
            const valueSpan = currentReading.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = current.toFixed(2);
            }
        }
        
        // Update power
        const powerReading = document.getElementById('power-power-reading');
        if (powerReading) {
            const valueSpan = powerReading.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = power.toFixed(2);
            }
        }
    }

    /**
     * Update readings history and chart
     * @private
     * @param {number} voltage - Voltage reading
     * @param {number} current - Current reading
     * @param {number} power - Power reading
     */
    updateReadingsHistory(voltage, current, power) {
        const timestamp = new Date().toLocaleTimeString();
        
        // Add to history
        this.readingsHistory.timestamps.push(timestamp);
        this.readingsHistory.voltage.push(voltage);
        this.readingsHistory.current.push(current);
        this.readingsHistory.power.push(power);
        
        // Limit history size
        if (this.readingsHistory.timestamps.length > this.maxHistoryPoints) {
            this.readingsHistory.timestamps.shift();
            this.readingsHistory.voltage.shift();
            this.readingsHistory.current.shift();
            this.readingsHistory.power.shift();
        }
        
        // Update chart if available
        if (this.readingsChart) {
            this.readingsChart.data.labels = this.readingsHistory.timestamps;
            this.readingsChart.data.datasets[0].data = this.readingsHistory.voltage;
            this.readingsChart.data.datasets[1].data = this.readingsHistory.current;
            this.readingsChart.data.datasets[2].data = this.readingsHistory.power;
            this.readingsChart.update('none');
        }
    }

    /**
     * Refresh overall status
     */
    async refreshStatus() {
        try {
            const response = await this.apiClient.get('/hardware/power/status');
            
            if (response.success && response.data) {
                const status = response.data;
                
                this.isConnected = status.connected || false;
                this.outputEnabled = status.output_enabled || false;
                this.deviceIdentity = status.device_identity || null;
                
                // Update displays
                this.updateConnectionStatus(this.isConnected);
                this.updateOutputStatus(this.outputEnabled);
                
                if (status.voltage !== undefined) this.currentVoltage = status.voltage;
                if (status.current !== undefined) this.currentCurrent = status.current;
                if (status.current_limit !== undefined) this.currentLimit = status.current_limit;
                
                this.updateVoltageDisplay(this.currentVoltage);
                this.updateCurrentDisplay(this.currentCurrent);
                this.updateCurrentLimitDisplay(this.currentLimit);
            }
            
        } catch (error) {
            console.warn('Status refresh failed:', error);
        }
    }

    // =========================
    // WebSocket Event Handlers
    // =========================

    /**
     * Handle status update from WebSocket
     * @private
     * @param {Object} data - Status data
     */
    handleStatusUpdate(data) {
        if (data.component === 'power') {
            this.isConnected = data.connected;
            this.outputEnabled = data.output_enabled;
            
            this.updateConnectionStatus(this.isConnected);
            this.updateOutputStatus(this.outputEnabled);
        }
    }

    /**
     * Handle readings update from WebSocket
     * @private
     * @param {Object} data - Readings data
     */
    handleReadingsUpdate(data) {
        if (data.component === 'power') {
            this.currentVoltage = data.voltage;
            this.currentCurrent = data.current;
            this.currentPower = data.power;
            
            this.updateReadingsDisplay(this.currentVoltage, this.currentCurrent, this.currentPower);
            this.updateReadingsHistory(this.currentVoltage, this.currentCurrent, this.currentPower);
        }
    }

    /**
     * Handle error update from WebSocket
     * @private
     * @param {Object} data - Error data
     */
    handleErrorUpdate(data) {
        if (data.component === 'power') {
            this.addLogEntry('error', data.message);
            this.uiManager.showNotification(`Power Error: ${data.message}`, 'error');
        }
    }

    // =========================
    // Operation Log
    // =========================

    /**
     * Add entry to operation log
     * @private
     * @param {string} level - Log level (info, success, warning, error)
     * @param {string} message - Log message
     */
    addLogEntry(level, message) {
        const timestamp = new Date().toLocaleTimeString();
        const entry = { timestamp, level, message };
        
        this.operationLog.push(entry);
        
        // Limit log size
        if (this.operationLog.length > this.maxLogEntries) {
            this.operationLog.shift();
        }
        
        this.updateLogDisplay();
    }

    /**
     * Update log display
     * @private
     */
    updateLogDisplay() {
        const logViewer = document.getElementById('power-log-viewer');
        if (!logViewer) return;
        
        const logHtml = this.operationLog.map(entry => `
            <div class="log-entry">
                <span class="timestamp">[${entry.timestamp}]</span>
                <span class="level ${entry.level}">${entry.level.toUpperCase()}</span>
                <span class="message">${entry.message}</span>
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
        this.operationLog = [];
        this.updateLogDisplay();
        this.addLogEntry('info', 'Operation log cleared');
    }

    /**
     * Handle export log
     */
    handleExportLog() {
        const logText = this.operationLog.map(entry => 
            `[${entry.timestamp}] ${entry.level.toUpperCase()}: ${entry.message}`
        ).join('\n');
        
        const blob = new Blob([logText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `power-log-${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addLogEntry('info', 'Operation log exported');
    }
}

console.log('📝 Power Control Page Manager loaded successfully');