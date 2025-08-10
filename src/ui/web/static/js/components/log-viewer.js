/**
 * Real-Time Log Viewer Component - WF EOL Tester Web Interface
 * 
 * This component provides comprehensive real-time log viewing capabilities including:
 * - WebSocket integration for live log streaming
 * - Color-coded severity levels with visual indicators
 * - Auto-scrolling with manual scroll lock functionality
 * - Search and filter functionality by level, timestamp, and content
 * - Log export in multiple formats (txt, json, csv)
 * - Virtual scrolling for large log volumes
 * - Message buffering and batching for smooth display
 * - Session management (save, load, clear logs)
 * - Performance optimizations with configurable update rates
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

import { LogFormatter } from '../utils/log-formatter.js';

/**
 * Log severity levels with display properties
 */
const LogLevel = {
    DEBUG: { name: 'DEBUG', priority: 0, color: '#9aa0a6', icon: '🔍' },
    INFO: { name: 'INFO', priority: 1, color: '#4285f4', icon: 'ℹ️' },
    WARNING: { name: 'WARNING', priority: 2, color: '#fbbc04', icon: '⚠️' },
    ERROR: { name: 'ERROR', priority: 3, color: '#ea4335', icon: '❌' },
    CRITICAL: { name: 'CRITICAL', priority: 4, color: '#d32f2f', icon: '🚨' }
};

/**
 * Log source types with color coding
 */
const LogSource = {
    HARDWARE: { name: 'Hardware', color: '#34a853', abbrev: 'HW' },
    TEST: { name: 'Test', color: '#1976d2', abbrev: 'TEST' },
    SYSTEM: { name: 'System', color: '#7b1fa2', abbrev: 'SYS' },
    API: { name: 'API', color: '#ff6d00', abbrev: 'API' },
    WEBSOCKET: { name: 'WebSocket', color: '#0288d1', abbrev: 'WS' },
    MCU: { name: 'MCU', color: '#f57c00', abbrev: 'MCU' },
    ROBOT: { name: 'Robot', color: '#388e3c', abbrev: 'ROB' },
    USER: { name: 'User', color: '#5f6368', abbrev: 'USR' }
};

/**
 * Export formats with configuration
 */
const ExportFormat = {
    TXT: { name: 'Plain Text', extension: 'txt', mimeType: 'text/plain' },
    JSON: { name: 'JSON', extension: 'json', mimeType: 'application/json' },
    CSV: { name: 'CSV', extension: 'csv', mimeType: 'text/csv' }
};

/**
 * Virtual scrolling configuration
 */
const VIRTUAL_SCROLL_CONFIG = {
    itemHeight: 40, // Height of each log entry in pixels
    bufferSize: 10, // Number of extra items to render outside viewport
    batchSize: 50,  // Number of items to render in each batch
    updateInterval: 16 // Update interval in milliseconds (60fps)
};

/**
 * Real-Time Log Viewer Component
 * 
 * Provides comprehensive log viewing with real-time updates, filtering,
 * virtual scrolling, and export capabilities.
 */
export class LogViewerComponent {
    /**
     * Initialize log viewer component
     * @param {HTMLElement} container - Container element for the log viewer
     * @param {WebSocketManager} websocketManager - WebSocket manager instance
     * @param {Object} config - Configuration options
     */
    constructor(container, websocketManager, config = {}) {
        console.log('📋 Initializing Log Viewer Component...');
        
        // Core dependencies
        this.container = container;
        this.websocketManager = websocketManager;
        this.formatter = new LogFormatter();
        
        // Configuration
        this.config = {
            maxMessages: 10000,
            batchSize: 20,
            updateInterval: 100,
            autoScroll: true,
            showTimestamps: true,
            showSources: true,
            showIcons: true,
            enableVirtualScrolling: true,
            saveToLocalStorage: true,
            storageKey: 'wf-eol-log-viewer',
            ...config
        };
        
        // State management
        this.messages = [];
        this.filteredMessages = [];
        this.isConnected = false;
        this.isPaused = false;
        this.isScrollLocked = false;
        this.isFullscreen = false;
        this.sessionId = this.generateSessionId();
        
        // Filter state
        this.filters = {
            level: 'ALL',
            source: 'ALL',
            search: '',
            timeRange: 'ALL',
            startTime: null,
            endTime: null
        };
        
        // Virtual scrolling state
        this.virtualScroll = {
            scrollTop: 0,
            viewportHeight: 0,
            totalHeight: 0,
            startIndex: 0,
            endIndex: 0,
            renderCache: new Map()
        };
        
        // Performance monitoring
        this.stats = {
            totalMessages: 0,
            errorCount: 0,
            warningCount: 0,
            messagesPerSecond: 0,
            lastUpdate: Date.now(),
            messageTimestamps: []
        };
        
        // Message buffer for batching
        this.messageBuffer = [];
        this.bufferTimer = null;
        
        // DOM elements
        this.elements = {};
        
        // Event handlers
        this.boundHandlers = {
            onLogMessage: this.handleLogMessage.bind(this),
            onConnectionChange: this.handleConnectionChange.bind(this),
            onScroll: this.throttle(this.handleScroll.bind(this), 16),
            onResize: this.throttle(this.handleResize.bind(this), 100)
        };
        
        // Initialize component
        this.init();
        
        console.log('✅ Log Viewer Component initialized');
    }
    
    /**
     * Initialize the component
     * @private
     */
    async init() {
        try {
            // Create DOM structure
            this.createDOM();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup WebSocket subscriptions
            this.setupWebSocketSubscriptions();
            
            // Setup virtual scrolling
            if (this.config.enableVirtualScrolling) {
                this.setupVirtualScrolling();
            }
            
            // Load saved session data
            if (this.config.saveToLocalStorage) {
                this.loadSessionData();
            }
            
            // Start performance monitoring
            this.startPerformanceMonitoring();
            
            console.log('✅ Log viewer initialization complete');
            
        } catch (error) {
            console.error('❌ Log viewer initialization failed:', error);
            this.showError('Failed to initialize log viewer', error);
        }
    }
    
