/**
 * UI Manager Component - WF EOL Tester Web Interface
 * 
 * This component manages the overall user interface including:
 * - DOM manipulation and updates with efficient rendering
 * - Page navigation and routing management
 * - Modal dialogs and notification systems
 * - Layout management and responsive behavior
 * - Loading states and progress indicators
 * - Form validation and data handling
 * - Theme switching and customization
 * - Component lifecycle management
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

/**
 * Notification types
 */
const NotificationType = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
};

/**
 * UI Manager with comprehensive interface management
 * 
 * Implements Clean Architecture principles with proper separation of concerns.
 * Manages all user interface interactions and visual feedback.
 */
export class UIManager {
    /**
     * Initialize UI Manager
     */
    constructor() {
        console.log('🔧 UI Manager initializing...');
        
        // Component registry
        this.components = new Map();
        this.pages = new Map();
        this.currentPage = 'welcome-page';
        
        // Modal management
        this.modals = new Map();
        this.activeModal = null;
        
        // Notification system
        this.notifications = [];
        this.notificationId = 0;
        this.maxNotifications = 5;
        
        // Loading states
        this.loadingStates = new Set();
        this.loadingOverlay = null;
        
        // Form handling
        this.validators = new Map();
        this.formData = new Map();
        
        // Event handling
        this.eventListeners = new Map();
        
        // Theme management
        this.currentTheme = 'default';
        this.themes = new Map();
        
        // Animation settings
        this.animationDuration = 300;
        this.animationsEnabled = true;
        
        // Initialize UI
        this.init();
        
        console.log('✅ UI Manager initialized');
    }

