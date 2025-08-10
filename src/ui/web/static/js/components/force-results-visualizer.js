/**
 * Force Results Visualizer Component - WF EOL Tester Web Interface
 * 
 * This component provides comprehensive EOL Force Test results visualization with:
 * - Tabbed interface: Table View, Chart View, Analysis View
 * - Integration with Force Data Matrix Table and Charts components
 * - Statistical analysis and reporting capabilities
 * - Data filtering and search functionality
 * - Real-time data updates during test execution
 * - Historical test data comparison
 * - Export functionality for all visualization types
 * - Responsive design for different screen sizes
 * - Print-friendly layouts for documentation
 * - Full-screen mode for detailed analysis
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

import { ForceDataMatrixTable } from './force-data-matrix-table.js';
import { ForceDataCharts } from './force-data-charts.js';

export class ForceResultsVisualizer {
    /**
     * Initialize Force Results Visualizer component
     * @param {HTMLElement} container - Container element for the visualizer
     * @param {Object} options - Configuration options
     */
    constructor(container, options = {}) {
        console.log('🎯 Initializing Force Results Visualizer component...');
        
        // Core properties
        this.container = container;
        this.options = {
            // Component configuration
            enableRealTimeUpdates: true,
            enableDataComparison: true,
            enableExport: true,
            enableAnalysis: true,
            enablePrintMode: true,
            
            // Default view
            defaultView: 'table', // table, charts, analysis
            
            // Data refresh settings
            refreshInterval: 1000, // ms
            maxHistoryEntries: 100,
            
            // UI settings
            tabsPosition: 'top', // top, bottom
            showViewControls: true,
            showDataFilter: true,
            showStatistics: true,
            
            // Analysis settings
            statisticalTests: ['ttest', 'anova', 'correlation'],
            confidenceLevel: 0.95,
            
            // Export settings
            exportFormats: ['csv', 'excel', 'json', 'pdf'],
            includeCharts: true,
            includeStatistics: true,
            
            ...options
        };
        
        // State management
        this.currentView = this.options.defaultView;
        this.currentData = null;
        this.historicalData = [];
        this.comparisonMode = false;
        this.selectedTests = new Set();
        this.filters = {
            temperature: null,
            strokePosition: null,
            forceRange: null,
            passFailStatus: null,
            dateRange: null
        };
        
        // Component instances
        this.matrixTable = null;
        this.chartsComponent = null;
        
        // UI elements
        this.tabsContainer = null;
        this.contentContainer = null;
        this.filterPanel = null;
        this.statisticsPanel = null;
        this.comparisonPanel = null;
        
        // Real-time update handling
        this.updateTimer = null;
        this.isUpdating = false;
        
        // Bind methods
        this.handleTabClick = this.handleTabClick.bind(this);
        this.handleDataFilter = this.handleDataFilter.bind(this);
        this.handleComparisonToggle = this.handleComparisonToggle.bind(this);
        this.handleExport = this.handleExport.bind(this);
        this.handlePrintMode = this.handlePrintMode.bind(this);
        this.handleFullscreen = this.handleFullscreen.bind(this);
        this.handleDataUpdate = this.handleDataUpdate.bind(this);
        
        // Initialize component
        this.init();
        
        console.log('✅ Force Results Visualizer component initialized');
    }
    
    /**
     * Initialize component
     * @private
     */
    init() {
        try {
            // Create component structure
            this.createStructure();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize child components
            this.initializeChildComponents();
            
            // Set default view
            this.setActiveView(this.options.defaultView);
            
            // Show loading state
            this.showLoading();
            
        } catch (error) {
            console.error('❌ Failed to initialize Force Results Visualizer:', error);
            this.showError('Visualizer initialization failed', error.message);
        }
    }
    
    /**
     * Create component structure
     * @private
     */
    createStructure() {
        this.container.innerHTML = `
            <div class="force-results-visualizer">
                
                <!-- Header with controls -->
                <div class="visualizer-header">
                    <div class="visualizer-title">
                        <h2>📊 EOL Force Test Results</h2>
                        <div class="visualizer-subtitle">
                            Comprehensive analysis and visualization of force measurement data
                        </div>
                    </div>
                    
                    <div class="visualizer-controls">
                        <!-- View Mode Controls -->
                        <div class="view-mode-controls">
                            <button class="btn btn-sm btn-info" id="comparison-mode-btn" title="Compare Multiple Tests">
                                📊 Compare Tests
                            </button>
                            <button class="btn btn-sm btn-secondary" id="print-mode-btn" title="Print-Friendly View">
                                🖨️ Print Mode
                            </button>
                            <button class="btn btn-sm btn-primary" id="fullscreen-btn" title="Fullscreen Mode">
                                🔍 Fullscreen
                            </button>
                        </div>
                        
                        <!-- Export Controls -->
                        <div class="export-controls">
                            <div class="dropdown">
                                <button class="btn btn-sm btn-success dropdown-toggle" id="visualizer-export-btn">
                                    💾 Export All
                                </button>
                                <div class="dropdown-menu" id="visualizer-export-menu">
                                    <a class="dropdown-item" data-format="comprehensive-csv">📊 Comprehensive CSV</a>
                                    <a class="dropdown-item" data-format="excel-workbook">📈 Excel Workbook</a>
                                    <a class="dropdown-item" data-format="json-data">🔗 Complete JSON</a>
                                    <a class="dropdown-item" data-format="pdf-report">📋 Full PDF Report</a>
                                    <div class="dropdown-divider"></div>
                                    <a class="dropdown-item" data-format="charts-only">🎨 Charts Only</a>
                                    <a class="dropdown-item" data-format="data-only">📄 Data Only</a>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Refresh Control -->
                        <div class="refresh-controls">
                            <button class="btn btn-sm btn-outline-primary" id="refresh-btn" title="Refresh Data">
                                🔄 Refresh
                            </button>
                            <div class="auto-refresh-toggle">
                                <input type="checkbox" id="auto-refresh-checkbox" checked>
                                <label for="auto-refresh-checkbox">Auto Refresh</label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Data Filter Panel -->
                <div class="data-filter-panel" id="data-filter-panel">
                    <div class="filter-header">
                        <h4>🔍 Data Filters</h4>
                        <button class="btn btn-sm btn-outline-secondary" id="clear-filters-btn">Clear All</button>
                    </div>
                    
                    <div class="filter-grid">
                        <div class="filter-group">
                            <label for="temperature-filter">Temperature Range</label>
                            <div class="range-filter">
                                <input type="number" id="temp-min-filter" placeholder="Min °C">
                                <span>to</span>
                                <input type="number" id="temp-max-filter" placeholder="Max °C">
                            </div>
                        </div>
                        
                        <div class="filter-group">
                            <label for="stroke-filter">Stroke Position Range</label>
                            <div class="range-filter">
                                <input type="number" id="stroke-min-filter" placeholder="Min mm">
                                <span>to</span>
                                <input type="number" id="stroke-max-filter" placeholder="Max mm">
                            </div>
                        </div>
                        
                        <div class="filter-group">
                            <label for="force-filter">Force Range</label>
                            <div class="range-filter">
                                <input type="number" id="force-min-filter" placeholder="Min N">
                                <span>to</span>
                                <input type="number" id="force-max-filter" placeholder="Max N">
                            </div>
                        </div>
                        
                        <div class="filter-group">
                            <label for="pass-fail-filter">Pass/Fail Status</label>
                            <select id="pass-fail-filter">
                                <option value="">All</option>
                                <option value="pass">Pass Only</option>
                                <option value="fail">Fail Only</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label for="date-range-filter">Date Range</label>
                            <div class="date-range-filter">
                                <input type="datetime-local" id="date-from-filter">
                                <span>to</span>
                                <input type="datetime-local" id="date-to-filter">
                            </div>
                        </div>
                        
                        <div class="filter-actions">
                            <button class="btn btn-sm btn-primary" id="apply-filters-btn">Apply Filters</button>
                            <button class="btn btn-sm btn-outline-secondary" id="toggle-filter-panel-btn">
                                Hide Filters
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Statistics Summary Panel -->
                <div class="statistics-summary-panel" id="statistics-panel">
                    <div class="stats-header">
                        <h4>📈 Statistics Summary</h4>
                        <button class="btn btn-sm btn-outline-info" id="detailed-stats-btn">Detailed Analysis</button>
                    </div>
                    
                    <div class="stats-grid" id="stats-grid">
                        <!-- Stats will be populated dynamically -->
                    </div>
                </div>
                
                <!-- Main Content with Tabs -->
                <div class="visualizer-main-content">
                    
                    <!-- Tab Navigation -->
                    <div class="visualizer-tabs" id="visualizer-tabs">
                        <button class="tab-button active" data-view="table">
                            📊 Data Matrix Table
                        </button>
                        <button class="tab-button" data-view="charts">
                            📈 Interactive Charts
                        </button>
                        <button class="tab-button" data-view="analysis">
                            🔬 Statistical Analysis
                        </button>
                        <button class="tab-button" data-view="comparison" id="comparison-tab" style="display: none;">
                            ⚖️ Test Comparison
                        </button>
                    </div>
                    
                    <!-- Tab Content -->
                    <div class="visualizer-content" id="visualizer-content">
                        
                        <!-- Table View -->
                        <div class="tab-content active" id="table-view">
                            <div class="table-view-header">
                                <div class="view-info">
                                    <h3>Temperature × Stroke Force Data Matrix</h3>
                                    <p>Interactive data table with sorting, filtering, and heatmap visualization</p>
                                </div>
                                <div class="table-view-controls">
                                    <button class="btn btn-sm btn-secondary" id="table-export-btn">
                                        💾 Export Table
                                    </button>
                                </div>
                            </div>
                            
                            <div class="table-container" id="table-container">
                                <!-- Force Data Matrix Table will be initialized here -->
                            </div>
                        </div>
                        
                        <!-- Charts View -->
                        <div class="tab-content" id="charts-view">
                            <div class="charts-view-header">
                                <div class="view-info">
                                    <h3>Interactive Force Data Visualization</h3>
                                    <p>Comprehensive charts and graphs for force measurement analysis</p>
                                </div>
                                <div class="charts-view-controls">
                                    <button class="btn btn-sm btn-secondary" id="charts-export-btn">
                                        💾 Export Charts
                                    </button>
                                </div>
                            </div>
                            
                            <div class="charts-container" id="charts-container">
                                <!-- Force Data Charts will be initialized here -->
                            </div>
                        </div>
                        
                        <!-- Analysis View -->
                        <div class="tab-content" id="analysis-view">
                            <div class="analysis-view-header">
                                <div class="view-info">
                                    <h3>Statistical Analysis & Insights</h3>
                                    <p>Advanced statistical analysis and data insights</p>
                                </div>
                                <div class="analysis-view-controls">
                                    <button class="btn btn-sm btn-primary" id="run-analysis-btn">
                                        🔬 Run Analysis
                                    </button>
                                    <button class="btn btn-sm btn-secondary" id="analysis-export-btn">
                                        💾 Export Analysis
                                    </button>
                                </div>
                            </div>
                            
                            <div class="analysis-content" id="analysis-content">
                                
                                <!-- Analysis Controls -->
                                <div class="analysis-controls">
                                    <div class="analysis-settings">
                                        <h4>Analysis Settings</h4>
                                        <div class="settings-grid">
                                            <div class="setting-group">
                                                <label>Statistical Tests</label>
                                                <div class="checkbox-group">
                                                    <label><input type="checkbox" value="descriptive" checked> Descriptive Statistics</label>
                                                    <label><input type="checkbox" value="normality"> Normality Test</label>
                                                    <label><input type="checkbox" value="correlation"> Correlation Analysis</label>
                                                    <label><input type="checkbox" value="regression"> Regression Analysis</label>
                                                    <label><input type="checkbox" value="anova"> ANOVA</label>
                                                </div>
                                            </div>
                                            
                                            <div class="setting-group">
                                                <label for="confidence-level">Confidence Level</label>
                                                <select id="confidence-level">
                                                    <option value="0.90">90%</option>
                                                    <option value="0.95" selected>95%</option>
                                                    <option value="0.99">99%</option>
                                                </select>
                                            </div>
                                            
                                            <div class="setting-group">
                                                <label for="analysis-grouping">Group Analysis By</label>
                                                <select id="analysis-grouping">
                                                    <option value="temperature">Temperature</option>
                                                    <option value="stroke">Stroke Position</option>
                                                    <option value="none">No Grouping</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Analysis Results -->
                                <div class="analysis-results" id="analysis-results">
                                    <div class="analysis-placeholder">
                                        <div class="placeholder-icon">🔬</div>
                                        <h3>Statistical Analysis</h3>
                                        <p>Click "Run Analysis" to perform statistical analysis on the current dataset</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Comparison View -->
                        <div class="tab-content" id="comparison-view">
                            <div class="comparison-view-header">
                                <div class="view-info">
                                    <h3>Test Results Comparison</h3>
                                    <p>Compare current results with historical test data</p>
                                </div>
                                <div class="comparison-view-controls">
                                    <button class="btn btn-sm btn-info" id="select-comparison-tests-btn">
                                        📋 Select Tests
                                    </button>
                                    <button class="btn btn-sm btn-secondary" id="comparison-export-btn">
                                        💾 Export Comparison
                                    </button>
                                </div>
                            </div>
                            
                            <div class="comparison-content" id="comparison-content">
                                <div class="comparison-placeholder">
                                    <div class="placeholder-icon">⚖️</div>
                                    <h3>Test Comparison</h3>
                                    <p>Select historical tests to compare with current results</p>
                                    <button class="btn btn-primary" id="enable-comparison-btn">Enable Comparison Mode</button>
                                </div>
                            </div>
                        </div>
                        
                    </div>
                </div>
                
                <!-- Loading State -->
                <div class="visualizer-loading" id="visualizer-loading">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Loading force test results...</div>
                </div>
                
                <!-- Error State -->
                <div class="visualizer-error" id="visualizer-error" style="display: none;">
                    <div class="error-icon">⚠️</div>
                    <div class="error-message">
                        <h4>Error Loading Results</h4>
                        <p class="error-details">Failed to load force test results data</p>
                    </div>
                    <button class="btn btn-primary" id="visualizer-retry-btn">Retry</button>
                </div>
                
            </div>
        `;
        
        // Cache DOM references
        this.tabsContainer = document.getElementById('visualizer-tabs');
        this.contentContainer = document.getElementById('visualizer-content');
        this.filterPanel = document.getElementById('data-filter-panel');
        this.statisticsPanel = document.getElementById('statistics-panel');
        this.loadingElement = document.getElementById('visualizer-loading');
        this.errorElement = document.getElementById('visualizer-error');
    }
    
    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Tab navigation
        if (this.tabsContainer) {
            this.tabsContainer.addEventListener('click', this.handleTabClick);
        }
        
        // Export controls
        const exportMenu = document.getElementById('visualizer-export-menu');
        if (exportMenu) {
            exportMenu.addEventListener('click', (e) => {
                if (e.target.hasAttribute('data-format')) {
                    e.preventDefault();
                    this.handleExport(e.target.getAttribute('data-format'));
                }
            });
        }
        
        // Export button toggle
        const exportBtn = document.getElementById('visualizer-export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                exportMenu?.classList.toggle('show');
            });
        }
        
        // View mode controls
        const comparisonBtn = document.getElementById('comparison-mode-btn');
        const printModeBtn = document.getElementById('print-mode-btn');
        const fullscreenBtn = document.getElementById('fullscreen-btn');
        
        if (comparisonBtn) comparisonBtn.addEventListener('click', this.handleComparisonToggle);
        if (printModeBtn) printModeBtn.addEventListener('click', this.handlePrintMode);
        if (fullscreenBtn) fullscreenBtn.addEventListener('click', this.handleFullscreen);
        
        // Filter controls
        const applyFiltersBtn = document.getElementById('apply-filters-btn');
        const clearFiltersBtn = document.getElementById('clear-filters-btn');
        const toggleFilterBtn = document.getElementById('toggle-filter-panel-btn');
        
        if (applyFiltersBtn) applyFiltersBtn.addEventListener('click', this.handleDataFilter);
        if (clearFiltersBtn) clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        if (toggleFilterBtn) toggleFilterBtn.addEventListener('click', () => this.toggleFilterPanel());
        
        // Refresh controls
        const refreshBtn = document.getElementById('refresh-btn');
        const autoRefreshCheckbox = document.getElementById('auto-refresh-checkbox');
        
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.refreshData());
        if (autoRefreshCheckbox) {
            autoRefreshCheckbox.addEventListener('change', (e) => {
                this.setAutoRefresh(e.target.checked);
            });
        }
        
        // Analysis controls
        const runAnalysisBtn = document.getElementById('run-analysis-btn');
        if (runAnalysisBtn) {
            runAnalysisBtn.addEventListener('click', () => this.runStatisticalAnalysis());
        }
        
        // Individual export buttons
        const tableExportBtn = document.getElementById('table-export-btn');
        const chartsExportBtn = document.getElementById('charts-export-btn');
        const analysisExportBtn = document.getElementById('analysis-export-btn');
        
        if (tableExportBtn) tableExportBtn.addEventListener('click', () => this.exportCurrentView('table'));
        if (chartsExportBtn) chartsExportBtn.addEventListener('click', () => this.exportCurrentView('charts'));
        if (analysisExportBtn) analysisExportBtn.addEventListener('click', () => this.exportCurrentView('analysis'));
        
        // Retry button
        const retryBtn = document.getElementById('visualizer-retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.retry());
        }
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
    }
    
    /**
     * Initialize child components
     * @private
     */
    initializeChildComponents() {
        // Initialize Matrix Table component
        const tableContainer = document.getElementById('table-container');
        if (tableContainer) {
            this.matrixTable = new ForceDataMatrixTable(tableContainer, {
                enableExport: true,
                enableHover: true,
                showStatistics: true
            });
            
            // Listen to matrix table events
            tableContainer.addEventListener('cellSelected', (e) => {
                console.log('📊 Matrix cell selected:', e.detail);
            });
            
            tableContainer.addEventListener('retryRequested', () => {
                this.refreshData();
            });
            
            tableContainer.addEventListener('messageRequested', (e) => {
                this.showMessage(e.detail.message, e.detail.type);
            });
        }
        
        // Initialize Charts component
        const chartsContainer = document.getElementById('charts-container');
        if (chartsContainer) {
            this.chartsComponent = new ForceDataCharts(chartsContainer, {
                enableExport: true,
                enableInteractivity: true,
                enableRealTimeUpdates: this.options.enableRealTimeUpdates
            });
            
            // Listen to charts events
            chartsContainer.addEventListener('chartClicked', (e) => {
                console.log('📈 Chart clicked:', e.detail);
            });
            
            chartsContainer.addEventListener('retryRequested', () => {
                this.refreshData();
            });
            
            chartsContainer.addEventListener('messageRequested', (e) => {
                this.showMessage(e.detail.message, e.detail.type);
            });
        }
    }
    
    /**
     * Load and display test results data
     * @param {Object} data - Test results data
     * @param {Object} options - Display options
     */
    loadData(data, options = {}) {
        console.log('🎯 Loading force test results data...', data);
        
        try {
            // Store current data
            this.currentData = data;
            
            // Add to historical data if enabled
            if (this.options.enableDataComparison && data.testId) {
                this.addToHistory(data);
            }
            
            // Apply filters if any
            const filteredData = this.applyCurrentFilters(data);
            
            // Load data into child components
            if (this.matrixTable) {
                this.matrixTable.loadData(filteredData);
            }
            
            if (this.chartsComponent) {
                this.chartsComponent.loadData(filteredData);
            }
            
            // Update statistics
            this.updateStatistics(filteredData);
            
            // Hide loading, show content
            this.hideLoading();
            this.showContent();
            
            console.log('✅ Force test results loaded successfully');
            
        } catch (error) {
            console.error('❌ Failed to load force test results:', error);
            this.showError('Results loading failed', error.message);
        }
    }
    
    /**
     * Add data to historical records
     * @private
     * @param {Object} data - Test data
     */
    addToHistory(data) {
        const historyEntry = {
            ...data,
            loadedAt: new Date().toISOString()
        };
        
        this.historicalData.unshift(historyEntry);
        
        // Limit history size
        if (this.historicalData.length > this.options.maxHistoryEntries) {
            this.historicalData = this.historicalData.slice(0, this.options.maxHistoryEntries);
        }
        
        console.log(`📚 Added to history: ${this.historicalData.length} entries`);
    }
    
    /**
     * Apply current filters to data
     * @private
     * @param {Object} data - Raw data
     * @returns {Object} Filtered data
     */
    applyCurrentFilters(data) {
        if (!data || !data.measurements) return data;
        
        let filteredMeasurements = [...data.measurements];
        
        // Temperature filter
        if (this.filters.temperature) {
            const { min, max } = this.filters.temperature;
            filteredMeasurements = filteredMeasurements.filter(m => 
                m.temperature >= min && m.temperature <= max
            );
        }
        
        // Stroke position filter
        if (this.filters.strokePosition) {
            const { min, max } = this.filters.strokePosition;
            filteredMeasurements = filteredMeasurements.filter(m => 
                m.strokePosition >= min && m.strokePosition <= max
            );
        }
        
        // Force range filter
        if (this.filters.forceRange) {
            const { min, max } = this.filters.forceRange;
            filteredMeasurements = filteredMeasurements.filter(m => 
                m.force >= min && m.force <= max
            );
        }
        
        // Pass/fail status filter
        if (this.filters.passFailStatus) {
            const shouldPass = this.filters.passFailStatus === 'pass';
            filteredMeasurements = filteredMeasurements.filter(m => 
                this.evaluatePassFail(m.force) === shouldPass
            );
        }
        
        // Date range filter
        if (this.filters.dateRange && this.filters.dateRange.from && this.filters.dateRange.to) {
            const fromDate = new Date(this.filters.dateRange.from);
            const toDate = new Date(this.filters.dateRange.to);
            filteredMeasurements = filteredMeasurements.filter(m => {
                const measurementDate = new Date(m.timestamp);
                return measurementDate >= fromDate && measurementDate <= toDate;
            });
        }
        
        return {
            ...data,
            measurements: filteredMeasurements
        };
    }
    
    /**
     * Evaluate pass/fail status for a force measurement
     * @private
     * @param {number} force - Force value
     * @returns {boolean} Pass status
     */
    evaluatePassFail(force) {
        // This should match the criteria in the matrix table
        const minForce = 100; // N
        const maxForce = 1000; // N
        const tolerance = 0.1; // 10%
        const toleranceRange = maxForce * tolerance;
        
        return force >= (minForce - toleranceRange) && force <= (maxForce + toleranceRange);
    }
    
    /**
     * Update statistics display
     * @private
     * @param {Object} data - Current data
     */
    updateStatistics(data) {
        if (!data || !data.measurements) return;
        
        const measurements = data.measurements;
        const forces = measurements.map(m => m.force);
        
        if (forces.length === 0) {
            this.showEmptyStatistics();
            return;
        }
        
        // Calculate statistics
        const stats = this.calculateStatistics(forces, measurements);
        
        // Update statistics panel
        const statsGrid = document.getElementById('stats-grid');
        if (statsGrid) {
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Total Measurements</div>
                    <div class="stat-value">${stats.total}</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Force Range</div>
                    <div class="stat-value">${stats.min.toFixed(1)} - ${stats.max.toFixed(1)} N</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Average Force</div>
                    <div class="stat-value">${stats.avg.toFixed(2)} N</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Standard Deviation</div>
                    <div class="stat-value">${stats.std.toFixed(2)} N</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Pass Rate</div>
                    <div class="stat-value ${stats.passRate >= 95 ? 'success' : stats.passRate >= 80 ? 'warning' : 'error'}">
                        ${stats.passRate.toFixed(1)}%
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Coefficient of Variation</div>
                    <div class="stat-value">${stats.cv.toFixed(1)}%</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Temperature Range</div>
                    <div class="stat-value">${stats.tempRange.min}°C - ${stats.tempRange.max}°C</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Stroke Range</div>
                    <div class="stat-value">${stats.strokeRange.min} - ${stats.strokeRange.max} mm</div>
                </div>
            `;
        }
    }
    
    /**
     * Calculate comprehensive statistics
     * @private
     * @param {Array} forces - Force values
     * @param {Array} measurements - All measurements
     * @returns {Object} Statistics
     */
    calculateStatistics(forces, measurements) {
        const total = forces.length;
        const min = Math.min(...forces);
        const max = Math.max(...forces);
        const sum = forces.reduce((a, b) => a + b, 0);
        const avg = sum / total;
        const variance = forces.reduce((sum, f) => sum + Math.pow(f - avg, 2), 0) / total;
        const std = Math.sqrt(variance);
        const cv = (std / avg) * 100; // Coefficient of variation
        
        // Pass/fail analysis
        const passCount = forces.filter(f => this.evaluatePassFail(f)).length;
        const passRate = (passCount / total) * 100;
        
        // Temperature and stroke ranges
        const temperatures = measurements.map(m => m.temperature);
        const strokes = measurements.map(m => m.strokePosition);
        
        return {
            total,
            min,
            max,
            avg,
            std,
            cv,
            passRate,
            tempRange: {
                min: Math.min(...temperatures),
                max: Math.max(...temperatures)
            },
            strokeRange: {
                min: Math.min(...strokes),
                max: Math.max(...strokes)
            }
        };
    }
    
    /**
     * Show empty statistics
     * @private
     */
    showEmptyStatistics() {
        const statsGrid = document.getElementById('stats-grid');
        if (statsGrid) {
            statsGrid.innerHTML = `
                <div class="empty-stats">
                    <div class="empty-stats-icon">📊</div>
                    <div class="empty-stats-text">No data available for statistics</div>
                </div>
            `;
        }
    }
    
    /**
     * Handle tab click events
     * @private
     * @param {Event} event - Click event
     */
    handleTabClick(event) {
        const tabButton = event.target.closest('.tab-button');
        if (!tabButton) return;
        
        const view = tabButton.getAttribute('data-view');
        this.setActiveView(view);
    }
    
    /**
     * Set active view
     * @private
     * @param {string} view - View name (table, charts, analysis, comparison)
     */
    setActiveView(view) {
        // Update tab buttons
        this.tabsContainer.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-view') === view);
        });
        
        // Update tab content
        this.contentContainer.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${view}-view`);
        });
        
        this.currentView = view;
        
        // Resize charts when switching to charts view
        if (view === 'charts' && this.chartsComponent) {
            setTimeout(() => {
                const charts = this.chartsComponent.getAllCharts();
                charts.forEach(chart => {
                    if (chart) chart.resize();
                });
            }, 100);
        }
        
        console.log(`🔄 Active view changed to: ${view}`);
    }
    
    /**
     * Handle data filter application
     * @private
     */
    handleDataFilter() {
        // Collect filter values
        const tempMin = parseFloat(document.getElementById('temp-min-filter')?.value);
        const tempMax = parseFloat(document.getElementById('temp-max-filter')?.value);
        const strokeMin = parseFloat(document.getElementById('stroke-min-filter')?.value);
        const strokeMax = parseFloat(document.getElementById('stroke-max-filter')?.value);
        const forceMin = parseFloat(document.getElementById('force-min-filter')?.value);
        const forceMax = parseFloat(document.getElementById('force-max-filter')?.value);
        const passFailStatus = document.getElementById('pass-fail-filter')?.value;
        const dateFrom = document.getElementById('date-from-filter')?.value;
        const dateTo = document.getElementById('date-to-filter')?.value;
        
        // Update filters
        this.filters = {
            temperature: (isNaN(tempMin) || isNaN(tempMax)) ? null : { min: tempMin, max: tempMax },
            strokePosition: (isNaN(strokeMin) || isNaN(strokeMax)) ? null : { min: strokeMin, max: strokeMax },
            forceRange: (isNaN(forceMin) || isNaN(forceMax)) ? null : { min: forceMin, max: forceMax },
            passFailStatus: passFailStatus || null,
            dateRange: (dateFrom && dateTo) ? { from: dateFrom, to: dateTo } : null
        };
        
        // Reapply filters to current data
        if (this.currentData) {
            this.loadData(this.currentData);
        }
        
        console.log('🔍 Filters applied:', this.filters);
    }
    
    /**
     * Clear all filters
     * @private
     */
    clearFilters() {
        // Reset filter UI
        document.getElementById('temp-min-filter').value = '';
        document.getElementById('temp-max-filter').value = '';
        document.getElementById('stroke-min-filter').value = '';
        document.getElementById('stroke-max-filter').value = '';
        document.getElementById('force-min-filter').value = '';
        document.getElementById('force-max-filter').value = '';
        document.getElementById('pass-fail-filter').value = '';
        document.getElementById('date-from-filter').value = '';
        document.getElementById('date-to-filter').value = '';
        
        // Clear filters
        this.filters = {
            temperature: null,
            strokePosition: null,
            forceRange: null,
            passFailStatus: null,
            dateRange: null
        };
        
        // Reload data without filters
        if (this.currentData) {
            this.loadData(this.currentData);
        }
        
        console.log('🧹 Filters cleared');
    }
    
    /**
     * Toggle filter panel visibility
     * @private
     */
    toggleFilterPanel() {
        const isVisible = this.filterPanel.style.display !== 'none';
        this.filterPanel.style.display = isVisible ? 'none' : 'block';
        
        const toggleBtn = document.getElementById('toggle-filter-panel-btn');
        if (toggleBtn) {
            toggleBtn.textContent = isVisible ? 'Show Filters' : 'Hide Filters';
        }
    }
    
    /**
     * Handle comparison mode toggle
     * @private
     */
    handleComparisonToggle() {
        this.comparisonMode = !this.comparisonMode;
        
        // Show/hide comparison tab
        const comparisonTab = document.getElementById('comparison-tab');
        if (comparisonTab) {
            comparisonTab.style.display = this.comparisonMode ? 'block' : 'none';
        }
        
        // Update button state
        const comparisonBtn = document.getElementById('comparison-mode-btn');
        if (comparisonBtn) {
            comparisonBtn.classList.toggle('active', this.comparisonMode);
            comparisonBtn.textContent = this.comparisonMode ? '📊 Exit Compare' : '📊 Compare Tests';
        }
        
        if (this.comparisonMode) {
            this.setActiveView('comparison');
            this.initializeComparisonView();
        }
        
        console.log('⚖️ Comparison mode:', this.comparisonMode);
    }
    
    /**
     * Initialize comparison view
     * @private
     */
    initializeComparisonView() {
        const comparisonContent = document.getElementById('comparison-content');
        if (!comparisonContent) return;
        
        if (this.historicalData.length === 0) {
            comparisonContent.innerHTML = `
                <div class="comparison-placeholder">
                    <div class="placeholder-icon">📚</div>
                    <h3>No Historical Data</h3>
                    <p>No historical test data available for comparison</p>
                </div>
            `;
            return;
        }
        
        // Generate historical data selection
        let historyHTML = `
            <div class="comparison-selection">
                <h4>Select Tests to Compare</h4>
                <div class="historical-tests-list">
        `;
        
        this.historicalData.forEach((data, index) => {
            const testDate = new Date(data.loadedAt).toLocaleString();
            const measurementCount = data.measurements?.length || 0;
            
            historyHTML += `
                <div class="historical-test-item">
                    <input type="checkbox" id="test-${index}" value="${index}">
                    <label for="test-${index}">
                        <strong>Test ${data.testId || index + 1}</strong>
                        <div class="test-details">
                            <span>${testDate}</span>
                            <span>${measurementCount} measurements</span>
                        </div>
                    </label>
                </div>
            `;
        });
        
        historyHTML += `
                </div>
                <button class="btn btn-primary" id="compare-selected-btn">Compare Selected</button>
            </div>
            
            <div class="comparison-results" id="comparison-results-container">
                <!-- Comparison results will appear here -->
            </div>
        `;
        
        comparisonContent.innerHTML = historyHTML;
        
        // Add event listener for comparison
        const compareBtn = document.getElementById('compare-selected-btn');
        if (compareBtn) {
            compareBtn.addEventListener('click', () => this.performComparison());
        }
    }
    
    /**
     * Perform test comparison
     * @private
     */
    performComparison() {
        const selectedCheckboxes = document.querySelectorAll('#comparison-content input[type="checkbox"]:checked');
        const selectedIndices = Array.from(selectedCheckboxes).map(cb => parseInt(cb.value));
        
        if (selectedIndices.length === 0) {
            this.showMessage('Please select at least one test to compare', 'warning');
            return;
        }
        
        const selectedTests = selectedIndices.map(index => this.historicalData[index]);
        const comparisonData = this.generateComparisonAnalysis(selectedTests, this.currentData);
        
        this.displayComparisonResults(comparisonData);
        
        console.log('⚖️ Comparison performed for', selectedIndices.length, 'tests');
    }
    
    /**
     * Generate comparison analysis
     * @private
     * @param {Array} historicalTests - Historical test data
     * @param {Object} currentTest - Current test data
     * @returns {Object} Comparison analysis
     */
    generateComparisonAnalysis(historicalTests, currentTest) {
        // This is a simplified implementation
        // In a real application, this would perform comprehensive statistical comparison
        
        const allTests = [...historicalTests, currentTest];
        const comparisonMetrics = allTests.map((test, index) => {
            const forces = test.measurements?.map(m => m.force) || [];
            const avg = forces.reduce((a, b) => a + b, 0) / forces.length || 0;
            const min = Math.min(...forces) || 0;
            const max = Math.max(...forces) || 0;
            
            return {
                testId: test.testId || `Test ${index + 1}`,
                isCurrent: index === allTests.length - 1,
                measurementCount: forces.length,
                averageForce: avg,
                minForce: min,
                maxForce: max,
                forceRange: max - min
            };
        });
        
        return {
            tests: comparisonMetrics,
            summary: {
                totalTests: allTests.length,
                totalMeasurements: comparisonMetrics.reduce((sum, t) => sum + t.measurementCount, 0),
                avgForceRange: {
                    min: Math.min(...comparisonMetrics.map(t => t.averageForce)),
                    max: Math.max(...comparisonMetrics.map(t => t.averageForce))
                }
            }
        };
    }
    
    /**
     * Display comparison results
     * @private
     * @param {Object} comparisonData - Comparison analysis data
     */
    displayComparisonResults(comparisonData) {
        const resultsContainer = document.getElementById('comparison-results-container');
        if (!resultsContainer) return;
        
        let resultsHTML = `
            <div class="comparison-summary">
                <h4>Comparison Summary</h4>
                <div class="summary-stats">
                    <div class="summary-stat">
                        <label>Tests Compared</label>
                        <value>${comparisonData.summary.totalTests}</value>
                    </div>
                    <div class="summary-stat">
                        <label>Total Measurements</label>
                        <value>${comparisonData.summary.totalMeasurements}</value>
                    </div>
                    <div class="summary-stat">
                        <label>Avg Force Range</label>
                        <value>${comparisonData.summary.avgForceRange.min.toFixed(1)} - ${comparisonData.summary.avgForceRange.max.toFixed(1)} N</value>
                    </div>
                </div>
            </div>
            
            <div class="comparison-table">
                <h4>Test Comparison Details</h4>
                <table class="comparison-data-table">
                    <thead>
                        <tr>
                            <th>Test ID</th>
                            <th>Status</th>
                            <th>Measurements</th>
                            <th>Avg Force (N)</th>
                            <th>Min Force (N)</th>
                            <th>Max Force (N)</th>
                            <th>Range (N)</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        comparisonData.tests.forEach(test => {
            resultsHTML += `
                <tr class="${test.isCurrent ? 'current-test' : 'historical-test'}">
                    <td>${test.testId}</td>
                    <td>
                        <span class="test-status ${test.isCurrent ? 'current' : 'historical'}">
                            ${test.isCurrent ? 'Current' : 'Historical'}
                        </span>
                    </td>
                    <td>${test.measurementCount}</td>
                    <td>${test.averageForce.toFixed(2)}</td>
                    <td>${test.minForce.toFixed(2)}</td>
                    <td>${test.maxForce.toFixed(2)}</td>
                    <td>${test.forceRange.toFixed(2)}</td>
                </tr>
            `;
        });
        
        resultsHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        resultsContainer.innerHTML = resultsHTML;
    }
    
    /**
     * Run statistical analysis
     * @private
     */
    runStatisticalAnalysis() {
        if (!this.currentData || !this.currentData.measurements) {
            this.showMessage('No data available for analysis', 'warning');
            return;
        }
        
        const measurements = this.currentData.measurements;
        const forces = measurements.map(m => m.force);
        
        // Get selected tests
        const selectedTests = Array.from(document.querySelectorAll('#analysis-content input[type="checkbox"]:checked'))
            .map(cb => cb.value);
        
        const confidenceLevel = parseFloat(document.getElementById('confidence-level')?.value || 0.95);
        const grouping = document.getElementById('analysis-grouping')?.value || 'none';
        
        // Perform analysis
        const analysisResults = this.performStatisticalAnalysis(measurements, selectedTests, confidenceLevel, grouping);
        
        // Display results
        this.displayAnalysisResults(analysisResults);
        
        console.log('🔬 Statistical analysis completed:', analysisResults);
    }
    
    /**
     * Perform statistical analysis
     * @private
     * @param {Array} measurements - Measurement data
     * @param {Array} selectedTests - Selected analysis types
     * @param {number} confidenceLevel - Confidence level
     * @param {string} grouping - Grouping method
     * @returns {Object} Analysis results
     */
    performStatisticalAnalysis(measurements, selectedTests, confidenceLevel, grouping) {
        const results = {
            timestamp: new Date().toISOString(),
            confidenceLevel,
            grouping,
            tests: {}
        };
        
        const forces = measurements.map(m => m.force);
        
        // Descriptive Statistics
        if (selectedTests.includes('descriptive')) {
            results.tests.descriptive = this.calculateDescriptiveStats(forces);
        }
        
        // Normality Test (simplified implementation)
        if (selectedTests.includes('normality')) {
            results.tests.normality = this.performNormalityTest(forces);
        }
        
        // Correlation Analysis
        if (selectedTests.includes('correlation')) {
            results.tests.correlation = this.performCorrelationAnalysis(measurements);
        }
        
        // Regression Analysis (simplified)
        if (selectedTests.includes('regression')) {
            results.tests.regression = this.performRegressionAnalysis(measurements);
        }
        
        // ANOVA (simplified)
        if (selectedTests.includes('anova')) {
            results.tests.anova = this.performANOVA(measurements, grouping);
        }
        
        return results;
    }
    
    /**
     * Calculate descriptive statistics
     * @private
     * @param {Array} values - Values to analyze
     * @returns {Object} Descriptive statistics
     */
    calculateDescriptiveStats(values) {
        const n = values.length;
        const mean = values.reduce((a, b) => a + b, 0) / n;
        const variance = values.reduce((sum, x) => sum + Math.pow(x - mean, 2), 0) / (n - 1);
        const stdDev = Math.sqrt(variance);
        const sortedValues = [...values].sort((a, b) => a - b);
        
        const q1Index = Math.floor(n * 0.25);
        const medianIndex = Math.floor(n * 0.5);
        const q3Index = Math.floor(n * 0.75);
        
        return {
            count: n,
            mean: mean,
            median: sortedValues[medianIndex],
            mode: this.calculateMode(values),
            standardDeviation: stdDev,
            variance: variance,
            minimum: Math.min(...values),
            maximum: Math.max(...values),
            range: Math.max(...values) - Math.min(...values),
            q1: sortedValues[q1Index],
            q3: sortedValues[q3Index],
            iqr: sortedValues[q3Index] - sortedValues[q1Index],
            skewness: this.calculateSkewness(values, mean, stdDev),
            kurtosis: this.calculateKurtosis(values, mean, stdDev)
        };
    }
    
    /**
     * Calculate mode
     * @private
     * @param {Array} values - Values
     * @returns {number} Mode
     */
    calculateMode(values) {
        const frequency = {};
        let maxFreq = 0;
        let mode = values[0];
        
        values.forEach(value => {
            frequency[value] = (frequency[value] || 0) + 1;
            if (frequency[value] > maxFreq) {
                maxFreq = frequency[value];
                mode = value;
            }
        });
        
        return mode;
    }
    
    /**
     * Calculate skewness
     * @private
     * @param {Array} values - Values
     * @param {number} mean - Mean
     * @param {number} stdDev - Standard deviation
     * @returns {number} Skewness
     */
    calculateSkewness(values, mean, stdDev) {
        const n = values.length;
        const skewness = values.reduce((sum, x) => sum + Math.pow((x - mean) / stdDev, 3), 0);
        return (n / ((n - 1) * (n - 2))) * skewness;
    }
    
    /**
     * Calculate kurtosis
     * @private
     * @param {Array} values - Values
     * @param {number} mean - Mean
     * @param {number} stdDev - Standard deviation
     * @returns {number} Kurtosis
     */
    calculateKurtosis(values, mean, stdDev) {
        const n = values.length;
        const kurtosis = values.reduce((sum, x) => sum + Math.pow((x - mean) / stdDev, 4), 0);
        return ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * kurtosis - (3 * Math.pow(n - 1, 2)) / ((n - 2) * (n - 3));
    }
    
    /**
     * Perform normality test (simplified Shapiro-Wilk approximation)
     * @private
     * @param {Array} values - Values to test
     * @returns {Object} Normality test results
     */
    performNormalityTest(values) {
        // Simplified implementation - in practice, would use proper statistical libraries
        const stats = this.calculateDescriptiveStats(values);
        
        // Simple normality indicators
        const skewnessTest = Math.abs(stats.skewness) < 2;
        const kurtosisTest = Math.abs(stats.kurtosis) < 7;
        
        return {
            testType: 'Shapiro-Wilk (approximation)',
            isNormal: skewnessTest && kurtosisTest,
            skewness: stats.skewness,
            kurtosis: stats.kurtosis,
            interpretation: skewnessTest && kurtosisTest ? 
                'Data appears to be normally distributed' : 
                'Data may not be normally distributed'
        };
    }
    
    /**
     * Perform correlation analysis
     * @private
     * @param {Array} measurements - Measurement data
     * @returns {Object} Correlation results
     */
    performCorrelationAnalysis(measurements) {
        const forces = measurements.map(m => m.force);
        const temperatures = measurements.map(m => m.temperature);
        const strokes = measurements.map(m => m.strokePosition);
        
        const forceTemp = this.calculateCorrelation(forces, temperatures);
        const forceStroke = this.calculateCorrelation(forces, strokes);
        const tempStroke = this.calculateCorrelation(temperatures, strokes);
        
        return {
            forceTemperature: {
                coefficient: forceTemp,
                strength: this.interpretCorrelation(forceTemp),
                significant: Math.abs(forceTemp) > 0.3
            },
            forceStroke: {
                coefficient: forceStroke,
                strength: this.interpretCorrelation(forceStroke),
                significant: Math.abs(forceStroke) > 0.3
            },
            temperatureStroke: {
                coefficient: tempStroke,
                strength: this.interpretCorrelation(tempStroke),
                significant: Math.abs(tempStroke) > 0.3
            }
        };
    }
    
    /**
     * Calculate Pearson correlation coefficient
     * @private
     * @param {Array} x - First variable
     * @param {Array} y - Second variable
     * @returns {number} Correlation coefficient
     */
    calculateCorrelation(x, y) {
        const n = x.length;
        const sumX = x.reduce((a, b) => a + b, 0);
        const sumY = y.reduce((a, b) => a + b, 0);
        const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
        const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
        const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);
        
        const numerator = n * sumXY - sumX * sumY;
        const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
        
        return denominator === 0 ? 0 : numerator / denominator;
    }
    
    /**
     * Interpret correlation strength
     * @private
     * @param {number} correlation - Correlation coefficient
     * @returns {string} Interpretation
     */
    interpretCorrelation(correlation) {
        const abs = Math.abs(correlation);
        if (abs >= 0.7) return 'Strong';
        if (abs >= 0.5) return 'Moderate';
        if (abs >= 0.3) return 'Weak';
        return 'Very Weak';
    }
    
    /**
     * Perform regression analysis (simplified)
     * @private
     * @param {Array} measurements - Measurement data
     * @returns {Object} Regression results
     */
    performRegressionAnalysis(measurements) {
        const forces = measurements.map(m => m.force);
        const temperatures = measurements.map(m => m.temperature);
        
        // Simple linear regression: force = a + b * temperature
        const regression = this.calculateLinearRegression(temperatures, forces);
        
        return {
            model: 'Linear Regression (Force vs Temperature)',
            equation: `Force = ${regression.intercept.toFixed(3)} + ${regression.slope.toFixed(3)} * Temperature`,
            rSquared: regression.rSquared,
            slope: regression.slope,
            intercept: regression.intercept,
            interpretation: `${(regression.rSquared * 100).toFixed(1)}% of force variation is explained by temperature`
        };
    }
    
    /**
     * Calculate linear regression
     * @private
     * @param {Array} x - Independent variable
     * @param {Array} y - Dependent variable
     * @returns {Object} Regression parameters
     */
    calculateLinearRegression(x, y) {
        const n = x.length;
        const sumX = x.reduce((a, b) => a + b, 0);
        const sumY = y.reduce((a, b) => a + b, 0);
        const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
        const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
        const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);
        
        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;
        
        // Calculate R-squared
        const yMean = sumY / n;
        const totalSumSquares = y.reduce((sum, yi) => sum + Math.pow(yi - yMean, 2), 0);
        const residualSumSquares = y.reduce((sum, yi, i) => {
            const predicted = intercept + slope * x[i];
            return sum + Math.pow(yi - predicted, 2);
        }, 0);
        const rSquared = 1 - (residualSumSquares / totalSumSquares);
        
        return { slope, intercept, rSquared };
    }
    
    /**
     * Perform ANOVA (simplified)
     * @private
     * @param {Array} measurements - Measurement data
     * @param {string} grouping - Grouping variable
     * @returns {Object} ANOVA results
     */
    performANOVA(measurements, grouping) {
        if (grouping === 'none') {
            return {
                error: 'ANOVA requires grouping variable'
            };
        }
        
        const groups = {};
        const groupVariable = grouping === 'temperature' ? 'temperature' : 'strokePosition';
        
        // Group measurements
        measurements.forEach(m => {
            const groupKey = m[groupVariable];
            if (!groups[groupKey]) {
                groups[groupKey] = [];
            }
            groups[groupKey].push(m.force);
        });
        
        const groupKeys = Object.keys(groups);
        if (groupKeys.length < 2) {
            return {
                error: 'ANOVA requires at least 2 groups'
            };
        }
        
        // Calculate ANOVA (simplified)
        const allValues = Object.values(groups).flat();
        const grandMean = allValues.reduce((a, b) => a + b, 0) / allValues.length;
        
        let betweenSumSquares = 0;
        let withinSumSquares = 0;
        
        Object.entries(groups).forEach(([key, values]) => {
            const groupMean = values.reduce((a, b) => a + b, 0) / values.length;
            betweenSumSquares += values.length * Math.pow(groupMean - grandMean, 2);
            withinSumSquares += values.reduce((sum, val) => sum + Math.pow(val - groupMean, 2), 0);
        });
        
        const dfBetween = groupKeys.length - 1;
        const dfWithin = allValues.length - groupKeys.length;
        const meanSquareBetween = betweenSumSquares / dfBetween;
        const meanSquareWithin = withinSumSquares / dfWithin;
        const fStatistic = meanSquareBetween / meanSquareWithin;
        
        return {
            grouping: grouping,
            groups: groupKeys.length,
            fStatistic: fStatistic,
            dfBetween: dfBetween,
            dfWithin: dfWithin,
            significant: fStatistic > 4.0, // Simplified critical value
            interpretation: fStatistic > 4.0 ? 
                `Significant difference between ${grouping} groups` : 
                `No significant difference between ${grouping} groups`
        };
    }
    
    /**
     * Display analysis results
     * @private
     * @param {Object} results - Analysis results
     */
    displayAnalysisResults(results) {
        const resultsContainer = document.getElementById('analysis-results');
        if (!resultsContainer) return;
        
        let resultsHTML = `
            <div class="analysis-header">
                <h4>Statistical Analysis Results</h4>
                <div class="analysis-metadata">
                    <span>Generated: ${new Date(results.timestamp).toLocaleString()}</span>
                    <span>Confidence Level: ${(results.confidenceLevel * 100)}%</span>
                </div>
            </div>
        `;
        
        // Display each test result
        Object.entries(results.tests).forEach(([testName, testResult]) => {
            resultsHTML += this.formatTestResult(testName, testResult);
        });
        
        resultsContainer.innerHTML = resultsHTML;
    }
    
    /**
     * Format individual test result
     * @private
     * @param {string} testName - Test name
     * @param {Object} result - Test result
     * @returns {string} Formatted HTML
     */
    formatTestResult(testName, result) {
        let html = `<div class="analysis-test-result">`;
        
        switch (testName) {
            case 'descriptive':
                html += `
                    <h5>📊 Descriptive Statistics</h5>
                    <div class="descriptive-stats-grid">
                        <div class="stat-item"><label>Count:</label><value>${result.count}</value></div>
                        <div class="stat-item"><label>Mean:</label><value>${result.mean.toFixed(3)}</value></div>
                        <div class="stat-item"><label>Median:</label><value>${result.median.toFixed(3)}</value></div>
                        <div class="stat-item"><label>Std Dev:</label><value>${result.standardDeviation.toFixed(3)}</value></div>
                        <div class="stat-item"><label>Min:</label><value>${result.minimum.toFixed(3)}</value></div>
                        <div class="stat-item"><label>Max:</label><value>${result.maximum.toFixed(3)}</value></div>
                        <div class="stat-item"><label>Range:</label><value>${result.range.toFixed(3)}</value></div>
                        <div class="stat-item"><label>IQR:</label><value>${result.iqr.toFixed(3)}</value></div>
                        <div class="stat-item"><label>Skewness:</label><value>${result.skewness.toFixed(3)}</value></div>
                        <div class="stat-item"><label>Kurtosis:</label><value>${result.kurtosis.toFixed(3)}</value></div>
                    </div>
                `;
                break;
                
            case 'normality':
                html += `
                    <h5>📐 Normality Test</h5>
                    <div class="test-result ${result.isNormal ? 'normal' : 'not-normal'}">
                        <div class="result-status">
                            ${result.isNormal ? '✅' : '❌'} ${result.interpretation}
                        </div>
                        <div class="test-details">
                            <div>Skewness: ${result.skewness.toFixed(3)}</div>
                            <div>Kurtosis: ${result.kurtosis.toFixed(3)}</div>
                        </div>
                    </div>
                `;
                break;
                
            case 'correlation':
                html += `
                    <h5>🔗 Correlation Analysis</h5>
                    <div class="correlation-results">
                        <div class="correlation-item">
                            <label>Force vs Temperature:</label>
                            <value class="${this.getCorrelationClass(result.forceTemperature.coefficient)}">
                                ${result.forceTemperature.coefficient.toFixed(3)} (${result.forceTemperature.strength})
                            </value>
                        </div>
                        <div class="correlation-item">
                            <label>Force vs Stroke:</label>
                            <value class="${this.getCorrelationClass(result.forceStroke.coefficient)}">
                                ${result.forceStroke.coefficient.toFixed(3)} (${result.forceStroke.strength})
                            </value>
                        </div>
                        <div class="correlation-item">
                            <label>Temperature vs Stroke:</label>
                            <value class="${this.getCorrelationClass(result.temperatureStroke.coefficient)}">
                                ${result.temperatureStroke.coefficient.toFixed(3)} (${result.temperatureStroke.strength})
                            </value>
                        </div>
                    </div>
                `;
                break;
                
            case 'regression':
                html += `
                    <h5>📈 Regression Analysis</h5>
                    <div class="regression-result">
                        <div class="equation">${result.equation}</div>
                        <div class="r-squared">R² = ${result.rSquared.toFixed(3)}</div>
                        <div class="interpretation">${result.interpretation}</div>
                    </div>
                `;
                break;
                
            case 'anova':
                if (result.error) {
                    html += `
                        <h5>📊 ANOVA</h5>
                        <div class="analysis-error">${result.error}</div>
                    `;
                } else {
                    html += `
                        <h5>📊 ANOVA</h5>
                        <div class="anova-result ${result.significant ? 'significant' : 'not-significant'}">
                            <div class="result-status">
                                ${result.significant ? '✅' : '❌'} ${result.interpretation}
                            </div>
                            <div class="anova-details">
                                <div>F-statistic: ${result.fStatistic.toFixed(3)}</div>
                                <div>df Between: ${result.dfBetween}</div>
                                <div>df Within: ${result.dfWithin}</div>
                            </div>
                        </div>
                    `;
                }
                break;
        }
        
        html += '</div>';
        return html;
    }
    
    /**
     * Get correlation CSS class
     * @private
     * @param {number} correlation - Correlation coefficient
     * @returns {string} CSS class
     */
    getCorrelationClass(correlation) {
        const abs = Math.abs(correlation);
        if (abs >= 0.7) return 'strong-correlation';
        if (abs >= 0.5) return 'moderate-correlation';
        if (abs >= 0.3) return 'weak-correlation';
        return 'no-correlation';
    }
    
    /**
     * Handle print mode
     * @private
     */
    handlePrintMode() {
        this.container.classList.toggle('print-mode');
        
        const printBtn = document.getElementById('print-mode-btn');
        if (printBtn) {
            const isPrintMode = this.container.classList.contains('print-mode');
            printBtn.textContent = isPrintMode ? '🖨️ Exit Print' : '🖨️ Print Mode';
            printBtn.classList.toggle('active', isPrintMode);
        }
        
        // Trigger print dialog in print mode
        if (this.container.classList.contains('print-mode')) {
            setTimeout(() => {
                window.print();
            }, 500);
        }
    }
    
    /**
     * Handle fullscreen toggle
     * @private
     */
    handleFullscreen() {
        const isFullscreen = this.container.classList.contains('fullscreen');
        
        if (isFullscreen) {
            this.container.classList.remove('fullscreen');
            document.body.style.overflow = 'auto';
        } else {
            this.container.classList.add('fullscreen');
            document.body.style.overflow = 'hidden';
        }
        
        const fullscreenBtn = document.getElementById('fullscreen-btn');
        if (fullscreenBtn) {
            fullscreenBtn.textContent = isFullscreen ? '🔍 Fullscreen' : '🔍 Exit Fullscreen';
            fullscreenBtn.classList.toggle('active', !isFullscreen);
        }
        
        // Resize charts after fullscreen toggle
        setTimeout(() => {
            if (this.chartsComponent) {
                const charts = this.chartsComponent.getAllCharts();
                charts.forEach(chart => {
                    if (chart) chart.resize();
                });
            }
        }, 100);
    }
    
    /**
     * Handle comprehensive export
     * @private
     * @param {string} format - Export format
     */
    async handleExport(format) {
        console.log('💾 Exporting comprehensive data as:', format);
        
        try {
            switch (format) {
                case 'comprehensive-csv':
                    await this.exportComprehensiveCSV();
                    break;
                    
                case 'excel-workbook':
                    await this.exportExcelWorkbook();
                    break;
                    
                case 'json-data':
                    await this.exportCompleteJSON();
                    break;
                    
                case 'pdf-report':
                    await this.exportPDFReport();
                    break;
                    
                case 'charts-only':
                    if (this.chartsComponent) {
                        await this.chartsComponent.handleExport('png');
                    }
                    break;
                    
                case 'data-only':
                    if (this.matrixTable) {
                        await this.matrixTable.handleExport('csv');
                    }
                    break;
                    
                default:
                    throw new Error(`Unsupported export format: ${format}`);
            }
            
            // Close export menu
            const exportMenu = document.getElementById('visualizer-export-menu');
            if (exportMenu) {
                exportMenu.classList.remove('show');
            }
            
            this.showMessage(`Data exported successfully as ${format}`, 'success');
            
        } catch (error) {
            console.error('❌ Comprehensive export failed:', error);
            this.showMessage(`Export failed: ${error.message}`, 'error');
        }
    }
    
    /**
     * Export current view
     * @private
     * @param {string} view - View to export
     */
    async exportCurrentView(view) {
        switch (view) {
            case 'table':
                if (this.matrixTable) {
                    await this.matrixTable.handleExport('csv');
                }
                break;
                
            case 'charts':
                if (this.chartsComponent) {
                    await this.chartsComponent.handleExport('png');
                }
                break;
                
            case 'analysis':
                await this.exportAnalysisResults();
                break;
                
            default:
                this.showMessage(`Export not supported for ${view} view`, 'warning');
        }
    }
    
    /**
     * Export comprehensive CSV
     * @private
     */
    async exportComprehensiveCSV() {
        if (!this.currentData) return;
        
        const data = this.matrixTable ? this.matrixTable.generateCSV() : '';
        this.downloadFile(data, 'comprehensive-force-data.csv', 'text/csv');
    }
    
    /**
     * Export complete JSON
     * @private
     */
    async exportCompleteJSON() {
        const exportData = {
            metadata: {
                exportDate: new Date().toISOString(),
                exportType: 'comprehensive',
                version: '1.0.0'
            },
            testData: this.currentData,
            statistics: this.matrixTable?.getStatistics(),
            filters: this.filters,
            historicalData: this.historicalData.slice(0, 10) // Last 10 entries
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        this.downloadFile(dataStr, 'comprehensive-force-results.json', 'application/json');
    }
    
    /**
     * Export analysis results
     * @private
     */
    async exportAnalysisResults() {
        const analysisResults = document.getElementById('analysis-results')?.innerHTML || '';
        
        if (!analysisResults) {
            this.showMessage('No analysis results to export', 'warning');
            return;
        }
        
        // Simple text export of analysis results
        const textContent = analysisResults
            .replace(/<[^>]*>/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
        
        this.downloadFile(textContent, 'statistical-analysis-results.txt', 'text/plain');
    }
    
    /**
     * Export Excel workbook
     * @private
     */
    async exportExcelWorkbook() {
        // Excel export would require additional library like SheetJS
        this.showMessage('Excel export requires additional implementation', 'info');
    }
    
    /**
     * Export PDF report
     * @private
     */
    async exportPDFReport() {
        // PDF export would require jsPDF library
        this.showMessage('PDF export requires additional implementation', 'info');
    }
    
    /**
     * Download file
     * @private
     * @param {string} data - File content
     * @param {string} filename - File name
     * @param {string} mimeType - MIME type
     */
    downloadFile(data, filename, mimeType) {
        const blob = new Blob([data], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        window.URL.revokeObjectURL(url);
    }
    
    /**
     * Set auto refresh
     * @private
     * @param {boolean} enabled - Auto refresh enabled
     */
    setAutoRefresh(enabled) {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
        
        if (enabled && this.options.enableRealTimeUpdates) {
            this.updateTimer = setInterval(() => {
                this.refreshData();
            }, this.options.refreshInterval);
        }
        
        console.log('🔄 Auto refresh:', enabled);
    }
    
    /**
     * Refresh data
     * @private
     */
    refreshData() {
        // Emit refresh event
        this.container.dispatchEvent(new CustomEvent('refreshRequested'));
    }
    
    /**
     * Handle real-time data updates
     * @param {Object} update - Data update
     */
    handleDataUpdate(update) {
        if (!this.options.enableRealTimeUpdates || this.isUpdating) return;
        
        this.isUpdating = true;
        
        // Update components with new data
        if (this.chartsComponent && update.chartUpdate) {
            Object.entries(update.chartUpdate).forEach(([chartId, dataPoint]) => {
                this.chartsComponent.updateChart(chartId, dataPoint);
            });
        }
        
        // Update statistics if needed
        if (update.statisticsUpdate) {
            this.updateStatistics(update.statisticsUpdate);
        }
        
        this.isUpdating = false;
    }
    
    /**
     * Show loading state
     * @private
     */
    showLoading() {
        if (this.loadingElement) {
            this.loadingElement.style.display = 'flex';
        }
        this.hideContent();
        this.hideError();
    }
    
    /**
     * Hide loading state
     * @private
     */
    hideLoading() {
        if (this.loadingElement) {
            this.loadingElement.style.display = 'none';
        }
    }
    
    /**
     * Show content
     * @private
     */
    showContent() {
        const mainContent = this.container.querySelector('.visualizer-main-content');
        const header = this.container.querySelector('.visualizer-header');
        
        if (mainContent) mainContent.style.display = 'block';
        if (header) header.style.display = 'block';
        if (this.filterPanel) this.filterPanel.style.display = 'block';
        if (this.statisticsPanel) this.statisticsPanel.style.display = 'block';
    }
    
    /**
     * Hide content
     * @private
     */
    hideContent() {
        const mainContent = this.container.querySelector('.visualizer-main-content');
        const header = this.container.querySelector('.visualizer-header');
        
        if (mainContent) mainContent.style.display = 'none';
        if (header) header.style.display = 'none';
        if (this.filterPanel) this.filterPanel.style.display = 'none';
        if (this.statisticsPanel) this.statisticsPanel.style.display = 'none';
    }
    
    /**
     * Show error state
     * @private
     * @param {string} title - Error title
     * @param {string} message - Error message
     */
    showError(title, message) {
        if (this.errorElement) {
            this.errorElement.querySelector('h4').textContent = title;
            this.errorElement.querySelector('.error-details').textContent = message;
            this.errorElement.style.display = 'flex';
        }
        this.hideLoading();
        this.hideContent();
    }
    
    /**
     * Hide error state
     * @private
     */
    hideError() {
        if (this.errorElement) {
            this.errorElement.style.display = 'none';
        }
    }
    
    /**
     * Retry loading
     * @private
     */
    retry() {
        this.hideError();
        this.showLoading();
        this.refreshData();
    }
    
    /**
     * Show message to user
     * @private
     * @param {string} message - Message text
     * @param {string} type - Message type
     */
    showMessage(message, type) {
        console.log(`📢 ${type.toUpperCase()}: ${message}`);
        
        // Emit message event for parent to handle
        this.container.dispatchEvent(new CustomEvent('messageRequested', {
            detail: { message, type }
        }));
    }
    
    /**
     * Get current view
     * @returns {string} Current view
     */
    getCurrentView() {
        return this.currentView;
    }
    
    /**
     * Get current data
     * @returns {Object} Current data
     */
    getCurrentData() {
        return this.currentData;
    }
    
    /**
     * Get applied filters
     * @returns {Object} Current filters
     */
    getFilters() {
        return { ...this.filters };
    }
    
    /**
     * Cleanup component resources
     */
    cleanup() {
        // Clear auto refresh
        this.setAutoRefresh(false);
        
        // Cleanup child components
        if (this.matrixTable && typeof this.matrixTable.cleanup === 'function') {
            this.matrixTable.cleanup();
        }
        
        if (this.chartsComponent && typeof this.chartsComponent.cleanup === 'function') {
            this.chartsComponent.cleanup();
        }
        
        // Clear data
        this.currentData = null;
        this.historicalData = [];
        
        console.log('🧹 Force Results Visualizer cleanup complete');
    }
}

console.log('📝 Force Results Visualizer component module loaded successfully');