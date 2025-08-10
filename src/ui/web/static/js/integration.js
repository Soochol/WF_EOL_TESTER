"""
FastAPI Integration for WF EOL Tester Web Interface

Integrates the existing web interface with the new FastAPI backend.
"""

// Global state management
window.appState = {
    hardwareStatus: {},
    testRunning: false,
    currentTestId: null,
    digitalInputs: {},
    systemStatus: {},
    profiles: [],
    currentProfile: 'default'
};

// Initialize FastAPI integration when page loads
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing FastAPI integration...');
    
    // Initialize API client
    if (!window.apiClient) {
        console.error('API Client not loaded!');
        return;
    }
    
    // Start WebSocket connections
    initializeWebSocketConnections();
    
    // Load initial data
    await loadInitialData();
    
    // Set up event handlers
    setupEventHandlers();
    
    // Start periodic status updates
    startPeriodicUpdates();
    
    console.log('FastAPI integration initialized');
});

// WebSocket initialization
function initializeWebSocketConnections() {
    // Digital input monitoring
    window.apiClient.startDigitalInputMonitoring(
        (inputs, changedChannels) => {
            window.appState.digitalInputs = inputs;
            updateDigitalInputDisplay(inputs, changedChannels);
        },
        (error) => {
            console.error('Digital input WebSocket error:', error);
        }
    );
    
    // Test log monitoring
    window.apiClient.startTestLogMonitoring(
        (message) => {
            handleTestLogMessage(message);
        },
        (error) => {
            console.error('Test log WebSocket error:', error);
        }
    );
    
    // System status monitoring
    window.apiClient.startSystemStatusMonitoring(
        (message) => {
            handleSystemStatusMessage(message);
        },
        (error) => {
            console.error('System status WebSocket error:', error);
        }
    );
}

// Load initial data
async function loadInitialData() {
    try {
        // Load profiles
        const profilesResponse = await window.apiClient.listProfiles();
        window.appState.profiles = profilesResponse.profiles;
        window.appState.currentProfile = profilesResponse.current_profile;
        
        // Load hardware status
        await updateHardwareStatus();
        
        // Load system status
        await updateSystemStatus();
        
    } catch (error) {
        console.error('Failed to load initial data:', error);
        showNotification('Failed to connect to server', 'error');
    }
}

// Event handler setup
function setupEventHandlers() {
    // Emergency stop button
    const emergencyStopBtn = document.getElementById('emergency-stop');
    if (emergencyStopBtn) {
        emergencyStopBtn.addEventListener('click', handleEmergencyStop);
    }
    
    // Quick action buttons
    const startTestBtn = document.querySelector('[data-action="start-eol-test"]');
    if (startTestBtn) {
        startTestBtn.addEventListener('click', () => showStartTestDialog());
    }
    
    const robotHomeBtn = document.querySelector('[data-action="robot-home"]');
    if (robotHomeBtn) {
        robotHomeBtn.addEventListener('click', handleRobotHome);
    }
    
    const checkHardwareBtn = document.querySelector('[data-action="check-hardware"]');
    if (checkHardwareBtn) {
        checkHardwareBtn.addEventListener('click', handleCheckHardware);
    }
}

// Periodic status updates
function startPeriodicUpdates() {
    // Update hardware status every 5 seconds
    setInterval(updateHardwareStatus, 5000);
    
    // Update system status every 10 seconds
    setInterval(updateSystemStatus, 10000);
    
    // Update time display
    setInterval(updateTimeDisplay, 1000);
}

// Hardware status update
async function updateHardwareStatus() {
    try {
        const status = await window.apiClient.getHardwareStatus();
        window.appState.hardwareStatus = status;
        
        // Update UI elements
        updateHardwareStatusDisplay(status);
        updateConnectionStatus(status.overall_status);
        
    } catch (error) {
        console.error('Failed to update hardware status:', error);
        updateConnectionStatus('disconnected');
    }
}

