# Silo Advanced Features Documentation

This document describes the advanced features available in Silo 2.0.

## Table of Contents

1. [CLI Tool](#cli-tool)
2. [Theme Customization](#theme-customization)
3. [Plugin System](#plugin-system)
4. [Unit Testing](#unit-testing)
5. [Modular Architecture](#modular-architecture)

---

## CLI Tool

Silo now includes a powerful command-line interface for batch operations and automation.

### Installation

The CLI tool is included in the main Silo package:

```bash
python silo-cli.py --help
```

### Basic Usage

#### Load and List Files

```bash
# Load all audiobooks from a directory
python silo-cli.py load -d ./audiobooks list

# Output example:
Loaded 15 files:
📖 The Great Gatsby
   Author: F. Scott Fitzgerald
   Duration: 4:30
   File: great_gatsby.m4b
```

#### Export Metadata

```bash
# Export metadata for all files to JSON
python silo-cli.py load -d ./audiobooks export -o metadata.json

# The JSON file will contain:
{
  "book1.m4b": {
    "metadata": {
      "title": "Book Title",
      "author": "Author Name",
      "narrator": "Narrator Name",
      ...
    },
    "duration": "4:30",
    "has_cover_art": true,
    "chapter_count": 15
  }
}
```

#### Import Metadata

```bash
# Preview changes (dry run)
python silo-cli.py load -d ./audiobooks import -i metadata.json --dry-run

# Actually apply changes
python silo-cli.py load -d ./audiobooks import -i metadata.json
```

#### Batch Update

```bash
# Update author for all files (dry run first)
python silo-cli.py load -d ./audiobooks update --author "New Author" --dry-run

# Apply the changes
python silo-cli.py load -d ./audiobooks update --author "New Author"

# Update multiple fields
python silo-cli.py load -d ./audiobooks update \
  --title "New Title" \
  --author "New Author" \
  --genre "Fiction" \
  --year "2024"
```

### CLI Automation Examples

#### Backup Script

```bash
#!/bin/bash
# Backup metadata for all audiobooks

python silo-cli.py load -d ./audiobooks export -o "backup_$(date +%Y%m%d).json"
```

#### Batch Genre Assignment

```bash
# Assign genre based on directory structure
for genre in Fiction Non-Fiction; do
  python silo-cli.py load -d "./audiobooks/$genre" update --genre "$genre"
done
```

---

## Theme Customization

Silo now supports multiple built-in themes and custom color schemes.

### Built-in Themes

- **dark** (default) - Classic dark theme with blue accents
- **darker** - Extra dark for low-light environments
- **ocean** - Calming blue/cyan theme
- **forest** - Natural green theme
- **light** - Clean light theme for daytime use

### Switching Themes

Themes can be changed via the settings file:

```json
{
  "theme": "ocean"
}
```

Location: `~/.silo/config.json`

### Custom Theme Creation

Create a custom theme by saving a JSON file:

```json
{
  "bg": "#1a1a2e",
  "fg": "#e0e0e0",
  "bg_secondary": "#16213e",
  "bg_tertiary": "#0f3460",
  "accent": "#e94560",
  "accent_hover": "#ff6b6b",
  "success": "#4cc9f0",
  "border": "#533483",
  "select_bg": "#4cc9f0",
  "select_fg": "#ffffff",
  "button_secondary": "#533483"
}
```

Save as: `~/.silo/themes/my_custom_theme.json`

### Theme File Structure

```
~/.silo/
├── config.json           # Main settings
├── themes/               # Custom themes directory
│   ├── cyberpunk.json
│   ├── nature.json
│   └── minimal.json
└── window_state.json     # Window position memory
```

---

## Plugin System

Silo now supports plugins for extending functionality.

### Plugin Architecture

Plugins can:
- Add custom menu items
- Process metadata automatically
- Create export formats
- Integrate with external services
- Add validation rules

### Creating a Plugin

Create a new Python file in `~/.silo/plugins/`:

```python
"""My custom plugin."""

from utils.plugin_system import SiloPlugin, PluginAPI
import logging

logger = logging.getLogger(__name__)


class MyCustomPlugin(SiloPlugin):
    """My custom plugin description."""

    @property
    def name(self) -> str:
        return "My Custom Plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "What this plugin does"

    def initialize(self, app) -> bool:
        """Initialize the plugin."""
        self.api = PluginAPI(app)

        # Register menu items
        self.api.register_menu_item(
            "Plugins",
            "My Custom Action",
            self.my_custom_function
        )

        logger.info(f"{self.name} initialized")
        return True

    def shutdown(self) -> None:
        """Cleanup."""
        logger.info(f"{self.name} shut down")

    def my_custom_function(self):
        """Custom plugin functionality."""
        files = self.api.get_files()

        for file_path in files:
            metadata = self.api.get_metadata(file_path)
            # Process metadata
            logger.info(f"Processing {file_path}")


# Required: Plugin factory function
def create_plugin():
    """Create plugin instance."""
    return MyCustomPlugin()
```

Save as: `~/.silo/plugins/my_custom_plugin.py`

### Plugin API

Plugins have access to the `PluginAPI` class:

```python
self.api.get_metadata(file_path)     # Get file metadata
self.api.set_metadata(file_path, metadata)  # Set file metadata
self.api.get_files()                  # Get all loaded files
self.api.register_menu_item(...)     # Add menu items
```

### Plugin Hooks

Plugins can register hooks for specific events:

```python
# Register a hook
app.plugin_manager.register_hook('before_save', self.before_save_handler)

# Hook handler
def before_save_handler(self, file_path, metadata):
    # Process metadata before saving
    metadata['processed_by'] = self.name
```

### Example: Filename Cleaner Plugin

Included in `plugins/examples/filename_cleaner_plugin.py` - automatically cleans filenames based on metadata.

---

## Unit Testing

Silo now includes comprehensive unit tests using pytest.

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_validators.py

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=core --cov=utils tests/
```

### Test Structure

```
tests/
├── test_validators.py          # Input validation tests
├── test_metadata_handler.py    # Metadata operations tests
└── test_chapter_handler.py     # Chapter handling tests
```

### Writing Tests

```python
import pytest
from utils.validators import validate_year

def test_valid_year():
    result = validate_year("2024")
    assert result.is_valid is True

def test_invalid_year():
    result = validate_year("999")
    assert result.is_valid is False
    assert "between 1000 and 9999" in result.error_message
```

### Continuous Integration

Tests can be integrated with CI/CD pipelines:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.14'
      - name: Install dependencies
        run: |
          pip install pytest mutagen Pillow
      - name: Run tests
        run: pytest tests/ -v
```

---

## Modular Architecture

Silo has been refactored into a clean, modular package structure.

### Directory Structure

```
silo/
├── silo.py                     # Original monolithic version
├── silo_new.py                  # New modular entry point
├── silo-cli.py                  # CLI tool
│
├── config/                      # Configuration
│   ├── constants.py            # Colors, genres, validation rules
│   └── settings.py             # User settings management
│
├── core/                        # Core business logic
│   ├── metadata_handler.py     # Audio metadata CRUD
│   ├── chapter_handler.py      # Chapter embedding (THE CRITICAL FIX)
│   ├── cover_handler.py        # Cover art processing
│   ├── undo_manager.py         # Undo/redo system
│   └── autosave.py             # Auto-save functionality
│
├── ui/                         # User interface
│   ├── main_window.py          # Main application window
│   └── widgets.py              # Reusable UI components
│
├── utils/                      # Utilities
│   ├── validators.py           # Input validation
│   ├── progress.py             # Progress dialogs
│   ├── logging_setup.py        # Logging configuration
│   ├── theme_manager.py        # Theme system
│   └── plugin_system.py        # Plugin architecture
│
└── tests/                      # Unit tests
    ├── test_validators.py
    ├── test_metadata_handler.py
    └── test_chapter_handler.py
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `config/` | Application constants and settings |
| `core/metadata_handler.py` | Read/write metadata from audio files |
| `core/chapter_handler.py` | Chapter embedding and auto-generation |
| `core/cover_handler.py` | Cover art extraction and processing |
| `core/undo_manager.py` | Undo/redo command pattern |
| `core/autosave.py` | Background auto-save threading |
| `ui/main_window.py` | Main application orchestration |
| `ui/widgets.py` | Reusable UI components |
| `utils/validators.py` | Input validation functions |
| `utils/progress.py` | Progress dialog implementation |
| `utils/theme_manager.py` | Theme management |
| `utils/plugin_system.py` | Plugin architecture |

### Benefits of Modular Architecture

1. **Testability** - Each module can be tested independently
2. **Maintainability** - Easier to locate and fix bugs
3. **Reusability** - Core functions work without UI
4. **Extensibility** - Plugin system for custom features
5. **Professional Structure** - Industry best practices

### Using the Modules

#### As a Library

```python
from core.metadata_handler import read_metadata, apply_metadata
from core.chapter_handler import embed_chapters

# Read metadata
metadata = read_metadata("audiobook.m4b")

# Modify metadata
metadata['author'] = "New Author"

# Save changes
apply_metadata("audiobook.m4b", metadata, None)
```

#### As an Application

```python
from ui.main_window import AudiobookMetadataEditor
from config.settings import Settings
import tkinter as tk

# Create application
root = tk.Tk()
settings = Settings.load()
app = AudiobookMetadataEditor(root, settings)
root.mainloop()
```

---

## Configuration Files

Silo uses the `~/.silo/` directory for user data:

```
~/.silo/
├── config.json           # User settings and theme selection
├── themes/               # Custom theme files
├── plugins/              # User plugins
├── window_state.json     # Window position and size
└── logs/                 # Application logs
    └── silo_YYYYMMDD.log # Daily log files
```

---

## Keyboard Shortcuts

### File Operations
- `Ctrl+O` - Load Files
- `Ctrl+D` - Load Directory
- `Ctrl+S` - Save Changes
- `Ctrl+R` - Refresh Metadata

### Edit Operations
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+A` - Select All Files

### Navigation
- `Ctrl+F` - Search/Filter
- `Delete` - Remove Selected
- `Escape` - Clear Selection

---

## Performance Tips

1. **Large Libraries** - Use search/filter instead of scrolling
2. **Batch Operations** - Use CLI tool for automation
3. **Auto-Save** - Adjust interval based on your workflow
4. **Themes** - Use simpler themes for better performance

---

## Troubleshooting

### CLI Tool Not Working

```bash
# Ensure Python path is correct
python --version

# Check dependencies
pip install mutagen Pillow

# Run with verbose output
python silo-cli.py load -d ./audiobooks list --verbose
```

### Custom Theme Not Loading

```bash
# Validate JSON format
python -m json.tool ~/.silo/themes/my_theme.json

# Check file permissions
ls -la ~/.silo/themes/
```

### Plugin Not Loading

```bash
# Check for syntax errors
python -m py_compile ~/.silo/plugins/my_plugin.py

# Check plugin API version
# Ensure plugin matches current API
```

---

## Future Enhancements

Planned for future versions:

- [ ] Drag-and-drop file support
- [ ] Audio playback preview
- [ ] Chapter preview playback
- [ ] Batch cover art download from URLs
- [ ] Metadata templates
- [ ] Cloud backup integration
- [ ] Multi-language support
- [ ] Performance optimizations for large libraries

---

## Support

For issues, questions, or feature requests:
- GitHub: https://github.com/pyrodiaz-droid/silo
- Documentation: See MODULAR_ARCHITECTURE.md

---

**Version:** 2.0 (Modular Architecture)  
**Last Updated:** 2025-01-14
