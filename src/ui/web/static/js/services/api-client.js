/**
 * API Client Service - WF EOL Tester Web Interface
 * 
 * This service handles all HTTP communication with the backend API including:
 * - RESTful API requests (GET, POST, PUT, DELETE)
 * - Authentication and authorization
 * - Request/response interceptors
 * - Error handling and retry logic with exponential backoff
 * - Request caching and deduplication
 * - Response data validation and transformation
 * - Timeout management and connection monitoring
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

/**
 * Custom API Error class for better error handling
 */
class APIError extends Error {
    constructor(message, status, response = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.response = response;
    }
}

/**
 * HTTP API Client with comprehensive error handling and retry logic
 * 
 * Implements Clean Architecture principles with proper separation of concerns.
 * Provides robust communication with the FastAPI backend.
 */
export class APIClient {
    /**
     * Initialize API Client
     * @param {Object} config - API configuration object
     */
    constructor(config) {
        this.config = {
            baseUrl: '/api/v1',
            timeout: 10000,
            retryAttempts: 3,
            retryDelay: 1000,
            ...config
        };
        
        console.log('🔧 API Client initializing with config:', this.config);
        
        // Request cache for deduplication
        this.requestCache = new Map();
        this.pendingRequests = new Map();
        
        // Authentication state
        this.authToken = null;
        this.authHeaders = {};
        
        // Request interceptors
        this.requestInterceptors = [];
        this.responseInterceptors = [];
        
        // Connection monitoring
        this.isOnline = navigator.onLine;
        this.setupConnectionMonitoring();
        
        console.log('✅ API Client initialized successfully');
    }

