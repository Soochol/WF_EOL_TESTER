/**
 * Hardware Configuration Editor
 * 
 * Provides interface for editing hardware configuration including:
 * - Robot settings (IRQ, axis, motion parameters)
 * - LoadCell configuration (serial communication)
 * - MCU settings (serial communication)
 * - Power supply configuration (TCP/IP)
 * - Digital I/O mappings
 */

class HardwareConfigurationEditor extends ConfigurationEditor {
    constructor() {
        super('hardware-config-container', '/api/config/hardware-config', 'hardware_config');
    }

    render() {
        if (!this.container || !this.currentData) return;

        this.container.innerHTML = `
            <div class="config-editor-header">
                <h2>Hardware Configuration Editor</h2>
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
                    <li class="tab-item active"><a href="#robot-tab" data-tab="robot">Robot</a></li>
                    <li class="tab-item"><a href="#loadcell-tab" data-tab="loadcell">LoadCell</a></li>
                    <li class="tab-item"><a href="#mcu-tab" data-tab="mcu">MCU</a></li>
                    <li class="tab-item"><a href="#power-tab" data-tab="power">Power Supply</a></li>
                    <li class="tab-item"><a href="#digital-io-tab" data-tab="digital-io">Digital I/O</a></li>
                </ul>

                <div class="tab-content">
                    <div id="robot-tab" class="tab-pane active">
                        ${this.renderRobotSection()}
                    </div>
                    <div id="loadcell-tab" class="tab-pane">
                        ${this.renderLoadCellSection()}
                    </div>
                    <div id="mcu-tab" class="tab-pane">
                        ${this.renderMCUSection()}
                    </div>
                    <div id="power-tab" class="tab-pane">
                        ${this.renderPowerSection()}
                    </div>
                    <div id="digital-io-tab" class="tab-pane">
                        ${this.renderDigitalIOSection()}
                    </div>
                </div>
            </div>
        `;

        this.setupTabNavigation();
        this.setupFormEventListeners();
    }

