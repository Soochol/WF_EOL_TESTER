/**
 * WebSocket Manager - WF EOL Tester Web Interface
 * 
 * This service handles WebSocket connections for real-time updates including:
 * - Connection management with automatic reconnection and exponential backoff
 * - Message routing and event handling with type safety
 * - Hardware status updates and digital I/O monitoring
 * - Test progress monitoring and live data streaming
 * - Connection state management and health monitoring
 * - Error handling, recovery, and graceful degradation
 * - Message queuing and delivery guarantees
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

/**
 * WebSocket connection states
 */
const ConnectionState = {
    DISCONNECTED: 'disconnected',
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    RECONNECTING: 'reconnecting',
    FAILED: 'failed'
};

/**
 * Message types for WebSocket communication
 */
const MessageType = {
    // Hardware messages
    HARDWARE_STATUS: 'hardware_status',
    HARDWARE_UPDATE: 'hardware_update',
    DIGITAL_IO_UPDATE: 'digital_io_update',
    
    // Test messages
    TEST_STATUS: 'test_status',
    TEST_PROGRESS: 'test_progress',
    TEST_DATA: 'test_data',
    TEST_LOG: 'test_log',
    
    // System messages
    SYSTEM_STATUS: 'system_status',
    ERROR: 'error',
    HEARTBEAT: 'heartbeat',
    
    // Control messages
    EMERGENCY_STOP: 'emergency_stop',
    SUBSCRIBE: 'subscribe',
    UNSUBSCRIBE: 'unsubscribe'
};

/**
 * WebSocket Manager with comprehensive connection management
 * 
 * Implements robust WebSocket communication with automatic reconnection,
 * message queuing, and event-driven architecture.
 */
export class WebSocketManager {
    /**
     * Initialize WebSocket Manager
     * @param {Object} config - WebSocket configuration
     */
    constructor(config) {
        this.config = {
            url: 'ws://localhost:8080/ws',
            reconnectInterval: 5000,
            maxReconnectAttempts: 10,
            heartbeatInterval: 30000,
            messageTimeout: 10000,
            ...config
        };
        
        console.log('🔧 WebSocket Manager initializing with config:', this.config);
        
        // Connection state
        this.state = ConnectionState.DISCONNECTED;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.reconnectTimer = null;
        this.heartbeatTimer = null;
        this.lastHeartbeat = null;
        
        // Event handling
        this.eventHandlers = new Map();
        this.messageQueue = [];
        this.pendingMessages = new Map();
        this.messageId = 0;
        
        // Subscription management
        this.subscriptions = new Set();
        this.autoResubscribe = true;
        
        // Connection monitoring
        this.connectionStartTime = null;
        this.totalReconnects = 0;
        this.lastError = null;
        
        // Bind methods
        this.handleOpen = this.handleOpen.bind(this);
        this.handleMessage = this.handleMessage.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.handleError = this.handleError.bind(this);
        
        console.log('✅ WebSocket Manager initialized');
    }

    /**
     * Connect to WebSocket server
     * @returns {Promise<void>}
     */
    async connect() {
        if (this.state === ConnectionState.CONNECTED || this.state === ConnectionState.CONNECTING) {
            console.log('⚠️ WebSocket already connected or connecting');
            return;
        }
        
        try {
            console.log(`🔄 Connecting to WebSocket: ${this.config.url}`);
            this.setState(ConnectionState.CONNECTING);
            this.connectionStartTime = Date.now();
            
            // Create WebSocket connection
            this.socket = new WebSocket(this.config.url);
            
            // Setup event handlers
            this.socket.onopen = this.handleOpen;
            this.socket.onmessage = this.handleMessage;
            this.socket.onclose = this.handleClose;
            this.socket.onerror = this.handleError;
            
            // Wait for connection with timeout
            await this.waitForConnection();
            
        } catch (error) {
            console.error('❌ WebSocket connection failed:', error);
            this.lastError = error;
            this.setState(ConnectionState.FAILED);
            this.scheduleReconnect();
            throw error;
        }
    }

