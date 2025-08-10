/**
 * Log Formatter Utility - WF EOL Tester Web Interface
 * 
 * This utility provides comprehensive log message formatting capabilities including:
 * - Timestamp formatting with multiple display options
 * - Syntax highlighting for different message types
 * - Message content parsing and structure detection
 * - Color coding for severity levels and sources
 * - Performance-optimized formatting with caching
 * - Internationalization support for timestamps
 * - Message truncation and expansion handling
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

/**
 * Timestamp format configurations
 */
const TimestampFormat = {
    TIME_ONLY: { 
        pattern: 'HH:mm:ss',
        options: { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            hour12: false
        }
    },
    TIME_WITH_MS: { 
        pattern: 'HH:mm:ss.SSS',
        options: { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            fractionalSecondDigits: 3,
            hour12: false
        }
    },
    DATE_TIME: { 
        pattern: 'YYYY-MM-DD HH:mm:ss',
        options: { 
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            hour12: false
        }
    },
    DATE_TIME_MS: { 
        pattern: 'YYYY-MM-DD HH:mm:ss.SSS',
        options: { 
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            fractionalSecondDigits: 3,
            hour12: false
        }
    },
    ISO: { 
        pattern: 'ISO 8601',
        options: null // Use toISOString()
    },
    RELATIVE: { 
        pattern: 'Relative',
        options: null // Custom relative time calculation
    },
    UNIX: { 
        pattern: 'Unix Timestamp',
        options: null // Show raw timestamp
    }
};

/**
 * Message type patterns for syntax highlighting
 */
const MessagePatterns = {
    // JSON detection
    JSON: {
        pattern: /^\s*[\{\[].+[\}\]]\s*$/s,
        highlight: 'json'
    },
    
    // XML detection
    XML: {
        pattern: /^\s*<[\s\S]*>\s*$/,
        highlight: 'xml'
    },
    
    // SQL detection
    SQL: {
        pattern: /\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|FROM|WHERE|JOIN|GROUP BY|ORDER BY)\b/i,
        highlight: 'sql'
    },
    
    // URL detection
    URL: {
        pattern: /https?:\/\/[^\s]+/g,
        highlight: 'url'
    },
    
    // File path detection
    FILE_PATH: {
        pattern: /(?:[a-zA-Z]:\\|\/)(?:[^\s\\\/]+[\\\/])*[^\s\\\/]*\.[a-zA-Z0-9]+/g,
        highlight: 'file-path'
    },
    
    // IP Address detection
    IP_ADDRESS: {
        pattern: /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g,
        highlight: 'ip-address'
    },
    
    // Numeric values
    NUMBER: {
        pattern: /\b-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b/g,
        highlight: 'number'
    },
    
    // Boolean values
    BOOLEAN: {
        pattern: /\b(true|false|True|False|TRUE|FALSE)\b/g,
        highlight: 'boolean'
    },
    
    // Null values
    NULL: {
        pattern: /\b(null|NULL|None|nil|NIL)\b/g,
        highlight: 'null'
    },
    
    // Stack trace detection
    STACK_TRACE: {
        pattern: /^\s*at\s+.+\s+\(.+:\d+:\d+\)$/gm,
        highlight: 'stack-trace'
    },
    
    // Exception detection
    EXCEPTION: {
        pattern: /Exception|Error|RuntimeError|ValueError|TypeError|KeyError|IndexError|AttributeError/g,
        highlight: 'exception'
    },
    
    // Status codes
    STATUS_CODE: {
        pattern: /\b[1-5]\d{2}\b/g,
        highlight: 'status-code'
    },
    
    // Duration/time values
    DURATION: {
        pattern: /\b\d+(?:\.\d+)?\s*(ms|μs|ns|s|sec|min|hour|hr|h)\b/g,
        highlight: 'duration'
    },
    
    // Memory sizes
    MEMORY_SIZE: {
        pattern: /\b\d+(?:\.\d+)?\s*(B|KB|MB|GB|TB|bytes?)\b/gi,
        highlight: 'memory-size'
    },
    
    // Percentage values
    PERCENTAGE: {
        pattern: /\b\d+(?:\.\d+)?%\b/g,
        highlight: 'percentage'
    },
    
    // Thread/Process IDs
    THREAD_ID: {
        pattern: /\b(?:thread|Thread|TID|PID|pid)\s*[:#]?\s*\d+\b/g,
        highlight: 'thread-id'
    },
    
    // Log levels in message content
    LOG_LEVEL: {
        pattern: /\b(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL|TRACE)\b/g,
        highlight: 'log-level'
    }
};