    renderRobotSection() {
        const robot = this.currentData.hardware_config?.robot || {};
        return `
            <div class="form-section">
                <h3>Robot Configuration</h3>
                <div class="alert alert-info">
                    <strong>Info:</strong> Configure the robot controller settings for motion control.
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">IRQ Number</label>
                        <input type="number" value="${robot.irq_no || 7}" 
                               data-path="hardware_config.robot.irq_no" class="form-control" min="0" max="15" required>
                        <div class="form-help">Interrupt request number for the robot controller</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Axis ID</label>
                        <input type="number" value="${robot.axis_id || 0}" 
                               data-path="hardware_config.robot.axis_id" class="form-control" min="0" max="31" required>
                        <div class="form-help">Axis identifier for the robot motion</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Velocity (mm/s)</label>
                        <input type="number" step="0.1" value="${robot.velocity || 200.0}" 
                               data-path="hardware_config.robot.velocity" class="form-control" min="0" required>
                        <div class="form-help">Default robot velocity</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Acceleration (mm/s²)</label>
                        <input type="number" step="0.1" value="${robot.acceleration || 1000.0}" 
                               data-path="hardware_config.robot.acceleration" class="form-control" min="0" required>
                        <div class="form-help">Robot acceleration rate</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Deceleration (mm/s²)</label>
                        <input type="number" step="0.1" value="${robot.deceleration || 1000.0}" 
                               data-path="hardware_config.robot.deceleration" class="form-control" min="0" required>
                        <div class="form-help">Robot deceleration rate</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderLoadCellSection() {
        const loadcell = this.currentData.hardware_config?.loadcell || {};
        return `
            <div class="form-section">
                <h3>LoadCell Configuration</h3>
                <div class="alert alert-info">
                    <strong>Info:</strong> Configure the load cell serial communication settings.
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Serial Port</label>
                        <input type="text" value="${loadcell.port || 'COM8'}" 
                               data-path="hardware_config.loadcell.port" class="form-control" required>
                        <div class="form-help">Serial port for load cell communication (e.g., COM8, /dev/ttyUSB0)</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Baud Rate</label>
                        <select data-path="hardware_config.loadcell.baudrate" class="form-control" required>
                            <option value="9600" ${(loadcell.baudrate || 9600) == 9600 ? 'selected' : ''}>9600</option>
                            <option value="19200" ${loadcell.baudrate == 19200 ? 'selected' : ''}>19200</option>
                            <option value="38400" ${loadcell.baudrate == 38400 ? 'selected' : ''}>38400</option>
                            <option value="57600" ${loadcell.baudrate == 57600 ? 'selected' : ''}>57600</option>
                            <option value="115200" ${loadcell.baudrate == 115200 ? 'selected' : ''}>115200</option>
                        </select>
                        <div class="form-help">Communication baud rate</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Timeout (seconds)</label>
                        <input type="number" step="0.1" value="${loadcell.timeout || 1.0}" 
                               data-path="hardware_config.loadcell.timeout" class="form-control" min="0.1" required>
                        <div class="form-help">Communication timeout</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Byte Size</label>
                        <select data-path="hardware_config.loadcell.bytesize" class="form-control" required>
                            <option value="5" ${(loadcell.bytesize || 8) == 5 ? 'selected' : ''}>5</option>
                            <option value="6" ${loadcell.bytesize == 6 ? 'selected' : ''}>6</option>
                            <option value="7" ${loadcell.bytesize == 7 ? 'selected' : ''}>7</option>
                            <option value="8" ${(loadcell.bytesize || 8) == 8 ? 'selected' : ''}>8</option>
                        </select>
                        <div class="form-help">Data bits per byte</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Stop Bits</label>
                        <select data-path="hardware_config.loadcell.stopbits" class="form-control" required>
                            <option value="1" ${(loadcell.stopbits || 1) == 1 ? 'selected' : ''}>1</option>
                            <option value="1.5" ${loadcell.stopbits == 1.5 ? 'selected' : ''}>1.5</option>
                            <option value="2" ${loadcell.stopbits == 2 ? 'selected' : ''}>2</option>
                        </select>
                        <div class="form-help">Number of stop bits</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Parity</label>
                        <select data-path="hardware_config.loadcell.parity" class="form-control" required>
                            <option value="none" ${(loadcell.parity || 'even') === 'none' ? 'selected' : ''}>None</option>
                            <option value="even" ${(loadcell.parity || 'even') === 'even' ? 'selected' : ''}>Even</option>
                            <option value="odd" ${loadcell.parity === 'odd' ? 'selected' : ''}>Odd</option>
                            <option value="mark" ${loadcell.parity === 'mark' ? 'selected' : ''}>Mark</option>
                            <option value="space" ${loadcell.parity === 'space' ? 'selected' : ''}>Space</option>
                        </select>
                        <div class="form-help">Parity checking method</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Indicator ID</label>
                        <input type="number" value="${loadcell.indicator_id || 0}" 
                               data-path="hardware_config.loadcell.indicator_id" class="form-control" min="0" required>
                        <div class="form-help">Load cell indicator device ID</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderMCUSection() {
        const mcu = this.currentData.hardware_config?.mcu || {};
        return `
            <div class="form-section">
                <h3>MCU Configuration</h3>
                <div class="alert alert-info">
                    <strong>Info:</strong> Configure the microcontroller unit communication settings.
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Serial Port</label>
                        <input type="text" value="${mcu.port || 'COM4'}" 
                               data-path="hardware_config.mcu.port" class="form-control" required>
                        <div class="form-help">Serial port for MCU communication (e.g., COM4, /dev/ttyUSB1)</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Baud Rate</label>
                        <select data-path="hardware_config.mcu.baudrate" class="form-control" required>
                            <option value="9600" ${(mcu.baudrate || 115200) == 9600 ? 'selected' : ''}>9600</option>
                            <option value="19200" ${mcu.baudrate == 19200 ? 'selected' : ''}>19200</option>
                            <option value="38400" ${mcu.baudrate == 38400 ? 'selected' : ''}>38400</option>
                            <option value="57600" ${mcu.baudrate == 57600 ? 'selected' : ''}>57600</option>
                            <option value="115200" ${(mcu.baudrate || 115200) == 115200 ? 'selected' : ''}>115200</option>
                            <option value="230400" ${mcu.baudrate == 230400 ? 'selected' : ''}>230400</option>
                        </select>
                        <div class="form-help">Communication baud rate</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Timeout (seconds)</label>
                        <input type="number" step="0.1" value="${mcu.timeout || 60.0}" 
                               data-path="hardware_config.mcu.timeout" class="form-control" min="0.1" required>
                        <div class="form-help">Communication timeout</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Byte Size</label>
                        <select data-path="hardware_config.mcu.bytesize" class="form-control" required>
                            <option value="5" ${(mcu.bytesize || 8) == 5 ? 'selected' : ''}>5</option>
                            <option value="6" ${mcu.bytesize == 6 ? 'selected' : ''}>6</option>
                            <option value="7" ${mcu.bytesize == 7 ? 'selected' : ''}>7</option>
                            <option value="8" ${(mcu.bytesize || 8) == 8 ? 'selected' : ''}>8</option>
                        </select>
                        <div class="form-help">Data bits per byte</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Stop Bits</label>
                        <select data-path="hardware_config.mcu.stopbits" class="form-control" required>
                            <option value="1" ${(mcu.stopbits || 1) == 1 ? 'selected' : ''}>1</option>
                            <option value="1.5" ${mcu.stopbits == 1.5 ? 'selected' : ''}>1.5</option>
                            <option value="2" ${mcu.stopbits == 2 ? 'selected' : ''}>2</option>
                        </select>
                        <div class="form-help">Number of stop bits</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Parity</label>
                        <select data-path="hardware_config.mcu.parity" class="form-control">
                            <option value="null" ${(mcu.parity === null || mcu.parity === 'null') ? 'selected' : ''}>None</option>
                            <option value="even" ${mcu.parity === 'even' ? 'selected' : ''}>Even</option>
                            <option value="odd" ${mcu.parity === 'odd' ? 'selected' : ''}>Odd</option>
                            <option value="mark" ${mcu.parity === 'mark' ? 'selected' : ''}>Mark</option>
                            <option value="space" ${mcu.parity === 'space' ? 'selected' : ''}>Space</option>
                        </select>
                        <div class="form-help">Parity checking method (null for none)</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderPowerSection() {
        const power = this.currentData.hardware_config?.power || {};
        return `
            <div class="form-section">
                <h3>Power Supply Configuration</h3>
                <div class="alert alert-info">
                    <strong>Info:</strong> Configure the power supply TCP/IP communication settings.
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Host Address</label>
                        <input type="text" value="${power.host || '192.168.1.100'}" 
                               data-path="hardware_config.power.host" class="form-control" required
                               pattern="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$">
                        <div class="form-help">IP address of the power supply</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Port</label>
                        <input type="number" value="${power.port || 8080}" 
                               data-path="hardware_config.power.port" class="form-control" min="1" max="65535" required>
                        <div class="form-help">TCP port for power supply communication</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Timeout (seconds)</label>
                        <input type="number" step="0.1" value="${power.timeout || 5.0}" 
                               data-path="hardware_config.power.timeout" class="form-control" min="0.1" required>
                        <div class="form-help">Connection timeout</div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Channel</label>
                        <input type="number" value="${power.channel || 1}" 
                               data-path="hardware_config.power.channel" class="form-control" min="1" max="8" required>
                        <div class="form-help">Power supply output channel</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderDigitalIOSection() {
        const digital_io = this.currentData.hardware_config?.digital_io || {};
        return `
            <div class="form-section">
                <h3>Digital I/O Configuration</h3>
                <div class="alert alert-info">
                    <strong>Info:</strong> Configure the digital input/output pin mappings for buttons and indicators.
                </div>
                
                <div class="subsection">
                    <h4>Input Buttons</h4>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Operator Start Button Left</label>
                            <input type="number" value="${digital_io.operator_start_button_left || 1}" 
                                   data-path="hardware_config.digital_io.operator_start_button_left" 
                                   class="form-control" min="0" max="31" required>
                            <div class="form-help">Digital input pin for left start button</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Operator Start Button Right</label>
                            <input type="number" value="${digital_io.operator_start_button_right || 2}" 
                                   data-path="hardware_config.digital_io.operator_start_button_right" 
                                   class="form-control" min="0" max="31" required>
                            <div class="form-help">Digital input pin for right start button</div>
                        </div>
                    </div>
                </div>

                <div class="subsection">
                    <h4>Output Indicators</h4>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Tower Lamp Red</label>
                            <input type="number" value="${digital_io.tower_lamp_red || 4}" 
                                   data-path="hardware_config.digital_io.tower_lamp_red" 
                                   class="form-control" min="0" max="31" required>
                            <div class="form-help">Digital output pin for red tower lamp</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Tower Lamp Yellow</label>
                            <input type="number" value="${digital_io.tower_lamp_yellow || 5}" 
                                   data-path="hardware_config.digital_io.tower_lamp_yellow" 
                                   class="form-control" min="0" max="31" required>
                            <div class="form-help">Digital output pin for yellow tower lamp</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Tower Lamp Green</label>
                            <input type="number" value="${digital_io.tower_lamp_green || 6}" 
                                   data-path="hardware_config.digital_io.tower_lamp_green" 
                                   class="form-control" min="0" max="31" required>
                            <div class="form-help">Digital output pin for green tower lamp</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Beep Output</label>
                            <input type="number" value="${digital_io.beep || 7}" 
                                   data-path="hardware_config.digital_io.beep" 
                                   class="form-control" min="0" max="31" required>
                            <div class="form-help">Digital output pin for beep sound</div>
                        </div>
                    </div>
                </div>

                <div class="subsection">
                    <h4>Pin Usage Summary</h4>
                    <div class="pin-usage-table">
                        <table class="usage-table">
                            <thead>
                                <tr>
                                    <th>Pin</th>
                                    <th>Function</th>
                                    <th>Type</th>
                                </tr>
                            </thead>
                            <tbody id="pin-usage-tbody">
                                <!-- Populated by JavaScript -->
                            </tbody>
                        </table>
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
                    
                    // Update pin usage table when Digital I/O tab is shown
                    if (link.getAttribute('href') === '#digital-io-tab') {
                        this.updatePinUsageTable();
                    }
                }
            });
        });
    }

    setupFormEventListeners() {
        // Set up input change listeners
        this.container.querySelectorAll('input[data-path], select[data-path]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateField(e.target.dataset.path, e.target.value);
                
                // Update pin usage table if it's a digital I/O field
                if (e.target.dataset.path.includes('digital_io')) {
                    this.updatePinUsageTable();
                }
            });
        });
    }

    updatePinUsageTable() {
        const tbody = document.getElementById('pin-usage-tbody');
        if (!tbody) return;

        const digital_io = this.currentData.hardware_config?.digital_io || {};
        const pinMappings = [
            { pin: digital_io.operator_start_button_left || 1, function: 'Operator Start Button Left', type: 'Input' },
            { pin: digital_io.operator_start_button_right || 2, function: 'Operator Start Button Right', type: 'Input' },
            { pin: digital_io.tower_lamp_red || 4, function: 'Tower Lamp Red', type: 'Output' },
            { pin: digital_io.tower_lamp_yellow || 5, function: 'Tower Lamp Yellow', type: 'Output' },
            { pin: digital_io.tower_lamp_green || 6, function: 'Tower Lamp Green', type: 'Output' },
            { pin: digital_io.beep || 7, function: 'Beep Output', type: 'Output' }
        ];

        // Sort by pin number
        pinMappings.sort((a, b) => a.pin - b.pin);

        // Check for conflicts
        const pinCounts = {};
        pinMappings.forEach(mapping => {
            pinCounts[mapping.pin] = (pinCounts[mapping.pin] || 0) + 1;
        });

        tbody.innerHTML = pinMappings.map(mapping => {
            const hasConflict = pinCounts[mapping.pin] > 1;
            const rowClass = hasConflict ? 'pin-conflict' : '';
            return `
                <tr class="${rowClass}">
                    <td>${mapping.pin}${hasConflict ? ' ⚠' : ''}</td>
                    <td>${mapping.function}</td>
                    <td>${mapping.type}</td>
                </tr>
            `;
        }).join('');
    }

    renderArraySection(path) {
        // Hardware Configuration doesn't use arrays, so this is a no-op
        return;
    }
}

// Initialize the editor when the page loads
let hardwareConfigurationEditor;
document.addEventListener('DOMContentLoaded', () => {
    hardwareConfigurationEditor = new HardwareConfigurationEditor();
});