/**
 * Application Configuration - WF EOL Tester Web Interface
 * 
 * This module contains all configuration settings for the web application including:
 * - API endpoints and URLs with environment detection
 * - WebSocket connection settings with fallback options
 * - UI behavior settings and animation preferences
 * - Chart configuration defaults and performance settings
 * - Polling intervals and timeout configurations
 * - Feature flags and experimental settings
 * - Environment-specific settings with auto-detection
 * - Hardware communication parameters
 * - Test execution parameters and limits
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

/**
 * Environment detection
 * @private
 */
const detectEnvironment = () => {
    const hostname = window.location.hostname;
    const port = window.location.port;
    
    // Development environment detection
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0') {
        return 'development';
    }
    
    // Production environment
    if (hostname.includes('production') || port === '80' || port === '443') {
        return 'production';
    }
    
    // Default to development
    return 'development';
};

/**
 * Get base API URL based on current environment
 * @private
 */
const getBaseApiUrl = () => {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const environment = detectEnvironment();
    
    if (environment === 'development') {
        // Development: assume API is on same host, port 8000
        return `${protocol}//${hostname}:8000/api/v1`;
    } else {
        // Production: API on same host and port
        return `${protocol}//${window.location.host}/api/v1`;
    }
};

/**
 * Get WebSocket URL based on current environment
 * @private
 */
const getWebSocketUrl = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const hostname = window.location.hostname;
    const environment = detectEnvironment();
    
    if (environment === 'development') {
        // Development: WebSocket on port 8080
        return `${protocol}//${hostname}:8080/ws`;
    } else {
        // Production: WebSocket on same host and port with /ws path
        return `${protocol}//${window.location.host}/ws`;
    }
};

/**
 * Application Configuration Object
 * 
 * Comprehensive configuration for all aspects of the WF EOL Tester web interface.
 * Automatically adapts to development and production environments.
 */