    /**
     * Initialize UI Manager
     * @private
     */
    init() {
        try {
            // Setup loading overlay
            this.setupLoadingOverlay();
            
            // Setup modal container
            this.setupModalContainer();
            
            // Setup notification container
            this.setupNotificationContainer();
            
            // Setup responsive behavior
            this.setupResponsiveBehavior();
            
            // Setup keyboard shortcuts
            this.setupKeyboardShortcuts();
            
            // Initialize default theme
            this.initializeThemes();
            
            console.log('✅ UI Manager initialization complete');
            
        } catch (error) {
            console.error('❌ UI Manager initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup loading overlay
     * @private
     */
    setupLoadingOverlay() {
        this.loadingOverlay = document.getElementById('loading-overlay');
        if (!this.loadingOverlay) {
            this.loadingOverlay = this.createElement('div', ['loading-overlay'], {
                id: 'loading-overlay',
                style: 'display: none;'
            });
            
            this.loadingOverlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <div class="loading-text">Loading...</div>
                </div>
            `;
            
            document.body.appendChild(this.loadingOverlay);
        }
    }

    /**
     * Setup modal container
     * @private
     */
    setupModalContainer() {
        let modalContainer = document.getElementById('modal-container');
        if (!modalContainer) {
            modalContainer = this.createElement('div', ['modal-container'], {
                id: 'modal-container',
                style: 'display: none;'
            });
            document.body.appendChild(modalContainer);
        }
    }

    /**
     * Setup notification container
     * @private
     */
    setupNotificationContainer() {
        let notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            notificationContainer = this.createElement('div', ['notification-container'], {
                id: 'notification-container'
            });
            document.body.appendChild(notificationContainer);
        }
    }

    /**
     * Setup responsive behavior
     * @private
     */
    setupResponsiveBehavior() {
        // Handle window resize
        window.addEventListener('resize', this.handleResize.bind(this));
        
        // Handle orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(this.handleResize.bind(this), 100);
        });
        
        // Initial responsive check
        this.handleResize();
    }

    /**
     * Setup keyboard shortcuts
     * @private
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // ESC key closes modals
            if (event.key === 'Escape' && this.activeModal) {
                this.hideModal();
            }
            
            // Ctrl+/ shows help (if available)
            if (event.ctrlKey && event.key === '/') {
                event.preventDefault();
                this.showHelp();
            }
        });
    }

    /**
     * Initialize theme system
     * @private
     */
    initializeThemes() {
        // Default theme
        this.themes.set('default', {
            name: 'Default',
            cssClass: 'theme-default',
            variables: {
                '--primary-color': '#007bff',
                '--secondary-color': '#6c757d',
                '--success-color': '#28a745',
                '--danger-color': '#dc3545',
                '--warning-color': '#ffc107',
                '--info-color': '#17a2b8'
            }
        });
        
        // Dark theme
        this.themes.set('dark', {
            name: 'Dark',
            cssClass: 'theme-dark',
            variables: {
                '--primary-color': '#0d6efd',
                '--secondary-color': '#6c757d',
                '--success-color': '#198754',
                '--danger-color': '#dc3545',
                '--warning-color': '#ffc107',
                '--info-color': '#0dcaf0'
            }
        });
        
        // Apply default theme
        this.applyTheme('default');
    }

    // =========================
    // Page Management
    // =========================

    /**
     * Switch to a different page
     * @param {string} pageId - Page identifier
     * @param {Object} options - Navigation options
     */
    async switchPage(pageId, options = {}) {
        try {
            console.log(`🔄 Switching to page: ${pageId}`);
            console.log(`🔄 Current page: ${this.currentPage}`);
            
            // Validate page exists
            if (!this.isValidPage(pageId)) {
                console.warn(`⚠️ Page ${pageId} does not exist, creating from template`);
                await this.createPagePlaceholder(pageId);
            } else {
                console.log(`✅ Page ${pageId} already exists in DOM`);
            }
            
            // Hide current page
            console.log(`🔧 Hiding current page: ${this.currentPage}`);
            this.hidePage(this.currentPage, options);
            
            // Show new page
            console.log(`🔧 Showing new page: ${pageId}`);
            this.showPage(pageId, options);
            
            // Update current page
            this.currentPage = pageId;
            
            // Update navigation state
            this.updateNavigationState(pageId);
            
            // Final verification
            const newPageElement = document.getElementById(pageId);
            if (newPageElement && newPageElement.style.display !== 'none') {
                console.log(`✅ Successfully switched to page: ${pageId}`);
                console.log(`✅ Page is visible with classes: ${newPageElement.className}`);
            } else {
                console.error(`❌ Page switch verification failed for ${pageId}`);
                if (newPageElement) {
                    console.error(`❌ Page exists but has display: ${newPageElement.style.display}`);
                } else {
                    console.error(`❌ Page element not found after switch`);
                }
            }
            
        } catch (error) {
            console.error(`❌ Failed to switch to page ${pageId}:`, error);
            throw error;
        }
    }

    /**
     * Check if page is valid
     * @private
     * @param {string} pageId - Page identifier
     * @returns {boolean} True if page exists
     */
    isValidPage(pageId) {
        const element = document.getElementById(pageId) || 
                      document.querySelector(`[data-page="${pageId}"]`);
        return element !== null;
    }

    /**
     * Load page template from server
     * @param {string} pageId - Page identifier
     * @returns {Promise<string>} Page HTML content
     */
    async loadPageTemplate(pageId) {
        try {
            console.log(`🔄 Loading template for ${pageId} from /templates/pages/${pageId}.html`);
            const response = await fetch(`/templates/pages/${pageId}.html?v=${Date.now()}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const templateContent = await response.text();
            console.log(`✅ Template loaded successfully for ${pageId}, content length: ${templateContent.length}`);
            return templateContent;
        } catch (error) {
            console.error(`❌ Failed to load template for ${pageId}:`, error);
            console.error(`❌ Template URL: /templates/pages/${pageId}.html`);
            return null;
        }
    }

    /**
     * Create page placeholder
     * @private
     * @param {string} pageId - Page identifier
     */
    async createPagePlaceholder(pageId) {
        const contentArea = document.getElementById('dynamic-content') || 
                           document.getElementById('app-content');
        
        if (!contentArea) return;

        // Try to load page template first
        const template = await this.loadPageTemplate(pageId);
        
        if (template) {
            // Insert loaded template
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = template;
            const pageElement = tempDiv.firstElementChild;
            
            if (pageElement) {
                console.log(`🔧 Inserting template element for ${pageId} with ID: ${pageElement.id}`);
                contentArea.appendChild(pageElement);
                
                // Verify insertion
                const inserted = document.getElementById(pageElement.id);
                if (inserted) {
                    console.log(`✅ Template successfully inserted for page: ${pageId}`);
                    console.log(`✅ Element ID: ${pageElement.id}, Classes: ${pageElement.className}`);
                    return;
                } else {
                    console.error(`❌ Failed to verify template insertion for ${pageId}`);
                }
            } else {
                console.error(`❌ No element found in template for ${pageId}`);
            }
        }

        // Fallback to placeholder if template loading failed
        const pageElement = this.createElement('div', ['content-page'], {
            id: pageId,
            'data-page': pageId,
            style: 'display: none;'
        });
        
        pageElement.innerHTML = `
            <div class="page-placeholder">
                <h2>🚨 ${this.formatPageTitle(pageId)} - Template Loading Failed</h2>
                <p><strong>DEBUG INFO:</strong> Template not loaded from /templates/pages/${pageId}.html</p>
                <p>Page ID: <code>${pageId}</code></p>
                <p>Check browser console for detailed error information.</p>
            </div>
        `;
        
        contentArea.appendChild(pageElement);
    }

    /**
     * Format page title from ID
     * @private
     * @param {string} pageId - Page identifier
     * @returns {string} Formatted title
     */
    formatPageTitle(pageId) {
        return pageId
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    /**
     * Hide page with animation
     * @private
     * @param {string} pageId - Page identifier
     * @param {Object} options - Animation options
     */
    hidePage(pageId, options = {}) {
        const page = document.getElementById(pageId);
        if (!page) return;
        
        if (this.animationsEnabled) {
            page.style.opacity = '0';
            setTimeout(() => {
                page.style.display = 'none';
                page.classList.remove('active');
            }, this.animationDuration);
        } else {
            page.style.display = 'none';
            page.classList.remove('active');
        }
    }

    /**
     * Show page with animation
     * @private
     * @param {string} pageId - Page identifier
     * @param {Object} options - Animation options
     */
    showPage(pageId, options = {}) {
        const page = document.getElementById(pageId);
        if (!page) return;
        
        page.style.display = 'block';
        page.classList.add('active');
        
        if (this.animationsEnabled) {
            page.style.opacity = '0';
            setTimeout(() => {
                page.style.opacity = '1';
            }, 50);
        } else {
            page.style.opacity = '1';
        }
        
        // Scroll to top
        window.scrollTo(0, 0);
    }

    /**
     * Update navigation state
     * @private
     * @param {string} activePageId - Active page identifier
     */
    updateNavigationState(activePageId) {
        // Update navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            const pageId = link.getAttribute('data-page');
            link.classList.toggle('active', pageId === activePageId);
        });
        
        // Update breadcrumb if exists
        this.updateBreadcrumb(activePageId);
    }

    /**
     * Update breadcrumb navigation
     * @private
     * @param {string} pageId - Current page identifier
     */
    updateBreadcrumb(pageId) {
        const breadcrumb = document.querySelector('.breadcrumb');
        if (breadcrumb) {
            breadcrumb.innerHTML = `
                <li><a href="#" data-page="welcome-page">Home</a></li>
                <li class="active">${this.formatPageTitle(pageId)}</li>
            `;
        }
    }

    // =========================
    // Modal Management
    // =========================

    /**
     * Show modal dialog
     * @param {Object|string} config - Modal configuration or ID
     * @returns {Promise<any>} Modal result
     */
    async showModal(config) {
        return new Promise((resolve, reject) => {
            try {
                // Normalize config
                const modalConfig = typeof config === 'string' ? { title: config } : config;
                const {
                    title = 'Dialog',
                    message = '',
                    type = 'info',
                    buttons = [{ text: 'OK', action: 'ok' }],
                    closable = true,
                    size = 'medium'
                } = modalConfig;
                
                // Create modal ID
                const modalId = `modal-${Date.now()}`;
                
                // Create modal HTML
                const modalHtml = this.createModalHtml(modalId, {
                    title,
                    message,
                    type,
                    buttons,
                    closable,
                    size
                });
                
                // Insert modal
                const modalContainer = document.getElementById('modal-container');
                modalContainer.innerHTML = modalHtml;
                modalContainer.style.display = 'flex';
                
                // Setup modal event handlers
                this.setupModalEventHandlers(modalId, resolve, reject);
                
                // Animate in
                if (this.animationsEnabled) {
                    const modal = document.querySelector('.modal');
                    modal.style.opacity = '0';
                    modal.style.transform = 'scale(0.9)';
                    
                    setTimeout(() => {
                        modal.style.opacity = '1';
                        modal.style.transform = 'scale(1)';
                    }, 50);
                }
                
                // Set active modal
                this.activeModal = modalId;
                
                // Focus first button
                setTimeout(() => {
                    const firstButton = modalContainer.querySelector('button');
                    if (firstButton) firstButton.focus();
                }, 100);
                
            } catch (error) {
                console.error('❌ Failed to show modal:', error);
                reject(error);
            }
        });
    }

    /**
     * Create modal HTML
     * @private
     * @param {string} modalId - Modal identifier
     * @param {Object} config - Modal configuration
     * @returns {string} Modal HTML
     */
    createModalHtml(modalId, config) {
        const { title, message, type, buttons, closable, size } = config;
        
        const typeIcon = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            question: '❓'
        }[type] || 'ℹ️';
        
        const buttonHtml = buttons.map(button => `
            <button class="btn btn-${button.variant || 'primary'}" 
                    data-action="${button.action}" 
                    ${button.default ? 'data-default="true"' : ''}>
                ${button.text}
            </button>
        `).join('');
        
        return `
            <div class="modal-overlay" data-modal-id="${modalId}">
                <div class="modal modal-${size} modal-${type}">
                    ${closable ? `
                        <button class="modal-close" data-action="close" aria-label="Close">
                            ×
                        </button>
                    ` : ''}
                    <div class="modal-header">
                        <h3 class="modal-title">
                            <span class="modal-icon">${typeIcon}</span>
                            ${title}
                        </h3>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        ${buttonHtml}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Setup modal event handlers
     * @private
     * @param {string} modalId - Modal identifier
     * @param {Function} resolve - Promise resolve function
     * @param {Function} reject - Promise reject function
     */
    setupModalEventHandlers(modalId, resolve, reject) {
        const modalContainer = document.getElementById('modal-container');
        
        // Button click handler
        const handleButtonClick = (event) => {
            const action = event.target.getAttribute('data-action');
            if (action) {
                this.hideModal().then(() => {
                    resolve({ action, modalId });
                }).catch(reject);
            }
        };
        
        // Overlay click handler
        const handleOverlayClick = (event) => {
            if (event.target.classList.contains('modal-overlay')) {
                this.hideModal().then(() => {
                    resolve({ action: 'backdrop', modalId });
                }).catch(reject);
            }
        };
        
        // Add event listeners
        modalContainer.addEventListener('click', handleButtonClick);
        modalContainer.addEventListener('click', handleOverlayClick);
        
        // Store cleanup function
        this.modals.set(modalId, () => {
            modalContainer.removeEventListener('click', handleButtonClick);
            modalContainer.removeEventListener('click', handleOverlayClick);
        });
    }

    /**
     * Hide current modal
     * @returns {Promise<void>}
     */
    async hideModal() {
        if (!this.activeModal) return;
        
        return new Promise((resolve) => {
            const modalContainer = document.getElementById('modal-container');
            const modal = modalContainer.querySelector('.modal');
            
            if (this.animationsEnabled && modal) {
                modal.style.opacity = '0';
                modal.style.transform = 'scale(0.9)';
                
                setTimeout(() => {
                    modalContainer.style.display = 'none';
                    modalContainer.innerHTML = '';
                    resolve();
                }, this.animationDuration);
            } else {
                modalContainer.style.display = 'none';
                modalContainer.innerHTML = '';
                resolve();
            }
            
            // Cleanup
            const cleanup = this.modals.get(this.activeModal);
            if (cleanup) {
                cleanup();
                this.modals.delete(this.activeModal);
            }
            
            this.activeModal = null;
        });
    }

    // =========================
    // Notification Management
    // =========================

    /**
     * Show notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type
     * @param {number} duration - Duration in milliseconds
     * @returns {string} Notification ID
     */
    showNotification(message, type = NotificationType.INFO, duration = 5000) {
        const notificationId = `notification-${++this.notificationId}`;
        
        console.log(`📢 Showing ${type} notification:`, message);
        
        const notification = {
            id: notificationId,
            message,
            type,
            timestamp: Date.now(),
            duration
        };
        
        // Add to notifications array
        this.notifications.push(notification);
        
        // Remove oldest if exceeding max
        if (this.notifications.length > this.maxNotifications) {
            const oldestId = this.notifications.shift().id;
            this.removeNotificationElement(oldestId);
        }
        
        // Create and show notification element
        this.createNotificationElement(notification);
        
        // Auto-hide after duration
        if (duration > 0) {
            setTimeout(() => {
                this.hideNotification(notificationId);
            }, duration);
        }
        
        return notificationId;
    }

    /**
     * Create notification element
     * @private
     * @param {Object} notification - Notification object
     */
    createNotificationElement(notification) {
        const container = document.getElementById('notification-container');
        
        const typeIcon = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        }[notification.type] || 'ℹ️';
        
        const element = this.createElement('div', 
            ['notification', `notification-${notification.type}`], 
            {
                id: notification.id,
                'data-type': notification.type
            }
        );
        
        element.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${typeIcon}</span>
                <span class="notification-message">${notification.message}</span>
                <button class="notification-close" onclick="window.wfEolApp?.uiManager?.hideNotification('${notification.id}')" aria-label="Close">
                    ×
                </button>
            </div>
        `;
        
        container.appendChild(element);
        
        // Animate in
        if (this.animationsEnabled) {
            element.style.opacity = '0';
            element.style.transform = 'translateX(100%)';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateX(0)';
            }, 50);
        }
    }

    /**
     * Hide notification
     * @param {string} notificationId - Notification identifier
     */
    hideNotification(notificationId) {
        const element = document.getElementById(notificationId);
        if (!element) return;
        
        if (this.animationsEnabled) {
            element.style.opacity = '0';
            element.style.transform = 'translateX(100%)';
            
            setTimeout(() => {
                this.removeNotificationElement(notificationId);
            }, this.animationDuration);
        } else {
            this.removeNotificationElement(notificationId);
        }
        
        // Remove from notifications array
        this.notifications = this.notifications.filter(n => n.id !== notificationId);
    }

    /**
     * Remove notification element
     * @private
     * @param {string} notificationId - Notification identifier
     */
    removeNotificationElement(notificationId) {
        const element = document.getElementById(notificationId);
        if (element) {
            element.remove();
        }
    }

    /**
     * Clear all notifications
     */
    clearNotifications() {
        this.notifications.forEach(notification => {
            this.hideNotification(notification.id);
        });
        this.notifications = [];
    }

    // =========================
    // Loading States
    // =========================

    /**
     * Show loading overlay
     * @param {string} message - Loading message
     */
    showLoading(message = 'Loading...') {
        if (this.loadingOverlay) {
            const textElement = this.loadingOverlay.querySelector('.loading-text');
            if (textElement) {
                textElement.textContent = message;
            }
            this.loadingOverlay.style.display = 'flex';
            
            if (this.animationsEnabled) {
                this.loadingOverlay.style.opacity = '0';
                setTimeout(() => {
                    this.loadingOverlay.style.opacity = '1';
                }, 50);
            }
        }
        
        console.log(`⏳ Loading: ${message}`);
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        if (this.loadingOverlay) {
            if (this.animationsEnabled) {
                this.loadingOverlay.style.opacity = '0';
                setTimeout(() => {
                    this.loadingOverlay.style.display = 'none';
                }, this.animationDuration);
            } else {
                this.loadingOverlay.style.display = 'none';
            }
        }
        
        console.log('✅ Loading hidden');
    }

    /**
     * Show loading for specific element
     * @param {string|Element} element - Element or selector
     * @param {string} message - Loading message
     */
    showElementLoading(element, message = 'Loading...') {
        const targetElement = typeof element === 'string' ? 
            document.querySelector(element) : element;
        
        if (!targetElement) return;
        
        const loadingId = `loading-${Date.now()}`;
        targetElement.setAttribute('data-loading', loadingId);
        this.loadingStates.add(loadingId);
        
        // Create loading indicator
        const loadingElement = this.createElement('div', ['element-loading'], {
            'data-loading-id': loadingId
        });
        
        loadingElement.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <div class="loading-text">${message}</div>
            </div>
        `;
        
        targetElement.appendChild(loadingElement);
    }

    /**
     * Hide loading for specific element
     * @param {string|Element} element - Element or selector
     */
    hideElementLoading(element) {
        const targetElement = typeof element === 'string' ? 
            document.querySelector(element) : element;
        
        if (!targetElement) return;
        
        const loadingId = targetElement.getAttribute('data-loading');
        if (loadingId) {
            const loadingElement = targetElement.querySelector(`[data-loading-id="${loadingId}"]`);
            if (loadingElement) {
                loadingElement.remove();
            }
            
            targetElement.removeAttribute('data-loading');
            this.loadingStates.delete(loadingId);
        }
    }

    // =========================
    // Theme Management
    // =========================

    /**
     * Apply theme
     * @param {string} themeName - Theme name
     */
    applyTheme(themeName) {
        const theme = this.themes.get(themeName);
        if (!theme) {
            console.warn(`Theme ${themeName} not found`);
            return;
        }
        
        // Remove existing theme classes
        document.body.classList.remove(...Array.from(this.themes.values()).map(t => t.cssClass));
        
        // Add new theme class
        document.body.classList.add(theme.cssClass);
        
        // Apply CSS variables
        const root = document.documentElement;
        Object.entries(theme.variables).forEach(([property, value]) => {
            root.style.setProperty(property, value);
        });
        
        this.currentTheme = themeName;
        console.log(`🎨 Applied theme: ${theme.name}`);
    }

    /**
     * Toggle between light and dark theme
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'default' ? 'dark' : 'default';
        this.applyTheme(newTheme);
    }

    // =========================
    // Utility Methods
    // =========================

    /**
     * Create DOM element
     * @param {string} tag - Element tag
     * @param {Array} classes - CSS classes
     * @param {Object} attributes - Element attributes
     * @returns {HTMLElement} Created element
     */
    createElement(tag, classes = [], attributes = {}) {
        const element = document.createElement(tag);
        
        if (classes.length > 0) {
            element.classList.add(...classes);
        }
        
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'style') {
                element.style.cssText = value;
            } else {
                element.setAttribute(key, value);
            }
        });
        
        return element;
    }

    /**
     * Update element content safely
     * @param {string|Element} element - Element or selector
     * @param {string} content - New content
     * @param {boolean} isHtml - Whether content is HTML
     */
    updateElement(element, content, isHtml = false) {
        const targetElement = typeof element === 'string' ? 
            document.querySelector(element) : element;
        
        if (!targetElement) return;
        
        if (isHtml) {
            targetElement.innerHTML = content;
        } else {
            targetElement.textContent = content;
        }
    }

    /**
     * Handle window resize
     * @private
     */
    handleResize() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        // Update CSS custom properties
        document.documentElement.style.setProperty('--viewport-width', `${width}px`);
        document.documentElement.style.setProperty('--viewport-height', `${height}px`);
        
        // Update responsive classes
        document.body.classList.toggle('mobile', width < 768);
        document.body.classList.toggle('tablet', width >= 768 && width < 1024);
        document.body.classList.toggle('desktop', width >= 1024);
    }

    /**
     * Show help dialog (placeholder)
     * @private
     */
    showHelp() {
        this.showModal({
            title: '❓ Help',
            message: `
                <h4>Keyboard Shortcuts</h4>
                <ul>
                    <li><kbd>Esc</kbd> - Close modal dialogs</li>
                    <li><kbd>Ctrl+/</kbd> - Show this help dialog</li>
                </ul>
                <h4>Navigation</h4>
                <p>Use the sidebar menu to navigate between different sections of the application.</p>
            `,
            buttons: [{ text: 'Got it!', action: 'ok' }]
        });
    }

    /**
     * Get current UI state
     * @returns {Object} UI state information
     */
    getState() {
        return {
            currentPage: this.currentPage,
            activeModal: this.activeModal,
            notificationCount: this.notifications.length,
            loadingStates: this.loadingStates.size,
            currentTheme: this.currentTheme,
            animationsEnabled: this.animationsEnabled
        };
    }
}

// Export notification types for use by other modules
export { NotificationType };

console.log('📝 UI Manager component loaded successfully');