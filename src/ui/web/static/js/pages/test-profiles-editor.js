/**
 * Test Profiles Configuration Editor
 * 
 * Provides interface for editing test profile configurations including:
 * - Hardware settings (voltage, current, temperature)
 * - Motion control parameters
 * - Test parameters (temperature/position lists)
 * - Timing and tolerance settings
 * - Safety limits and pass criteria
 */

class TestProfilesEditor extends ConfigurationEditor {
    constructor() {
        super('test-profiles-container', '/api/config/profiles/default', 'test_profile');
        this.profileName = 'default'; // Can be made configurable
    }

    async loadConfiguration() {
        try {
            const response = await fetch(`/api/config/profiles/${this.profileName}`);
            if (!response.ok) {
                throw new Error(`Failed to load configuration: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.originalData = data.test_configuration;
            this.currentData = JSON.parse(JSON.stringify(this.originalData));
            this.isDirty = false;
            this.updateDirtyStatus();
            
        } catch (error) {
            console.error('Failed to load test profile:', error);
            this.showNotification('Failed to load test profile', 'error');
        }
    }

    async saveConfiguration(createBackup = true) {
        try {
            this.showLoadingIndicator('Saving test profile...');
            
            const payload = {
                profile_name: this.profileName,
                test_configuration: this.currentData,
                create_backup: createBackup
            };

            const response = await fetch(`/api/config/profiles/${this.profileName}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            
            if (result.success) {
                this.originalData = JSON.parse(JSON.stringify(this.currentData));
                this.isDirty = false;
                this.updateDirtyStatus();
                
                let message = result.message;
                if (result.backup_created && result.backup_path) {
                    message += `\nBackup created: ${result.backup_path}`;
                }
                
                this.showNotification(message, 'success');
            } else {
                this.validationErrors = result.validation_errors || [];
                this.validationWarnings = result.validation_warnings || [];
                this.showValidationErrors();
                this.showNotification(result.message, 'error');
            }
            
        } catch (error) {
            console.error('Failed to save test profile:', error);
            this.showNotification('Failed to save test profile', 'error');
        } finally {
            this.hideLoadingIndicator();
        }
    }

    render() {
        if (!this.container || !this.currentData) return;

        this.container.innerHTML = `
            <div class="config-editor-header">
                <h2>Test Profile Editor - ${this.profileName}</h2>
                <div class="config-status-bar">
                    <span id="config-status" class="status-clean">Saved</span>
                    <div class="config-actions">
                        <button id="validate-config-btn" class="btn btn-secondary">Validate</button>
                        <button id="reset-config-btn" class="btn btn-warning">Reset</button>
                        <button id="export-config-btn" class="btn btn-info">Export</button>
                        <button id="import-config-btn" class="btn btn-info">Import</button>
                        <button id="save-config-btn" class="btn btn-primary">Save</button>
                    </div>
                </div>
            </div>

            <div class="validation-messages">
                <div id="validation-errors" class="validation-errors" style="display: none;"></div>
                <div id="validation-warnings" class="validation-warnings" style="display: none;"></div>
            </div>

            <div class="config-tabs">
                <ul class="tab-nav">
                    <li class="tab-item active"><a href="#hardware-tab" data-tab="hardware">Hardware</a></li>
                    <li class="tab-item"><a href="#motion-tab" data-tab="motion">Motion Control</a></li>
                    <li class="tab-item"><a href="#test-params-tab" data-tab="test-params">Test Parameters</a></li>
                    <li class="tab-item"><a href="#timing-tab" data-tab="timing">Timing</a></li>
                    <li class="tab-item"><a href="#tolerances-tab" data-tab="tolerances">Tolerances</a></li>
                    <li class="tab-item"><a href="#safety-tab" data-tab="safety">Safety</a></li>
                    <li class="tab-item"><a href="#pass-criteria-tab" data-tab="pass-criteria">Pass Criteria</a></li>
                </ul>

                <div class="tab-content">
                    <div id="hardware-tab" class="tab-pane active">
                        ${this.renderHardwareSection()}
                    </div>
                    <div id="motion-tab" class="tab-pane">
                        ${this.renderMotionSection()}
                    </div>
                    <div id="test-params-tab" class="tab-pane">
                        ${this.renderTestParametersSection()}
                    </div>
                    <div id="timing-tab" class="tab-pane">
                        ${this.renderTimingSection()}
                    </div>
                    <div id="tolerances-tab" class="tab-pane">
                        ${this.renderTolerancesSection()}
                    </div>
                    <div id="safety-tab" class="tab-pane">
                        ${this.renderSafetySection()}
                    </div>
                    <div id="pass-criteria-tab" class="tab-pane">
                        ${this.renderPassCriteriaSection()}
                    </div>
                </div>
            </div>
        `;

        this.setupTabNavigation();
        this.setupFormEventListeners();
        this.renderArraySections();
    }

    renderHardwareSection() {
        const hw = this.currentData.hardware || {};
        return `
            <div class="form-section">
                <h3>Hardware Settings</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Voltage (V)</label>
                        <input type="number" step="0.1" value="${hw.voltage || 18.0}" 
                               data-path="hardware.voltage" class="form-control">
                        <div class="form-help">Operating voltage for the test</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Current (A)</label>
                        <input type="number" step="0.1" value="${hw.current || 20.0}" 
                               data-path="hardware.current" class="form-control">
                        <div class="form-help">Operating current for the test</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Upper Current (A)</label>
                        <input type="number" step="0.1" value="${hw.upper_current || 30.0}" 
                               data-path="hardware.upper_current" class="form-control">
                        <div class="form-help">Maximum allowable current</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Upper Temperature (°C)</label>
                        <input type="number" step="0.1" value="${hw.upper_temperature || 80.0}" 
                               data-path="hardware.upper_temperature" class="form-control">
                        <div class="form-help">Maximum operating temperature</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Activation Temperature (°C)</label>
                        <input type="number" step="0.1" value="${hw.activation_temperature || 60.0}" 
                               data-path="hardware.activation_temperature" class="form-control">
                        <div class="form-help">Temperature at which device activates</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Standby Temperature (°C)</label>
                        <input type="number" step="0.1" value="${hw.standby_temperature || 40.0}" 
                               data-path="hardware.standby_temperature" class="form-control">
                        <div class="form-help">Temperature for standby mode</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Fan Speed</label>
                        <input type="number" step="1" value="${hw.fan_speed || 10}" 
                               data-path="hardware.fan_speed" class="form-control">
                        <div class="form-help">Fan speed setting (0-100)</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Stroke (mm)</label>
                        <input type="number" step="0.1" value="${hw.max_stroke || 240.0}" 
                               data-path="hardware.max_stroke" class="form-control">
                        <div class="form-help">Maximum stroke length</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Initial Position (mm)</label>
                        <input type="number" step="0.1" value="${hw.initial_position || 10.0}" 
                               data-path="hardware.initial_position" class="form-control">
                        <div class="form-help">Starting position for tests</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderMotionSection() {
        const motion = this.currentData.motion_control || {};
        return `
            <div class="form-section">
                <h3>Motion Control Parameters</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Velocity (mm/s)</label>
                        <input type="number" step="0.1" value="${motion.velocity || 100.0}" 
                               data-path="motion_control.velocity" class="form-control">
                        <div class="form-help">Movement velocity</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Acceleration (mm/s²)</label>
                        <input type="number" step="0.1" value="${motion.acceleration || 100.0}" 
                               data-path="motion_control.acceleration" class="form-control">
                        <div class="form-help">Acceleration rate</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Deceleration (mm/s²)</label>
                        <input type="number" step="0.1" value="${motion.deceleration || 100.0}" 
                               data-path="motion_control.deceleration" class="form-control">
                        <div class="form-help">Deceleration rate</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderTestParametersSection() {
        return `
            <div class="form-section">
                <h3>Test Parameters</h3>
                <div class="array-editors">
                    <div id="temperature-list-editor" class="array-editor-container">
                        <div class="array-header">
                            <label class="form-label">Temperature List (°C)</label>
                            <button type="button" class="btn btn-sm btn-secondary" onclick="testProfilesEditor.addArrayItem('test_parameters.temperature_list', 25.0)">Add Temperature</button>
                        </div>
                        <div id="test_parameters.temperature_list-items" class="array-items"></div>
                        <div class="form-help">List of temperatures to test at</div>
                    </div>
                    
                    <div id="stroke-positions-editor" class="array-editor-container">
                        <div class="array-header">
                            <label class="form-label">Stroke Positions (mm)</label>
                            <button type="button" class="btn btn-sm btn-secondary" onclick="testProfilesEditor.addArrayItem('test_parameters.stroke_positions', 50.0)">Add Position</button>
                        </div>
                        <div id="test_parameters.stroke_positions-items" class="array-items"></div>
                        <div class="form-help">List of stroke positions to test</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderTimingSection() {
        const timing = this.currentData.timing || {};
        return `
            <div class="form-section">
                <h3>Timing Settings</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Stabilization Delay (s)</label>
                        <input type="number" step="0.01" value="${timing.stabilization_delay || 0.1}" 
                               data-path="timing.stabilization_delay" class="form-control">
                        <div class="form-help">General stabilization delay</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Temperature Stabilization (s)</label>
                        <input type="number" step="0.01" value="${timing.temperature_stabilization || 0.1}" 
                               data-path="timing.temperature_stabilization" class="form-control">
                        <div class="form-help">Time to wait for temperature stabilization</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Standby Stabilization (s)</label>
                        <input type="number" step="0.01" value="${timing.standby_stabilization || 1.0}" 
                               data-path="timing.standby_stabilization" class="form-control">
                        <div class="form-help">Time to wait in standby mode</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Power Stabilization (s)</label>
                        <input type="number" step="0.01" value="${timing.power_stabilization || 0.5}" 
                               data-path="timing.power_stabilization" class="form-control">
                        <div class="form-help">Time to wait for power stabilization</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Loadcell Zero Delay (s)</label>
                        <input type="number" step="0.01" value="${timing.loadcell_zero_delay || 0.1}" 
                               data-path="timing.loadcell_zero_delay" class="form-control">
                        <div class="form-help">Delay before zeroing loadcell</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderTolerancesSection() {
        const tolerances = this.currentData.tolerances || {};
        return `
            <div class="form-section">
                <h3>Tolerance Settings</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Measurement Tolerance</label>
                        <input type="number" step="0.0001" value="${tolerances.measurement_tolerance || 0.001}" 
                               data-path="tolerances.measurement_tolerance" class="form-control">
                        <div class="form-help">General measurement tolerance</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Force Precision (digits)</label>
                        <input type="number" step="1" value="${tolerances.force_precision || 2}" 
                               data-path="tolerances.force_precision" class="form-control">
                        <div class="form-help">Number of decimal places for force measurements</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Temperature Precision (digits)</label>
                        <input type="number" step="1" value="${tolerances.temperature_precision || 1}" 
                               data-path="tolerances.temperature_precision" class="form-control">
                        <div class="form-help">Number of decimal places for temperature measurements</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderSafetySection() {
        const safety = this.currentData.safety || {};
        return `
            <div class="form-section">
                <h3>Safety Limits</h3>
                <div class="alert alert-warning">
                    <strong>Warning:</strong> These are maximum safety limits. Exceeding these values may cause damage or injury.
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Max Voltage (V)</label>
                        <input type="number" step="0.1" value="${safety.max_voltage || 30.0}" 
                               data-path="safety.max_voltage" class="form-control">
                        <div class="form-help">Maximum safe voltage</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Current (A)</label>
                        <input type="number" step="0.1" value="${safety.max_current || 30.0}" 
                               data-path="safety.max_current" class="form-control">
                        <div class="form-help">Maximum safe current</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Velocity (mm/s)</label>
                        <input type="number" step="0.1" value="${safety.max_velocity || 500.0}" 
                               data-path="safety.max_velocity" class="form-control">
                        <div class="form-help">Maximum safe velocity</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Acceleration (mm/s²)</label>
                        <input type="number" step="0.1" value="${safety.max_acceleration || 1000.0}" 
                               data-path="safety.max_acceleration" class="form-control">
                        <div class="form-help">Maximum safe acceleration</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Deceleration (mm/s²)</label>
                        <input type="number" step="0.1" value="${safety.max_deceleration || 1000.0}" 
                               data-path="safety.max_deceleration" class="form-control">
                        <div class="form-help">Maximum safe deceleration</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderPassCriteriaSection() {
        const pass = this.currentData.pass_criteria || {};
        return `
            <div class="form-section">
                <h3>Pass Criteria</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Force Limit Min (N)</label>
                        <input type="number" step="0.1" value="${pass.force_limit_min || 0.0}" 
                               data-path="pass_criteria.force_limit_min" class="form-control">
                        <div class="form-help">Minimum acceptable force</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Force Limit Max (N)</label>
                        <input type="number" step="0.1" value="${pass.force_limit_max || 100.0}" 
                               data-path="pass_criteria.force_limit_max" class="form-control">
                        <div class="form-help">Maximum acceptable force</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Temperature Limit Max (°C)</label>
                        <input type="number" step="0.1" value="${pass.temperature_limit_max || 80.0}" 
                               data-path="pass_criteria.temperature_limit_max" class="form-control">
                        <div class="form-help">Maximum acceptable temperature</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Temperature Limit Min (°C)</label>
                        <input type="number" step="0.1" value="${pass.temperature_limit_min || -10.0}" 
                               data-path="pass_criteria.temperature_limit_min" class="form-control">
                        <div class="form-help">Minimum acceptable temperature</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Position Tolerance (mm)</label>
                        <input type="number" step="0.01" value="${pass.position_tolerance || 0.5}" 
                               data-path="pass_criteria.position_tolerance" class="form-control">
                        <div class="form-help">Acceptable position tolerance</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Max Test Duration (s)</label>
                        <input type="number" step="1" value="${pass.max_test_duration || 300.0}" 
                               data-path="pass_criteria.max_test_duration" class="form-control">
                        <div class="form-help">Maximum time allowed for test</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Min Stabilization Time (s)</label>
                        <input type="number" step="0.01" value="${pass.min_stabilization_time || 0.5}" 
                               data-path="pass_criteria.min_stabilization_time" class="form-control">
                        <div class="form-help">Minimum required stabilization time</div>
                    </div>
                </div>
            </div>
        `;
    }

    setupTabNavigation() {
        const tabLinks = this.container.querySelectorAll('.tab-nav a');
        const tabPanes = this.container.querySelectorAll('.tab-pane');

        tabLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all tabs and panes
                tabLinks.forEach(l => l.parentElement.classList.remove('active'));
                tabPanes.forEach(p => p.classList.remove('active'));
                
                // Add active class to clicked tab
                link.parentElement.classList.add('active');
                
                // Show corresponding pane
                const targetPane = this.container.querySelector(link.getAttribute('href'));
                if (targetPane) {
                    targetPane.classList.add('active');
                }
            });
        });
    }

    setupFormEventListeners() {
        // Set up input change listeners
        this.container.querySelectorAll('input[data-path]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateField(e.target.dataset.path, e.target.value);
            });
        });
    }

    renderArraySections() {
        this.renderArraySection('test_parameters.temperature_list');
        this.renderArraySection('test_parameters.stroke_positions');
    }

    renderArraySection(path) {
        const keys = path.split('.');
        let obj = this.currentData;
        
        for (let key of keys) {
            obj = obj[key] || [];
        }
        
        const itemsContainer = document.getElementById(`${path}-items`);
        if (!itemsContainer || !Array.isArray(obj)) return;
        
        itemsContainer.innerHTML = '';
        
        obj.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'array-item';
            
            const input = document.createElement('input');
            input.type = 'number';
            input.step = '0.1';
            input.value = item;
            input.className = 'form-control';
            input.addEventListener('change', (e) => {
                this.updateArrayItem(path, index, parseFloat(e.target.value) || 0);
            });
            
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'btn btn-sm btn-danger';
            removeBtn.textContent = 'Remove';
            removeBtn.addEventListener('click', () => {
                this.removeArrayItem(path, index);
            });
            
            itemDiv.appendChild(input);
            itemDiv.appendChild(removeBtn);
            itemsContainer.appendChild(itemDiv);
        });
    }
}

// Initialize the editor when the page loads
let testProfilesEditor;
document.addEventListener('DOMContentLoaded', () => {
    testProfilesEditor = new TestProfilesEditor();
});