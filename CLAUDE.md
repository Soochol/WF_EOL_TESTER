# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WF EOL Tester is an End-of-Line testing application for wafer fabrication with a simplified Clean Architecture. The project uses Python 3.10+ and implements dependency injection using the `dependency-injector` library.

## Core Commands

### Development Setup
```bash
# Install dependencies using uv (preferred package manager)
uv sync

# Alternative with pip
pip install -e .
```

### Running the Application
```bash
# CLI-only version (main entry point)
python src/main_cli.py

# GUI version
python src/main_gui.py

# Generate configuration files
python src/main_cli.py --generate-config default    # Development config with mock hardware
python src/main_cli.py --generate-config production # Production config with real hardware

# Run with specific configuration
python src/main_cli.py --config config_default.json

# Debug mode
python src/main_cli.py --debug
```

### Code Quality and Testing
```bash
# Format code
black src/ --line-length 100

# Sort imports
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
pylint src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## Architecture Overview

This project uses a simplified Clean Architecture pattern with dependency injection:

### Directory Structure
- `src/application/` - Application layer with use cases, services, and interfaces
  - `containers/` - Dependency injection containers  
  - `interfaces/` - Abstract interfaces for hardware, configuration, and repositories
  - `services/` - Core business services and hardware facade
  - `use_cases/` - Business logic use cases (EOL tests, robot operations)
- `src/domain/` - Domain entities, value objects, and business rules
- `src/infrastructure/` - Infrastructure implementations (hardware adapters, repositories)
- `src/driver/` - Hardware driver implementations
- `src/ui/` - User interface (CLI and GUI implementations)

### Key Components

#### Dependency Injection Container
The application uses `ApplicationContainer` (src/application/containers/application_container.py) to manage all dependencies. This is the central configuration point for the entire application.

#### Hardware Services
Hardware is abstracted through interfaces in `src/application/interfaces/hardware/`:
- `LoadcellService` - Force measurement hardware
- `MCUService` - Microcontroller operations  
- `PowerService` - Power supply control
- `RobotService` - Robot arm operations
- `DigitalIOService` - Digital I/O operations

#### Test Use Cases
Main testing functionality is in `src/application/use_cases/`:
- `EOLForceTestUseCase` - End-of-line force testing
- `HeatingCoolingTimeTestUseCase` - Temperature cycling tests
- `SimpleMCUTestUseCase` - MCU communication tests
- `RobotHomeUseCase` - Robot homing operations

## Configuration

The application supports both development (mock hardware) and production configurations:

### Mock Hardware (Development)
```json
{
  "hardware": {
    "loadcell": {"type": "mock"},
    "power_supply": {"type": "mock"}
  }
}
```

### Real Hardware (Production)
```json
{
  "hardware": {
    "loadcell": {
      "type": "bs205",
      "connection": {"port": "COM1", "baudrate": 9600}
    },
    "power_supply": {
      "type": "oda", 
      "connection": {"host": "192.168.1.10", "port": 8080}
    }
  }
}
```

## Development Guidelines

### Code Style
- Line length: 100 characters (configured in pyproject.toml)
- Use Black for formatting with isort for import organization
- Follow the configured import order: stdlib → third-party → first-party → local

### Testing Strategy  
- Tests should be in a `tests/` directory (not yet created)
- Use pytest with async support (`pytest-asyncio`)
- Mock hardware services for unit testing
- Use the existing mock implementations in development configs

### Adding New Hardware
1. Define interface in `src/application/interfaces/hardware/`
2. Implement in `src/infrastructure/adapters/hardware/`
3. Add to `HardwareFactory` in `src/infrastructure/factories/hardware_factory.py`
4. Update `ApplicationContainer` dependency injection configuration

### Adding New Use Cases
1. Create new directory in `src/application/use_cases/`
2. Implement use case following existing patterns
3. Register in `ApplicationContainer`
4. Add CLI/GUI integration points

## Key Files to Understand

- `src/main_cli.py` - CLI entry point with dependency injection setup
- `src/application/containers/application_container.py` - Dependency injection configuration
- `src/application/services/hardware_facade/hardware_service_facade.py` - Hardware abstraction layer
- `pyproject.toml` - Project configuration, dependencies, and tool settings
- `CLI_USAGE.md` - Detailed CLI usage instructions