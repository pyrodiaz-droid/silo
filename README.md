# Silo - Audiobook Metadata Editor

A powerful, professional audiobook metadata editor with support for MP3, M4B, M4A, and FLAC formats.

![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-success.svg)

## ✨ Features

### Core Functionality
- 📖 **Edit Metadata**: Title, author, narrator, series, publisher, year, genre, description
- 🎨 **Cover Art Management**: Load, remove, and save cover art from files or URLs
- 📑 **Chapter Support**: Create, edit, and embed chapters in M4B/M4A files
- 🔄 **Batch Processing**: Apply metadata changes to multiple files at once
- 🔁 **Undo/Redo**: Full undo/redo support for all operations (Ctrl+Z/Ctrl+Y)

### Advanced Features
- 💾 **Auto-Save**: Automatic saving every 5 minutes (configurable)
- 📤 **Export/Import**: Backup and restore metadata via JSON
- 🔍 **Search/Filter**: Real-time filtering of large audiobook libraries
- ⌨️ **Keyboard Shortcuts**: Comprehensive shortcut support
- 🎭 **Theme System**: 5 built-in themes + custom themes
- 🔌 **Plugin System**: Extensible architecture for custom functionality
- 🖥️ **CLI Tool**: Command-line interface for batch operations and automation
- 📋 **Metadata Templates**: Save and reuse common metadata patterns
- 🖱️ **Drag-and-Drop**: Drop files or folders directly into the application
- ⚡ **Performance Optimized**: Handles large libraries (1000+ files) efficiently

### User Experience
- ✅ **Professional UI**: Dark theme with clean, intuitive interface
- 💡 **Tooltips**: Helpful tooltips throughout the application
- 📊 **Progress Indicators**: Visual feedback for long operations
- 🪟 **Status Bar**: Real-time status updates
- 📝 **Input Validation**: Smart validation for all user inputs
- 🪟 **Window Memory**: Remembers window position and size

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python silo.py
```

### Alternative Launch Methods

```bash
# New modular version
python silo_new.py

# CLI tool
python silo-cli.py --help
```

## 🆕 What's New in Version 2.1

### Future Enhancements Implemented

**Metadata Templates** (v2.1)
- Save current metadata as reusable templates
- Apply templates to new audiobooks instantly
- Manage templates (rename, delete, view details)
- Perfect for series with common metadata

**Drag-and-Drop Support** (v2.1)
- Drop individual files or entire folders
- Automatic format detection
- Progress indicator for large drops
- Error handling for unsupported formats

**Performance Optimizations** (v2.1)
- Cached sorting for instant file list updates
- Batch insert operations for large libraries
- Progress dialogs for directories with 20+ files
- Handles 1000+ audiobooks smoothly

## 📖 Usage Guide

### Basic Workflow

1. **Load Files**: Click "Load Files" or "Load Directory"
2. **Select File**: Click on a file in the list to view/edit
3. **Edit Metadata**: Make changes in the "Book Info" tab
4. **Manage Cover Art**: Use the "Cover Art" tab
5. **Create Chapters**: Use the "Chapters" tab for M4B/M4A files
6. **Save Changes**: Click "Save Changes" or press Ctrl+S

### Keyboard Shortcuts

| Operation | Shortcut | Description |
|-----------|----------|-------------|
| Load Files | `Ctrl+O` | Open file dialog |
| Load Directory | `Ctrl+D` | Open directory dialog |
| Save Changes | `Ctrl+S` | Save current file |
| Refresh | `Ctrl+R` | Reload metadata from file |
| Undo | `Ctrl+Z` | Undo last operation |
| Redo | `Ctrl+Y` | Redo undone operation |
| Select All | `Ctrl+A` | Select all files |
| Search | `Ctrl+F` | Focus search box |
| Remove | `Delete` | Remove selected files |
| Clear | `Escape` | Clear selection |

## 🛠️ Advanced Usage

### CLI Tool for Batch Operations

```bash
# Export metadata from all audiobooks
python silo-cli.py load -d ./audiobooks export -o backup.json

# Batch update author
python silo-cli.py load -d ./audiobooks update --author "New Author"

# Import metadata
python silo-cli.py load -d ./audiobooks import -i backup.json
```

### Custom Themes

Create `~/.silo/themes/my_theme.json`:
```json
{
  "bg": "#1a1a2e",
  "fg": "#e0e0e0",
  "accent": "#e94560"
}
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest --cov=core --cov=utils tests/
```

## 📦 Project Structure

```
silo/
├── silo.py                     # Original version (2372 lines)
├── silo_new.py                  # Modular entry point (50 lines)
├── silo-cli.py                  # CLI tool
├── requirements.txt             # Dependencies
│
├── config/                      # Configuration
├── core/                        # Core business logic
├── ui/                         # User interface
├── utils/                      # Utilities
└── tests/                      # Unit tests
```

## 📚 Documentation

- **[MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md)** - Complete architecture documentation
- **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** - CLI, themes, plugins, and testing guide

## 🔧 Configuration

Settings location: `~/.silo/config.json`

## 📝 License

MIT License

## 👨‍💻 Author

Created with ❤️ using Claude Code

## 📧 Support

GitHub: https://github.com/pyrodiaz-droid/silo
