/**
 * LoadCell Control Page Manager - WF EOL Tester Web Interface
 * 
 * This module manages the LoadCell hardware control panel including:
 * - Connection management with serial communication settings
 * - Real-time force readings with unit display
 * - Zero calibration functionality
 * - Live force monitoring with chart visualization
 * - Force measurement history and statistics
 * - Calibration status and accuracy indicators
 * - Real-time WebSocket updates
 * - Data analysis and quality indicators
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

import { APIClient } from '../services/api-client.js';
import { WebSocketManager } from '../services/websocket-manager.js';
import { UIManager } from '../components/ui-manager.js';

/**
 * LoadCell Control Page Manager
 * 
 * Manages all LoadCell control functionality with real-time status updates,
 * force monitoring, and comprehensive statistics tracking.
 */
export class LoadCellControlPageManager {
    /**
     * Initialize LoadCell Control Page Manager
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
        this.currentForce = null;
        this.forceUnit = 'kgf';
        this.isMonitoring = false;
        this.lastCalibrationTime = null;
        this.zeroOffset = 0.0;
        
        // Configuration
        this.port = 'COM8';
        this.baudrate = 9600;
        this.timeout = 1.0;
        this.bytesize = 8;
        this.stopbits = 1;
        this.parity = null;
        this.indicatorId = 1;
        
        // Monitoring settings
        this.monitoringInterval = null;
        this.updateRate = 2.0; // Hz
        this.maxForceRange = 100.0; // kgf
        
        // Operation log
        this.operationLog = [];
        this.maxLogEntries = 100;
        
        // Force chart
        this.forceChart = null;
        this.forceHistory = {
            timestamps: [],
            forces: []
        };
        this.maxHistoryPoints = 50;
        
        // Statistics
        this.statistics = {
            current: 0.0,
            max: null,
            min: null,
            sum: 0.0,
            count: 0,
            values: []
        };
        
        console.log('⚖️ LoadCell Control Page Manager initialized');
    }

    /**
     * Initialize page when activated
     */
    async init() {
        try {
            console.log('🔧 Initializing LoadCell Control Page...');
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup WebSocket subscriptions
            this.setupWebSocketSubscriptions();
            
            // Initialize force chart
            this.initializeForceChart();
            
            // Load initial status
            await this.refreshStatus();
            
            this.addLogEntry('info', 'LoadCell Control Panel initialized');
            
            console.log('✅ LoadCell Control Page initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize LoadCell Control Page:', error);
            this.uiManager.showNotification('Failed to initialize LoadCell Control Panel', 'error');
        }
    }

    /**
     * Cleanup when page is deactivated
     */
    cleanup() {
        console.log('🧹 Cleaning up LoadCell Control Page...');
        
        // Stop monitoring
        this.stopMonitoring();
        
        // Remove WebSocket subscriptions
        this.wsManager.unsubscribe('loadcell-status');
        this.wsManager.unsubscribe('loadcell-force');
        
        // Remove event listeners
        this.removeEventListeners();
        
        // Cleanup chart
        if (this.forceChart) {
            this.forceChart.destroy();
            this.forceChart = null;
        }
        
        console.log('✅ LoadCell Control Page cleanup complete');
    }

    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Connection controls
        document.getElementById('loadcell-connect-btn')?.addEventListener('click', 
            this.handleConnect.bind(this));
        document.getElementById('loadcell-disconnect-btn')?.addEventListener('click', 
            this.handleDisconnect.bind(this));
        
        // Force reading controls
        document.getElementById('loadcell-read-single-btn')?.addEventListener('click', 
            this.handleReadForce.bind(this));
        document.getElementById('loadcell-read-force-btn')?.addEventListener('click', 
            this.handleReadForce.bind(this));
        document.getElementById('loadcell-monitor-force-btn')?.addEventListener('click', 
            this.handleStartMonitoring.bind(this));
        document.getElementById('loadcell-stop-monitor-btn')?.addEventListener('click', 
            this.handleStopMonitoring.bind(this));
        
        // Calibration controls
        document.getElementById('loadcell-zero-calibration-btn')?.addEventListener('click', 
            this.handleZeroCalibration.bind(this));
        
        // Chart controls
        document.getElementById('loadcell-clear-chart-btn')?.addEventListener('click', 
            this.handleClearChart.bind(this));
        document.getElementById('loadcell-export-chart-btn')?.addEventListener('click', 
            this.handleExportChart.bind(this));
        
