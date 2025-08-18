// Common API Client Utilities for WF EOL Tester
// Shared API calling patterns and error handling

const APIClient = {
    // Common API call function with consistent error handling
    call: async function(method, url, data = null, timeout = 5000) {
        const options = {
            method: method,
            headers: { 
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        console.log(`📡 [API] ${method} ${url}`, data || '');
        
        try {
            const response = await Promise.race([
                fetch(`/api${url}`, options),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Request timeout')), timeout)
                )
            ]);
            
            console.log(`🔍 [API] HTTP ${response.status} ${response.statusText}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ [API] Error response:`, errorText);
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log(`✅ [API] Response:`, result);
            return result;
        } catch (error) {
            console.error(`❌ [API] Call failed:`, error);
            throw error;
        }
    },

    // Hardware-specific API calls
    hardware: {
        // Get overall hardware status
        getStatus: async function() {
            return await APIClient.call('GET', '/hardware/status');
        },

        // Robot API calls
        robot: {
            connect: async function(axisId = 0, irqNo = 7) {
                return await APIClient.call('POST', '/hardware/robot/connect', {
                    axis_id: axisId,
                    irq_no: irqNo
                });
            },

            disconnect: async function() {
                return await APIClient.call('POST', '/hardware/robot/disconnect');
            },

            enableServo: async function(axisId = 0) {
                return await APIClient.call('POST', '/hardware/robot/servo/enable', {
                    axis_id: axisId
                });
            },

            disableServo: async function(axisId = 0) {
                return await APIClient.call('POST', '/hardware/robot/servo/disable', {
                    axis_id: axisId
                });
            },

            homeAxis: async function(axisId = 0) {
                return await APIClient.call('POST', '/hardware/robot/home-axis', {
                    axis_id: axisId
                });
            },

            moveAbsolute: async function(axisId, position, velocity = 200, acceleration = 1000, deceleration = 1000) {
                return await APIClient.call('POST', '/hardware/robot/move-absolute', {
                    axis_id: axisId,
                    position: position,
                    velocity: velocity,
                    acceleration: acceleration,
                    deceleration: deceleration
                });
            },

            moveRelative: async function(axisId, distance, velocity = 200, acceleration = 1000, deceleration = 1000) {
                return await APIClient.call('POST', '/hardware/robot/move-relative', {
                    axis_id: axisId,
                    distance: distance,
                    velocity: velocity,
                    acceleration: acceleration,
                    deceleration: deceleration
                });
            },

            emergencyStop: async function(axisId = 0) {
                return await APIClient.call('POST', '/hardware/robot/emergency-stop', {
                    axis_id: axisId
                });
            },

            getStatus: async function(axisId = 0) {
                return await APIClient.call('GET', `/hardware/robot/status?axis_id=${axisId}`);
            },

            getPosition: async function(axisId = 0) {
                return await APIClient.call('GET', `/hardware/robot/position?axis_id=${axisId}`);
            }
        },

        // Power supply API calls
        power: {
            getStatus: async function() {
                return await APIClient.call('GET', '/hardware/power/status');
            },

            enableOutput: async function() {
                return await APIClient.call('POST', '/hardware/power/control', {
                    operation: 'enable'
                });
            },

            disableOutput: async function() {
                return await APIClient.call('POST', '/hardware/power/control', {
                    operation: 'disable'
                });
            },

            setVoltage: async function(voltage) {
                return await APIClient.call('POST', '/hardware/power/control', {
                    operation: 'set_voltage',
                    voltage: voltage
                });
            },

            setCurrent: async function(current) {
                return await APIClient.call('POST', '/hardware/power/control', {
                    operation: 'set_current',
                    current: current
                });
            }
        },

        // MCU API calls
        mcu: {
            getStatus: async function() {
                return await APIClient.call('GET', '/hardware/mcu/status');
            },

            setOperatingTemperature: async function(temperature) {
                return await APIClient.call('POST', '/hardware/mcu/control', {
                    operation: 'set_operating_temperature',
                    temperature: temperature
                });
            },

            enterTestMode: async function() {
                return await APIClient.call('POST', '/hardware/mcu/control', {
                    operation: 'enter_test_mode'
                });
            },

            exitTestMode: async function() {
                return await APIClient.call('POST', '/hardware/mcu/control', {
                    operation: 'exit_test_mode'
                });
            },

            getTemperature: async function() {
                return await APIClient.call('GET', '/hardware/mcu/temperature');
            }
        },

        // Load cell API calls
        loadcell: {
            getStatus: async function() {
                return await APIClient.call('GET', '/hardware/loadcell/status');
            },

            zero: async function() {
                return await APIClient.call('POST', '/hardware/loadcell/zero');
            }
        },

        // Digital I/O API calls
        digitalIO: {
            getStatus: async function() {
                return await APIClient.call('GET', '/hardware/digital-io/status');
            },

            readInput: async function(channel) {
                return await APIClient.call('POST', '/hardware/digital-io/control', {
                    operation: 'read_input',
                    channel: channel
                });
            },

            writeOutput: async function(channel, value) {
                return await APIClient.call('POST', '/hardware/digital-io/control', {
                    operation: 'write_output',
                    channel: channel,
                    value: value
                });
            },

            readAllInputs: async function() {
                return await APIClient.call('POST', '/hardware/digital-io/control', {
                    operation: 'read_all_inputs'
                });
            }
        }
    },

    // Health check
    health: async function() {
        return await APIClient.call('GET', '/health');
    },

    // Error handling utility
    handleError: function(error, context = 'API Call') {
        console.error(`❌ [API] ${context} failed:`, error);
        
        let userMessage = 'An error occurred';
        if (error.message.includes('timeout')) {
            userMessage = 'Request timed out. Please try again.';
        } else if (error.message.includes('HTTP 404')) {
            userMessage = 'Endpoint not found. Please check the API documentation.';
        } else if (error.message.includes('HTTP 500')) {
            userMessage = 'Server error. Please check the server logs.';
        } else if (error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
            userMessage = 'Network error. Please check your connection.';
        }
        
        // Show notification if CommonUtils is available
        if (window.CommonUtils) {
            window.CommonUtils.showNotification(`${context}: ${userMessage}`, 'error');
        }
        
        return userMessage;
    }
};

// Make APIClient globally available
window.APIClient = APIClient;

console.log('✅ [API-COMMON] API Client utilities loaded and ready');