    /**
     * Setup connection monitoring
     * @private
     */
    setupConnectionMonitoring() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            console.log('🌐 Network connection restored');
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            console.log('📵 Network connection lost');
        });
    }

    /**
     * Set authentication token
     * @param {string} token - JWT or API token
     */
    setAuthToken(token) {
        this.authToken = token;
        this.authHeaders = token ? { Authorization: `Bearer ${token}` } : {};
        console.log('🔐 Authentication token updated');
    }

    /**
     * Clear authentication
     */
    clearAuth() {
        this.authToken = null;
        this.authHeaders = {};
        console.log('🔓 Authentication cleared');
    }

    /**
     * Add request interceptor
     * @param {Function} interceptor - Function to modify request before sending
     */
    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }

    /**
     * Add response interceptor
     * @param {Function} interceptor - Function to process response
     */
    addResponseInterceptor(interceptor) {
        this.responseInterceptors.push(interceptor);
    }

    /**
     * Build full URL for endpoint
     * @private
     * @param {string} endpoint - API endpoint
     * @returns {string} Full URL
     */
    buildUrl(endpoint) {
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return `${this.config.baseUrl}${cleanEndpoint}`;
    }

    /**
     * Build request options with headers and configuration
     * @private
     * @param {string} method - HTTP method
     * @param {Object} data - Request data
     * @param {Object} options - Additional options
     * @returns {Object} Fetch options
     */
    buildRequestOptions(method, data = null, options = {}) {
        const requestOptions = {
            method: method.toUpperCase(),
            headers: {
                'Content-Type': 'application/json',
                ...this.authHeaders,
                ...options.headers
            },
            ...options
        };

        // Add request body for non-GET requests
        if (data && !['GET', 'HEAD'].includes(requestOptions.method)) {
            requestOptions.body = JSON.stringify(data);
        }

        return requestOptions;
    }

    /**
     * Apply request interceptors
     * @private
     * @param {Object} options - Request options
     * @returns {Object} Modified options
     */
    async applyRequestInterceptors(options) {
        let modifiedOptions = { ...options };
        
        for (const interceptor of this.requestInterceptors) {
            try {
                modifiedOptions = await interceptor(modifiedOptions);
            } catch (error) {
                console.warn('Request interceptor failed:', error);
            }
        }
        
        return modifiedOptions;
    }

    /**
     * Apply response interceptors
     * @private
     * @param {Response} response - Fetch response
     * @returns {Response} Modified response
     */
    async applyResponseInterceptors(response) {
        let modifiedResponse = response;
        
        for (const interceptor of this.responseInterceptors) {
            try {
                modifiedResponse = await interceptor(modifiedResponse);
            } catch (error) {
                console.warn('Response interceptor failed:', error);
            }
        }
        
        return modifiedResponse;
    }

    /**
     * Execute HTTP request with retry logic and error handling
     * @private
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<any>} Response data
     */
    async executeRequest(endpoint, options) {
        // Check network connectivity
        if (!this.isOnline) {
            throw new APIError('No network connection available', 0);
        }

        const url = this.buildUrl(endpoint);
        const cacheKey = `${options.method}:${url}:${JSON.stringify(options.body || {})}`;
        
        // Check for pending identical request
        if (this.pendingRequests.has(cacheKey)) {
            console.log('📋 Returning pending request for:', cacheKey);
            return this.pendingRequests.get(cacheKey);
        }

        // Apply request interceptors
        const finalOptions = await this.applyRequestInterceptors(options);
        
        // Create the request promise
        const requestPromise = this.executeWithRetry(url, finalOptions);
        
        // Cache the promise to prevent duplicate requests
        this.pendingRequests.set(cacheKey, requestPromise);
        
        try {
            const result = await requestPromise;
            return result;
        } finally {
            // Remove from pending requests
            this.pendingRequests.delete(cacheKey);
        }
    }

    /**
     * Execute request with retry logic
     * @private
     * @param {string} url - Request URL
     * @param {Object} options - Request options
     * @returns {Promise<any>} Response data
     */
    async executeWithRetry(url, options) {
        let lastError;
        
        for (let attempt = 0; attempt <= this.config.retryAttempts; attempt++) {
            try {
                console.log(`🔄 API Request [Attempt ${attempt + 1}]: ${options.method} ${url}`);
                
                // Create abort controller for timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
                
                // Make the request
                const response = await fetch(url, {
                    ...options,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                // Apply response interceptors
                const processedResponse = await this.applyResponseInterceptors(response);
                
                // Handle response
                if (!processedResponse.ok) {
                    const errorData = await this.parseErrorResponse(processedResponse);
                    throw new APIError(
                        errorData.message || `HTTP ${processedResponse.status}`,
                        processedResponse.status,
                        errorData
                    );
                }
                
                const data = await this.parseSuccessResponse(processedResponse);
                console.log(`✅ API Request successful: ${options.method} ${url}`);
                
                return data;
                
            } catch (error) {
                lastError = error;
                
                // Don't retry on certain error types
                if (this.shouldNotRetry(error, attempt)) {
                    break;
                }
                
                // Wait before retry with exponential backoff
                if (attempt < this.config.retryAttempts) {
                    const delay = this.config.retryDelay * Math.pow(2, attempt);
                    console.log(`⏳ Retrying in ${delay}ms... (${attempt + 1}/${this.config.retryAttempts})`);
                    await this.sleep(delay);
                }
            }
        }
        
        console.error(`❌ API Request failed after ${this.config.retryAttempts + 1} attempts:`, lastError);
        throw lastError;
    }

    /**
     * Determine if request should not be retried
     * @private
     * @param {Error} error - Request error
     * @param {number} attempt - Current attempt number
     * @returns {boolean} True if should not retry
     */
    shouldNotRetry(error, attempt) {
        // Don't retry on client errors (4xx) except 408, 429
        if (error instanceof APIError) {
            const status = error.status;
            if (status >= 400 && status < 500 && ![408, 429].includes(status)) {
                return true;
            }
        }
        
        // Don't retry on abort errors (user cancelled)
        if (error.name === 'AbortError') {
            return true;
        }
        
        // Don't retry on final attempt
        return attempt >= this.config.retryAttempts;
    }

    /**
     * Parse successful response
     * @private
     * @param {Response} response - Fetch response
     * @returns {Promise<any>} Parsed data
     */
    async parseSuccessResponse(response) {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else if (contentType && contentType.includes('text/')) {
            return await response.text();
        } else {
            return await response.blob();
        }
    }

    /**
     * Parse error response
     * @private
     * @param {Response} response - Fetch response
     * @returns {Promise<Object>} Error data
     */
    async parseErrorResponse(response) {
        try {
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                const text = await response.text();
                return { message: text || `HTTP ${response.status}` };
            }
        } catch (error) {
            return { message: `HTTP ${response.status}` };
        }
    }

    /**
     * Sleep for specified milliseconds
     * @private
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise<void>}
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // =========================
    // Generic HTTP Methods
    // =========================

    /**
     * Execute GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} params - Query parameters
     * @param {Object} options - Additional options
     * @returns {Promise<any>} Response data
     */
    async get(endpoint, params = {}, options = {}) {
        // Build query string
        const queryString = new URLSearchParams(params).toString();
        const fullEndpoint = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        const requestOptions = this.buildRequestOptions('GET', null, options);
        return this.executeRequest(fullEndpoint, requestOptions);
    }

    /**
     * Execute POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} options - Additional options
     * @returns {Promise<any>} Response data
     */
    async post(endpoint, data = {}, options = {}) {
        const requestOptions = this.buildRequestOptions('POST', data, options);
        return this.executeRequest(endpoint, requestOptions);
    }

    /**
     * Execute PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} options - Additional options
     * @returns {Promise<any>} Response data
     */
    async put(endpoint, data = {}, options = {}) {
        const requestOptions = this.buildRequestOptions('PUT', data, options);
        return this.executeRequest(endpoint, requestOptions);
    }

    /**
     * Execute PATCH request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} options - Additional options
     * @returns {Promise<any>} Response data
     */
    async patch(endpoint, data = {}, options = {}) {
        const requestOptions = this.buildRequestOptions('PATCH', data, options);
        return this.executeRequest(endpoint, requestOptions);
    }

    /**
     * Execute DELETE request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Additional options
     * @returns {Promise<any>} Response data
     */
    async delete(endpoint, options = {}) {
        const requestOptions = this.buildRequestOptions('DELETE', null, options);
        return this.executeRequest(endpoint, requestOptions);
    }

    // =========================
    // Hardware API Methods
    // =========================

    /**
     * Get status of all hardware components
     * @returns {Promise<Object>} Hardware status data
     */
    async getHardwareStatus() {
        try {
            console.log('🔄 Fetching hardware status...');
            const status = await this.get('/hardware/status');
            console.log('✅ Hardware status retrieved:', status);
            return status;
        } catch (error) {
            console.error('❌ Failed to get hardware status:', error);
            throw error;
        }
    }

    /**
     * Get status of specific hardware component
     * @param {string} component - Component name (robot, power, mcu, loadcell, digital-io)
     * @returns {Promise<Object>} Component status
     */
    async getComponentStatus(component) {
        try {
            console.log(`🔄 Fetching ${component} status...`);
            const status = await this.get(`/hardware/${component}/status`);
            console.log(`✅ ${component} status retrieved:`, status);
            return status;
        } catch (error) {
            console.error(`❌ Failed to get ${component} status:`, error);
            throw error;
        }
    }

    /**
     * Send control command to hardware component
     * @param {string} component - Component name
     * @param {string} action - Action to perform
     * @param {Object} parameters - Action parameters
     * @returns {Promise<Object>} Command result
     */
    async controlHardware(component, action, parameters = {}) {
        try {
            console.log(`🔄 Sending ${action} command to ${component}...`);
            const result = await this.post(`/hardware/${component}/control`, {
                action,
                parameters
            });
            console.log(`✅ ${component} ${action} command successful:`, result);
            return result;
        } catch (error) {
            console.error(`❌ Failed to control ${component}:`, error);
            throw error;
        }
    }

    /**
     * Execute emergency stop for all hardware
     * @returns {Promise<Object>} Emergency stop result
     */
    async emergencyStop() {
        try {
            console.log('🚨 Executing emergency stop...');
            const result = await this.post('/hardware/emergency-stop');
            console.log('✅ Emergency stop executed:', result);
            return result;
        } catch (error) {
            console.error('❌ Emergency stop failed:', error);
            throw error;
        }
    }

    /**
     * Get hardware configuration
     * @returns {Promise<Object>} Hardware configuration
     */
    async getHardwareConfiguration() {
        try {
            console.log('🔄 Fetching hardware configuration...');
            const config = await this.get('/hardware/configuration');
            console.log('✅ Hardware configuration retrieved:', config);
            return config;
        } catch (error) {
            console.error('❌ Failed to get hardware configuration:', error);
            throw error;
        }
    }

    /**
     * Update hardware configuration
     * @param {Object} config - New configuration
     * @returns {Promise<Object>} Update result
     */
    async updateHardwareConfiguration(config) {
        try {
            console.log('🔄 Updating hardware configuration...');
            const result = await this.put('/hardware/configuration', config);
            console.log('✅ Hardware configuration updated:', result);
            return result;
        } catch (error) {
            console.error('❌ Failed to update hardware configuration:', error);
            throw error;
        }
    }

    // =========================
    // Test API Methods
    // =========================

    /**
     * Start a new EOL test
     * @param {Object} testConfig - Test configuration
     * @returns {Promise<Object>} Test start result
     */
    async startTest(testConfig) {
        try {
            console.log('🔄 Starting EOL test...', testConfig);
            const result = await this.post('/tests/start', testConfig);
            console.log('✅ Test started successfully:', result);
            return result;
        } catch (error) {
            console.error('❌ Failed to start test:', error);
            throw error;
        }
    }

    /**
     * Stop running test
     * @param {string} testId - Test ID
     * @returns {Promise<Object>} Stop result
     */
    async stopTest(testId) {
        try {
            console.log(`🔄 Stopping test ${testId}...`);
            const result = await this.post(`/tests/${testId}/stop`);
            console.log('✅ Test stopped successfully:', result);
            return result;
        } catch (error) {
            console.error(`❌ Failed to stop test ${testId}:`, error);
            throw error;
        }
    }

    /**
     * Get test results
     * @param {string} testId - Test ID
     * @returns {Promise<Object>} Test results
     */
    async getTestResults(testId) {
        try {
            console.log(`🔄 Fetching test results for ${testId}...`);
            const results = await this.get(`/tests/${testId}/results`);
            console.log('✅ Test results retrieved:', results);
            return results;
        } catch (error) {
            console.error(`❌ Failed to get test results for ${testId}:`, error);
            throw error;
        }
    }

    /**
     * Get test history with optional filters
     * @param {Object} filters - Filter options
     * @returns {Promise<Array>} Test history
     */
    async getTestHistory(filters = {}) {
        try {
            console.log('🔄 Fetching test history...', filters);
            const history = await this.get('/tests/history', filters);
            console.log('✅ Test history retrieved:', history);
            return history;
        } catch (error) {
            console.error('❌ Failed to get test history:', error);
            throw error;
        }
    }

    /**
     * Get current test status
     * @returns {Promise<Object>} Current test status
     */
    async getCurrentTestStatus() {
        try {
            console.log('🔄 Fetching current test status...');
            const status = await this.get('/tests/current');
            console.log('✅ Current test status retrieved:', status);
            return status;
        } catch (error) {
            console.error('❌ Failed to get current test status:', error);
            throw error;
        }
    }

    // =========================
    // Configuration API Methods
    // =========================

    /**
     * Get system configuration
     * @returns {Promise<Object>} System configuration
     */
    async getConfiguration() {
        try {
            console.log('🔄 Fetching system configuration...');
            const config = await this.get('/config');
            console.log('✅ System configuration retrieved:', config);
            return config;
        } catch (error) {
            console.error('❌ Failed to get system configuration:', error);
            throw error;
        }
    }

    /**
     * Update system configuration
     * @param {Object} config - New configuration
     * @returns {Promise<Object>} Update result
     */
    async updateConfiguration(config) {
        try {
            console.log('🔄 Updating system configuration...');
            const result = await this.put('/config', config);
            console.log('✅ System configuration updated:', result);
            return result;
        } catch (error) {
            console.error('❌ Failed to update system configuration:', error);
            throw error;
        }
    }

    /**
     * Get test profiles
     * @returns {Promise<Array>} Available test profiles
     */
    async getTestProfiles() {
        try {
            console.log('🔄 Fetching test profiles...');
            const profiles = await this.get('/config/profiles');
            console.log('✅ Test profiles retrieved:', profiles);
            return profiles;
        } catch (error) {
            console.error('❌ Failed to get test profiles:', error);
            throw error;
        }
    }

    /**
     * Create or update test profile
     * @param {Object} profile - Test profile data
     * @returns {Promise<Object>} Save result
     */
    async saveTestProfile(profile) {
        try {
            console.log('🔄 Saving test profile...', profile);
            const result = await this.post('/config/profiles', profile);
            console.log('✅ Test profile saved:', result);
            return result;
        } catch (error) {
            console.error('❌ Failed to save test profile:', error);
            throw error;
        }
    }

    /**
     * Delete test profile
     * @param {string} profileId - Profile ID
     * @returns {Promise<Object>} Delete result
     */
    async deleteTestProfile(profileId) {
        try {
            console.log(`🔄 Deleting test profile ${profileId}...`);
            const result = await this.delete(`/config/profiles/${profileId}`);
            console.log('✅ Test profile deleted:', result);
            return result;
        } catch (error) {
            console.error(`❌ Failed to delete test profile ${profileId}:`, error);
            throw error;
        }
    }

    // =========================
    // Health and Monitoring
    // =========================

    /**
     * Get API health status
     * @returns {Promise<Object>} Health status
     */
    async getHealth() {
        try {
            const health = await this.get('/health');
            return health;
        } catch (error) {
            console.error('❌ Health check failed:', error);
            throw error;
        }
    }

    /**
     * Get system metrics
     * @returns {Promise<Object>} System metrics
     */
    async getSystemMetrics() {
        try {
            console.log('🔄 Fetching system metrics...');
            const metrics = await this.get('/system/metrics');
            console.log('✅ System metrics retrieved:', metrics);
            return metrics;
        } catch (error) {
            console.error('❌ Failed to get system metrics:', error);
            throw error;
        }
    }

    // =========================
    // File Operations
    // =========================

    /**
     * Upload file
     * @param {string} endpoint - Upload endpoint
     * @param {File} file - File to upload
     * @param {Object} options - Upload options
     * @returns {Promise<Object>} Upload result
     */
    async uploadFile(endpoint, file, options = {}) {
        try {
            console.log(`🔄 Uploading file to ${endpoint}:`, file.name);
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Add additional form fields if provided
            if (options.fields) {
                Object.entries(options.fields).forEach(([key, value]) => {
                    formData.append(key, value);
                });
            }
            
            const requestOptions = {
                method: 'POST',
                body: formData,
                headers: {
                    ...this.authHeaders,
                    // Don't set Content-Type for FormData - browser will set it with boundary
                }
            };
            
            const result = await this.executeRequest(endpoint, requestOptions);
            console.log('✅ File uploaded successfully:', result);
            return result;
            
        } catch (error) {
            console.error('❌ File upload failed:', error);
            throw error;
        }
    }

    /**
     * Download file
     * @param {string} endpoint - Download endpoint
     * @param {string} filename - Target filename
     * @returns {Promise<Blob>} File blob
     */
    async downloadFile(endpoint, filename = null) {
        try {
            console.log(`🔄 Downloading file from ${endpoint}...`);
            
            const requestOptions = this.buildRequestOptions('GET');
            const url = this.buildUrl(endpoint);
            
            const response = await fetch(url, requestOptions);
            
            if (!response.ok) {
                throw new APIError(`Download failed: ${response.status}`, response.status);
            }
            
            const blob = await response.blob();
            
            // Trigger download if filename provided
            if (filename) {
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(link.href);
            }
            
            console.log('✅ File downloaded successfully');
            return blob;
            
        } catch (error) {
            console.error('❌ File download failed:', error);
            throw error;
        }
    }

    // =========================
    // Cache Management
    // =========================

    /**
     * Clear request cache
     */
    clearCache() {
        this.requestCache.clear();
        console.log('🗑️ Request cache cleared');
    }

    /**
     * Get cache statistics
     * @returns {Object} Cache statistics
     */
    getCacheStats() {
        return {
            cacheSize: this.requestCache.size,
            pendingRequests: this.pendingRequests.size
        };
    }
}

console.log('📝 API Client service loaded successfully');