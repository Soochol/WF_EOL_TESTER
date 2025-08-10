/**
 * Configuration Management Dashboard
 * 
 * Main dashboard for managing all configuration files with overview,
 * status monitoring, and batch operations.
 */

class ConfigurationManagement {
    constructor() {
        this.init();
    }

    async init() {
        await this.loadSystemStatus();
        await this.loadRecentChanges();
        this.setupEventListeners();
    }

    async loadSystemStatus() {
        try {
            // Load active profile
            const profileResponse = await fetch('/api/config/profiles/usage');
            if (profileResponse.ok) {
                const profileData = await profileResponse.json();
                document.getElementById('active-profile').textContent = 
                    profileData.current_profile || 'default';
            }

            // Load hardware model info
            const hardwareResponse = await fetch('/api/config/hardware-model');
            if (hardwareResponse.ok) {
                const hardwareData = await hardwareResponse.json();
                const hardwareModel = hardwareData.hardware_model || {};
                const realCount = Object.values(hardwareModel).filter(value => value !== 'mock').length;
                const totalCount = Object.keys(hardwareModel).length;
                
                if (realCount === 0) {
                    document.getElementById('hardware-mode').textContent = 'All Mock (Testing)';
                } else if (realCount === totalCount) {
                    document.getElementById('hardware-mode').textContent = 'All Real Hardware';
                } else {
                    document.getElementById('hardware-mode').textContent = `Mixed (${realCount}/${totalCount} real)`;
                }
            }

            // Load configuration version and last modified
            document.getElementById('config-version').textContent = '1.0';
            document.getElementById('last-modified').textContent = new Date().toLocaleDateString();

        } catch (error) {
            console.error('Failed to load system status:', error);
            this.showNotification('Failed to load system status', 'error');
        }
    }

    async loadRecentChanges() {
        try {
            const container = document.getElementById('recent-changes-list');
            
            // Mock recent changes data - in a real system, this would come from the API
            const recentChanges = [
                {
                    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
                    config_type: 'Test Profile',
                    operation: 'Updated',
                    description: 'Modified temperature list and timing settings',
                    user: 'System'
                },
                {
                    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
                    config_type: 'Hardware Model',
                    operation: 'Changed',
                    description: 'Switched to mock mode for testing',
                    user: 'System'
                },
                {
                    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
                    config_type: 'DUT Defaults',
                    operation: 'Created',
                    description: 'Added new DUT default configuration',
                    user: 'System'
                }
            ];

            container.innerHTML = '';
            
            if (recentChanges.length === 0) {
                container.innerHTML = '<p class="no-changes">No recent changes found.</p>';
                return;
            }

            recentChanges.forEach(change => {
                const changeItem = document.createElement('div');
                changeItem.className = 'change-item';
                changeItem.innerHTML = `
                    <div class="change-header">
                        <span class="change-type">${change.config_type}</span>
                        <span class="change-operation operation-${change.operation.toLowerCase()}">${change.operation}</span>
                        <span class="change-timestamp">${this.formatTimestamp(change.timestamp)}</span>
                    </div>
                    <div class="change-description">${change.description}</div>
                    <div class="change-user">by ${change.user}</div>
                `;
                container.appendChild(changeItem);
            });

        } catch (error) {
            console.error('Failed to load recent changes:', error);
            document.getElementById('recent-changes-list').innerHTML = 
                '<p class="error-message">Failed to load recent changes.</p>';
        }
    }

    setupEventListeners() {
        // Validate All button
        document.getElementById('validate-all-btn')?.addEventListener('click', () => {
            this.validateAllConfigurations();
        });

        // Backup All button
        document.getElementById('backup-all-btn')?.addEventListener('click', () => {
            this.createConfigurationBackup();
        });

        // Import Configuration button
        document.getElementById('import-config-btn')?.addEventListener('click', () => {
            this.importConfiguration();
        });

        // Export All button
        document.getElementById('export-all-btn')?.addEventListener('click', () => {
            this.exportAllConfigurations();
        });
    }

