// Embedded Robot Control JavaScript
// Extracted from index.html for better maintainability

// Global embedded robot control variables
let embeddedRobotState = {
    isConnected: false,
    axisId: 0,
    motionStatus: 'idle',
    servoEnabled: false,
    currentPosition: 0,
    positionPollingInterval: null,
    statusPollingInterval: null,
    motionMonitoringInterval: null,
    isPageVisible: true
};

// Initialize embedded robot control
function initializeEmbeddedRobotControl() {
    console.log('🚀 [EMBEDDED] Initializing embedded robot control in index.html...');
    
    // Clear any existing intervals
    if (embeddedRobotState.positionPollingInterval) {
        clearInterval(embeddedRobotState.positionPollingInterval);
    }
    if (embeddedRobotState.motionMonitoringInterval) {
        clearInterval(embeddedRobotState.motionMonitoringInterval);
    }
    
    // Remove existing event listeners by cloning elements
    const buttonIds = [
        'robot-connect-btn', 'robot-disconnect-btn', 
        'robot-servo-on-btn', 'robot-servo-off-btn',
        'robot-home-axis-btn', 'robot-move-absolute-btn', 'robot-move-relative-btn',
        'robot-emergency-stop-btn', 'robot-refresh-status-btn'
    ];
    
    console.log('🔧 [EMBEDDED] Removing existing event listeners...');
    buttonIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            const newElement = element.cloneNode(true);
            element.parentNode.replaceChild(newElement, element);
            console.log(`🔧 [EMBEDDED] Cloned element: ${id}`);
        }
    });
    
    // Add embedded event listeners
    console.log('🔧 [EMBEDDED] Adding embedded event listeners...');
    document.getElementById('robot-connect-btn')?.addEventListener('click', embeddedHandleConnect);
    document.getElementById('robot-disconnect-btn')?.addEventListener('click', embeddedHandleDisconnect);
    document.getElementById('robot-servo-on-btn')?.addEventListener('click', embeddedHandleServoOn);
    document.getElementById('robot-servo-off-btn')?.addEventListener('click', embeddedHandleServoOff);
    document.getElementById('robot-home-axis-btn')?.addEventListener('click', embeddedHandleHomeAxis);
    document.getElementById('robot-move-absolute-btn')?.addEventListener('click', embeddedHandleMoveAbsolute);
    document.getElementById('robot-move-relative-btn')?.addEventListener('click', embeddedHandleMoveRelative);
    document.getElementById('robot-emergency-stop-btn')?.addEventListener('click', embeddedHandleEmergencyStop);
    
    // Override global functions as fallback
    window.handleConnect = embeddedHandleConnect;
    window.handleDisconnect = embeddedHandleDisconnect;
    window.handleServoOn = embeddedHandleServoOn;
    window.handleServoOff = embeddedHandleServoOff;
    window.handleHomeAxis = embeddedHandleHomeAxis;
    window.handleMoveAbsolute = embeddedHandleMoveAbsolute;
    window.handleMoveRelative = embeddedHandleMoveRelative;
    window.handleEmergencyStop = embeddedHandleEmergencyStop;
    
    // Add page visibility listener for performance optimization
    document.addEventListener('visibilitychange', () => {
        embeddedRobotState.isPageVisible = !document.hidden;
        if (embeddedRobotState.isPageVisible) {
            console.log('👁️ [EMBEDDED] Page visible - resuming polling');
        } else {
            console.log('🙈 [EMBEDDED] Page hidden - pausing polling');
        }
    });
    
    // Setup tab navigation for Movement Control
    setupEmbeddedTabs();
    
    // Start separate polling for position and status
    startEmbeddedPositionPolling(1000);
    startEmbeddedStatusPolling();
    
    console.log('✅ [EMBEDDED] Robot control functions overridden and polling started');
    console.log('✅ [EMBEDDED] Event listeners replaced with embedded versions');
}

