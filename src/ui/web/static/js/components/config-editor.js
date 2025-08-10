/**
 * Configuration Editor Base Component
 * 
 * Provides common functionality for all configuration editors including:
 * - Form validation and error handling
 * - Save/load operations with backup creation
 * - YAML preview and syntax validation
 * - Change tracking and auto-save
 * - Array editing capabilities
 */

class ConfigurationEditor {
    constructor(containerId, apiEndpoint, configType) {
        this.container = document.getElementById(containerId);
        this.apiEndpoint = apiEndpoint;
        this.configType = configType;
        this.originalData = {};
        this.currentData = {};
        this.isDirty = false;
        this.validationErrors = [];
        this.validationWarnings = [];
        this.autoSaveEnabled = true;
        this.autoSaveInterval = null;
        this.autoSaveDelay = 5000; // 5 seconds

        this.init();
    }

    async init() {
        await this.loadConfiguration();
        this.setupEventListeners();
        this.setupAutoSave();
        this.render();
    }

    async loadConfiguration() {
        try {
            const response = await fetch(this.apiEndpoint);
            if (!response.ok) {
                throw new Error(`Failed to load configuration: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.originalData = JSON.parse(JSON.stringify(data));
            this.currentData = JSON.parse(JSON.stringify(data));
            this.isDirty = false;
            this.updateDirtyStatus();
            
        } catch (error) {
            console.error('Failed to load configuration:', error);
            this.showNotification('Failed to load configuration', 'error');
        }
    }

    async saveConfiguration(createBackup = true) {
        try {
            this.showLoadingIndicator('Saving configuration...');
            
            const payload = {
                ...this.currentData,
                create_backup: createBackup
            };

            const response = await fetch(this.apiEndpoint, {
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
            console.error('Failed to save configuration:', error);
            this.showNotification('Failed to save configuration', 'error');
        } finally {
            this.hideLoadingIndicator();
        }
    }

    async validateConfiguration() {
        try {
            const response = await fetch('/api/config/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    configuration: this.currentData,
                    config_type: this.configType,
                    strict_validation: false
                })
            });

            const result = await response.json();
            
            this.validationErrors = result.validation_errors || [];
            this.validationWarnings = result.validation_warnings || [];
            
            this.showValidationErrors();
            
            return result.is_valid;
            
        } catch (error) {
            console.error('Failed to validate configuration:', error);
            return false;
        }
    }

    resetConfiguration() {
        if (confirm('Are you sure you want to reset all changes? This cannot be undone.')) {
            this.currentData = JSON.parse(JSON.stringify(this.originalData));
            this.isDirty = false;
            this.updateDirtyStatus();
            this.validationErrors = [];
            this.validationWarnings = [];
            this.render();
            this.showNotification('Configuration reset to original values', 'info');
        }
    }

    exportConfiguration() {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.currentData, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `${this.configType}_${new Date().toISOString().slice(0,19).replace(/:/g, '-')}.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    }

    importConfiguration() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json,.yaml,.yml';
        
        input.onchange = (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const importedData = JSON.parse(e.target.result);
                        this.currentData = importedData;
                        this.isDirty = true;
                        this.updateDirtyStatus();
                        this.render();
                        this.showNotification('Configuration imported successfully', 'success');
                    } catch (error) {
                        this.showNotification('Failed to parse imported file', 'error');
                    }
                };
                reader.readAsText(file);
            }
        };
        