/**
 * Color schemes for different themes
 */
const ColorScheme = {
    DARK: {
        json: '#98d982',
        xml: '#f97583',
        sql: '#79b8ff',
        url: '#79b8ff',
        'file-path': '#ffab70',
        'ip-address': '#b392f0',
        number: '#79b8ff',
        boolean: '#f97583',
        null: '#959da5',
        'stack-trace': '#ff6b6b',
        exception: '#ff6347',
        'status-code': '#ffab70',
        duration: '#85e89d',
        'memory-size': '#ffd33d',
        percentage: '#85e89d',
        'thread-id': '#b392f0',
        'log-level': '#ffd33d'
    },
    
    LIGHT: {
        json: '#22863a',
        xml: '#d73a49',
        sql: '#005cc5',
        url: '#0366d6',
        'file-path': '#e36209',
        'ip-address': '#6f42c1',
        number: '#005cc5',
        boolean: '#d73a49',
        null: '#6a737d',
        'stack-trace': '#d73a49',
        exception: '#d73a49',
        'status-code': '#e36209',
        duration: '#28a745',
        'memory-size': '#f9c513',
        percentage: '#28a745',
        'thread-id': '#6f42c1',
        'log-level': '#f9c513'
    }
};

/**
 * Log Formatter Class
 * 
 * Provides comprehensive formatting for log messages with performance
 * optimizations and extensive customization options.
 */
export class LogFormatter {
    /**
     * Initialize log formatter
     * @param {Object} config - Configuration options
     */
    constructor(config = {}) {
        console.log('🎨 Initializing Log Formatter...');
        
        // Configuration
        this.config = {
            timestampFormat: 'TIME_WITH_MS',
            enableSyntaxHighlighting: true,
            enableLineNumbers: false,
            maxMessageLength: 1000,
            expandableThreshold: 500,
            theme: 'DARK',
            locale: 'en-US',
            timezone: 'local',
            enableCaching: true,
            cacheSize: 1000,
            enablePerformanceMetrics: false,
            ...config
        };
        
        // Performance monitoring
        this.metrics = {
            formatCalls: 0,
            cacheHits: 0,
            totalFormatTime: 0,
            averageFormatTime: 0
        };
        
        // Caching system
        this.formatCache = new Map();
        this.timestampCache = new Map();
        this.highlightCache = new Map();
        
        // Color scheme
        this.colors = ColorScheme[this.config.theme] || ColorScheme.DARK;
        
        // Initialize timezone handling
        this.initializeTimezone();
        
        console.log('✅ Log Formatter initialized');
    }
    
    /**
     * Initialize timezone handling
     * @private
     */
    initializeTimezone() {
        try {
            // Detect user timezone if not specified
            if (this.config.timezone === 'local') {
                this.config.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            }
            
            // Validate timezone
            try {
                Intl.DateTimeFormat(this.config.locale, { timeZone: this.config.timezone });
            } catch (error) {
                console.warn('Invalid timezone, falling back to UTC:', this.config.timezone);
                this.config.timezone = 'UTC';
            }
            
        } catch (error) {
            console.warn('Timezone initialization failed:', error);
            this.config.timezone = 'UTC';
        }
    }
    
    /**
     * Format timestamp according to configuration
     * @param {number|string|Date} timestamp - Timestamp to format
     * @param {string} [format] - Optional format override
     * @returns {string} Formatted timestamp
     */
    formatTimestamp(timestamp, format = null) {
        const formatType = format || this.config.timestampFormat;
        
        // Check cache first
        if (this.config.enableCaching) {
            const cacheKey = `${timestamp}_${formatType}`;
            if (this.timestampCache.has(cacheKey)) {
                return this.timestampCache.get(cacheKey);
            }
        }
        
        const startTime = this.config.enablePerformanceMetrics ? performance.now() : 0;
        
        try {
            let result;
            const date = new Date(timestamp);
            
            // Validate date
            if (isNaN(date.getTime())) {
                result = 'Invalid Date';
            } else {
                const formatConfig = TimestampFormat[formatType];
                
                if (!formatConfig) {
                    result = date.toLocaleString(this.config.locale);
                } else {
                    switch (formatType) {
                        case 'ISO':
                            result = date.toISOString();
                            break;
                            
                        case 'RELATIVE':
                            result = this.formatRelativeTime(date);
                            break;
                            
                        case 'UNIX':
                            result = date.getTime().toString();
                            break;
                            
                        default:
                            // Handle milliseconds manually for better control
                            if (formatType.includes('MS')) {
                                const baseOptions = { ...formatConfig.options };
                                delete baseOptions.fractionalSecondDigits;
                                
                                const baseTime = date.toLocaleString(this.config.locale, {
                                    ...baseOptions,
                                    timeZone: this.config.timezone
                                });
                                
                                const ms = date.getMilliseconds().toString().padStart(3, '0');
                                result = `${baseTime}.${ms}`;
                            } else {
                                result = date.toLocaleString(this.config.locale, {
                                    ...formatConfig.options,
                                    timeZone: this.config.timezone
                                });
                            }
                    }
                }
            }
            
            // Cache result
            if (this.config.enableCaching) {
                const cacheKey = `${timestamp}_${formatType}`;
                this.timestampCache.set(cacheKey, result);
                
                // Limit cache size
                if (this.timestampCache.size > this.config.cacheSize) {
                    const firstKey = this.timestampCache.keys().next().value;
                    this.timestampCache.delete(firstKey);
                }
            }
            
            // Record performance metrics
            if (this.config.enablePerformanceMetrics) {
                const endTime = performance.now();
                this.updateMetrics(endTime - startTime);
            }
            
            return result;
            
        } catch (error) {
            console.warn('Timestamp formatting failed:', error);
            return new Date(timestamp).toString();
        }
    }
    
