/**
 * Robot Home Page Manager - WF EOL Tester Web Interface
 * 
 * This module manages the Robot Home page including:
 * - Robot homing operation control and monitoring
 * - Robot position and status display
 * - Safety controls and emergency stop integration
 * - Real-time progress tracking and feedback
 * - Operation history and logging
 * - Hardware monitoring and diagnostics
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

/**
 * Robot Home Page Manager Class
 * 
 * Manages the complete lifecycle of robot homing operations with real-time
 * monitoring, safety controls, and comprehensive status feedback.
 */
export class RobotHomePageManager {
    /**
     * Initialize Robot Home page manager
     * @param {APIClient} apiClient - API client instance
     * @param {WebSocketManager} websocketManager - WebSocket manager instance
     * @param {UIManager} uiManager - UI manager instance
     */
    constructor(apiClient, websocketManager, uiManager) {
        console.log('🏠 Initializing Robot Home page manager...');
        
        // Core dependencies
        this.apiClient = apiClient;
        this.websocketManager = websocketManager;
        this.uiManager = uiManager;
        
        // Robot state
        this.robotStatus = {
            connected: false,
            servoEnabled: false,
            isHomed: false,
            hasError: false,
            position: { x: 0, y: 0, z: 0 },
            targetPosition: { x: 0, y: 0, z: 0 },
            model: '--',
            firmware: '--',
            temperature: 0,
            voltage: 0
        };
        
        // Operation state
        this.operationState = 'idle'; // idle, running, completed, error
        this.currentOperation = null;
        
        // Progress tracking
        this.homeSteps = [
            { id: 1, name: 'Initialize', progress: 0 },
            { id: 2, name: 'Enable Servo', progress: 0 },
            { id: 3, name: 'Home Axes', progress: 0 },
            { id: 4, name: 'Verify', progress: 0 },
            { id: 5, name: 'Complete', progress: 0 }
        ];
        this.currentStep = 0;
        this.overallProgress = 0;
        
        // Real-time data
        this.homingData = {
            startTime: null,
            elapsedTime: 0,
            estimatedTime: 30, // seconds
            distanceToHome: 0,
            accuracy: 0
        };
        
        // Hardware monitoring
        this.hardwareStatus = {
            mainPower: false,
            servoPower: false,
            current: 0,
            consumption: 0,
            estopStatus: true, // true = normal, false = activated
            safetyCurtain: true,
            doorLock: true,
            areaClear: true
        };
        
        // Operation history
        this.operationHistory = [];
        
        // Update intervals
        this.statusUpdateInterval = null;
        this.progressUpdateInterval = null;
        
        // Bind methods
        this.handleStartHoming = this.handleStartHoming.bind(this);
        this.handleEmergencyStop = this.handleEmergencyStop.bind(this);
        this.handleServoEnable = this.handleServoEnable.bind(this);
        this.handleServoDisable = this.handleServoDisable.bind(this);
        this.handleRobotStatusUpdate = this.handleRobotStatusUpdate.bind(this);
        this.handleHardwareUpdate = this.handleHardwareUpdate.bind(this);
        
        // Initialize page
        this.init();
        
        console.log('✅ Robot Home page manager initialized');
    }
    
    /**
     * Initialize page manager
     * @private
     */
    init() {
        try {
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup WebSocket subscriptions
            this.setupWebSocketSubscriptions();
            
            // Load initial data
            this.loadInitialData();
            
            // Start monitoring
            this.startStatusMonitoring();
            
            console.log('✅ Robot Home page initialization complete');
            
        } catch (error) {
            console.error('❌ Robot Home page initialization failed:', error);
            this.showError('Failed to initialize Robot Home page', error);
        }
    }
    
    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Main control buttons
        const startHomeBtn = document.getElementById('start-home-btn');
        const emergencyBtn = document.getElementById('emergency-stop-robot');
        const servoEnableBtn = document.getElementById('servo-enable-btn');
        const servoDisableBtn = document.getElementById('servo-disable-btn');
        
        if (startHomeBtn) startHomeBtn.addEventListener('click', this.handleStartHoming);
        if (emergencyBtn) emergencyBtn.addEventListener('click', this.handleEmergencyStop);
        if (servoEnableBtn) servoEnableBtn.addEventListener('click', this.handleServoEnable);
        if (servoDisableBtn) servoDisableBtn.addEventListener('click', this.handleServoDisable);
        
        // History controls
        const refreshHistoryBtn = document.getElementById('refresh-history-btn');
        const exportHistoryBtn = document.getElementById('export-history-btn');
        