    /**
     * Create DOM structure
     * @private
     */
    createDOM() {
        this.container.className = 'log-viewer';
        this.container.innerHTML = `
            <div class="log-viewer__header">
                <div class="log-viewer__controls">
                    <div class="log-viewer__control-group">
                        <button class="log-viewer__btn log-viewer__btn--icon" id="log-connect-btn" title="Connect/Disconnect">
                            <span class="log-viewer__connection-indicator"></span>
                            <span class="log-viewer__btn-text">Connect</span>
                        </button>
                        
                        <button class="log-viewer__btn log-viewer__btn--icon" id="log-pause-btn" title="Pause/Resume">
                            <span class="log-viewer__icon">⏸️</span>
                            <span class="log-viewer__btn-text">Pause</span>
                        </button>
                        
                        <button class="log-viewer__btn log-viewer__btn--icon" id="log-clear-btn" title="Clear Logs">
                            <span class="log-viewer__icon">🗑️</span>
                            <span class="log-viewer__btn-text">Clear</span>
                        </button>
                    </div>
                    
                    <div class="log-viewer__control-group">
                        <button class="log-viewer__btn log-viewer__btn--icon" id="log-scroll-lock-btn" title="Toggle Auto-scroll">
                            <span class="log-viewer__icon">📌</span>
                            <span class="log-viewer__btn-text">Lock Scroll</span>
                        </button>
                        
                        <button class="log-viewer__btn log-viewer__btn--icon" id="log-fullscreen-btn" title="Toggle Fullscreen">
                            <span class="log-viewer__icon">⛶</span>
                            <span class="log-viewer__btn-text">Fullscreen</span>
                        </button>
                    </div>
                    
                    <div class="log-viewer__control-group">
                        <div class="log-viewer__dropdown">
                            <button class="log-viewer__btn log-viewer__btn--dropdown" id="log-export-btn">
                                <span class="log-viewer__icon">💾</span>
                                <span class="log-viewer__btn-text">Export</span>
                                <span class="log-viewer__dropdown-arrow">▼</span>
                            </button>
                            <div class="log-viewer__dropdown-menu" id="log-export-menu">
                                <button class="log-viewer__dropdown-item" data-format="txt">
                                    <span class="log-viewer__icon">📄</span>
                                    Plain Text (.txt)
                                </button>
                                <button class="log-viewer__dropdown-item" data-format="json">
                                    <span class="log-viewer__icon">📋</span>
                                    JSON (.json)
                                </button>
                                <button class="log-viewer__dropdown-item" data-format="csv">
                                    <span class="log-viewer__icon">📊</span>
                                    CSV (.csv)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="log-viewer__filters">
                    <div class="log-viewer__filter-group">
                        <label class="log-viewer__filter-label">Level:</label>
                        <select class="log-viewer__filter-select" id="log-level-filter">
                            <option value="ALL">All Levels</option>
                            <option value="DEBUG">Debug</option>
                            <option value="INFO">Info</option>
                            <option value="WARNING">Warning</option>
                            <option value="ERROR">Error</option>
                            <option value="CRITICAL">Critical</option>
                        </select>
                    </div>
                    
                    <div class="log-viewer__filter-group">
                        <label class="log-viewer__filter-label">Source:</label>
                        <select class="log-viewer__filter-select" id="log-source-filter">
                            <option value="ALL">All Sources</option>
                            <option value="HARDWARE">Hardware</option>
                            <option value="TEST">Test</option>
                            <option value="SYSTEM">System</option>
                            <option value="API">API</option>
                            <option value="WEBSOCKET">WebSocket</option>
                            <option value="MCU">MCU</option>
                            <option value="ROBOT">Robot</option>
                            <option value="USER">User</option>
                        </select>
                    </div>
                    
                    <div class="log-viewer__filter-group log-viewer__filter-group--search">
                        <label class="log-viewer__filter-label">Search:</label>
                        <div class="log-viewer__search-container">
                            <input type="text" class="log-viewer__search-input" id="log-search-input" 
                                   placeholder="Search messages..." autocomplete="off">
                            <button class="log-viewer__search-clear" id="log-search-clear">×</button>
                        </div>
                    </div>
                    
                    <div class="log-viewer__filter-group">
                        <label class="log-viewer__filter-label">Time:</label>
                        <select class="log-viewer__filter-select" id="log-time-filter">
                            <option value="ALL">All Time</option>
                            <option value="LAST_MINUTE">Last Minute</option>
                            <option value="LAST_5_MINUTES">Last 5 Minutes</option>
                            <option value="LAST_HOUR">Last Hour</option>
                            <option value="TODAY">Today</option>
                            <option value="CUSTOM">Custom Range</option>
                        </select>
                    </div>
                </div>
                
                <div class="log-viewer__stats">
                    <div class="log-viewer__stat">
                        <span class="log-viewer__stat-label">Total:</span>
                        <span class="log-viewer__stat-value" id="log-total-count">0</span>
                    </div>
                    <div class="log-viewer__stat log-viewer__stat--error">
                        <span class="log-viewer__stat-label">Errors:</span>
                        <span class="log-viewer__stat-value" id="log-error-count">0</span>
                    </div>
                    <div class="log-viewer__stat log-viewer__stat--warning">
                        <span class="log-viewer__stat-label">Warnings:</span>
                        <span class="log-viewer__stat-value" id="log-warning-count">0</span>
                    </div>
                    <div class="log-viewer__stat">
                        <span class="log-viewer__stat-label">Rate:</span>
                        <span class="log-viewer__stat-value" id="log-message-rate">0</span>
                        <span class="log-viewer__stat-unit">msg/s</span>
                    </div>
                </div>
            </div>
            
            <div class="log-viewer__content" id="log-content">
                <div class="log-viewer__viewport" id="log-viewport">
                    <div class="log-viewer__virtual-container" id="log-virtual-container">
                        <div class="log-viewer__messages" id="log-messages"></div>
                    </div>
                </div>
            </div>
            
            <div class="log-viewer__footer">
                <div class="log-viewer__session-info">
                    <span class="log-viewer__session-label">Session:</span>
                    <span class="log-viewer__session-id">${this.sessionId}</span>
                </div>
                
                <div class="log-viewer__connection-status" id="log-connection-status">
                    <span class="log-viewer__connection-dot"></span>
                    <span class="log-viewer__connection-text">Disconnected</span>
                </div>
            </div>
        `;
        
        // Cache DOM elements
        this.elements = {
            header: this.container.querySelector('.log-viewer__header'),
            controls: this.container.querySelector('.log-viewer__controls'),
            filters: this.container.querySelector('.log-viewer__filters'),
            stats: this.container.querySelector('.log-viewer__stats'),
            content: this.container.querySelector('.log-viewer__content'),
            viewport: this.container.querySelector('.log-viewer__viewport'),
            virtualContainer: this.container.querySelector('.log-viewer__virtual-container'),
            messages: this.container.querySelector('.log-viewer__messages'),
            footer: this.container.querySelector('.log-viewer__footer'),
            
            // Controls
            connectBtn: this.container.querySelector('#log-connect-btn'),
            pauseBtn: this.container.querySelector('#log-pause-btn'),
            clearBtn: this.container.querySelector('#log-clear-btn'),
            scrollLockBtn: this.container.querySelector('#log-scroll-lock-btn'),
            fullscreenBtn: this.container.querySelector('#log-fullscreen-btn'),
            exportBtn: this.container.querySelector('#log-export-btn'),
            exportMenu: this.container.querySelector('#log-export-menu'),
            
            // Filters
            levelFilter: this.container.querySelector('#log-level-filter'),
            sourceFilter: this.container.querySelector('#log-source-filter'),
            searchInput: this.container.querySelector('#log-search-input'),
            searchClear: this.container.querySelector('#log-search-clear'),
            timeFilter: this.container.querySelector('#log-time-filter'),
            
            // Stats
            totalCount: this.container.querySelector('#log-total-count'),
            errorCount: this.container.querySelector('#log-error-count'),
            warningCount: this.container.querySelector('#log-warning-count'),
            messageRate: this.container.querySelector('#log-message-rate'),
            
            // Status
            connectionStatus: this.container.querySelector('#log-connection-status'),
            connectionIndicator: this.container.querySelector('.log-viewer__connection-indicator'),
            connectionText: this.container.querySelector('.log-viewer__connection-text'),
            connectionDot: this.container.querySelector('.log-viewer__connection-dot')
        };
        
        console.log('✅ DOM structure created');
    }
    
    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Control buttons
        this.elements.connectBtn.addEventListener('click', this.handleConnectToggle.bind(this));
        this.elements.pauseBtn.addEventListener('click', this.handlePauseToggle.bind(this));
        this.elements.clearBtn.addEventListener('click', this.handleClear.bind(this));
        this.elements.scrollLockBtn.addEventListener('click', this.handleScrollLockToggle.bind(this));
        this.elements.fullscreenBtn.addEventListener('click', this.handleFullscreenToggle.bind(this));
        