    /**
     * Wait for WebSocket connection to establish
     * @private
     * @returns {Promise<void>}
     */
    waitForConnection() {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                if (this.socket) {
                    this.socket.close();
                }
                reject(new Error('WebSocket connection timeout'));
            }, this.config.messageTimeout);
            
            const checkConnection = () => {
                if (this.state === ConnectionState.CONNECTED) {
                    clearTimeout(timeout);
                    resolve();
                } else if (this.state === ConnectionState.FAILED) {
                    clearTimeout(timeout);
                    reject(this.lastError || new Error('WebSocket connection failed'));
                } else {
                    setTimeout(checkConnection, 100);
                }
            };
            
            checkConnection();
        });
    }

    /**
     * Disconnect from WebSocket server
     * @param {boolean} preventReconnect - Prevent automatic reconnection
     */
    disconnect(preventReconnect = true) {
        console.log('🔄 Disconnecting WebSocket...');
        
        if (preventReconnect) {
            this.clearReconnectTimer();
            this.reconnectAttempts = this.config.maxReconnectAttempts; // Prevent reconnection
        }
        
        this.clearHeartbeatTimer();
        
        if (this.socket) {
            this.socket.onopen = null;
            this.socket.onmessage = null;
            this.socket.onclose = null;
            this.socket.onerror = null;
            
            if (this.socket.readyState === WebSocket.OPEN) {
                this.socket.close(1000, 'Client disconnect');
            }
            
            this.socket = null;
        }
        
        this.setState(ConnectionState.DISCONNECTED);
        this.messageQueue = [];
        this.pendingMessages.clear();
        
        console.log('✅ WebSocket disconnected');
    }

    /**
     * Handle WebSocket open event
     * @private
     */
    handleOpen() {
        const connectionTime = Date.now() - this.connectionStartTime;
        console.log(`✅ WebSocket connected in ${connectionTime}ms`);
        
        this.setState(ConnectionState.CONNECTED);
        this.reconnectAttempts = 0;
        this.lastError = null;
        
        // Start heartbeat
        this.startHeartbeat();
        
        // Process queued messages
        this.processMessageQueue();
        
        // Resubscribe to topics if needed
        if (this.autoResubscribe && this.subscriptions.size > 0) {
            this.resubscribeAll();
        }
        
        // Emit connected event
        this.emit('connected', true);
    }

    /**
     * Handle incoming WebSocket message
     * @private
     * @param {MessageEvent} event - WebSocket message event
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 WebSocket message received:', data.type || 'unknown');
            
            // Handle heartbeat response
            if (data.type === MessageType.HEARTBEAT) {
                this.lastHeartbeat = Date.now();
                return;
            }
            
            // Handle message response (for pending messages)
            if (data.messageId && this.pendingMessages.has(data.messageId)) {
                const { resolve } = this.pendingMessages.get(data.messageId);
                this.pendingMessages.delete(data.messageId);
                resolve(data);
                return;
            }
            
            // Route message to appropriate handlers
            this.routeMessage(data);
            
        } catch (error) {
            console.error('❌ Failed to process WebSocket message:', error, event.data);
            this.emit('error', error);
        }
    }

    /**
     * Handle WebSocket close event
     * @private
     * @param {CloseEvent} event - WebSocket close event
     */
    handleClose(event) {
        console.log(`🔌 WebSocket closed: ${event.code} - ${event.reason}`);
        
        this.clearHeartbeatTimer();
        this.socket = null;
        
        // Determine if we should reconnect
        if (this.reconnectAttempts < this.config.maxReconnectAttempts && event.code !== 1000) {
            this.setState(ConnectionState.RECONNECTING);
            this.scheduleReconnect();
        } else {
            this.setState(ConnectionState.DISCONNECTED);
            this.emit('disconnected', false);
        }
    }

    /**
     * Handle WebSocket error event
     * @private
     * @param {Event} event - WebSocket error event
     */
    handleError(event) {
        console.error('❌ WebSocket error:', event);
        this.lastError = new Error(`WebSocket error: ${event.type}`);
        this.emit('error', this.lastError);
    }

    /**
     * Schedule automatic reconnection
     * @private
     */
    scheduleReconnect() {
        this.clearReconnectTimer();
        
        if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            this.setState(ConnectionState.FAILED);
            this.emit('disconnected', false);
            return;
        }
        
        this.reconnectAttempts++;
        const delay = Math.min(
            this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
            30000 // Max 30 seconds
        );
        
        console.log(`⏳ Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`);
        
        this.reconnectTimer = setTimeout(() => {
            this.totalReconnects++;
            this.connect().catch(error => {
                console.warn('Reconnection attempt failed:', error);
            });
        }, delay);
    }

    /**
     * Clear reconnection timer
     * @private
     */
    clearReconnectTimer() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }

    /**
     * Start heartbeat mechanism
     * @private
     */
    startHeartbeat() {
        this.clearHeartbeatTimer();
        this.lastHeartbeat = Date.now();
        
        this.heartbeatTimer = setInterval(() => {
            if (this.state === ConnectionState.CONNECTED) {
                this.sendMessage({
                    type: MessageType.HEARTBEAT,
                    timestamp: Date.now()
                });
                
                // Check for missed heartbeats
                const timeSinceHeartbeat = Date.now() - this.lastHeartbeat;
                if (timeSinceHeartbeat > this.config.heartbeatInterval * 2) {
                    console.warn('⚠️ Heartbeat timeout detected, reconnecting...');
                    this.socket?.close(1001, 'Heartbeat timeout');
                }
            }
        }, this.config.heartbeatInterval);
    }

    /**
     * Clear heartbeat timer
     * @private
     */
    clearHeartbeatTimer() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * Set connection state and emit events
     * @private
     * @param {string} newState - New connection state
     */
    setState(newState) {
        if (this.state !== newState) {
            const oldState = this.state;
            this.state = newState;
            console.log(`🔄 WebSocket state changed: ${oldState} → ${newState}`);
            this.emit('stateChange', { from: oldState, to: newState });
        }
    }

    /**
     * Route incoming message to appropriate handlers
     * @private
     * @param {Object} data - Message data
     */
    routeMessage(data) {
        const { type, payload, timestamp } = data;
        
        switch (type) {
            case MessageType.HARDWARE_STATUS:
                this.emit('hardwareStatus', payload);
                break;
                
            case MessageType.HARDWARE_UPDATE:
                this.emit('hardwareUpdate', payload);
                break;
                
            case MessageType.DIGITAL_IO_UPDATE:
                this.emit('digitalIoUpdate', payload);
                break;
                
            case MessageType.TEST_STATUS:
                this.emit('testStatus', payload);
                break;
                
            case MessageType.TEST_PROGRESS:
                this.emit('testProgress', payload);
                break;
                
            case MessageType.TEST_DATA:
                this.emit('testData', payload);
                break;
                
            case MessageType.TEST_LOG:
                this.emit('testLog', payload);
                break;
                
            case MessageType.SYSTEM_STATUS:
                this.emit('systemStatus', payload);
                break;
                
            case MessageType.ERROR:
                this.emit('error', new Error(payload.message || 'WebSocket error'));
                break;
                
            case MessageType.EMERGENCY_STOP:
                this.emit('emergencyStop', payload);
                break;
                
            default:
                console.warn(`Unknown message type: ${type}`);
                this.emit('message', data);
        }
        
        // Emit generic message event
        this.emit('data', data);
    }

    /**
     * Send message through WebSocket
     * @param {Object} message - Message to send
     * @param {boolean} expectResponse - Whether to expect a response
     * @returns {Promise<Object|void>} Response if expected
     */
    async sendMessage(message, expectResponse = false) {
        // Add message metadata
        const messageWithMeta = {
            ...message,
            messageId: expectResponse ? ++this.messageId : undefined,
            timestamp: Date.now()
        };
        
        // If not connected, queue the message
        if (this.state !== ConnectionState.CONNECTED) {
            if (expectResponse) {
                throw new Error('Cannot send message requiring response while disconnected');
            }
            
            console.log('📤 Queuing message (not connected):', message.type);
            this.messageQueue.push(messageWithMeta);
            return;
        }
        
        try {
            console.log('📤 Sending WebSocket message:', message.type);
            const messageString = JSON.stringify(messageWithMeta);
            this.socket.send(messageString);
            
            // Handle response expectation
            if (expectResponse) {
                return new Promise((resolve, reject) => {
                    // Store pending message
                    this.pendingMessages.set(messageWithMeta.messageId, { resolve, reject });
                    
                    // Set timeout for response
                    setTimeout(() => {
                        if (this.pendingMessages.has(messageWithMeta.messageId)) {
                            this.pendingMessages.delete(messageWithMeta.messageId);
                            reject(new Error('Message response timeout'));
                        }
                    }, this.config.messageTimeout);
                });
            }
            
        } catch (error) {
            console.error('❌ Failed to send WebSocket message:', error);
            throw error;
        }
    }

    /**
     * Process queued messages
     * @private
     */
    processMessageQueue() {
        if (this.messageQueue.length > 0) {
            console.log(`📤 Processing ${this.messageQueue.length} queued messages`);
            
            const messages = [...this.messageQueue];
            this.messageQueue = [];
            
            messages.forEach(message => {
                this.sendMessage(message).catch(error => {
                    console.warn('Failed to send queued message:', error);
                });
            });
        }
    }

    /**
     * Subscribe to a topic for real-time updates
     * @param {string} topic - Topic to subscribe to
     * @param {Object} options - Subscription options
     * @returns {Promise<void>}
     */
    async subscribe(topic, options = {}) {
        console.log(`📢 Subscribing to topic: ${topic}`);
        
        this.subscriptions.add(topic);
        
        await this.sendMessage({
            type: MessageType.SUBSCRIBE,
            payload: {
                topic,
                options
            }
        });
    }

    /**
     * Unsubscribe from a topic
     * @param {string} topic - Topic to unsubscribe from
     * @returns {Promise<void>}
     */
    async unsubscribe(topic) {
        console.log(`📢 Unsubscribing from topic: ${topic}`);
        
        this.subscriptions.delete(topic);
        
        await this.sendMessage({
            type: MessageType.UNSUBSCRIBE,
            payload: { topic }
        });
    }

    /**
     * Resubscribe to all topics
     * @private
     */
    async resubscribeAll() {
        console.log('📢 Resubscribing to all topics...');
        
        for (const topic of this.subscriptions) {
            try {
                await this.sendMessage({
                    type: MessageType.SUBSCRIBE,
                    payload: { topic }
                });
            } catch (error) {
                console.warn(`Failed to resubscribe to ${topic}:`, error);
            }
        }
    }

    /**
     * Send emergency stop command
     * @returns {Promise<void>}
     */
    async sendEmergencyStop() {
        console.log('🚨 Sending emergency stop command');
        
        await this.sendMessage({
            type: MessageType.EMERGENCY_STOP,
            payload: {
                timestamp: Date.now(),
                source: 'web_interface'
            }
        });
    }

    // =========================
    // Event System
    // =========================

    /**
     * Register event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler function
     */
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
        console.log(`📡 Event handler registered for: ${event}`);
    }

    /**
     * Unregister event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler function to remove
     */
    off(event, handler) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index !== -1) {
                handlers.splice(index, 1);
                console.log(`📡 Event handler removed for: ${event}`);
            }
        }
    }

    /**
     * Register one-time event handler
     * @param {string} event - Event name
     * @param {Function} handler - Event handler function
     */
    once(event, handler) {
        const onceHandler = (data) => {
            handler(data);
            this.off(event, onceHandler);
        };
        this.on(event, onceHandler);
    }

    /**
     * Emit event to all registered handlers
     * @private
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    emit(event, data) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Event handler error for ${event}:`, error);
                }
            });
        }
    }

    /**
     * Remove all event handlers for an event
     * @param {string} event - Event name
     */
    removeAllListeners(event) {
        if (event) {
            this.eventHandlers.delete(event);
        } else {
            this.eventHandlers.clear();
        }
    }

    // =========================
    // Status and Diagnostics
    // =========================

    /**
     * Get connection status information
     * @returns {Object} Connection status
     */
    getStatus() {
        return {
            state: this.state,
            isConnected: this.state === ConnectionState.CONNECTED,
            reconnectAttempts: this.reconnectAttempts,
            totalReconnects: this.totalReconnects,
            lastError: this.lastError?.message,
            lastHeartbeat: this.lastHeartbeat,
            queuedMessages: this.messageQueue.length,
            pendingMessages: this.pendingMessages.size,
            subscriptions: Array.from(this.subscriptions),
            config: this.config
        };
    }

    /**
     * Get connection statistics
     * @returns {Object} Connection statistics
     */
    getStats() {
        const now = Date.now();
        const uptime = this.connectionStartTime ? now - this.connectionStartTime : 0;
        
        return {
            uptime,
            totalReconnects: this.totalReconnects,
            averageReconnectInterval: this.totalReconnects > 0 ? uptime / this.totalReconnects : 0,
            messagesQueued: this.messageQueue.length,
            messagesPending: this.pendingMessages.size,
            subscriptionCount: this.subscriptions.size,
            lastHeartbeatAge: this.lastHeartbeat ? now - this.lastHeartbeat : null
        };
    }

    /**
     * Test connection health
     * @returns {Promise<boolean>} True if connection is healthy
     */
    async testConnection() {
        if (this.state !== ConnectionState.CONNECTED) {
            return false;
        }
        
        try {
            await this.sendMessage({
                type: MessageType.HEARTBEAT,
                payload: { test: true }
            }, true);
            
            return true;
        } catch (error) {
            console.warn('Connection health test failed:', error);
            return false;
        }
    }

    /**
     * Force reconnection
     * @returns {Promise<void>}
     */
    async forceReconnect() {
        console.log('🔄 Forcing WebSocket reconnection...');
        
        if (this.socket) {
            this.socket.close(1000, 'Force reconnect');
        }
        
        this.reconnectAttempts = 0;
        await this.connect();
    }
}

// Export message types and connection states for use by other modules
export { MessageType, ConnectionState };

console.log('📝 WebSocket Manager service loaded successfully');