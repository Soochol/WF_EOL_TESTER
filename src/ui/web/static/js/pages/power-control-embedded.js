// Embedded Power Control JavaScript
// Extracted from index.html for better maintainability

// Power Control Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
    // Tab switching for current control panel
    const powerTabButtons = document.querySelectorAll('#power-control .tab-btn');
    const powerTabContents = document.querySelectorAll('#power-control .tab-content');
    
    powerTabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Update button states
            powerTabButtons.forEach(btn => {
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
            powerTabContents.forEach(content => {
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
    
    // Voltage preset buttons
    const presetButtons = document.querySelectorAll('#power-control .preset-btn');
    const voltageInput = document.getElementById('voltage-setpoint');
    
    presetButtons.forEach(button => {
        button.addEventListener('click', function() {
            const voltage = this.getAttribute('data-voltage');
            if (voltageInput) {
                voltageInput.value = voltage;
            }
            
            // Visual feedback
            presetButtons.forEach(btn => {
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
    
    console.log('✅ Power Control Tab functionality initialized - EMBEDDED VERSION');
});

console.log('✅ [EMBEDDED] Power Control functions defined in external file');