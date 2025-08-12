/**
 * Robot Control Page Manager - WF EOL Tester Web Interface
 * 
 * This module manages the Robot hardware control panel including:
 * - Connection management (Connect/Disconnect)
 * - Servo control (Enable/Disable motor power)
 * - Movement controls (Home Axis, Move Absolute, Move Relative)
 * - Position display and monitoring
 * - Motion parameters configuration (velocity, acceleration, deceleration)
 * - Emergency stop functionality
 * - Status monitoring (connection, position, servo state, motion status)
 * - Real-time WebSocket updates
 * - Safety confirmations and validations
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

import { APIClient } from '../services/api-client.js';
import { WebSocketManager } from '../services/websocket-manager.js';
import { UIManager } from '../components/ui-manager.js';

/**
 * Robot Control Page Manager
 * 
 * Manages all robot control functionality with real-time status updates,
 * safety features, and comprehensive error handling.
 */
export class RobotControlPageManager {
    /**
     * Initialize Robot Control Page Manager
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
        this.servoEnabled = false;
        this.currentPosition = null;
        this.motionStatus = 'idle';
        this.isInitialized = false;
        
        // Configuration
        this.axisId = 0;
        this.irqNo = 7;
        
        // Update intervals
        this.statusUpdateInterval = null;
        this.positionUpdateInterval = null;
        
        // Operation log
        this.operationLog = [];
        this.maxLogEntries = 100;
        
        // Safety confirmations
        this.requireConfirmations = true;
        
        console.log('🤖 Robot Control Page Manager initialized');
    }

    /**
     * Initialize page when activated
     */
    async init() {
        try {
            console.log('🔧 Initializing Robot Control Page...');
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup WebSocket subscriptions
            this.setupWebSocketSubscriptions();
            
            // Setup tabs
            this.setupTabs();
            
            // Load initial status
            await this.refreshStatus();
            
            // Load default motion parameters from current configuration
            await this.loadDefaultMotionParameters();
            
            // Start periodic updates
            this.startPeriodicUpdates();
            
            this.addLogEntry('info', 'Robot Control Panel initialized');
            
            console.log('✅ Robot Control Page initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize Robot Control Page:', error);
            this.uiManager.showNotification('Failed to initialize Robot Control Panel', 'error');
        }
    }

    /**
     * Load default motion parameters from current test configuration
     * @private
     */
    async loadDefaultMotionParameters() {
        try {
            console.log('📥 Loading default motion parameters...');
            
            // Get current configuration
            const response = await this.apiClient.get('/config/current');
            
            // Set default values in the UI
            const velocityInput = document.getElementById('absolute-velocity');
            const accelerationInput = document.getElementById('absolute-acceleration');
            const decelerationInput = document.getElementById('absolute-deceleration');
            
            if (velocityInput) velocityInput.value = response.velocity || 60000;
            if (accelerationInput) accelerationInput.value = response.acceleration || 60000;
            if (decelerationInput) decelerationInput.value = response.deceleration || 60000;
            
            // Also set relative motion defaults
            const relVelocityInput = document.getElementById('relative-velocity');
            const relAccelerationInput = document.getElementById('relative-acceleration');
            const relDecelerationInput = document.getElementById('relative-deceleration');
            
            if (relVelocityInput) relVelocityInput.value = response.velocity || 60000;
            if (relAccelerationInput) relAccelerationInput.value = response.acceleration || 60000;
            if (relDecelerationInput) relDecelerationInput.value = response.deceleration || 60000;
            
            this.addLogEntry('info', `Motion parameters loaded from profile: ${response.profile_name}`);
            console.log('✅ Default motion parameters loaded successfully');
            
        } catch (error) {
            console.error('❌ Failed to load default motion parameters:', error);
            this.addLogEntry('error', 'Failed to load default motion parameters from configuration');
            
            // Set fallback defaults if config loading fails
            const fallbackValues = { velocity: 60000, acceleration: 60000, deceleration: 60000 };
            
            ['absolute', 'relative'].forEach(type => {
                const velocityInput = document.getElementById(`${type}-velocity`);
                const accelerationInput = document.getElementById(`${type}-acceleration`);
                const decelerationInput = document.getElementById(`${type}-deceleration`);
                
                if (velocityInput) velocityInput.value = fallbackValues.velocity;
                if (accelerationInput) accelerationInput.value = fallbackValues.acceleration;
                if (decelerationInput) decelerationInput.value = fallbackValues.deceleration;
            });
        }
    }