        if (refreshHistoryBtn) refreshHistoryBtn.addEventListener('click', this.loadOperationHistory.bind(this));
        if (exportHistoryBtn) exportHistoryBtn.addEventListener('click', this.exportHistory.bind(this));
        
        // Log controls
        const clearLogBtn = document.getElementById('clear-robot-log-btn');
        const exportLogBtn = document.getElementById('export-robot-log-btn');
        
        if (clearLogBtn) clearLogBtn.addEventListener('click', this.clearLog.bind(this));
        if (exportLogBtn) exportLogBtn.addEventListener('click', this.exportLog.bind(this));
        
        console.log('✅ Event listeners setup complete');
    }
    
    /**
     * Setup WebSocket subscriptions
     * @private
     */
    setupWebSocketSubscriptions() {
        if (!this.websocketManager) {
            console.warn('WebSocket manager not available');
            return;
        }
        
        try {
            // Subscribe to robot status updates
            this.websocketManager.on('robot-status', this.handleRobotStatusUpdate);
            
            // Subscribe to hardware status updates
            this.websocketManager.on('hardware-status', this.handleHardwareUpdate);
            
            // Subscribe to homing progress updates
            this.websocketManager.on('homing-progress', this.handleHomingProgress.bind(this));
            
            console.log('✅ WebSocket subscriptions setup');
            
        } catch (error) {
            console.error('❌ Failed to setup WebSocket subscriptions:', error);
        }
    }
    
    /**
     * Load initial data
     * @private
     */
    async loadInitialData() {
        try {
            // Load robot status
            await this.loadRobotStatus();
            
            // Load hardware status
            await this.loadHardwareStatus();
            
            // Load operation history
            await this.loadOperationHistory();
            
            // Update displays
            this.updateRobotStatusDisplay();
            this.updateHardwareDisplay();
            this.updateControlButtons();
            
            console.log('✅ Initial data loaded');
            
        } catch (error) {
            console.error('❌ Failed to load initial data:', error);
        }
    }
    
    /**
     * Start status monitoring
     * @private
     */
    startStatusMonitoring() {
        // Update robot status every 2 seconds
        this.statusUpdateInterval = setInterval(async () => {
            try {
                await this.loadRobotStatus();
                await this.loadHardwareStatus();
            } catch (error) {
                console.warn('Status update failed:', error);
            }
        }, 2000);
    }
    
    // =========================
    // Robot Control Methods
    // =========================
    
    /**
     * Handle start homing button click
     * @private
     */
    async handleStartHoming() {
        try {
            console.log('🏠 Starting robot homing operation...');
            
            // Show safety confirmation
            const confirmed = await this.showSafetyConfirmation();
            if (!confirmed) {
                this.addLogEntry('info', 'Homing operation cancelled by user');
                return;
            }
            
            // Validate robot is ready
            if (!this.validateRobotReady()) {
                return;
            }
            
            // Start homing operation
            await this.startHomingOperation();
            
        } catch (error) {
            console.error('❌ Failed to start homing:', error);
            this.showError('Homing Start Failed', error.message);
        }
    }
    
    /**
     * Start the actual homing operation
     * @private
     */
    async startHomingOperation() {
        try {
            // Update UI state
            this.setOperationState('running');
            this.showProgressSection();
            this.updateControlButtons();
            
            // Reset progress
            this.resetProgress();
            
            // Send homing command to API
            const response = await this.apiClient.post('/hardware/robot/control', {
                action: 'home',
                parameters: {}
            });
            
            this.currentOperation = response.data;
            this.homingData.startTime = Date.now();
            
            this.addLogEntry('success', 'Robot homing operation started');
            
            // Start progress monitoring
            this.startProgressMonitoring();
            
        } catch (error) {
            this.setOperationState('error');
            throw error;
        }
    }
    
    /**
     * Handle emergency stop
     * @private
     */
    async handleEmergencyStop() {
        try {
            console.log('🚨 Robot emergency stop activated!');
            
            // Immediate API call
            await this.apiClient.post('/hardware/emergency-stop');
            
            // Stop operation
            this.stopOperation(true);
            
            // Show emergency modal
            this.uiManager.showModal({
                title: '🛑 Emergency Stop',
                message: 'Emergency stop has been activated. All robot operations have been halted.',
                type: 'error'
            });
            
            this.addLogEntry('error', 'EMERGENCY STOP ACTIVATED');
            
        } catch (error) {
            console.error('❌ Emergency stop failed:', error);
            this.showError('Emergency Stop Failed', error.message);
        }
    }
    
    /**
     * Handle servo enable
     * @private
     */
    async handleServoEnable() {
        try {
            console.log('⚡ Enabling robot servo...');
            
            await this.apiClient.post('/hardware/robot/control', {
                action: 'servo_on',
                parameters: {}
            });
            
            this.addLogEntry('info', 'Robot servo enabled');
            
        } catch (error) {
            console.error('❌ Failed to enable servo:', error);
            this.showError('Servo Enable Failed', error.message);
        }
    }
    
    /**
     * Handle servo disable
     * @private
     */
    async handleServoDisable() {
        try {
            console.log('🔌 Disabling robot servo...');
            
            const confirmed = await this.uiManager.showModal({
                title: 'Disable Servo',
                message: 'Are you sure you want to disable the robot servo? This will stop all robot movements.',
                type: 'warning',
                buttons: [
                    { text: 'Cancel', action: 'cancel', variant: 'secondary' },
                    { text: 'Disable', action: 'confirm', variant: 'warning' }
                ]
            });
            
            if (confirmed.action !== 'confirm') return;
            
            await this.apiClient.post('/hardware/robot/control', {
                action: 'servo_off',
                parameters: {}
            });
            
            this.addLogEntry('warning', 'Robot servo disabled');
            
        } catch (error) {
            console.error('❌ Failed to disable servo:', error);
            this.showError('Servo Disable Failed', error.message);
        }
    }
    
    /**
     * Stop operation
     * @private
     * @param {boolean} emergency - Whether this is an emergency stop
     */
    stopOperation(emergency = false) {
        // Stop progress monitoring
        this.stopProgressMonitoring();
        
        // Update state
        this.setOperationState(emergency ? 'emergency' : 'completed');
        this.updateControlButtons();
        
        // Show results if not emergency
        if (!emergency && this.currentOperation) {
            this.showOperationResult();
        }
        
        // Clear current operation
        this.currentOperation = null;
        this.homingData.startTime = null;
    }
    
    // =========================
    // Progress Monitoring
    // =========================
    
    /**
     * Start progress monitoring
     * @private
     */
    startProgressMonitoring() {
        // Update progress every 250ms for smooth animation
        this.progressUpdateInterval = setInterval(() => {
            this.updateProgressDisplay();
            this.updateRealTimeStatus();
        }, 250);
    }
    
    /**
     * Stop progress monitoring
     * @private
     */
    stopProgressMonitoring() {
        if (this.progressUpdateInterval) {
            clearInterval(this.progressUpdateInterval);
            this.progressUpdateInterval = null;
        }
    }
    
    /**
     * Handle homing progress updates
     * @private
     * @param {Object} progress - Progress data
     */
    handleHomingProgress(progress) {
        if (!progress || this.operationState !== 'running') return;
        
        // Update progress data
        this.currentStep = progress.currentStep || 0;
        this.overallProgress = progress.percentage || 0;
        this.homingData.distanceToHome = progress.distanceToHome || 0;
        
        // Update robot position if provided
        if (progress.currentPosition) {
            this.robotStatus.position = progress.currentPosition;
        }
        
        // Handle completion
        if (progress.completed) {
            this.handleHomingCompletion(progress);
        }
        
        this.addLogEntry('info', `Homing progress: ${progress.message || `${Math.round(this.overallProgress)}%`}`);
    }
    
    /**
     * Handle homing completion
     * @private
     * @param {Object} result - Completion result
     */
    handleHomingCompletion(result) {
        console.log('✅ Homing completed:', result);
        
        this.stopOperation();
        
        // Update robot status
        this.robotStatus.isHomed = result.success || false;
        this.homingData.accuracy = result.accuracy || 0;
        
        // Show completion notification
        this.uiManager.showNotification(
            `Homing ${result.success ? 'completed successfully' : 'failed'}: ${result.message}`,
            result.success ? 'success' : 'error'
        );
        
        this.addLogEntry(result.success ? 'success' : 'error', 
                        `Homing completed: ${result.message}`);
    }
    
    // =========================
    // Status Update Methods
    // =========================
    
    /**
     * Set operation state
     * @private
     * @param {string} state - New operation state
     */
    setOperationState(state) {
        this.operationState = state;
        
        // Update status badge
        const statusBadge = document.getElementById('robot-home-status');
        if (statusBadge) {
            const indicator = statusBadge.querySelector('.status-indicator');
            const text = statusBadge.querySelector('.status-text');
            
            if (indicator && text) {
                indicator.className = `status-indicator ${this.getStatusClass(state)}`;
                text.textContent = this.getStatusText(state);
            }
        }
        
        // Update home operation status
        const homeOpStatus = document.getElementById('home-operation-status');
        if (homeOpStatus) {
            const indicator = homeOpStatus.querySelector('.status-indicator');
            const text = homeOpStatus.querySelector('.status-text');
            
            if (indicator && text) {
                indicator.className = `status-indicator ${this.getStatusClass(state)}`;
                text.textContent = this.getStatusText(state);
            }
        }
        
        console.log(`📊 Operation state changed to: ${state}`);
    }
    
    /**
     * Get status CSS class for state
     * @private
     * @param {string} state - Operation state
     * @returns {string} CSS class
     */
    getStatusClass(state) {
        const classes = {
            idle: 'ready',
            running: 'active',
            completed: 'success',
            error: 'error',
            emergency: 'error'
        };
        return classes[state] || 'unknown';
    }
    
    /**
     * Get status text for state
     * @private
     * @param {string} state - Operation state
     * @returns {string} Status text
     */
    getStatusText(state) {
        const texts = {
            idle: 'Ready',
            running: 'Homing...',
            completed: 'Completed',
            error: 'Error',
            emergency: 'Emergency Stop'
        };
        return texts[state] || 'Unknown';
    }
    
    /**
     * Update control buttons
     * @private
     */
    updateControlButtons() {
        const startBtn = document.getElementById('start-home-btn');
        const servoEnableBtn = document.getElementById('servo-enable-btn');
        const servoDisableBtn = document.getElementById('servo-disable-btn');
        
        if (!startBtn || !servoEnableBtn || !servoDisableBtn) return;
        
        const isRunning = this.operationState === 'running';
        const isConnected = this.robotStatus.connected;
        const servoEnabled = this.robotStatus.servoEnabled;
        
        startBtn.disabled = !isConnected || isRunning || !servoEnabled;
        servoEnableBtn.disabled = !isConnected || servoEnabled;
        servoDisableBtn.disabled = !isConnected || !servoEnabled || isRunning;
    }
    
    /**
     * Show progress section
     * @private
     */
    showProgressSection() {
        const progressSection = document.getElementById('home-progress-section');
        if (progressSection) {
            progressSection.style.display = 'block';
        }
    }
    
    /**
     * Update progress display
     * @private
     */
    updateProgressDisplay() {
        // Update progress bar
        const progressFill = document.getElementById('home-progress-fill');
        if (progressFill) {
            progressFill.style.width = `${this.overallProgress}%`;
        }
        
        // Update progress percentage
        const progressPercentage = document.getElementById('home-progress-percentage');
        if (progressPercentage) {
            progressPercentage.textContent = `${Math.round(this.overallProgress)}%`;
        }
        
        // Update current step
        const currentStepEl = document.getElementById('home-current-step');
        if (currentStepEl && this.homeSteps[this.currentStep]) {
            currentStepEl.textContent = this.homeSteps[this.currentStep].name;
        }
        
        // Update step indicators
        document.querySelectorAll('.step').forEach((stepEl, index) => {
            const stepNum = index + 1;
            stepEl.classList.toggle('active', stepNum === this.currentStep + 1);
            stepEl.classList.toggle('completed', stepNum < this.currentStep + 1);
        });
    }
    
    /**
     * Update real-time status during operation
     * @private
     */
    updateRealTimeStatus() {
        if (this.operationState !== 'running') return;
        
        // Update elapsed time
        if (this.homingData.startTime) {
            this.homingData.elapsedTime = (Date.now() - this.homingData.startTime) / 1000;
            
            const elapsedEl = document.getElementById('home-elapsed-time');
            if (elapsedEl) {
                const minutes = Math.floor(this.homingData.elapsedTime / 60);
                const seconds = Math.floor(this.homingData.elapsedTime % 60);
                elapsedEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }
        
        // Update distance to home
        const distanceEl = document.getElementById('distance-to-home');
        if (distanceEl) {
            const valueEl = distanceEl.querySelector('.distance-value');
            if (valueEl) {
                valueEl.textContent = `${this.homingData.distanceToHome.toFixed(2)} mm`;
            }
            
            // Update progress bar based on distance
            const progressBar = distanceEl.querySelector('.distance-bar');
            if (progressBar) {
                const maxDistance = 100; // Assume max 100mm travel
                const progress = Math.max(0, (maxDistance - this.homingData.distanceToHome) / maxDistance * 100);
                progressBar.style.width = `${progress}%`;
            }
        }
    }
    
    // =========================
    // Data Loading Methods
    // =========================
    
    /**
     * Load robot status
     * @private
     */
    async loadRobotStatus() {
        try {
            const response = await this.apiClient.get('/hardware/robot/status');
            if (response.data) {
                this.robotStatus = {
                    ...this.robotStatus,
                    connected: response.data.connected || false,
                    servoEnabled: response.data.servoEnabled || false,
                    isHomed: response.data.isHomed || false,
                    hasError: response.data.hasError || false,
                    position: response.data.position || { x: 0, y: 0, z: 0 },
                    model: response.data.model || '--',
                    firmware: response.data.firmware || '--',
                    temperature: response.data.temperature || 0,
                    voltage: response.data.voltage || 0
                };
                this.updateRobotStatusDisplay();
                this.updateControlButtons();
            }
        } catch (error) {
            console.warn('Failed to load robot status:', error);
        }
    }
    
    /**
     * Load hardware status
     * @private
     */
    async loadHardwareStatus() {
        try {
            const response = await this.apiClient.get('/hardware/status');
            if (response.data) {
                this.hardwareStatus = {
                    mainPower: response.data.power?.connected || false,
                    servoPower: response.data.robot?.servoPower || false,
                    current: response.data.power?.current || 0,
                    consumption: response.data.power?.consumption || 0,
                    estopStatus: !response.data.safety?.emergencyStop || true,
                    safetyCurtain: !response.data.safety?.lightCurtain || true,
                    doorLock: response.data.safety?.doorLock || true,
                    areaClear: response.data.safety?.areaClear || true
                };
                this.updateHardwareDisplay();
            }
        } catch (error) {
            console.warn('Failed to load hardware status:', error);
        }
    }
    
    /**
     * Load operation history
     * @private
     */
    async loadOperationHistory() {
        try {
            const response = await this.apiClient.get('/hardware/robot/history', {
                params: { operation: 'home', limit: 20 }
            });
            
            if (response.data) {
                this.operationHistory = response.data;
                this.updateHistoryTable();
            }
        } catch (error) {
            console.warn('Failed to load operation history:', error);
        }
    }
    
    // =========================
    // Display Update Methods
    // =========================
    
    /**
     * Update robot status display
     * @private
     */
    updateRobotStatusDisplay() {
        // Update position display
        const posXEl = document.getElementById('robot-pos-x');
        const posYEl = document.getElementById('robot-pos-y');
        const posZEl = document.getElementById('robot-pos-z');
        
        if (posXEl) posXEl.textContent = `${this.robotStatus.position.x.toFixed(2)} mm`;
        if (posYEl) posYEl.textContent = `${this.robotStatus.position.y.toFixed(2)} mm`;
        if (posZEl) posZEl.textContent = `${this.robotStatus.position.z.toFixed(2)} mm`;
        
        // Update connection status
        const connectionEl = document.getElementById('robot-connection');
        if (connectionEl) {
            const indicator = connectionEl.querySelector('.status-indicator');
            const text = connectionEl.textContent || connectionEl.innerHTML;
            
            if (indicator) {
                indicator.className = `status-indicator ${this.robotStatus.connected ? 'connected' : 'disconnected'}`;
            }
            // Update text part only
            const textParts = text.split('</span>');
            if (textParts.length > 1) {
                connectionEl.innerHTML = textParts[0] + '</span>' + (this.robotStatus.connected ? 'Connected' : 'Disconnected');
            }
        }
        
        // Update servo state
        const servoEl = document.getElementById('robot-servo');
        if (servoEl) {
            const indicator = servoEl.querySelector('.status-indicator');
            if (indicator) {
                indicator.className = `status-indicator ${this.robotStatus.servoEnabled ? 'on' : 'off'}`;
            }
            const textNode = Array.from(servoEl.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
            if (textNode) {
                textNode.textContent = this.robotStatus.servoEnabled ? 'On' : 'Off';
            }
        }
        
        // Update home state
        const homeStateEl = document.getElementById('robot-home-state');
        if (homeStateEl) {
            const indicator = homeStateEl.querySelector('.status-indicator');
            if (indicator) {
                indicator.className = `status-indicator ${this.robotStatus.isHomed ? 'homed' : 'not-homed'}`;
            }
            const textNode = Array.from(homeStateEl.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
            if (textNode) {
                textNode.textContent = this.robotStatus.isHomed ? 'Homed' : 'Not Homed';
            }
        }
        
        // Update error state
        const errorEl = document.getElementById('robot-error');
        if (errorEl) {
            const indicator = errorEl.querySelector('.status-indicator');
            if (indicator) {
                indicator.className = `status-indicator ${this.robotStatus.hasError ? 'error' : 'ok'}`;
            }
            const textNode = Array.from(errorEl.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
            if (textNode) {
                textNode.textContent = this.robotStatus.hasError ? 'Error Present' : 'No Errors';
            }
        }
        
        // Update robot details
        const modelEl = document.getElementById('robot-model');
        const firmwareEl = document.getElementById('robot-firmware');
        const tempEl = document.getElementById('robot-temperature');
        const voltageEl = document.getElementById('robot-voltage');
        
        if (modelEl) modelEl.textContent = this.robotStatus.model;
        if (firmwareEl) firmwareEl.textContent = this.robotStatus.firmware;
        if (tempEl) tempEl.textContent = `${this.robotStatus.temperature} °C`;
        if (voltageEl) voltageEl.textContent = `${this.robotStatus.voltage} V`;
    }
    
    /**
     * Update hardware display
     * @private
     */
    updateHardwareDisplay() {
        // Update power status
        const mainPowerEl = document.getElementById('main-power');
        const servoPowerEl = document.getElementById('servo-power');
        const currentEl = document.getElementById('power-current');
        const consumptionEl = document.getElementById('power-consumption');
        
        if (mainPowerEl) {
            const indicator = mainPowerEl.querySelector('.status-indicator');
            if (indicator) {
                indicator.className = `status-indicator ${this.hardwareStatus.mainPower ? 'on' : 'off'}`;
            }
            const textNode = Array.from(mainPowerEl.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
            if (textNode) {
                textNode.textContent = this.hardwareStatus.mainPower ? 'On' : 'Off';
            }
        }
        
        if (servoPowerEl) {
            const indicator = servoPowerEl.querySelector('.status-indicator');
            if (indicator) {
                indicator.className = `status-indicator ${this.hardwareStatus.servoPower ? 'on' : 'off'}`;
            }
            const textNode = Array.from(servoPowerEl.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
            if (textNode) {
                textNode.textContent = this.hardwareStatus.servoPower ? 'On' : 'Off';
            }
        }
        
        if (currentEl) currentEl.textContent = `${this.hardwareStatus.current.toFixed(2)} A`;
        if (consumptionEl) consumptionEl.textContent = `${this.hardwareStatus.consumption.toFixed(1)} W`;
        
        // Update safety status
        const estopEl = document.getElementById('estop-status');
        const curtainEl = document.getElementById('safety-curtain');
        const doorLockEl = document.getElementById('door-lock');
        const areaClearEl = document.getElementById('area-clear');
        
        const safetyElements = [
            { element: estopEl, status: this.hardwareStatus.estopStatus, normalText: 'Normal', errorText: 'Activated' },
            { element: curtainEl, status: this.hardwareStatus.safetyCurtain, normalText: 'Clear', errorText: 'Blocked' },
            { element: doorLockEl, status: this.hardwareStatus.doorLock, normalText: 'Secured', errorText: 'Open' },
            { element: areaClearEl, status: this.hardwareStatus.areaClear, normalText: 'Safe', errorText: 'Occupied' }
        ];
        
        safetyElements.forEach(({ element, status, normalText, errorText }) => {
            if (element) {
                const indicator = element.querySelector('.status-indicator');
                if (indicator) {
                    indicator.className = `status-indicator ${status ? 'ok' : 'error'}`;
                }
                const textNode = Array.from(element.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
                if (textNode) {
                    textNode.textContent = status ? normalText : errorText;
                }
            }
        });
    }
    
    /**
     * Update history table
     * @private
     */
    updateHistoryTable() {
        const tableBody = document.getElementById('history-table-body');
        if (!tableBody) return;
        
        if (this.operationHistory.length === 0) {
            tableBody.innerHTML = '<tr class="no-data"><td colspan="5">No homing operations recorded</td></tr>';
            return;
        }
        
        const rows = this.operationHistory.map(operation => {
            const timestamp = new Date(operation.timestamp).toLocaleString();
            const duration = this.formatDuration(operation.duration || 0);
            const position = `X:${operation.finalPosition?.x?.toFixed(1) || '--'} Y:${operation.finalPosition?.y?.toFixed(1) || '--'} Z:${operation.finalPosition?.z?.toFixed(1) || '--'}`;
            const statusClass = operation.success ? 'success' : 'error';
            const statusText = operation.success ? 'Success' : 'Failed';
            
            return `
                <tr>
                    <td>${timestamp}</td>
                    <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                    <td>${duration}</td>
                    <td>${position}</td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="window.robotHomeManager?.viewOperationDetails('${operation.id}')">
                            View
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
        
        tableBody.innerHTML = rows;
    }
    
    // =========================
    // WebSocket Event Handlers
    // =========================
    
    /**
     * Handle robot status updates
     * @private
     * @param {Object} status - Robot status data
     */
    handleRobotStatusUpdate(status) {
        if (!status) return;
        
        // Update robot status
        this.robotStatus = {
            ...this.robotStatus,
            ...status
        };
        
        // Update display
        this.updateRobotStatusDisplay();
        this.updateControlButtons();
    }
    
    /**
     * Handle hardware status updates
     * @private
     * @param {Object} status - Hardware status data
     */
    handleHardwareUpdate(status) {
        if (!status) return;
        
        // Update hardware status
        if (status.power) {
            this.hardwareStatus.mainPower = status.power.connected || false;
            this.hardwareStatus.current = status.power.current || 0;
            this.hardwareStatus.consumption = status.power.consumption || 0;
        }
        
        if (status.safety) {
            this.hardwareStatus.estopStatus = !status.safety.emergencyStop;
            this.hardwareStatus.safetyCurtain = !status.safety.lightCurtain;
            this.hardwareStatus.doorLock = status.safety.doorLock || false;
            this.hardwareStatus.areaClear = status.safety.areaClear || false;
        }
        
        // Update display
        this.updateHardwareDisplay();
    }
    
    // =========================
    // Safety and Validation
    // =========================
    
    /**
     * Show safety confirmation modal
     * @private
     * @returns {Promise<boolean>} Safety confirmed
     */
    async showSafetyConfirmation() {
        return new Promise((resolve) => {
            const modal = document.getElementById('robot-safety-confirmation-modal-template');
            if (!modal) {
                resolve(true);
                return;
            }
            
            // Clone and show modal
            const modalClone = modal.cloneNode(true);
            modalClone.id = 'active-robot-safety-modal';
            modalClone.style.display = 'flex';
            document.body.appendChild(modalClone);
            
            // Handle buttons
            modalClone.addEventListener('click', (e) => {
                const action = e.target.getAttribute('data-action');
                
                if (action === 'confirm') {
                    modalClone.remove();
                    resolve(true);
                } else {
                    modalClone.remove();
                    resolve(false);
                }
            });
        });
    }
    
    /**
     * Validate robot is ready for homing
     * @private
     * @returns {boolean} Robot ready
     */
    validateRobotReady() {
        if (!this.robotStatus.connected) {
            this.showError('Robot Not Connected', 'Please check robot connection and try again.');
            return false;
        }
        
        if (!this.robotStatus.servoEnabled) {
            this.showError('Servo Not Enabled', 'Please enable robot servo before starting homing operation.');
            return false;
        }
        
        if (!this.hardwareStatus.estopStatus) {
            this.showError('Emergency Stop Active', 'Emergency stop is currently active. Please reset before proceeding.');
            return false;
        }
        
        if (!this.hardwareStatus.areaClear) {
            this.showError('Area Not Clear', 'Please ensure the robot workspace is clear of personnel and obstacles.');
            return false;
        }
        
        return true;
    }
    
    // =========================
    // Results and Export
    // =========================
    
    /**
     * Show operation result
     * @private
     */
    showOperationResult() {
        const resultSection = document.getElementById('home-result-section');
        if (!resultSection) return;
        
        const success = this.robotStatus.isHomed;
        const accuracy = this.homingData.accuracy;
        const totalTime = this.homingData.elapsedTime;
        
        // Update result display
        const resultStatus = document.getElementById('home-result-status');
        if (resultStatus) {
            const icon = resultStatus.querySelector('.result-icon');
            const title = resultStatus.querySelector('#result-title');
            const message = resultStatus.querySelector('#result-message');
            
            if (icon) icon.textContent = success ? '✅' : '❌';
            if (title) title.textContent = success ? 'Homing Successful' : 'Homing Failed';
            if (message) message.textContent = success ? 'Robot successfully moved to home position' : 'Robot failed to reach home position';
        }
        
        // Update result details
        const finalPos = document.getElementById('final-position');
        const homeAccuracy = document.getElementById('home-accuracy');
        const totalHomeTime = document.getElementById('total-home-time');
        const completionTime = document.getElementById('completion-time');
        
        if (finalPos) {
            finalPos.textContent = `X: ${this.robotStatus.position.x.toFixed(2)} Y: ${this.robotStatus.position.y.toFixed(2)} Z: ${this.robotStatus.position.z.toFixed(2)}`;
        }
        if (homeAccuracy) homeAccuracy.textContent = `±${accuracy.toFixed(3)} mm`;
        if (totalHomeTime) totalHomeTime.textContent = this.formatDuration(totalTime);
        if (completionTime) completionTime.textContent = new Date().toLocaleString();
        
        // Show result section
        resultSection.style.display = 'block';
    }
    
    /**
     * Export operation history
     * @private
     */
    exportHistory() {
        if (this.operationHistory.length === 0) {
            this.uiManager.showNotification('No history data to export', 'warning');
            return;
        }
        
        const csvData = [
            'Timestamp,Status,Duration,Final Position X,Final Position Y,Final Position Z,Accuracy'
        ];
        
        this.operationHistory.forEach(op => {
            const row = [
                new Date(op.timestamp).toISOString(),
                op.success ? 'Success' : 'Failed',
                op.duration || 0,
                op.finalPosition?.x || 0,
                op.finalPosition?.y || 0,
                op.finalPosition?.z || 0,
                op.accuracy || 0
            ].join(',');
            csvData.push(row);
        });
        
        const blob = new Blob([csvData.join('\n')], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `robot-homing-history-${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
        
        window.URL.revokeObjectURL(url);
        this.uiManager.showNotification('Operation history exported', 'success');
    }
    
    // =========================
    // Utility Methods
    // =========================
    
    /**
     * Reset progress tracking
     * @private
     */
    resetProgress() {
        this.currentStep = 0;
        this.overallProgress = 0;
        this.homingData.elapsedTime = 0;
        this.homingData.distanceToHome = 0;
        this.updateProgressDisplay();
    }
    
    /**
     * Format duration in seconds to MM:SS
     * @private
     * @param {number} seconds - Duration in seconds
     * @returns {string} Formatted duration
     */
    formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    /**
     * Add log entry
     * @param {string} level - Log level (info, warning, error, success)
     * @param {string} message - Log message
     */
    addLogEntry(level, message) {
        const logContainer = document.getElementById('robot-operation-log');
        if (!logContainer) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${level}`;
        logEntry.innerHTML = `
            <span class="log-time">${timestamp}</span>
            <span class="log-message">${message}</span>
        `;
        
        // Add to top of log
        const firstEntry = logContainer.firstChild;
        if (firstEntry) {
            logContainer.insertBefore(logEntry, firstEntry);
        } else {
            logContainer.appendChild(logEntry);
        }
        
        // Limit log entries (keep last 50)
        const entries = logContainer.querySelectorAll('.log-entry');
        if (entries.length > 50) {
            entries[entries.length - 1].remove();
        }
        
        console.log(`📝 [${level.toUpperCase()}] ${message}`);
    }
    
    /**
     * Clear operation log
     * @private
     */
    clearLog() {
        const logContainer = document.getElementById('robot-operation-log');
        if (logContainer) {
            logContainer.innerHTML = '';
            this.addLogEntry('info', 'Robot operation log cleared');
        }
    }
    
    /**
     * Export operation log
     * @private
     */
    exportLog() {
        const logContainer = document.getElementById('robot-operation-log');
        if (!logContainer) return;
        
        const entries = logContainer.querySelectorAll('.log-entry');
        const logData = Array.from(entries).map(entry => {
            const time = entry.querySelector('.log-time')?.textContent || '';
            const message = entry.querySelector('.log-message')?.textContent || '';
            const level = entry.classList[1] || 'info';
            return `${time}\t${level.toUpperCase()}\t${message}`;
        }).join('\n');
        
        const blob = new Blob([`Time\tLevel\tMessage\n${logData}`], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `robot-home-log-${new Date().toISOString().split('T')[0]}.txt`;
        link.click();
        
        window.URL.revokeObjectURL(url);
        this.uiManager.showNotification('Robot operation log exported', 'success');
    }
    
    /**
     * Show error message
     * @private
     * @param {string} title - Error title
     * @param {string} message - Error message
     */
    showError(title, message) {
        this.uiManager.showModal({
            title: `❌ ${title}`,
            message: message,
            type: 'error'
        });
        
        this.addLogEntry('error', `${title}: ${message}`);
    }
    
    /**
     * View operation details (placeholder for future implementation)
     * @param {string} operationId - Operation ID
     */
    viewOperationDetails(operationId) {
        console.log('View operation details:', operationId);
        this.uiManager.showModal({
            title: 'Operation Details',
            message: `Details for operation ${operationId} will be implemented in a future version.`,
            type: 'info'
        });
    }
    
    /**
     * Get page manager instance (for external access)
     * @returns {RobotHomePageManager} Page manager instance
     */
    static getInstance() {
        return window.robotHomeManager;
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        // Stop monitoring intervals
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
            this.statusUpdateInterval = null;
        }
        
        if (this.progressUpdateInterval) {
            clearInterval(this.progressUpdateInterval);
            this.progressUpdateInterval = null;
        }
        
        // Remove WebSocket listeners
        if (this.websocketManager) {
            this.websocketManager.off('robot-status', this.handleRobotStatusUpdate);
            this.websocketManager.off('hardware-status', this.handleHardwareUpdate);
        }
        
        console.log('🧹 Robot Home page manager cleanup complete');
    }
}

console.log('📝 Robot Home page manager module loaded successfully');