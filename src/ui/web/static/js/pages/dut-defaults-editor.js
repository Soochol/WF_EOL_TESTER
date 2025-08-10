/**
 * DUT Defaults Configuration Editor
 * 
 * Provides interface for editing DUT defaults configuration including:
 * - Active profile selection
 * - DUT information (ID, model, operator, manufacturer)
 * - Metadata management
 */

class DUTDefaultsEditor extends ConfigurationEditor {
    constructor() {
        super('dut-defaults-container', '/api/config/dut-defaults-config', 'dut_defaults');
    }

    render() {
        if (!this.container || !this.currentData) return;

        this.container.innerHTML = `
            <div class="config-editor-header">
                <h2>DUT Defaults Configuration Editor</h2>
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
                    ${this.renderDUTDefaultsSection()}
                </div>
            </div>
        `;

        this.setupFormEventListeners();
    }

    renderDUTDefaultsSection() {
        const active_profile = this.currentData.active_profile || 'default';
        const defaults = this.currentData.default || {};
        const metadata = this.currentData.metadata || {};
        
        return `
            <div class="form-section">
                <h3>Profile Configuration</h3>
                <div class="alert alert-info">
                    <strong>Info:</strong> The active profile determines which DUT defaults to use during testing.
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Active Profile</label>
                        <select data-path="active_profile" class="form-control">
                            <option value="default" ${active_profile === 'default' ? 'selected' : ''}>Default</option>
                            <option value="production" ${active_profile === 'production' ? 'selected' : ''}>Production</option>
                            <option value="testing" ${active_profile === 'testing' ? 'selected' : ''}>Testing</option>
                            <option value="development" ${active_profile === 'development' ? 'selected' : ''}>Development</option>
                        </select>
                        <div class="form-help">Select which profile configuration to use</div>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3>Default DUT Information</h3>
                <div class="alert alert-warning">
                    <strong>Note:</strong> These values will be used as defaults for new DUT entries.
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">DUT ID</label>
                        <input type="text" value="${defaults.dut_id || 'DEFAULT001'}" 
                               data-path="default.dut_id" class="form-control" required>
                        <div class="form-help">Default Device Under Test identifier</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Model</label>
                        <input type="text" value="${defaults.model || 'Default Model'}" 
                               data-path="default.model" class="form-control" required>
                        <div class="form-help">Default device model name</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Operator ID</label>
                        <input type="text" value="${defaults.operator_id || 'DEFAULT_OP'}" 
                               data-path="default.operator_id" class="form-control" required>
                        <div class="form-help">Default operator identifier</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Manufacturer</label>
                        <input type="text" value="${defaults.manufacturer || 'Default Manufacturer'}" 
                               data-path="default.manufacturer" class="form-control" required>
                        <div class="form-help">Default manufacturer name</div>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3>Additional DUT Fields</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Serial Number Pattern</label>
                        <input type="text" value="${defaults.serial_number_pattern || 'SN{YYYYMMDD}{###}'}" 
                               data-path="default.serial_number_pattern" class="form-control">
                        <div class="form-help">Pattern for generating serial numbers (optional)</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Part Number</label>
                        <input type="text" value="${defaults.part_number || ''}" 
                               data-path="default.part_number" class="form-control">
                        <div class="form-help">Default part number (optional)</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Revision</label>
                        <input type="text" value="${defaults.revision || 'Rev A'}" 
                               data-path="default.revision" class="form-control">
                        <div class="form-help">Default hardware revision</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Test Station</label>
                        <input type="text" value="${defaults.test_station || 'STATION_01'}" 
                               data-path="default.test_station" class="form-control">
                        <div class="form-help">Default test station identifier</div>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3>Quality Control</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">QC Level</label>
                        <select data-path="default.qc_level" class="form-control">
                            <option value="standard" ${(defaults.qc_level || 'standard') === 'standard' ? 'selected' : ''}>Standard</option>
                            <option value="enhanced" ${defaults.qc_level === 'enhanced' ? 'selected' : ''}>Enhanced</option>
                            <option value="critical" ${defaults.qc_level === 'critical' ? 'selected' : ''}>Critical</option>
                        </select>
                        <div class="form-help">Quality control level for testing</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Inspector ID</label>
                        <input type="text" value="${defaults.inspector_id || 'QC_INSPECTOR'}" 
                               data-path="default.inspector_id" class="form-control">
                        <div class="form-help">Default quality control inspector</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Batch Size</label>
                        <input type="number" value="${defaults.batch_size || 10}" 
                               data-path="default.batch_size" class="form-control" min="1" max="1000">
                        <div class="form-help">Default batch size for testing</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Test Environment</label>
                        <select data-path="default.test_environment" class="form-control">
                            <option value="production" ${(defaults.test_environment || 'production') === 'production' ? 'selected' : ''}>Production</option>
                            <option value="staging" ${defaults.test_environment === 'staging' ? 'selected' : ''}>Staging</option>
                            <option value="development" ${defaults.test_environment === 'development' ? 'selected' : ''}>Development</option>
                        </select>
                        <div class="form-help">Test environment designation</div>
                    </div>
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
                        <textarea data-path="metadata.description" class="form-control" rows="3">${metadata.description || 'DUT defaults configuration'}</textarea>
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

            <div class="form-section">
                <h3>Preview Generated Values</h3>
                <div class="alert alert-success">
                    <strong>Preview:</strong> These values will be used for new DUT entries.
                </div>
                <div class="preview-grid">
                    <div class="preview-item">
                        <strong>Sample DUT ID:</strong> 
                        <span id="preview-dut-id">${defaults.dut_id || 'DEFAULT001'}</span>
                    </div>
                    <div class="preview-item">
                        <strong>Sample Model:</strong> 
                        <span id="preview-model">${defaults.model || 'Default Model'}</span>
                    </div>
                    <div class="preview-item">
                        <strong>Sample Operator:</strong> 
                        <span id="preview-operator">${defaults.operator_id || 'DEFAULT_OP'}</span>
                    </div>
                    <div class="preview-item">
                        <strong>Sample Manufacturer:</strong> 
                        <span id="preview-manufacturer">${defaults.manufacturer || 'Default Manufacturer'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    setupFormEventListeners() {
        // Set up input change listeners
        this.container.querySelectorAll('input[data-path], select[data-path], textarea[data-path]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateField(e.target.dataset.path, e.target.value);
                this.updatePreview();
            });
        });
    }

    updatePreview() {
        // Update preview values when fields change
        const defaults = this.currentData.default || {};
        
        const previewElements = {
            'preview-dut-id': defaults.dut_id || 'DEFAULT001',
            'preview-model': defaults.model || 'Default Model',
            'preview-operator': defaults.operator_id || 'DEFAULT_OP',
            'preview-manufacturer': defaults.manufacturer || 'Default Manufacturer'
        };
        
        Object.entries(previewElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    renderArraySection(path) {
        // DUT Defaults doesn't use arrays, so this is a no-op
        return;
    }
}

// Initialize the editor when the page loads
let dutDefaultsEditor;
document.addEventListener('DOMContentLoaded', () => {
    dutDefaultsEditor = new DUTDefaultsEditor();
});