    /**
     * Cleanup when page is deactivated
     */
    cleanup() {
        console.log('🧹 Cleaning up Robot Control Page...');
        
        // Clear intervals
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
        if (this.positionUpdateInterval) {
            clearInterval(this.positionUpdateInterval);
        }
        
        // Remove WebSocket subscriptions
        this.wsManager.unsubscribe('robot-status');
        this.wsManager.unsubscribe('robot-position');
        
        // Remove event listeners
        this.removeEventListeners();
        
        console.log('✅ Robot Control Page cleanup complete');
    }

    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Connection controls
        document.getElementById('robot-connect-btn')?.addEventListener('click', 
            this.handleConnect.bind(this));
        document.getElementById('robot-disconnect-btn')?.addEventListener('click', 
            this.handleDisconnect.bind(this));
        
        // Servo controls
        document.getElementById('robot-servo-on-btn')?.addEventListener('click', 
            this.handleServoOn.bind(this));
        document.getElementById('robot-servo-off-btn')?.addEventListener('click', 
            this.handleServoOff.bind(this));
        
        // Emergency controls
        document.getElementById('robot-emergency-stop-btn')?.addEventListener('click', 
            this.handleEmergencyStop.bind(this));
        document.getElementById('robot-stop-motion-btn')?.addEventListener('click', 
            this.handleStopMotion.bind(this));
        
        // Movement controls
        document.getElementById('robot-home-axis-btn')?.addEventListener('click', 
            this.handleHomeAxis.bind(this));
        document.getElementById('robot-move-absolute-btn')?.addEventListener('click', 
            this.handleMoveAbsolute.bind(this));
        document.getElementById('robot-move-relative-btn')?.addEventListener('click', 
            this.handleMoveRelative.bind(this));
        
        // Position control
        document.getElementById('robot-get-position-btn')?.addEventListener('click', 
            this.handleGetPosition.bind(this));
        document.getElementById('robot-refresh-status-btn')?.addEventListener('click', 
            this.refreshStatus.bind(this));
        
        // Log controls
        document.getElementById('robot-clear-log-btn')?.addEventListener('click', 
            this.handleClearLog.bind(this));
        document.getElementById('robot-export-log-btn')?.addEventListener('click', 
            this.handleExportLog.bind(this));
        
