/**
 * Main JavaScript Entry Point - WF EOL Tester Web Interface
 * 
 * This is the main entry point for the web application. It handles:
 * - Application initialization and startup
 * - Module loading and dependency management
 * - Event system setup and global error handling
 * - Navigation management and page routing
 * - Real-time clock updates and system monitoring
 * - WebSocket connection initialization for live updates
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

// Import core modules
import { AppConfig } from './config/app-config.js';
import { APIClient } from './services/api-client.js';
import { WebSocketManager } from './services/websocket-manager.js';
import { UIManager } from './components/ui-manager.js';
import { HardwareMonitor } from './components/hardware-monitor.js';
import { TestRunner } from './components/test-runner.js';

// Import page managers
import { EOLForceTestPageManager } from './pages/eol-force-test.js';
import { RobotHomePageManager } from './pages/robot-home.js';
import { HardwareDashboardPageManager } from './pages/hardware-dashboard.js';
import { RobotControlPageManager } from './pages/robot-control.js';
import { PowerControlPageManager } from './pages/power-control.js';
import { MCUControlPageManager } from './pages/mcu-control.js';
import { LoadCellControlPageManager } from './pages/loadcell-control.js';

/**
 * Main Application Class - WF EOL Tester Web Interface
 * 
 * Orchestrates all application components and manages the overall application lifecycle.
 * Implements Clean Architecture principles with proper separation of concerns.
 */
class WFEOLTesterApp {
    /**
     * Initialize application instance
     */
    constructor() {
        console.log('🚀 Initializing WF EOL Tester Web Interface...');
        
        // Application state
        this.isInitialized = false;
        this.isConnected = false;
        this.currentPage = 'welcome-page';
        this.emergencyStopActive = false;
        
        // Core services
        this.config = AppConfig;
        this.apiClient = null;
        this.websocketManager = null;
        this.uiManager = null;
        this.hardwareMonitor = null;
        this.testRunner = null;
        
        // Page managers
        this.pageManagers = new Map();
        this.currentPageManager = null;
        
        // Event handlers binding
        this.handleEmergencyStop = this.handleEmergencyStop.bind(this);
        this.handlePageNavigation = this.handlePageNavigation.bind(this);
        this.handleConnectionChange = this.handleConnectionChange.bind(this);
        this.handleError = this.handleError.bind(this);
        
        // Initialize core components
        this.setupComponents();
        this.setupEventListeners();
        this.setupErrorHandling();
    }

    /**
     * Initialize core application components
     * @private
     */
    setupComponents() {
        try {
            // Initialize API Client
            this.apiClient = new APIClient(this.config.api);
            console.log('✅ API Client initialized');
            
            // Initialize WebSocket Manager
            this.websocketManager = new WebSocketManager(this.config.websocket);
            console.log('✅ WebSocket Manager initialized');
            
            // Initialize UI Manager
            this.uiManager = new UIManager();
            console.log('✅ UI Manager initialized');
            
            // Initialize Hardware Monitor
            this.hardwareMonitor = new HardwareMonitor(this.apiClient, this.websocketManager);
            console.log('✅ Hardware Monitor initialized');
            
            // Initialize Test Runner
            this.testRunner = new TestRunner(this.apiClient, this.websocketManager);
            console.log('✅ Test Runner initialized');
            
            // Initialize page managers
            this.initializePageManagers();
            
        } catch (error) {
            console.error('❌ Failed to initialize components:', error);
            this.handleError(error, 'Component Initialization');
        }
    }

    /**
     * Initialize page managers
     * @private
     */
    initializePageManagers() {
        try {
            // Create page manager registry
            const managers = {
                'eol-force-test': EOLForceTestPageManager,
                'robot-home': RobotHomePageManager,
                'hardware-dashboard': HardwareDashboardPageManager,
                'robot-control': RobotControlPageManager,
                'power-control': PowerControlPageManager,
                'mcu-control': MCUControlPageManager,
                'loadcell-control': LoadCellControlPageManager
            };
            
            // Store manager classes (lazy initialization)
            Object.entries(managers).forEach(([pageId, ManagerClass]) => {
                this.pageManagers.set(pageId, {
                    ManagerClass,
                    instance: null
                });
            });
            
            console.log('✅ Page managers registry initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize page managers:', error);
        }
    }
    