export const AppConfig = {
    // Environment Configuration
    environment: {
        current: detectEnvironment(),
        isDevelopment: detectEnvironment() === 'development',
        isProduction: detectEnvironment() === 'production',
        version: '1.0.0',
        buildDate: new Date().toISOString(),
        features: {
            debugMode: detectEnvironment() === 'development',
            verboseLogging: detectEnvironment() === 'development',
            mockData: false,
            experimentalFeatures: false
        }
    },

    // API Configuration
    api: {
        baseUrl: getBaseApiUrl(),
        timeout: 10000,                    // 10 seconds
        retryAttempts: 3,
        retryDelay: 1000,                  // 1 second base delay
        maxRetryDelay: 30000,              // 30 seconds max delay
        cacheTimeout: 5 * 60 * 1000,       // 5 minutes
        
        // Endpoint-specific timeouts
        timeouts: {
            health: 5000,                   // Health checks
            hardware: 15000,                // Hardware operations
            test: 30000,                    // Test operations
            configuration: 10000,           // Configuration operations
            upload: 60000,                  // File uploads
            download: 120000                // File downloads
        },
        
        // Rate limiting
        rateLimit: {
            requestsPerMinute: 60,
            burstLimit: 10
        }
    },
    
    // WebSocket Configuration
    websocket: {
        url: getWebSocketUrl(),
        reconnectInterval: 5000,            // 5 seconds
        maxReconnectAttempts: 10,
        heartbeatInterval: 30000,           // 30 seconds
        messageTimeout: 10000,              // 10 seconds
        
        // Auto-reconnection settings
        reconnection: {
            enabled: true,
            exponentialBackoff: true,
            maxDelay: 30000,                // 30 seconds max
            jitter: true
        },
        
        // Message handling
        messageQueue: {
            maxSize: 100,
            persistOffline: true,
            retryFailedMessages: true
        }
    },
    
    // UI Configuration
    ui: {
        // Refresh intervals
        refreshInterval: 1000,              // 1 second
        chartUpdateInterval: 100,           // 100ms
        statusUpdateInterval: 500,          // 500ms
        clockUpdateInterval: 1000,          // 1 second
        
        // Animation settings
        animations: {
            enabled: true,
            duration: 300,                  // 300ms
            easing: 'ease-in-out',
            reducedMotion: false            // Auto-detect from system
        },
        
        // Display limits
        limits: {
            maxLogEntries: 1000,
            maxNotifications: 5,
            maxChartDataPoints: 500,
            maxHistoryEntries: 100
        },
        
        // Responsive breakpoints
        breakpoints: {
            mobile: 768,
            tablet: 1024,
            desktop: 1200,
            widescreen: 1400
        },
        
        // Theme settings
        theme: {
            default: 'default',
            available: ['default', 'dark'],
            autoDetectSystemTheme: true,
            persistUserChoice: true
        },
        
        // Accessibility
        accessibility: {
            highContrast: false,
            reducedMotion: false,
            screenReaderSupport: true,
            keyboardNavigation: true
        }
    },
    
    // Hardware Configuration
    hardware: {
        // Status monitoring
        statusCheckInterval: 500,           // 500ms
        timeoutDuration: 30000,             // 30 seconds
        maxRetries: 3,
        
        // Component-specific settings
        components: {
            robot: {
                timeout: 15000,             // 15 seconds
                homeTimeout: 30000,         // 30 seconds
                maxSpeed: 100,              // percentage
                precision: 0.1              // mm
            },
            power: {
                timeout: 5000,              // 5 seconds
                voltageRange: [0, 50],      // volts
                currentRange: [0, 10],      // amps
                safetyLimits: true
            },
            mcu: {
                timeout: 10000,             // 10 seconds
                baudRate: 115200,
                dataFormat: '8N1',
                bufferSize: 4096
            },
            loadcell: {
                timeout: 5000,              // 5 seconds
                sampleRate: 100,            // Hz
                forceRange: [0, 1000],      // N
                calibrationPoints: 5
            },
            digitalIo: {
                timeout: 2000,              // 2 seconds
                debounceTime: 50,           // ms
                inputPullup: true,
                outputDefault: false
            }
        },
        
        // Emergency stop
        emergencyStop: {
            timeout: 1000,                  // 1 second
            confirmationRequired: false,
            autoReset: false,
            priority: 'highest'
        }
    },
    
    // Test Configuration
    test: {
        // Execution parameters
        maxTestDuration: 300000,            // 5 minutes
        dataPointsPerSecond: 10,
        maxDataPoints: 3000,                // 5 minutes at 10 Hz
        
        // Test types
        types: {
            forceTest: {
                duration: 60000,            // 1 minute
                sampleRate: 10,             // Hz
                forceThresholds: {
                    min: 10,                // N
                    max: 500,               // N
                    tolerance: 0.05         // 5%
                }
            },
            enduranceTest: {
                duration: 300000,           // 5 minutes
                cycles: 1000,
                restPeriod: 100,            // ms
                failureThreshold: 0.02      // 2%
            }
        },
        
        // Data collection
        dataCollection: {
            bufferSize: 10000,
            compressionEnabled: true,
            autoSave: true,
            saveInterval: 30000,            // 30 seconds
            retentionPeriod: 30 * 24 * 60 * 60 * 1000  // 30 days
        },
        
        // Result evaluation
        evaluation: {
            passCriteria: {
                forceAccuracy: 0.95,        // 95%
                repeatability: 0.02,        // 2%
                stability: 0.01             // 1%
            },
            reportGeneration: {
                format: 'json',
                includeRawData: false,
                includeStatistics: true,
                includePlots: false
            }
        }
    },
    
    // Chart Configuration
    charts: {
        // Default settings
        defaults: {
            backgroundColor: 'transparent',
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 300,
                easing: 'easeOutQuart'
            }
        },
        
        // Real-time charts
        realtime: {
            updateInterval: 100,            // 100ms
            maxDataPoints: 100,
            scrolling: true,
            bufferSize: 200
        },
        
        // Color schemes
        colors: {
            primary: ['#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8'],
            dark: ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#0dcaf0'],
            colorBlind: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        },
        
        // Performance settings
        performance: {
            enableWebGL: true,
            enableAnimation: true,
            maxRenderTime: 16,              // 60fps target
            throttleUpdates: true
        }
    },
    
    // Logging Configuration
    logging: {
        level: detectEnvironment() === 'development' ? 'debug' : 'info',
        levels: ['error', 'warn', 'info', 'debug', 'trace'],
        
        // Console logging
        console: {
            enabled: true,
            colorize: true,
            timestamp: true,
            format: 'simple'
        },
        
        // Remote logging
        remote: {
            enabled: detectEnvironment() === 'production',
            endpoint: '/api/v1/logs',
            batchSize: 10,
            flushInterval: 30000,           // 30 seconds
            maxRetries: 3
        },
        
        // Local storage
        localStorage: {
            enabled: true,
            maxEntries: 1000,
            retention: 7 * 24 * 60 * 60 * 1000,  // 7 days
            key: 'wf-eol-logs'
        }
    },
    
    // Security Configuration
    security: {
        // CSRF protection
        csrf: {
            enabled: true,
            tokenHeader: 'X-CSRF-Token',
            cookieName: 'csrf_token'
        },
        
        // Content Security Policy
        csp: {
            enforced: detectEnvironment() === 'production',
            reportUri: '/api/v1/csp-report'
        },
        
        // Session management
        session: {
            timeout: 60 * 60 * 1000,        // 1 hour
            renewThreshold: 10 * 60 * 1000, // 10 minutes
            warningTime: 5 * 60 * 1000      // 5 minutes
        }
    },
    
    // Storage Configuration
    storage: {
        // Local storage keys
        keys: {
            theme: 'wf-eol-theme',
            preferences: 'wf-eol-preferences',
            session: 'wf-eol-session',
            cache: 'wf-eol-cache'
        },
        
        // Storage limits
        limits: {
            localStorage: 5 * 1024 * 1024,  // 5MB
            sessionStorage: 1 * 1024 * 1024, // 1MB
            cacheStorage: 50 * 1024 * 1024  // 50MB
        },
        
        // Cleanup settings
        cleanup: {
            enabled: true,
            interval: 24 * 60 * 60 * 1000,  // 24 hours
            maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
        }
    },
    
    // Debug Configuration
    debug: {
        enabled: detectEnvironment() === 'development',
        
        // Debug panels
        panels: {
            performance: true,
            network: true,
            storage: true,
            events: true
        },
        
        // Mock data
        mockData: {
            enabled: false,
            scenarios: ['normal', 'error', 'slow', 'offline'],
            currentScenario: 'normal'
        },
        
        // Development tools
        devTools: {
            showFPS: false,
            showMemory: false,
            showNetwork: false,
            verboseErrors: true
        }
    }
};

