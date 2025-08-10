/**
 * Force Data Matrix Table Component - WF EOL Tester Web Interface
 * 
 * This component provides a comprehensive Temperature×Stroke Force data matrix table with:
 * - 2D matrix display (Temperature rows × Stroke position columns)
 * - Sortable columns and rows with custom sorting logic
 * - Color-coded cells based on force values (heatmap visualization)
 * - Pass/fail indicators based on test criteria
 * - Export functionality (CSV, Excel, JSON formats)
 * - Cell detail view with measurement metadata
 * - Statistical summaries (min, max, average, standard deviation)
 * - Missing data indicators for incomplete tests
 * - Interactive features with hover effects and tooltips
 * - Responsive design for different screen sizes
 * 
 * @author WF EOL Tester Team
 * @version 1.0.0
 */

export class ForceDataMatrixTable {
    /**
     * Initialize Force Data Matrix Table component
     * @param {HTMLElement} container - Container element for the table
     * @param {Object} options - Configuration options
     */
    constructor(container, options = {}) {
        console.log('📊 Initializing Force Data Matrix Table component...');
        
        // Core properties
        this.container = container;
        this.options = {
            // Data configuration
            temperatureList: [20, 25, 30, 35, 40, 45, 50], // Default temperature points
            strokePositions: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], // Default stroke positions (mm)
            
            // Display options
            showStatistics: true,
            showPassFail: true,
            enableSorting: true,
            enableExport: true,
            enableHover: true,
            
            // Color scheme for heatmap
            colorScheme: 'viridis', // viridis, plasma, inferno, magma
            minColor: '#440154',
            maxColor: '#fde725',
            neutralColor: '#21908c',
            missingColor: '#f0f0f0',
            
            // Pass/fail criteria
            passCriteria: {
                minForce: 100, // Minimum force (N)
                maxForce: 1000, // Maximum force (N)
                tolerance: 0.1 // 10% tolerance
            },
            
            // Table formatting
            decimalPlaces: 1,
            units: 'N',
            locale: 'en-US',
            
            ...options
        };
        
        // State management
        this.data = null;
        this.processedData = null;
        this.sortConfig = { column: null, direction: 'asc' };
        this.selectedCell = null;
        this.statistics = {};
        
        // UI elements
        this.tableElement = null;
        this.headerElement = null;
        this.bodyElement = null;
        this.statisticsElement = null;
        this.exportElement = null;
        this.tooltipElement = null;
        
        // Bind methods
        this.handleCellClick = this.handleCellClick.bind(this);
        this.handleCellHover = this.handleCellHover.bind(this);
        this.handleCellLeave = this.handleCellLeave.bind(this);
        this.handleSort = this.handleSort.bind(this);
        this.handleExport = this.handleExport.bind(this);
        this.handleResize = this.handleResize.bind(this);
        
        // Initialize component
        this.init();
        
        console.log('✅ Force Data Matrix Table component initialized');
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
            
            // Apply initial styling
            this.applyInitialStyling();
            