    /**
     * Get or create page manager instance
     * @private
     * @param {string} pageId - Page identifier
     * @returns {Object|null} Page manager instance
     */
    getPageManager(pageId) {
        const managerInfo = this.pageManagers.get(pageId);
        if (!managerInfo) return null;
        
        // Lazy initialization
        if (!managerInfo.instance && managerInfo.ManagerClass) {
            try {
                // Hardware control page managers expect (apiClient, uiManager, wsManager)
                // while other page managers might expect different parameter order
                if (['hardware-dashboard', 'robot-control', 'power-control', 'mcu-control', 'loadcell-control'].includes(pageId)) {
                    managerInfo.instance = new managerInfo.ManagerClass(
                        this.apiClient,
                        this.uiManager,
                        this.websocketManager
                    );
                } else {
                    // For other page managers, use original order
                    managerInfo.instance = new managerInfo.ManagerClass(
                        this.apiClient,
                        this.websocketManager,
                        this.uiManager
                    );
                }
                console.log(`✅ Page manager initialized for: ${pageId}`);
            } catch (error) {
                console.error(`❌ Failed to initialize page manager for ${pageId}:`, error);
                return null;
            }
        }
        
        return managerInfo.instance;
    }
    
    /**
     * Activate page manager
     * @private
     * @param {string} pageId - Page identifier
     */
    async activatePageManager(pageId) {
        // Deactivate current page manager
        if (this.currentPageManager) {
            // Call cleanup on hardware control page managers
            if (this.currentPageManager.cleanup && typeof this.currentPageManager.cleanup === 'function') {
                try {
                    this.currentPageManager.cleanup();
                } catch (error) {
                    console.warn(`❌ Failed to cleanup page manager:`, error);
                }
            }
            this.currentPageManager = null;
        }
        
        // Activate new page manager
        const manager = this.getPageManager(pageId);
        if (manager) {
            this.currentPageManager = manager;
            
            // Initialize hardware control page managers
            if (manager.init && typeof manager.init === 'function') {
                try {
                    await manager.init();
                    
                    // Expose robot control page manager globally for debugging
                    if (pageId === 'robot-control') {
                        window.robotControlPage = manager;
                        console.log('🔧 Robot Control Page Manager exposed globally as window.robotControlPage');
                        console.log('🔧 Use window.robotControlPage.testAPIEndpoints() to test API endpoints');
                    }
                } catch (error) {
                    console.warn(`❌ Failed to initialize page manager for ${pageId}:`, error);
                }
            }
            
            // Store globally for debugging/external access
            const globalName = pageId.replace(/-([a-z])/g, (match, letter) => letter.toUpperCase()) + 'Manager';
            window[globalName] = manager;
            
            console.log(`📄 Page manager activated: ${pageId}`);
        }
    }

    /**
     * Setup global event listeners
     * @private
     */
    setupEventListeners() {
        try {
            // Emergency stop button
            const emergencyBtn = document.getElementById('emergency-stop');
            if (emergencyBtn) {
                emergencyBtn.addEventListener('click', this.handleEmergencyStop);
                console.log('✅ Emergency stop listener registered');
            }
            
            // Navigation event delegation
            document.addEventListener('click', this.handlePageNavigation);
            console.log('✅ Navigation event delegation setup');
            
            // Sidebar toggle functionality
            document.addEventListener('click', (e) => {
                if (e.target.hasAttribute('data-toggle')) {
                    this.handleSidebarToggle(e.target);
                }
            });
            
            // Quick action buttons
            document.addEventListener('click', (e) => {
                if (e.target.hasAttribute('data-action')) {
                    this.handleQuickAction(e.target.getAttribute('data-action'));
                }
            });
            
            // WebSocket connection events
            if (this.websocketManager) {
                this.websocketManager.on('connected', this.handleConnectionChange);
                this.websocketManager.on('disconnected', this.handleConnectionChange);
                this.websocketManager.on('error', this.handleError);
            }
            
            // Window events
            window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
            window.addEventListener('error', this.handleError);
            window.addEventListener('unhandledrejection', this.handleUnhandledRejection.bind(this));
            
            console.log('✅ Global event listeners setup complete');
            
        } catch (error) {
            console.error('❌ Failed to setup event listeners:', error);
            this.handleError(error, 'Event Listener Setup');
        }
    }

