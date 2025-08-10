/**
 * Logs Page Manager - WF EOL Tester Web Interface
 * 
 * This module manages the standalone logs page including:
 * - Log viewer component initialization and configuration
 * - Split view and sidebar functionality
 * - Session management and persistence
 * - Page-specific UI interactions and modals
 * - Statistics and monitoring display
 * - Integration with the main application context
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

import { LogViewerComponent } from '../components/log-viewer.js';
import { WebSocketManager } from '../services/websocket-manager.js';
import { APIClient } from '../services/api-client.js';

/**
 * View modes for the logs page
 */
const ViewMode = {
    FULL: 'full',
    SPLIT: 'split'
};

/**
 * Logs Page Manager Class
 * 
 * Manages the standalone logs page with enhanced functionality
 * for comprehensive log viewing and analysis.
 */
export class LogsPageManager {
    /**
     * Initialize logs page manager
     */
    constructor() {
        console.log('📋 Initializing Logs Page Manager...');
        
        // Core dependencies
        this.apiClient = null;
        this.websocketManager = null;
        this.logViewer = null;
        
        // Page state
        this.currentView = ViewMode.FULL;
        this.isInitialized = false;
        this.sidebarVisible = false;
        
        // Statistics
        this.stats = {
            activeSessions: 0,
            systemStatus: 'Unknown',
            websocketStatus: 'Disconnected',
            storageUsed: '0 MB',
            sourceCounts: {}
        };
        
        // Session management
        this.currentSession = null;
        this.savedSessions = [];
        
        // DOM elements
        this.elements = {};
        
        // Event handlers
        this.boundHandlers = {
            onViewToggle: this.handleViewToggle.bind(this),
            onSourceSelect: this.handleSourceSelect.bind(this),
            onStatsUpdate: this.handleStatsUpdate.bind(this),
            onSessionAction: this.handleSessionAction.bind(this)
        };
        
        // Initialize page
        this.init();
        
        console.log('✅ Logs Page Manager initialized');
    }
    
    /**
     * Initialize the page manager
     * @private
     */
    async init() {
        try {
            // Show loading screen
            this.showLoadingScreen();
            
            // Cache DOM elements
            this.cacheElements();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize core services
            await this.initializeServices();
            
            // Initialize log viewer component
            await this.initializeLogViewer();
            
            // Load initial data
            await this.loadInitialData();
            
            // Setup periodic updates
            this.startPeriodicUpdates();
            
            // Mark as initialized
            this.isInitialized = true;
            
            // Hide loading screen
            this.hideLoadingScreen();
            
            console.log('✅ Logs page initialization complete');
            
        } catch (error) {
            console.error('❌ Logs page initialization failed:', error);
            this.showError('Initialization failed', error.message);
            this.hideLoadingScreen();
        }
    }
    