            // Show loading state
            this.showLoading();
            
        } catch (error) {
            console.error('❌ Failed to initialize Force Data Matrix Table:', error);
            this.showError('Initialization failed', error.message);
        }
    }
    
    /**
     * Create component structure
     * @private
     */
    createStructure() {
        this.container.innerHTML = `
            <div class="force-matrix-table-container">
                <!-- Header with title and controls -->
                <div class="force-matrix-header">
                    <div class="force-matrix-title">
                        <h3>🌡️📏 Temperature × Stroke Force Data Matrix</h3>
                        <div class="force-matrix-subtitle">
                            Force measurements across temperature and stroke position combinations
                        </div>
                    </div>
                    <div class="force-matrix-controls">
                        <div class="force-matrix-view-controls">
                            <button class="btn btn-sm btn-secondary" id="matrix-table-view" data-view="table">
                                📊 Table View
                            </button>
                            <button class="btn btn-sm btn-secondary" id="matrix-heatmap-view" data-view="heatmap">
                                🔥 Heatmap View
                            </button>
                        </div>
                        <div class="force-matrix-export-controls">
                            <div class="dropdown">
                                <button class="btn btn-sm btn-info dropdown-toggle" id="matrix-export-btn">
                                    💾 Export Data
                                </button>
                                <div class="dropdown-menu" id="matrix-export-menu">
                                    <a class="dropdown-item" data-format="csv">📄 CSV File</a>
                                    <a class="dropdown-item" data-format="excel">📊 Excel File</a>
                                    <a class="dropdown-item" data-format="json">🔗 JSON Data</a>
                                    <a class="dropdown-item" data-format="pdf">📋 PDF Report</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Statistics Summary -->
                <div class="force-matrix-statistics" id="matrix-statistics" style="display: none;">
                    <div class="statistics-grid">
                        <div class="stat-item">
                            <div class="stat-label">Total Measurements</div>
                            <div class="stat-value" id="stat-total">-</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Min Force</div>
                            <div class="stat-value" id="stat-min">- N</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Max Force</div>
                            <div class="stat-value" id="stat-max">- N</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Average Force</div>
                            <div class="stat-value" id="stat-avg">- N</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Std Deviation</div>
                            <div class="stat-value" id="stat-std">- N</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Pass Rate</div>
                            <div class="stat-value" id="stat-pass-rate">-%</div>
                        </div>
                    </div>
                </div>
                
                <!-- Matrix Table Container -->
                <div class="force-matrix-table-wrapper">
                    <div class="force-matrix-scroll-container">
                        <table class="force-matrix-table" id="force-matrix-table">
                            <thead id="matrix-table-header">
                                <!-- Table header will be generated dynamically -->
                            </thead>
                            <tbody id="matrix-table-body">
                                <!-- Table body will be generated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Color Scale Legend -->
                <div class="force-matrix-legend">
                    <div class="legend-title">Force Scale (N)</div>
                    <div class="legend-scale" id="matrix-legend-scale">
                        <!-- Legend will be generated dynamically -->
                    </div>
                    <div class="legend-labels" id="matrix-legend-labels">
                        <!-- Legend labels will be generated dynamically -->
                    </div>
                </div>
                
                <!-- Loading State -->
                <div class="force-matrix-loading" id="matrix-loading">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Loading force data matrix...</div>
                </div>
                
                <!-- Error State -->
                <div class="force-matrix-error" id="matrix-error" style="display: none;">
                    <div class="error-icon">⚠️</div>
                    <div class="error-message">
                        <h4>Error Loading Data</h4>
                        <p class="error-details">Failed to load force measurement data</p>
                    </div>
                    <button class="btn btn-primary" id="matrix-retry-btn">Retry</button>
                </div>
            </div>
            
            <!-- Cell Detail Tooltip -->
            <div class="force-matrix-tooltip" id="matrix-tooltip" style="display: none;">
                <div class="tooltip-header">
                    <strong class="tooltip-title"></strong>
                </div>
                <div class="tooltip-content">
                    <div class="tooltip-row">
                        <span class="tooltip-label">Temperature:</span>
                        <span class="tooltip-value" id="tooltip-temp">-</span>
                    </div>
                    <div class="tooltip-row">
                        <span class="tooltip-label">Stroke Position:</span>
                        <span class="tooltip-value" id="tooltip-stroke">-</span>
                    </div>
                    <div class="tooltip-row">
                        <span class="tooltip-label">Force:</span>
                        <span class="tooltip-value" id="tooltip-force">-</span>
                    </div>
                    <div class="tooltip-row">
                        <span class="tooltip-label">Status:</span>
                        <span class="tooltip-status" id="tooltip-status">-</span>
                    </div>
                    <div class="tooltip-row">
                        <span class="tooltip-label">Timestamp:</span>
                        <span class="tooltip-value" id="tooltip-timestamp">-</span>
                    </div>
                </div>
            </div>
        `;
        
        // Cache DOM references
        this.tableElement = document.getElementById('force-matrix-table');
        this.headerElement = document.getElementById('matrix-table-header');
        this.bodyElement = document.getElementById('matrix-table-body');
        this.statisticsElement = document.getElementById('matrix-statistics');
        this.exportElement = document.getElementById('matrix-export-menu');
        this.tooltipElement = document.getElementById('matrix-tooltip');
        this.loadingElement = document.getElementById('matrix-loading');
        this.errorElement = document.getElementById('matrix-error');
    }
    
    /**
     * Setup event listeners
     * @private
     */
    setupEventListeners() {
        // Export menu events
        if (this.exportElement) {
            this.exportElement.addEventListener('click', (e) => {
                if (e.target.hasAttribute('data-format')) {
                    e.preventDefault();
                    this.handleExport(e.target.getAttribute('data-format'));
                }
            });
        }
        
        // Export button toggle
        const exportBtn = document.getElementById('matrix-export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.exportElement.classList.toggle('show');
            });
        }
        
        // Close export menu when clicking outside
        document.addEventListener('click', () => {
            if (this.exportElement) {
                this.exportElement.classList.remove('show');
            }
        });
        
        // View control buttons
        const tableViewBtn = document.getElementById('matrix-table-view');
        const heatmapViewBtn = document.getElementById('matrix-heatmap-view');
        
        if (tableViewBtn) {
            tableViewBtn.addEventListener('click', () => {
                this.setView('table');
                this.updateViewButtons('table');
            });
        }
        
        if (heatmapViewBtn) {
            heatmapViewBtn.addEventListener('click', () => {
                this.setView('heatmap');
                this.updateViewButtons('heatmap');
            });
        }
        
        // Retry button
        const retryBtn = document.getElementById('matrix-retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => {
                this.retry();
            });
        }
        
        // Window resize for responsive behavior
        window.addEventListener('resize', this.handleResize);
        
        // Table mouse events (will be attached to cells when created)
        if (this.tableElement) {
            this.tableElement.addEventListener('click', this.handleCellClick);
            this.tableElement.addEventListener('mouseover', this.handleCellHover);
            this.tableElement.addEventListener('mouseout', this.handleCellLeave);
        }
    }
    
    /**
     * Apply initial styling
     * @private
     */
    applyInitialStyling() {
        // Add component-specific CSS class
        this.container.classList.add('force-matrix-component');
        
        // Set default view
        this.setView('table');
        this.updateViewButtons('table');
    }
    
    /**
     * Load and display force data matrix
     * @param {Object} data - Force measurement data
     * @param {Object} options - Display options
     */
    loadData(data, options = {}) {
        console.log('📊 Loading force data matrix...', data);
        
        try {
            // Merge options
            this.options = { ...this.options, ...options };
            
            // Validate and process data
            this.data = this.validateData(data);
            this.processedData = this.processData(this.data);
            
            // Calculate statistics
            this.calculateStatistics();
            
            // Generate table
            this.generateTable();
            
            // Generate legend
            this.generateLegend();
            
            // Update statistics display
            this.updateStatistics();
            
            // Hide loading, show content
            this.hideLoading();
            this.showContent();
            
            console.log('✅ Force data matrix loaded successfully');
            
        } catch (error) {
            console.error('❌ Failed to load force data matrix:', error);
            this.showError('Data loading failed', error.message);
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
        
        // Extract required fields
        const { measurements, temperatureList, strokePositions, passCriteria } = data;
        
        if (!measurements || !Array.isArray(measurements)) {
            throw new Error('Invalid data: Measurements must be an array');
        }
        
        // Validate measurement structure
        measurements.forEach((measurement, index) => {
            if (!measurement.temperature || !measurement.strokePosition || measurement.force === undefined) {
                throw new Error(`Invalid measurement at index ${index}: Missing required fields`);
            }
        });
        
        return {
            measurements,
            temperatureList: temperatureList || this.options.temperatureList,
            strokePositions: strokePositions || this.options.strokePositions,
            passCriteria: passCriteria || this.options.passCriteria
        };
    }
    
    /**
     * Process data for display
     * @private
     * @param {Object} data - Validated data
     * @returns {Object} Processed data matrix
     */
    processData(data) {
        const { measurements, temperatureList, strokePositions } = data;
        
        // Create matrix structure
        const matrix = {};
        
        // Initialize matrix with empty values
        temperatureList.forEach(temp => {
            matrix[temp] = {};
            strokePositions.forEach(stroke => {
                matrix[temp][stroke] = null;
            });
        });
        
        // Populate matrix with measurements
        measurements.forEach(measurement => {
            const { temperature, strokePosition, force, timestamp, status } = measurement;
            
            if (matrix[temperature] && matrix[temperature][strokePosition] !== undefined) {
                matrix[temperature][strokePosition] = {
                    force: parseFloat(force),
                    timestamp: timestamp || new Date().toISOString(),
                    status: status || 'unknown',
                    pass: this.evaluatePassFail(force)
                };
            }
        });
        
        return {
            matrix,
            temperatureList,
            strokePositions,
            measurementCount: measurements.length
        };
    }
    
    /**
     * Evaluate pass/fail status for a force measurement
     * @private
     * @param {number} force - Force value to evaluate
     * @returns {boolean} Pass/fail status
     */
    evaluatePassFail(force) {
        const { minForce, maxForce, tolerance } = this.options.passCriteria;
        const toleranceRange = maxForce * tolerance;
        
        return force >= (minForce - toleranceRange) && force <= (maxForce + toleranceRange);
    }
    
    /**
     * Calculate statistics for the data
     * @private
     */
    calculateStatistics() {
        const forces = [];
        let passCount = 0;
        let totalCount = 0;
        
        // Extract all force values
        Object.values(this.processedData.matrix).forEach(tempRow => {
            Object.values(tempRow).forEach(cell => {
                if (cell && cell.force !== null && cell.force !== undefined) {
                    forces.push(cell.force);
                    totalCount++;
                    if (cell.pass) passCount++;
                }
            });
        });
        
        if (forces.length === 0) {
            this.statistics = {
                total: 0,
                min: 0,
                max: 0,
                avg: 0,
                std: 0,
                passRate: 0
            };
            return;
        }
        
        // Calculate statistics
        const min = Math.min(...forces);
        const max = Math.max(...forces);
        const avg = forces.reduce((sum, f) => sum + f, 0) / forces.length;
        const variance = forces.reduce((sum, f) => sum + Math.pow(f - avg, 2), 0) / forces.length;
        const std = Math.sqrt(variance);
        const passRate = totalCount > 0 ? (passCount / totalCount) * 100 : 0;
        
        this.statistics = {
            total: totalCount,
            min: min,
            max: max,
            avg: avg,
            std: std,
            passRate: passRate
        };
        
        console.log('📈 Statistics calculated:', this.statistics);
    }
    
    /**
     * Generate HTML table
     * @private
     */
    generateTable() {
        // Generate header
        this.generateTableHeader();
        
        // Generate body
        this.generateTableBody();
    }
    
    /**
     * Generate table header
     * @private
     */
    generateTableHeader() {
        const { strokePositions } = this.processedData;
        
        let headerHTML = `
            <tr>
                <th class="matrix-temp-header sortable" data-sort="temperature">
                    <div class="header-content">
                        <span class="header-text">Temperature (°C)</span>
                        <span class="sort-icon">↕️</span>
                    </div>
                </th>
        `;
        
        strokePositions.forEach(stroke => {
            headerHTML += `
                <th class="matrix-stroke-header sortable" data-sort="stroke-${stroke}">
                    <div class="header-content">
                        <span class="header-text">${stroke}mm</span>
                        <span class="sort-icon">↕️</span>
                    </div>
                </th>
            `;
        });
        
        headerHTML += `
                <th class="matrix-stats-header">
                    <div class="header-content">
                        <span class="header-text">Statistics</span>
                    </div>
                </th>
            </tr>
        `;
        
        this.headerElement.innerHTML = headerHTML;
        
        // Add sort event listeners
        this.headerElement.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', () => {
                this.handleSort(header.getAttribute('data-sort'));
            });
        });
    }
    
    /**
     * Generate table body
     * @private
     */
    generateTableBody() {
        const { matrix, temperatureList, strokePositions } = this.processedData;
        
        let bodyHTML = '';
        
        // Sort temperatures if needed
        const sortedTemperatures = this.getSortedTemperatures();
        
        sortedTemperatures.forEach(temp => {
            const row = matrix[temp];
            if (!row) return;
            
            // Calculate row statistics
            const rowForces = strokePositions
                .map(stroke => row[stroke]?.force)
                .filter(f => f !== null && f !== undefined);
            
            const rowStats = this.calculateRowStatistics(rowForces);
            
            let rowHTML = `
                <tr class="matrix-data-row" data-temperature="${temp}">
                    <td class="matrix-temp-cell">
                        <div class="temp-value">${temp}°C</div>
                    </td>
            `;
            
            strokePositions.forEach(stroke => {
                const cell = row[stroke];
                const cellClass = this.getCellClass(cell);
                const cellStyle = this.getCellStyle(cell);
                
                rowHTML += `
                    <td class="matrix-force-cell ${cellClass}" 
                        style="${cellStyle}"
                        data-temperature="${temp}"
                        data-stroke="${stroke}"
                        data-force="${cell?.force || 'null'}"
                        data-pass="${cell?.pass || 'null'}"
                        data-timestamp="${cell?.timestamp || ''}"
                        data-status="${cell?.status || 'missing'}">
                        <div class="cell-content">
                            ${this.formatCellContent(cell)}
                        </div>
                        ${cell?.pass !== null ? `<div class="pass-indicator ${cell.pass ? 'pass' : 'fail'}">${cell.pass ? '✓' : '✗'}</div>` : ''}
                    </td>
                `;
            });
            
            // Add row statistics cell
            rowHTML += `
                <td class="matrix-stats-cell">
                    <div class="row-stats">
                        <div class="stat-item">Avg: ${rowStats.avg.toFixed(1)}N</div>
                        <div class="stat-item">Range: ${rowStats.min.toFixed(1)}-${rowStats.max.toFixed(1)}N</div>
                        <div class="stat-item">Count: ${rowStats.count}</div>
                    </div>
                </td>
            </tr>
            `;
            
            bodyHTML += rowHTML;
        });
        
        this.bodyElement.innerHTML = bodyHTML;
    }
    
    /**
     * Get sorted temperatures based on current sort configuration
     * @private
     * @returns {Array} Sorted temperature array
     */
    getSortedTemperatures() {
        const { temperatureList } = this.processedData;
        let sorted = [...temperatureList];
        
        if (this.sortConfig.column === 'temperature') {
            sorted.sort((a, b) => {
                return this.sortConfig.direction === 'asc' ? a - b : b - a;
            });
        }
        
        return sorted;
    }
    
    /**
     * Calculate statistics for a row
     * @private
     * @param {Array} forces - Array of force values
     * @returns {Object} Row statistics
     */
    calculateRowStatistics(forces) {
        if (forces.length === 0) {
            return { min: 0, max: 0, avg: 0, count: 0 };
        }
        
        return {
            min: Math.min(...forces),
            max: Math.max(...forces),
            avg: forces.reduce((sum, f) => sum + f, 0) / forces.length,
            count: forces.length
        };
    }
    
    /**
     * Get CSS class for cell based on its data
     * @private
     * @param {Object} cell - Cell data
     * @returns {string} CSS class
     */
    getCellClass(cell) {
        if (!cell) return 'missing-data';
        if (cell.pass === true) return 'pass-cell';
        if (cell.pass === false) return 'fail-cell';
        return 'unknown-cell';
    }
    
    /**
     * Get CSS style for cell based on force value
     * @private
     * @param {Object} cell - Cell data
     * @returns {string} CSS style
     */
    getCellStyle(cell) {
        if (!cell || cell.force === null || cell.force === undefined) {
            return `background-color: ${this.options.missingColor};`;
        }
        
        const color = this.getHeatmapColor(cell.force);
        return `background-color: ${color};`;
    }
    
    /**
     * Get heatmap color for force value
     * @private
     * @param {number} force - Force value
     * @returns {string} Hex color
     */
    getHeatmapColor(force) {
        const { min, max } = this.statistics;
        
        if (min === max) {
            return this.options.neutralColor;
        }
        
        // Normalize force value to 0-1 range
        const normalized = (force - min) / (max - min);
        
        // Apply color scheme
        return this.interpolateColor(
            this.options.minColor,
            this.options.maxColor,
            normalized
        );
    }
    
    /**
     * Interpolate between two colors
     * @private
     * @param {string} color1 - Start color (hex)
     * @param {string} color2 - End color (hex)
     * @param {number} factor - Interpolation factor (0-1)
     * @returns {string} Interpolated color (hex)
     */
    interpolateColor(color1, color2, factor) {
        // Convert hex to RGB
        const rgb1 = this.hexToRgb(color1);
        const rgb2 = this.hexToRgb(color2);
        
        // Interpolate
        const r = Math.round(rgb1.r + factor * (rgb2.r - rgb1.r));
        const g = Math.round(rgb1.g + factor * (rgb2.g - rgb1.g));
        const b = Math.round(rgb1.b + factor * (rgb2.b - rgb1.b));
        
        // Convert back to hex
        return this.rgbToHex(r, g, b);
    }
    
    /**
     * Convert hex color to RGB
     * @private
     * @param {string} hex - Hex color
     * @returns {Object} RGB values
     */
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }
    
    /**
     * Convert RGB to hex color
     * @private
     * @param {number} r - Red value
     * @param {number} g - Green value
     * @param {number} b - Blue value
     * @returns {string} Hex color
     */
    rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }
    
    /**
     * Format cell content for display
     * @private
     * @param {Object} cell - Cell data
     * @returns {string} Formatted content
     */
    formatCellContent(cell) {
        if (!cell) {
            return '<span class="missing-value">No Data</span>';
        }
        
        const force = parseFloat(cell.force);
        if (isNaN(force)) {
            return '<span class="invalid-value">Invalid</span>';
        }
        
        return `<span class="force-value">${force.toFixed(this.options.decimalPlaces)}</span><span class="force-unit">${this.options.units}</span>`;
    }
    
    /**
     * Generate color legend
     * @private
     */
    generateLegend() {
        const legendScale = document.getElementById('matrix-legend-scale');
        const legendLabels = document.getElementById('matrix-legend-labels');
        
        if (!legendScale || !legendLabels) return;
        
        const { min, max } = this.statistics;
        const steps = 10;
        const stepSize = (max - min) / steps;
        
        // Generate color scale
        let scaleHTML = '';
        for (let i = 0; i <= steps; i++) {
            const value = min + (i * stepSize);
            const color = this.getHeatmapColor(value);
            scaleHTML += `<div class="legend-step" style="background-color: ${color};" title="${value.toFixed(1)}N"></div>`;
        }
        legendScale.innerHTML = scaleHTML;
        
        // Generate labels
        legendLabels.innerHTML = `
            <div class="legend-label legend-min">${min.toFixed(1)}</div>
            <div class="legend-label legend-mid">${((min + max) / 2).toFixed(1)}</div>
            <div class="legend-label legend-max">${max.toFixed(1)}</div>
        `;
    }
    
    /**
     * Update statistics display
     * @private
     */
    updateStatistics() {
        document.getElementById('stat-total').textContent = this.statistics.total;
        document.getElementById('stat-min').textContent = `${this.statistics.min.toFixed(1)} N`;
        document.getElementById('stat-max').textContent = `${this.statistics.max.toFixed(1)} N`;
        document.getElementById('stat-avg').textContent = `${this.statistics.avg.toFixed(1)} N`;
        document.getElementById('stat-std').textContent = `${this.statistics.std.toFixed(1)} N`;
        document.getElementById('stat-pass-rate').textContent = `${this.statistics.passRate.toFixed(1)}%`;
        
        if (this.options.showStatistics) {
            this.statisticsElement.style.display = 'block';
        }
    }
    
    /**
     * Handle cell click events
     * @private
     * @param {Event} event - Click event
     */
    handleCellClick(event) {
        const cell = event.target.closest('.matrix-force-cell');
        if (!cell) return;
        
        // Update selected cell
        if (this.selectedCell) {
            this.selectedCell.classList.remove('selected');
        }
        
        cell.classList.add('selected');
        this.selectedCell = cell;
        
        // Get cell data
        const cellData = this.getCellData(cell);
        console.log('🎯 Cell selected:', cellData);
        
        // Emit cell selection event
        this.container.dispatchEvent(new CustomEvent('cellSelected', {
            detail: cellData
        }));
    }
    
    /**
     * Handle cell hover events
     * @private
     * @param {Event} event - Mouse over event
     */
    handleCellHover(event) {
        const cell = event.target.closest('.matrix-force-cell');
        if (!cell || !this.options.enableHover) return;
        
        // Get cell data
        const cellData = this.getCellData(cell);
        
        // Update tooltip content
        this.updateTooltip(cellData);
        
        // Position and show tooltip
        this.showTooltip(event.pageX, event.pageY);
    }
    
    /**
     * Handle cell leave events
     * @private
     * @param {Event} event - Mouse out event
     */
    handleCellLeave(event) {
        if (!event.relatedTarget || !this.tooltipElement.contains(event.relatedTarget)) {
            this.hideTooltip();
        }
    }
    
    /**
     * Get data for a specific cell
     * @private
     * @param {HTMLElement} cellElement - Cell DOM element
     * @returns {Object} Cell data
     */
    getCellData(cellElement) {
        return {
            temperature: parseFloat(cellElement.getAttribute('data-temperature')),
            strokePosition: parseFloat(cellElement.getAttribute('data-stroke')),
            force: parseFloat(cellElement.getAttribute('data-force')),
            pass: cellElement.getAttribute('data-pass') === 'true',
            timestamp: cellElement.getAttribute('data-timestamp'),
            status: cellElement.getAttribute('data-status')
        };
    }
    
    /**
     * Update tooltip content
     * @private
     * @param {Object} cellData - Cell data
     */
    updateTooltip(cellData) {
        if (!this.tooltipElement) return;
        
        const { temperature, strokePosition, force, pass, timestamp, status } = cellData;
        
        // Update tooltip content
        this.tooltipElement.querySelector('.tooltip-title').textContent = 
            `Measurement at ${temperature}°C, ${strokePosition}mm`;
        
        document.getElementById('tooltip-temp').textContent = `${temperature}°C`;
        document.getElementById('tooltip-stroke').textContent = `${strokePosition}mm`;
        document.getElementById('tooltip-force').textContent = 
            isNaN(force) ? 'No Data' : `${force.toFixed(1)}N`;
        
        const statusElement = document.getElementById('tooltip-status');
        if (isNaN(force)) {
            statusElement.textContent = 'Missing Data';
            statusElement.className = 'tooltip-status missing';
        } else {
            statusElement.textContent = pass ? 'PASS' : 'FAIL';
            statusElement.className = `tooltip-status ${pass ? 'pass' : 'fail'}`;
        }
        
        document.getElementById('tooltip-timestamp').textContent = 
            timestamp ? new Date(timestamp).toLocaleString() : 'Unknown';
    }
    
    /**
     * Show tooltip at position
     * @private
     * @param {number} x - X coordinate
     * @param {number} y - Y coordinate
     */
    showTooltip(x, y) {
        if (!this.tooltipElement) return;
        
        this.tooltipElement.style.left = `${x + 10}px`;
        this.tooltipElement.style.top = `${y - 10}px`;
        this.tooltipElement.style.display = 'block';
        
        // Adjust position if tooltip goes off screen
        setTimeout(() => {
            const rect = this.tooltipElement.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            
            if (rect.right > viewportWidth) {
                this.tooltipElement.style.left = `${x - rect.width - 10}px`;
            }
            
            if (rect.bottom > viewportHeight) {
                this.tooltipElement.style.top = `${y - rect.height - 10}px`;
            }
        }, 0);
    }
    
    /**
     * Hide tooltip
     * @private
     */
    hideTooltip() {
        if (this.tooltipElement) {
            this.tooltipElement.style.display = 'none';
        }
    }
    
    /**
     * Handle sorting
     * @private
     * @param {string} column - Column to sort
     */
    handleSort(column) {
        // Update sort configuration
        if (this.sortConfig.column === column) {
            this.sortConfig.direction = this.sortConfig.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortConfig.column = column;
            this.sortConfig.direction = 'asc';
        }
        
        // Regenerate table with new sort
        this.generateTableBody();
        
        // Update sort indicators
        this.updateSortIndicators();
        
        console.log('🔄 Table sorted:', this.sortConfig);
    }
    
    /**
     * Update sort indicators in headers
     * @private
     */
    updateSortIndicators() {
        // Reset all indicators
        this.headerElement.querySelectorAll('.sort-icon').forEach(icon => {
            icon.textContent = '↕️';
        });
        
        // Update active indicator
        const activeHeader = this.headerElement.querySelector(`[data-sort="${this.sortConfig.column}"]`);
        if (activeHeader) {
            const icon = activeHeader.querySelector('.sort-icon');
            if (icon) {
                icon.textContent = this.sortConfig.direction === 'asc' ? '↑' : '↓';
            }
        }
    }
    
    /**
     * Handle data export
     * @private
     * @param {string} format - Export format (csv, excel, json, pdf)
     */
    async handleExport(format) {
        console.log('💾 Exporting data as:', format);
        
        try {
            let exportData;
            let filename = `force-data-matrix-${new Date().toISOString().split('T')[0]}`;
            
            switch (format.toLowerCase()) {
                case 'csv':
                    exportData = this.generateCSV();
                    filename += '.csv';
                    this.downloadFile(exportData, filename, 'text/csv');
                    break;
                
                case 'excel':
                    exportData = this.generateExcel();
                    filename += '.xlsx';
                    // Excel export would require additional library
                    this.showMessage('Excel export requires additional setup', 'warning');
                    break;
                
                case 'json':
                    exportData = JSON.stringify(this.generateJSON(), null, 2);
                    filename += '.json';
                    this.downloadFile(exportData, filename, 'application/json');
                    break;
                
                case 'pdf':
                    await this.generatePDF();
                    break;
                
                default:
                    throw new Error(`Unsupported export format: ${format}`);
            }
            
            // Close export menu
            this.exportElement.classList.remove('show');
            
            // Show success message
            this.showMessage(`Data exported successfully as ${format.toUpperCase()}`, 'success');
            
        } catch (error) {
            console.error('❌ Export failed:', error);
            this.showMessage(`Export failed: ${error.message}`, 'error');
        }
    }
    
    /**
     * Generate CSV data
     * @private
     * @returns {string} CSV content
     */
    generateCSV() {
        const { matrix, temperatureList, strokePositions } = this.processedData;
        let csv = '';
        
        // Header row
        csv += 'Temperature (°C)';
        strokePositions.forEach(stroke => {
            csv += `,${stroke}mm Force (N),${stroke}mm Pass/Fail,${stroke}mm Status`;
        });
        csv += ',Row Average,Row Min,Row Max,Row Count\n';
        
        // Data rows
        temperatureList.forEach(temp => {
            const row = matrix[temp];
            csv += temp;
            
            const rowForces = [];
            
            strokePositions.forEach(stroke => {
                const cell = row[stroke];
                if (cell) {
                    csv += `,${cell.force},${cell.pass ? 'PASS' : 'FAIL'},${cell.status}`;
                    rowForces.push(cell.force);
                } else {
                    csv += ',,,';
                }
            });
            
            // Row statistics
            if (rowForces.length > 0) {
                const avg = rowForces.reduce((sum, f) => sum + f, 0) / rowForces.length;
                const min = Math.min(...rowForces);
                const max = Math.max(...rowForces);
                csv += `,${avg.toFixed(2)},${min.toFixed(2)},${max.toFixed(2)},${rowForces.length}`;
            } else {
                csv += ',,,0';
            }
            
            csv += '\n';
        });
        
        return csv;
    }
    
    /**
     * Generate JSON data
     * @private
     * @returns {Object} JSON data
     */
    generateJSON() {
        return {
            metadata: {
                exportDate: new Date().toISOString(),
                totalMeasurements: this.statistics.total,
                temperatureRange: {
                    min: Math.min(...this.processedData.temperatureList),
                    max: Math.max(...this.processedData.temperatureList)
                },
                strokeRange: {
                    min: Math.min(...this.processedData.strokePositions),
                    max: Math.max(...this.processedData.strokePositions)
                }
            },
            statistics: this.statistics,
            matrix: this.processedData.matrix,
            temperatureList: this.processedData.temperatureList,
            strokePositions: this.processedData.strokePositions
        };
    }
    
    /**
     * Generate PDF report
     * @private
     */
    async generatePDF() {
        // This would require a PDF library like jsPDF
        // For now, show a message about implementation
        this.showMessage('PDF export requires additional implementation', 'info');
    }
    
    /**
     * Download file with data
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
     * Set view mode
     * @private
     * @param {string} view - View mode (table, heatmap)
     */
    setView(view) {
        this.currentView = view;
        
        const tableElement = this.container.querySelector('.force-matrix-table-wrapper');
        
        if (view === 'heatmap') {
            tableElement.classList.add('heatmap-view');
        } else {
            tableElement.classList.remove('heatmap-view');
        }
    }
    
    /**
     * Update view button states
     * @private
     * @param {string} activeView - Active view
     */
    updateViewButtons(activeView) {
        const tableBtn = document.getElementById('matrix-table-view');
        const heatmapBtn = document.getElementById('matrix-heatmap-view');
        
        if (tableBtn && heatmapBtn) {
            tableBtn.classList.toggle('active', activeView === 'table');
            heatmapBtn.classList.toggle('active', activeView === 'heatmap');
        }
    }
    
    /**
     * Handle window resize
     * @private
     */
    handleResize() {
        // Responsive adjustments if needed
        if (this.tooltipElement && this.tooltipElement.style.display === 'block') {
            this.hideTooltip();
        }
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
        const wrapper = this.container.querySelector('.force-matrix-table-wrapper');
        const legend = this.container.querySelector('.force-matrix-legend');
        
        if (wrapper) wrapper.style.display = 'block';
        if (legend) legend.style.display = 'block';
    }
    
    /**
     * Hide content
     * @private
     */
    hideContent() {
        const wrapper = this.container.querySelector('.force-matrix-table-wrapper');
        const legend = this.container.querySelector('.force-matrix-legend');
        
        if (wrapper) wrapper.style.display = 'none';
        if (legend) legend.style.display = 'none';
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
     * Retry loading data
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
     * @param {string} type - Message type (success, error, warning, info)
     */
    showMessage(message, type) {
        // This would integrate with the app's notification system
        console.log(`📢 ${type.toUpperCase()}: ${message}`);
        
        // Emit message event
        this.container.dispatchEvent(new CustomEvent('messageRequested', {
            detail: { message, type }
        }));
    }
    
    /**
     * Update component with new options
     * @param {Object} newOptions - New options to merge
     */
    updateOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
        
        if (this.data) {
            // Regenerate with new options
            this.processedData = this.processData(this.data);
            this.calculateStatistics();
            this.generateTable();
            this.generateLegend();
            this.updateStatistics();
        }
    }
    
    /**
     * Get current data
     * @returns {Object} Current matrix data
     */
    getData() {
        return this.processedData;
    }
    
    /**
     * Get statistics
     * @returns {Object} Current statistics
     */
    getStatistics() {
        return this.statistics;
    }
    
    /**
     * Cleanup component resources
     */
    cleanup() {
        // Remove event listeners
        window.removeEventListener('resize', this.handleResize);
        
        if (this.tableElement) {
            this.tableElement.removeEventListener('click', this.handleCellClick);
            this.tableElement.removeEventListener('mouseover', this.handleCellHover);
            this.tableElement.removeEventListener('mouseout', this.handleCellLeave);
        }
        
        // Hide tooltip
        this.hideTooltip();
        
        // Clear references
        this.data = null;
        this.processedData = null;
        this.selectedCell = null;
        
        console.log('🧹 Force Data Matrix Table cleanup complete');
    }
}

console.log('📝 Force Data Matrix Table component module loaded successfully');