// System status update
async function updateSystemStatus() {
    try {
        const status = await window.apiClient.getSystemStatus();
        window.appState.systemStatus = status;
        
        // Update memory and CPU display
        updateSystemResourceDisplay(status);
        
    } catch (error) {
        console.error('Failed to update system status:', error);
    }
}

// Update hardware status display
function updateHardwareStatusDisplay(status) {
    const statusElements = {
        'robot-status': status.robot ? 'Connected' : 'Disconnected',
        'power-status': status.power ? 'Connected' : 'Disconnected',
        'mcu-status': status.mcu ? 'Connected' : 'Disconnected',
        'loadcell-status': status.loadcell ? 'Connected' : 'Disconnected'
    };
    
    for (const [elementId, statusText] of Object.entries(statusElements)) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = statusText;
            element.className = `status-value ${status[elementId.split('-')[0]] ? 'connected' : 'disconnected'}`;
        }
    }
}

// Update connection status indicator
function updateConnectionStatus(overallStatus) {
    const connectionIndicator = document.getElementById('connection-indicator');
    const connectionText = document.getElementById('connection-text');
    
    if (connectionIndicator && connectionText) {
        connectionIndicator.className = `connection-indicator ${overallStatus === 'connected' ? 'online' : 'offline'}`;
        connectionText.textContent = overallStatus === 'connected' ? 'Online' : 'Offline';
    }
    
    // Update main status indicator
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (statusIndicator && statusText) {
        if (overallStatus === 'connected') {
            statusIndicator.style.color = '#28a745';
            statusText.textContent = 'System Ready';
        } else if (overallStatus === 'partial') {
            statusIndicator.style.color = '#ffc107';
            statusText.textContent = 'Partial Connection';
        } else {
            statusIndicator.style.color = '#dc3545';
            statusText.textContent = 'Hardware Disconnected';
        }
    }
}

// Update system resource display
function updateSystemResourceDisplay(status) {
    const memoryUsage = document.getElementById('memory-usage');
    const cpuUsage = document.getElementById('cpu-usage');
    
    if (status.system) {
        if (memoryUsage) {
            const memPercent = status.system.memory ? status.system.memory.percent.toFixed(1) : '--';
            memoryUsage.textContent = `${memPercent}%`;
        }
        
        if (cpuUsage) {
            const cpuPercent = status.system.cpu_percent ? status.system.cpu_percent.toFixed(1) : '--';
            cpuUsage.textContent = `${cpuPercent}%`;
        }
    }
}

// Update digital input display
function updateDigitalInputDisplay(inputs, changedChannels) {
    // This would integrate with any digital I/O display components
    console.log('Digital inputs updated:', inputs, 'Changed:', changedChannels);
}

// Update time display
function updateTimeDisplay() {
    const timeElement = document.getElementById('footer-time');
    if (timeElement) {
        const now = new Date();
        timeElement.textContent = now.toLocaleTimeString();
    }
}

// Event handlers
async function handleEmergencyStop() {
    try {
        if (window.appState.currentTestId) {
            await window.apiClient.cancelTest(window.appState.currentTestId, 'Emergency stop requested', true);
            showNotification('Emergency stop activated', 'warning');
        } else {
            showNotification('Emergency stop pressed (no active test)', 'warning');
        }
    } catch (error) {
        console.error('Emergency stop failed:', error);
        showNotification('Emergency stop failed: ' + error.message, 'error');
    }
}

async function handleRobotHome() {
    try {
        showNotification('Robot homing started...', 'info');
        const result = await window.apiClient.executeRobotHome();
        
        if (result.success) {
            showNotification(`Robot homing completed in ${result.duration_seconds.toFixed(2)}s`, 'success');
        } else {
            showNotification('Robot homing failed: ' + result.error_message, 'error');
        }
    } catch (error) {
        console.error('Robot home failed:', error);
        showNotification('Robot homing failed: ' + error.message, 'error');
    }
}