        // Export functionality
        this.elements.exportBtn.addEventListener('click', this.handleExportToggle.bind(this));
        this.elements.exportMenu.addEventListener('click', this.handleExport.bind(this));
        
        // Filter controls
        this.elements.levelFilter.addEventListener('change', this.handleFilterChange.bind(this));
        this.elements.sourceFilter.addEventListener('change', this.handleFilterChange.bind(this));
        this.elements.timeFilter.addEventListener('change', this.handleFilterChange.bind(this));
        
        // Search functionality
        this.elements.searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        this.elements.searchClear.addEventListener('click', this.handleSearchClear.bind(this));
        
        // Scrolling and viewport
        this.elements.viewport.addEventListener('scroll', this.boundHandlers.onScroll);
        window.addEventListener('resize', this.boundHandlers.onResize);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeydown.bind(this));
        
        // Click outside to close dropdowns
        document.addEventListener('click', this.handleDocumentClick.bind(this));
        
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
            // Subscribe to log messages
            this.websocketManager.on('testLog', this.boundHandlers.onLogMessage);
            this.websocketManager.on('systemLog', this.boundHandlers.onLogMessage);
            this.websocketManager.on('hardwareLog', this.boundHandlers.onLogMessage);
            
            // Subscribe to connection state changes
            this.websocketManager.on('stateChange', this.boundHandlers.onConnectionChange);
            this.websocketManager.on('connected', () => this.updateConnectionStatus(true));
            this.websocketManager.on('disconnected', () => this.updateConnectionStatus(false));
            
            // Initialize connection status
            this.updateConnectionStatus(this.websocketManager.getStatus().isConnected);
            
            console.log('✅ WebSocket subscriptions setup complete');
            
        } catch (error) {
            console.error('❌ Failed to setup WebSocket subscriptions:', error);
        }
    }
    
    /**
     * Setup virtual scrolling
     * @private
     */
    setupVirtualScrolling() {
        // Calculate viewport dimensions
        this.updateVirtualScrollDimensions();
        
        // Set initial virtual container height
        this.updateVirtualContainerHeight();
        
        console.log('✅ Virtual scrolling setup complete');
    }
    
    /**
     * Handle incoming log message
     * @private
     * @param {Object} logData - Log message data
     */
    handleLogMessage(logData) {
        if (this.isPaused) return;
        
        try {
            const message = this.normalizeLogMessage(logData);
            
            // Add to buffer for batching
            this.messageBuffer.push(message);
            
            // Process buffer if it reaches batch size or after timeout
            if (this.messageBuffer.length >= this.config.batchSize) {
                this.processBatch();
            } else if (!this.bufferTimer) {
                this.bufferTimer = setTimeout(() => {
                    this.processBatch();
                }, this.config.updateInterval);
            }
            
        } catch (error) {
            console.error('❌ Failed to handle log message:', error, logData);
        }
    }
    
    /**
     * Normalize incoming log message to standard format
     * @private
     * @param {Object} logData - Raw log data
     * @returns {Object} Normalized message
     */
    normalizeLogMessage(logData) {
        const timestamp = logData.timestamp || Date.now();
        const level = this.normalizeLogLevel(logData.level || logData.severity || 'INFO');
        const source = this.normalizeLogSource(logData.source || logData.component || 'SYSTEM');
        const message = logData.message || logData.text || String(logData);
        
        return {
            id: this.generateMessageId(),
            timestamp,
            level,
            source,
            message,
            details: logData.details || null,
            metadata: {
                session: this.sessionId,
                sequence: this.stats.totalMessages + this.messageBuffer.length,
                ...logData.metadata
            }
        };
    }
    
    /**
     * Normalize log level
     * @private
     * @param {string} level - Raw log level
     * @returns {string} Normalized level
     */
    normalizeLogLevel(level) {
        const levelUpper = String(level).toUpperCase();
        const levelMap = {
            'TRACE': 'DEBUG',
            'VERBOSE': 'DEBUG',
            'WARN': 'WARNING',
            'ERR': 'ERROR',
            'FATAL': 'CRITICAL',
            'CRIT': 'CRITICAL'
        };
        
        return levelMap[levelUpper] || (LogLevel[levelUpper] ? levelUpper : 'INFO');
    }
    
    /**
     * Normalize log source
     * @private
     * @param {string} source - Raw log source
     * @returns {string} Normalized source
     */
    normalizeLogSource(source) {
        const sourceUpper = String(source).toUpperCase();
        const sourceMap = {
            'HW': 'HARDWARE',
            'HWR': 'HARDWARE',
            'SYS': 'SYSTEM',
            'SOCKET': 'WEBSOCKET',
            'WS': 'WEBSOCKET',
            'BOT': 'ROBOT',
            'ROB': 'ROBOT',
            'MICROCONTROLLER': 'MCU',
            'CONTROLLER': 'MCU'
        };
        
        return sourceMap[sourceUpper] || (LogSource[sourceUpper] ? sourceUpper : 'SYSTEM');
    }
    
    /**
     * Process message buffer batch
     * @private
     */
    processBatch() {
        if (this.messageBuffer.length === 0) return;
        
        const batch = [...this.messageBuffer];
        this.messageBuffer = [];
        
        // Clear buffer timer
        if (this.bufferTimer) {
            clearTimeout(this.bufferTimer);
            this.bufferTimer = null;
        }
        
        // Add messages to main array
        this.messages.push(...batch);
        
        // Update statistics
        this.updateStats(batch);
        
        // Trim messages if over limit
        if (this.messages.length > this.config.maxMessages) {
            const excess = this.messages.length - this.config.maxMessages;
            this.messages.splice(0, excess);
        }
        
        // Apply filters and update display
        this.applyFilters();
        this.updateDisplay();
        
        // Auto-scroll if enabled and not locked
        if (this.config.autoScroll && !this.isScrollLocked) {
            this.scrollToBottom();
        }
        
        // Save to local storage
        if (this.config.saveToLocalStorage) {
            this.saveSessionData();
        }
    }
    
    /**
     * Update statistics
     * @private
     * @param {Array} batch - Batch of messages
     */
    updateStats(batch) {
        const now = Date.now();
        
        // Update counts
        this.stats.totalMessages += batch.length;
        
        batch.forEach(message => {
            if (message.level === 'ERROR' || message.level === 'CRITICAL') {
                this.stats.errorCount++;
            } else if (message.level === 'WARNING') {
                this.stats.warningCount++;
            }
        });
        
        // Update message rate
        this.stats.messageTimestamps.push(...batch.map(m => m.timestamp));
        
        // Keep only timestamps from last minute for rate calculation
        const oneMinuteAgo = now - 60000;
        this.stats.messageTimestamps = this.stats.messageTimestamps.filter(ts => ts > oneMinuteAgo);
        this.stats.messagesPerSecond = this.stats.messageTimestamps.length / 60;
        
        this.stats.lastUpdate = now;
        
        // Update display
        this.updateStatsDisplay();
    }
    
    /**
     * Apply current filters
     * @private
     */
    applyFilters() {
        let filtered = [...this.messages];
        
        // Apply level filter
        if (this.filters.level !== 'ALL') {
            filtered = filtered.filter(msg => msg.level === this.filters.level);
        }
        
        // Apply source filter
        if (this.filters.source !== 'ALL') {
            filtered = filtered.filter(msg => msg.source === this.filters.source);
        }
        
        // Apply search filter
        if (this.filters.search) {
            const searchLower = this.filters.search.toLowerCase();
            filtered = filtered.filter(msg => 
                msg.message.toLowerCase().includes(searchLower) ||
                msg.source.toLowerCase().includes(searchLower) ||
                msg.level.toLowerCase().includes(searchLower)
            );
        }
        
        // Apply time range filter
        if (this.filters.timeRange !== 'ALL') {
            const now = Date.now();
            let cutoffTime;
            
            switch (this.filters.timeRange) {
                case 'LAST_MINUTE':
                    cutoffTime = now - 60000;
                    break;
                case 'LAST_5_MINUTES':
                    cutoffTime = now - 300000;
                    break;
                case 'LAST_HOUR':
                    cutoffTime = now - 3600000;
                    break;
                case 'TODAY':
                    cutoffTime = new Date().setHours(0, 0, 0, 0);
                    break;
                case 'CUSTOM':
                    if (this.filters.startTime) cutoffTime = this.filters.startTime;
                    break;
            }
            
            if (cutoffTime) {
                filtered = filtered.filter(msg => msg.timestamp >= cutoffTime);
            }
            
            if (this.filters.timeRange === 'CUSTOM' && this.filters.endTime) {
                filtered = filtered.filter(msg => msg.timestamp <= this.filters.endTime);
            }
        }
        
        this.filteredMessages = filtered;
    }
    
    /**
     * Update display
     * @private
     */
    updateDisplay() {
        if (this.config.enableVirtualScrolling) {
            this.updateVirtualScrollDisplay();
        } else {
            this.updateDirectDisplay();
        }
    }
    
    /**
     * Update virtual scroll display
     * @private
     */
    updateVirtualScrollDisplay() {
        this.updateVirtualScrollDimensions();
        this.updateVirtualContainerHeight();
        this.calculateVisibleRange();
        this.renderVisibleMessages();
    }
    
    /**
     * Update direct display (non-virtual scrolling)
     * @private
     */
    updateDirectDisplay() {
        const messagesContainer = this.elements.messages;
        const fragment = document.createDocumentFragment();
        
        // Clear existing messages
        messagesContainer.innerHTML = '';
        
        // Render filtered messages
        this.filteredMessages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            fragment.appendChild(messageElement);
        });
        
        messagesContainer.appendChild(fragment);
    }
    
    /**
     * Create message element
     * @private
     * @param {Object} message - Log message
     * @returns {HTMLElement} Message element
     */
    createMessageElement(message) {
        const messageEl = document.createElement('div');
        messageEl.className = `log-viewer__message log-viewer__message--${message.level.toLowerCase()}`;
        messageEl.setAttribute('data-message-id', message.id);
        
        const levelConfig = LogLevel[message.level] || LogLevel.INFO;
        const sourceConfig = LogSource[message.source] || LogSource.SYSTEM;
        
        const timestamp = this.config.showTimestamps 
            ? this.formatter.formatTimestamp(message.timestamp)
            : '';
        
        const icon = this.config.showIcons ? levelConfig.icon : '';
        const source = this.config.showSources 
            ? `<span class="log-viewer__source" style="color: ${sourceConfig.color}">[${sourceConfig.abbrev}]</span>`
            : '';
        
        messageEl.innerHTML = `
            <div class="log-viewer__message-header">
                <span class="log-viewer__timestamp">${timestamp}</span>
                <span class="log-viewer__level" style="color: ${levelConfig.color}">
                    ${icon} ${levelConfig.name}
                </span>
                ${source}
                ${message.metadata?.sequence ? `<span class="log-viewer__sequence">#${message.metadata.sequence}</span>` : ''}
            </div>
            <div class="log-viewer__message-content">
                <span class="log-viewer__message-text">${this.escapeHtml(message.message)}</span>
                ${message.details ? `<button class="log-viewer__details-toggle">Details</button>` : ''}
            </div>
            ${message.details ? `<div class="log-viewer__message-details" style="display: none;">
                <pre>${this.escapeHtml(JSON.stringify(message.details, null, 2))}</pre>
            </div>` : ''}
        `;
        
        // Add details toggle functionality
        if (message.details) {
            const detailsToggle = messageEl.querySelector('.log-viewer__details-toggle');
            const detailsContainer = messageEl.querySelector('.log-viewer__message-details');
            
            detailsToggle.addEventListener('click', () => {
                const isVisible = detailsContainer.style.display !== 'none';
                detailsContainer.style.display = isVisible ? 'none' : 'block';
                detailsToggle.textContent = isVisible ? 'Details' : 'Hide Details';
            });
        }
        
        return messageEl;
    }
    
    /**
     * Update virtual scroll dimensions
     * @private
     */
    updateVirtualScrollDimensions() {
        const rect = this.elements.viewport.getBoundingClientRect();
        this.virtualScroll.viewportHeight = rect.height;
        this.virtualScroll.scrollTop = this.elements.viewport.scrollTop;
    }
    
    /**
     * Update virtual container height
     * @private
     */
    updateVirtualContainerHeight() {
        this.virtualScroll.totalHeight = this.filteredMessages.length * VIRTUAL_SCROLL_CONFIG.itemHeight;
        this.elements.virtualContainer.style.height = `${this.virtualScroll.totalHeight}px`;
    }
    
    /**
     * Calculate visible range for virtual scrolling
     * @private
     */
    calculateVisibleRange() {
        const { scrollTop, viewportHeight } = this.virtualScroll;
        const { itemHeight, bufferSize } = VIRTUAL_SCROLL_CONFIG;
        
        const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - bufferSize);
        const endIndex = Math.min(
            this.filteredMessages.length - 1,
            Math.floor((scrollTop + viewportHeight) / itemHeight) + bufferSize
        );
        
        this.virtualScroll.startIndex = startIndex;
        this.virtualScroll.endIndex = endIndex;
    }
    
    /**
     * Render visible messages for virtual scrolling
     * @private
     */
    renderVisibleMessages() {
        const { startIndex, endIndex } = this.virtualScroll;
        const { itemHeight } = VIRTUAL_SCROLL_CONFIG;
        
        // Clear messages container
        this.elements.messages.innerHTML = '';
        this.elements.messages.style.paddingTop = `${startIndex * itemHeight}px`;
        this.elements.messages.style.paddingBottom = `${(this.filteredMessages.length - endIndex - 1) * itemHeight}px`;
        
        // Render visible messages
        const fragment = document.createDocumentFragment();
        
        for (let i = startIndex; i <= endIndex; i++) {
            const message = this.filteredMessages[i];
            if (!message) continue;
            
            let messageElement = this.virtualScroll.renderCache.get(message.id);
            
            if (!messageElement) {
                messageElement = this.createMessageElement(message);
                messageElement.style.height = `${itemHeight}px`;
                this.virtualScroll.renderCache.set(message.id, messageElement);
            }
            
            fragment.appendChild(messageElement.cloneNode(true));
        }
        
        this.elements.messages.appendChild(fragment);
        
        // Cleanup render cache if it gets too large
        if (this.virtualScroll.renderCache.size > this.config.maxMessages) {
            const cacheEntries = Array.from(this.virtualScroll.renderCache.keys());
            const toRemove = cacheEntries.slice(0, cacheEntries.length - this.config.maxMessages);
            toRemove.forEach(key => this.virtualScroll.renderCache.delete(key));
        }
    }
    
    /**
     * Update stats display
     * @private
     */
    updateStatsDisplay() {
        this.elements.totalCount.textContent = this.stats.totalMessages.toLocaleString();
        this.elements.errorCount.textContent = this.stats.errorCount.toLocaleString();
        this.elements.warningCount.textContent = this.stats.warningCount.toLocaleString();
        this.elements.messageRate.textContent = this.stats.messagesPerSecond.toFixed(1);
    }
    
    /**
     * Handle connection state change
     * @private
     * @param {Object} stateChange - Connection state change event
     */
    handleConnectionChange(stateChange) {
        this.updateConnectionStatus(stateChange.to === 'connected');
    }
    
    /**
     * Update connection status
     * @private
     * @param {boolean} connected - Connection status
     */
    updateConnectionStatus(connected) {
        this.isConnected = connected;
        
        // Update connection indicator
        this.elements.connectionIndicator.className = 
            `log-viewer__connection-indicator ${connected ? 'log-viewer__connection-indicator--connected' : ''}`;
        
        // Update connection text
        this.elements.connectionText.textContent = connected ? 'Connected' : 'Disconnected';
        this.elements.connectionDot.className = 
            `log-viewer__connection-dot ${connected ? 'log-viewer__connection-dot--connected' : ''}`;
        
        // Update connect button
        const btnText = this.elements.connectBtn.querySelector('.log-viewer__btn-text');
        btnText.textContent = connected ? 'Disconnect' : 'Connect';
        
        // Add connection status message
        if (connected) {
            this.addSystemMessage('Connected to log stream', 'INFO');
        } else {
            this.addSystemMessage('Disconnected from log stream', 'WARNING');
        }
    }
    
    // =========================
    // Event Handlers
    // =========================
    
    /**
     * Handle connect/disconnect toggle
     * @private
     */
    async handleConnectToggle() {
        try {
            if (this.isConnected) {
                await this.websocketManager.disconnect();
            } else {
                await this.websocketManager.connect();
            }
        } catch (error) {
            console.error('❌ Connection toggle failed:', error);
            this.showError('Connection failed', error.message);
        }
    }
    
    /**
     * Handle pause/resume toggle
     * @private
     */
    handlePauseToggle() {
        this.isPaused = !this.isPaused;
        
        const btnText = this.elements.pauseBtn.querySelector('.log-viewer__btn-text');
        const btnIcon = this.elements.pauseBtn.querySelector('.log-viewer__icon');
        
        if (this.isPaused) {
            btnText.textContent = 'Resume';
            btnIcon.textContent = '▶️';
            this.elements.pauseBtn.classList.add('log-viewer__btn--active');
            this.addSystemMessage('Log stream paused', 'INFO');
        } else {
            btnText.textContent = 'Pause';
            btnIcon.textContent = '⏸️';
            this.elements.pauseBtn.classList.remove('log-viewer__btn--active');
            this.addSystemMessage('Log stream resumed', 'INFO');
        }
    }
    
    /**
     * Handle clear logs
     * @private
     */
    handleClear() {
        if (confirm('Are you sure you want to clear all log messages? This action cannot be undone.')) {
            this.messages = [];
            this.filteredMessages = [];
            this.messageBuffer = [];
            
            // Reset statistics
            this.stats.totalMessages = 0;
            this.stats.errorCount = 0;
            this.stats.warningCount = 0;
            this.stats.messageTimestamps = [];
            
            // Clear render cache
            this.virtualScroll.renderCache.clear();
            
            // Update display
            this.updateDisplay();
            this.updateStatsDisplay();
            
            // Clear local storage
            if (this.config.saveToLocalStorage) {
                this.clearSessionData();
            }
            
            this.addSystemMessage('Log cleared', 'INFO');
        }
    }
    
    /**
     * Handle scroll lock toggle
     * @private
     */
    handleScrollLockToggle() {
        this.isScrollLocked = !this.isScrollLocked;
        
        const btnText = this.elements.scrollLockBtn.querySelector('.log-viewer__btn-text');
        const btnIcon = this.elements.scrollLockBtn.querySelector('.log-viewer__icon');
        
        if (this.isScrollLocked) {
            btnText.textContent = 'Unlock Scroll';
            btnIcon.textContent = '🔓';
            this.elements.scrollLockBtn.classList.add('log-viewer__btn--active');
        } else {
            btnText.textContent = 'Lock Scroll';
            btnIcon.textContent = '📌';
            this.elements.scrollLockBtn.classList.remove('log-viewer__btn--active');
            // Auto-scroll to bottom when unlocked
            this.scrollToBottom();
        }
    }
    
    /**
     * Handle fullscreen toggle
     * @private
     */
    handleFullscreenToggle() {
        this.isFullscreen = !this.isFullscreen;
        
        if (this.isFullscreen) {
            this.container.classList.add('log-viewer--fullscreen');
            this.elements.fullscreenBtn.querySelector('.log-viewer__btn-text').textContent = 'Exit Fullscreen';
            this.elements.fullscreenBtn.querySelector('.log-viewer__icon').textContent = '🗗';
        } else {
            this.container.classList.remove('log-viewer--fullscreen');
            this.elements.fullscreenBtn.querySelector('.log-viewer__btn-text').textContent = 'Fullscreen';
            this.elements.fullscreenBtn.querySelector('.log-viewer__icon').textContent = '⛶';
        }
        
        // Update virtual scroll dimensions after fullscreen change
        setTimeout(() => {
            if (this.config.enableVirtualScrolling) {
                this.updateVirtualScrollDimensions();
                this.updateDisplay();
            }
        }, 100);
    }
    
    /**
     * Handle export dropdown toggle
     * @private
     */
    handleExportToggle(event) {
        event.stopPropagation();
        const isOpen = this.elements.exportMenu.classList.contains('log-viewer__dropdown-menu--open');
        
        if (isOpen) {
            this.elements.exportMenu.classList.remove('log-viewer__dropdown-menu--open');
        } else {
            this.elements.exportMenu.classList.add('log-viewer__dropdown-menu--open');
        }
    }
    
    /**
     * Handle export format selection
     * @private
     * @param {Event} event - Click event
     */
    handleExport(event) {
        const format = event.target.closest('[data-format]')?.getAttribute('data-format');
        if (!format) return;
        
        event.stopPropagation();
        this.elements.exportMenu.classList.remove('log-viewer__dropdown-menu--open');
        
        this.exportLogs(format);
    }
    
    /**
     * Handle filter change
     * @private
     */
    handleFilterChange() {
        // Update filter state
        this.filters.level = this.elements.levelFilter.value;
        this.filters.source = this.elements.sourceFilter.value;
        this.filters.timeRange = this.elements.timeFilter.value;
        
        // Apply filters and update display
        this.applyFilters();
        this.updateDisplay();
        
        // Save filter preferences
        this.saveFilterPreferences();
    }
    
    /**
     * Handle search input
     * @private
     */
    handleSearch() {
        this.filters.search = this.elements.searchInput.value.trim();
        
        // Show/hide clear button
        this.elements.searchClear.style.display = this.filters.search ? 'block' : 'none';
        
        // Apply filters and update display
        this.applyFilters();
        this.updateDisplay();
    }
    
    /**
     * Handle search clear
     * @private
     */
    handleSearchClear() {
        this.elements.searchInput.value = '';
        this.filters.search = '';
        this.elements.searchClear.style.display = 'none';
        
        // Apply filters and update display
        this.applyFilters();
        this.updateDisplay();
    }
    
    /**
     * Handle viewport scroll
     * @private
     */
    handleScroll() {
        if (this.config.enableVirtualScrolling) {
            this.updateVirtualScrollDimensions();
            this.calculateVisibleRange();
            this.renderVisibleMessages();
        }
        
        // Auto-detect scroll lock based on user scrolling
        const viewport = this.elements.viewport;
        const isAtBottom = viewport.scrollTop + viewport.clientHeight >= viewport.scrollHeight - 10;
        
        if (isAtBottom && this.isScrollLocked) {
            // User scrolled to bottom, unlock auto-scroll
            this.isScrollLocked = false;
            this.handleScrollLockToggle();
        } else if (!isAtBottom && !this.isScrollLocked && this.config.autoScroll) {
            // User scrolled up, lock auto-scroll
            this.isScrollLocked = true;
            this.handleScrollLockToggle();
        }
    }
    
    /**
     * Handle window resize
     * @private
     */
    handleResize() {
        if (this.config.enableVirtualScrolling) {
            this.updateVirtualScrollDimensions();
            this.updateVirtualContainerHeight();
            this.calculateVisibleRange();
            this.renderVisibleMessages();
        }
    }
    
    /**
     * Handle keyboard shortcuts
     * @private
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeydown(event) {
        // Only handle if log viewer is focused or no specific element is focused
        if (!this.container.contains(event.target) && event.target !== document.body) return;
        
        switch (event.key) {
            case 'Escape':
                if (this.isFullscreen) {
                    this.handleFullscreenToggle();
                }
                break;
            case 'f':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    this.elements.searchInput.focus();
                }
                break;
            case 'l':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    this.handleClear();
                }
                break;
            case ' ':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    this.handlePauseToggle();
                }
                break;
            case 'End':
                event.preventDefault();
                this.scrollToBottom();
                break;
            case 'Home':
                event.preventDefault();
                this.scrollToTop();
                break;
        }
    }
    
    /**
     * Handle document click (for closing dropdowns)
     * @private
     * @param {Event} event - Click event
     */
    handleDocumentClick(event) {
        if (!this.elements.exportBtn.contains(event.target)) {
            this.elements.exportMenu.classList.remove('log-viewer__dropdown-menu--open');
        }
    }
    
    // =========================
    // Public API Methods
    // =========================
    
    /**
     * Add a system message to the log
     * @param {string} message - Message text
     * @param {string} level - Log level
     */
    addSystemMessage(message, level = 'INFO') {
        const systemMessage = {
            id: this.generateMessageId(),
            timestamp: Date.now(),
            level: level,
            source: 'SYSTEM',
            message: message,
            metadata: {
                session: this.sessionId,
                sequence: this.stats.totalMessages,
                system: true
            }
        };
        
        this.messageBuffer.push(systemMessage);
        this.processBatch();
    }
    
    /**
     * Export logs in specified format
     * @param {string} format - Export format (txt, json, csv)
     */
    exportLogs(format) {
        try {
            const exportConfig = ExportFormat[format.toUpperCase()];
            if (!exportConfig) {
                throw new Error(`Unsupported export format: ${format}`);
            }
            
            let content;
            const messages = this.filteredMessages.length > 0 ? this.filteredMessages : this.messages;
            
            switch (format) {
                case 'txt':
                    content = this.formatAsText(messages);
                    break;
                case 'json':
                    content = this.formatAsJSON(messages);
                    break;
                case 'csv':
                    content = this.formatAsCSV(messages);
                    break;
                default:
                    throw new Error(`Unsupported format: ${format}`);
            }
            
            // Create and trigger download
            const blob = new Blob([content], { type: exportConfig.mimeType });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            
            link.href = url;
            link.download = `wf-eol-logs-${this.sessionId}.${exportConfig.extension}`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            URL.revokeObjectURL(url);
            
            this.addSystemMessage(`Logs exported as ${format.toUpperCase()}`, 'INFO');
            
        } catch (error) {
            console.error('❌ Export failed:', error);
            this.showError('Export Failed', error.message);
        }
    }
    
    /**
     * Clear all logs
     */
    clear() {
        this.handleClear();
    }
    
    /**
     * Pause/resume log streaming
     * @param {boolean} [pause] - Optional pause state, toggles if not provided
     */
    pause(pause) {
        if (pause === undefined) {
            this.handlePauseToggle();
        } else if (pause !== this.isPaused) {
            this.handlePauseToggle();
        }
    }
    
    /**
     * Set filters programmatically
     * @param {Object} filters - Filter configuration
     */
    setFilters(filters) {
        if (filters.level) {
            this.filters.level = filters.level;
            this.elements.levelFilter.value = filters.level;
        }
        
        if (filters.source) {
            this.filters.source = filters.source;
            this.elements.sourceFilter.value = filters.source;
        }
        
        if (filters.search !== undefined) {
            this.filters.search = filters.search;
            this.elements.searchInput.value = filters.search;
            this.elements.searchClear.style.display = filters.search ? 'block' : 'none';
        }
        
        if (filters.timeRange) {
            this.filters.timeRange = filters.timeRange;
            this.elements.timeFilter.value = filters.timeRange;
        }
        
        // Apply filters and update display
        this.applyFilters();
        this.updateDisplay();
    }
    
    /**
     * Get current filter state
     * @returns {Object} Current filters
     */
    getFilters() {
        return { ...this.filters };
    }
    
    /**
     * Get log statistics
     * @returns {Object} Log statistics
     */
    getStats() {
        return { ...this.stats };
    }
    
    /**
     * Scroll to bottom of log
     */
    scrollToBottom() {
        const viewport = this.elements.viewport;
        viewport.scrollTop = viewport.scrollHeight;
    }
    
    /**
     * Scroll to top of log
     */
    scrollToTop() {
        this.elements.viewport.scrollTop = 0;
    }
    
    // =========================
    // Format Export Methods
    // =========================
    
    /**
     * Format messages as plain text
     * @private
     * @param {Array} messages - Messages to format
     * @returns {string} Formatted text
     */
    formatAsText(messages) {
        const lines = [`WF EOL Tester Log Export - Session: ${this.sessionId}`, 
                      `Generated: ${new Date().toISOString()}`,
                      `Total Messages: ${messages.length}`,
                      '',
                      ...messages.map(msg => {
                          const timestamp = this.formatter.formatTimestamp(msg.timestamp);
                          const levelConfig = LogLevel[msg.level] || LogLevel.INFO;
                          const sourceConfig = LogSource[msg.source] || LogSource.SYSTEM;
                          
                          return `[${timestamp}] ${levelConfig.name} [${sourceConfig.abbrev}] ${msg.message}`;
                      })];
        
        return lines.join('\n');
    }
    
    /**
     * Format messages as JSON
     * @private
     * @param {Array} messages - Messages to format
     * @returns {string} Formatted JSON
     */
    formatAsJSON(messages) {
        const exportData = {
            session: this.sessionId,
            exported: new Date().toISOString(),
            totalMessages: messages.length,
            filters: this.filters,
            messages: messages.map(msg => ({
                id: msg.id,
                timestamp: msg.timestamp,
                iso_timestamp: new Date(msg.timestamp).toISOString(),
                level: msg.level,
                source: msg.source,
                message: msg.message,
                details: msg.details,
                metadata: msg.metadata
            }))
        };
        
        return JSON.stringify(exportData, null, 2);
    }
    
    /**
     * Format messages as CSV
     * @private
     * @param {Array} messages - Messages to format
     * @returns {string} Formatted CSV
     */
    formatAsCSV(messages) {
        const headers = ['Timestamp', 'ISO_Timestamp', 'Level', 'Source', 'Message', 'Details', 'Sequence'];
        const rows = messages.map(msg => [
            msg.timestamp,
            new Date(msg.timestamp).toISOString(),
            msg.level,
            msg.source,
            `"${msg.message.replace(/"/g, '""')}"`, // Escape quotes in CSV
            msg.details ? `"${JSON.stringify(msg.details).replace(/"/g, '""')}"` : '',
            msg.metadata?.sequence || ''
        ]);
        
        return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    }
    
    // =========================
    // Storage Methods
    // =========================
    
    /**
     * Save session data to local storage
     * @private
     */
    saveSessionData() {
        try {
            const sessionData = {
                sessionId: this.sessionId,
                messages: this.messages.slice(-1000), // Keep last 1000 messages
                filters: this.filters,
                stats: this.stats,
                config: this.config,
                timestamp: Date.now()
            };
            
            localStorage.setItem(this.config.storageKey, JSON.stringify(sessionData));
            
        } catch (error) {
            console.warn('Failed to save session data:', error);
        }
    }
    
    /**
     * Load session data from local storage
     * @private
     */
    loadSessionData() {
        try {
            const savedData = localStorage.getItem(this.config.storageKey);
            if (!savedData) return;
            
            const sessionData = JSON.parse(savedData);
            
            // Only load if the session is recent (less than 24 hours old)
            if (Date.now() - sessionData.timestamp > 24 * 60 * 60 * 1000) {
                return;
            }
            
            // Restore messages
            this.messages = sessionData.messages || [];
            
            // Restore filters
            if (sessionData.filters) {
                this.setFilters(sessionData.filters);
            }
            
            // Restore stats
            if (sessionData.stats) {
                this.stats = { ...this.stats, ...sessionData.stats };
                this.updateStatsDisplay();
            }
            
            // Apply filters and update display
            this.applyFilters();
            this.updateDisplay();
            
            this.addSystemMessage(`Restored ${this.messages.length} messages from previous session`, 'INFO');
            
        } catch (error) {
            console.warn('Failed to load session data:', error);
        }
    }
    
    /**
     * Clear session data from local storage
     * @private
     */
    clearSessionData() {
        try {
            localStorage.removeItem(this.config.storageKey);
        } catch (error) {
            console.warn('Failed to clear session data:', error);
        }
    }
    
    /**
     * Save filter preferences
     * @private
     */
    saveFilterPreferences() {
        try {
            const prefKey = `${this.config.storageKey}-filters`;
            localStorage.setItem(prefKey, JSON.stringify(this.filters));
        } catch (error) {
            console.warn('Failed to save filter preferences:', error);
        }
    }
    
    /**
     * Load filter preferences
     * @private
     */
    loadFilterPreferences() {
        try {
            const prefKey = `${this.config.storageKey}-filters`;
            const savedFilters = localStorage.getItem(prefKey);
            if (savedFilters) {
                const filters = JSON.parse(savedFilters);
                this.setFilters(filters);
            }
        } catch (error) {
            console.warn('Failed to load filter preferences:', error);
        }
    }
    
    // =========================
    // Performance Monitoring
    // =========================
    
    /**
     * Start performance monitoring
     * @private
     */
    startPerformanceMonitoring() {
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 5000); // Update every 5 seconds
    }
    
    /**
     * Update performance metrics
     * @private
     */
    updatePerformanceMetrics() {
        // Update message rate
        const now = Date.now();
        const oneMinuteAgo = now - 60000;
        this.stats.messageTimestamps = this.stats.messageTimestamps.filter(ts => ts > oneMinuteAgo);
        this.stats.messagesPerSecond = this.stats.messageTimestamps.length / 60;
        
        // Update display
        this.updateStatsDisplay();
    }
    
    // =========================
    // Utility Methods
    // =========================
    
    /**
     * Generate unique message ID
     * @private
     * @returns {string} Unique message ID
     */
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Generate unique session ID
     * @private
     * @returns {string} Session ID
     */
    generateSessionId() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substr(2, 9);
        return `${timestamp}_${random}`;
    }
    
    /**
     * Escape HTML characters
     * @private
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Show error message
     * @private
     * @param {string} title - Error title
     * @param {string} message - Error message
     */
    showError(title, message) {
        console.error(`❌ ${title}: ${message}`);
        // Add error to log
        this.addSystemMessage(`Error: ${title} - ${message}`, 'ERROR');
    }
    
    /**
     * Debounce function calls
     * @private
     * @param {Function} func - Function to debounce
     * @param {number} delay - Delay in milliseconds
     * @returns {Function} Debounced function
     */
    debounce(func, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }
    
    /**
     * Throttle function calls
     * @private
     * @param {Function} func - Function to throttle
     * @param {number} delay - Delay in milliseconds
     * @returns {Function} Throttled function
     */
    throttle(func, delay) {
        let lastCall = 0;
        return (...args) => {
            const now = Date.now();
            if (now - lastCall >= delay) {
                lastCall = now;
                return func.apply(this, args);
            }
        };
    }
    
    /**
     * Cleanup resources and event listeners
     */
    cleanup() {
        // Clear timers
        if (this.bufferTimer) {
            clearTimeout(this.bufferTimer);
        }
        
        // Remove event listeners
        if (this.websocketManager) {
            this.websocketManager.off('testLog', this.boundHandlers.onLogMessage);
            this.websocketManager.off('systemLog', this.boundHandlers.onLogMessage);
            this.websocketManager.off('hardwareLog', this.boundHandlers.onLogMessage);
            this.websocketManager.off('stateChange', this.boundHandlers.onConnectionChange);
        }
        
        window.removeEventListener('resize', this.boundHandlers.onResize);
        document.removeEventListener('keydown', this.handleKeydown);
        document.removeEventListener('click', this.handleDocumentClick);
        
        // Clear render cache
        this.virtualScroll.renderCache.clear();
        
        // Save final session state
        if (this.config.saveToLocalStorage) {
            this.saveSessionData();
        }
        
        console.log('🧹 Log Viewer Component cleanup complete');
    }
}

// Export for use in other modules
export { LogLevel, LogSource, ExportFormat };

console.log('📝 Log Viewer Component loaded successfully');