    async validateAllConfigurations() {
        try {
            this.showLoadingIndicator('Validating all configurations...');
            
            const validationResults = [];
            const configTypes = [
                { type: 'test_profile', endpoint: '/api/config/profiles/default' },
                { type: 'hardware_config', endpoint: '/api/config/hardware-config' },
                { type: 'hardware_model', endpoint: '/api/config/hardware-model' },
                { type: 'dut_defaults', endpoint: '/api/config/dut-defaults-config' }
            ];

            for (const config of configTypes) {
                try {
                    // Load configuration
                    const response = await fetch(config.endpoint);
                    if (!response.ok) {
                        validationResults.push({
                            type: config.type,
                            valid: false,
                            errors: [`Failed to load ${config.type}: ${response.statusText}`]
                        });
                        continue;
                    }

                    const data = await response.json();
                    let configData;

                    // Extract configuration data based on type
                    switch (config.type) {
                        case 'test_profile':
                            configData = data.test_configuration;
                            break;
                        case 'hardware_config':
                            configData = data.hardware_config;
                            break;
                        case 'hardware_model':
                            configData = data.hardware_model;
                            break;
                        case 'dut_defaults':
                            configData = data;
                            break;
                        default:
                            configData = data;
                    }

                    // Validate configuration
                    const validationResponse = await fetch('/api/config/validate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            configuration: configData,
                            config_type: config.type
                        })
                    });

                    const validationResult = await validationResponse.json();
                    validationResults.push({
                        type: config.type,
                        valid: validationResult.is_valid,
                        errors: validationResult.validation_errors || [],
                        warnings: validationResult.validation_warnings || []
                    });

                } catch (error) {
                    validationResults.push({
                        type: config.type,
                        valid: false,
                        errors: [`Validation failed: ${error.message}`]
                    });
                }
            }

            this.showValidationResults(validationResults);

        } catch (error) {
            console.error('Failed to validate configurations:', error);
            this.showNotification('Failed to validate configurations', 'error');
        } finally {
            this.hideLoadingIndicator();
        }
    }

    showValidationResults(results) {
        const totalConfigs = results.length;
        const validConfigs = results.filter(r => r.valid).length;
        const hasErrors = results.some(r => r.errors.length > 0);

        let message = `Validation complete: ${validConfigs}/${totalConfigs} configurations valid.`;
        
        if (hasErrors) {
            message += '\n\nErrors found:';
            results.forEach(result => {
                if (result.errors.length > 0) {
                    message += `\n\n${result.type.replace('_', ' ').toUpperCase()}:`;
                    result.errors.forEach(error => {
                        message += `\n• ${error}`;
                    });
                }
            });
        }

        // Show in a modal or notification
        if (hasErrors) {
            alert(message);
        } else {
            this.showNotification(`All ${totalConfigs} configurations are valid!`, 'success');
        }
    }

    async createConfigurationBackup() {
        try {
            this.showLoadingIndicator('Creating configuration backup...');
            
            // This would call a backup API endpoint
            const response = await fetch('/api/config/backup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    include_all: true,
                    backup_name: `backup_${new Date().toISOString().slice(0,19).replace(/:/g, '-')}`
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification(`Backup created successfully: ${result.backup_name}`, 'success');
            } else {
                throw new Error(`Backup failed: ${response.statusText}`);
            }

        } catch (error) {
            console.error('Failed to create backup:', error);
            this.showNotification('Backup creation is not yet implemented', 'info');
        } finally {
            this.hideLoadingIndicator();
        }
    }

    importConfiguration() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json,.yaml,.yml,.zip';
        
        input.onchange = async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            try {
                this.showLoadingIndicator('Importing configuration...');
                
                // This would upload and process the configuration file
                const formData = new FormData();
                formData.append('config_file', file);

                const response = await fetch('/api/config/import', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    this.showNotification(`Configuration imported: ${result.imported_configs?.length || 0} files processed`, 'success');
                    await this.loadSystemStatus();
                    await this.loadRecentChanges();
                } else {
                    throw new Error(`Import failed: ${response.statusText}`);
                }

            } catch (error) {
                console.error('Failed to import configuration:', error);
                this.showNotification('Configuration import is not yet implemented', 'info');
            } finally {
                this.hideLoadingIndicator();
            }
        };
        
        input.click();
    }

    async exportAllConfigurations() {
        try {
            this.showLoadingIndicator('Exporting all configurations...');
            
            // Create a zip file with all configurations
            const timestamp = new Date().toISOString().slice(0,19).replace(/:/g, '-');
            const filename = `wf_eol_tester_config_${timestamp}.zip`;
            
            const response = await fetch('/api/config/export-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showNotification('Configurations exported successfully', 'success');
            } else {
                throw new Error(`Export failed: ${response.statusText}`);
            }

        } catch (error) {
            console.error('Failed to export configurations:', error);
            this.showNotification('Configuration export is not yet implemented', 'info');
        } finally {
            this.hideLoadingIndicator();
        }
    }

    formatTimestamp(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) {
            return `${days} day${days === 1 ? '' : 's'} ago`;
        } else if (hours > 0) {
            return `${hours} hour${hours === 1 ? '' : 's'} ago`;
        } else if (minutes > 0) {
            return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
        } else {
            return 'Just now';
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
}

// Initialize the configuration management dashboard when the page loads
let configurationManagement;
document.addEventListener('DOMContentLoaded', () => {
    configurationManagement = new ConfigurationManagement();
});