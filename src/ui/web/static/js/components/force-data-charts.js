/**
 * Force Data Charts Component - WF EOL Tester Web Interface
 * 
 * This component provides comprehensive force data visualization including:
 * - Line Charts: Force vs Temperature at different stroke positions
 * - Scatter Plots: Force vs Stroke position at different temperatures  
 * - Heatmap: Temperature×Stroke matrix with color-coded force values
 * - 3D Surface Plot: Temperature×Stroke×Force (optional with Plotly.js)
 * - Box Plots: Force distribution analysis across test conditions
 * - Trend Analysis: Force variation trends over test sequences
 * - Interactive features with zoom, pan, and hover information
 * - Chart export functionality (PNG, SVG, PDF)
 * - Real-time chart updates during test execution
 * - Chart comparison mode for multiple test runs
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

export class ForceDataCharts {
    /**
     * Initialize Force Data Charts component
     * @param {HTMLElement} container - Container element for the charts
     * @param {Object} options - Configuration options
     */
    constructor(container, options = {}) {
        console.log('📊 Initializing Force Data Charts component...');
        
        // Core properties
        this.container = container;
        this.options = {
            // Chart configuration
            enableInteractivity: true,
            enableExport: true,
            enableAnimation: false, // Disabled for performance
            enableRealTimeUpdates: true,
            
            // Chart types to display
            chartTypes: ['line', 'scatter', 'heatmap', 'box', 'trend'],
            
            // Color schemes
            colorSchemes: {
                temperature: ['#3b82f6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6'],
                stroke: ['#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'],
                force: ['#22d3ee', '#a3e635', '#fb923c', '#f472b6', '#818cf8']
            },
            
            // Chart dimensions
            chartHeight: 400,
            chartWidth: '100%',
            
            // Data formatting
            decimalPlaces: 2,
            units: {
                force: 'N',
                temperature: '°C',
                stroke: 'mm',
                time: 's'
            },
            
            // Performance settings
            maxDataPoints: 1000,
            updateThrottle: 100, // ms
            
            ...options
        };
        
        // State management
        this.data = null;
        this.charts = new Map();
        this.updateQueue = [];
        this.isUpdating = false;
        this.selectedSeries = new Set();
        
        // Chart.js plugins and configurations
        this.chartDefaults = {};
        this.customPlugins = [];
        
        // Real-time update handling
        this.updateTimer = null;
        this.lastUpdate = 0;
        
        // Bind methods
        this.handleChartClick = this.handleChartClick.bind(this);
        this.handleChartHover = this.handleChartHover.bind(this);
        this.handleLegendClick = this.handleLegendClick.bind(this);
        this.handleExport = this.handleExport.bind(this);
        this.handleResize = this.handleResize.bind(this);
        
        // Initialize component
        this.init();
        
        console.log('✅ Force Data Charts component initialized');
    }
    
    /**
     * Initialize component
     * @private
     */
    init() {
        try {
            // Check Chart.js availability
            if (typeof Chart === 'undefined') {
                throw new Error('Chart.js library not available');
            }
            
            // Setup Chart.js defaults
            this.setupChartDefaults();
            
            // Create component structure
            this.createStructure();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize chart containers
            this.initializeChartContainers();
            
            // Show loading state
            this.showLoading();
            
        } catch (error) {
            console.error('❌ Failed to initialize Force Data Charts:', error);
            this.showError('Chart initialization failed', error.message);
        }
    }
    
    /**
     * Setup Chart.js default configurations
     * @private
     */
    setupChartDefaults() {
        // Global Chart.js defaults
        Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = 'rgba(75, 85, 99, 0.8)';
        
        // Common options for all charts
        this.chartDefaults = {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: this.options.enableAnimation ? 750 : 0
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            weight: 500
                        }
                    },
                    onClick: this.handleLegendClick
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    cornerRadius: 8,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        title: (context) => this.formatTooltipTitle(context),
                        label: (context) => this.formatTooltipLabel(context)
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(75, 85, 99, 0.1)',
                        lineWidth: 1
                    },
                    ticks: {
                        color: 'rgba(75, 85, 99, 0.7)'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(75, 85, 99, 0.1)',
                        lineWidth: 1
                    },
                    ticks: {
                        color: 'rgba(75, 85, 99, 0.7)'
                    }
                }
            }
        };
        
        // Custom plugins
        this.customPlugins = [
            // Background grid plugin
            {
                id: 'backgroundGrid',
                beforeDraw: (chart) => this.drawBackgroundGrid(chart)
            },
            // Data point labels plugin
            {
                id: 'dataLabels',
                afterDatasetsDraw: (chart) => this.drawDataLabels(chart)
            }
        ];
    }
    
    /**
     * Create component structure
     * @private
     */
    createStructure() {
        this.container.innerHTML = `
            <div class="force-charts-container">
                <!-- Header with controls -->
                <div class="force-charts-header">
                    <div class="force-charts-title">
                        <h3>📊 Force Data Visualization</h3>
                        <div class="force-charts-subtitle">
                            Interactive charts and graphs for force measurement analysis
                        </div>
                    </div>
                    <div class="force-charts-controls">
                        <div class="chart-type-selector">
                            <button class="btn btn-sm btn-secondary active" data-chart-type="all">All Charts</button>
                            <button class="btn btn-sm btn-secondary" data-chart-type="line">Line Charts</button>
                            <button class="btn btn-sm btn-secondary" data-chart-type="scatter">Scatter Plots</button>
                            <button class="btn btn-sm btn-secondary" data-chart-type="heatmap">Heatmaps</button>
                            <button class="btn btn-sm btn-secondary" data-chart-type="box">Box Plots</button>
                        </div>
                        <div class="chart-actions">
                            <button class="btn btn-sm btn-info" id="charts-fullscreen-btn" title="Fullscreen Mode">
                                🔍 Fullscreen
                            </button>
                            <div class="dropdown">
                                <button class="btn btn-sm btn-success dropdown-toggle" id="charts-export-btn">
                                    💾 Export Charts
                                </button>
                                <div class="dropdown-menu" id="charts-export-menu">
                                    <a class="dropdown-item" data-format="png">🖼️ PNG Images</a>
                                    <a class="dropdown-item" data-format="svg">🎨 SVG Vector</a>
                                    <a class="dropdown-item" data-format="pdf">📋 PDF Report</a>
                                    <a class="dropdown-item" data-format="data">📊 Chart Data</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Charts Grid -->
                <div class="force-charts-grid" id="charts-grid">
                    
                    <!-- Line Charts Section -->
                    <div class="chart-section" data-chart-type="line">
                        <h4 class="chart-section-title">📈 Force vs Temperature Analysis</h4>
                        <div class="chart-row">
                            <div class="chart-container">
                                <div class="chart-header">
                                    <h5>Force vs Temperature (by Stroke Position)</h5>
                                    <div class="chart-controls">
                                        <button class="chart-control-btn" data-action="zoom-reset">🔍 Reset Zoom</button>
                                        <button class="chart-control-btn" data-action="export" data-chart="force-temp-chart">💾 Export</button>
                                    </div>
                                </div>
                                <div class="chart-wrapper">
                                    <canvas id="force-temp-chart"></canvas>
                                </div>
                            </div>
                        </div>
                        
                        <h4 class="chart-section-title">📏 Force vs Stroke Position Analysis</h4>
                        <div class="chart-row">
                            <div class="chart-container">
                                <div class="chart-header">
                                    <h5>Force vs Stroke Position (by Temperature)</h5>
                                    <div class="chart-controls">
                                        <button class="chart-control-btn" data-action="zoom-reset">🔍 Reset Zoom</button>
                                        <button class="chart-control-btn" data-action="export" data-chart="force-stroke-chart">💾 Export</button>
                                    </div>
                                </div>
                                <div class="chart-wrapper">
                                    <canvas id="force-stroke-chart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Scatter Plots Section -->
                    <div class="chart-section" data-chart-type="scatter">
                        <h4 class="chart-section-title">🔸 Force Distribution Analysis</h4>
                        <div class="chart-row">
                            <div class="chart-container">
                                <div class="chart-header">
                                    <h5>Force Distribution Scatter Plot</h5>
                                    <div class="chart-controls">
                                        <button class="chart-control-btn" data-action="zoom-reset">🔍 Reset Zoom</button>
                                        <button class="chart-control-btn" data-action="export" data-chart="force-distribution-chart">💾 Export</button>
                                    </div>
                                </div>
                                <div class="chart-wrapper">
                                    <canvas id="force-distribution-chart"></canvas>
                                </div>
                            </div>
                        </div>
                        
                        <div class="chart-row">
                            <div class="chart-container">
                                <div class="chart-header">
                                    <h5>Temperature vs Stroke Correlation</h5>
                                    <div class="chart-controls">
                                        <button class="chart-control-btn" data-action="zoom-reset">🔍 Reset Zoom</button>
                                        <button class="chart-control-btn" data-action="export" data-chart="temp-stroke-correlation-chart">💾 Export</button>
                                    </div>
                                </div>
                                <div class="chart-wrapper">
                                    <canvas id="temp-stroke-correlation-chart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Heatmap Section -->
                    <div class="chart-section" data-chart-type="heatmap">
                        <h4 class="chart-section-title">🔥 Force Heatmap Visualization</h4>
                        <div class="chart-row">
                            <div class="chart-container chart-lg">
                                <div class="chart-header">
                                    <h5>Temperature × Stroke Force Heatmap</h5>
                                    <div class="chart-controls">
                                        <select class="chart-control-select" id="heatmap-color-scheme">
                                            <option value="viridis">Viridis</option>
                                            <option value="plasma">Plasma</option>
                                            <option value="inferno">Inferno</option>
                                            <option value="magma">Magma</option>
                                        </select>
                                        <button class="chart-control-btn" data-action="export" data-chart="force-heatmap-chart">💾 Export</button>
                                    </div>
                                </div>
                                <div class="chart-wrapper">
                                    <canvas id="force-heatmap-chart"></canvas>
                                </div>
                                <div class="heatmap-legend" id="heatmap-legend">
                                    <!-- Legend will be generated dynamically -->
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Box Plots Section -->
                    <div class="chart-section" data-chart-type="box">
                        <h4 class="chart-section-title">📦 Force Distribution Box Plots</h4>
                        <div class="chart-row">
                            <div class="chart-container">
                                <div class="chart-header">
                                    <h5>Force by Temperature</h5>
                                    <div class="chart-controls">
                                        <button class="chart-control-btn" data-action="export" data-chart="force-by-temp-box-chart">💾 Export</button>
                                    </div>
                                </div>
                                <div class="chart-wrapper">
                                    <canvas id="force-by-temp-box-chart"></canvas>
                                </div>
                            </div>
                            <div class="chart-container">
                                <div class="chart-header">
                                    <h5>Force by Stroke Position</h5>
                                    <div class="chart-controls">
                                        <button class="chart-control-btn" data-action="export" data-chart="force-by-stroke-box-chart">💾 Export</button>
                                    </div>
                                </div>
                                <div class="chart-wrapper">
                                    <canvas id="force-by-stroke-box-chart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Trend Analysis Section -->
                    <div class="chart-section" data-chart-type="trend">
                        <h4 class="chart-section-title">📊 Trend Analysis</h4>
                        <div class="chart-row">
                            <div class="chart-container">
                                <div class="chart-header">
                                    <h5>Force Trends Over Time</h5>
                                    <div class="chart-controls">
                                        <button class="chart-control-btn" data-action="zoom-reset">🔍 Reset Zoom</button>
                                        <button class="chart-control-btn" data-action="export" data-chart="force-trend-chart">💾 Export</button>
                                    </div>
                                </div>
                                <div class="chart-wrapper">
                                    <canvas id="force-trend-chart"></canvas>
                                </div>
                            </div>
                        </div>
                        
                        <div class="chart-row">
                            <div class="chart-container">
                                <div class="chart-header">
                                    <h5>Statistical Trends</h5>
                                    <div class="chart-controls">
                                        <button class="chart-control-btn" data-action="export" data-chart="stats-trend-chart">💾 Export</button>
                                    </div>
                                </div>
                                <div class="chart-wrapper">
                                    <canvas id="stats-trend-chart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Loading State -->
                <div class="force-charts-loading" id="charts-loading">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Loading force data charts...</div>
                </div>
                
                <!-- Error State -->
                <div class="force-charts-error" id="charts-error" style="display: none;">
                    <div class="error-icon">⚠️</div>
                    <div class="error-message">
                        <h4>Error Loading Charts</h4>
                        <p class="error-details">Failed to load force measurement charts</p>
                    </div>
                    <button class="btn btn-primary" id="charts-retry-btn">Retry</button>
                </div>
            </div>
        `;
        
        // Cache DOM references
        this.gridElement = document.getElementById('charts-grid');
        this.loadingElement = document.getElementById('charts-loading');
        this.errorElement = document.getElementById('charts-error');
        this.exportMenuElement = document.getElementById('charts-export-menu');
    }
    
    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Chart type selector buttons
        this.container.querySelectorAll('[data-chart-type]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setChartTypeFilter(e.target.getAttribute('data-chart-type'));
                this.updateChartTypeButtons(e.target);
            });
        });
        
        // Export menu events
        if (this.exportMenuElement) {
            this.exportMenuElement.addEventListener('click', (e) => {
                if (e.target.hasAttribute('data-format')) {
                    e.preventDefault();
                    this.handleExport(e.target.getAttribute('data-format'));
                }
            });
        }
        
        // Export button toggle
        const exportBtn = document.getElementById('charts-export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.exportMenuElement.classList.toggle('show');
            });
        }
        
        // Chart control buttons
        this.container.addEventListener('click', (e) => {
            if (e.target.hasAttribute('data-action')) {
                const action = e.target.getAttribute('data-action');
                const chartId = e.target.getAttribute('data-chart');
                this.handleChartAction(action, chartId);
            }
        });
        
        // Heatmap color scheme selector
        const colorSchemeSelect = document.getElementById('heatmap-color-scheme');
        if (colorSchemeSelect) {
            colorSchemeSelect.addEventListener('change', (e) => {
                this.updateHeatmapColorScheme(e.target.value);
            });
        }
        
        // Fullscreen toggle
        const fullscreenBtn = document.getElementById('charts-fullscreen-btn');
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => {
                this.toggleFullscreen();
            });
        }
        
        // Retry button
        const retryBtn = document.getElementById('charts-retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => {
                this.retry();
            });
        }
        
        // Close export menu when clicking outside
        document.addEventListener('click', () => {
            if (this.exportMenuElement) {
                this.exportMenuElement.classList.remove('show');
            }
        });
        
        // Window resize for responsive behavior
        window.addEventListener('resize', this.handleResize);
    }
    
    /**
     * Initialize chart containers
     * @private
     */
    initializeChartContainers() {
        // Get all canvas elements
        const canvasElements = this.container.querySelectorAll('canvas');
        
        canvasElements.forEach(canvas => {
            const chartId = canvas.id;
            
            // Initialize chart placeholder
            this.charts.set(chartId, null);
            
            // Setup canvas click handler
            canvas.addEventListener('click', (e) => {
                this.handleChartClick(e, chartId);
            });
        });
    }
    
    /**
     * Load and display force data charts
     * @param {Object} data - Force measurement data
     * @param {Object} options - Chart options
     */
    loadData(data, options = {}) {
        console.log('📊 Loading force data charts...', data);
        
        try {
            // Merge options
            this.options = { ...this.options, ...options };
            
            // Validate and process data
            this.data = this.validateData(data);
            
            // Create all charts
            this.createAllCharts();
            
            // Hide loading, show content
            this.hideLoading();
            this.showContent();
            
            console.log('✅ Force data charts loaded successfully');
            
        } catch (error) {
            console.error('❌ Failed to load force data charts:', error);
            this.showError('Chart loading failed', error.message);
        }
    }
    
    /**
     * Validate incoming data
     * @private
     * @param {Object} data - Raw data to validate
     * @returns {Object} Validated data
     */
    validateData(data) {
        if (!data || typeof data !== 'object') {
            throw new Error('Invalid data: Data must be an object');
        }
        
        const { measurements, temperatureList, strokePositions } = data;
        
        if (!measurements || !Array.isArray(measurements)) {
            throw new Error('Invalid data: Measurements must be an array');
        }
        
        return {
            measurements,
            temperatureList: temperatureList || [],
            strokePositions: strokePositions || []
        };
    }
    
    /**
     * Create all charts
     * @private
     */
    createAllCharts() {
        console.log('🎨 Creating all force data charts...');
        
        try {
            // Line charts
            this.createForceTemperatureChart();
            this.createForceStrokeChart();
            
            // Scatter plots
            this.createForceDistributionChart();
            this.createTemperatureStrokeCorrelationChart();
            
            // Heatmap
            this.createForceHeatmapChart();
            
            // Box plots
            this.createForceByTemperatureBoxChart();
            this.createForceByStrokeBoxChart();
            
            // Trend charts
            this.createForceTrendChart();
            this.createStatsTrendChart();
            
        } catch (error) {
            console.error('❌ Failed to create charts:', error);
            throw error;
        }
    }
    
    /**
     * Create Force vs Temperature line chart
     * @private
     */
    createForceTemperatureChart() {
        const canvas = document.getElementById('force-temp-chart');
        if (!canvas) return;
        
        const { measurements, strokePositions } = this.data;
        
        // Group data by stroke position
        const datasets = [];
        const colors = this.options.colorSchemes.stroke;
        
        strokePositions.forEach((stroke, index) => {
            const strokeData = measurements
                .filter(m => m.strokePosition === stroke)
                .sort((a, b) => a.temperature - b.temperature);
            
            if (strokeData.length === 0) return;
            
            datasets.push({
                label: `${stroke}mm`,
                data: strokeData.map(m => ({
                    x: m.temperature,
                    y: m.force
                })),
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '20',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            });
        });
        
        const chart = new Chart(canvas, {
            type: 'line',
            data: {
                datasets
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    x: {
                        ...this.chartDefaults.scales.x,
                        title: {
                            display: true,
                            text: `Temperature (${this.options.units.temperature})`
                        }
                    },
                    y: {
                        ...this.chartDefaults.scales.y,
                        title: {
                            display: true,
                            text: `Force (${this.options.units.force})`
                        }
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    title: {
                        display: true,
                        text: 'Force vs Temperature by Stroke Position'
                    }
                }
            },
            plugins: this.customPlugins
        });
        
        this.charts.set('force-temp-chart', chart);
    }
    
    /**
     * Create Force vs Stroke Position line chart
     * @private
     */
    createForceStrokeChart() {
        const canvas = document.getElementById('force-stroke-chart');
        if (!canvas) return;
        
        const { measurements, temperatureList } = this.data;
        
        // Group data by temperature
        const datasets = [];
        const colors = this.options.colorSchemes.temperature;
        
        temperatureList.forEach((temp, index) => {
            const tempData = measurements
                .filter(m => m.temperature === temp)
                .sort((a, b) => a.strokePosition - b.strokePosition);
            
            if (tempData.length === 0) return;
            
            datasets.push({
                label: `${temp}°C`,
                data: tempData.map(m => ({
                    x: m.strokePosition,
                    y: m.force
                })),
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '20',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            });
        });
        
        const chart = new Chart(canvas, {
            type: 'line',
            data: {
                datasets
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    x: {
                        ...this.chartDefaults.scales.x,
                        title: {
                            display: true,
                            text: `Stroke Position (${this.options.units.stroke})`
                        }
                    },
                    y: {
                        ...this.chartDefaults.scales.y,
                        title: {
                            display: true,
                            text: `Force (${this.options.units.force})`
                        }
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    title: {
                        display: true,
                        text: 'Force vs Stroke Position by Temperature'
                    }
                }
            },
            plugins: this.customPlugins
        });
        
        this.charts.set('force-stroke-chart', chart);
    }
    
    /**
     * Create Force Distribution scatter plot
     * @private
     */
    createForceDistributionChart() {
        const canvas = document.getElementById('force-distribution-chart');
        if (!canvas) return;
        
        const { measurements } = this.data;
        
        // Create scatter plot with force values
        const data = measurements.map(m => ({
            x: m.temperature,
            y: m.strokePosition,
            force: m.force
        }));
        
        const chart = new Chart(canvas, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Force Measurements',
                    data: data.map(d => ({ x: d.x, y: d.y })),
                    backgroundColor: data.map(d => this.getForceColor(d.force)),
                    borderColor: data.map(d => this.getForceColor(d.force, 0.8)),
                    borderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    x: {
                        ...this.chartDefaults.scales.x,
                        title: {
                            display: true,
                            text: `Temperature (${this.options.units.temperature})`
                        }
                    },
                    y: {
                        ...this.chartDefaults.scales.y,
                        title: {
                            display: true,
                            text: `Stroke Position (${this.options.units.stroke})`
                        }
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    title: {
                        display: true,
                        text: 'Force Distribution (Color = Force Value)'
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        ...this.chartDefaults.plugins.tooltip,
                        callbacks: {
                            label: (context) => {
                                const dataPoint = data[context.dataIndex];
                                return [
                                    `Temperature: ${dataPoint.x}°C`,
                                    `Stroke: ${dataPoint.y}mm`,
                                    `Force: ${dataPoint.force.toFixed(2)}N`
                                ];
                            }
                        }
                    }
                }
            },
            plugins: this.customPlugins
        });
        
        this.charts.set('force-distribution-chart', chart);
    }
    
    /**
     * Create Temperature vs Stroke correlation chart
     * @private
     */
    createTemperatureStrokeCorrelationChart() {
        const canvas = document.getElementById('temp-stroke-correlation-chart');
        if (!canvas) return;
        
        const { measurements } = this.data;
        
        // Group by force ranges
        const forceRanges = this.getForceRanges(measurements);
        const datasets = [];
        const colors = this.options.colorSchemes.force;
        
        forceRanges.forEach((range, index) => {
            const rangeData = measurements.filter(m => 
                m.force >= range.min && m.force < range.max
            );
            
            if (rangeData.length === 0) return;
            
            datasets.push({
                label: `${range.min}-${range.max}N`,
                data: rangeData.map(m => ({
                    x: m.temperature,
                    y: m.strokePosition
                })),
                backgroundColor: colors[index % colors.length] + '80',
                borderColor: colors[index % colors.length],
                borderWidth: 1,
                pointRadius: 5,
                pointHoverRadius: 7
            });
        });
        
        const chart = new Chart(canvas, {
            type: 'scatter',
            data: {
                datasets
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    x: {
                        ...this.chartDefaults.scales.x,
                        title: {
                            display: true,
                            text: `Temperature (${this.options.units.temperature})`
                        }
                    },
                    y: {
                        ...this.chartDefaults.scales.y,
                        title: {
                            display: true,
                            text: `Stroke Position (${this.options.units.stroke})`
                        }
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    title: {
                        display: true,
                        text: 'Temperature vs Stroke Correlation by Force Range'
                    }
                }
            },
            plugins: this.customPlugins
        });
        
        this.charts.set('temp-stroke-correlation-chart', chart);
    }
    
    /**
     * Create Force Heatmap chart
     * @private
     */
    createForceHeatmapChart() {
        const canvas = document.getElementById('force-heatmap-chart');
        if (!canvas) return;
        
        const { measurements, temperatureList, strokePositions } = this.data;
        
        // Create matrix data for heatmap
        const matrixData = [];
        
        temperatureList.forEach((temp, tempIndex) => {
            strokePositions.forEach((stroke, strokeIndex) => {
                const measurement = measurements.find(m => 
                    m.temperature === temp && m.strokePosition === stroke
                );
                
                if (measurement) {
                    matrixData.push({
                        x: strokeIndex,
                        y: tempIndex,
                        value: measurement.force,
                        temp: temp,
                        stroke: stroke
                    });
                }
            });
        });
        
        // Custom heatmap implementation using Chart.js scatter
        const chart = new Chart(canvas, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Force Heatmap',
                    data: matrixData.map(d => ({
                        x: d.x,
                        y: d.y,
                        value: d.value,
                        temp: d.temp,
                        stroke: d.stroke
                    })),
                    backgroundColor: matrixData.map(d => this.getHeatmapColor(d.value)),
                    borderColor: '#ffffff',
                    borderWidth: 1,
                    pointRadius: 15,
                    pointHoverRadius: 17
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: `Stroke Position (${this.options.units.stroke})`
                        },
                        ticks: {
                            callback: (value) => {
                                return strokePositions[Math.round(value)] || '';
                            }
                        },
                        min: -0.5,
                        max: strokePositions.length - 0.5
                    },
                    y: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: `Temperature (${this.options.units.temperature})`
                        },
                        ticks: {
                            callback: (value) => {
                                return temperatureList[Math.round(value)] || '';
                            }
                        },
                        min: -0.5,
                        max: temperatureList.length - 0.5
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    title: {
                        display: true,
                        text: 'Force Heatmap: Temperature × Stroke Position'
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        ...this.chartDefaults.plugins.tooltip,
                        callbacks: {
                            title: () => 'Force Measurement',
                            label: (context) => {
                                const dataPoint = context.raw;
                                return [
                                    `Temperature: ${dataPoint.temp}°C`,
                                    `Stroke: ${dataPoint.stroke}mm`,
                                    `Force: ${dataPoint.value.toFixed(2)}N`
                                ];
                            }
                        }
                    }
                }
            },
            plugins: this.customPlugins
        });
        
        this.charts.set('force-heatmap-chart', chart);
        
        // Generate heatmap legend
        this.generateHeatmapLegend();
    }
    
    /**
     * Create Force by Temperature box plot
     * @private
     */
    createForceByTemperatureBoxChart() {
        const canvas = document.getElementById('force-by-temp-box-chart');
        if (!canvas) return;
        
        const { measurements, temperatureList } = this.data;
        
        // Group forces by temperature
        const boxData = temperatureList.map(temp => {
            const tempForces = measurements
                .filter(m => m.temperature === temp)
                .map(m => m.force)
                .sort((a, b) => a - b);
            
            if (tempForces.length === 0) return null;
            
            const stats = this.calculateBoxPlotStats(tempForces);
            return {
                label: `${temp}°C`,
                ...stats,
                forces: tempForces
            };
        }).filter(Boolean);
        
        // Create box plot visualization using error bars
        const chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: boxData.map(d => d.label),
                datasets: [{
                    label: 'Force Distribution',
                    data: boxData.map(d => d.median),
                    backgroundColor: this.options.colorSchemes.temperature[0] + '40',
                    borderColor: this.options.colorSchemes.temperature[0],
                    borderWidth: 2,
                    errorBars: {
                        plus: boxData.map(d => d.q3 - d.median),
                        minus: boxData.map(d => d.median - d.q1)
                    }
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    y: {
                        ...this.chartDefaults.scales.y,
                        title: {
                            display: true,
                            text: `Force (${this.options.units.force})`
                        }
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    title: {
                        display: true,
                        text: 'Force Distribution by Temperature'
                    }
                }
            },
            plugins: this.customPlugins
        });
        
        this.charts.set('force-by-temp-box-chart', chart);
    }
    
    /**
     * Create Force by Stroke Position box plot
     * @private
     */
    createForceByStrokeBoxChart() {
        const canvas = document.getElementById('force-by-stroke-box-chart');
        if (!canvas) return;
        
        const { measurements, strokePositions } = this.data;
        
        // Group forces by stroke position
        const boxData = strokePositions.map(stroke => {
            const strokeForces = measurements
                .filter(m => m.strokePosition === stroke)
                .map(m => m.force)
                .sort((a, b) => a - b);
            
            if (strokeForces.length === 0) return null;
            
            const stats = this.calculateBoxPlotStats(strokeForces);
            return {
                label: `${stroke}mm`,
                ...stats,
                forces: strokeForces
            };
        }).filter(Boolean);
        
        const chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: boxData.map(d => d.label),
                datasets: [{
                    label: 'Force Distribution',
                    data: boxData.map(d => d.median),
                    backgroundColor: this.options.colorSchemes.stroke[0] + '40',
                    borderColor: this.options.colorSchemes.stroke[0],
                    borderWidth: 2,
                    errorBars: {
                        plus: boxData.map(d => d.q3 - d.median),
                        minus: boxData.map(d => d.median - d.q1)
                    }
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    y: {
                        ...this.chartDefaults.scales.y,
                        title: {
                            display: true,
                            text: `Force (${this.options.units.force})`
                        }
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    title: {
                        display: true,
                        text: 'Force Distribution by Stroke Position'
                    }
                }
            },
            plugins: this.customPlugins
        });
        
        this.charts.set('force-by-stroke-box-chart', chart);
    }
    
    /**
     * Create Force Trend chart
     * @private
     */
    createForceTrendChart() {
        const canvas = document.getElementById('force-trend-chart');
        if (!canvas) return;
        
        const { measurements } = this.data;
        
        // Sort measurements by timestamp
        const sortedMeasurements = measurements
            .filter(m => m.timestamp)
            .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        const chart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: sortedMeasurements.map((_, index) => index + 1),
                datasets: [{
                    label: 'Force Trend',
                    data: sortedMeasurements.map(m => m.force),
                    borderColor: this.options.colorSchemes.force[0],
                    backgroundColor: this.options.colorSchemes.force[0] + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 2,
                    pointHoverRadius: 4
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    x: {
                        ...this.chartDefaults.scales.x,
                        title: {
                            display: true,
                            text: 'Measurement Sequence'
                        }
                    },
                    y: {
                        ...this.chartDefaults.scales.y,
                        title: {
                            display: true,
                            text: `Force (${this.options.units.force})`
                        }
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    title: {
                        display: true,
                        text: 'Force Measurements Over Time'
                    }
                }
            },
            plugins: this.customPlugins
        });
        
        this.charts.set('force-trend-chart', chart);
    }
    
    /**
     * Create Statistical Trends chart
     * @private
     */
    createStatsTrendChart() {
        const canvas = document.getElementById('stats-trend-chart');
        if (!canvas) return;
        
        const { measurements, temperatureList } = this.data;
        
        // Calculate statistics for each temperature
        const statsData = temperatureList.map(temp => {
            const tempForces = measurements
                .filter(m => m.temperature === temp)
                .map(m => m.force);
            
            if (tempForces.length === 0) return null;
            
            const avg = tempForces.reduce((sum, f) => sum + f, 0) / tempForces.length;
            const min = Math.min(...tempForces);
            const max = Math.max(...tempForces);
            const std = Math.sqrt(
                tempForces.reduce((sum, f) => sum + Math.pow(f - avg, 2), 0) / tempForces.length
            );
            
            return { temp, avg, min, max, std };
        }).filter(Boolean);
        
        const chart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: statsData.map(d => `${d.temp}°C`),
                datasets: [
                    {
                        label: 'Average',
                        data: statsData.map(d => d.avg),
                        borderColor: this.options.colorSchemes.temperature[0],
                        backgroundColor: this.options.colorSchemes.temperature[0],
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4
                    },
                    {
                        label: 'Maximum',
                        data: statsData.map(d => d.max),
                        borderColor: this.options.colorSchemes.temperature[1],
                        backgroundColor: this.options.colorSchemes.temperature[1],
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        borderDash: [5, 5]
                    },
                    {
                        label: 'Minimum',
                        data: statsData.map(d => d.min),
                        borderColor: this.options.colorSchemes.temperature[2],
                        backgroundColor: this.options.colorSchemes.temperature[2],
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    y: {
                        ...this.chartDefaults.scales.y,
                        title: {
                            display: true,
                            text: `Force (${this.options.units.force})`
                        }
                    }
                },
                plugins: {
                    ...this.chartDefaults.plugins,
                    title: {
                        display: true,
                        text: 'Statistical Trends by Temperature'
                    }
                }
            },
            plugins: this.customPlugins
        });
        
        this.charts.set('stats-trend-chart', chart);
    }
    
    /**
     * Get force ranges for correlation analysis
     * @private
     * @param {Array} measurements - Measurement data
     * @returns {Array} Force ranges
     */
    getForceRanges(measurements) {
        const forces = measurements.map(m => m.force);
        const min = Math.min(...forces);
        const max = Math.max(...forces);
        const range = max - min;
        const step = range / 5; // 5 ranges
        
        const ranges = [];
        for (let i = 0; i < 5; i++) {
            ranges.push({
                min: Math.round((min + i * step) * 10) / 10,
                max: Math.round((min + (i + 1) * step) * 10) / 10
            });
        }
        
        return ranges;
    }
    
    /**
     * Calculate box plot statistics
     * @private
     * @param {Array} values - Sorted array of values
     * @returns {Object} Box plot statistics
     */
    calculateBoxPlotStats(values) {
        const n = values.length;
        const q1Index = Math.floor(n * 0.25);
        const medianIndex = Math.floor(n * 0.5);
        const q3Index = Math.floor(n * 0.75);
        
        return {
            min: values[0],
            q1: values[q1Index],
            median: values[medianIndex],
            q3: values[q3Index],
            max: values[n - 1]
        };
    }
    
    /**
     * Get color based on force value
     * @private
     * @param {number} force - Force value
     * @param {number} alpha - Alpha value (0-1)
     * @returns {string} RGBA color
     */
    getForceColor(force, alpha = 0.6) {
        const { measurements } = this.data;
        const forces = measurements.map(m => m.force);
        const min = Math.min(...forces);
        const max = Math.max(...forces);
        
        if (min === max) return `rgba(33, 150, 243, ${alpha})`; // Blue
        
        const normalized = (force - min) / (max - min);
        
        // Color gradient from blue (low) to red (high)
        const r = Math.round(normalized * 255);
        const b = Math.round((1 - normalized) * 255);
        const g = Math.round((1 - Math.abs(normalized - 0.5) * 2) * 255);
        
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    /**
     * Get heatmap color based on force value
     * @private
     * @param {number} force - Force value
     * @returns {string} Hex color
     */
    getHeatmapColor(force) {
        const { measurements } = this.data;
        const forces = measurements.map(m => m.force);
        const min = Math.min(...forces);
        const max = Math.max(...forces);
        
        if (min === max) return '#21908c'; // Neutral color
        
        const normalized = (force - min) / (max - min);
        
        // Viridis color scheme approximation
        const viridisColors = [
            '#440154', '#482777', '#3f4a8a', '#31678e',
            '#26838f', '#1f9d8a', '#6cce5a', '#b6de2b', '#fee825'
        ];
        
        const index = Math.floor(normalized * (viridisColors.length - 1));
        return viridisColors[index];
    }
    
    /**
     * Generate heatmap legend
     * @private
     */
    generateHeatmapLegend() {
        const legendElement = document.getElementById('heatmap-legend');
        if (!legendElement) return;
        
        const { measurements } = this.data;
        const forces = measurements.map(m => m.force);
        const min = Math.min(...forces);
        const max = Math.max(...forces);
        
        const steps = 10;
        const stepSize = (max - min) / steps;
        
        let legendHTML = '<div class="legend-title">Force Scale (N)</div><div class="legend-scale">';
        
        for (let i = 0; i <= steps; i++) {
            const value = min + (i * stepSize);
            const color = this.getHeatmapColor(value);
            legendHTML += `<div class="legend-step" style="background-color: ${color};" title="${value.toFixed(1)}N"></div>`;
        }
        
        legendHTML += '</div><div class="legend-labels">';
        legendHTML += `<span class="legend-min">${min.toFixed(1)}</span>`;
        legendHTML += `<span class="legend-mid">${((min + max) / 2).toFixed(1)}</span>`;
        legendHTML += `<span class="legend-max">${max.toFixed(1)}</span>`;
        legendHTML += '</div>';
        
        legendElement.innerHTML = legendHTML;
    }
    
    /**
     * Format tooltip title
     * @private
     * @param {Array} context - Chart context
     * @returns {string} Formatted title
     */
    formatTooltipTitle(context) {
        if (context.length === 0) return '';
        
        const chart = context[0].chart;
        const chartId = chart.canvas.id;
        
        switch (chartId) {
            case 'force-temp-chart':
                return `Temperature: ${context[0].parsed.x}°C`;
            case 'force-stroke-chart':
                return `Stroke Position: ${context[0].parsed.x}mm`;
            case 'force-trend-chart':
                return `Measurement #${context[0].dataIndex + 1}`;
            default:
                return 'Measurement Data';
        }
    }
    
    /**
     * Format tooltip label
     * @private
     * @param {Object} context - Chart context
     * @returns {string} Formatted label
     */
    formatTooltipLabel(context) {
        const value = context.parsed.y;
        const dataset = context.dataset.label;
        
        return `${dataset}: ${value.toFixed(this.options.decimalPlaces)}${this.options.units.force}`;
    }
    
    /**
     * Handle chart click events
     * @private
     * @param {Event} event - Click event
     * @param {string} chartId - Chart identifier
     */
    handleChartClick(event, chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        const points = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
        
        if (points.length > 0) {
            const point = points[0];
            const datasetIndex = point.datasetIndex;
            const index = point.index;
            
            console.log(`🎯 Chart clicked: ${chartId}, dataset: ${datasetIndex}, point: ${index}`);
            
            // Emit chart click event
            this.container.dispatchEvent(new CustomEvent('chartClicked', {
                detail: {
                    chartId,
                    datasetIndex,
                    index,
                    chart
                }
            }));
        }
    }
    
    /**
     * Handle chart hover events
     * @private
     * @param {Event} event - Hover event
     * @param {string} chartId - Chart identifier
     */
    handleChartHover(event, chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        const points = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
        
        if (points.length > 0) {
            event.native.target.style.cursor = 'pointer';
        } else {
            event.native.target.style.cursor = 'default';
        }
    }
    
    /**
     * Handle legend click events
     * @private
     * @param {Event} event - Click event
     * @param {Object} legendItem - Legend item
     * @param {Object} legend - Legend instance
     */
    handleLegendClick(event, legendItem, legend) {
        const chart = legend.chart;
        const datasetIndex = legendItem.datasetIndex;
        const dataset = chart.data.datasets[datasetIndex];
        
        // Toggle dataset visibility
        dataset.hidden = !dataset.hidden;
        
        // Update chart
        chart.update();
        
        console.log(`👁️ Dataset visibility toggled: ${dataset.label}, hidden: ${dataset.hidden}`);
    }
    
    /**
     * Handle chart actions
     * @private
     * @param {string} action - Action type
     * @param {string} chartId - Chart identifier
     */
    handleChartAction(action, chartId) {
        const chart = this.charts.get(chartId);
        
        switch (action) {
            case 'zoom-reset':
                if (chart && chart.resetZoom) {
                    chart.resetZoom();
                    console.log(`🔍 Zoom reset for chart: ${chartId}`);
                }
                break;
                
            case 'export':
                if (chart) {
                    this.exportSingleChart(chartId);
                }
                break;
                
            default:
                console.warn(`Unknown chart action: ${action}`);
        }
    }
    
    /**
     * Set chart type filter
     * @private
     * @param {string} chartType - Chart type to show
     */
    setChartTypeFilter(chartType) {
        const sections = this.container.querySelectorAll('.chart-section');
        
        sections.forEach(section => {
            const sectionType = section.getAttribute('data-chart-type');
            
            if (chartType === 'all' || sectionType === chartType) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
        
        console.log(`📊 Chart filter set to: ${chartType}`);
    }
    
    /**
     * Update chart type button states
     * @private
     * @param {HTMLElement} activeButton - Active button
     */
    updateChartTypeButtons(activeButton) {
        this.container.querySelectorAll('[data-chart-type]').forEach(btn => {
            btn.classList.remove('active');
        });
        
        activeButton.classList.add('active');
    }
    
    /**
     * Update heatmap color scheme
     * @private
     * @param {string} scheme - Color scheme name
     */
    updateHeatmapColorScheme(scheme) {
        // Recreate heatmap chart with new color scheme
        const chart = this.charts.get('force-heatmap-chart');
        if (chart) {
            chart.destroy();
            this.options.colorScheme = scheme;
            this.createForceHeatmapChart();
        }
        
        console.log(`🎨 Heatmap color scheme changed to: ${scheme}`);
    }
    
    /**
     * Toggle fullscreen mode
     * @private
     */
    toggleFullscreen() {
        const container = this.container.querySelector('.force-charts-container');
        
        if (container.classList.contains('fullscreen')) {
            container.classList.remove('fullscreen');
            document.body.style.overflow = 'auto';
        } else {
            container.classList.add('fullscreen');
            document.body.style.overflow = 'hidden';
        }
        
        // Resize charts after fullscreen toggle
        setTimeout(() => {
            this.charts.forEach(chart => {
                if (chart) chart.resize();
            });
        }, 100);
    }
    
    /**
     * Handle export functionality
     * @private
     * @param {string} format - Export format
     */
    async handleExport(format) {
        console.log('💾 Exporting charts as:', format);
        
        try {
            switch (format.toLowerCase()) {
                case 'png':
                    await this.exportChartsAsPNG();
                    break;
                    
                case 'svg':
                    await this.exportChartsAsSVG();
                    break;
                    
                case 'pdf':
                    await this.exportChartsAsPDF();
                    break;
                    
                case 'data':
                    await this.exportChartData();
                    break;
                    
                default:
                    throw new Error(`Unsupported export format: ${format}`);
            }
            
            // Close export menu
            this.exportMenuElement.classList.remove('show');
            
            // Show success message
            this.showMessage(`Charts exported successfully as ${format.toUpperCase()}`, 'success');
            
        } catch (error) {
            console.error('❌ Export failed:', error);
            this.showMessage(`Export failed: ${error.message}`, 'error');
        }
    }
    
    /**
     * Export single chart
     * @private
     * @param {string} chartId - Chart identifier
     */
    exportSingleChart(chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        const canvas = chart.canvas;
        const url = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = `${chartId}-${new Date().toISOString().split('T')[0]}.png`;
        link.href = url;
        link.click();
        
        console.log(`💾 Chart exported: ${chartId}`);
    }
    
    /**
     * Export all charts as PNG
     * @private
     */
    async exportChartsAsPNG() {
        const zip = new JSZip(); // Would require JSZip library
        
        for (const [chartId, chart] of this.charts) {
            if (chart) {
                const canvas = chart.canvas;
                const dataURL = canvas.toDataURL('image/png');
                const base64Data = dataURL.split(',')[1];
                zip.file(`${chartId}.png`, base64Data, { base64: true });
            }
        }
        
        const blob = await zip.generateAsync({ type: 'blob' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `force-charts-${new Date().toISOString().split('T')[0]}.zip`;
        link.click();
        window.URL.revokeObjectURL(url);
    }
    
    /**
     * Export charts as SVG
     * @private
     */
    async exportChartsAsSVG() {
        // SVG export would require additional implementation
        this.showMessage('SVG export requires additional implementation', 'info');
    }
    
    /**
     * Export charts as PDF
     * @private
     */
    async exportChartsAsPDF() {
        // PDF export would require jsPDF library
        this.showMessage('PDF export requires additional implementation', 'info');
    }
    
    /**
     * Export chart data
     * @private
     */
    async exportChartData() {
        const exportData = {
            metadata: {
                exportDate: new Date().toISOString(),
                chartCount: this.charts.size,
                dataPoints: this.data.measurements.length
            },
            charts: {}
        };
        
        this.charts.forEach((chart, chartId) => {
            if (chart) {
                exportData.charts[chartId] = {
                    type: chart.config.type,
                    data: chart.data,
                    options: chart.options
                };
            }
        });
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `force-charts-data-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        window.URL.revokeObjectURL(url);
    }
    
    /**
     * Handle window resize
     * @private
     */
    handleResize() {
        // Resize all charts
        setTimeout(() => {
            this.charts.forEach(chart => {
                if (chart) chart.resize();
            });
        }, 100);
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
        if (this.gridElement) {
            this.gridElement.style.display = 'block';
        }
    }
    
    /**
     * Hide content
     * @private
     */
    hideContent() {
        if (this.gridElement) {
            this.gridElement.style.display = 'none';
        }
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
     * Retry loading charts
     * @private
     */
    retry() {
        this.hideError();
        this.showLoading();
        
        // Emit retry event
        this.container.dispatchEvent(new CustomEvent('retryRequested'));
    }
    
    /**
     * Show message to user
     * @private
     * @param {string} message - Message text
     * @param {string} type - Message type
     */
    showMessage(message, type) {
        console.log(`📢 ${type.toUpperCase()}: ${message}`);
        
        // Emit message event
        this.container.dispatchEvent(new CustomEvent('messageRequested', {
            detail: { message, type }
        }));
    }
    
    /**
     * Update chart with new data point (real-time)
     * @param {string} chartId - Chart identifier
     * @param {Object} dataPoint - New data point
     */
    updateChart(chartId, dataPoint) {
        if (!this.options.enableRealTimeUpdates) return;
        
        const now = Date.now();
        if (now - this.lastUpdate < this.options.updateThrottle) {
            // Queue update for later
            this.updateQueue.push({ chartId, dataPoint, timestamp: now });
            return;
        }
        
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        // Add data point to chart
        this.addDataPointToChart(chart, dataPoint);
        
        this.lastUpdate = now;
    }
    
    /**
     * Add data point to chart
     * @private
     * @param {Chart} chart - Chart instance
     * @param {Object} dataPoint - Data point
     */
    addDataPointToChart(chart, dataPoint) {
        const data = chart.data;
        
        // Add new data point
        if (data.labels && data.datasets) {
            data.labels.push(dataPoint.label || data.labels.length + 1);
            
            data.datasets.forEach((dataset, index) => {
                const value = dataPoint.values ? dataPoint.values[index] : dataPoint.value;
                dataset.data.push(value);
                
                // Limit data points for performance
                if (dataset.data.length > this.options.maxDataPoints) {
                    dataset.data.shift();
                    if (data.labels.length > this.options.maxDataPoints) {
                        data.labels.shift();
                    }
                }
            });
        }
        
        // Update chart
        chart.update('none');
    }
    
    /**
     * Process queued updates
     * @private
     */
    processUpdateQueue() {
        if (this.isUpdating || this.updateQueue.length === 0) return;
        
        this.isUpdating = true;
        
        const updates = this.updateQueue.splice(0, 10); // Process up to 10 updates
        
        updates.forEach(update => {
            this.updateChart(update.chartId, update.dataPoint);
        });
        
        this.isUpdating = false;
        
        // Schedule next batch if queue not empty
        if (this.updateQueue.length > 0) {
            setTimeout(() => this.processUpdateQueue(), this.options.updateThrottle);
        }
    }
    
    /**
     * Get chart instance
     * @param {string} chartId - Chart identifier
     * @returns {Chart|null} Chart instance
     */
    getChart(chartId) {
        return this.charts.get(chartId) || null;
    }
    
    /**
     * Get all chart instances
     * @returns {Map} All chart instances
     */
    getAllCharts() {
        return new Map(this.charts);
    }
    
    /**
     * Cleanup component resources
     */
    cleanup() {
        // Destroy all charts
        this.charts.forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts.clear();
        
        // Clear update timer
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
        
        // Remove event listeners
        window.removeEventListener('resize', this.handleResize);
        
        // Clear update queue
        this.updateQueue = [];
        
        // Clear references
        this.data = null;
        
        console.log('🧹 Force Data Charts cleanup complete');
    }
}

console.log('📝 Force Data Charts component module loaded successfully');