    /**
     * Format relative time (e.g., "2 minutes ago")
     * @private
     * @param {Date} date - Date to format
     * @returns {string} Relative time string
     */
    formatRelativeTime(date) {
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        
        // If in the future
        if (diff < 0) {
            return 'in the future';
        }
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (seconds < 60) {
            return seconds === 1 ? '1 second ago' : `${seconds} seconds ago`;
        } else if (minutes < 60) {
            return minutes === 1 ? '1 minute ago' : `${minutes} minutes ago`;
        } else if (hours < 24) {
            return hours === 1 ? '1 hour ago' : `${hours} hours ago`;
        } else {
            return days === 1 ? '1 day ago' : `${days} days ago`;
        }
    }
    
    /**
     * Apply syntax highlighting to message content
     * @param {string} message - Message to highlight
     * @returns {string} Highlighted message HTML
     */
    applySyntaxHighlighting(message) {
        if (!this.config.enableSyntaxHighlighting || !message) {
            return this.escapeHtml(message);
        }
        
        // Check cache first
        if (this.config.enableCaching) {
            if (this.highlightCache.has(message)) {
                return this.highlightCache.get(message);
            }
        }
        
        const startTime = this.config.enablePerformanceMetrics ? performance.now() : 0;
        
        let highlighted = this.escapeHtml(message);
        
        // Apply patterns in order of priority
        const patterns = [
            MessagePatterns.JSON,
            MessagePatterns.XML,
            MessagePatterns.SQL,
            MessagePatterns.STACK_TRACE,
            MessagePatterns.EXCEPTION,
            MessagePatterns.URL,
            MessagePatterns.FILE_PATH,
            MessagePatterns.IP_ADDRESS,
            MessagePatterns.STATUS_CODE,
            MessagePatterns.DURATION,
            MessagePatterns.MEMORY_SIZE,
            MessagePatterns.PERCENTAGE,
            MessagePatterns.THREAD_ID,
            MessagePatterns.LOG_LEVEL,
            MessagePatterns.NUMBER,
            MessagePatterns.BOOLEAN,
            MessagePatterns.NULL
        ];
        
        patterns.forEach(pattern => {
            if (pattern.pattern.test(highlighted)) {
                highlighted = highlighted.replace(pattern.pattern, (match) => {
                    const color = this.colors[pattern.highlight];
                    return `<span class="log-highlight log-highlight--${pattern.highlight}" style="color: ${color}">${match}</span>`;
                });
                
                // Reset regex lastIndex for global patterns
                pattern.pattern.lastIndex = 0;
            }
        });
        
        // Cache result
        if (this.config.enableCaching) {
            this.highlightCache.set(message, highlighted);
            
            // Limit cache size
            if (this.highlightCache.size > this.config.cacheSize) {
                const firstKey = this.highlightCache.keys().next().value;
                this.highlightCache.delete(firstKey);
            }
        }
        
        // Record performance metrics
        if (this.config.enablePerformanceMetrics) {
            const endTime = performance.now();
            this.updateMetrics(endTime - startTime);
        }
        
        return highlighted;
    }
    
