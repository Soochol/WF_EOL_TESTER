// API Test Page JavaScript
// Extracted from index.html for better maintainability

document.addEventListener('DOMContentLoaded', function() {
    // Quick API test functionality
    document.getElementById('test-api-health')?.addEventListener('click', async function() {
        const output = document.getElementById('test-output');
        const result = document.getElementById('test-result');
        
        result.textContent = 'Testing...';
        result.style.color = '#ffc107';
        
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            output.innerHTML = `<strong>GET /api/health</strong>\nStatus: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}`;
            result.textContent = '✅ Success';
            result.style.color = '#28a745';
        } catch (error) {
            output.innerHTML = `<strong>GET /api/health</strong>\nError: ${error.message}`;
            result.textContent = '❌ Failed';
            result.style.color = '#dc3545';
        }
    });
    
    document.getElementById('test-hardware-status')?.addEventListener('click', async function() {
        const output = document.getElementById('test-output');
        const result = document.getElementById('test-result');
        
        result.textContent = 'Testing...';
        result.style.color = '#ffc107';
        
        try {
            const response = await fetch('/api/hardware/status');
            const data = await response.json();
            
            output.innerHTML = `<strong>GET /api/hardware/status</strong>\nStatus: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}`;
            result.textContent = '✅ Success';
            result.style.color = '#28a745';
        } catch (error) {
            output.innerHTML = `<strong>GET /api/hardware/status</strong>\nError: ${error.message}`;
            result.textContent = '❌ Failed';
            result.style.color = '#dc3545';
        }
    });
    
    console.log('✅ API Status page initialized');
});

console.log('✅ [EMBEDDED] API Test Page functions defined in external file');