/**
 * Get configuration for specific component
 * @param {string} component - Component name
 * @returns {Object} Component configuration
 */
export function getComponentConfig(component) {
    const parts = component.split('.');
    let config = AppConfig;
    
    for (const part of parts) {
        if (config && typeof config === 'object' && part in config) {
            config = config[part];
        } else {
            console.warn(`Configuration path '${component}' not found`);
            return {};
        }
    }
    
    return config;
}

/**
 * Update configuration at runtime
 * @param {string} path - Configuration path (dot notation)
 * @param {*} value - New value
 */
export function updateConfig(path, value) {
    const parts = path.split('.');
    let config = AppConfig;
    
    // Navigate to parent object
    for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i];
        if (config && typeof config === 'object' && part in config) {
            config = config[part];
        } else {
            console.warn(`Configuration path '${path}' not found`);
            return false;
        }
    }
    
    // Set the value
    const lastPart = parts[parts.length - 1];
    if (config && typeof config === 'object') {
        config[lastPart] = value;
        console.log(`Configuration updated: ${path} = ${JSON.stringify(value)}`);
        return true;
    }
    
    return false;
}

/**
 * Get environment-specific configuration
 * @returns {Object} Environment configuration
 */
export function getEnvironmentConfig() {
    return AppConfig.environment;
}

/**
 * Check if feature is enabled
 * @param {string} feature - Feature name
 * @returns {boolean} True if feature is enabled
 */
export function isFeatureEnabled(feature) {
    return AppConfig.environment.features[feature] || false;
}

/**
 * Get API endpoint URL
 * @param {string} endpoint - Endpoint path
 * @returns {string} Full URL
 */
export function getApiUrl(endpoint) {
    const baseUrl = AppConfig.api.baseUrl;
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${baseUrl}${cleanEndpoint}`;
}

/**
 * Get WebSocket URL
 * @param {string} path - WebSocket path (optional)
 * @returns {string} WebSocket URL
 */
export function getWebSocketUrl(path = '') {
    const baseUrl = AppConfig.websocket.url;
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return path ? `${baseUrl}${cleanPath}` : baseUrl;
}

console.log('📝 Application configuration loaded successfully');
console.log(`🌍 Environment: ${AppConfig.environment.current}`);
console.log(`🔗 API Base URL: ${AppConfig.api.baseUrl}`);
console.log(`📡 WebSocket URL: ${AppConfig.websocket.url}`);