    /**
     * Format complete log message with all formatting options
     * @param {Object} message - Message object
     * @param {Object} [options] - Formatting options override
     * @returns {string} Formatted message HTML
     */
    formatMessage(message, options = {}) {
        const opts = { ...this.config, ...options };
        const startTime = this.config.enablePerformanceMetrics ? performance.now() : 0;
        
        try {
            // Format timestamp
            const timestamp = this.formatTimestamp(message.timestamp, opts.timestampFormat);
            
            // Format message content
            let content = message.message || '';
            
            // Handle message length
            let isExpanded = false;
            let originalContent = content;
            
            if (content.length > opts.maxMessageLength) {
                if (content.length > opts.expandableThreshold) {
                    content = content.substring(0, opts.expandableThreshold) + '...';
                    isExpanded = true;
                } else {
                    content = content.substring(0, opts.maxMessageLength) + '...';
                }
            }
            
            // Apply syntax highlighting
            const highlightedContent = this.applySyntaxHighlighting(content);
            
            // Build formatted message
            let formatted = `<span class="log-timestamp">${timestamp}</span> `;
            
            if (opts.enableLineNumbers && message.line) {
                formatted += `<span class="log-line-number">${message.line}</span> `;
            }
            
            formatted += `<span class="log-content">${highlightedContent}</span>`;
            
            // Add expand/collapse functionality for long messages
            if (isExpanded) {
                const expandedContent = this.applySyntaxHighlighting(originalContent);
                formatted += `<button class="log-expand-toggle" onclick="this.parentElement.querySelector('.log-content').innerHTML = '${expandedContent.replace(/'/g, "\\'")}'; this.style.display = 'none';">Expand</button>`;
            }
            
            // Record performance metrics
            if (this.config.enablePerformanceMetrics) {
                const endTime = performance.now();
                this.updateMetrics(endTime - startTime);
            }
            
            return formatted;
            
        } catch (error) {
            console.error('Message formatting failed:', error);
            return `<span class="log-error">Formatting Error: ${this.escapeHtml(message.message || 'Unknown message')}</span>`;
        }
    }
    
    /**
     * Format message for plain text export
     * @param {Object} message - Message object
     * @param {Object} [options] - Formatting options
     * @returns {string} Plain text formatted message
     */
    formatMessagePlainText(message, options = {}) {
        const opts = { ...this.config, ...options };
        
        try {
            const timestamp = this.formatTimestamp(message.timestamp, opts.timestampFormat);
            let content = message.message || '';
            
            // Handle message length for plain text
            if (content.length > opts.maxMessageLength && !opts.includeFullContent) {
                content = content.substring(0, opts.maxMessageLength) + '...';
            }
            
            let formatted = `${timestamp} `;
            
            if (opts.enableLineNumbers && message.line) {
                formatted += `${message.line} `;
            }
            
            formatted += content;
            
            return formatted;
            
        } catch (error) {
            console.error('Plain text formatting failed:', error);
            return `${new Date(message.timestamp).toISOString()} ${message.message || 'Unknown message'}`;
        }
    }
    
    /**
     * Parse structured log message
     * @param {string} message - Raw message string
     * @returns {Object} Parsed message components
     */
    parseStructuredMessage(message) {
        try {
            // Try to parse as JSON first
            if (MessagePatterns.JSON.pattern.test(message)) {
                const parsed = JSON.parse(message);
                return {
                    type: 'json',
                    structured: true,
                    data: parsed,
                    formatted: this.formatJSON(parsed)
                };
            }
            
            // Try to parse as XML
            if (MessagePatterns.XML.pattern.test(message)) {
                return {
                    type: 'xml',
                    structured: true,
                    data: message,
                    formatted: this.formatXML(message)
                };
            }
            
            // Check for key-value pairs (e.g., "key1=value1 key2=value2")
            const kvPattern = /(\w+)=([^\s]+)/g;
            const kvMatches = [...message.matchAll(kvPattern)];
            
            if (kvMatches.length > 0) {
                const kvData = {};
                kvMatches.forEach(match => {
                    kvData[match[1]] = match[2];
                });
                
                return {
                    type: 'key-value',
                    structured: true,
                    data: kvData,
                    formatted: this.formatKeyValue(kvData)
                };
            }
            
            // Return as unstructured
            return {
                type: 'plain',
                structured: false,
                data: message,
                formatted: message
            };
            
        } catch (error) {
            console.warn('Message parsing failed:', error);
            return {
                type: 'plain',
                structured: false,
                data: message,
                formatted: message
            };
        }
    }
    
    /**
     * Format JSON data with indentation and highlighting
     * @private
     * @param {Object} data - JSON data
     * @returns {string} Formatted JSON HTML
     */
    formatJSON(data) {
        try {
            const jsonString = JSON.stringify(data, null, 2);
            return this.applySyntaxHighlighting(jsonString);
        } catch (error) {
            return this.escapeHtml(String(data));
        }
    }
    
