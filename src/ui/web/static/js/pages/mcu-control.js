/**
 * MCU Control Page Manager - WF EOL Tester Web Interface
 * 
 * This module manages the MCU hardware control panel including:
 * - Connection management with serial port settings
 * - Temperature monitoring and control
 * - Test mode operations (Enter/Exit test modes)
 * - Operating temperature setting
 * - Standby heating/cooling operations with parameter input
 * - Boot completion monitoring
 * - Real-time temperature readings with chart visualization
 * - Real-time WebSocket updates
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

import { APIClient } from '../services/api-client.js';
import { WebSocketManager } from '../services/websocket-manager.js';
import { UIManager } from '../components/ui-manager.js';

/**
 * MCU Control Page Manager
 * 
 * Manages all MCU control functionality with real-time status updates,
 * temperature monitoring, and comprehensive error handling.
 */
export class MCUControlPageManager {
    /**
     * Initialize MCU Control Page Manager
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
        this.currentTemperature = null;
        this.temperatureSetpoint = null;
        this.testMode = 'normal';
        this.isBootComplete = false;
        
        // Configuration
        this.port = 'COM4';
        this.baudrate = 115200;
        this.timeout = 2.0;
        this.bytesize = 8;
        this.stopbits = 1;
        this.parity = null;
        
        // Update intervals
        this.temperatureUpdateInterval = null;
        
        // Operation log
        this.operationLog = [];
        this.maxLogEntries = 100;
        
        // Temperature chart
        this.temperatureChart = null;
        this.temperatureHistory = {
            timestamps: [],
            temperatures: []
        };
        this.maxHistoryPoints = 50;
        
        console.log('🔬 MCU Control Page Manager initialized');
    }

    /**
     * Initialize page when activated
     */
    async init() {
        try {
            console.log('🔧 Initializing MCU Control Page...');
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup WebSocket subscriptions
            this.setupWebSocketSubscriptions();
            
            // Setup tabs
            this.setupTabs();
            
            // Setup presets
            this.setupPresets();
            
            // Setup parameter preview updates
            this.setupParameterPreview();
            
            // Initialize temperature chart
            this.initializeTemperatureChart();
            
            // Load initial status
            await this.refreshStatus();
            
            // Start periodic updates
            this.startPeriodicUpdates();
            
            this.addLogEntry('info', 'MCU Control Panel initialized');
            
            console.log('✅ MCU Control Page initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize MCU Control Page:', error);
            this.uiManager.showNotification('Failed to initialize MCU Control Panel', 'error');
        }
    }

    /**
     * Cleanup when page is deactivated
     */
    cleanup() {
        console.log('🧹 Cleaning up MCU Control Page...');
        
        // Clear intervals
        if (this.temperatureUpdateInterval) {
            clearInterval(this.temperatureUpdateInterval);
        }
        
        // Remove WebSocket subscriptions
        this.wsManager.unsubscribe('mcu-status');
        this.wsManager.unsubscribe('mcu-temperature');
        
        // Remove event listeners
        this.removeEventListeners();
        
        // Cleanup chart
        if (this.temperatureChart) {
            this.temperatureChart.destroy();
            this.temperatureChart = null;
        }
        
        console.log('✅ MCU Control Page cleanup complete');
    }

    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Connection controls
        document.getElementById('mcu-connect-btn')?.addEventListener('click', 
            this.handleConnect.bind(this));
        document.getElementById('mcu-disconnect-btn')?.addEventListener('click', 
            this.handleDisconnect.bind(this));
        
        // Temperature controls
        document.getElementById('mcu-get-temperature-btn')?.addEventListener('click', 
            this.handleGetTemperature.bind(this));
        document.getElementById('mcu-refresh-temperature-btn')?.addEventListener('click', 
            this.handleGetTemperature.bind(this));
        document.getElementById('mcu-set-temperature-btn')?.addEventListener('click', 
            this.handleSetTemperature.bind(this));
        
        // Test mode controls
        document.getElementById('mcu-enter-test-mode-btn')?.addEventListener('click', 
            this.handleEnterTestMode.bind(this));
        document.getElementById('mcu-exit-test-mode-btn')?.addEventListener('click', 
            this.handleExitTestMode.bind(this));
        
        // Standby controls
        document.getElementById('mcu-start-heating-btn')?.addEventListener('click', 
            this.handleStartHeating.bind(this));
        document.getElementById('mcu-start-cooling-btn')?.addEventListener('click', 
            this.handleStartCooling.bind(this));
        
