/**
 * Hardware Model Configuration Editor
 * 
 * Provides interface for editing hardware model selection including:
 * - Robot model selection (mock vs real hardware)
 * - MCU model selection
 * - LoadCell model selection
 * - Power supply model selection
 * - Digital I/O model selection
 */

class HardwareModelEditor extends ConfigurationEditor {
    constructor() {
        super('hardware-model-container', '/api/config/hardware-model', 'hardware_model');
        this.availableModels = {
            robot: ['mock', 'ajinextek'],
            mcu: ['mock', 'lma'],
            loadcell: ['mock', 'bs205'],
            power: ['mock', 'oda'],
            digital_io: ['mock', 'ajinextek']
        };
    }

    render() {
        if (!this.container || !this.currentData) return;

        this.container.innerHTML = `
            <div class="config-editor-header">
                <h2>Hardware Model Configuration Editor</h2>
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

            <div class="tab-content">
                <div class="tab-pane active">
                    ${this.renderHardwareModelSection()}
                </div>
            </div>
        `;

        this.setupFormEventListeners();
        this.updateConfigurationPreview();
    }

    renderHardwareModelSection() {
        const hardware_model = this.currentData.hardware_model || {};
        const metadata = this.currentData.metadata || {};
        
        return `
            <div class="form-section">
                <h3>Hardware Model Selection</h3>
                <div class="alert alert-info">
                    <strong>Info:</strong> Select the hardware implementation to use for each component. 
                    Use 'mock' for testing without physical hardware.
                </div>
                
                <div class="model-grid">
                    <div class="model-card">
                        <div class="model-header">
                            <h4>Robot Controller</h4>
                            <div class="model-status" id="robot-status">
                                ${this.getModelStatusBadge(hardware_model.robot || 'mock')}
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Robot Model</label>
                            <select data-path="hardware_model.robot" class="form-control model-select" data-component="robot">
                                ${this.renderModelOptions('robot', hardware_model.robot || 'mock')}
                            </select>
                            <div class="form-help">${this.getModelDescription('robot', hardware_model.robot || 'mock')}</div>
                        </div>
                    </div>

                    <div class="model-card">
                        <div class="model-header">
                            <h4>Microcontroller (MCU)</h4>
                            <div class="model-status" id="mcu-status">
                                ${this.getModelStatusBadge(hardware_model.mcu || 'mock')}
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">MCU Model</label>
                            <select data-path="hardware_model.mcu" class="form-control model-select" data-component="mcu">
                                ${this.renderModelOptions('mcu', hardware_model.mcu || 'mock')}
                            </select>
                            <div class="form-help">${this.getModelDescription('mcu', hardware_model.mcu || 'mock')}</div>
                        </div>
                    </div>

                    <div class="model-card">
                        <div class="model-header">
                            <h4>Load Cell</h4>
                            <div class="model-status" id="loadcell-status">
                                ${this.getModelStatusBadge(hardware_model.loadcell || 'mock')}
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">LoadCell Model</label>
                            <select data-path="hardware_model.loadcell" class="form-control model-select" data-component="loadcell">
                                ${this.renderModelOptions('loadcell', hardware_model.loadcell || 'mock')}
                            </select>
                            <div class="form-help">${this.getModelDescription('loadcell', hardware_model.loadcell || 'mock')}</div>
                        </div>
                    </div>

                    <div class="model-card">
                        <div class="model-header">
                            <h4>Power Supply</h4>
                            <div class="model-status" id="power-status">
                                ${this.getModelStatusBadge(hardware_model.power || 'mock')}
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Power Model</label>
                            <select data-path="hardware_model.power" class="form-control model-select" data-component="power">
                                ${this.renderModelOptions('power', hardware_model.power || 'mock')}
                            </select>
                            <div class="form-help">${this.getModelDescription('power', hardware_model.power || 'mock')}</div>
                        </div>
                    </div>

                    <div class="model-card">
                        <div class="model-header">
                            <h4>Digital I/O</h4>
                            <div class="model-status" id="digital_io-status">
                                ${this.getModelStatusBadge(hardware_model.digital_io || 'mock')}
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Digital I/O Model</label>
                            <select data-path="hardware_model.digital_io" class="form-control model-select" data-component="digital_io">
                                ${this.renderModelOptions('digital_io', hardware_model.digital_io || 'mock')}
                            </select>
                            <div class="form-help">${this.getModelDescription('digital_io', hardware_model.digital_io || 'mock')}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3>Configuration Overview</h3>
                <div class="config-overview">
                    <div class="overview-item">
                        <strong>System Mode:</strong>
                        <span id="system-mode">${this.getSystemMode(hardware_model)}</span>
                    </div>
                    <div class="overview-item">
                        <strong>Hardware Components:</strong>
                        <span id="hardware-count">${this.getRealHardwareCount(hardware_model)} real, ${this.getMockHardwareCount(hardware_model)} mock</span>
                    </div>
                    <div class="overview-item">
                        <strong>Test Environment:</strong>
                        <span id="test-env">${this.getTestEnvironment(hardware_model)}</span>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3>Quick Configuration Templates</h3>
                <div class="template-buttons">
                    <button type="button" class="btn btn-secondary template-btn" onclick="hardwareModelEditor.applyTemplate('all_mock')">
                        All Mock (Testing)
                    </button>
                    <button type="button" class="btn btn-secondary template-btn" onclick="hardwareModelEditor.applyTemplate('all_real')">
                        All Real Hardware
                    </button>
                    <button type="button" class="btn btn-secondary template-btn" onclick="hardwareModelEditor.applyTemplate('mixed_dev')">
                        Mixed (Development)
                    </button>
                    <button type="button" class="btn btn-secondary template-btn" onclick="hardwareModelEditor.applyTemplate('production')">
                        Production Setup
                    </button>
                </div>
                <div class="template-description">
                    <p><strong>Templates:</strong></p>
                    <ul>
                        <li><strong>All Mock:</strong> Use mock implementations for all components (safe for testing)</li>
                        <li><strong>All Real:</strong> Use real hardware for all components (requires physical hardware)</li>
                        <li><strong>Mixed Development:</strong> Mix of real and mock for development testing</li>
                        <li><strong>Production:</strong> Optimized configuration for production testing</li>
                    </ul>
                </div>
            </div>

            <div class="form-section">
                <h3>Configuration Metadata</h3>
                <div class="alert alert-info">
                    <strong>Info:</strong> Metadata is automatically managed but can be viewed for reference.
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Description</label>
                        <textarea data-path="metadata.description" class="form-control" rows="3">${metadata.description || 'Hardware model configuration'}</textarea>
                        <div class="form-help">Configuration description</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Version</label>
                        <input type="text" value="${metadata.version || '1.0'}" 
                               data-path="metadata.version" class="form-control" readonly>
                        <div class="form-help">Configuration version (read-only)</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Created By</label>
                        <input type="text" value="${metadata.created_by || 'System'}" 
                               data-path="metadata.created_by" class="form-control" readonly>
                        <div class="form-help">Who created this configuration (read-only)</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Created Time</label>
                        <input type="text" value="${metadata.created_time || new Date().toISOString()}" 
                               data-path="metadata.created_time" class="form-control" readonly>
                        <div class="form-help">When configuration was created (read-only)</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderModelOptions(component, selected) {
        return this.availableModels[component].map(model => 
            `<option value="${model}" ${model === selected ? 'selected' : ''}>${this.formatModelName(model)}</option>`
        ).join('');
    }

    formatModelName(model) {
        const names = {
            'mock': 'Mock (Testing)',
            'ajinextek': 'Ajinextek',
            'lma': 'LMA',
            'bs205': 'BS205',
            'oda': 'ODA'
        };
        return names[model] || model.charAt(0).toUpperCase() + model.slice(1);
    }

    getModelDescription(component, model) {
        const descriptions = {
            robot: {
                mock: 'Virtual robot for testing without physical hardware',
                ajinextek: 'Ajinextek robot controller for real hardware control'
            },
            mcu: {
                mock: 'Virtual MCU for testing without physical microcontroller',
                lma: 'LMA microcontroller for real hardware communication'
            },
            loadcell: {
                mock: 'Virtual load cell for testing without physical sensor',
                bs205: 'BS205 load cell indicator for real force measurements'
            },
            power: {
                mock: 'Virtual power supply for testing without physical power control',
                oda: 'ODA power supply for real power control'
            },
            digital_io: {
                mock: 'Virtual digital I/O for testing without physical buttons/lights',
                ajinextek: 'Ajinextek digital I/O for real button and indicator control'
            }
        };
        return descriptions[component]?.[model] || `${model} implementation for ${component}`;
    }

    getModelStatusBadge(model) {
        if (model === 'mock') {
            return '<span class="badge badge-warning">Mock</span>';
        } else {
            return '<span class="badge badge-success">Real Hardware</span>';
        }
    }

    getSystemMode(hardware_model) {
        const realCount = this.getRealHardwareCount(hardware_model);
        const totalCount = Object.keys(this.availableModels).length;
        
        if (realCount === 0) {
            return 'Full Mock (Testing)';
        } else if (realCount === totalCount) {
            return 'Full Hardware (Production)';
        } else {
            return 'Mixed (Development)';
        }
    }

    getRealHardwareCount(hardware_model) {
        return Object.entries(hardware_model || {}).filter(([key, value]) => value !== 'mock').length;
    }

    getMockHardwareCount(hardware_model) {
        return Object.entries(hardware_model || {}).filter(([key, value]) => value === 'mock').length;
    }

    getTestEnvironment(hardware_model) {
        const realCount = this.getRealHardwareCount(hardware_model);
        const totalCount = Object.keys(this.availableModels).length;
        
        if (realCount === 0) {
            return 'Safe for automated testing';
        } else if (realCount === totalCount) {
            return 'Requires all physical hardware';
        } else {
            return 'Requires some physical hardware';
        }
    }

    setupFormEventListeners() {
        // Set up input change listeners
        this.container.querySelectorAll('input[data-path], select[data-path], textarea[data-path]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateField(e.target.dataset.path, e.target.value);
                
                // Update status badges and overview when model selection changes
                if (input.classList.contains('model-select')) {
                    this.updateModelStatus(e.target.dataset.component, e.target.value);
                    this.updateConfigurationPreview();
                }
            });
        });
    }

    updateModelStatus(component, model) {
        const statusElement = document.getElementById(`${component}-status`);
        if (statusElement) {
            statusElement.innerHTML = this.getModelStatusBadge(model);
        }
        
        // Update description
        const helpElement = statusElement?.parentElement?.parentElement?.querySelector('.form-help');
        if (helpElement) {
            helpElement.textContent = this.getModelDescription(component, model);
        }
    }

    updateConfigurationPreview() {
        const hardware_model = this.currentData.hardware_model || {};
        
        // Update system mode
        const systemModeElement = document.getElementById('system-mode');
        if (systemModeElement) {
            systemModeElement.textContent = this.getSystemMode(hardware_model);
        }
        
        // Update hardware count
        const hardwareCountElement = document.getElementById('hardware-count');
        if (hardwareCountElement) {
            hardwareCountElement.textContent = `${this.getRealHardwareCount(hardware_model)} real, ${this.getMockHardwareCount(hardware_model)} mock`;
        }
        
        // Update test environment
        const testEnvElement = document.getElementById('test-env');
        if (testEnvElement) {
            testEnvElement.textContent = this.getTestEnvironment(hardware_model);
        }
    }

    applyTemplate(templateName) {
        const templates = {
            all_mock: {
                robot: 'mock',
                mcu: 'mock',
                loadcell: 'mock',
                power: 'mock',
                digital_io: 'mock'
            },
            all_real: {
                robot: 'ajinextek',
                mcu: 'lma',
                loadcell: 'bs205',
                power: 'oda',
                digital_io: 'ajinextek'
            },
            mixed_dev: {
                robot: 'mock',
                mcu: 'lma',
                loadcell: 'bs205',
                power: 'mock',
                digital_io: 'mock'
            },
            production: {
                robot: 'ajinextek',
                mcu: 'lma',
                loadcell: 'bs205',
                power: 'oda',
                digital_io: 'ajinextek'
            }
        };
        
        const template = templates[templateName];
        if (!template) return;
        
        // Confirm with user
        const templateDescriptions = {
            all_mock: 'All Mock (safe for testing without hardware)',
            all_real: 'All Real Hardware (requires physical components)',
            mixed_dev: 'Mixed Development (some real, some mock)',
            production: 'Production Setup (optimized for real testing)'
        };
        
        if (!confirm(`Apply template: ${templateDescriptions[templateName]}?\n\nThis will change all hardware model selections.`)) {
            return;
        }
        
        // Apply template
        this.currentData.hardware_model = { ...template };
        this.isDirty = true;
        this.updateDirtyStatus();
        
        // Update the UI
        Object.entries(template).forEach(([component, model]) => {
            const selectElement = this.container.querySelector(`select[data-path="hardware_model.${component}"]`);
            if (selectElement) {
                selectElement.value = model;
                this.updateModelStatus(component, model);
            }
        });
        
        this.updateConfigurationPreview();
        this.showNotification(`Applied template: ${templateDescriptions[templateName]}`, 'success');
    }

    renderArraySection(path) {
        // Hardware Model doesn't use arrays, so this is a no-op
        return;
    }
}

// Initialize the editor when the page loads
let hardwareModelEditor;
document.addEventListener('DOMContentLoaded', () => {
    hardwareModelEditor = new HardwareModelEditor();
});