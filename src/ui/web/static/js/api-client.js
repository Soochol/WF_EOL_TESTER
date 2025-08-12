"""
API Client for WF EOL Tester FastAPI Backend

Provides a JavaScript client library for communicating with the FastAPI backend.
"""

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.websockets = {};
        this.eventCallbacks = {};
    }

    // Utility methods
    async _request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({
                    error: 'Unknown Error',
                    message: `HTTP ${response.status}: ${response.statusText}`
                }));
                throw new Error(errorData.message || errorData.error || 'Request failed');
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error(`API Request failed: ${method} ${url}`, error);
            throw error;
        }
    }

    // Health and status endpoints
    async getHealthStatus() {
        return this._request('GET', '/health');
    }

    async getSystemStatus() {
        return this._request('GET', '/status/system');
    }

    async getComprehensiveStatus() {
        return this._request('GET', '/status/comprehensive');
    }

    // Hardware control endpoints
    async getHardwareStatus() {
        return this._request('GET', '/hardware/status');
    }

    async connectHardware() {
        return this._request('POST', '/hardware/connect', {
            operation: 'connect'
        });
    }

    async disconnectHardware() {
        return this._request('POST', '/hardware/connect', {
            operation: 'disconnect'
        });
    }

    async initializeHardware(profileName = null, forceReconnect = false) {
        return this._request('POST', '/hardware/initialize', {
            profile_name: profileName,
            force_reconnect: forceReconnect
        });
    }

    // Robot control
    async getRobotStatus() {
        return this._request('GET', '/hardware/robot/status');
    }

    async controlRobot(operation, options = {}) {
        const payload = {
            operation: operation,
            ...options
        };
        return this._request('POST', '/hardware/robot/control', payload);
    }

    async homeRobot(axisId = 0) {
        return this.controlRobot('home', { axis_id: axisId });
    }

    async moveRobot(position, axisId = 0, velocity = null, acceleration = null, deceleration = null) {
        return this.controlRobot('move', {
            axis_id: axisId,
            position: position,
            velocity: velocity,
            acceleration: acceleration,
            deceleration: deceleration
        });
    }

    async enableRobotServo(axisId = 0) {
        return this.controlRobot('enable', { axis_id: axisId });
    }

    async disableRobotServo(axisId = 0) {
        return this.controlRobot('disable', { axis_id: axisId });
    }

    // Power control
    async getPowerStatus() {
        return this._request('GET', '/hardware/power/status');
    }

    async controlPower(operation, options = {}) {
        const payload = {
            operation: operation,
            ...options
        };
        return this._request('POST', '/hardware/power/control', payload);
    }

    async enablePowerOutput() {
        return this.controlPower('enable');
    }

    async disablePowerOutput() {
        return this.controlPower('disable');
    }

    async setPowerVoltage(voltage) {
        return this.controlPower('set_voltage', { voltage: voltage });
    }

    async setPowerCurrent(current) {
        return this.controlPower('set_current', { current: current });
    }

    // MCU control
    async getMCUStatus() {
        return this._request('GET', '/hardware/mcu/status');
    }

    async controlMCU(operation, options = {}) {
        const payload = {
            operation: operation,
            ...options
        };
        return this._request('POST', '/hardware/mcu/control', payload);
    }

    async setMCUOperatingTemperature(temperature) {
        return this.controlMCU('set_operating_temperature', { temperature: temperature });
    }

    async setMCUFanSpeed(fanSpeed) {
        return this.controlMCU('set_fan_speed', { fan_speed: fanSpeed });
    }

    // Load cell control
    async getLoadCellStatus() {
        return this._request('GET', '/hardware/loadcell/status');
    }

    async zeroLoadCell() {
        return this._request('POST', '/hardware/loadcell/zero');
    }

    // Digital I/O control
    async getDigitalIOStatus() {
        return this._request('GET', '/hardware/digital-io/status');
    }

    async controlDigitalIO(operation, options = {}) {
        const payload = {
            operation: operation,
            ...options
        };
        return this._request('POST', '/hardware/digital-io/control', payload);
    }

    async readDigitalInput(channel) {
        return this.controlDigitalIO('read_input', { channel: channel });
    }

    async writeDigitalOutput(channel, value) {
        return this.controlDigitalIO('write_output', { channel: channel, value: value });
    }

    async readAllDigitalInputs() {
        return this.controlDigitalIO('read_all_inputs');
    }

    // Test execution endpoints
    async startEOLForceTest(dutSerialNumber, dutPartNumber, profileName = null, operatorId = 'system') {
        return this._request('POST', '/tests/eol-force-test', {
            dut_serial_number: dutSerialNumber,
            dut_part_number: dutPartNumber,
            profile_name: profileName,
            operator_id: operatorId
        });
    }

    async getTestStatus(testId) {
        return this._request('GET', `/tests/eol-force-test/${testId}/status`);
    }

    async getTestProgress(testId) {
        return this._request('GET', `/tests/eol-force-test/${testId}/progress`);
    }

    async cancelTest(testId, reason = null, emergencyStop = false) {
        return this._request('POST', `/tests/eol-force-test/${testId}/cancel`, {
            reason: reason,
            emergency_stop: emergencyStop
        });
    }

    async executeRobotHome(operatorId = 'system') {
        return this._request('POST', '/tests/robot-home', {
            operator_id: operatorId
        });
    }

    async getActiveTests() {
        return this._request('GET', '/tests/active');
    }

    async cleanupCompletedTests() {
        return this._request('DELETE', '/tests/cleanup');
    }

    // Configuration endpoints
    async listProfiles() {
        return this._request('GET', '/config/profiles');
    }

    async getProfileUsage() {
        return this._request('GET', '/config/profiles/usage');
    }

    async getProfileConfiguration(profileName) {
        return this._request('GET', `/config/profiles/${profileName}`);
    }

    async validateProfileConfiguration(profileName) {
        return this._request('GET', `/config/profiles/${profileName}/validate`);
    }

    async getHardwareConfiguration() {
        return this._request('GET', '/config/hardware');
    }

    async getDUTDefaults(profileName = null) {
        const params = profileName ? `?profile_name=${encodeURIComponent(profileName)}` : '';
        return this._request('GET', `/config/dut-defaults${params}`);
    }

    async clearProfilePreferences() {
        return this._request('POST', '/config/profiles/clear-preferences');
    }

    // WebSocket connections
    connectWebSocket(endpoint, onMessage, onError = null, onClose = null) {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsURL = `${wsProtocol}//${window.location.host}/ws/${endpoint}`;
        
        if (this.websockets[endpoint]) {
            this.websockets[endpoint].close();
        }

        const ws = new WebSocket(wsURL);
        
        ws.onopen = () => {
            console.log(`WebSocket connected: ${endpoint}`);
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
                if (onError) onError(error);
            }
        };
        
        ws.onerror = (error) => {
            console.error(`WebSocket error on ${endpoint}:`, error);
            if (onError) onError(error);
        };
        
        ws.onclose = (event) => {
            console.log(`WebSocket closed: ${endpoint}`, event.code, event.reason);
            delete this.websockets[endpoint];
            if (onClose) onClose(event);
        };
        
        this.websockets[endpoint] = ws;
        return ws;
    }

    // Digital input monitoring
    startDigitalInputMonitoring(onUpdate, onError = null) {
        return this.connectWebSocket(
            'digital-input',
            (message) => {
                if (message.type === 'digital_input') {
                    onUpdate(message.inputs, message.changed_channels);
                }
            },
            onError
        );
    }

    // Test log monitoring
    startTestLogMonitoring(onLog, onError = null) {
        return this.connectWebSocket(
            'test-logs',
            (message) => {
                if (message.type === 'test_log') {
                    onLog(message);
                } else if (message.type === 'test_progress') {
                    onLog(message);
                }
            },
            onError
        );
    }

    // System status monitoring
    startSystemStatusMonitoring(onUpdate, onError = null) {
        return this.connectWebSocket(
            'system-status',
            (message) => {
                if (message.type === 'system_status') {
                    onUpdate(message);
                } else if (message.type === 'hardware_event') {
                    onUpdate(message);
                }
            },
            onError
        );
    }

    // Close all WebSocket connections
    closeAllWebSockets() {
        for (const [endpoint, ws] of Object.entries(this.websockets)) {
            ws.close();
        }
        this.websockets = {};
    }

    // Event handling
    on(event, callback) {
        if (!this.eventCallbacks[event]) {
            this.eventCallbacks[event] = [];
        }
        this.eventCallbacks[event].push(callback);
    }

    off(event, callback) {
        if (this.eventCallbacks[event]) {
            const index = this.eventCallbacks[event].indexOf(callback);
            if (index > -1) {
                this.eventCallbacks[event].splice(index, 1);
            }
        }
    }

    emit(event, data) {
        if (this.eventCallbacks[event]) {
            this.eventCallbacks[event].forEach(callback => callback(data));
        }
    }
}

// Export for use in other modules
window.APIClient = APIClient;

// Create global instance
window.apiClient = new APIClient();
