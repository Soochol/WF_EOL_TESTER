# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WF EOL Tester is an End-of-Line testing application for wafer fabrication with a simplified Clean Architecture. The project uses Python 3.10+ with modern tooling including PySide6 for GUI, dependency injection for modularity, and comprehensive hardware abstraction for both real and mock hardware implementations.

## Core Commands

### Development Setup
```bash
# Install dependencies using uv (preferred package manager)
uv sync

# Platform detection and diagnosis (if issues occur)
python src/utils/platform_detection.py

# Alternative with pip
pip install -e .
```

### Running the Application

#### GUI Application (Multiple Options)
```bash
# Option 1: Standard command line (shows both CMD and GUI windows)
uv run src/main_gui.py

# Option 2: GUI-only launcher (Windows - minimal console visibility)
./run_gui.bat

# Option 3: Silent GUI launcher (Windows - completely hidden console)
./run_gui_silent.vbs
# or double-click: run_gui_silent.vbs

# Option 4: Create desktop shortcut for easy access
./create_desktop_shortcut.bat
```

#### CLI Application
```bash
# CLI-only version (main entry point)
uv run src/main_cli.py
# or: python src/main_cli.py

# Generate configuration files
uv run src/main_cli.py --generate-config default    # Development config with mock hardware
uv run src/main_cli.py --generate-config production # Production config with real hardware

# Run with specific configuration
uv run src/main_cli.py --config config_default.json

# Debug mode
uv run src/main_cli.py --debug
```

### Code Quality and Testing
```bash
# Format code
black src/ --line-length 100

# Sort imports
isort src/

# Type checking
mypy src/

# Linting and Error Checking (multiple options available)
ruff check src/          # Modern fast linter (preferred for speed)
flake8 src/             # Traditional linter with extensive plugin ecosystem
pylint src/             # Comprehensive static analysis with detailed reports
pylint src/ --output-format=json > pylint_report.json  # Generate JSON report

# IDE Language Servers and Real-time Error Checking
# Pylance (VS Code) - Install Python extension for automatic setup
# PyCharm/IntelliJ - Built-in Python support with real-time analysis
# vim/neovim - Use python-lsp-server or pylsp with pylint integration

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# All-in-one development tools (using uv)
uv run black src/
uv run isort src/
uv run mypy src/
uv run ruff check src/
uv run pylint src/

# Complete code quality pipeline
uv run black src/ && uv run isort src/ && uv run mypy src/ && uv run ruff check src/ && uv run pylint src/

# Troubleshooting PySide6 issues
uv cache clean          # Clear package cache
uv sync                 # Reinstall packages
uv sync --reinstall     # Force complete reinstall
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
  - `ajinextek/` - Ajinextek robot controller drivers
  - `serial/` - Serial communication drivers
  - `tcp/` - TCP/IP communication drivers
- `src/ui/` - User interface implementations
  - `cli/` - Command-line interface with rich presentation
  - `gui/` - GUI implementation using PySide6
  - `components/` - Shared UI components
- `src/utils/` - Utility functions and helpers

### Key Components

#### Dependency Injection Container
The application uses `SimpleReloadableContainer` (src/application/containers/simple_reloadable_container.py) to manage all dependencies with hot-reload capabilities. This is the central configuration point for the entire application, featuring:

- **Hot-reload functionality**: Settings changes are applied immediately without restart
- **Layered architecture**: Separates configuration, connection, and service management
- **Connection preservation**: Maintains active hardware connections during configuration changes
- **Intelligent reload**: Only reloads components affected by configuration changes

#### Hardware Services
Hardware is abstracted through interfaces in `src/application/interfaces/hardware/`:
- `LoadcellService` - Force measurement hardware
- `MCUService` - Microcontroller operations
- `PowerService` - Power supply control
- `RobotService` - Robot arm operations
- `DigitalIOService` - Digital I/O operations

#### Hardware Implementations
Real hardware implementations are in `src/infrastructure/implementation/hardware/`:
- **Loadcell**: BS205 strain gauge amplifier, Mock implementation
- **MCU**: LMA microcontroller, Mock implementation
- **Power Supply**: ODA power supply, Mock implementation
- **Robot**: Ajinextek robot controller, Mock implementation
- **Digital I/O**: Ajinextek digital I/O board, Mock implementation

Each hardware type supports both production hardware and mock implementations for development/testing.

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
    "power_supply": {"type": "mock"},
    "mcu": {"type": "mock"},
    "robot": {"type": "mock"},
    "digital_io": {"type": "mock"}
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
    },
    "mcu": {
      "type": "lma",
      "connection": {"port": "COM2", "baudrate": 115200}
    },
    "robot": {
      "type": "ajinextek",
      "connection": {"library_path": "./driver/ajinextek/AXL(Library)"}
    },
    "digital_io": {
      "type": "ajinextek",
      "connection": {"board_id": 0}
    }
  }
}
```