    /**
     * Setup global error handling
     * @private
     */
    setupErrorHandling() {
        // Global error handler
        window.onerror = (message, source, lineno, colno, error) => {
            console.error('Global Error:', { message, source, lineno, colno, error });
            this.handleError(error || message, 'Global Error');
            return true;
        };
        
        // Promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled Promise Rejection:', event.reason);
            this.handleError(event.reason, 'Promise Rejection');
            event.preventDefault();
        });
        
        console.log('✅ Global error handling setup complete');
    }

    /**
     * Main application initialization
     * @returns {Promise<void>}
     */
    async init() {
        try {
            console.log('🔄 Starting application initialization...');
            
            // Show loading overlay
            this.uiManager?.showLoading('Initializing application...');
            
            // Update status
            this.updateSystemStatus('initializing', 'Initializing application...');
            
            // Initialize real-time clock
            this.startClock();
            
            // Connect to WebSocket
            await this.connectWebSocket();
            
            // Initialize hardware monitoring
            await this.initializeHardwareMonitoring();
            
            // Load initial data
            await this.loadInitialData();
            
            // Mark as initialized
            this.isInitialized = true;
            
            // Update status
            this.updateSystemStatus('ready', 'System ready');
            
            // Hide loading overlay
            this.uiManager?.hideLoading();
            
            console.log('✅ Application initialization complete');
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.handleError(error, 'Application Initialization');
            
            // Update status to error state
            this.updateSystemStatus('error', 'Initialization failed');
            this.uiManager?.hideLoading();
        }
    }

    /**
     * Connect to WebSocket for real-time updates
     * @private
     * @returns {Promise<void>}
     */
    async connectWebSocket() {
        try {
            if (!this.websocketManager) {
                throw new Error('WebSocket Manager not initialized');
            }
            
            console.log('🔄 Connecting to WebSocket...');
            await this.websocketManager.connect();
            console.log('✅ WebSocket connected successfully');
            
        } catch (error) {
            console.warn('⚠️ WebSocket connection failed, continuing in offline mode:', error);
            // Don't throw error - allow app to work offline
        }
    }

    /**
     * Initialize hardware monitoring
     * @private
     * @returns {Promise<void>}
     */
    async initializeHardwareMonitoring() {
        try {
            if (!this.hardwareMonitor) {
                throw new Error('Hardware Monitor not initialized');
            }
            
            console.log('🔄 Initializing hardware monitoring...');
            await this.hardwareMonitor.start();
            console.log('✅ Hardware monitoring started');
            
        } catch (error) {
            console.warn('⚠️ Hardware monitoring initialization failed:', error);
            // Continue without hardware monitoring
        }
    }

    /**
     * Load initial application data
     * @private
     * @returns {Promise<void>}
     */
    async loadInitialData() {
        try {
            console.log('🔄 Loading initial data...');
            
            // Load system configuration
            await this.loadSystemConfiguration();
            
            // Load hardware status
            await this.loadHardwareStatus();
            
            // Load recent test history
            await this.loadRecentTests();
            
            console.log('✅ Initial data loaded');
            
        } catch (error) {
            console.warn('⚠️ Failed to load some initial data:', error);
            // Continue with partial data
        }
    }

    /**
     * Load system configuration
     * @private
     * @returns {Promise<void>}
     */
    async loadSystemConfiguration() {
        try {
            const config = await this.apiClient.getConfiguration();
            console.log('Configuration loaded:', config);
        } catch (error) {
            console.warn('Failed to load configuration:', error);
        }
    }

    /**
     * Load hardware status
     * @private
     * @returns {Promise<void>}
     */
    async loadHardwareStatus() {
        try {
            const status = await this.apiClient.getHardwareStatus();
            this.updateHardwareStatusDisplay(status);
            console.log('Hardware status loaded:', status);
        } catch (error) {
            console.warn('Failed to load hardware status:', error);
        }
    }

    /**
     * Load recent test results
     * @private
     * @returns {Promise<void>}
     */
    async loadRecentTests() {
        try {
            const tests = await this.apiClient.getTestHistory({ limit: 5 });
            this.updateLastTestDisplay(tests);
            console.log('Recent tests loaded:', tests);
        } catch (error) {
            console.warn('Failed to load recent tests:', error);
        }
    }

    /**
     * Start real-time clock in footer
     * @private
     */
    startClock() {
        const updateClock = () => {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            const clockElement = document.getElementById('footer-time');
            if (clockElement) {
                clockElement.textContent = timeString;
            }
        };
        
        // Update immediately
        updateClock();
        
        // Update every second
        setInterval(updateClock, 1000);
        
        console.log('✅ Real-time clock started');
    }

    /**
     * Handle emergency stop button click
     * @private
     * @param {Event} event - Click event
     */
    async handleEmergencyStop(event) {
        event.preventDefault();
        
        try {
            console.log('🚨 Emergency stop activated!');
            
            // Activate emergency stop state
            this.emergencyStopActive = true;
            
            // Update UI to show emergency state
            this.updateSystemStatus('emergency', 'EMERGENCY STOP ACTIVE');
            this.uiManager?.showModal({
                title: '🛑 Emergency Stop',
                message: 'Emergency stop has been activated. All hardware operations have been halted.',
                type: 'error'
            });
            
            // Send emergency stop command to backend
            await this.apiClient.emergencyStop();
            
            // Stop all ongoing operations
            await this.testRunner?.stop();
            await this.hardwareMonitor?.pause();
            
            console.log('✅ Emergency stop executed successfully');
            
        } catch (error) {
            console.error('❌ Emergency stop execution failed:', error);
            this.handleError(error, 'Emergency Stop');
        }
    }

    /**
     * Handle page navigation
     * @private
     * @param {Event} event - Click event
     */
    handlePageNavigation(event) {
        const target = event.target.closest('[data-page]');
        if (!target) return;
        
        event.preventDefault();
        const pageName = target.getAttribute('data-page');
        
        if (pageName) {
            this.navigateToPage(pageName);
        }
    }

    /**
     * Navigate to specific page
     * @param {string} pageName - Name of page to navigate to
     */
    async navigateToPage(pageName) {
        try {
            console.log(`🔄 Navigating to page: ${pageName}`);
            
            // Update current page
            this.currentPage = pageName;
            
            // Use UI Manager to switch pages
            await this.uiManager?.switchPage(pageName);
            
            // Activate page manager if available
            await this.activatePageManager(pageName);
            
            // Update navigation state
            this.updateNavigationState(pageName);
            
            console.log(`✅ Navigation to ${pageName} complete`);
            
        } catch (error) {
            console.error(`❌ Navigation to ${pageName} failed:`, error);
            this.handleError(error, 'Page Navigation');
        }
    }

    /**
     * Handle sidebar menu toggle
     * @private
     * @param {HTMLElement} toggleElement - Element that triggered toggle
     */
    handleSidebarToggle(toggleElement) {
        const menuType = toggleElement.getAttribute('data-toggle');
        const menu = document.getElementById(`${menuType}-menu`);
        
        if (menu) {
            const isVisible = menu.style.display !== 'none';
            menu.style.display = isVisible ? 'none' : 'block';
            
            // Update toggle indicator
            toggleElement.classList.toggle('expanded', !isVisible);
        }
    }

    /**
     * Handle quick action buttons
     * @private
     * @param {string} action - Action to perform
     */
    async handleQuickAction(action) {
        try {
            console.log(`🔄 Executing quick action: ${action}`);
            
            switch (action) {
                case 'start-eol-test':
                    await this.startEOLTest();
                    break;
                case 'robot-home':
                    await this.homeRobot();
                    break;
                case 'check-hardware':
                    await this.checkHardware();
                    break;
                default:
                    console.warn(`Unknown quick action: ${action}`);
            }
            
        } catch (error) {
            console.error(`❌ Quick action ${action} failed:`, error);
            this.handleError(error, `Quick Action: ${action}`);
        }
    }

    /**
     * Start EOL test
     * @private
     * @returns {Promise<void>}
     */
    async startEOLTest() {
        if (this.emergencyStopActive) {
            this.uiManager?.showNotification('Cannot start test: Emergency stop is active', 'warning');
            return;
        }
        
        console.log('🔬 Starting EOL test...');
        await this.navigateToPage('eol-force-test');
        // Additional test start logic will be handled by EOL Force Test Page Manager
    }

    /**
     * Home robot
     * @private
     * @returns {Promise<void>}
     */
    async homeRobot() {
        if (this.emergencyStopActive) {
            this.uiManager?.showNotification('Cannot home robot: Emergency stop is active', 'warning');
            return;
        }
        
        console.log('🏠 Homing robot...');
        await this.navigateToPage('robot-home');
        // Additional robot homing logic will be handled by Robot Home Page Manager
    }

    /**
     * Check hardware status
     * @private
     * @returns {Promise<void>}
     */
    async checkHardware() {
        console.log('🔧 Checking hardware status...');
        this.uiManager?.showLoading('Checking hardware...');
        
        try {
            const status = await this.apiClient.getHardwareStatus();
            this.updateHardwareStatusDisplay(status);
            this.uiManager?.showNotification('Hardware status updated', 'success');
        } catch (error) {
            this.uiManager?.showNotification('Hardware check failed', 'error');
        } finally {
            this.uiManager?.hideLoading();
        }
    }

    /**
     * Handle connection state changes
     * @private
     * @param {boolean} connected - Connection state
     */
    handleConnectionChange(connected) {
        this.isConnected = connected;
        
        const indicator = document.getElementById('connection-indicator');
        const text = document.getElementById('connection-text');
        
        if (indicator && text) {
            if (connected) {
                indicator.className = 'connection-indicator online';
                text.textContent = 'Connected';
            } else {
                indicator.className = 'connection-indicator offline';
                text.textContent = 'Offline';
            }
        }
        
        console.log(`🔗 Connection state changed: ${connected ? 'Connected' : 'Offline'}`);
    }

    /**
     * Handle application errors
     * @private
     * @param {Error|string} error - Error object or message
     * @param {string} context - Error context
     */
    handleError(error, context = 'Unknown') {
        const errorMsg = error instanceof Error ? error.message : String(error);
        const timestamp = new Date().toISOString();
        
        console.error(`❌ [${context}] ${errorMsg}`, error);
        
        // Log error for debugging
        this.logError(error, context, timestamp);
        
        // Show user-friendly error notification
        if (this.uiManager) {
            const userMsg = this.getUserFriendlyErrorMessage(errorMsg, context);
            this.uiManager.showNotification(userMsg, 'error');
        }
    }

    /**
     * Handle unhandled promise rejections
     * @private
     * @param {PromiseRejectionEvent} event - Rejection event
     */
    handleUnhandledRejection(event) {
        console.error('Unhandled Promise Rejection:', event.reason);
        this.handleError(event.reason, 'Promise Rejection');
        event.preventDefault();
    }

    /**
     * Handle before unload event
     * @private
     * @param {Event} event - Before unload event
     */
    handleBeforeUnload(event) {
        // Close WebSocket connection gracefully
        if (this.websocketManager) {
            this.websocketManager.disconnect();
        }
        
        // Stop monitoring services
        if (this.hardwareMonitor) {
            this.hardwareMonitor.stop();
        }
        
        console.log('🔄 Application cleanup completed');
    }

    /**
     * Update system status display
     * @private
     * @param {string} status - Status level (ready, initializing, error, emergency)
     * @param {string} message - Status message
     */
    updateSystemStatus(status, message) {
        const indicator = document.getElementById('status-indicator');
        const text = document.getElementById('status-text');
        const footerStatus = document.getElementById('footer-status');
        
        if (indicator) {
            indicator.className = `status-indicator ${status}`;
        }
        
        if (text) {
            text.textContent = message;
        }
        
        if (footerStatus) {
            footerStatus.textContent = message;
        }
    }

    /**
     * Update hardware status display
     * @private
     * @param {Object} status - Hardware status data
     */
    updateHardwareStatusDisplay(status) {
        const components = ['robot', 'power', 'mcu', 'loadcell'];
        
        components.forEach(component => {
            const element = document.getElementById(`${component}-status`);
            if (element && status[component]) {
                element.textContent = status[component].connected ? 'Connected' : 'Disconnected';
                element.className = `status-value ${status[component].connected ? 'connected' : 'disconnected'}`;
            }
        });
    }

    /**
     * Update last test display
     * @private
     * @param {Array} tests - Recent test data
     */
    updateLastTestDisplay(tests) {
        const element = document.getElementById('last-test-time');
        if (element && tests && tests.length > 0) {
            const lastTest = tests[0];
            const testTime = new Date(lastTest.timestamp).toLocaleString();
            element.textContent = testTime;
        }
    }

    /**
     * Update navigation state
     * @private
     * @param {string} activePage - Currently active page
     */
    updateNavigationState(activePage) {
        // Update active navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.getAttribute('data-page') === activePage);
        });
    }

    /**
     * Get user-friendly error message
     * @private
     * @param {string} errorMsg - Original error message
     * @param {string} context - Error context
     * @returns {string} User-friendly message
     */
    getUserFriendlyErrorMessage(errorMsg, context) {
        const errorMap = {
            'Network Error': 'Unable to connect to server. Please check your connection.',
            'Timeout': 'Operation timed out. Please try again.',
            'Component Initialization': 'Failed to start application components.',
            'Emergency Stop': 'Emergency stop execution failed. Please check system status.',
            'WebSocket': 'Lost connection to server. Attempting to reconnect...',
        };
        
        return errorMap[context] || `An error occurred: ${errorMsg}`;
    }

    /**
     * Log error for debugging
     * @private
     * @param {Error|string} error - Error object or message
     * @param {string} context - Error context
     * @param {string} timestamp - Error timestamp
     */
    logError(error, context, timestamp) {
        // In a real application, this would send errors to a logging service
        const errorLog = {
            timestamp,
            context,
            message: error instanceof Error ? error.message : String(error),
            stack: error instanceof Error ? error.stack : null,
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        // Store in localStorage for debugging (implement proper logging in production)
        try {
            const logs = JSON.parse(localStorage.getItem('wf-eol-error-logs') || '[]');
            logs.push(errorLog);
            // Keep only last 50 errors
            if (logs.length > 50) {
                logs.splice(0, logs.length - 50);
            }
            localStorage.setItem('wf-eol-error-logs', JSON.stringify(logs));
        } catch (e) {
            console.warn('Failed to store error log:', e);
        }
    }

    /**
     * Get application instance (for debugging)
     * @returns {WFEOLTesterApp} Application instance
     */
    static getInstance() {
        return window.wfEolApp;
    }
}

/**
 * Initialize the application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('🚀 DOM loaded, initializing WF EOL Tester...');
        
        // Create application instance
        const app = new WFEOLTesterApp();
        
        // Store globally for debugging
        window.wfEolApp = app;
        
        // Initialize application
        app.init().catch(error => {
            console.error('❌ Failed to initialize application:', error);
        });
        
    } catch (error) {
        console.error('❌ Critical error during application startup:', error);
        
        // Show critical error message
        document.body.innerHTML = `
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                        background: #f8d7da; color: #721c24; padding: 2rem; border-radius: 8px; 
                        border: 1px solid #f5c6cb; font-family: Arial, sans-serif; text-align: center;">
                <h2>🚨 Application Startup Failed</h2>
                <p>The WF EOL Tester web interface failed to start.</p>
                <p>Please refresh the page or contact support.</p>
                <details style="margin-top: 1rem; text-align: left;">
                    <summary>Technical Details</summary>
                    <pre>${error.stack || error.message || error}</pre>
                </details>
            </div>
        `;
    }
});

console.log('📝 Main application module loaded successfully');