        // Boot control
        document.getElementById('mcu-wait-boot-btn')?.addEventListener('click', 
            this.handleWaitBoot.bind(this));
        
        // Log controls
        document.getElementById('mcu-clear-log-btn')?.addEventListener('click', 
            this.handleClearLog.bind(this));
        document.getElementById('mcu-export-log-btn')?.addEventListener('click', 
            this.handleExportLog.bind(this));
    }

    /**
     * Remove event listeners
     * @private
     */
    removeEventListeners() {
        const buttons = [
            'mcu-connect-btn', 'mcu-disconnect-btn',
            'mcu-get-temperature-btn', 'mcu-refresh-temperature-btn', 'mcu-set-temperature-btn',
            'mcu-enter-test-mode-btn', 'mcu-exit-test-mode-btn',
            'mcu-start-heating-btn', 'mcu-start-cooling-btn',
            'mcu-wait-boot-btn', 'mcu-clear-log-btn', 'mcu-export-log-btn'
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
        // Subscribe to MCU status updates
        this.wsManager.subscribe('mcu-status', (data) => {
            this.handleStatusUpdate(data);
        });
        
        // Subscribe to MCU temperature updates
        this.wsManager.subscribe('mcu-temperature', (data) => {
            this.handleTemperatureUpdate(data);
        });
        
        // Subscribe to MCU errors
        this.wsManager.subscribe('mcu-error', (data) => {
            this.handleErrorUpdate(data);
        });
    }

    /**
     * Setup tab navigation
     * @private
     */
    setupTabs() {
        const tabButtons = document.querySelectorAll('.standby-panel .tab-btn');
        const tabContents = document.querySelectorAll('.standby-panel .tab-content');
        
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
     * Setup temperature presets
     * @private
     */
    setupPresets() {
        const presetButtons = document.querySelectorAll('.preset-btn');
        
        presetButtons.forEach(button => {
            button.addEventListener('click', () => {
                const temperature = parseFloat(button.getAttribute('data-temperature'));
                const tempInput = document.getElementById('operating-temperature');
                if (tempInput) {
                    tempInput.value = temperature;
                    
                    // Visual feedback
                    button.classList.add('active');
                    setTimeout(() => button.classList.remove('active'), 200);
                }
            });
        });
    }

    /**
     * Setup parameter preview updates
     * @private
     */
    setupParameterPreview() {
        const inputs = [
            'heating-operating-temp',
            'heating-standby-temp',
            'heating-hold-time'
        ];
        
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', this.updateHeatingPreview.bind(this));
            }
        });
        
        // Initial preview update
        this.updateHeatingPreview();
    }

    /**
     * Update heating preview display
     * @private
     */
    updateHeatingPreview() {
        const operatingTemp = document.getElementById('heating-operating-temp')?.value || '60.0';
        const standbyTemp = document.getElementById('heating-standby-temp')?.value || '40.0';
        const holdTime = document.getElementById('heating-hold-time')?.value || '10000';
        
        const previewOperating = document.getElementById('preview-operating');
        const previewStandby = document.getElementById('preview-standby');
        const previewHold = document.getElementById('preview-hold');
        
        if (previewOperating) previewOperating.textContent = parseFloat(operatingTemp).toFixed(1);
        if (previewStandby) previewStandby.textContent = parseFloat(standbyTemp).toFixed(1);
        if (previewHold) previewHold.textContent = (parseInt(holdTime) / 1000).toFixed(1);
    }

    /**
     * Initialize temperature chart
     * @private
     */
    initializeTemperatureChart() {
        const chartContainer = document.getElementById('mcu-temperature-chart');
        if (!chartContainer || typeof Chart === 'undefined') return;

        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        const ctx = canvas.getContext('2d');
        
        this.temperatureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Temperature (°C)',
                    data: [],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
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
                        display: true,
                        title: {
                            display: true,
                            text: 'Temperature (°C)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    /**
     * Start periodic temperature updates
     * @private
     */
    startPeriodicUpdates() {
        // Temperature update every 3 seconds when connected
        this.temperatureUpdateInterval = setInterval(() => {
            if (this.isConnected) {
                this.updateTemperature();
            }
        }, 3000);
    }

    // =========================
    // Connection Management
    // =========================

    /**
     * Handle MCU connection
     */
    async handleConnect() {
        try {
            this.uiManager.showElementLoading('#mcu-connect-btn', 'Connecting...');
            
            const response = await this.apiClient.post('/hardware/mcu/connect', {
                port: this.port,
                baudrate: this.baudrate,
                timeout: this.timeout,
                bytesize: this.bytesize,
                stopbits: this.stopbits,
                parity: this.parity
            });
            
            if (response.success) {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.addLogEntry('success', 'MCU connected successfully');
                this.uiManager.showNotification('MCU connected successfully', 'success');
            } else {
                throw new Error(response.error || 'Connection failed');
            }
            
        } catch (error) {
            console.error('MCU connection failed:', error);
            this.addLogEntry('error', `Connection failed: ${error.message}`);
            this.uiManager.showNotification(`MCU connection failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#mcu-connect-btn');
        }
    }

    /**
     * Handle MCU disconnection
     */
    async handleDisconnect() {
        try {
            this.uiManager.showElementLoading('#mcu-disconnect-btn', 'Disconnecting...');
            
            const response = await this.apiClient.post('/hardware/mcu/disconnect');
            
            if (response.success) {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.addLogEntry('info', 'MCU disconnected successfully');
                this.uiManager.showNotification('MCU disconnected successfully', 'info');
            } else {
                throw new Error(response.error || 'Disconnection failed');
            }
            
        } catch (error) {
            console.error('MCU disconnection failed:', error);
            this.addLogEntry('error', `Disconnection failed: ${error.message}`);
            this.uiManager.showNotification(`MCU disconnection failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#mcu-disconnect-btn');
        }
    }

    /**
     * Update connection status display
     * @private
     * @param {boolean} connected - Connection state
     */
    updateConnectionStatus(connected) {
        const statusBadge = document.getElementById('mcu-status-badge');
        const connectionStatus = document.getElementById('mcu-connection-status');
        const connectBtn = document.getElementById('mcu-connect-btn');
        const disconnectBtn = document.getElementById('mcu-disconnect-btn');
        
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
            'mcu-get-temperature-btn', 'mcu-refresh-temperature-btn', 'mcu-set-temperature-btn',
            'mcu-enter-test-mode-btn', 'mcu-exit-test-mode-btn',
            'mcu-start-heating-btn', 'mcu-start-cooling-btn', 'mcu-wait-boot-btn'
        ];
        
        buttons.forEach(id => {
            const button = document.getElementById(id);
            if (button) {
                button.disabled = !connected;
            }
        });
    }

    // =========================
    // Temperature Control
    // =========================

    /**
     * Handle get temperature
     */
    async handleGetTemperature() {
        try {
            this.uiManager.showElementLoading('#mcu-get-temperature-btn', 'Reading...');
            
            const response = await this.apiClient.get('/hardware/mcu/temperature');
            
            if (response.success && response.data !== undefined) {
                this.currentTemperature = response.data.temperature;
                this.updateTemperatureDisplay(this.currentTemperature);
                this.updateTemperatureHistory(this.currentTemperature);
                this.addLogEntry('info', `Temperature read: ${this.currentTemperature.toFixed(2)} °C`);
                this.uiManager.showNotification(`Temperature: ${this.currentTemperature.toFixed(2)} °C`, 'success');
            } else {
                throw new Error(response.error || 'Failed to read temperature');
            }
            
        } catch (error) {
            console.error('Temperature reading failed:', error);
            this.addLogEntry('error', `Temperature reading failed: ${error.message}`);
            this.uiManager.showNotification(`Temperature reading failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#mcu-get-temperature-btn');
        }
    }

    /**
     * Handle set operating temperature
     */
    async handleSetTemperature() {
        try {
            const tempInput = document.getElementById('operating-temperature');
            const temperature = parseFloat(tempInput.value);
            
            // Validate input
            if (!this.validateTemperature(temperature)) {
                return;
            }
            
            this.uiManager.showElementLoading('#mcu-set-temperature-btn', 'Setting...');
            
            const response = await this.apiClient.post('/hardware/mcu/set-temperature', {
                temperature: temperature
            });
            
            if (response.success) {
                this.temperatureSetpoint = temperature;
                this.updateTemperatureSetpointDisplay(temperature);
                this.addLogEntry('info', `Operating temperature set to ${temperature.toFixed(2)} °C`);
                this.uiManager.showNotification(`Operating temperature set to ${temperature.toFixed(2)} °C`, 'success');
                
                // Clear input
                tempInput.value = '';
            } else {
                throw new Error(response.error || 'Temperature setting failed');
            }
            
        } catch (error) {
            console.error('Temperature setting failed:', error);
            this.addLogEntry('error', `Temperature setting failed: ${error.message}`);
            this.uiManager.showNotification(`Temperature setting failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#mcu-set-temperature-btn');
        }
    }

    /**
     * Validate temperature input
     * @private
     * @param {number} temperature - Temperature value
     * @returns {boolean} True if valid
     */
    validateTemperature(temperature) {
        if (isNaN(temperature)) {
            this.uiManager.showNotification('Please enter a valid temperature value', 'error');
            return false;
        }
        
        if (temperature < -50 || temperature > 200) {
            this.uiManager.showNotification('Temperature must be between -50.0 and 200.0 °C', 'error');
            return false;
        }
        
        return true;
    }

    /**
     * Update temperature from WebSocket or periodic updates
     * @private
     */
    async updateTemperature() {
        try {
            const response = await this.apiClient.get('/hardware/mcu/temperature');
            
            if (response.success && response.data !== undefined) {
                this.currentTemperature = response.data.temperature;
                this.updateTemperatureDisplay(this.currentTemperature);
                this.updateTemperatureHistory(this.currentTemperature);
            }
            
        } catch (error) {
            // Silently fail for background updates
            console.warn('Background temperature update failed:', error);
        }
    }

    /**
     * Update temperature display
     * @private
     * @param {number} temperature - Temperature in °C
     */
    updateTemperatureDisplay(temperature) {
        const tempReading = document.getElementById('mcu-current-temperature');
        const tempStatus = document.getElementById('mcu-temperature-status');
        
        if (tempReading) {
            const valueSpan = tempReading.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = temperature !== null ? temperature.toFixed(2) : '---.--';
            }
        }
        
        if (tempStatus) {
            const statusDot = tempStatus.querySelector('.status-dot');
            const statusSpan = tempStatus.querySelector('span');
            
            if (temperature !== null) {
                statusDot.className = 'status-dot status-success';
                statusSpan.textContent = 'Valid';
            } else {
                statusDot.className = 'status-dot status-unknown';
                statusSpan.textContent = 'Unknown';
            }
        }
    }

    /**
     * Update temperature setpoint display
     * @private
     * @param {number} setpoint - Temperature setpoint in °C
     */
    updateTemperatureSetpointDisplay(setpoint) {
        const setpointElement = document.getElementById('mcu-temperature-setpoint');
        
        if (setpointElement) {
            const span = setpointElement.querySelector('span');
            if (span) {
                span.textContent = setpoint !== null ? `${setpoint.toFixed(2)} °C` : '---.-- °C';
            }
        }
    }

    /**
     * Update temperature history and chart
     * @private
     * @param {number} temperature - Temperature reading
     */
    updateTemperatureHistory(temperature) {
        if (temperature === null) return;
        
        const timestamp = new Date().toLocaleTimeString();
        
        // Add to history
        this.temperatureHistory.timestamps.push(timestamp);
        this.temperatureHistory.temperatures.push(temperature);
        
        // Limit history size
        if (this.temperatureHistory.timestamps.length > this.maxHistoryPoints) {
            this.temperatureHistory.timestamps.shift();
            this.temperatureHistory.temperatures.shift();
        }
        
        // Update chart if available
        if (this.temperatureChart) {
            this.temperatureChart.data.labels = this.temperatureHistory.timestamps;
            this.temperatureChart.data.datasets[0].data = this.temperatureHistory.temperatures;
            this.temperatureChart.update('none');
        }
    }

    // =========================
    // Test Mode Control
    // =========================

    /**
     * Handle enter test mode
     */
    async handleEnterTestMode() {
        try {
            this.uiManager.showElementLoading('#mcu-enter-test-mode-btn', 'Entering...');
            
            const response = await this.apiClient.post('/hardware/mcu/enter-test-mode', {
                test_mode: 'MODE_1'
            });
            
            if (response.success) {
                this.testMode = 'test_mode_1';
                this.updateTestModeStatus('test_mode_1');
                this.addLogEntry('info', 'Entered test mode successfully');
                this.uiManager.showNotification('Entered test mode successfully', 'info');
            } else {
                throw new Error(response.error || 'Failed to enter test mode');
            }
            
        } catch (error) {
            console.error('Enter test mode failed:', error);
            this.addLogEntry('error', `Enter test mode failed: ${error.message}`);
            this.uiManager.showNotification(`Enter test mode failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#mcu-enter-test-mode-btn');
        }
    }

    /**
     * Handle exit test mode
     */
    async handleExitTestMode() {
        try {
            this.uiManager.showElementLoading('#mcu-exit-test-mode-btn', 'Exiting...');
            
            const response = await this.apiClient.post('/hardware/mcu/exit-test-mode');
            
            if (response.success) {
                this.testMode = 'normal';
                this.updateTestModeStatus('normal');
                this.addLogEntry('info', 'Exited test mode successfully');
                this.uiManager.showNotification('Exited test mode successfully', 'info');
            } else {
                throw new Error(response.error || 'Failed to exit test mode');
            }
            
        } catch (error) {
            console.error('Exit test mode failed:', error);
            this.addLogEntry('error', `Exit test mode failed: ${error.message}`);
            this.uiManager.showNotification(`Exit test mode failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#mcu-exit-test-mode-btn');
        }
    }

    /**
     * Update test mode status display
     * @private
     * @param {string} mode - Test mode
     */
    updateTestModeStatus(mode) {
        const testModeStatus = document.getElementById('mcu-test-mode-status');
        const currentModeElement = document.getElementById('mcu-current-mode');
        
        let statusClass = 'status-unknown';
        let statusText = 'Unknown Mode';
        let modeText = 'Unknown';
        
        switch (mode) {
            case 'normal':
                statusClass = 'status-success';
                statusText = 'Normal Mode';
                modeText = 'Normal Mode';
                break;
            case 'test_mode_1':
                statusClass = 'status-warning';
                statusText = 'Test Mode 1';
                modeText = 'Test Mode 1';
                break;
        }
        
        if (testModeStatus) {
            const statusDot = testModeStatus.querySelector('.status-dot');
            const statusSpan = testModeStatus.querySelector('span');
            
            statusDot.className = `status-dot ${statusClass}`;
            statusSpan.textContent = statusText;
        }
        
        if (currentModeElement) {
            currentModeElement.textContent = modeText;
        }
    }

    // =========================
    // Standby Operations
    // =========================

    /**
     * Handle start standby heating
     */
    async handleStartHeating() {
        try {
            // Get heating parameters
            const operatingTemp = parseFloat(document.getElementById('heating-operating-temp').value);
            const standbyTemp = parseFloat(document.getElementById('heating-standby-temp').value);
            const holdTime = parseInt(document.getElementById('heating-hold-time').value);
            
            // Validate parameters
            if (!this.validateHeatingParameters(operatingTemp, standbyTemp, holdTime)) {
                return;
            }
            
            this.uiManager.showElementLoading('#mcu-start-heating-btn', 'Starting...');
            
            const response = await this.apiClient.post('/hardware/mcu/start-standby-heating', {
                operating_temp: operatingTemp,
                standby_temp: standbyTemp,
                hold_time: holdTime
            });
            
            if (response.success) {
                this.addLogEntry('info', `Standby heating started - Op:${operatingTemp}°C, Standby:${standbyTemp}°C, Hold:${holdTime}ms`);
                this.uiManager.showNotification('Standby heating started successfully', 'info');
            } else {
                throw new Error(response.error || 'Failed to start standby heating');
            }
            
        } catch (error) {
            console.error('Start heating failed:', error);
            this.addLogEntry('error', `Start heating failed: ${error.message}`);
            this.uiManager.showNotification(`Start heating failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#mcu-start-heating-btn');
        }
    }

    /**
     * Handle start standby cooling
     */
    async handleStartCooling() {
        try {
            this.uiManager.showElementLoading('#mcu-start-cooling-btn', 'Starting...');
            
            const response = await this.apiClient.post('/hardware/mcu/start-standby-cooling');
            
            if (response.success) {
                this.addLogEntry('info', 'Standby cooling started');
                this.uiManager.showNotification('Standby cooling started successfully', 'info');
            } else {
                throw new Error(response.error || 'Failed to start standby cooling');
            }
            
        } catch (error) {
            console.error('Start cooling failed:', error);
            this.addLogEntry('error', `Start cooling failed: ${error.message}`);
            this.uiManager.showNotification(`Start cooling failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#mcu-start-cooling-btn');
        }
    }

    /**
     * Validate heating parameters
     * @private
     * @param {number} operatingTemp - Operating temperature
     * @param {number} standbyTemp - Standby temperature
     * @param {number} holdTime - Hold time
     * @returns {boolean} True if valid
     */
    validateHeatingParameters(operatingTemp, standbyTemp, holdTime) {
        if (isNaN(operatingTemp) || operatingTemp < 30 || operatingTemp > 60) {
            this.uiManager.showNotification('Operating temperature must be between 30 and 60 °C', 'error');
            return false;
        }
        
        if (isNaN(standbyTemp) || standbyTemp < 30 || standbyTemp > 60) {
            this.uiManager.showNotification('Standby temperature must be between 30 and 60 °C', 'error');
            return false;
        }
        
        if (isNaN(holdTime) || holdTime < 1000 || holdTime > 60000) {
            this.uiManager.showNotification('Hold time must be between 1000 and 60000 ms', 'error');
            return false;
        }
        
        if (operatingTemp <= standbyTemp) {
            this.uiManager.showNotification('Operating temperature must be higher than standby temperature', 'error');
            return false;
        }
        
        return true;
    }

    // =========================
    // Boot Control
    // =========================

    /**
     * Handle wait for boot completion
     */
    async handleWaitBoot() {
        try {
            this.uiManager.showElementLoading('#mcu-wait-boot-btn', 'Waiting...');
            
            const response = await this.apiClient.post('/hardware/mcu/wait-boot-complete');
            
            if (response.success) {
                this.isBootComplete = true;
                this.updateBootStatus(true);
                this.addLogEntry('success', 'MCU boot complete signal received');
                this.uiManager.showNotification('MCU boot complete signal received', 'success');
            } else {
                throw new Error(response.error || 'Boot wait failed');
            }
            
        } catch (error) {
            console.error('Boot wait failed:', error);
            this.addLogEntry('error', `Boot wait failed: ${error.message}`);
            this.uiManager.showNotification(`Boot wait failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#mcu-wait-boot-btn');
        }
    }

    /**
     * Update boot status display
     * @private
     * @param {boolean} complete - Boot completion status
     */
    updateBootStatus(complete) {
        const bootStatus = document.getElementById('mcu-boot-status');
        const bootCompleteStatus = document.getElementById('mcu-boot-complete-status');
        const lastBootTime = document.getElementById('mcu-last-boot-time');
        
        if (bootStatus) {
            const statusDot = bootStatus.querySelector('.status-dot');
            const statusSpan = bootStatus.querySelector('span');
            
            statusDot.className = `status-dot status-${complete ? 'success' : 'warning'}`;
            statusSpan.textContent = complete ? 'Complete' : 'Waiting';
        }
        
        if (bootCompleteStatus) {
            bootCompleteStatus.textContent = complete ? 'Complete' : 'Waiting';
        }
        
        if (lastBootTime && complete) {
            lastBootTime.textContent = new Date().toLocaleTimeString();
        }
    }

    /**
     * Refresh overall status
     */
    async refreshStatus() {
        try {
            const response = await this.apiClient.get('/hardware/mcu/status');
            
            if (response.success && response.data) {
                const status = response.data;
                
                this.isConnected = status.connected || false;
                this.testMode = status.test_mode || 'normal';
                
                // Update displays
                this.updateConnectionStatus(this.isConnected);
                this.updateTestModeStatus(this.testMode);
                
                if (status.temperature !== undefined) {
                    this.currentTemperature = status.temperature;
                    this.updateTemperatureDisplay(this.currentTemperature);
                    this.updateTemperatureHistory(this.currentTemperature);
                }
                
                if (status.temperature_setpoint !== undefined) {
                    this.temperatureSetpoint = status.temperature_setpoint;
                    this.updateTemperatureSetpointDisplay(this.temperatureSetpoint);
                }
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
        if (data.component === 'mcu') {
            this.isConnected = data.connected;
            this.testMode = data.test_mode || 'normal';
            
            this.updateConnectionStatus(this.isConnected);
            this.updateTestModeStatus(this.testMode);
        }
    }

    /**
     * Handle temperature update from WebSocket
     * @private
     * @param {Object} data - Temperature data
     */
    handleTemperatureUpdate(data) {
        if (data.component === 'mcu') {
            this.currentTemperature = data.temperature;
            this.updateTemperatureDisplay(this.currentTemperature);
            this.updateTemperatureHistory(this.currentTemperature);
        }
    }

    /**
     * Handle error update from WebSocket
     * @private
     * @param {Object} data - Error data
     */
    handleErrorUpdate(data) {
        if (data.component === 'mcu') {
            this.addLogEntry('error', data.message);
            this.uiManager.showNotification(`MCU Error: ${data.message}`, 'error');
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
        const logViewer = document.getElementById('mcu-log-viewer');
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
        a.download = `mcu-log-${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addLogEntry('info', 'Operation log exported');
    }
}

console.log('📝 MCU Control Page Manager loaded successfully');