        // Axis selection
        document.getElementById('robot-axis-select')?.addEventListener('change', 
            this.handleAxisChange.bind(this));
    }

    /**
     * Remove event listeners
     * @private
     */
    removeEventListeners() {
        // Remove all event listeners by cloning and replacing elements
        const buttons = [
            'robot-connect-btn', 'robot-disconnect-btn',
            'robot-servo-on-btn', 'robot-servo-off-btn',
            'robot-emergency-stop-btn', 'robot-stop-motion-btn',
            'robot-home-axis-btn', 'robot-move-absolute-btn', 'robot-move-relative-btn',
            'robot-get-position-btn', 'robot-refresh-status-btn',
            'robot-clear-log-btn', 'robot-export-log-btn'
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
        // Subscribe to robot status updates
        this.wsManager.subscribe('robot-status', (data) => {
            this.handleStatusUpdate(data);
        });
        
        // Subscribe to robot position updates
        this.wsManager.subscribe('robot-position', (data) => {
            this.handlePositionUpdate(data);
        });
        
        // Subscribe to robot errors
        this.wsManager.subscribe('robot-error', (data) => {
            this.handleErrorUpdate(data);
        });
    }

    /**
     * Setup tab navigation
     * @private
     */
    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
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
     * Start periodic status updates
     * @private
     */
    startPeriodicUpdates() {
        // Status update every 5 seconds
        this.statusUpdateInterval = setInterval(() => {
            if (this.isConnected) {
                this.refreshStatus();
            }
        }, 5000);
        
        // Position update every 2 seconds when connected
        this.positionUpdateInterval = setInterval(() => {
            if (this.isConnected) {
                this.updatePosition();
            }
        }, 2000);
    }

    // =========================
    // Axis Configuration
    // =========================

    /**
     * Handle axis selection change
     */
    handleAxisChange() {
        const axisSelect = document.getElementById('robot-axis-select');
        if (axisSelect) {
            this.axisId = parseInt(axisSelect.value);
            this.addLogEntry('info', `Axis selection changed to: ${this.axisId}`);
            console.log(`Robot axis changed to: ${this.axisId}`);
        }
    }

    // =========================
    // Connection Management
    // =========================

    /**
     * Handle robot connection
     */
    async handleConnect() {
        try {
            this.uiManager.showElementLoading('#robot-connect-btn', 'Connecting...');
            
            const response = await this.apiClient.post('/hardware/robot/connect', {
                axis_id: this.axisId,
                irq_no: this.irqNo
            });
            
            if (response.success) {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.addLogEntry('success', 'Robot connected successfully');
                this.uiManager.showNotification('Robot connected successfully', 'success');
            } else {
                throw new Error(response.error || 'Connection failed');
            }
            
        } catch (error) {
            console.error('Robot connection failed:', error);
            this.addLogEntry('error', `Connection failed: ${error.message}`);
            this.uiManager.showNotification(`Robot connection failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#robot-connect-btn');
        }
    }

    /**
     * Handle robot disconnection
     */
    async handleDisconnect() {
        try {
            this.uiManager.showElementLoading('#robot-disconnect-btn', 'Disconnecting...');
            
            const response = await this.apiClient.post('/hardware/robot/disconnect');
            
            if (response.success) {
                this.isConnected = false;
                this.servoEnabled = false;
                this.updateConnectionStatus(false);
                this.addLogEntry('info', 'Robot disconnected successfully');
                this.uiManager.showNotification('Robot disconnected successfully', 'info');
            } else {
                throw new Error(response.error || 'Disconnection failed');
            }
            
        } catch (error) {
            console.error('Robot disconnection failed:', error);
            this.addLogEntry('error', `Disconnection failed: ${error.message}`);
            this.uiManager.showNotification(`Robot disconnection failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#robot-disconnect-btn');
        }
    }

    /**
     * Update connection status display
     * @private
     * @param {boolean} connected - Connection state
     */
    updateConnectionStatus(connected) {
        const statusBadge = document.getElementById('robot-status-badge');
        const connectionStatus = document.getElementById('robot-connection-status');
        const connectBtn = document.getElementById('robot-connect-btn');
        const disconnectBtn = document.getElementById('robot-disconnect-btn');
        
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
            'robot-servo-on-btn', 'robot-servo-off-btn',
            'robot-home-axis-btn', 'robot-move-absolute-btn', 'robot-move-relative-btn',
            'robot-get-position-btn', 'robot-stop-motion-btn'
        ];
        
        buttons.forEach(id => {
            const button = document.getElementById(id);
            if (button) {
                button.disabled = !connected;
            }
        });
    }

    // =========================
    // Servo Control
    // =========================

    /**
     * Handle servo enable
     */
    async handleServoOn() {
        try {
            if (this.requireConfirmations) {
                const result = await this.uiManager.showModal({
                    title: '⚠️ Enable Servo Motor',
                    message: `
                        <p><strong>WARNING:</strong> This will enable motor power!</p>
                        <p>Ensure all safety precautions are in place before proceeding.</p>
                        <ul>
                            <li>Check workspace is clear</li>
                            <li>Verify emergency stop accessibility</li>
                            <li>Confirm proper positioning</li>
                        </ul>
                    `,
                    type: 'warning',
                    buttons: [
                        { text: 'Cancel', action: 'cancel', variant: 'secondary' },
                        { text: 'Enable Servo', action: 'confirm', variant: 'warning' }
                    ]
                });
                
                if (result.action !== 'confirm') {
                    return;
                }
            }
            
            this.uiManager.showElementLoading('#robot-servo-on-btn', 'Enabling...');
            
            const response = await this.apiClient.post('/hardware/robot/servo/enable', {
                axis_id: this.axisId
            });
            
            if (response.success) {
                this.servoEnabled = true;
                this.updateServoStatus(true);
                this.addLogEntry('success', `Servo enabled for axis ${this.axisId}`);
                this.uiManager.showNotification('Servo enabled successfully', 'success');
            } else {
                throw new Error(response.error || 'Servo enable failed');
            }
            
        } catch (error) {
            console.error('Servo enable failed:', error);
            this.addLogEntry('error', `Servo enable failed: ${error.message}`);
            this.uiManager.showNotification(`Servo enable failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#robot-servo-on-btn');
        }
    }

    /**
     * Handle servo disable
     */
    async handleServoOff() {
        try {
            this.uiManager.showElementLoading('#robot-servo-off-btn', 'Disabling...');
            
            const response = await this.apiClient.post('/hardware/robot/servo/disable', {
                axis_id: this.axisId
            });
            
            if (response.success) {
                this.servoEnabled = false;
                this.updateServoStatus(false);
                this.addLogEntry('info', `Servo disabled for axis ${this.axisId}`);
                this.uiManager.showNotification('Servo disabled successfully', 'info');
            } else {
                throw new Error(response.error || 'Servo disable failed');
            }
            
        } catch (error) {
            console.error('Servo disable failed:', error);
            this.addLogEntry('error', `Servo disable failed: ${error.message}`);
            this.uiManager.showNotification(`Servo disable failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#robot-servo-off-btn');
        }
    }

    /**
     * Update servo status display
     * @private
     * @param {boolean} enabled - Servo state
     */
    updateServoStatus(enabled) {
        const servoStatus = document.getElementById('robot-servo-status');
        
        if (servoStatus) {
            const statusDot = servoStatus.querySelector('.status-dot');
            const statusSpan = servoStatus.querySelector('span');
            
            statusDot.className = `status-dot status-${enabled ? 'success' : 'warning'}`;
            statusSpan.textContent = enabled ? 'Enabled' : 'Disabled';
        }
    }

    // =========================
    // Emergency and Safety
    // =========================

    /**
     * Handle emergency stop
     */
    async handleEmergencyStop() {
        try {
            // Emergency stop should work immediately without confirmation
            const response = await this.apiClient.post('/hardware/robot/emergency-stop', {
                axis_id: this.axisId
            });
            
            if (response.success) {
                this.motionStatus = 'stopped';
                this.updateMotionStatus('emergency_stopped');
                this.addLogEntry('warning', `Emergency stop executed for axis ${this.axisId}`);
                this.uiManager.showNotification('Emergency stop executed successfully', 'warning');
            } else {
                throw new Error(response.error || 'Emergency stop failed');
            }
            
        } catch (error) {
            console.error('Emergency stop failed:', error);
            this.addLogEntry('error', `Emergency stop failed: ${error.message}`);
            this.uiManager.showNotification(`Emergency stop failed: ${error.message}`, 'error');
        }
    }

    /**
     * Handle controlled motion stop
     */
    async handleStopMotion() {
        try {
            this.uiManager.showElementLoading('#robot-stop-motion-btn', 'Stopping...');
            
            const response = await this.apiClient.post('/hardware/robot/stop-motion', {
                axis_id: this.axisId,
                deceleration: 1000.0 // Use default deceleration
            });
            
            if (response.success) {
                this.motionStatus = 'stopping';
                this.updateMotionStatus('stopping');
                this.addLogEntry('info', `Motion stop initiated for axis ${this.axisId}`);
                this.uiManager.showNotification('Motion stop initiated', 'info');
            } else {
                throw new Error(response.error || 'Motion stop failed');
            }
            
        } catch (error) {
            console.error('Motion stop failed:', error);
            this.addLogEntry('error', `Motion stop failed: ${error.message}`);
            this.uiManager.showNotification(`Motion stop failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#robot-stop-motion-btn');
        }
    }

    // =========================
    // Movement Control
    // =========================

    /**
     * Handle home axis operation
     */
    async handleHomeAxis() {
        try {
            if (this.requireConfirmations) {
                const result = await this.uiManager.showModal({
                    title: '🏠 Home Axis',
                    message: `
                        <p>This will move axis ${this.axisId} to the origin position (0.000 μm).</p>
                        <p><strong>Ensure the axis path is clear before proceeding.</strong></p>
                    `,
                    type: 'question',
                    buttons: [
                        { text: 'Cancel', action: 'cancel', variant: 'secondary' },
                        { text: 'Home Axis', action: 'confirm', variant: 'primary' }
                    ]
                });
                
                if (result.action !== 'confirm') {
                    return;
                }
            }
            
            this.uiManager.showElementLoading('#robot-home-axis-btn', 'Homing...');
            
            const response = await this.apiClient.post('/hardware/robot/home-axis', {
                axis_id: this.axisId
            });
            
            if (response.success) {
                this.motionStatus = 'homing';
                this.updateMotionStatus('moving');
                this.addLogEntry('info', `Homing axis ${this.axisId} to origin`);
                this.uiManager.showNotification('Axis homing started', 'info');
                
                // Update position display after homing completes
                setTimeout(() => this.updatePosition(), 3000);
            } else {
                throw new Error(response.error || 'Homing failed');
            }
            
        } catch (error) {
            console.error('Homing failed:', error);
            this.addLogEntry('error', `Homing failed: ${error.message}`);
            this.uiManager.showNotification(`Homing failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#robot-home-axis-btn');
        }
    }

    /**
     * Handle absolute move operation
     */
    async handleMoveAbsolute() {
        try {
            // Get form values
            const position = parseFloat(document.getElementById('absolute-position').value);
            const velocity = parseFloat(document.getElementById('absolute-velocity').value);
            const acceleration = parseFloat(document.getElementById('absolute-acceleration').value);
            const deceleration = parseFloat(document.getElementById('absolute-deceleration').value);
            
            // Validate inputs
            if (!this.validateMotionParameters(position, velocity, acceleration, deceleration)) {
                return;
            }
            
            if (this.requireConfirmations) {
                const result = await this.uiManager.showModal({
                    title: '📍 Absolute Move',
                    message: `
                        <p>Move axis ${this.axisId} to position <strong>${position.toFixed(3)} μm</strong></p>
                        <div class="motion-preview">
                            <div><strong>Motion Parameters:</strong></div>
                            <ul>
                                <li>Velocity: ${velocity.toFixed(1)} μm/s</li>
                                <li>Acceleration: ${acceleration.toFixed(0)} μm/s²</li>
                                <li>Deceleration: ${deceleration.toFixed(0)} μm/s²</li>
                            </ul>
                        </div>
                        <p><strong>Ensure the axis path is clear before proceeding.</strong></p>
                    `,
                    type: 'question',
                    buttons: [
                        { text: 'Cancel', action: 'cancel', variant: 'secondary' },
                        { text: 'Execute Move', action: 'confirm', variant: 'primary' }
                    ]
                });
                
                if (result.action !== 'confirm') {
                    return;
                }
            }
            
            this.uiManager.showElementLoading('#robot-move-absolute-btn', 'Moving...');
            
            const response = await this.apiClient.post('/hardware/robot/move-absolute', {
                axis_id: this.axisId,
                position: position,
                velocity: velocity,
                acceleration: acceleration,
                deceleration: deceleration
            });
            
            if (response.success) {
                this.motionStatus = 'moving';
                this.updateMotionStatus('moving');
                this.addLogEntry('info', `Moving axis ${this.axisId} to position ${position.toFixed(3)} μm`);
                this.uiManager.showNotification(`Moving to position ${position.toFixed(3)} μm`, 'info');
            } else {
                throw new Error(response.error || 'Absolute move failed');
            }
            
        } catch (error) {
            console.error('Absolute move failed:', error);
            this.addLogEntry('error', `Absolute move failed: ${error.message}`);
            this.uiManager.showNotification(`Absolute move failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#robot-move-absolute-btn');
        }
    }

    /**
     * Handle relative move operation
     */
    async handleMoveRelative() {
        try {
            // Get form values
            const distance = parseFloat(document.getElementById('relative-distance').value);
            const velocity = parseFloat(document.getElementById('relative-velocity').value);
            const acceleration = parseFloat(document.getElementById('relative-acceleration').value);
            const deceleration = parseFloat(document.getElementById('relative-deceleration').value);
            
            // Validate inputs
            if (!this.validateMotionParameters(distance, velocity, acceleration, deceleration)) {
                return;
            }
            
            if (this.requireConfirmations) {
                const result = await this.uiManager.showModal({
                    title: '↔️ Relative Move',
                    message: `
                        <p>Move axis ${this.axisId} by distance <strong>${distance.toFixed(3)} μm</strong></p>
                        <div class="motion-preview">
                            <div><strong>Motion Parameters:</strong></div>
                            <ul>
                                <li>Velocity: ${velocity.toFixed(1)} μm/s</li>
                                <li>Acceleration: ${acceleration.toFixed(0)} μm/s²</li>
                                <li>Deceleration: ${deceleration.toFixed(0)} μm/s²</li>
                            </ul>
                        </div>
                        <p><strong>Ensure the axis path is clear before proceeding.</strong></p>
                    `,
                    type: 'question',
                    buttons: [
                        { text: 'Cancel', action: 'cancel', variant: 'secondary' },
                        { text: 'Execute Move', action: 'confirm', variant: 'primary' }
                    ]
                });
                
                if (result.action !== 'confirm') {
                    return;
                }
            }
            
            this.uiManager.showElementLoading('#robot-move-relative-btn', 'Moving...');
            
            const response = await this.apiClient.post('/hardware/robot/move-relative', {
                axis_id: this.axisId,
                distance: distance,
                velocity: velocity,
                acceleration: acceleration,
                deceleration: deceleration
            });
            
            if (response.success) {
                this.motionStatus = 'moving';
                this.updateMotionStatus('moving');
                this.addLogEntry('info', `Moving axis ${this.axisId} by distance ${distance.toFixed(3)} μm`);
                this.uiManager.showNotification(`Moving distance ${distance.toFixed(3)} μm`, 'info');
            } else {
                throw new Error(response.error || 'Relative move failed');
            }
            
        } catch (error) {
            console.error('Relative move failed:', error);
            this.addLogEntry('error', `Relative move failed: ${error.message}`);
            this.uiManager.showNotification(`Relative move failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#robot-move-relative-btn');
        }
    }

    /**
     * Validate motion parameters
     * @private
     * @param {number} position - Position or distance
     * @param {number} velocity - Velocity
     * @param {number} acceleration - Acceleration
     * @param {number} deceleration - Deceleration
     * @returns {boolean} True if valid
     */
    validateMotionParameters(position, velocity, acceleration, deceleration) {
        // Check if values are numbers
        if (isNaN(position) || isNaN(velocity) || isNaN(acceleration) || isNaN(deceleration)) {
            this.uiManager.showNotification('Please enter valid numeric values for all parameters', 'error');
            return false;
        }
        
        // Check ranges
        if (position < 0 || position > 500000) {
            this.uiManager.showNotification('Position/Distance must be between 0 and 500,000 μm', 'error');
            return false;
        }
        
        if (velocity < 1 || velocity > 60000) {
            this.uiManager.showNotification('Velocity must be between 1 and 60,000 μm/s', 'error');
            return false;
        }
        
        if (acceleration < 100 || acceleration > 60000) {
            this.uiManager.showNotification('Acceleration must be between 100 and 60,000 μm/s²', 'error');
            return false;
        }
        
        if (deceleration < 100 || deceleration > 60000) {
            this.uiManager.showNotification('Deceleration must be between 100 and 60,000 μm/s²', 'error');
            return false;
        }
        
        return true;
    }

    // =========================
    // Position and Status
    // =========================

    /**
     * Handle get position operation
     */
    async handleGetPosition() {
        try {
            this.uiManager.showElementLoading('#robot-get-position-btn', 'Reading...');
            
            const response = await this.apiClient.get(`/hardware/robot/position?axis_id=${this.axisId}`);
            
            if (response.success && response.data) {
                this.currentPosition = response.data.position;
                this.updatePositionDisplay(this.currentPosition);
                this.addLogEntry('info', `Position read: ${this.currentPosition.toFixed(3)} μm`);
                this.uiManager.showNotification(`Position: ${this.currentPosition.toFixed(3)} μm`, 'success');
            } else {
                throw new Error(response.error || 'Failed to read position');
            }
            
        } catch (error) {
            console.error('Get position failed:', error);
            this.addLogEntry('error', `Get position failed: ${error.message}`);
            this.uiManager.showNotification(`Get position failed: ${error.message}`, 'error');
        } finally {
            this.uiManager.hideElementLoading('#robot-get-position-btn');
        }
    }

    /**
     * Update position from WebSocket or periodic updates
     * @private
     */
    async updatePosition() {
        try {
            const response = await this.apiClient.get(`/hardware/robot/position?axis_id=${this.axisId}`);
            
            if (response.success && response.data) {
                this.currentPosition = response.data.position;
                this.updatePositionDisplay(this.currentPosition);
            }
            
        } catch (error) {
            // Silently fail for background updates
            console.warn('Background position update failed:', error);
        }
    }

    /**
     * Update position display
     * @private
     * @param {number} position - Position in μm
     */
    updatePositionDisplay(position) {
        const positionElement = document.getElementById('robot-current-position');
        
        if (positionElement) {
            const valueSpan = positionElement.querySelector('.value');
            if (valueSpan) {
                valueSpan.textContent = position !== null ? position.toFixed(3) : '---.---';
            }
        }
    }

    /**
     * Update motion status display
     * @private
     * @param {string} status - Motion status
     */
    updateMotionStatus(status) {
        const motionStatus = document.getElementById('robot-motion-status');
        
        if (motionStatus) {
            const statusDot = motionStatus.querySelector('.status-dot');
            const statusSpan = motionStatus.querySelector('span');
            
            let statusClass = 'status-unknown';
            let statusText = 'Unknown';
            
            switch (status) {
                case 'idle':
                    statusClass = 'status-success';
                    statusText = 'Idle';
                    break;
                case 'moving':
                    statusClass = 'status-warning';
                    statusText = 'Moving';
                    break;
                case 'stopping':
                    statusClass = 'status-warning';
                    statusText = 'Stopping';
                    break;
                case 'emergency_stopped':
                    statusClass = 'status-error';
                    statusText = 'Emergency Stopped';
                    break;
            }
            
            statusDot.className = `status-dot ${statusClass}`;
            statusSpan.textContent = statusText;
        }
    }

    /**
     * Refresh overall status
     */
    async refreshStatus() {
        try {
            const response = await this.apiClient.get('/hardware/robot/status');
            
            if (response.success && response.data) {
                const status = response.data;
                
                this.isConnected = status.connected || false;
                this.servoEnabled = status.servo_enabled || false;
                this.isInitialized = status.initialized || false;
                this.motionStatus = status.motion_status || 'idle';
                
                // Update displays
                this.updateConnectionStatus(this.isConnected);
                this.updateServoStatus(this.servoEnabled);
                this.updateMotionStatus(this.motionStatus);
                this.updateInitializationStatus(this.isInitialized);
                
                if (status.position !== undefined) {
                    this.currentPosition = status.position;
                    this.updatePositionDisplay(this.currentPosition);
                }
            }
            
        } catch (error) {
            console.warn('Status refresh failed:', error);
        }
    }

    /**
     * Update initialization status display
     * @private
     * @param {boolean} initialized - Initialization state
     */
    updateInitializationStatus(initialized) {
        const initStatus = document.getElementById('robot-init-status');
        
        if (initStatus) {
            const statusDot = initStatus.querySelector('.status-dot');
            const statusSpan = initStatus.querySelector('span');
            
            statusDot.className = `status-dot status-${initialized ? 'success' : 'warning'}`;
            statusSpan.textContent = initialized ? 'Ready' : 'Not Initialized';
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
        if (data.component === 'robot') {
            this.isConnected = data.connected;
            this.servoEnabled = data.servo_enabled;
            this.motionStatus = data.motion_status;
            this.isInitialized = data.initialized;
            
            this.updateConnectionStatus(this.isConnected);
            this.updateServoStatus(this.servoEnabled);
            this.updateMotionStatus(this.motionStatus);
            this.updateInitializationStatus(this.isInitialized);
        }
    }

    /**
     * Handle position update from WebSocket
     * @private
     * @param {Object} data - Position data
     */
    handlePositionUpdate(data) {
        if (data.component === 'robot' && data.axis_id === this.axisId) {
            this.currentPosition = data.position;
            this.updatePositionDisplay(this.currentPosition);
        }
    }

    /**
     * Handle error update from WebSocket
     * @private
     * @param {Object} data - Error data
     */
    handleErrorUpdate(data) {
        if (data.component === 'robot') {
            this.addLogEntry('error', data.message);
            this.uiManager.showNotification(`Robot Error: ${data.message}`, 'error');
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
        const logViewer = document.getElementById('robot-log-viewer');
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
        a.download = `robot-log-${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addLogEntry('info', 'Operation log exported');
    }
}

console.log('📝 Robot Control Page Manager loaded successfully');