        input.click();
    }

    updateField(path, value) {
        const keys = path.split('.');
        let obj = this.currentData;
        
        for (let i = 0; i < keys.length - 1; i++) {
            if (!obj[keys[i]]) {
                obj[keys[i]] = {};
            }
            obj = obj[keys[i]];
        }
        
        const lastKey = keys[keys.length - 1];
        const oldValue = obj[lastKey];
        
        // Convert value to appropriate type
        if (typeof oldValue === 'number') {
            value = parseFloat(value) || 0;
        } else if (typeof oldValue === 'boolean') {
            value = value === 'true' || value === true;
        }
        
        obj[lastKey] = value;
        this.isDirty = true;
        this.updateDirtyStatus();
        this.clearAutoSaveTimer();
        this.setAutoSaveTimer();
    }

    addArrayItem(path, defaultValue = '') {
        const keys = path.split('.');
        let obj = this.currentData;
        
        for (let key of keys) {
            if (!obj[key]) {
                obj[key] = [];
            }
            obj = obj[key];
        }
        
        if (Array.isArray(obj)) {
            obj.push(defaultValue);
            this.isDirty = true;
            this.updateDirtyStatus();
            this.renderArraySection(path);
        }
    }

    removeArrayItem(path, index) {
        const keys = path.split('.');
        let obj = this.currentData;
        
        for (let key of keys) {
            obj = obj[key];
        }
        
        if (Array.isArray(obj) && index >= 0 && index < obj.length) {
            obj.splice(index, 1);
            this.isDirty = true;
            this.updateDirtyStatus();
            this.renderArraySection(path);
        }
    }

    setupEventListeners() {
        // Save button
        const saveBtn = document.getElementById('save-config-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveConfiguration());
        }

        // Reset button
        const resetBtn = document.getElementById('reset-config-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetConfiguration());
        }

        // Validate button
        const validateBtn = document.getElementById('validate-config-btn');
        if (validateBtn) {
            validateBtn.addEventListener('click', () => this.validateConfiguration());
        }

        // Export button
        const exportBtn = document.getElementById('export-config-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportConfiguration());
        }

        // Import button
        const importBtn = document.getElementById('import-config-btn');
        if (importBtn) {
            importBtn.addEventListener('click', () => this.importConfiguration());
        }

        // Prevent page unload when there are unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (this.isDirty) {
                const message = 'You have unsaved changes. Are you sure you want to leave?';
                e.returnValue = message;
                return message;
            }
        });
    }

    setupAutoSave() {
        if (this.autoSaveEnabled) {
            this.setAutoSaveTimer();
        }
    }

    setAutoSaveTimer() {
        if (this.autoSaveInterval) {
            clearTimeout(this.autoSaveInterval);
        }
        
        this.autoSaveInterval = setTimeout(() => {
            if (this.isDirty) {
                this.autoSave();
            }
        }, this.autoSaveDelay);
    }

    clearAutoSaveTimer() {
        if (this.autoSaveInterval) {
            clearTimeout(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
    }

    async autoSave() {
        try {
            // Only auto-save if validation passes
            const isValid = await this.validateConfiguration();
            if (isValid) {
                await this.saveConfiguration(false); // Don't create backup for auto-save
                this.showNotification('Auto-saved', 'info');
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }

    updateDirtyStatus() {
        const statusElement = document.getElementById('config-status');
        if (statusElement) {
            statusElement.textContent = this.isDirty ? 'Unsaved changes' : 'Saved';
            statusElement.className = this.isDirty ? 'status-dirty' : 'status-clean';
        }

        // Update save button state
        const saveBtn = document.getElementById('save-config-btn');
        if (saveBtn) {
            saveBtn.disabled = !this.isDirty;
        }
    }

    showValidationErrors() {
        const errorsContainer = document.getElementById('validation-errors');
        const warningsContainer = document.getElementById('validation-warnings');
        
        if (errorsContainer) {
            errorsContainer.innerHTML = '';
            if (this.validationErrors.length > 0) {
                errorsContainer.style.display = 'block';
                this.validationErrors.forEach(error => {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'validation-error';
                    errorDiv.textContent = error;
                    errorsContainer.appendChild(errorDiv);
                });
            } else {
                errorsContainer.style.display = 'none';
            }
        }
        
        if (warningsContainer) {
            warningsContainer.innerHTML = '';
            if (this.validationWarnings.length > 0) {
                warningsContainer.style.display = 'block';
                this.validationWarnings.forEach(warning => {
                    const warningDiv = document.createElement('div');
                    warningDiv.className = 'validation-warning';
                    warningDiv.textContent = warning;
                    warningsContainer.appendChild(warningDiv);
                });
            } else {
                warningsContainer.style.display = 'none';
            }
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        
        // Add to notifications container or create one
        let container = document.getElementById('notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notifications-container';
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds for info notifications
        if (type === 'info' || type === 'success') {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 5000);
        }
    }

    showLoadingIndicator(message = 'Loading...') {
        let indicator = document.getElementById('loading-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'loading-indicator';
            indicator.className = 'loading-indicator';
            document.body.appendChild(indicator);
        }
        
        indicator.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-message">${message}</div>
        `;
        indicator.style.display = 'flex';
    }

    hideLoadingIndicator() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    // Abstract methods to be implemented by specific editors
    render() {
        throw new Error('render() method must be implemented by subclass');
    }

    renderArraySection(path) {
        throw new Error('renderArraySection() method must be implemented by subclass');
    }

    // Utility methods for form generation
    createInputElement(type, path, value, attributes = {}) {
        const input = document.createElement('input');
        input.type = type;
        input.value = value || '';
        input.dataset.path = path;
        
        Object.keys(attributes).forEach(key => {
            input.setAttribute(key, attributes[key]);
        });
        
        input.addEventListener('change', (e) => {
            this.updateField(path, e.target.value);
        });
        
        return input;
    }

    createSelectElement(path, value, options, attributes = {}) {
        const select = document.createElement('select');
        select.dataset.path = path;
        
        Object.keys(attributes).forEach(key => {
            select.setAttribute(key, attributes[key]);
        });
        
        options.forEach(option => {
            const optElement = document.createElement('option');
            optElement.value = option.value;
            optElement.textContent = option.label;
            if (option.value === value) {
                optElement.selected = true;
            }
            select.appendChild(optElement);
        });
        
        select.addEventListener('change', (e) => {
            this.updateField(path, e.target.value);
        });
        
        return select;
    }

    createFormGroup(label, element, helpText = null) {
        const group = document.createElement('div');
        group.className = 'form-group';
        
        const labelElement = document.createElement('label');
        labelElement.textContent = label;
        labelElement.className = 'form-label';
        
        if (element.id) {
            labelElement.setAttribute('for', element.id);
        }
        
        group.appendChild(labelElement);
        group.appendChild(element);
        
        if (helpText) {
            const help = document.createElement('div');
            help.className = 'form-help';
            help.textContent = helpText;
            group.appendChild(help);
        }
        
        return group;
    }

    createArrayEditor(label, path, items = [], itemType = 'text') {
        const container = document.createElement('div');
        container.className = 'array-editor';
        container.dataset.path = path;
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'array-header';
        
        const labelElement = document.createElement('label');
        labelElement.textContent = label;
        labelElement.className = 'form-label';
        
        const addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.className = 'btn btn-sm btn-secondary';
        addBtn.textContent = 'Add Item';
        addBtn.addEventListener('click', () => {
            const defaultValue = itemType === 'number' ? 0 : '';
            this.addArrayItem(path, defaultValue);
        });
        
        headerDiv.appendChild(labelElement);
        headerDiv.appendChild(addBtn);
        container.appendChild(headerDiv);
        
        const itemsContainer = document.createElement('div');
        itemsContainer.className = 'array-items';
        itemsContainer.id = `${path}-items`;
        container.appendChild(itemsContainer);
        
        this.renderArrayItems(path, items, itemType);
        
        return container;
    }

    renderArrayItems(path, items, itemType = 'text') {
        const container = document.getElementById(`${path}-items`);
        if (!container) return;
        
        container.innerHTML = '';
        
        items.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'array-item';
            
            const input = document.createElement('input');
            input.type = itemType;
            input.value = item;
            input.addEventListener('change', (e) => {
                this.updateArrayItem(path, index, e.target.value);
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
            container.appendChild(itemDiv);
        });
    }

    updateArrayItem(path, index, value) {
        const keys = path.split('.');
        let obj = this.currentData;
        
        for (let key of keys) {
            obj = obj[key];
        }
        
        if (Array.isArray(obj) && index >= 0 && index < obj.length) {
            // Convert value to appropriate type
            if (typeof obj[index] === 'number') {
                value = parseFloat(value) || 0;
            }
            obj[index] = value;
            this.isDirty = true;
            this.updateDirtyStatus();
            this.clearAutoSaveTimer();
            this.setAutoSaveTimer();
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConfigurationEditor;
}