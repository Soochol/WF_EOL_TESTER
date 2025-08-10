/**
 * EOL Force Test Page Manager - WF EOL Tester Web Interface
 * 
 * This module manages the End-of-Line Force Test page including:
 * - Test execution control and monitoring
 * - Real-time data visualization and progress tracking
 * - Hardware status monitoring during tests
 * - Test configuration and parameter management
 * - Results display and export functionality
 * - Safety confirmations and emergency controls
 * - Integrated real-time log viewer for test logs
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

import { LogViewerComponent } from '../components/log-viewer.js';
import { ForceResultsVisualizer } from '../components/force-results-visualizer.js';

/**
 * EOL Force Test Page Manager Class
 * 
 * Manages the complete lifecycle of EOL Force Test operations with real-time
 * monitoring, safety controls, and comprehensive result analysis.
 */
export class EOLForceTestPageManager {
    /**
     * Initialize EOL Force Test page manager
     * @param {APIClient} apiClient - API client instance
     * @param {WebSocketManager} websocketManager - WebSocket manager instance
     * @param {UIManager} uiManager - UI manager instance
     */
    constructor(apiClient, websocketManager, uiManager) {
        console.log('🔬 Initializing EOL Force Test page manager...');
        
        // Core dependencies
        this.apiClient = apiClient;
        this.websocketManager = websocketManager;
        this.uiManager = uiManager;
        
        // Test state
        this.currentTest = null;
        this.testState = 'idle'; // idle, running, paused, completed, error
        this.testStartTime = null;
        this.testConfig = {
            temperature: 25,
            maxForce: 1000,
            strokeLength: 50,
            duration: 120,
            forceLimit: 1200,
            tempLimit: 70
        };
        
        // Real-time data
        this.testData = {
            force: [],
            position: [],
            temperature: [],
            timestamps: []
        };
        this.currentMeasurements = {
            force: 0,
            position: 0,
            temperature: 25,
            elapsedTime: 0
        };
        
        // Charts
        this.charts = new Map();
        this.updateInterval = null;
        
        // Hardware status
        this.hardwareStatus = {
            robot: false,
            loadcell: false,
            mcu: false,
            power: false
        };
        
        // Progress tracking
        this.testSteps = [
            { id: 1, name: 'Initialize', progress: 0 },
            { id: 2, name: 'Prepare', progress: 0 },
            { id: 3, name: 'Execute', progress: 0 },
            { id: 4, name: 'Analyze', progress: 0 },
            { id: 5, name: 'Complete', progress: 0 }
        ];
        this.currentStep = 0;
        this.overallProgress = 0;
        
        // Log viewer component
        this.logViewer = null;
        
        // Force results visualizer component
        this.forceResultsVisualizer = null;
        this.resultsVisualizerEnabled = false;
        
        // Bind methods
        this.handleStartTest = this.handleStartTest.bind(this);
        this.handlePauseTest = this.handlePauseTest.bind(this);
        this.handleResumeTest = this.handleResumeTest.bind(this);
        this.handleStopTest = this.handleStopTest.bind(this);
        this.handleEmergencyStop = this.handleEmergencyStop.bind(this);
        this.handleTestData = this.handleTestData.bind(this);
        this.handleHardwareUpdate = this.handleHardwareUpdate.bind(this);
        this.handleExpandLogViewer = this.handleExpandLogViewer.bind(this);
        this.handleToggleResultsView = this.handleToggleResultsView.bind(this);
        this.handleComprehensiveExport = this.handleComprehensiveExport.bind(this);
        this.handleResultsFullscreen = this.handleResultsFullscreen.bind(this);
        
        // Initialize page
        this.init();
        
        console.log('✅ EOL Force Test page manager initialized');
    }
    
    /**
     * Initialize page manager
     * @private
     */
    init() {
        try {
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize charts
            this.initializeCharts();
            
            // Setup WebSocket subscriptions
            this.setupWebSocketSubscriptions();
            
            // Initialize log viewer
            this.initializeLogViewer();
            
            // Initialize force results visualizer
            this.initializeForceResultsVisualizer();
            
            // Load initial data
            this.loadInitialData();
            
            // Start hardware monitoring
            this.startHardwareMonitoring();
            
            console.log('✅ EOL Force Test page initialization complete');
            
        } catch (error) {
            console.error('❌ EOL Force Test page initialization failed:', error);
            this.showError('Failed to initialize EOL Force Test page', error);
        }
    }
    
    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Test control buttons
        const startBtn = document.getElementById('start-test-btn');
        const pauseBtn = document.getElementById('pause-test-btn');
        const resumeBtn = document.getElementById('resume-test-btn');
        const stopBtn = document.getElementById('stop-test-btn');
        const emergencyBtn = document.getElementById('emergency-stop-test');
        
        if (startBtn) startBtn.addEventListener('click', this.handleStartTest);
        if (pauseBtn) pauseBtn.addEventListener('click', this.handlePauseTest);
        if (resumeBtn) resumeBtn.addEventListener('click', this.handleResumeTest);
        if (stopBtn) stopBtn.addEventListener('click', this.handleStopTest);
        if (emergencyBtn) emergencyBtn.addEventListener('click', this.handleEmergencyStop);
        
        // Export and report buttons
        const exportBtn = document.getElementById('export-results-btn');
        const reportBtn = document.getElementById('view-report-btn');
        
        if (exportBtn) exportBtn.addEventListener('click', this.exportResults.bind(this));
        if (reportBtn) reportBtn.addEventListener('click', this.viewReport.bind(this));
        
        // Log controls
        const expandLogBtn = document.getElementById('expand-log-viewer-btn');
        
        if (expandLogBtn) expandLogBtn.addEventListener('click', this.handleExpandLogViewer);
        