// API helper
async function embeddedApiCall(method, url, data = null) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (data) options.body = JSON.stringify(data);
    
    console.log(`📡 [EMBEDDED] API ${method} ${url}`, data || '');
    
    try {
        const response = await fetch(`/api${url}`, options);
        console.log(`🔍 [EMBEDDED] HTTP Response status: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
            console.error(`❌ [EMBEDDED] HTTP Error: ${response.status} ${response.statusText}`);
            const errorText = await response.text();
            console.error(`❌ [EMBEDDED] Error response body:`, errorText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log(`✅ [EMBEDDED] API Response:`, result);
        return result;
    } catch (error) {
        console.error(`❌ [EMBEDDED] API Error:`, error);
        console.error(`❌ [EMBEDDED] API Error details:`, error.message);
        throw error;
    }
}

// Separate position and status polling for better performance
function startEmbeddedPositionPolling(interval) {
    console.log(`📍 [EMBEDDED] Starting position polling with ${interval}ms interval`);
    
    if (embeddedRobotState.positionPollingInterval) {
        clearInterval(embeddedRobotState.positionPollingInterval);
    }
    
    embeddedRobotState.positionPollingInterval = setInterval(async () => {
        if (embeddedRobotState.isConnected && embeddedRobotState.isPageVisible) {
            console.log(`🔄 [EMBEDDED] Polling position (${interval}ms interval)...`);
            try {
                await updateEmbeddedPosition();
            } catch (error) {
                console.error('❌ [EMBEDDED] Position update failed:', error);
            }
        }
    }, interval);
}

function startEmbeddedStatusPolling() {
    console.log(`📊 [EMBEDDED] Starting status polling with 2000ms interval`);
    
    if (embeddedRobotState.statusPollingInterval) {
        clearInterval(embeddedRobotState.statusPollingInterval);
    }
    
    embeddedRobotState.statusPollingInterval = setInterval(async () => {
        if (embeddedRobotState.isConnected && embeddedRobotState.isPageVisible) {
            console.log(`🔄 [EMBEDDED] Polling status (2000ms interval)...`);
            try {
                await updateEmbeddedStatus();
            } catch (error) {
                console.error('❌ [EMBEDDED] Status update failed:', error);
            }
        }
    }, 2000);
}

function stopEmbeddedPolling() {
    if (embeddedRobotState.positionPollingInterval) {
        clearInterval(embeddedRobotState.positionPollingInterval);
        embeddedRobotState.positionPollingInterval = null;
    }
    if (embeddedRobotState.statusPollingInterval) {
        clearInterval(embeddedRobotState.statusPollingInterval);
        embeddedRobotState.statusPollingInterval = null;
    }
    console.log('🛑 [EMBEDDED] All polling stopped');
}

function updateEmbeddedPollingInterval() {
    if (embeddedRobotState.motionStatus === 'moving' || embeddedRobotState.motionStatus === 'homing') {
        console.log('🏃 [EMBEDDED] Motion detected: Switching to fast polling (250ms)');
        startEmbeddedPositionPolling(250);
    } else {
        console.log('🛑 [EMBEDDED] Motion completed: Switching to normal polling (1000ms)');
        startEmbeddedPositionPolling(1000);
    }
}

async function updateEmbeddedPosition() {
    try {
        const result = await embeddedApiCall('GET', `/hardware/robot/position?axis_id=${embeddedRobotState.axisId}`);
        if (result.success) {
            embeddedRobotState.currentPosition = result.data.position;
            updateEmbeddedPositionDisplay(result.data.position);
            console.log(`📍 [EMBEDDED] Position updated: ${result.data.position}μm`);
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Failed to update position:', error);
    }
}

function updateEmbeddedPositionDisplay(position) {
    const positionElement = document.getElementById('robot-current-position');
    if (positionElement) {
        // Check if it has a nested .value span structure
        const valueSpan = positionElement.querySelector('.value');
        if (valueSpan) {
            valueSpan.textContent = position.toFixed(3);
            console.log(`📍 [EMBEDDED] Position display updated with nested structure: ${position.toFixed(3)}μm`);
        } else {
            // Fallback to direct text content
            positionElement.textContent = position.toFixed(3);
            console.log(`📍 [EMBEDDED] Position display updated directly: ${position.toFixed(3)}μm`);
        }
    } else {
        console.warn('❌ [EMBEDDED] robot-current-position element not found');
    }
}

// Event handlers
async function embeddedHandleConnect() {
    console.log('🔌 [EMBEDDED] Connect clicked');
    try {
        const result = await embeddedApiCall('POST', '/hardware/robot/connect', { 
            axis_id: embeddedRobotState.axisId, 
            irq_no: 7 
        });
        
        console.log('🔍 [EMBEDDED] Connect API result:', result);
        
        if (result && result.success) {
            embeddedRobotState.isConnected = true;
            console.log('✅ [EMBEDDED] Connected successfully');
            
            // Update UI state after successful connection
            updateEmbeddedConnectionState(true);
            
            // Get current status to update servo state
            await updateEmbeddedStatus();
        } else {
            console.warn('⚠️ [EMBEDDED] Connect API returned failure:', result);
            updateEmbeddedConnectionState(false);
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Connect failed:', error);
        console.error('❌ [EMBEDDED] Error details:', error.message, error.stack);
        updateEmbeddedConnectionState(false);
    }
}

async function embeddedHandleDisconnect() {
    console.log('🔌 [EMBEDDED] Disconnect clicked');
    try {
        const result = await embeddedApiCall('POST', '/hardware/robot/disconnect');
        if (result.success) {
            embeddedRobotState.isConnected = false;
            embeddedRobotState.motionStatus = 'idle';
            updateEmbeddedPollingInterval();
            console.log('✅ [EMBEDDED] Disconnected successfully');
            
            // Update UI state after disconnection
            updateEmbeddedConnectionState(false);
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Disconnect failed:', error);
    }
}

async function embeddedHandleServoOn() {
    console.log('⚡ [EMBEDDED] Servo enable clicked');
    try {
        const result = await embeddedApiCall('POST', '/hardware/robot/servo/enable', { 
            axis_id: embeddedRobotState.axisId 
        });
        if (result.success) {
            embeddedRobotState.servoEnabled = true;
            console.log('✅ [EMBEDDED] Servo enabled');
            
            // Update servo status in UI
            updateEmbeddedServoStatus(true);
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Servo enable failed:', error);
    }
}

async function embeddedHandleServoOff() {
    console.log('🔴 [EMBEDDED] Servo disable clicked');
    try {
        const result = await embeddedApiCall('POST', '/hardware/robot/servo/disable', { 
            axis_id: embeddedRobotState.axisId 
        });
        if (result.success) {
            embeddedRobotState.servoEnabled = false;
            console.log('✅ [EMBEDDED] Servo disabled');
            
            // Update servo status in UI
            updateEmbeddedServoStatus(false);
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Servo disable failed:', error);
    }
}

async function embeddedHandleHomeAxis() {
    console.log('🏠 [EMBEDDED] Home axis clicked');
    try {
        embeddedRobotState.motionStatus = 'homing';
        updateEmbeddedPollingInterval();
        startEmbeddedMotionMonitoring();
        
        const result = await embeddedApiCall('POST', '/hardware/robot/home-axis', { 
            axis_id: embeddedRobotState.axisId 
        });
        if (result.success) {
            console.log('✅ [EMBEDDED] Homing started');
            updateEmbeddedMotionStatus('homing');
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Home failed:', error);
        embeddedRobotState.motionStatus = 'idle';
        updateEmbeddedPollingInterval();
        updateEmbeddedMotionStatus('idle');
    }
}

async function embeddedHandleMoveAbsolute() {
    console.log('🎯 [EMBEDDED] Absolute move clicked');
    try {
        const position = parseFloat(document.getElementById('absolute-position').value);
        const velocity = parseFloat(document.getElementById('absolute-velocity').value) || 200;
        const acceleration = parseFloat(document.getElementById('absolute-acceleration').value) || 1000;
        const deceleration = parseFloat(document.getElementById('absolute-deceleration').value) || 1000;
        
        if (isNaN(position)) {
            console.error('❌ [EMBEDDED] Invalid position value');
            return;
        }
        
        embeddedRobotState.motionStatus = 'moving';
        updateEmbeddedPollingInterval();
        startEmbeddedMotionMonitoring();
        
        const result = await embeddedApiCall('POST', '/hardware/robot/move-absolute', {
            axis_id: embeddedRobotState.axisId,
            position: position,
            velocity: velocity,
            acceleration: acceleration,
            deceleration: deceleration
        });
        
        if (result.success) {
            console.log(`✅ [EMBEDDED] Moving to ${position}μm`);
            updateEmbeddedMotionStatus('moving');
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Absolute move failed:', error);
        embeddedRobotState.motionStatus = 'idle';
        updateEmbeddedPollingInterval();
        updateEmbeddedMotionStatus('idle');
    }
}

async function embeddedHandleMoveRelative() {
    console.log('↔️ [EMBEDDED] Relative move clicked');
    try {
        const distance = parseFloat(document.getElementById('relative-distance').value);
        const velocity = parseFloat(document.getElementById('relative-velocity').value) || 200;
        const acceleration = parseFloat(document.getElementById('relative-acceleration').value) || 1000;
        const deceleration = parseFloat(document.getElementById('relative-deceleration').value) || 1000;
        
        if (isNaN(distance)) {
            console.error('❌ [EMBEDDED] Invalid distance value');
            return;
        }
        
        embeddedRobotState.motionStatus = 'moving';
        updateEmbeddedPollingInterval();
        startEmbeddedMotionMonitoring();
        
        const result = await embeddedApiCall('POST', '/hardware/robot/move-relative', {
            axis_id: embeddedRobotState.axisId,
            distance: distance,
            velocity: velocity,
            acceleration: acceleration,
            deceleration: deceleration
        });
        
        if (result.success) {
            console.log(`✅ [EMBEDDED] Moving ${distance}μm`);
            updateEmbeddedMotionStatus('moving');
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Relative move failed:', error);
        embeddedRobotState.motionStatus = 'idle';
        updateEmbeddedPollingInterval();
        updateEmbeddedMotionStatus('idle');
    }
}

async function embeddedHandleEmergencyStop() {
    console.log('🛑 [EMBEDDED] Emergency stop clicked!');
    try {
        const result = await embeddedApiCall('POST', '/hardware/robot/emergency-stop', { 
            axis_id: embeddedRobotState.axisId 
        });
        if (result.success) {
            embeddedRobotState.motionStatus = 'stopped';
            updateEmbeddedPollingInterval();
            stopEmbeddedMotionMonitoring();
            console.log('🛑 [EMBEDDED] Emergency stop completed successfully');
            updateEmbeddedMotionStatus('stopped');
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Emergency stop failed:', error);
    }
}

// Motion monitoring
function startEmbeddedMotionMonitoring() {
    console.log('👀 [EMBEDDED] Starting motion monitoring...');
    
    if (embeddedRobotState.motionMonitoringInterval) {
        clearInterval(embeddedRobotState.motionMonitoringInterval);
    }
    
    embeddedRobotState.motionMonitoringInterval = setInterval(async () => {
        try {
            const result = await embeddedApiCall('GET', `/hardware/robot/status?axis_id=${embeddedRobotState.axisId}`);
            if (result.success) {
                const isMoving = result.data.is_moving;
                console.log(`🔍 [EMBEDDED] Motion check: isMoving=${isMoving}, motionStatus=${embeddedRobotState.motionStatus}`);
                
                if (!isMoving && (embeddedRobotState.motionStatus === 'moving' || embeddedRobotState.motionStatus === 'homing')) {
                    console.log('✅ [EMBEDDED] Motion completed detected!');
                    embeddedRobotState.motionStatus = 'idle';
                    updateEmbeddedPollingInterval();
                    stopEmbeddedMotionMonitoring();
                } else if (embeddedRobotState.motionStatus === 'stopped') {
                    console.log('🛑 [EMBEDDED] Emergency stop detected, stopping monitoring');
                    stopEmbeddedMotionMonitoring();
                    updateEmbeddedPollingInterval();
                }
            }
        } catch (error) {
            console.warn('❌ [EMBEDDED] Motion monitoring failed:', error);
        }
    }, 100);
}

function stopEmbeddedMotionMonitoring() {
    if (embeddedRobotState.motionMonitoringInterval) {
        clearInterval(embeddedRobotState.motionMonitoringInterval);
        embeddedRobotState.motionMonitoringInterval = null;
        console.log('🛑 [EMBEDDED] Motion monitoring stopped');
    }
}

// UI State Management Functions
function updateEmbeddedConnectionState(connected) {
    console.log(`🔗 [EMBEDDED] Updating connection state: ${connected}`);
    
    // Update connection status display
    const statusElement = document.getElementById('robot-connection-status');
    if (statusElement) {
        const statusText = statusElement.querySelector('span');
        const statusDot = statusElement.querySelector('.status-dot');
        if (statusText && statusDot) {
            statusText.textContent = connected ? 'Connected' : 'Disconnected';
            statusDot.className = connected ? 'status-dot status-success' : 'status-dot status-error';
        }
    }
    
    // Update badge status
    const badgeElement = document.getElementById('robot-status-badge');
    if (badgeElement) {
        const badgeText = badgeElement.querySelector('.status-text');
        const badgeLight = badgeElement.querySelector('.status-light');
        if (badgeText && badgeLight) {
            badgeText.textContent = connected ? 'Connected' : 'Disconnected';
            badgeLight.className = connected ? 'status-light status-success' : 'status-light status-error';
        }
    }
    
    // Enable/disable buttons based on connection state
    const connectBtn = document.getElementById('robot-connect-btn');
    const disconnectBtn = document.getElementById('robot-disconnect-btn');
    const servoOnBtn = document.getElementById('robot-servo-on-btn');
    const servoOffBtn = document.getElementById('robot-servo-off-btn');
    const homeBtn = document.getElementById('robot-home-axis-btn');
    const moveAbsBtn = document.getElementById('robot-move-absolute-btn');
    const moveRelBtn = document.getElementById('robot-move-relative-btn');
    
    if (connectBtn) connectBtn.disabled = connected;
    if (disconnectBtn) disconnectBtn.disabled = !connected;
    
    // Enable servo controls when connected
    if (servoOnBtn) {
        servoOnBtn.disabled = !connected;
        console.log(`🔧 [EMBEDDED] Servo ON button disabled: ${servoOnBtn.disabled}`);
    }
    if (servoOffBtn) {
        servoOffBtn.disabled = !connected;
        console.log(`🔧 [EMBEDDED] Servo OFF button disabled: ${servoOffBtn.disabled}`);
    }
    
    // Enable movement controls when connected
    if (homeBtn) homeBtn.disabled = !connected;
    if (moveAbsBtn) moveAbsBtn.disabled = !connected;
    if (moveRelBtn) moveRelBtn.disabled = !connected;
    
    console.log(`✅ [EMBEDDED] UI state updated for connection: ${connected}`);
}

function updateEmbeddedServoStatus(enabled) {
    console.log(`⚙️ [EMBEDDED] Updating servo status: ${enabled}`);
    
    const servoElement = document.getElementById('robot-servo-status');
    if (servoElement) {
        // Direct selection to match actual HTML structure
        const statusDot = servoElement.querySelector('.status-dot');
        const statusText = servoElement.querySelector('span');
        
        if (statusDot && statusText) {
            statusText.textContent = enabled ? 'Enabled' : 'Disabled';
            statusDot.className = enabled ? 'status-dot status-success' : 'status-dot status-error';
            console.log(`🎯 [EMBEDDED] DOM updated - Dot: ${statusDot.className}, Text: ${statusText.textContent}`);
        } else {
            console.warn(`❌ [EMBEDDED] Could not find status elements - Dot: ${!!statusDot}, Text: ${!!statusText}`);
        }
    } else {
        console.warn('❌ [EMBEDDED] robot-servo-status element not found');
    }
    
    console.log(`✅ [EMBEDDED] Servo status updated: ${enabled}`);
}

function updateEmbeddedMotionStatus(status) {
    console.log(`🔄 [EMBEDDED] Updating motion status: ${status}`);
    
    const motionElement = document.getElementById('robot-motion-status');
    if (motionElement) {
        const statusIndicator = motionElement.querySelector('.status-indicator');
        if (statusIndicator) {
            const statusDot = statusIndicator.querySelector('.status-dot');
            const statusText = statusIndicator.querySelector('span');
            
            if (statusDot && statusText) {
                let displayText = 'Unknown';
                let statusClass = 'status-dot status-unknown';
                
                switch (status) {
                    case 'idle':
                        displayText = 'Idle';
                        statusClass = 'status-dot status-success';
                        break;
                    case 'moving':
                        displayText = 'Moving';
                        statusClass = 'status-dot status-warning';
                        break;
                    case 'homing':
                        displayText = 'Homing';
                        statusClass = 'status-dot status-warning';
                        break;
                    case 'stopped':
                        displayText = 'Stopped';
                        statusClass = 'status-dot status-error';
                        break;
                }
                
                statusText.textContent = displayText;
                statusDot.className = statusClass;
            }
        }
    }
    
    console.log(`✅ [EMBEDDED] Motion status updated: ${status}`);
}

async function updateEmbeddedStatus() {
    console.log('📊 [EMBEDDED] Updating full status...');
    try {
        const result = await embeddedApiCall('GET', `/hardware/robot/status?axis_id=${embeddedRobotState.axisId}`);
        if (result.success) {
            const status = result.data;
            
            // Update internal state
            embeddedRobotState.isConnected = status.connected;
            embeddedRobotState.servoEnabled = status.servo_enabled;
            embeddedRobotState.currentPosition = status.current_position || status.position || 0;
            
            // Update UI
            updateEmbeddedConnectionState(status.connected);
            updateEmbeddedServoStatus(status.servo_enabled);
            updateEmbeddedPositionDisplay(embeddedRobotState.currentPosition);
            
            // Update motion status
            const isMoving = status.is_moving;
            if (isMoving) {
                updateEmbeddedMotionStatus('moving');
            } else {
                updateEmbeddedMotionStatus('idle');
            }
            
            console.log('✅ [EMBEDDED] Full status updated:', status);
        }
    } catch (error) {
        console.error('❌ [EMBEDDED] Failed to update status:', error);
    }
}

// Setup tab navigation for Movement Control
function setupEmbeddedTabs() {
    console.log('🔧 [EMBEDDED] Setting up tab navigation...');
    
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (tabButtons.length === 0) {
        console.warn('⚠️ [EMBEDDED] No tab buttons found');
        return;
    }
    
    console.log(`🔧 [EMBEDDED] Found ${tabButtons.length} tab buttons and ${tabContents.length} tab contents`);
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            console.log(`🔧 [EMBEDDED] Tab clicked: ${tabName}`);
            
            // Update active tab button
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
                btn.style.background = '#f8f9fa';
                btn.style.color = '#495057';
            });
            
            button.classList.add('active');
            button.style.background = '#007bff';
            button.style.color = 'white';
            
            // Update active tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                content.style.display = 'none';
            });
            
            const targetTab = document.getElementById(`${tabName}-tab`);
            if (targetTab) {
                targetTab.classList.add('active');
                targetTab.style.display = 'block';
                console.log(`✅ [EMBEDDED] Tab switched to: ${tabName}`);
            } else {
                console.error(`❌ [EMBEDDED] Target tab not found: ${tabName}-tab`);
            }
        });
    });
    
    console.log('✅ [EMBEDDED] Tab navigation setup completed');
}

console.log('✅ [EMBEDDED] Robot Control functions defined in external file');