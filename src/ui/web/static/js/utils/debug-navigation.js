// Debug Navigation and Menu Management
// Extracted from index.html for better maintainability

console.log('🔧 Debug script loaded - Adding basic menu functionality');
        
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🔧 DOM loaded, setting up basic menu toggles');
            
            // Basic sidebar toggle functionality
            document.addEventListener('click', function(e) {
                console.log('🔧 Click detected on:', e.target);
                
                // Handle menu toggles
                if (e.target.hasAttribute('data-toggle')) {
                    console.log('🔧 Toggle clicked:', e.target.getAttribute('data-toggle'));
                    e.preventDefault();
                    
                    const menuType = e.target.getAttribute('data-toggle');
                    const menu = document.getElementById(menuType + '-menu');
                    
                    if (menu) {
                        const isHidden = menu.style.display === 'none' || menu.style.display === '';
                        menu.style.display = isHidden ? 'block' : 'none';
                        console.log('🔧 Menu toggled:', menuType, isHidden ? 'shown' : 'hidden');
                        
                        // Add expanded class for styling
                        e.target.classList.toggle('expanded', isHidden);
                    } else {
                        console.error('🔧 Menu not found:', menuType + '-menu');
                    }
                    return;
                }
                
                // Handle page navigation
                if (e.target.hasAttribute('data-page')) {
                    console.log('🔧 Page navigation clicked:', e.target.getAttribute('data-page'));
                    e.preventDefault();
                    
                    const pageName = e.target.getAttribute('data-page');
                    
                    // Hide all pages
                    document.querySelectorAll('.content-page').forEach(page => {
                        page.classList.remove('active');
                        page.style.display = 'none';
                    });
                    
                    // Show selected page or welcome page
                    let targetPage = document.getElementById(pageName);
                    if (!targetPage) {
                        targetPage = document.getElementById('welcome-page');
                        console.log('🔧 Page not found, showing welcome page:', pageName);
                    }
                    
                    if (targetPage) {
                        targetPage.style.display = 'block';
                        targetPage.classList.add('active');
                        console.log('🔧 Page shown:', pageName);
                        
                        // Initialize embedded robot control when robot-control page is shown
                        if (pageName === 'robot-control') {
                            console.log('🚀 [EMBEDDED] Robot Control page detected - Initializing embedded control...');
                            setTimeout(() => {
                                initializeEmbeddedRobotControl();
                            }, 100);
                        }
                    }
                    
                    // Update active nav links
                    document.querySelectorAll('.nav-link').forEach(link => {
                        link.classList.remove('active');
                    });
                    e.target.classList.add('active');
                    
                    return;
                }
            });
            
            // Initialize clock
            function updateClock() {
                const now = new Date();
                const timeString = now.toLocaleTimeString();
                const clockElement = document.getElementById('footer-time');
                if (clockElement) {
                    clockElement.textContent = timeString;
                }
            }
            
            updateClock();
            setInterval(updateClock, 1000);
            
            // Hardware Dashboard functionality
            let hardwareDashboardInterval;
            let autoRefreshEnabled = true;
            
            // Navigation function for hardware dashboard
            window.navigateToPage = function(pageName) {
                console.log('🔧 Navigating to page:', pageName);
                
                // Hide all pages
                document.querySelectorAll('.content-page').forEach(page => {
                    page.classList.remove('active');
                    page.style.display = 'none';
                });
                
                // Show target page
                const targetPage = document.getElementById(pageName);
                if (targetPage) {
                    targetPage.style.display = 'block';
                    targetPage.classList.add('active');
                    console.log('✅ Page shown:', pageName);
                } else {
                    console.error('❌ Page not found:', pageName);
                }
            };
            
            // Hardware control function
            window.controlHardware = async function(hardware, action) {
                console.log('🔧 Hardware control:', hardware, action);
                
                try {
                    let response;
                    const url = `/api/hardware/${hardware}/${action}`;
                    
                    // Show loading state
                    const statusElement = document.getElementById(`${hardware}-status-label`);
                    if (statusElement) {
                        statusElement.textContent = 'Processing...';
                    }
                    
                    switch (action) {
                        case 'connect':
                            response = await fetch(url, { method: 'POST' });
                            break;
                        case 'home':
                        case 'reset':
                        case 'zero':
                        case 'enable':
                            response = await fetch(url, { method: 'POST' });
                            break;
                        default:
                            console.warn('Unknown action:', action);
                            return;
                    }
                    
                    if (response.ok) {
                        const result = await response.json();
                        console.log('✅ Hardware control success:', result);
                        
                        // Show success feedback
                        showNotification(`${hardware} ${action} completed successfully`, 'success');
                        
                        // Refresh hardware status
                        setTimeout(() => updateHardwareStatus(), 1000);
                    } else {
                        const error = await response.text();
                        console.error('❌ Hardware control failed:', error);
                        showNotification(`${hardware} ${action} failed: ${error}`, 'error');
                        
                        // Reset status
                        if (statusElement) {
                            statusElement.textContent = 'Error';
                        }
                    }
                } catch (error) {
                    console.error('❌ Hardware control error:', error);
                    showNotification(`Communication error: ${error.message}`, 'error');
                    
                    // Reset status
                    const statusElement = document.getElementById(`${hardware}-status-label`);
                    if (statusElement) {
                        statusElement.textContent = 'Error';
                    }
                }
            };
            
            // Update hardware status
            async function updateHardwareStatus() {
                try {
                    console.log('🔄 Updating hardware status...');
                    
                    const response = await fetch('/api/hardware/status');
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    console.log('📊 Hardware status received:', data);
                    
                    // Update overall status
                    updateOverallStatus(data);
                    
                    // Update individual hardware cards
                    updateRobotStatus(data.robot || {});
                    updateMCUStatus(data.mcu || {});
                    updatePowerStatus(data.power || {});
                    updateLoadCellStatus(data.loadcell || {});
                    updateDigitalIOStatus(data.digital_io || {});
                    
                    // Update last update time
                    const now = new Date().toLocaleTimeString();
                    const updateElement = document.getElementById('dashboard-last-update');
                    if (updateElement) {
                        updateElement.textContent = now;
                    }
                    
                } catch (error) {
                    console.error('❌ Failed to update hardware status:', error);
                    showNotification('Failed to update hardware status', 'error');
                }
            }
            
            // Update overall status
            function updateOverallStatus(data) {
                const overallStatusDot = document.getElementById('overall-status-dot');
                const overallStatusText = document.getElementById('overall-status-text');
                const activeCountElement = document.getElementById('active-count');
                
                let connectedCount = 0;
                const totalHardware = 5;
                
                // Count connected hardware
                ['robot', 'mcu', 'power', 'loadcell', 'digital_io'].forEach(hw => {
                    if (data[hw] && data[hw].connected) {
                        connectedCount++;
                    }
                });
                
                // Update active count
                if (activeCountElement) {
                    activeCountElement.textContent = connectedCount;
                }
                
                // Update overall status
                let statusText, statusClass;
                if (connectedCount === totalHardware) {
                    statusText = 'All Connected';
                    statusClass = 'online';
                } else if (connectedCount > 0) {
                    statusText = 'Partial Connection';
                    statusClass = 'warning';
                } else {
                    statusText = 'Disconnected';
                    statusClass = 'offline';
                }
                
                if (overallStatusText) {
                    overallStatusText.textContent = statusText;
                }
                if (overallStatusDot) {
                    overallStatusDot.className = `status-dot ${statusClass}`;
                }
            }
            
            // Update individual hardware status functions
            function updateHardwareCard(hardware, data) {
                const statusDot = document.getElementById(`${hardware}-status-dot`);
                const statusLabel = document.getElementById(`${hardware}-status-label`);
                
                if (statusDot && statusLabel) {
                    if (data.connected) {
                        statusDot.className = 'status-dot online';
                        statusLabel.textContent = 'Connected';
                    } else {
                        statusDot.className = 'status-dot offline';
                        statusLabel.textContent = 'Disconnected';
                    }
                }
            }
            
            function updateRobotStatus(data) {
                updateHardwareCard('robot', data);
                
                // Update robot-specific metrics
                const elements = {
                    'robot-position': data.current_position ? `${data.current_position.toFixed(0)} μm` : '-- μm',
                    'robot-servo-status': data.servo_enabled ? 'ON' : 'OFF',
                    'robot-homed-status': data.is_homed ? 'YES' : 'NO',
                    'robot-moving-status': data.is_moving ? 'YES' : 'NO'
                };
                
                Object.entries(elements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value;
                    }
                });
            }
            
            function updateMCUStatus(data) {
                updateHardwareCard('mcu', data);
                
                const elements = {
                    'mcu-temperature': data.current_temperature ? `${data.current_temperature.toFixed(1)} °C` : '-- °C',
                    'mcu-target-temp': data.target_temperature ? `${data.target_temperature.toFixed(1)} °C` : '-- °C',
                    'mcu-fan-speed': data.fan_speed ? `${data.fan_speed} RPM` : '-- RPM',
                    'mcu-test-mode': data.test_mode || '--'
                };
                
                Object.entries(elements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value;
                    }
                });
            }
            
            function updatePowerStatus(data) {
                updateHardwareCard('power', data);
                
                const voltage = data.measured_voltage || data.voltage || 0;
                const current = data.measured_current || data.current || 0;
                const power = (voltage * current).toFixed(1);
                
                const elements = {
                    'power-voltage': `${voltage.toFixed(2)} V`,
                    'power-current': `${current.toFixed(3)} A`,
                    'power-output-status': data.output_enabled ? 'ON' : 'OFF',
                    'power-wattage': `${power} W`
                };
                
                Object.entries(elements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value;
                    }
                });
            }
            
            function updateLoadCellStatus(data) {
                updateHardwareCard('loadcell', data);
                
                const elements = {
                    'loadcell-force': data.force ? `${data.force.toFixed(3)} N` : '-- N',
                    'loadcell-raw': data.raw_value || '--',
                    'loadcell-calibrated': data.calibrated ? 'YES' : 'NO',
                    'loadcell-range': data.range ? `±${data.range} N` : '-- N'
                };
                
                Object.entries(elements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value;
                    }
                });
            }
            
            function updateDigitalIOStatus(data) {
                updateHardwareCard('digital_io', data);
                
                const elements = {
                    'dio-active-inputs': data.active_inputs || '--',
                    'dio-active-outputs': data.active_outputs || '--'
                };
                
                Object.entries(elements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value;
                    }
                });
            }
            
            // Notification system
            function showNotification(message, type = 'info') {
                console.log(`📢 ${type.toUpperCase()}: ${message}`);
                
                // Create notification element
                const notification = document.createElement('div');
                notification.className = `notification ${type}`;
                notification.innerHTML = `
                    <span class="notification-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
                    <span class="notification-message">${message}</span>
                `;
                
                // Add to page
                document.body.appendChild(notification);
                
                // Auto remove after 3 seconds
                setTimeout(() => {
                    notification.remove();
                }, 3000);
            }
            
            // Initialize hardware dashboard when that page is shown
            document.addEventListener('click', function(e) {
                if (e.target.hasAttribute('data-page') && e.target.getAttribute('data-page') === 'hardware-dashboard') {
                    // Start auto refresh
                    console.log('🔄 Starting hardware dashboard auto-refresh');
                    updateHardwareStatus();
                    
                    // Clear existing interval
                    if (hardwareDashboardInterval) {
                        clearInterval(hardwareDashboardInterval);
                    }
                    
                    // Set up auto refresh
                    if (autoRefreshEnabled) {
                        hardwareDashboardInterval = setInterval(updateHardwareStatus, 5000);
                    }
                }
            });
            
            // Dashboard action buttons
            document.addEventListener('click', function(e) {
                if (e.target.id === 'refresh-hardware') {
                    updateHardwareStatus();
                } else if (e.target.id === 'connect-all-hardware') {
                    connectAllHardware();
                } else if (e.target.id === 'emergency-stop-hardware') {
                    emergencyStopAllHardware();
                } else if (e.target.id === 'auto-refresh-toggle') {
                    autoRefreshEnabled = e.target.checked;
                    if (autoRefreshEnabled && document.getElementById('hardware-dashboard').classList.contains('active')) {
                        hardwareDashboardInterval = setInterval(updateHardwareStatus, 5000);
                    } else {
                        clearInterval(hardwareDashboardInterval);
                    }
                }
            });
            
            async function connectAllHardware() {
                console.log('🔌 Connecting all hardware...');
                showNotification('Connecting all hardware...', 'info');
                
                const hardwareList = ['robot', 'mcu', 'power', 'loadcell', 'digital_io'];
                const promises = hardwareList.map(hw => controlHardware(hw, 'connect'));
                
                try {
                    await Promise.all(promises);
                    showNotification('All hardware connection initiated', 'success');
                } catch (error) {
                    showNotification('Some hardware connections failed', 'warning');
                }
            }
            
            async function emergencyStopAllHardware() {
                console.log('🛑 Emergency stop all hardware...');
                showNotification('EMERGENCY STOP ACTIVATED', 'error');
                
                try {
                    const response = await fetch('/api/hardware/emergency-stop', { method: 'POST' });
                    if (response.ok) {
                        showNotification('Emergency stop completed', 'success');
                    } else {
                        showNotification('Emergency stop failed', 'error');
                    }
                } catch (error) {
                    console.error('Emergency stop error:', error);
                    showNotification('Emergency stop communication error', 'error');
                }
            }
            
            console.log('✅ Hardware Dashboard functionality initialized');
        });
console.log("✅ [EMBEDDED] Debug Navigation functions loaded from external file");
