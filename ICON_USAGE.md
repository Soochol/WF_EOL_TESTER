# Icon System Usage Guide

## Overview

The GUI application now includes a comprehensive icon management system that supports:
- File-based icons (PNG, SVG, ICO formats)
- Theme support (light/dark themes)
- Automatic emoji fallbacks
- Qt resource system integration
- Centralized icon management

## Quick Start

### Basic Usage

```python
from src.ui.gui.utils.icon_manager import get_icon, get_emoji, IconSize

# Get an icon for use in buttons, labels, etc.
icon = get_icon("dashboard", IconSize.MEDIUM)

# Use in a QPushButton
button = QPushButton("Dashboard")
if not icon.isNull():
    button.setIcon(icon)
else:
    # Fallback to emoji
    button.setText(f"{get_emoji('dashboard')} Dashboard")
```

### Available Icon Names

#### Navigation Icons
- `dashboard` - Dashboard/home (🏠)
- `test_control` - Test control panel (⚡)
- `results` - Results/reports (📊)
- `hardware` - Hardware configuration (⚙️)
- `settings` - Settings/configuration (🔧)
- `logs` - Logs/console (📋)

#### Status Icons
- `status_ready` - Ready/idle status (🔘)
- `status_running` - Running/active status (🟢)
- `status_success` - Success/pass status (✅)
- `status_warning` - Warning status (⚠️)
- `status_error` - Error/fail status (❌)
- `status_info` - Information status (ℹ️)
- `status_loading` - Loading/processing status (🔄)

#### Action Icons
- `play` - Start/play action (▶️)
- `pause` - Pause action (⏸️)
- `stop` - Stop action (⏹️)
- `refresh` - Refresh/reload action (🔄)
- `save` - Save action (💾)
- `export` - Export data action (📤)
- `import` - Import data action (📥)

#### Hardware Icons
- `robot` - Robot arm (🤖)
- `loadcell` - Load cell/force sensor (⚖️)
- `power` - Power supply (🔌)
- `mcu` - Microcontroller unit (🎛️)
- `connection` - Connected status (🔗)
- `disconnect` - Disconnected status (❌)

## Icon Sizes

```python
from src.ui.gui.utils.icon_manager import IconSize

IconSize.SMALL   # 16x16 pixels
IconSize.MEDIUM  # 24x24 pixels
IconSize.LARGE   # 32x32 pixels
IconSize.XLARGE  # 48x48 pixels
```

## Adding Custom Icons

### 1. Add Icon Files

Place icon files in the appropriate directory:

```
src/ui/gui/resources/icons/
├── dashboard.png          # General icon
├── light/
│   └── dashboard.png      # Light theme variant
└── dark/
    └── dashboard.png      # Dark theme variant
```

### 2. Update Resource File (Optional)

If using Qt resources, add to `resources.qrc`:

```xml
<file>icons/my_new_icon.png</file>
```

### 3. Rebuild Resources

```bash
cd src/ui/gui/resources
python build_resources.py
```

### 4. Use in Code

```python
icon = get_icon("my_new_icon", IconSize.MEDIUM)
```

## Theme Support

```python
from src.ui.gui.utils.icon_manager import get_icon_manager, IconTheme

manager = get_icon_manager()

# Change theme
manager.set_theme(IconTheme.DARK)

# Icons will now prefer dark theme variants
icon = get_icon("dashboard")
```

## Advanced Usage

### Direct Manager Access

```python
from src.ui.gui.utils.icon_manager import get_icon_manager

manager = get_icon_manager()

# Check if icon exists
if manager.has_icon("dashboard"):
    icon = manager.get_icon("dashboard")

# Get available icons
available = manager.get_available_icons()
print(f"Available icons: {', '.join(available)}")

# Clear cache
manager.clear_cache()
```

### Status Icon Updates

For dynamic status displays:

```python
def update_status_display(self, status_name: str, message: str):
    # Update icon
    self._update_status_icon(status_name)

    # Update text
    self.status_label.setText(message)

def _update_status_icon(self, icon_name: str):
    icon = get_icon(icon_name, IconSize.SMALL)

    if not icon.isNull():
        pixmap = icon.pixmap(16, 16)
        self.status_icon.setPixmap(pixmap)
        self.status_icon.setText("")
    else:
        emoji = get_emoji(icon_name)
        if emoji:
            self.status_icon.setText(emoji)
            self.status_icon.setPixmap(None)
```

## Current Implementation Status

### ✅ Completed
- Icon manager utility with theme support
- Qt resource system (.qrc) configuration
- Navigation menu icon integration
- Test control widget icon integration
- Status icon handling with fallbacks
- Comprehensive documentation

### 📋 Todo (for actual icon files)
- Add actual PNG/SVG icon files to replace emoji fallbacks
- Create light/dark theme variants
- Generate Qt resource file using `pyside6-rcc`

## Troubleshooting

### Icons Not Showing
1. Check if icon files exist in `src/ui/gui/resources/icons/`
2. Verify icon names match exactly (case-sensitive)
3. Check if Qt resources are built (`resources_rc.py` exists)
4. Fallback emojis should appear if icons are missing

### Performance Issues
1. Clear icon cache: `get_icon_manager().clear_cache()`
2. Check file sizes - optimize large icon files
3. Consider using SVG for scalable icons

### Theme Issues
1. Ensure theme-specific icons exist in `light/` and `dark/` subdirectories
2. Use `manager.set_theme()` to change themes
3. Clear cache after theme changes