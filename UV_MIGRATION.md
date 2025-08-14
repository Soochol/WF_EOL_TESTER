# UV Migration Guide

This project has been migrated from pip to uv for faster and more reliable Python package management.

## What Changed

### Dependencies
- **Before**: `requirements.txt` and `pip`
- **After**: `pyproject.toml` and `uv`

### Virtual Environment
- **Before**: `venv/` directory managed by pip
- **After**: `.venv/` directory managed by uv

### Installation Commands
- **Before**: `pip install -r requirements.txt`
- **After**: `uv sync --dev`

## New Workflow

### Setup (First Time)
```bash
# Install uv (if not already installed)
pip install uv

# Sync all dependencies (creates .venv automatically)
uv sync --dev
```

### Running the Application
```bash
# Option 1: Use the updated scripts
./run.bat          # Windows batch
./run.ps1          # PowerShell

# Option 2: Direct uv command
uv run python main.py
```

### Development Commands
```bash
# Add a new dependency
uv add package-name

# Add a development dependency  
uv add --dev package-name

# Update dependencies
uv sync --upgrade

# Run tests
uv run pytest

# Run linting
uv run black src/
uv run mypy src/
```

## Benefits of uv

1. **Speed**: 10-100x faster than pip
2. **Reliability**: Better dependency resolution
3. **Reproducibility**: Lock file ensures consistent builds
4. **Simplicity**: Single tool for all Python package needs

## Migration Notes

- Old `venv/` directories can be safely deleted
- `uv.lock` file should be committed to git for reproducible builds
- All dependencies are now in `pyproject.toml`
- Build scripts have been updated to use `uv run`

## Troubleshooting

If you encounter issues:

1. **Clean install**: Remove `.venv/` and run `uv sync --dev`
2. **Update uv**: `pip install --upgrade uv`
3. **Check pyproject.toml**: Ensure all dependencies are listed

For more information, visit: https://docs.astral.sh/uv/