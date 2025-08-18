// Common Utilities for WF EOL Tester
// Shared functions across all pages

// Common DOM manipulation utilities
const CommonUtils = {
    // Get element by ID with error handling
    getElementById: function(id) {
        const element = document.getElementById(id);
        if (!element) {
            console.warn(`Element with ID '${id}' not found`);
        }
        return element;
    },

    // Set element text content safely
    setElementText: function(id, text) {
        const element = this.getElementById(id);
        if (element) {
            element.textContent = text;
        }
    },

    // Set element innerHTML safely
    setElementHTML: function(id, html) {
        const element = this.getElementById(id);
        if (element) {
            element.innerHTML = html;
        }
    },

    // Toggle element visibility
    toggleElement: function(id, show = null) {
        const element = this.getElementById(id);
        if (element) {
            if (show === null) {
                element.style.display = element.style.display === 'none' ? 'block' : 'none';
            } else {
                element.style.display = show ? 'block' : 'none';
            }
        }
    },

    // Enable/disable button with visual feedback
    setButtonState: function(id, enabled, text = null) {
        const button = this.getElementById(id);
        if (button) {
            button.disabled = !enabled;
            button.style.opacity = enabled ? '1' : '0.5';
            if (text) {
                button.textContent = text;
            }
        }
    },

    // Update status indicator (dot + text)
    updateStatusIndicator: function(containerId, enabled, enabledText = 'Enabled', disabledText = 'Disabled') {
        const container = this.getElementById(containerId);
        if (container) {
            const statusDot = container.querySelector('.status-dot');
            const statusText = container.querySelector('span');
            
            if (statusDot && statusText) {
                statusText.textContent = enabled ? enabledText : disabledText;
                statusDot.className = enabled ? 'status-dot status-success' : 'status-dot status-error';
            }
        }
    },

    // Format timestamp for logging
    formatTimestamp: function() {
        const now = new Date();
        return `[${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}]`;
    },

    // Add log entry to log viewer
    addLogEntry: function(logViewerId, level, message) {
        const logViewer = this.getElementById(logViewerId);
        if (logViewer) {
            const timestamp = this.formatTimestamp();
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.style.marginBottom = '5px';
            
            const levelClass = level.toLowerCase();
            const levelColor = {
                'info': '#007bff',
                'success': '#28a745', 
                'warning': '#ffc107',
                'error': '#dc3545'
            }[levelClass] || '#6c757d';
            
            logEntry.innerHTML = `
                <span class="timestamp" style="color: #6c757d;">${timestamp}</span>
                <span class="level ${levelClass}" style="color: ${levelColor}; font-weight: bold;">${level.toUpperCase()}</span>
                <span class="message">${message}</span>
            `;
            
            logViewer.appendChild(logEntry);
            logViewer.scrollTop = logViewer.scrollHeight;
            
            // Keep only last 100 entries
            const entries = logViewer.querySelectorAll('.log-entry');
            if (entries.length > 100) {
                logViewer.removeChild(entries[0]);
            }
        }
    },

    // Clear log entries
    clearLog: function(logViewerId) {
        const logViewer = this.getElementById(logViewerId);
        if (logViewer) {
            logViewer.innerHTML = '';
        }
    },

    // Show notification (simple implementation)
    showNotification: function(message, type = 'info', duration = 3000) {
        console.log(`📢 [${type.toUpperCase()}] ${message}`);
        // Could be enhanced with actual notification UI later
    },

    // Format numbers with units
    formatValue: function(value, unit = '', decimals = 3) {
        if (value === null || value === undefined || isNaN(value)) {
            return `---.---${unit ? ' ' + unit : ''}`;
        }
        return `${parseFloat(value).toFixed(decimals)}${unit ? ' ' + unit : ''}`;
    },

    // Tab switching utility
    switchTab: function(tabButtons, tabContents, activeTabId) {
        // Update button states
        tabButtons.forEach(btn => {
            if (btn.getAttribute('data-tab') === activeTabId) {
                btn.style.background = '#007bff';
                btn.style.color = 'white';
                btn.classList.add('active');
            } else {
                btn.style.background = '#f8f9fa';
                btn.style.color = '#495057';
                btn.classList.remove('active');
            }
        });
        
        // Update tab content visibility
        tabContents.forEach(content => {
            if (content.id === activeTabId + '-tab') {
                content.style.display = 'block';
                content.classList.add('active');
            } else {
                content.style.display = 'none';
                content.classList.remove('active');
            }
        });
    }
};

// Global utility functions for backward compatibility
function getElementById(id) {
    return CommonUtils.getElementById(id);
}

function addLogEntry(level, message, logViewerId = 'operations-log-viewer') {
    CommonUtils.addLogEntry(logViewerId, level, message);
}

function showNotification(message, type = 'info', duration = 3000) {
    CommonUtils.showNotification(message, type, duration);
}

function updateUIBasedOnConnectionState(connected) {
    console.log(`🔧 [COMMON] Connection state changed: ${connected}`);
    // This can be overridden by specific pages
}

// Make CommonUtils globally available
window.CommonUtils = CommonUtils;

console.log('✅ [COMMON] Common utilities loaded and ready');