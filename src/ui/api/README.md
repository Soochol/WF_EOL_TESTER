# WF EOL Tester - FastAPI Web Server

FastAPI-based web server providing REST API endpoints and WebSocket support for the WF EOL Tester web interface.

## Features

### REST API Endpoints

#### Hardware Control (`/api/hardware/*`)
- **GET** `/api/hardware/status` - Get overall hardware connection status
- **POST** `/api/hardware/connect` - Connect/disconnect hardware components
- **POST** `/api/hardware/initialize` - Initialize hardware with configuration
- **GET/POST** `/api/hardware/robot/*` - Robot control and status
- **GET/POST** `/api/hardware/power/*` - Power supply control
- **GET/POST** `/api/hardware/mcu/*` - MCU control and monitoring
- **GET/POST** `/api/hardware/loadcell/*` - Load cell operations
- **GET/POST** `/api/hardware/digital-io/*` - Digital I/O control

#### Test Execution (`/api/tests/*`)
- **POST** `/api/tests/eol-force-test` - Start EOL force test execution
- **GET** `/api/tests/eol-force-test/{test_id}/status` - Get test status
- **GET** `/api/tests/eol-force-test/{test_id}/progress` - Get detailed test progress
- **POST** `/api/tests/eol-force-test/{test_id}/cancel` - Cancel running test
- **POST** `/api/tests/robot-home` - Execute robot homing operation
- **GET** `/api/tests/active` - List active tests
- **DELETE** `/api/tests/cleanup` - Clean up completed test records

#### Configuration Management (`/api/config/*`)
- **GET** `/api/config/profiles` - List available configuration profiles
- **GET** `/api/config/profiles/usage` - Get profile usage information
- **GET** `/api/config/profiles/{profile_name}` - Get specific profile configuration
- **GET** `/api/config/profiles/{profile_name}/validate` - Validate profile configuration
- **GET** `/api/config/hardware` - Get hardware configuration
- **GET** `/api/config/dut-defaults` - Get DUT default values
- **POST** `/api/config/profiles/clear-preferences` - Clear profile preferences

#### System Status (`/api/status/*`)
- **GET** `/api/status/health` - Basic health check
- **GET** `/api/status/system` - Detailed system status (CPU, memory, disk)
- **GET** `/api/status/hardware` - Hardware system status
- **GET** `/api/status/configuration` - Configuration system status
- **GET** `/api/status/services` - Application services status
- **GET** `/api/status/comprehensive` - Complete system status

### WebSocket Endpoints

#### Real-time Communication (`/ws/*`)
- **WS** `/ws/digital-input` - Real-time Digital I/O monitoring (32 inputs)
- **WS** `/ws/test-logs` - EOL test execution log streaming
- **WS** `/ws/system-status` - System status updates

## Architecture Integration

### Clean Architecture Compliance
- **Application Layer**: Uses existing `HardwareServiceFacade`, `ConfigurationService`
- **Use Cases**: Integrates `EOLForceTestUseCase` and `RobotHomeUseCase`
- **Domain Layer**: Works with domain entities and value objects
- **Infrastructure**: No direct access - all through application services

### Dependency Injection
- Centralized container in `dependencies.py`
- Singleton pattern for shared services
- Proper resource cleanup on shutdown

### Error Handling
- Domain-specific exception mapping
- Structured error responses
- Centralized logging with Loguru

## Running the Server

### Development
```bash
# From project root
python run_web_server.py

# Or directly with uvicorn
uvicorn ui.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Set environment variables
export WF_HOST=0.0.0.0
export WF_PORT=8000
export WF_RELOAD=false

# Run server
python run_web_server.py
```

### Environment Variables
- `WF_HOST`: Server host (default: 0.0.0.0)
- `WF_PORT`: Server port (default: 8000)
- `WF_RELOAD`: Enable auto-reload in development (default: true)

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Web Interface

The server serves the web interface at the root URL:
- **Main Interface**: http://localhost:8000/
- **Static Files**: http://localhost:8000/static/

## WebSocket Usage

### JavaScript Client Example
```javascript
// Digital input monitoring
const ws = new WebSocket('ws://localhost:8000/ws/digital-input');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'digital_input') {
        console.log('Digital inputs:', data.inputs);
        console.log('Changed channels:', data.changed_channels);
    }
};

// Test log monitoring
const testWs = new WebSocket('ws://localhost:8000/ws/test-logs');
testWs.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'test_log') {
        console.log(`[${data.level}] ${data.message}`);
    }
};
```

## Security Considerations

- CORS is configured for development (allow all origins)
- No authentication implemented (add as needed)
- Input validation via Pydantic models
- Error messages don't expose internal details in production

## Performance Features

- Async/await for all I/O operations
- WebSocket connection pooling
- Background tasks for periodic monitoring
- Proper resource cleanup
- Structured logging for monitoring

## Dependencies

- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server implementation
- **Pydantic**: Data validation and serialization
- **psutil**: System resource monitoring
- **Loguru**: Structured logging

All dependencies are included in the main `pyproject.toml`.
