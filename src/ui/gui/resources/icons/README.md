# Icons Directory

This directory contains icon resources for the GUI application.

## Directory Structure

```
icons/
├── README.md           # This file
├── light/             # Light theme icons
├── dark/              # Dark theme icons
└── *.png/svg/ico      # General icons (theme-neutral)
```

## Icon Categories

### Navigation Icons
- `dashboard.png` - Dashboard/home icon
- `test_control.png` - Test control panel icon
- `results.png` - Results/reports icon
- `hardware.png` - Hardware configuration icon
- `settings.png` - Settings/configuration icon
- `logs.png` - Logs/console icon

### Status Icons
- `status_ready.png` - Ready/idle status
- `status_running.png` - Running/active status
- `status_success.png` - Success/pass status
- `status_warning.png` - Warning status
- `status_error.png` - Error/fail status
- `status_info.png` - Information status
- `status_loading.png` - Loading/processing status

### Action Icons
- `play.png` - Start/play action
- `pause.png` - Pause action
- `stop.png` - Stop action
- `refresh.png` - Refresh/reload action
- `save.png` - Save action
- `export.png` - Export data action
- `import.png` - Import data action

### Hardware Icons
- `robot.png` - Robot arm icon
- `loadcell.png` - Load cell/force sensor icon
- `power.png` - Power supply icon
- `mcu.png` - Microcontroller unit icon
- `connection.png` - Connected status icon
- `disconnect.png` - Disconnected status icon

## Icon Specifications

### Recommended Formats
- **PNG**: For bitmap icons with transparency
- **SVG**: For vector icons (scalable, preferred)
- **ICO**: For Windows-style icons

### Standard Sizes
- **16x16**: Small icons (toolbar, status)
- **24x24**: Medium icons (navigation, buttons)
- **32x32**: Large icons (primary actions)
- **48x48**: Extra large icons (dialogs, headers)

### Design Guidelines
- Use consistent visual style across all icons
- Ensure good contrast in both light and dark themes
- Keep designs simple and recognizable at small sizes
- Use appropriate padding (2-4px) within the icon bounds

## Usage

Icons are managed through the `IconManager` class in `ui/gui/utils/icon_manager.py`.

```python
from ui.gui.utils.icon_manager import get_icon, IconSize

# Get an icon
icon = get_icon("dashboard", IconSize.MEDIUM)

# Use in a button
button.setIcon(icon)
```

## Adding New Icons

1. Create icon files in appropriate sizes
2. Place in theme-specific folders (`light/`, `dark/`) or root for theme-neutral icons
3. Use consistent naming convention (lowercase, underscores)
4. Update the `emoji_fallbacks` dict in `icon_manager.py` if needed
5. Test with both light and dark themes

## Current Status

Currently using emoji fallbacks while actual icon files are being created.
The system will automatically fall back to emoji if icon files are not found.