    /**
     * Format XML with basic indentation
     * @private
     * @param {string} xml - XML string
     * @returns {string} Formatted XML HTML
     */
    formatXML(xml) {
        try {
            // Basic XML formatting (this is simplified)
            let formatted = xml
                .replace(/></g, '>\n<')
                .replace(/^\s*\n/gm, '');
            
            return this.applySyntaxHighlighting(formatted);
        } catch (error) {
            return this.escapeHtml(xml);
        }
    }
    
    /**
     * Format key-value pairs
     * @private
     * @param {Object} data - Key-value data
     * @returns {string} Formatted key-value HTML
     */
    formatKeyValue(data) {
        const pairs = Object.entries(data).map(([key, value]) => {
            const highlightedKey = `<span class="log-highlight log-highlight--key" style="color: ${this.colors.number}">${key}</span>`;
            const highlightedValue = this.applySyntaxHighlighting(value);
            return `${highlightedKey}=${highlightedValue}`;
        });
        
        return pairs.join(' ');
    }
    
    /**
     * Get suggested timestamp format based on message frequency
     * @param {number} messagesPerSecond - Current message rate
     * @returns {string} Suggested format
     */
    getSuggestedTimestampFormat(messagesPerSecond) {
        if (messagesPerSecond > 10) {
            return 'TIME_WITH_MS'; // High frequency needs milliseconds
        } else if (messagesPerSecond > 1) {
            return 'TIME_ONLY'; // Medium frequency can skip milliseconds
        } else {
            return 'DATE_TIME'; // Low frequency can show full date
        }
    }
    
    /**
     * Update performance metrics
     * @private
     * @param {number} formatTime - Time taken for formatting
     */
    updateMetrics(formatTime) {
        this.metrics.formatCalls++;
        this.metrics.totalFormatTime += formatTime;
        this.metrics.averageFormatTime = this.metrics.totalFormatTime / this.metrics.formatCalls;
    }
    
    /**
     * Get performance metrics
     * @returns {Object} Performance metrics
     */
    getMetrics() {
        return {
            ...this.metrics,
            cacheHitRatio: this.metrics.formatCalls > 0 ? this.metrics.cacheHits / this.metrics.formatCalls : 0,
            cacheSize: {
                format: this.formatCache.size,
                timestamp: this.timestampCache.size,
                highlight: this.highlightCache.size
            }
        };
    }
    
    /**
     * Clear all caches
     */
    clearCache() {
        this.formatCache.clear();
        this.timestampCache.clear();
        this.highlightCache.clear();
        
        console.log('🧹 Log formatter caches cleared');
    }
    
    /**
     * Update configuration
     * @param {Object} newConfig - New configuration options
     */
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        
        // Update color scheme if theme changed
        if (newConfig.theme) {
            this.colors = ColorScheme[newConfig.theme] || ColorScheme.DARK;
        }
        
        // Clear caches if critical settings changed
        if (newConfig.enableSyntaxHighlighting !== undefined || 
            newConfig.theme !== undefined ||
            newConfig.timestampFormat !== undefined) {
            this.clearCache();
        }
        
        console.log('⚙️ Log formatter configuration updated');
    }
    
    /**
     * Escape HTML characters
     * @private
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (typeof text !== 'string') {
            text = String(text);
        }
        
        const htmlEscapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '/': '&#x2F;'
        };
        
        return text.replace(/[&<>"'\/]/g, char => htmlEscapeMap[char]);
    }
    
    /**
     * Get available timestamp formats
     * @returns {Array} Available formats with descriptions
     */
    getAvailableTimestampFormats() {
        return Object.entries(TimestampFormat).map(([key, config]) => ({
            key,
            name: config.pattern,
            example: this.formatTimestamp(Date.now(), key)
        }));
    }
    
    /**
     * Get available color themes
     * @returns {Array} Available themes
     */
    getAvailableThemes() {
        return Object.keys(ColorScheme);
    }
    
    /**
     * Export formatter configuration
     * @returns {Object} Current configuration
     */
    exportConfig() {
        return { ...this.config };
    }
    
    /**
     * Import formatter configuration
     * @param {Object} config - Configuration to import
     */
    importConfig(config) {
        this.updateConfig(config);
    }
}

// Export constants for external use
export { TimestampFormat, MessagePatterns, ColorScheme };

console.log('📝 Log Formatter utility loaded successfully');