async function handleCheckHardware() {
    try {
        showNotification('Checking hardware connections...', 'info');
        await window.apiClient.connectHardware();
        await updateHardwareStatus();
        showNotification('Hardware check completed', 'success');
    } catch (error) {
        console.error('Hardware check failed:', error);
        showNotification('Hardware check failed: ' + error.message, 'error');
    }
}

// Test log message handler
function handleTestLogMessage(message) {
    if (message.type === 'test_log') {
        // Add log message to display
        addLogMessage(message.timestamp, message.level, message.message);
    } else if (message.type === 'test_progress') {
        // Update test progress
        updateTestProgress(message);
    }
}

// System status message handler
function handleSystemStatusMessage(message) {
    if (message.type === 'system_status') {
        window.appState.hardwareStatus = message.hardware_status;
        updateHardwareStatusDisplay(message.hardware_status);
    } else if (message.type === 'hardware_event') {
        showNotification(`Hardware Event: ${message.message}`, 'info');
    }
}

// Show start test dialog
function showStartTestDialog() {
    // This would open a modal dialog with test parameters
    // For now, use simple prompts
    const dutSerial = prompt('Enter DUT Serial Number:', 'WF-EOL-001');
    if (!dutSerial) return;
    
    const dutPart = prompt('Enter DUT Part Number:', 'WF-PART-001');
    if (!dutPart) return;
    
    startEOLTest(dutSerial, dutPart);
}

// Start EOL test
async function startEOLTest(dutSerial, dutPart, profileName = null) {
    try {
        showNotification('Starting EOL Force Test...', 'info');
        
        const result = await window.apiClient.startEOLForceTest(
            dutSerial,
            dutPart,
            profileName || window.appState.currentProfile
        );
        
        window.appState.testRunning = true;
        window.appState.currentTestId = result.test_id;
        
        showNotification(`EOL Test started - ID: ${result.test_id}`, 'success');
        
        // Start monitoring test progress
        monitorTestProgress(result.test_id);
        
    } catch (error) {
        console.error('Failed to start EOL test:', error);
        showNotification('Failed to start test: ' + error.message, 'error');
    }
}

// Monitor test progress
function monitorTestProgress(testId) {
    const progressInterval = setInterval(async () => {
        try {
            const status = await window.apiClient.getTestStatus(testId);
            
            updateTestProgress(status);
            
            // Check if test is complete
            if (['completed', 'failed', 'cancelled'].includes(status.status)) {
                clearInterval(progressInterval);
                window.appState.testRunning = false;
                window.appState.currentTestId = null;
                
                const statusColor = status.status === 'completed' ? 'success' : 'error';
                showNotification(`Test ${status.status}: ${status.result || 'See logs for details'}`, statusColor);
            }
            
        } catch (error) {
            console.error('Failed to get test status:', error);
            clearInterval(progressInterval);
        }
    }, 2000); // Check every 2 seconds
}

// Update test progress display
function updateTestProgress(progress) {
    const activeTestElement = document.getElementById('active-test');
    if (activeTestElement) {
        if (progress.test_id) {
            activeTestElement.textContent = `Test ${progress.test_id.substring(0, 8)}... (${progress.progress_percentage || 0}%)`;
        } else {
            activeTestElement.textContent = 'None';
        }
    }
}

// Add log message to display
function addLogMessage(timestamp, level, message) {
    console.log(`[${timestamp}] ${level}: ${message}`);
    // This could be enhanced to add to a log display component
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple notification system - could be enhanced with a proper notification component
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Update footer status
    const footerStatus = document.getElementById('footer-status');
    if (footerStatus) {
        footerStatus.textContent = message;
        footerStatus.className = `footer-value status-${type}`;
    }
}

// Export functions for use in other modules
window.fastAPIIntegration = {
    updateHardwareStatus,
    updateSystemStatus,
    startEOLTest,
    handleRobotHome,
    handleCheckHardware,
    showNotification
};