## Development Guidelines

### Code Style
- Line length: 100 characters (configured in pyproject.toml)
- Use Black for formatting with isort for import organization
- Follow the configured import order: stdlib → third-party → first-party → local
- Use `ruff` for fast linting and additional code quality checks
- Use `pylint` for comprehensive static analysis and code quality metrics
- Configure IDE with Pylance (VS Code) or PyCharm for real-time error detection

### Error Checking and Code Quality
- **Primary Linter**: `ruff` for fast, modern Python linting
- **Comprehensive Analysis**: `pylint` for detailed code quality reports and metrics
- **Type Checking**: `mypy` for static type analysis
- **IDE Integration**: Use Pylance (VS Code) or built-in PyCharm analysis for real-time feedback
- **Pre-commit Hooks**: Set up automated quality checks before commits
- **CI/CD Integration**: Include linting and type checking in continuous integration pipelines

### Package Management
- **Primary**: Use `uv` for fast dependency management and virtual environment
- **Alternative**: Traditional pip for compatibility
- Development dependencies are configured in `[dependency-groups]` section

### Platform Compatibility
- **Windows**: Windows 10 (1809+) and Windows 11 supported
- **Windows 10 End of Life**: October 14, 2025 (extended support available)
- **Python**: 3.9+ required (current project uses Python 3.10+)
- **PySide6**: Version 6.5.3 to 6.7.x recommended for stability

#### Windows Version-Specific PySide6 Installation
The project includes automatic Windows version detection for optimal PySide6 compatibility:

| Windows Version | PySide6 Version | Python Version | Installation Command |
|----------------|----------------|----------------|----------------------|
| Windows 7/8/8.1 | 6.1.0 - 6.1.3 | 3.6 - 3.8 | `uv add "pyside6>=6.1.0,<6.2.0"` |
| Windows 10 < 1809 | 6.1.0 - 6.1.3 | 3.6 - 3.8 | `uv add "pyside6>=6.1.0,<6.2.0"` |
| Windows 10 ≥ 1809 | 6.2.0 - 6.7.x | 3.9 - 3.13 | `uv add "pyside6>=6.2.0,<6.8.0"` |
| Windows 11 | 6.5.0 - 6.7.x | 3.9 - 3.13 | `uv add "pyside6>=6.5.0,<6.8.0"` |

Use the platform detection utility: `python src/utils/platform_detection.py`

### IDE and Editor Setup

#### Visual Studio Code (Recommended)
1. **Install Python Extension**: Includes Pylance language server automatically
2. **Workspace Settings** (`.vscode/settings.json`):
   ```json
   {
     "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.linting.ruffEnabled": true,
     "python.formatting.provider": "black",
     "python.sortImports.args": ["--profile", "black"],
     "python.analysis.typeCheckingMode": "basic",
     "python.analysis.autoImportCompletions": true,
     "files.trimTrailingWhitespace": true,
     "editor.formatOnSave": true
   }
   ```
3. **Recommended Extensions**:
   - Python (ms-python.python) - Includes Pylance
   - Black Formatter (ms-python.black-formatter)
   - isort (ms-python.isort)
   - Ruff (charliermarsh.ruff)

#### PyCharm/IntelliJ IDEA
1. **Configure Python Interpreter**: Point to `.venv/Scripts/python.exe`
2. **Enable Code Inspections**: File → Settings → Editor → Inspections → Python
3. **Configure External Tools**: Add Black, isort, pylint, and ruff as external tools
4. **Real-time Analysis**: Enable "Highlight errors and warnings" in editor settings