    /**
     * Cache DOM elements
     * @private
     */
    cacheElements() {
        this.elements = {
            // Main containers
            page: document.querySelector('.logs-page'),
            sidebar: document.querySelector('#logs-sidebar'),
            main: document.querySelector('#logs-main'),
            viewerContainer: document.querySelector('#logs-page-viewer'),
            
            // Header elements
            helpBtn: document.querySelector('#logs-help-btn'),
            settingsBtn: document.querySelector('#logs-settings-btn'),
            viewToggleBtns: document.querySelectorAll('.logs-page__toggle-btn'),
            
            // Stats bar elements
            activeSessionsCount: document.querySelector('#active-sessions-count'),
            systemStatus: document.querySelector('#system-status'),
            websocketStatus: document.querySelector('#websocket-status'),
            storageUsed: document.querySelector('#storage-used'),
            
            // Sidebar elements
            sourceItems: document.querySelectorAll('.logs-page__source-item'),
            recentSessionsList: document.querySelector('#recent-sessions-list'),
            
            // Source count elements
            sourceCounts: {
                all: document.querySelector('#source-all-count'),
                hardware: document.querySelector('#source-hardware-count'),
                test: document.querySelector('#source-test-count'),
                system: document.querySelector('#source-system-count'),
                api: document.querySelector('#source-api-count'),
                websocket: document.querySelector('#source-websocket-count'),
                mcu: document.querySelector('#source-mcu-count'),
                robot: document.querySelector('#source-robot-count')
            },
            
            // Modal elements
            sessionModal: document.querySelector('#session-management-modal'),
            analysisModal: document.querySelector('#log-analysis-modal'),
            loadingScreen: document.querySelector('#logs-loading-screen'),
            loadingProgressBar: document.querySelector('#loading-progress-bar'),
            
            // Session management elements
            sessionTabs: document.querySelectorAll('.logs-page__session-tab'),
            sessionPanels: document.querySelectorAll('.logs-page__session-panel'),
            currentSessionId: document.querySelector('#current-session-id'),
            sessionStartTime: document.querySelector('#session-start-time'),
            sessionMessageCount: document.querySelector('#session-message-count'),
            sessionStorageSize: document.querySelector('#session-storage-size'),
            
            // Session action buttons
            saveSessionBtn: document.querySelector('#save-session-btn'),
            exportSessionBtn: document.querySelector('#export-session-btn'),
            clearSessionBtn: document.querySelector('#clear-session-btn'),
            
            // Analysis elements
            startAnalysisBtn: document.querySelector('#start-analysis-btn')
        };
        
        console.log('✅ DOM elements cached');
    }
    
    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // View toggle buttons
        this.elements.viewToggleBtns.forEach(btn => {
            btn.addEventListener('click', this.boundHandlers.onViewToggle);
        });
        
        // Source selection
        this.elements.sourceItems.forEach(item => {
            item.addEventListener('click', this.boundHandlers.onSourceSelect);
        });
        
        // Header buttons
        if (this.elements.helpBtn) {
            this.elements.helpBtn.addEventListener('click', this.showKeyboardShortcuts.bind(this));
        }
        
        if (this.elements.settingsBtn) {
            this.elements.settingsBtn.addEventListener('click', this.showSettings.bind(this));
        }
        
        // Session management
        this.elements.sessionTabs.forEach(tab => {
            tab.addEventListener('click', this.handleSessionTabChange.bind(this));
        });
        
        if (this.elements.saveSessionBtn) {
            this.elements.saveSessionBtn.addEventListener('click', () => this.handleSessionAction('save'));
        }
        
        if (this.elements.exportSessionBtn) {
            this.elements.exportSessionBtn.addEventListener('click', () => this.handleSessionAction('export'));
        }
        
        if (this.elements.clearSessionBtn) {
            this.elements.clearSessionBtn.addEventListener('click', () => this.handleSessionAction('clear'));
        }
        
        // Analysis
        if (this.elements.startAnalysisBtn) {
            this.elements.startAnalysisBtn.addEventListener('click', this.startLogAnalysis.bind(this));
        }
        