        // Results visualization controls
        const toggleResultsBtn = document.getElementById('toggle-results-view-btn');
        const comprehensiveExportBtn = document.getElementById('comprehensive-export-btn');
        const resultsFullscreenBtn = document.getElementById('results-fullscreen-btn');
        
        if (toggleResultsBtn) toggleResultsBtn.addEventListener('click', this.handleToggleResultsView);
        if (comprehensiveExportBtn) comprehensiveExportBtn.addEventListener('click', this.handleComprehensiveExport);
        if (resultsFullscreenBtn) resultsFullscreenBtn.addEventListener('click', this.handleResultsFullscreen);
        
        console.log('✅ Event listeners setup complete');
    }
    
    /**
     * Initialize charts for real-time data
     * @private
     */
    initializeCharts() {
        try {
            // Check if Chart.js is available
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not available, skipping chart initialization');
                return;
            }
            
            // Initialize mini charts for real-time display
            this.initializeMiniCharts();
            
            // Initialize result charts
            this.initializeResultCharts();
            
            console.log('✅ Charts initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize charts:', error);
        }
    }
    
    /**
     * Initialize mini charts for real-time monitoring
     * @private
     */
    initializeMiniCharts() {
        const chartConfig = {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                elements: { point: { radius: 0 } }
            }
        };
        
        // Force chart
        const forceCanvas = document.getElementById('force-chart');
        if (forceCanvas) {
            this.charts.set('force', new Chart(forceCanvas, {
                ...chartConfig,
                data: {
                    ...chartConfig.data,
                    datasets: [{
                        ...chartConfig.data.datasets[0],
                        borderColor: '#28a745'
                    }]
                }
            }));
        }
        
        // Position chart
        const positionCanvas = document.getElementById('position-chart');
        if (positionCanvas) {
            this.charts.set('position', new Chart(positionCanvas, {
                ...chartConfig,
                data: {
                    ...chartConfig.data,
                    datasets: [{
                        ...chartConfig.data.datasets[0],
                        borderColor: '#ffc107'
                    }]
                }
            }));
        }
        
        // Temperature chart
        const tempCanvas = document.getElementById('temp-chart');
        if (tempCanvas) {
            this.charts.set('temperature', new Chart(tempCanvas, {
                ...chartConfig,
                data: {
                    ...chartConfig.data,
                    datasets: [{
                        ...chartConfig.data.datasets[0],
                        borderColor: '#dc3545'
                    }]
                }
            }));
        }
    }
    
    /**
     * Initialize result charts
     * @private
     */
    initializeResultCharts() {
        // Force vs Time chart
        const forceTimeCanvas = document.getElementById('force-time-chart');
        if (forceTimeCanvas) {
            this.charts.set('forceTime', new Chart(forceTimeCanvas, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Force (N)',
                        data: [],
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        borderWidth: 2,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: 'Time (s)' } },
                        y: { title: { display: true, text: 'Force (N)' } }
                    }
                }
            }));
        }
        
        // Position vs Time chart
        const positionTimeCanvas = document.getElementById('position-time-chart');
        if (positionTimeCanvas) {
            this.charts.set('positionTime', new Chart(positionTimeCanvas, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Position (mm)',
                        data: [],
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        borderWidth: 2,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: 'Time (s)' } },
                        y: { title: { display: true, text: 'Position (mm)' } }
                    }
                }
            }));
        }
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
            // Subscribe to test data updates
            this.websocketManager.on('test-data', this.handleTestData);
            
            // Subscribe to hardware status updates
            this.websocketManager.on('hardware-status', this.handleHardwareUpdate);
            
            // Subscribe to test status updates
            this.websocketManager.on('test-status', this.handleTestStatusUpdate.bind(this));
            
            console.log('✅ WebSocket subscriptions setup');
            
        } catch (error) {
            console.error('❌ Failed to setup WebSocket subscriptions:', error);
        }
    }
    
    /**
     * Initialize force results visualizer component
     * @private
     */
    initializeForceResultsVisualizer() {
        try {
            const resultsVisualizerContainer = document.getElementById('force-results-visualizer-container');
            if (!resultsVisualizerContainer) {
                console.warn('Force Results Visualizer container not found');
                return;
            }
            
            // Configure results visualizer options
            const options = {
                enableRealTimeUpdates: true,
                enableDataComparison: true,
                enableExport: true,
                enableAnalysis: true,
                defaultView: 'table',
                refreshInterval: 2000, // 2 seconds
                maxHistoryEntries: 50
            };
            
            // Initialize force results visualizer component
            this.forceResultsVisualizer = new ForceResultsVisualizer(
                resultsVisualizerContainer,
                options
            );
            
            // Listen to visualizer events
            resultsVisualizerContainer.addEventListener('refreshRequested', () => {
                this.refreshTestResults();
            });
            
            resultsVisualizerContainer.addEventListener('messageRequested', (e) => {
                this.handleVisualizerMessage(e.detail);
            });
            
            console.log('✅ Force Results Visualizer initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize Force Results Visualizer:', error);
        }
    }
    
    /**
     * Initialize log viewer component
     * @private
     */
    initializeLogViewer() {
        try {
            const logViewerContainer = document.getElementById('eol-test-log-viewer');
            if (!logViewerContainer) {
                console.warn('Log viewer container not found');
                return;
            }
            
            // Configure log viewer for EOL test context
            const config = {
                maxMessages: 5000,
                batchSize: 20,
                updateInterval: 100,
                autoScroll: true,
                showTimestamps: true,
                showSources: true,
                showIcons: true,
                enableVirtualScrolling: false, // Disable for embedded view
                saveToLocalStorage: true,
                storageKey: 'wf-eol-test-logs'
            };
            
            // Initialize log viewer component
            this.logViewer = new LogViewerComponent(
                logViewerContainer,
                this.websocketManager,
                config
            );
            
            // Set initial filters for test logs
            if (this.logViewer.setFilters) {
                this.logViewer.setFilters({
                    source: 'TEST', // Focus on test-related logs
                    level: 'ALL'
                });
            }
            
            // Add some initial test messages
            if (this.logViewer.addSystemMessage) {
                this.logViewer.addSystemMessage('EOL Force Test page loaded', 'INFO');
                this.logViewer.addSystemMessage('Log viewer initialized', 'INFO');
            }
            
            console.log('✅ Log viewer initialized for EOL test page');
            
        } catch (error) {
            console.error('❌ Failed to initialize log viewer:', error);
        }
    }
    
    /**
     * Load initial data
     * @private
     */
    async loadInitialData() {
        try {
            // Load test configuration
            await this.loadTestConfiguration();
            
            // Load hardware status
            await this.loadHardwareStatus();
            
            // Update display
            this.updateParameterDisplay();
            this.updateHardwareDisplay();
            
            console.log('✅ Initial data loaded');
            
        } catch (error) {
            console.error('❌ Failed to load initial data:', error);
        }
    }
    
    /**
     * Start hardware monitoring
     * @private
     */
    startHardwareMonitoring() {
        // Monitor hardware status every 2 seconds
        setInterval(async () => {
            try {
                await this.loadHardwareStatus();
            } catch (error) {
                console.warn('Hardware status update failed:', error);
            }
        }, 2000);
    }
    
    // =========================
    // Test Control Methods
    // =========================
    
    /**
     * Handle start test button click
     * @private
     */
    async handleStartTest() {
        try {
            console.log('🔬 Starting EOL Force Test...');
            
            // Show safety confirmation
            const confirmed = await this.showSafetyConfirmation();
            if (!confirmed) {
                this.addLogEntry('info', 'Test start cancelled by user');
                return;
            }
            
            // Validate hardware status
            if (!this.validateHardwareReady()) {
                this.showError('Hardware not ready', 'Please check hardware connections');
                return;
            }
            
            // Show configuration modal
            const configConfirmed = await this.showTestConfiguration();
            if (!configConfirmed) {
                this.addLogEntry('info', 'Test configuration cancelled');
                return;
            }
            
            // Start test
            await this.startTest();
            
        } catch (error) {
            console.error('❌ Failed to start test:', error);
            this.showError('Test Start Failed', error.message);
        }
    }
    
    /**
     * Start the actual test
     * @private
     */
    async startTest() {
        try {
            // Update UI state
            this.setTestState('running');
            this.showProgressSection();
            this.updateControlButtons();
            
            // Record test start time
            this.testStartTime = new Date().toISOString();
            
            // Reset data and progress
            this.resetTestData();
            this.resetProgress();
            
            // Send start command to API
            const response = await this.apiClient.post('/tests', {
                config: this.testConfig,
                type: 'eol-force-test'
            });
            
            this.currentTest = response.data;
            this.addLogEntry('success', `Test started successfully (ID: ${this.currentTest.id})`);
            
            // Start real-time updates
            this.startRealTimeUpdates();
            
        } catch (error) {
            this.setTestState('error');
            throw error;
        }
    }
    
    /**
     * Handle pause test
     * @private
     */
    async handlePauseTest() {
        try {
            console.log('⏸️ Pausing test...');
            
            if (!this.currentTest) return;
            
            await this.apiClient.put(`/tests/${this.currentTest.id}`, { action: 'pause' });
            this.setTestState('paused');
            this.updateControlButtons();
            this.addLogEntry('warning', 'Test paused');
            
        } catch (error) {
            console.error('❌ Failed to pause test:', error);
            this.showError('Pause Failed', error.message);
        }
    }
    
    /**
     * Handle resume test
     * @private
     */
    async handleResumeTest() {
        try {
            console.log('⏯️ Resuming test...');
            
            if (!this.currentTest) return;
            
            await this.apiClient.put(`/tests/${this.currentTest.id}`, { action: 'resume' });
            this.setTestState('running');
            this.updateControlButtons();
            this.addLogEntry('info', 'Test resumed');
            
        } catch (error) {
            console.error('❌ Failed to resume test:', error);
            this.showError('Resume Failed', error.message);
        }
    }
    
    /**
     * Handle stop test
     * @private
     */
    async handleStopTest() {
        try {
            console.log('⏹️ Stopping test...');
            
            const confirmed = await this.uiManager.showModal({
                title: 'Stop Test',
                message: 'Are you sure you want to stop the current test? This action cannot be undone.',
                type: 'warning',
                buttons: [
                    { text: 'Cancel', action: 'cancel', variant: 'secondary' },
                    { text: 'Stop Test', action: 'confirm', variant: 'danger' }
                ]
            });
            
            if (confirmed.action !== 'confirm') return;
            
            if (this.currentTest) {
                await this.apiClient.put(`/tests/${this.currentTest.id}`, { action: 'stop' });
            }
            
            this.stopTest();
            this.addLogEntry('warning', 'Test stopped by user');
            
        } catch (error) {
            console.error('❌ Failed to stop test:', error);
            this.showError('Stop Failed', error.message);
        }
    }
    
    /**
     * Handle emergency stop
     * @private
     */
    async handleEmergencyStop() {
        try {
            console.log('🚨 Emergency stop activated!');
            
            // Immediate API call
            await this.apiClient.post('/hardware/emergency-stop');
            
            // Stop test
            this.stopTest(true);
            
            // Show emergency modal
            this.uiManager.showModal({
                title: '🛑 Emergency Stop',
                message: 'Emergency stop has been activated. All test operations have been halted.',
                type: 'error'
            });
            
            this.addLogEntry('error', 'EMERGENCY STOP ACTIVATED');
            
        } catch (error) {
            console.error('❌ Emergency stop failed:', error);
            this.showError('Emergency Stop Failed', error.message);
        }
    }
    
    /**
     * Stop test (internal)
     * @private
     * @param {boolean} emergency - Whether this is an emergency stop
     */
    stopTest(emergency = false) {
        // Stop real-time updates
        this.stopRealTimeUpdates();
        
        // Update state
        this.setTestState(emergency ? 'emergency' : 'completed');
        this.updateControlButtons();
        
        // Show results if not emergency
        if (!emergency && this.currentTest) {
            this.showTestResults();
        }
        
        // Update results visualizer if enabled
        if (!emergency && this.forceResultsVisualizer) {
            this.updateResultsVisualizer();
        }
        
        // Clear current test
        this.currentTest = null;
    }
    
    // =========================
    // Real-time Data Methods
    // =========================
    
    /**
     * Start real-time updates
     * @private
     */
    startRealTimeUpdates() {
        // Update every 100ms for smooth visualization
        this.updateInterval = setInterval(() => {
            this.updateRealTimeDisplay();
            this.updateProgress();
        }, 100);
    }
    
    /**
     * Stop real-time updates
     * @private
     */
    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    /**
     * Handle incoming test data
     * @private
     * @param {Object} data - Test data
     */
    handleTestData(data) {
        if (!data || this.testState !== 'running') return;
        
        // Update current measurements
        this.currentMeasurements = {
            force: data.force || 0,
            position: data.position || 0,
            temperature: data.temperature || 25,
            elapsedTime: data.elapsedTime || 0
        };
        
        // Add to historical data
        const timestamp = Date.now();
        this.testData.timestamps.push(timestamp);
        this.testData.force.push(data.force || 0);
        this.testData.position.push(data.position || 0);
        this.testData.temperature.push(data.temperature || 25);
        
        // Limit data points (keep last 500 points)
        const maxPoints = 500;
        if (this.testData.timestamps.length > maxPoints) {
            this.testData.timestamps = this.testData.timestamps.slice(-maxPoints);
            this.testData.force = this.testData.force.slice(-maxPoints);
            this.testData.position = this.testData.position.slice(-maxPoints);
            this.testData.temperature = this.testData.temperature.slice(-maxPoints);
        }
        
        // Update charts
        this.updateMiniCharts();
    }
    
    /**
     * Handle test status updates
     * @private
     * @param {Object} status - Test status
     */
    handleTestStatusUpdate(status) {
        if (!status) return;
        
        // Update test state
        if (status.state && status.state !== this.testState) {
            this.setTestState(status.state);
            this.updateControlButtons();
        }
        
        // Update progress
        if (status.progress) {
            this.currentStep = status.progress.currentStep || 0;
            this.overallProgress = status.progress.percentage || 0;
            this.updateProgressDisplay();
        }
        
        // Handle test completion
        if (status.completed) {
            this.handleTestCompletion(status);
        }
        
        this.addLogEntry('info', `Test status: ${status.message || status.state}`);
    }
    
    /**
     * Handle test completion
     * @private
     * @param {Object} status - Completion status
     */
    handleTestCompletion(status) {
        console.log('✅ Test completed:', status);
        
        this.stopTest();
        
        // Show completion notification
        const success = status.result === 'pass';
        this.uiManager.showNotification(
            `Test ${success ? 'passed' : 'failed'}: ${status.message}`,
            success ? 'success' : 'error'
        );
        
        this.addLogEntry(success ? 'success' : 'error', 
                        `Test completed: ${status.result} - ${status.message}`);
    }
    
    // =========================
    // UI Update Methods
    // =========================
    
    /**
     * Set test state
     * @private
     * @param {string} state - New test state
     */
    setTestState(state) {
        this.testState = state;
        
        // Update status badge
        const statusBadge = document.getElementById('eol-test-status');
        if (statusBadge) {
            const indicator = statusBadge.querySelector('.status-indicator');
            const text = statusBadge.querySelector('.status-text');
            
            if (indicator && text) {
                indicator.className = `status-indicator ${this.getStatusClass(state)}`;
                text.textContent = this.getStatusText(state);
            }
        }
        
        console.log(`📊 Test state changed to: ${state}`);
    }
    
    /**
     * Get status CSS class for state
     * @private
     * @param {string} state - Test state
     * @returns {string} CSS class
     */
    getStatusClass(state) {
        const classes = {
            idle: 'ready',
            running: 'active',
            paused: 'warning',
            completed: 'success',
            error: 'error',
            emergency: 'error'
        };
        return classes[state] || 'unknown';
    }
    
    /**
     * Get status text for state
     * @private
     * @param {string} state - Test state
     * @returns {string} Status text
     */
    getStatusText(state) {
        const texts = {
            idle: 'Ready',
            running: 'Running',
            paused: 'Paused',
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
        const startBtn = document.getElementById('start-test-btn');
        const pauseBtn = document.getElementById('pause-test-btn');
        const resumeBtn = document.getElementById('resume-test-btn');
        const stopBtn = document.getElementById('stop-test-btn');
        
        if (!startBtn || !pauseBtn || !resumeBtn || !stopBtn) return;
        
        const isRunning = this.testState === 'running';
        const isPaused = this.testState === 'paused';
        const isIdle = this.testState === 'idle' || this.testState === 'completed' || this.testState === 'error';
        
        startBtn.disabled = !isIdle;
        pauseBtn.disabled = !isRunning;
        resumeBtn.disabled = !isPaused;
        stopBtn.disabled = isIdle;
    }
    
    /**
     * Show progress section
     * @private
     */
    showProgressSection() {
        const progressSection = document.getElementById('test-progress-section');
        if (progressSection) {
            progressSection.style.display = 'block';
        }
    }
    
    /**
     * Update real-time display
     * @private
     */
    updateRealTimeDisplay() {
        // Update measurement displays
        const forceEl = document.getElementById('current-force');
        const positionEl = document.getElementById('current-position');
        const tempEl = document.getElementById('current-temp');
        const timeEl = document.getElementById('elapsed-time');
        
        if (forceEl) forceEl.textContent = `${this.currentMeasurements.force.toFixed(1)} N`;
        if (positionEl) positionEl.textContent = `${this.currentMeasurements.position.toFixed(2)} mm`;
        if (tempEl) tempEl.textContent = `${this.currentMeasurements.temperature.toFixed(1)} °C`;
        if (timeEl) {
            const minutes = Math.floor(this.currentMeasurements.elapsedTime / 60);
            const seconds = (this.currentMeasurements.elapsedTime % 60).toFixed(0);
            timeEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Update time remaining
        const remainingEl = document.getElementById('time-remaining');
        if (remainingEl) {
            const remaining = Math.max(0, this.testConfig.duration - this.currentMeasurements.elapsedTime);
            const minutes = Math.floor(remaining / 60);
            const seconds = Math.floor(remaining % 60);
            remainingEl.textContent = `Remaining: ${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }
    
    /**
     * Update progress display
     * @private
     */
    updateProgressDisplay() {
        // Update progress bar
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            progressFill.style.width = `${this.overallProgress}%`;
        }
        
        // Update progress percentage
        const progressPercentage = document.getElementById('progress-percentage');
        if (progressPercentage) {
            progressPercentage.textContent = `${Math.round(this.overallProgress)}%`;
        }
        
        // Update current step
        const currentStepEl = document.getElementById('current-step');
        if (currentStepEl && this.testSteps[this.currentStep]) {
            currentStepEl.textContent = this.testSteps[this.currentStep].name;
        }
        
        // Update step indicators
        document.querySelectorAll('.step').forEach((stepEl, index) => {
            const stepNum = index + 1;
            stepEl.classList.toggle('active', stepNum === this.currentStep + 1);
            stepEl.classList.toggle('completed', stepNum < this.currentStep + 1);
        });
    }
    
    /**
     * Update mini charts
     * @private
     */
    updateMiniCharts() {
        const maxPoints = 50; // Show last 50 points in mini charts
        const recentTimestamps = this.testData.timestamps.slice(-maxPoints);
        
        // Update force chart
        const forceChart = this.charts.get('force');
        if (forceChart) {
            forceChart.data.labels = recentTimestamps.map((_, i) => i);
            forceChart.data.datasets[0].data = this.testData.force.slice(-maxPoints);
            forceChart.update('none');
        }
        
        // Update position chart
        const positionChart = this.charts.get('position');
        if (positionChart) {
            positionChart.data.labels = recentTimestamps.map((_, i) => i);
            positionChart.data.datasets[0].data = this.testData.position.slice(-maxPoints);
            positionChart.update('none');
        }
        
        // Update temperature chart
        const tempChart = this.charts.get('temperature');
        if (tempChart) {
            tempChart.data.labels = recentTimestamps.map((_, i) => i);
            tempChart.data.datasets[0].data = this.testData.temperature.slice(-maxPoints);
            tempChart.update('none');
        }
    }
    
    // =========================
    // Configuration Methods
    // =========================
    
    /**
     * Show test configuration modal
     * @private
     * @returns {Promise<boolean>} Configuration confirmed
     */
    async showTestConfiguration() {
        return new Promise((resolve) => {
            const modal = document.getElementById('test-config-modal-template');
            if (!modal) {
                resolve(true);
                return;
            }
            
            // Clone and show modal
            const modalClone = modal.cloneNode(true);
            modalClone.id = 'active-test-config-modal';
            modalClone.style.display = 'flex';
            
            // Populate current values
            const form = modalClone.querySelector('#test-config-form');
            if (form) {
                Object.keys(this.testConfig).forEach(key => {
                    const input = form.querySelector(`[name="${key}"], #config-${key}`);
                    if (input) {
                        input.value = this.testConfig[key];
                    }
                });
            }
            
            // Add to DOM
            document.body.appendChild(modalClone);
            
            // Handle buttons
            modalClone.addEventListener('click', (e) => {
                const action = e.target.getAttribute('data-action');
                
                if (action === 'save') {
                    // Save configuration
                    if (form) {
                        const formData = new FormData(form);
                        Object.keys(this.testConfig).forEach(key => {
                            const value = formData.get(key) || form.querySelector(`#config-${key}`)?.value;
                            if (value) {
                                this.testConfig[key] = parseFloat(value) || value;
                            }
                        });
                    }
                    
                    this.updateParameterDisplay();
                    modalClone.remove();
                    resolve(true);
                } else if (action === 'cancel' || action === 'close') {
                    modalClone.remove();
                    resolve(false);
                }
            });
        });
    }
    
    /**
     * Update parameter display
     * @private
     */
    updateParameterDisplay() {
        const tempEl = document.getElementById('test-temp');
        const forceEl = document.getElementById('test-force');
        const strokeEl = document.getElementById('test-stroke');
        const durationEl = document.getElementById('test-duration');
        
        if (tempEl) tempEl.textContent = `${this.testConfig.temperature}°C`;
        if (forceEl) forceEl.textContent = `${this.testConfig.maxForce}N`;
        if (strokeEl) strokeEl.textContent = `${this.testConfig.strokeLength}mm`;
        if (durationEl) durationEl.textContent = `${this.testConfig.duration}s`;
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
            const modal = document.getElementById('safety-confirmation-modal-template');
            if (!modal) {
                resolve(true);
                return;
            }
            
            // Clone and show modal
            const modalClone = modal.cloneNode(true);
            modalClone.id = 'active-safety-modal';
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
     * Validate hardware is ready
     * @private
     * @returns {boolean} Hardware ready
     */
    validateHardwareReady() {
        const requiredHardware = ['robot', 'loadcell', 'mcu', 'power'];
        const missing = requiredHardware.filter(hw => !this.hardwareStatus[hw]);
        
        if (missing.length > 0) {
            this.addLogEntry('error', `Hardware not ready: ${missing.join(', ')}`);
            return false;
        }
        
        return true;
    }
    
    // =========================
    // Data Management Methods
    // =========================
    
    /**
     * Load test configuration
     * @private
     */
    async loadTestConfiguration() {
        try {
            const response = await this.apiClient.get('/tests/configuration');
            if (response.data) {
                this.testConfig = { ...this.testConfig, ...response.data };
            }
        } catch (error) {
            console.warn('Failed to load test configuration:', error);
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
                    robot: response.data.robot?.connected || false,
                    loadcell: response.data.loadcell?.connected || false,
                    mcu: response.data.mcu?.connected || false,
                    power: response.data.power?.connected || false
                };
                this.updateHardwareDisplay();
            }
        } catch (error) {
            console.warn('Failed to load hardware status:', error);
        }
    }
    
    /**
     * Handle hardware status updates
     * @private
     * @param {Object} status - Hardware status
     */
    handleHardwareUpdate(status) {
        if (!status) return;
        
        // Update local status
        Object.keys(this.hardwareStatus).forEach(key => {
            if (status[key] !== undefined) {
                this.hardwareStatus[key] = status[key].connected || false;
            }
        });
        
        // Update display
        this.updateHardwareDisplay();
    }
    
    /**
     * Update hardware display
     * @private
     */
    updateHardwareDisplay() {
        const components = ['robot', 'loadcell', 'mcu', 'power'];
        
        components.forEach(component => {
            const statusEl = document.getElementById(`${component}-status-test`);
            if (statusEl) {
                const indicator = statusEl.querySelector('.status-indicator');
                const text = statusEl.querySelector('.status-text');
                
                if (indicator && text) {
                    const connected = this.hardwareStatus[component];
                    indicator.className = `status-indicator ${connected ? 'connected' : 'disconnected'}`;
                    text.textContent = connected ? 'Connected' : 'Disconnected';
                }
            }
        });
    }
    
    /**
     * Reset test data
     * @private
     */
    resetTestData() {
        this.testData = {
            force: [],
            position: [],
            temperature: [],
            timestamps: []
        };
        
        this.currentMeasurements = {
            force: 0,
            position: 0,
            temperature: 25,
            elapsedTime: 0
        };
    }
    
    /**
     * Reset progress
     * @private
     */
    resetProgress() {
        this.currentStep = 0;
        this.overallProgress = 0;
        this.updateProgressDisplay();
    }
    
    // =========================
    // Results and Export Methods
    // =========================
    
    /**
     * Show test results
     * @private
     */
    async showTestResults() {
        try {
            if (!this.currentTest) return;
            
            // Load test results
            const response = await this.apiClient.get(`/tests/${this.currentTest.id}/results`);
            const results = response.data;
            
            // Update result display
            this.updateResultsDisplay(results);
            
            // Show results section
            const resultsSection = document.getElementById('test-results-section');
            if (resultsSection) {
                resultsSection.style.display = 'block';
            }
            
            // Update result charts
            this.updateResultCharts(results);
            
        } catch (error) {
            console.error('❌ Failed to load test results:', error);
        }
    }
    
    /**
     * Update results display
     * @private
     * @param {Object} results - Test results
     */
    updateResultsDisplay(results) {
        if (!results) return;
        
        // Update result status
        const statusEl = document.getElementById('test-result-status');
        if (statusEl) {
            const indicator = statusEl.querySelector('.result-indicator');
            const text = statusEl.querySelector('.result-text');
            
            if (indicator && text) {
                const passed = results.result === 'pass';
                indicator.className = `result-indicator ${passed ? 'pass' : 'fail'}`;
                text.textContent = passed ? 'PASS' : 'FAIL';
            }
        }
        
        // Update result values
        const peakForceEl = document.getElementById('peak-force');
        const maxDisplacementEl = document.getElementById('max-displacement');
        const actualDurationEl = document.getElementById('actual-duration');
        
        if (peakForceEl) peakForceEl.textContent = `${results.peakForce || '--'} N`;
        if (maxDisplacementEl) maxDisplacementEl.textContent = `${results.maxDisplacement || '--'} mm`;
        if (actualDurationEl) {
            const duration = results.duration || 0;
            const minutes = Math.floor(duration / 60);
            const seconds = Math.floor(duration % 60);
            actualDurationEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }
    
    /**
     * Update result charts
     * @private
     * @param {Object} results - Test results
     */
    updateResultCharts(results) {
        if (!results.data) return;
        
        const timeLabels = results.data.timestamps.map(t => (t / 1000).toFixed(1));
        
        // Update force-time chart
        const forceChart = this.charts.get('forceTime');
        if (forceChart) {
            forceChart.data.labels = timeLabels;
            forceChart.data.datasets[0].data = results.data.force;
            forceChart.update();
        }
        
        // Update position-time chart
        const positionChart = this.charts.get('positionTime');
        if (positionChart) {
            positionChart.data.labels = timeLabels;
            positionChart.data.datasets[0].data = results.data.position;
            positionChart.update();
        }
    }
    
    /**
     * Export test results
     * @private
     */
    async exportResults() {
        try {
            if (!this.currentTest) {
                this.showError('No Test Results', 'No test results available to export');
                return;
            }
            
            console.log('💾 Exporting test results...');
            
            const response = await this.apiClient.get(`/tests/${this.currentTest.id}/export`, {
                format: 'csv',
                responseType: 'blob'
            });
            
            // Create download link
            const blob = new Blob([response.data], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `eol-test-${this.currentTest.id}-results.csv`;
            link.click();
            
            window.URL.revokeObjectURL(url);
            
            this.uiManager.showNotification('Test results exported successfully', 'success');
            this.addLogEntry('success', 'Test results exported');
            
        } catch (error) {
            console.error('❌ Failed to export results:', error);
            this.showError('Export Failed', error.message);
        }
    }
    
    /**
     * View detailed report
     * @private
     */
    async viewReport() {
        if (!this.currentTest) return;
        
        try {
            // Open report in new window
            const reportUrl = `/reports/test/${this.currentTest.id}`;
            window.open(reportUrl, '_blank');
            
            this.addLogEntry('info', 'Detailed report opened');
            
        } catch (error) {
            console.error('❌ Failed to view report:', error);
            this.showError('Report Failed', error.message);
        }
    }
    
    // =========================
    // Force Results Visualizer Integration Methods
    // =========================
    
    /**
     * Handle toggle results view button click
     * @private
     */
    handleToggleResultsView() {
        try {
            // Toggle the comprehensive results section
            const comprehensiveSection = document.getElementById('comprehensive-results-section');
            if (comprehensiveSection) {
                const isVisible = comprehensiveSection.style.display !== 'none';
                comprehensiveSection.style.display = isVisible ? 'none' : 'block';
                
                // Update button text
                const button = document.getElementById('toggle-results-view-btn');
                if (button) {
                    button.innerHTML = isVisible ? '📈 Show Results' : '📊 Hide Results';
                    button.title = isVisible ? 'Show Results View' : 'Hide Results View';
                }
                
                this.addLogEntry('info', `Results visualization ${isVisible ? 'hidden' : 'shown'}`);
            }
            
        } catch (error) {
            console.error('❌ Failed to toggle results view:', error);
            this.showError('Toggle Failed', error.message);
        }
    }
    
    /**
     * Handle comprehensive export button click
     * @private
     */
    async handleComprehensiveExport() {
        try {
            console.log('💾 Exporting comprehensive results...');
            
            if (this.forceResultsVisualizer && typeof this.forceResultsVisualizer.exportAllData === 'function') {
                // Use the visualizer's export functionality
                await this.forceResultsVisualizer.exportAllData();
                this.addLogEntry('success', 'Comprehensive results exported successfully');
            } else {
                // Fallback to regular export
                await this.exportResults();
            }
            
        } catch (error) {
            console.error('❌ Failed to export comprehensive results:', error);
            this.showError('Comprehensive Export Failed', error.message);
        }
    }
    
    /**
     * Handle results fullscreen button click
     * @private
     */
    handleResultsFullscreen() {
        try {
            const comprehensiveSection = document.getElementById('comprehensive-results-section');
            if (!comprehensiveSection) return;
            
            // Toggle fullscreen class
            const isFullscreen = comprehensiveSection.classList.contains('fullscreen');
            
            if (isFullscreen) {
                // Exit fullscreen
                comprehensiveSection.classList.remove('fullscreen');
                document.body.classList.remove('fullscreen-active');
                
                // Update button
                const button = document.getElementById('results-fullscreen-btn');
                if (button) {
                    button.innerHTML = '🔍 Fullscreen';
                    button.title = 'Fullscreen Results';
                }
                
                this.addLogEntry('info', 'Exited fullscreen results view');
            } else {
                // Enter fullscreen
                comprehensiveSection.classList.add('fullscreen');
                document.body.classList.add('fullscreen-active');
                
                // Update button
                const button = document.getElementById('results-fullscreen-btn');
                if (button) {
                    button.innerHTML = '🔍 Exit Fullscreen';
                    button.title = 'Exit Fullscreen';
                }
                
                // Show comprehensive section if hidden
                comprehensiveSection.style.display = 'block';
                
                this.addLogEntry('info', 'Entered fullscreen results view');
            }
            
        } catch (error) {
            console.error('❌ Failed to toggle fullscreen:', error);
            this.showError('Fullscreen Failed', error.message);
        }
    }
    
    /**
     * Update results visualizer with current test data
     * @private
     */
    updateResultsVisualizer() {
        try {
            if (!this.forceResultsVisualizer) return;
            
            // Prepare comprehensive test data
            const visualizerData = {
                testId: this.currentTest?.id,
                timestamp: new Date().toISOString(),
                configuration: this.testConfig,
                measurements: {
                    force: this.testData.force,
                    position: this.testData.position,
                    temperature: this.testData.temperature,
                    timestamps: this.testData.timestamps
                },
                statistics: this.calculateTestStatistics(),
                metadata: {
                    testState: this.testState,
                    startTime: this.testStartTime,
                    endTime: new Date().toISOString(),
                    duration: this.currentMeasurements.elapsedTime
                }
            };
            
            // Update visualizer with data
            if (typeof this.forceResultsVisualizer.updateData === 'function') {
                this.forceResultsVisualizer.updateData(visualizerData);
            }
            
            // Show comprehensive results section
            const comprehensiveSection = document.getElementById('comprehensive-results-section');
            if (comprehensiveSection) {
                comprehensiveSection.style.display = 'block';
            }
            
            this.addLogEntry('info', 'Results visualizer updated with test data');
            
        } catch (error) {
            console.error('❌ Failed to update results visualizer:', error);
        }
    }
    
    /**
     * Calculate test statistics for visualizer
     * @private
     * @returns {Object} Test statistics
     */
    calculateTestStatistics() {
        try {
            const forceData = this.testData.force || [];
            const positionData = this.testData.position || [];
            const tempData = this.testData.temperature || [];
            
            if (forceData.length === 0) return null;
            
            // Force statistics
            const forceStats = {
                min: Math.min(...forceData),
                max: Math.max(...forceData),
                mean: forceData.reduce((sum, val) => sum + val, 0) / forceData.length,
                std: this.calculateStandardDeviation(forceData)
            };
            
            // Position statistics
            const positionStats = {
                min: Math.min(...positionData),
                max: Math.max(...positionData),
                mean: positionData.reduce((sum, val) => sum + val, 0) / positionData.length,
                std: this.calculateStandardDeviation(positionData)
            };
            
            // Temperature statistics
            const tempStats = {
                min: Math.min(...tempData),
                max: Math.max(...tempData),
                mean: tempData.reduce((sum, val) => sum + val, 0) / tempData.length,
                std: this.calculateStandardDeviation(tempData)
            };
            
            return {
                force: forceStats,
                position: positionStats,
                temperature: tempStats,
                dataPoints: forceData.length,
                testDuration: this.currentMeasurements.elapsedTime
            };
            
        } catch (error) {
            console.error('Failed to calculate test statistics:', error);
            return null;
        }
    }
    
    /**
     * Calculate standard deviation
     * @private
     * @param {number[]} data - Data array
     * @returns {number} Standard deviation
     */
    calculateStandardDeviation(data) {
        if (!data || data.length === 0) return 0;
        
        const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
        const squaredDiffs = data.map(val => Math.pow(val - mean, 2));
        const avgSquaredDiff = squaredDiffs.reduce((sum, val) => sum + val, 0) / data.length;
        
        return Math.sqrt(avgSquaredDiff);
    }
    
    /**
     * Refresh test results for visualizer
     * @private
     */
    async refreshTestResults() {
        try {
            if (!this.currentTest) return;
            
            // Load latest test results
            const response = await this.apiClient.get(`/tests/${this.currentTest.id}/results`);
            const results = response.data;
            
            // Update the results visualizer
            if (results && this.forceResultsVisualizer) {
                this.updateResultsVisualizer();
            }
            
            this.addLogEntry('info', 'Test results refreshed');
            
        } catch (error) {
            console.error('❌ Failed to refresh test results:', error);
        }
    }
    
    /**
     * Handle visualizer messages
     * @private
     * @param {Object} detail - Message detail
     */
    handleVisualizerMessage(detail) {
        if (!detail) return;
        
        // Add visualizer messages to log
        this.addLogEntry(detail.level || 'info', detail.message || 'Visualizer message');
        
        // Handle specific visualizer actions
        if (detail.action) {
            switch (detail.action) {
                case 'export':
                    this.handleComprehensiveExport();
                    break;
                case 'refresh':
                    this.refreshTestResults();
                    break;
                case 'fullscreen':
                    this.handleResultsFullscreen();
                    break;
            }
        }
    }
    
    // =========================
    // Log Viewer Integration Methods
    // =========================
    
    /**
     * Add log entry using the log viewer component
     * @param {string} level - Log level (info, warning, error, success)
     * @param {string} message - Log message
     */
    addLogEntry(level, message) {
        // Use the log viewer component if available
        if (this.logViewer && typeof this.logViewer.addSystemMessage === 'function') {
            this.logViewer.addSystemMessage(message, level.toUpperCase());
        } else {
            // Fallback to console logging
            console.log(`📝 [${level.toUpperCase()}] ${message}`);
        }
    }
    
    /**
     * Handle expand log viewer button click
     * @private
     */
    handleExpandLogViewer() {
        try {
            // Toggle fullscreen mode on the log viewer
            if (this.logViewer && typeof this.logViewer.handleFullscreenToggle === 'function') {
                this.logViewer.handleFullscreenToggle();
            } else {
                // Fallback: open logs page in new tab
                window.open('/logs', '_blank');
            }
            
            console.log('🔍 Log viewer expanded');
            
        } catch (error) {
            console.error('❌ Failed to expand log viewer:', error);
            // Fallback: open logs page
            window.open('/logs', '_blank');
        }
    }
    
    // =========================
    // Utility Methods
    // =========================
    
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
     * Update progress based on elapsed time
     * @private
     */
    updateProgress() {
        if (this.testState !== 'running') return;
        
        const elapsed = this.currentMeasurements.elapsedTime;
        const total = this.testConfig.duration;
        
        if (total > 0) {
            this.overallProgress = Math.min(100, (elapsed / total) * 100);
            
            // Update current step based on progress
            const stepProgress = this.overallProgress / 20; // 5 steps
            this.currentStep = Math.floor(stepProgress);
            
            this.updateProgressDisplay();
        }
    }
    
    /**
     * Get page manager instance (for external access)
     * @returns {EOLForceTestPageManager} Page manager instance
     */
    static getInstance() {
        return window.eolForceTestManager;
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        // Stop updates
        this.stopRealTimeUpdates();
        
        // Cleanup charts
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
        
        // Cleanup log viewer
        if (this.logViewer && typeof this.logViewer.cleanup === 'function') {
            this.logViewer.cleanup();
        }
        
        // Cleanup force results visualizer
        if (this.forceResultsVisualizer && typeof this.forceResultsVisualizer.cleanup === 'function') {
            this.forceResultsVisualizer.cleanup();
        }
        
        // Remove WebSocket listeners
        if (this.websocketManager) {
            this.websocketManager.off('test-data', this.handleTestData);
            this.websocketManager.off('hardware-status', this.handleHardwareUpdate);
        }
        
        console.log('🧹 EOL Force Test page manager cleanup complete');
    }
}

console.log('📝 EOL Force Test page manager module loaded successfully');