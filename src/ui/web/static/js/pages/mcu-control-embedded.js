// Embedded MCU Control JavaScript
// Extracted from index.html for better maintainability

// MCU Control embedded functionality
document.addEventListener('DOMContentLoaded', function() {
    // MCU Control Tab switching functionality for standby operations
    const mcuTabButtons = document.querySelectorAll('#mcu-control .standby-panel .tab-btn');
    const mcuTabContents = document.querySelectorAll('#mcu-control .standby-panel .tab-content');
    
    mcuTabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Update button states
            mcuTabButtons.forEach(btn => {
                if (btn === this) {
                    btn.style.background = '#007bff';
                    btn.style.color = 'white';
                    btn.classList.add('active');
                } else {
                    btn.style.background = 'transparent';
                    btn.style.color = '#6c757d';
                    btn.classList.remove('active');
                }
            });
            
            // Update tab content visibility
            mcuTabContents.forEach(content => {
                if (content.id === targetTab + '-tab') {
                    content.style.display = 'block';
                    content.classList.add('active');
                } else {
                    content.style.display = 'none';
                    content.classList.remove('active');
                }
            });
        });
    });
    
    // MCU Temperature preset buttons
    const mcuPresetButtons = document.querySelectorAll('#mcu-control .preset-btn');
    const operatingTempInput = document.getElementById('operating-temperature');
    
    mcuPresetButtons.forEach(button => {
        button.addEventListener('click', function() {
            const temperature = this.getAttribute('data-temperature');
            if (operatingTempInput) {
                operatingTempInput.value = temperature;
            }
            
            // Visual feedback
            mcuPresetButtons.forEach(btn => {
                btn.style.background = 'transparent';
                btn.style.color = '#007bff';
            });
            this.style.background = '#007bff';
            this.style.color = 'white';
            
            // Reset after 1 second
            setTimeout(() => {
                this.style.background = 'transparent';
                this.style.color = '#007bff';
            }, 1000);
        });
    });
    
    // MCU Heating parameter preview updates
    const updateHeatingPreview = () => {
        const operatingTemp = document.getElementById('heating-operating-temp')?.value || '60.0';
        const standbyTemp = document.getElementById('heating-standby-temp')?.value || '40.0';
        const holdTime = document.getElementById('heating-hold-time')?.value || '10000';
        
        const previewOperating = document.getElementById('preview-operating');
        const previewStandby = document.getElementById('preview-standby');
        const previewHold = document.getElementById('preview-hold');
        
        if (previewOperating) previewOperating.textContent = parseFloat(operatingTemp).toFixed(1);
        if (previewStandby) previewStandby.textContent = parseFloat(standbyTemp).toFixed(1);
        if (previewHold) previewHold.textContent = (parseInt(holdTime) / 1000).toFixed(1);
    };
    
    // Setup heating parameter inputs
    const heatingInputs = ['heating-operating-temp', 'heating-standby-temp', 'heating-hold-time'];
    heatingInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', updateHeatingPreview);
        }
    });
    
    // Initial preview update
    updateHeatingPreview();
    
    console.log('✅ MCU Control embedded functionality initialized - EMBEDDED VERSION');
});

console.log('✅ [EMBEDDED] MCU Control functions defined in external file');