        // Statistics controls
        document.getElementById('loadcell-reset-stats-btn')?.addEventListener('click', 
            this.handleResetStatistics.bind(this));
        
        // Log controls
        document.getElementById('loadcell-clear-log-btn')?.addEventListener('click', 
            this.handleClearLog.bind(this));
        document.getElementById('loadcell-export-log-btn')?.addEventListener('click', 
            this.handleExportLog.bind(this));
    }

    /**
     * Remove event listeners
     * @private
     */
    removeEventListeners() {
        const buttons = [
            'loadcell-connect-btn', 'loadcell-disconnect-btn',
            'loadcell-read-single-btn', 'loadcell-read-force-btn',
            'loadcell-monitor-force-btn', 'loadcell-stop-monitor-btn',
            'loadcell-zero-calibration-btn', 'loadcell-clear-chart-btn',
            'loadcell-export-chart-btn', 'loadcell-reset-stats-btn',
            'loadcell-clear-log-btn', 'loadcell-export-log-btn'
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
        // Subscribe to LoadCell status updates
        this.wsManager.subscribe('loadcell-status', (data) => {
            this.handleStatusUpdate(data);
        });
        
        // Subscribe to LoadCell force updates
        this.wsManager.subscribe('loadcell-force', (data) => {
            this.handleForceUpdate(data);
        });
        
        // Subscribe to LoadCell errors
        this.wsManager.subscribe('loadcell-error', (data) => {
            this.handleErrorUpdate(data);
        });
    }

    /**
     * Initialize force chart
     * @private
     */
    initializeForceChart() {
        const chartContainer = document.getElementById('loadcell-chart-container');
        if (!chartContainer || typeof Chart === 'undefined') return;

        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        const ctx = canvas.getContext('2d');
        
        this.forceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Force (kgf)',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.1,
                    pointRadius: 2,
                    pointHoverRadius: 4
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
                            text: 'Force (kgf)'
                        },
                        beginAtZero: true
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

    // =========================
    // Connection Management
    // =========================

    /**
     * Handle LoadCell connection
     */
    async handleConnect() {
        try {
            this.uiManager.showElementLoading('#loadcell-connect-btn', 'Connecting...');
            
            const response = await this.apiClient.post('/hardware/loadcell/connect', {
                port: this.port,
                baudrate: this.baudrate,
                timeout: this.timeout,
                bytesize: this.bytesize,
                stopbits: this.stopbits,
                parity: this.parity,
                indicator_id: this.indicatorId
            });
            
            if (response.success) {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.addLogEntry('success', 'LoadCell connected successfully');
                this.uiManager.showNotification('LoadCell connected successfully', 'success');
            } else {
                throw new Error(response.error || 'Connection failed');
            }
            
        } catch (error) {
            console.error('LoadCell connection failed:', error);
            this.addLogEntry('error', `Connection failed: ${error.message}`);
            this.uiManager.showNotification(`LoadCell connection failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#loadcell-connect-btn');
        }
    }

    /**
     * Handle LoadCell disconnection
     */
    async handleDisconnect() {
        try {
            this.uiManager.showElementLoading('#loadcell-disconnect-btn', 'Disconnecting...');
            
            // Stop monitoring first
            if (this.isMonitoring) {
                this.stopMonitoring();
            }
            
            const response = await this.apiClient.post('/hardware/loadcell/disconnect');
            
            if (response.success) {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.addLogEntry('info', 'LoadCell disconnected successfully');
                this.uiManager.showNotification('LoadCell disconnected successfully', 'info');
            } else {
                throw new Error(response.error || 'Disconnection failed');
            }
            
        } catch (error) {
            console.error('LoadCell disconnection failed:', error);
            this.addLogEntry('error', `Disconnection failed: ${error.message}`);
            this.uiManager.showNotification(`LoadCell disconnection failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#loadcell-disconnect-btn');
        }
    }

    /**
     * Update connection status display
     * @private
     * @param {boolean} connected - Connection state
     */
    updateConnectionStatus(connected) {
        const statusBadge = document.getElementById('loadcell-status-badge');
        const connectionStatus = document.getElementById('loadcell-connection-status');
        const connectBtn = document.getElementById('loadcell-connect-btn');
        const disconnectBtn = document.getElementById('loadcell-disconnect-btn');
        
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
            'loadcell-read-single-btn', 'loadcell-read-force-btn',
            'loadcell-monitor-force-btn', 'loadcell-zero-calibration-btn'
        ];
        
        buttons.forEach(id => {
            const button = document.getElementById(id);
            if (button) {
                button.disabled = !connected;
            }
        });
    }

    // =========================
    // Force Reading
    // =========================

    /**
     * Handle single force reading
     */
    async handleReadForce() {
        try {
            this.uiManager.showElementLoading('#loadcell-read-single-btn', 'Reading...');
            
            const response = await this.apiClient.get('/hardware/loadcell/force');
            
            if (response.success && response.data) {
                this.currentForce = response.data.force;
                this.forceUnit = response.data.unit || 'kgf';
                
                this.updateForceDisplay(this.currentForce, this.forceUnit);
                this.updateForceHistory(this.currentForce);
                this.updateStatistics(this.currentForce);
                
                this.addLogEntry('info', `Force reading: ${this.currentForce.toFixed(3)} ${this.forceUnit}`);
                this.uiManager.showNotification(`Force: ${this.currentForce.toFixed(3)} ${this.forceUnit}`, 'success');
            } else {
                throw new Error(response.error || 'Failed to read force');
            }
            
        } catch (error) {
            console.error('Force reading failed:', error);
            this.addLogEntry('error', `Force reading failed: ${error.message}`);
            this.uiManager.showNotification(`Force reading failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#loadcell-read-single-btn');
        }
    }

    /**
     * Handle start live monitoring
     */
    async handleStartMonitoring() {
        try {
            if (this.isMonitoring) {
                return;
            }
            
            this.isMonitoring = true;
            this.updateMonitoringButtons(true);
            
            // Start periodic force readings
            this.monitoringInterval = setInterval(() => {
                this.readForceForMonitoring();
            }, 1000 / this.updateRate);
            
            this.addLogEntry('info', `Started live force monitoring at ${this.updateRate} Hz`);
            this.uiManager.showNotification('Started live force monitoring', 'info');
            
        } catch (error) {
            console.error('Failed to start monitoring:', error);
            this.uiManager.showNotification('Failed to start monitoring', 'error');
        }
    }

    /**
     * Handle stop live monitoring
     */
    handleStopMonitoring() {
        this.stopMonitoring();
        this.addLogEntry('info', 'Stopped live force monitoring');
        this.uiManager.showNotification('Stopped live force monitoring', 'info');
    }

    /**
     * Stop monitoring internally
     * @private
     */
    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
        
        this.isMonitoring = false;
        this.updateMonitoringButtons(false);
    }

    /**
     * Update monitoring button states
     * @private
     * @param {boolean} monitoring - Monitoring state
     */
    updateMonitoringButtons(monitoring) {
        const monitorBtn = document.getElementById('loadcell-monitor-force-btn');
        const stopBtn = document.getElementById('loadcell-stop-monitor-btn');
        
        if (monitorBtn) {
            monitorBtn.style.display = monitoring ? 'none' : 'inline-block';
            monitorBtn.disabled = monitoring;
        }
        
        if (stopBtn) {
            stopBtn.style.display = monitoring ? 'inline-block' : 'none';
            stopBtn.disabled = !monitoring;
        }
    }

    /**
     * Read force for monitoring (silent errors)
     * @private
     */
    async readForceForMonitoring() {
        try {
            const response = await this.apiClient.get('/hardware/loadcell/force');
            
            if (response.success && response.data) {
                this.currentForce = response.data.force;
                this.forceUnit = response.data.unit || 'kgf';
                
                this.updateForceDisplay(this.currentForce, this.forceUnit);
                this.updateForceHistory(this.currentForce);
                this.updateStatistics(this.currentForce);
            }
            
        } catch (error) {
            // Silently handle monitoring errors to avoid spam
            console.warn('Monitoring force reading failed:', error);
        }
    }

    /**
     * Update force display
     * @private
     * @param {number} force - Force value
     * @param {string} unit - Force unit
     */
    updateForceDisplay(force, unit) {
        const forceReading = document.getElementById('loadcell-current-force');
        const forceStatus = document.getElementById('loadcell-force-status');
        const rangeFill = document.getElementById('loadcell-range-fill');
        
        if (forceReading) {
            const valueSpan = forceReading.querySelector('.value');
            const unitSpan = forceReading.querySelector('.unit');
            
            if (valueSpan) valueSpan.textContent = force !== null ? force.toFixed(3) : '---.---';
            if (unitSpan) unitSpan.textContent = unit;
        }
        
        if (forceStatus && force !== null) {
            const statusDot = forceStatus.querySelector('.status-dot');
            const statusSpan = forceStatus.querySelector('span');
            
            statusDot.className = 'status-dot status-success';
            statusSpan.textContent = 'Valid';
        }
        
        // Update range indicator
        if (rangeFill && force !== null) {
            const percentage = Math.min(Math.abs(force) / this.maxForceRange * 100, 100);
            rangeFill.style.width = `${percentage}%`;
            
            // Color based on force level
            if (percentage > 80) {
                rangeFill.style.backgroundColor = '#dc3545'; // Red
            } else if (percentage > 60) {
                rangeFill.style.backgroundColor = '#ffc107'; // Yellow
            } else {
                rangeFill.style.backgroundColor = '#28a745'; // Green
            }
        }
    }

    /**
     * Update force history and chart
     * @private
     * @param {number} force - Force value
     */
    updateForceHistory(force) {
        if (force === null) return;
        
        const timestamp = new Date().toLocaleTimeString();
        
        // Add to history
        this.forceHistory.timestamps.push(timestamp);
        this.forceHistory.forces.push(force);
        
        // Limit history size
        if (this.forceHistory.timestamps.length > this.maxHistoryPoints) {
            this.forceHistory.timestamps.shift();
            this.forceHistory.forces.shift();
        }
        
        // Update chart if available
        if (this.forceChart) {
            this.forceChart.data.labels = this.forceHistory.timestamps;
            this.forceChart.data.datasets[0].data = this.forceHistory.forces;
            this.forceChart.update('none');
        }
        
        // Update data points counter
        const dataPointsElement = document.getElementById('loadcell-data-points');
        if (dataPointsElement) {
            dataPointsElement.textContent = this.forceHistory.forces.length;
        }
    }

    // =========================
    // Calibration
    // =========================

    /**
     * Handle zero calibration
     */
    async handleZeroCalibration() {
        try {
            const result = await this.uiManager.showModal({
                title: '🔧 Zero Calibration',
                message: `
                    <p><strong>Zero Calibration Procedure</strong></p>
                    <div class="calibration-instructions">
                        <p>Before proceeding, ensure:</p>
                        <ul>
                            <li>All loads are removed from the sensor</li>
                            <li>The sensor is stable and not moving</li>
                            <li>Environmental conditions are stable</li>
                            <li>You have waited for sensor settling time</li>
                        </ul>
                        <p>This will set the current reading as the new zero reference.</p>
                    </div>
                `,
                type: 'warning',
                buttons: [
                    { text: 'Cancel', action: 'cancel', variant: 'secondary' },
                    { text: 'Calibrate Zero', action: 'confirm', variant: 'warning' }
                ]
            });
            
            if (result.action !== 'confirm') {
                return;
            }
            
            this.uiManager.showElementLoading('#loadcell-zero-calibration-btn', 'Calibrating...');
            
            const response = await this.apiClient.post('/hardware/loadcell/zero-calibration');
            
            if (response.success) {
                this.lastCalibrationTime = new Date();
                this.zeroOffset = response.data?.zero_offset || 0.0;
                
                this.updateCalibrationStatus();
                this.addLogEntry('success', 'Zero calibration completed successfully');
                this.uiManager.showNotification('Zero calibration completed successfully', 'success');
                
                // Read force after calibration to verify
                setTimeout(() => this.handleReadForce(), 1000);
            } else {
                throw new Error(response.error || 'Zero calibration failed');
            }
            
        } catch (error) {
            console.error('Zero calibration failed:', error);
            this.addLogEntry('error', `Zero calibration failed: ${error.message}`);
            this.uiManager.showNotification(`Zero calibration failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#loadcell-zero-calibration-btn');
        }
    }

    /**
     * Update calibration status display
     * @private
     */
    updateCalibrationStatus() {
        const calibrationStatus = document.getElementById('loadcell-calibration-status');
        const lastCalibration = document.getElementById('loadcell-last-calibration');
        const zeroOffset = document.getElementById('loadcell-zero-offset');
        
        if (calibrationStatus) {
            const statusDot = calibrationStatus.querySelector('.status-dot');
            const statusSpan = calibrationStatus.querySelector('span');
            
            statusDot.className = 'status-dot status-success';
            statusSpan.textContent = 'Calibrated';
        }
        
        if (lastCalibration && this.lastCalibrationTime) {
            lastCalibration.textContent = this.lastCalibrationTime.toLocaleString();
        }
        
        if (zeroOffset) {
            const valueSpan = zeroOffset.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = this.zeroOffset.toFixed(3);
            }
        }
    }

    // =========================
    // Statistics
    // =========================

    /**
     * Update force statistics
     * @private
     * @param {number} force - Force value
     */
    updateStatistics(force) {
        if (force === null) return;
        
        // Update basic statistics
        this.statistics.current = force;
        this.statistics.count++;
        this.statistics.sum += force;
        
        // Update min/max
        if (this.statistics.max === null || force > this.statistics.max) {
            this.statistics.max = force;
        }
        if (this.statistics.min === null || force < this.statistics.min) {
            this.statistics.min = force;
        }
        
        // Store values for standard deviation (limit size)
        this.statistics.values.push(force);
        if (this.statistics.values.length > 1000) {
            this.statistics.values.shift();
        }
        
        // Update display
        this.updateStatisticsDisplay();
        this.updateQualityIndicators();
    }

    /**
     * Update statistics display
     * @private
     */
    updateStatisticsDisplay() {
        const stats = this.statistics;
        
        // Current
        const currentElement = document.getElementById('loadcell-stat-current');
        if (currentElement) {
            const valueSpan = currentElement.querySelector('.value');
            if (valueSpan) valueSpan.textContent = stats.current.toFixed(3);
        }
        
        // Maximum
        const maxElement = document.getElementById('loadcell-stat-max');
        if (maxElement && stats.max !== null) {
            const valueSpan = maxElement.querySelector('.value');
            if (valueSpan) valueSpan.textContent = stats.max.toFixed(3);
        }
        
        // Minimum
        const minElement = document.getElementById('loadcell-stat-min');
        if (minElement && stats.min !== null) {
            const valueSpan = minElement.querySelector('.value');
            if (valueSpan) valueSpan.textContent = stats.min.toFixed(3);
        }
        
        // Average
        const avgElement = document.getElementById('loadcell-stat-avg');
        if (avgElement && stats.count > 0) {
            const average = stats.sum / stats.count;
            const valueSpan = avgElement.querySelector('.value');
            if (valueSpan) valueSpan.textContent = average.toFixed(3);
        }
        
        // Standard deviation
        const stdElement = document.getElementById('loadcell-stat-std');
        if (stdElement && stats.values.length > 1) {
            const mean = stats.sum / stats.count;
            const variance = stats.values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / stats.values.length;
            const stdDev = Math.sqrt(variance);
            const valueSpan = stdElement.querySelector('.value');
            if (valueSpan) valueSpan.textContent = stdDev.toFixed(3);
        }
        
        // Count
        const countElement = document.getElementById('loadcell-stat-count');
        if (countElement) {
            const valueSpan = countElement.querySelector('.value');
            if (valueSpan) valueSpan.textContent = stats.count.toString();
        }
    }

    /**
     * Update quality indicators
     * @private
     */
    updateQualityIndicators() {
        const stats = this.statistics;
        
        if (stats.values.length < 10) return; // Need enough data
        
        // Calculate stability (based on standard deviation)
        const recent = stats.values.slice(-10); // Last 10 readings
        const mean = recent.reduce((sum, val) => sum + val, 0) / recent.length;
        const variance = recent.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / recent.length;
        const stdDev = Math.sqrt(variance);
        
        // Stability percentage (inverse of coefficient of variation)
        const cv = Math.abs(mean) > 0.001 ? stdDev / Math.abs(mean) : 0;
        const stabilityPercent = Math.max(0, Math.min(100, (1 - cv * 10) * 100));
        
        // Signal quality (based on reading consistency)
        const signalQuality = Math.min(100, Math.max(50, 100 - (stdDev * 1000)));
        
        // Update stability display
        const stabilityElement = document.getElementById('loadcell-stability');
        const stabilityFill = document.getElementById('loadcell-stability-fill');
        
        if (stabilityElement) {
            let stabilityText = 'Excellent';
            if (stabilityPercent < 50) stabilityText = 'Poor';
            else if (stabilityPercent < 70) stabilityText = 'Fair';
            else if (stabilityPercent < 85) stabilityText = 'Good';
            
            stabilityElement.textContent = stabilityText;
        }
        
        if (stabilityFill) {
            stabilityFill.style.width = `${stabilityPercent}%`;
            
            // Color coding
            if (stabilityPercent < 50) {
                stabilityFill.style.backgroundColor = '#dc3545'; // Red
            } else if (stabilityPercent < 70) {
                stabilityFill.style.backgroundColor = '#ffc107'; // Yellow
            } else {
                stabilityFill.style.backgroundColor = '#28a745'; // Green
            }
        }
        
        // Update signal quality display
        const signalQualityElement = document.getElementById('loadcell-signal-quality');
        const signalFill = document.getElementById('loadcell-signal-fill');
        
        if (signalQualityElement) {
            let qualityText = 'Excellent';
            if (signalQuality < 60) qualityText = 'Poor';
            else if (signalQuality < 75) qualityText = 'Fair';
            else if (signalQuality < 90) qualityText = 'Good';
            
            signalQualityElement.textContent = qualityText;
        }
        
        if (signalFill) {
            signalFill.style.width = `${signalQuality}%`;
            
            // Color coding
            if (signalQuality < 60) {
                signalFill.style.backgroundColor = '#dc3545'; // Red
            } else if (signalQuality < 75) {
                signalFill.style.backgroundColor = '#ffc107'; // Yellow
            } else {
                signalFill.style.backgroundColor = '#28a745'; // Green
            }
        }
    }

    /**
     * Handle reset statistics
     */
    handleResetStatistics() {
        this.statistics = {
            current: 0.0,
            max: null,
            min: null,
            sum: 0.0,
            count: 0,
            values: []
        };
        
        this.updateStatisticsDisplay();
        this.addLogEntry('info', 'Force statistics reset');
        this.uiManager.showNotification('Force statistics reset', 'info');
    }

    // =========================
    // Chart Operations
    // =========================

    /**
     * Handle clear chart
     */
    handleClearChart() {
        this.forceHistory = {
            timestamps: [],
            forces: []
        };
        
        if (this.forceChart) {
            this.forceChart.data.labels = [];
            this.forceChart.data.datasets[0].data = [];
            this.forceChart.update();
        }
        
        // Update data points counter
        const dataPointsElement = document.getElementById('loadcell-data-points');
        if (dataPointsElement) {
            dataPointsElement.textContent = '0';
        }
        
        this.addLogEntry('info', 'Force chart cleared');
        this.uiManager.showNotification('Force chart cleared', 'info');
    }

    /**
     * Handle export chart data
     */
    handleExportChart() {
        if (this.forceHistory.forces.length === 0) {
            this.uiManager.showNotification('No data to export', 'warning');
            return;
        }
        
        // Create CSV data
        const csvData = [
            ['Timestamp', 'Force (kgf)'],
            ...this.forceHistory.timestamps.map((timestamp, index) => [
                timestamp,
                this.forceHistory.forces[index].toFixed(3)
            ])
        ];
        
        const csvContent = csvData.map(row => row.join(',')).join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `loadcell-data-${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addLogEntry('info', 'Force chart data exported');
        this.uiManager.showNotification('Force chart data exported', 'success');
    }

    /**
     * Refresh overall status
     */
    async refreshStatus() {
        try {
            const response = await this.apiClient.get('/hardware/loadcell/status');
            
            if (response.success && response.data) {
                const status = response.data;
                
                this.isConnected = status.connected || false;
                
                // Update displays
                this.updateConnectionStatus(this.isConnected);
                
                if (status.force !== undefined) {
                    this.currentForce = status.force;
                    this.forceUnit = status.unit || 'kgf';
                    this.updateForceDisplay(this.currentForce, this.forceUnit);
                }
                
                if (status.last_calibration) {
                    this.lastCalibrationTime = new Date(status.last_calibration);
                    this.updateCalibrationStatus();
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
        if (data.component === 'loadcell') {
            this.isConnected = data.connected;
            this.updateConnectionStatus(this.isConnected);
        }
    }

    /**
     * Handle force update from WebSocket
     * @private
     * @param {Object} data - Force data
     */
    handleForceUpdate(data) {
        if (data.component === 'loadcell') {
            this.currentForce = data.force;
            this.forceUnit = data.unit || 'kgf';
            
            this.updateForceDisplay(this.currentForce, this.forceUnit);
            this.updateForceHistory(this.currentForce);
            this.updateStatistics(this.currentForce);
        }
    }

    /**
     * Handle error update from WebSocket
     * @private
     * @param {Object} data - Error data
     */
    handleErrorUpdate(data) {
        if (data.component === 'loadcell') {
            this.addLogEntry('error', data.message);
            this.uiManager.showNotification(`LoadCell Error: ${data.message}`, 'error');
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
        const logViewer = document.getElementById('loadcell-log-viewer');
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
        a.download = `loadcell-log-${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addLogEntry('info', 'Operation log exported');
    }
}

console.log('📝 LoadCell Control Page Manager loaded successfully');