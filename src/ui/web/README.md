# WF EOL Tester Web Interface

This directory contains the web-based user interface for the WF EOL Tester application, providing a modern browser-based interface for test execution, hardware control, and result analysis.

## Directory Structure

```
src/ui/web/
├── index.html                 # Main HTML entry point
├── static/                    # Static web assets
│   ├── css/                   # Stylesheets
│   │   ├── main.css          # Main application styles
│   │   ├── components.css    # UI component styles
│   │   └── charts.css        # Chart and visualization styles
│   ├── js/                   # JavaScript modules
│   │   ├── main.js           # Main application entry point
│   │   ├── config/           # Configuration modules
│   │   ├── services/         # API and WebSocket services
│   │   ├── components/       # UI components
│   │   ├── modules/          # Feature modules
│   │   └── utils/           # Utility functions
│   ├── libs/                 # Third-party libraries
│   └── assets/              # Images, fonts, icons
├── templates/                # HTML templates
│   ├── layouts/             # Base layouts
│   ├── components/          # Reusable template components
│   └── pages/               # Page templates
├── api/                      # FastAPI backend
│   ├── main.py              # FastAPI application
│   ├── routes/              # API route definitions
│   ├── controllers/         # Business logic controllers
│   ├── models/              # Pydantic models
│   ├── middleware/          # Custom middleware
│   └── services/            # Backend services
└── src/                      # Additional source files
    ├── components/          # Reusable components
    ├── services/            # Service classes
    ├── utils/               # Utility modules
    ├── config/              # Configuration management
    ├── models/              # Data models
    └── types/               # Type definitions
```

## Features

### Core Functionality
- **Real-time Test Monitoring**: Live visualization of test execution and results
- **Hardware Control**: Browser-based interface for hardware components
- **Test Management**: Start, stop, and configure EOL tests
- **Result Analysis**: Comprehensive test result viewing and analysis
- **Data Export**: Export test data in multiple formats (CSV, JSON, Excel)

### Technical Features
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: WebSocket-based live data streaming
- **Interactive Charts**: Dynamic data visualization using Chart.js
- **RESTful API**: FastAPI-based backend with OpenAPI documentation
- **Modern JavaScript**: ES6+ modules with async/await patterns
- **Type Safety**: Pydantic models for data validation

## Installation

1. **Install Python Dependencies**:
   ```bash
   cd src/ui/web
   pip install -r requirements.txt
   ```

2. **Install JavaScript Dependencies** (if using npm):
   ```bash
   # Chart.js and other libraries can be installed via CDN or npm
   npm install chart.js
   ```

3. **Configure Environment**:
   ```bash
   # Copy and configure environment variables
   cp .env.example .env
   ```

## Running the Application

### Development Server
```bash
# Run the FastAPI development server
python api/main.py

# Or using uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
# Using uvicorn with production settings
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

The web interface will be available at `http://localhost:8000`

## API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Architecture

### Frontend Architecture
- **Modular JavaScript**: ES6 modules for maintainable code organization
- **Component-Based UI**: Reusable components with clear interfaces
- **Event-Driven**: Custom event system for component communication
- **Real-time Data**: WebSocket integration for live updates

### Backend Architecture
- **FastAPI Framework**: Modern Python web framework with automatic API docs
- **Dependency Injection**: Clean separation of concerns
- **Async/Await**: Non-blocking request handling
- **Pydantic Models**: Type-safe data validation and serialization

### Integration
- **Hardware Service Integration**: Direct connection to existing hardware services
- **Test Execution Integration**: Seamless integration with EOL test workflows
- **Configuration Management**: Unified configuration with existing CLI interface

## Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use ES6+ features, consistent naming conventions
- **CSS**: BEM methodology for class naming
- **HTML**: Semantic markup with accessibility considerations

### Testing
- **Backend**: pytest for API testing
- **Frontend**: Jest for JavaScript testing
- **Integration**: End-to-end testing with Playwright

### Performance
- **Optimize Bundle Size**: Use code splitting for JavaScript modules
- **Caching**: Implement appropriate caching strategies
- **Real-time Optimization**: Throttle high-frequency updates
- **Database Queries**: Optimize database interactions

## Security Considerations

- **Input Validation**: All inputs validated using Pydantic models
- **Authentication**: JWT-based authentication (if required)
- **CORS**: Properly configured Cross-Origin Resource Sharing
- **HTTPS**: Use HTTPS in production environments
- **Rate Limiting**: Protect API endpoints from abuse

## Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **JavaScript Features**: ES6+ modules, async/await, WebSockets
- **CSS Features**: Grid, Flexbox, CSS Custom Properties

## Contributing

1. Follow the established directory structure
2. Implement proper error handling
3. Add appropriate logging and monitoring
4. Write tests for new functionality
5. Update documentation as needed
6. Follow the coding standards and guidelines