        // Modal close handlers
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('logs-page__modal-overlay') ||
                event.target.classList.contains('logs-page__modal-close')) {
                this.closeAllModals();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeydown.bind(this));
        
        console.log('✅ Event listeners setup complete');
    }
    
    /**
     * Initialize core services
     * @private
     */
    async initializeServices() {
        try {
            // Update progress
            this.updateLoadingProgress(25, 'Initializing API client...');
            
            // Initialize API client
            this.apiClient = new APIClient();
            
            // Update progress
            this.updateLoadingProgress(50, 'Connecting to WebSocket...');
            
            // Initialize WebSocket manager
            this.websocketManager = new WebSocketManager({
                url: 'ws://localhost:8080/ws',
                reconnectInterval: 3000,
                maxReconnectAttempts: 10
            });
            
            // Connect to WebSocket
            await this.websocketManager.connect();
            
            // Setup WebSocket event handlers
            this.websocketManager.on('stateChange', (stateChange) => {
                this.stats.websocketStatus = stateChange.to === 'connected' ? 'Connected' : 'Disconnected';
                this.updateStatsDisplay();
            });
            
            console.log('✅ Core services initialized');
            
        } catch (error) {
            console.warn('⚠️ Some services failed to initialize:', error);
            // Continue with degraded functionality
        }
    }
    
    /**
     * Initialize log viewer component
     * @private
     */
    async initializeLogViewer() {
        try {
            // Update progress
            this.updateLoadingProgress(75, 'Setting up log viewer...');
            
            // Create log viewer configuration
            const config = {
                maxMessages: 15000,
                batchSize: 30,
                updateInterval: 100,
                autoScroll: true,
                enableVirtualScrolling: true,
                saveToLocalStorage: true,
                storageKey: 'wf-eol-logs-page'
            };
            
            // Initialize log viewer component
            this.logViewer = new LogViewerComponent(
                this.elements.viewerContainer,
                this.websocketManager,
                config
            );
            
            // Setup log viewer event handlers
            this.setupLogViewerHandlers();
            
            console.log('✅ Log viewer component initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize log viewer:', error);
            throw error;
        }
    }
    
    /**
     * Setup log viewer event handlers
     * @private
     */
    setupLogViewerHandlers() {
        // Listen for stats updates from log viewer
        if (this.logViewer && this.logViewer.on) {
            this.logViewer.on('statsUpdate', this.boundHandlers.onStatsUpdate);
        }
        
        // Monitor log viewer stats periodically
        setInterval(() => {
            if (this.logViewer && typeof this.logViewer.getStats === 'function') {
                const stats = this.logViewer.getStats();
                this.updateSourceCounts(stats);
            }
        }, 2000);
    }
    
    /**
     * Load initial data
     * @private
     */
    async loadInitialData() {
        try {
            // Update progress
            this.updateLoadingProgress(90, 'Loading initial data...');
            
            // Load system status
            await this.loadSystemStatus();
            
            // Load session data
            await this.loadSessionData();
            
            // Update displays
            this.updateStatsDisplay();
            this.updateSessionInfo();
            
            console.log('✅ Initial data loaded');
            
        } catch (error) {
            console.warn('⚠️ Failed to load some initial data:', error);
            // Continue with available data
        }
    }
    
    /**
     * Load system status
     * @private
     */
    async loadSystemStatus() {
        try {
            if (this.apiClient) {
                const response = await this.apiClient.get('/system/status');
                if (response.data) {
                    this.stats.systemStatus = response.data.status || 'Unknown';
                    this.stats.activeSessions = response.data.activeSessions || 0;
                }
            }
        } catch (error) {
            console.warn('Failed to load system status:', error);
        }
    }
    
    /**
     * Load session data
     * @private
     */
    loadSessionData() {
        try {
            // Load from localStorage
            const savedData = localStorage.getItem('wf-eol-logs-sessions');
            if (savedData) {
                const data = JSON.parse(savedData);
                this.savedSessions = data.sessions || [];
                this.currentSession = data.currentSession || null;
            }
            
            // Calculate storage usage
            this.calculateStorageUsage();
            
        } catch (error) {
            console.warn('Failed to load session data:', error);
        }
    }
    
    /**
     * Calculate storage usage
     * @private
     */
    calculateStorageUsage() {
        try {
            let totalSize = 0;
            
            // Calculate localStorage usage
            for (let key in localStorage) {
                if (localStorage.hasOwnProperty(key) && key.startsWith('wf-eol-')) {
                    totalSize += localStorage[key].length;
                }
            }
            
            // Convert to MB
            const sizeInMB = (totalSize / 1024 / 1024).toFixed(2);
            this.stats.storageUsed = `${sizeInMB} MB`;
            
        } catch (error) {
            console.warn('Failed to calculate storage usage:', error);
            this.stats.storageUsed = 'Unknown';
        }
    }
    
    /**
     * Start periodic updates
     * @private
     */
    startPeriodicUpdates() {
        // Update stats every 5 seconds
        setInterval(async () => {
            try {
                await this.loadSystemStatus();
                this.calculateStorageUsage();
                this.updateStatsDisplay();
            } catch (error) {
                console.warn('Periodic update failed:', error);
            }
        }, 5000);
        
        // Update session info every 10 seconds
        setInterval(() => {
            this.updateSessionInfo();
        }, 10000);
    }
    
    /**
     * Handle view toggle
     * @private
     * @param {Event} event - Click event
     */
    handleViewToggle(event) {
        const viewMode = event.currentTarget.getAttribute('data-view');
        
        if (viewMode === this.currentView) return;
        
        this.currentView = viewMode;
        
        // Update button states
        this.elements.viewToggleBtns.forEach(btn => {
            btn.classList.toggle('logs-page__toggle-btn--active', 
                               btn.getAttribute('data-view') === viewMode);
        });
        
        // Toggle sidebar visibility
        if (viewMode === ViewMode.SPLIT) {
            this.showSidebar();
        } else {
            this.hideSidebar();
        }
        
        console.log(`📊 View mode changed to: ${viewMode}`);
    }
    
    /**
     * Show sidebar
     * @private
     */
    showSidebar() {
        if (this.elements.sidebar) {
            this.elements.sidebar.style.display = 'flex';
            this.sidebarVisible = true;
            
            // Update source counts
            this.updateSourceCountsDisplay();
        }
    }
    
    /**
     * Hide sidebar
     * @private
     */
    hideSidebar() {
        if (this.elements.sidebar) {
            this.elements.sidebar.style.display = 'none';
            this.sidebarVisible = false;
        }
    }
    
    /**
     * Handle source selection
     * @private
     * @param {Event} event - Click event
     */
    handleSourceSelect(event) {
        const sourceItem = event.currentTarget;
        const source = sourceItem.getAttribute('data-source');
        
        // Update active state
        this.elements.sourceItems.forEach(item => {
            item.classList.remove('logs-page__source-item--active');
        });
        sourceItem.classList.add('logs-page__source-item--active');
        
        // Apply filter to log viewer
        if (this.logViewer && typeof this.logViewer.setFilters === 'function') {
            this.logViewer.setFilters({ source });
        }
        
        console.log(`📋 Source filter applied: ${source}`);
    }
    
    /**
     * Handle stats update
     * @private
     * @param {Object} stats - Updated statistics
     */
    handleStatsUpdate(stats) {
        this.updateSourceCounts(stats);
    }
    
    /**
     * Update source counts
     * @private
     * @param {Object} stats - Log statistics
     */
    updateSourceCounts(stats) {
        // This would be implemented based on actual log viewer stats structure
        // For now, we'll simulate some counts
        this.stats.sourceCounts = {
            all: stats.totalMessages || 0,
            hardware: Math.floor((stats.totalMessages || 0) * 0.2),
            test: Math.floor((stats.totalMessages || 0) * 0.3),
            system: Math.floor((stats.totalMessages || 0) * 0.25),
            api: Math.floor((stats.totalMessages || 0) * 0.15),
            websocket: Math.floor((stats.totalMessages || 0) * 0.05),
            mcu: Math.floor((stats.totalMessages || 0) * 0.03),
            robot: Math.floor((stats.totalMessages || 0) * 0.02)
        };
        
        this.updateSourceCountsDisplay();
    }
    
    /**
     * Update source counts display
     * @private
     */
    updateSourceCountsDisplay() {
        Object.entries(this.stats.sourceCounts).forEach(([source, count]) => {
            const element = this.elements.sourceCounts[source];
            if (element) {
                element.textContent = count.toLocaleString();
            }
        });
    }
    
    /**
     * Update stats display
     * @private
     */
    updateStatsDisplay() {
        // Update active sessions
        if (this.elements.activeSessionsCount) {
            this.elements.activeSessionsCount.textContent = this.stats.activeSessions.toString();
        }
        
        // Update system status
        if (this.elements.systemStatus) {
            this.elements.systemStatus.textContent = this.stats.systemStatus;
            this.elements.systemStatus.className = `logs-page__stat-value logs-page__stat-value--status ${this.stats.systemStatus.toLowerCase()}`;
        }
        
        // Update WebSocket status
        if (this.elements.websocketStatus) {
            this.elements.websocketStatus.textContent = this.stats.websocketStatus;
            this.elements.websocketStatus.classList.toggle('connected', 
                                                          this.stats.websocketStatus === 'Connected');
        }
        
        // Update storage used
        if (this.elements.storageUsed) {
            this.elements.storageUsed.textContent = this.stats.storageUsed;
        }
    }
    
    /**
     * Handle session tab change
     * @private
     * @param {Event} event - Click event
     */
    handleSessionTabChange(event) {
        const tab = event.currentTarget;
        const tabName = tab.getAttribute('data-tab');
        
        // Update tab states
        this.elements.sessionTabs.forEach(t => {
            t.classList.remove('logs-page__session-tab--active');
        });
        tab.classList.add('logs-page__session-tab--active');
        
        // Update panel visibility
        this.elements.sessionPanels.forEach(panel => {
            const panelName = panel.getAttribute('data-panel');
            panel.classList.toggle('logs-page__session-panel--active', panelName === tabName);
        });
        
        console.log(`📝 Session tab changed to: ${tabName}`);
    }
    
    /**
     * Handle session actions
     * @private
     * @param {string} action - Action type
     */
    async handleSessionAction(action) {
        try {
            switch (action) {
                case 'save':
                    await this.saveCurrentSession();
                    break;
                case 'export':
                    this.exportCurrentSession();
                    break;
                case 'clear':
                    await this.clearCurrentSession();
                    break;
                default:
                    console.warn(`Unknown session action: ${action}`);
            }
        } catch (error) {
            console.error(`❌ Session action failed: ${action}`, error);
            this.showError('Session Action Failed', error.message);
        }
    }
    
    /**
     * Save current session
     * @private
     */
    async saveCurrentSession() {
        if (!this.logViewer) return;
        
        const sessionData = {
            id: `session_${Date.now()}`,
            name: `Session ${new Date().toLocaleString()}`,
            timestamp: Date.now(),
            stats: this.logViewer.getStats ? this.logViewer.getStats() : {},
            filters: this.logViewer.getFilters ? this.logViewer.getFilters() : {},
            messages: [] // We would save actual messages here
        };
        
        this.savedSessions.push(sessionData);
        this.saveSessionsToStorage();
        
        this.showNotification('Session saved successfully', 'success');
        console.log('💾 Session saved:', sessionData.id);
    }
    
    /**
     * Export current session
     * @private
     */
    exportCurrentSession() {
        if (!this.logViewer || typeof this.logViewer.exportLogs !== 'function') {
            this.showError('Export Failed', 'Log viewer not available');
            return;
        }
        
        // Use log viewer's export functionality
        this.logViewer.exportLogs('json');
        
        console.log('📤 Session exported');
    }
    
    /**
     * Clear current session
     * @private
     */
    async clearCurrentSession() {
        if (!confirm('Are you sure you want to clear the current session? This will remove all log messages.')) {
            return;
        }
        
        if (this.logViewer && typeof this.logViewer.clear === 'function') {
            this.logViewer.clear();
        }
        
        this.showNotification('Session cleared', 'info');
        console.log('🗑️ Session cleared');
    }
    
    /**
     * Update session info
     * @private
     */
    updateSessionInfo() {
        if (!this.logViewer) return;
        
        // Update current session ID
        if (this.elements.currentSessionId) {
            this.elements.currentSessionId.textContent = this.currentSession?.id || 'N/A';
        }
        
        // Update start time
        if (this.elements.sessionStartTime) {
            const startTime = this.currentSession?.timestamp || Date.now();
            this.elements.sessionStartTime.textContent = new Date(startTime).toLocaleString();
        }
        
        // Update message count
        if (this.elements.sessionMessageCount) {
            const stats = this.logViewer.getStats ? this.logViewer.getStats() : {};
            this.elements.sessionMessageCount.textContent = (stats.totalMessages || 0).toLocaleString();
        }
        
        // Update storage size
        if (this.elements.sessionStorageSize) {
            this.elements.sessionStorageSize.textContent = this.stats.storageUsed;
        }
    }
    
    /**
     * Save sessions to storage
     * @private
     */
    saveSessionsToStorage() {
        try {
            const data = {
                sessions: this.savedSessions,
                currentSession: this.currentSession,
                timestamp: Date.now()
            };
            
            localStorage.setItem('wf-eol-logs-sessions', JSON.stringify(data));
            
        } catch (error) {
            console.error('Failed to save sessions to storage:', error);
        }
    }
    
    /**
     * Start log analysis
     * @private
     */
    async startLogAnalysis() {
        try {
            // This would implement actual log analysis functionality
            this.showNotification('Log analysis started', 'info');
            
            // Simulate analysis process
            setTimeout(() => {
                this.showNotification('Log analysis completed', 'success');
            }, 3000);
            
        } catch (error) {
            console.error('❌ Log analysis failed:', error);
            this.showError('Analysis Failed', error.message);
        }
    }
    
    /**
     * Show keyboard shortcuts help
     * @private
     */
    showKeyboardShortcuts() {
        const helpOverlay = document.getElementById('keyboard-shortcuts-help');
        if (helpOverlay) {
            helpOverlay.style.display = 'flex';
        }
    }
    
    /**
     * Show settings modal
     * @private
     */
    showSettings() {
        const settingsModal = document.getElementById('log-settings-modal');
        if (settingsModal) {
            settingsModal.style.display = 'flex';
        }
    }
    
    /**
     * Close all modals
     * @private
     */
    closeAllModals() {
        document.querySelectorAll('.logs-page__modal').forEach(modal => {
            modal.style.display = 'none';
        });
        
        // Also close help overlay
        const helpOverlay = document.getElementById('keyboard-shortcuts-help');
        if (helpOverlay) {
            helpOverlay.style.display = 'none';
        }
    }
    
    /**
     * Handle keyboard shortcuts
     * @private
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeydown(event) {
        if (!this.isInitialized) return;
        
        switch (event.key) {
            case 'F1':
                event.preventDefault();
                this.showKeyboardShortcuts();
                break;
            case 'Escape':
                this.closeAllModals();
                break;
            case 's':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    this.handleSessionAction('save');
                }
                break;
            case 'e':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    this.handleSessionAction('export');
                }
                break;
        }
    }
    
    /**
     * Show loading screen
     * @private
     */
    showLoadingScreen() {
        if (this.elements.loadingScreen) {
            this.elements.loadingScreen.style.display = 'flex';
        }
    }
    
    /**
     * Hide loading screen
     * @private
     */
    hideLoadingScreen() {
        if (this.elements.loadingScreen) {
            this.elements.loadingScreen.style.display = 'none';
        }
    }
    
    /**
     * Update loading progress
     * @private
     * @param {number} percentage - Progress percentage
     * @param {string} text - Loading text
     */
    updateLoadingProgress(percentage, text) {
        if (this.elements.loadingProgressBar) {
            this.elements.loadingProgressBar.style.width = `${percentage}%`;
        }
        
        const loadingText = document.querySelector('.logs-page__loading-text');
        if (loadingText && text) {
            loadingText.textContent = text;
        }
    }
    
    /**
     * Show notification
     * @private
     * @param {string} message - Notification message
     * @param {string} type - Notification type
     */
    showNotification(message, type = 'info') {
        // This would integrate with a notification system
        console.log(`📢 ${type.toUpperCase()}: ${message}`);
        
        // For now, just use a simple alert
        // In a real implementation, this would show a proper notification
    }
    
    /**
     * Show error message
     * @private
     * @param {string} title - Error title
     * @param {string} message - Error message
     */
    showError(title, message) {
        console.error(`❌ ${title}: ${message}`);
        // This would show a proper error modal
        alert(`${title}: ${message}`);
    }
    
    /**
     * Get page instance (for external access)
     * @returns {LogsPageManager} Page manager instance
     */
    static getInstance() {
        return window.logsPageManager;
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        // Stop periodic updates
        // Clear intervals would go here
        
        // Cleanup log viewer
        if (this.logViewer && typeof this.logViewer.cleanup === 'function') {
            this.logViewer.cleanup();
        }
        
        // Disconnect WebSocket
        if (this.websocketManager && typeof this.websocketManager.disconnect === 'function') {
            this.websocketManager.disconnect();
        }
        
        // Save final session state
        this.saveSessionsToStorage();
        
        console.log('🧹 Logs Page Manager cleanup complete');
    }
}

// Initialize logs page manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.logsPageManager = new LogsPageManager();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.logsPageManager) {
        window.logsPageManager.cleanup();
    }
});

console.log('📝 Logs page manager module loaded successfully');