#### Command Line and CI/CD Setup
```bash
# Pre-commit hook setup (optional)
pip install pre-commit
pre-commit install

# Create .pre-commit-config.yaml for automated quality checks
# Run quality checks in CI pipeline
uv run ruff check src/ --output-format=github  # GitHub Actions format
uv run pylint src/ --output-format=json        # Machine-readable output
```

### Testing Strategy
- Tests should be in a `tests/` directory (currently not implemented)
- Use pytest with async support (`pytest-asyncio`)
- Mock hardware services for unit testing
- Use the existing mock implementations in development configs
- Test configuration is already set up in `pyproject.toml` with coverage reporting

### Adding New Hardware
1. Define interface in `src/application/interfaces/hardware/`
2. Implement in `src/infrastructure/implementation/hardware/[hardware_type]/`
3. Create both real hardware and mock implementations
4. Add to `HardwareFactory` in `src/infrastructure/factories/hardware_factory.py`
5. Update `SimpleReloadableContainer` dependency injection configuration

### Adding New Use Cases
1. Create new directory in `src/application/use_cases/`
2. Implement use case following existing patterns
3. Register in `SimpleReloadableContainer`
4. Add CLI/GUI integration points

## Troubleshooting

### PySide6 Installation Issues
If you encounter PySide6 import errors:

1. **Use UV Auto-Installation** (Recommended):
   ```bash
   # UV automatically installs compatible PySide6
   uv run src/main_gui.py

   # Check compatibility if needed
   python src/utils/platform_detection.py
   ```

2. **Environment Reset**:
   ```bash
   uv cache clean
   rm -rf .venv  # or delete .venv folder
   uv sync
   ```

3. **Manual Version-specific Installation**:
   ```bash
   # For Windows 11 / Windows 10 (1809+)
   uv add "pyside6>=6.5.0,<6.8.0"

   # For older Windows 10 versions
   uv add "pyside6>=6.2.0,<6.8.0"

   # For Windows 7/8 (legacy)
   uv add "pyside6>=6.1.0,<6.2.0"
   ```

4. **Quick Solutions**:
   ```bash
   # Most issues can be resolved with:
   uv cache clean && uv sync         # Clean reinstall
   uv run src/main_gui.py            # Auto-detects and installs compatible PySide6

   # GUI-only execution (no console window)
   ./run_gui_silent.vbs              # Completely silent (recommended)
   ./run_gui.bat                     # Minimal console visibility

   # For legacy Windows systems (manual)
   uv add "pyside6>=6.1.0,<6.2.0"   # Windows 7/8/10 < 1809

   # Advanced diagnosis
   python src/utils/platform_detection.py
   ```

### Creating Standalone Executable (Optional)

For distribution without requiring Python/UV installation:

```bash
# Install PyInstaller (already included in dependencies)
uv sync

# Create standalone GUI executable (Windows)
uv run pyinstaller --windowed --onefile --name "WF_EOL_Tester" src/main_gui.py

# Create with custom icon (if available)
uv run pyinstaller --windowed --onefile --name "WF_EOL_Tester" --icon="src/ui/gui/resources/icons/app.ico" src/main_gui.py

# Output location: dist/WF_EOL_Tester.exe
```

**PyInstaller Options Explained:**
- `--windowed`: No console window (GUI only)
- `--onefile`: Single executable file
- `--name`: Custom executable name
- `--icon`: Custom application icon

### Migration Planning
- **Windows 10 EOL (Oct 2025)**: Plan migration to Windows 11 or consider extended support
- **Python Version**: Stay within Python 3.9-3.13 range for PySide6 compatibility
- **Alternative GUI**: Consider Tkinter for maximum compatibility if PySide6 issues persist

## Key Files to Understand

- `src/main_cli.py` - CLI entry point with dependency injection setup
- `src/application/containers/simple_reloadable_container.py` - Hot-reloadable dependency injection configuration
- `src/application/services/hardware_facade/hardware_service_facade.py` - Hardware abstraction layer
- `pyproject.toml` - Project configuration, dependencies, and tool settings
- `CLI_USAGE.md` - Detailed CLI usage instructions