# Silo - Modular Architecture

This document describes the modular architecture of Silo audiobook metadata editor.

## Directory Structure

```
silo/
├── silo.py                    # Original monolithic version (2372 lines)
├── silo_new.py               # New modular entry point
│
├── config/                    # Configuration management
│   ├── __init__.py
│   ├── constants.py          # Color schemes, genres, validation constants
│   └── settings.py           # Settings management (save/load from ~/.silo/config.json)
│
├── core/                     # Core business logic
│   ├── __init__.py
│   ├── metadata_handler.py   # Audio metadata CRUD operations
│   ├── chapter_handler.py    # Chapter embedding (CRITICAL FIX - actually writes chapters)
│   ├── cover_handler.py      # Cover art processing
│   ├── undo_manager.py       # Undo/redo system
│   └── autosave.py           # Auto-save functionality
│
├── ui/                       # User interface components
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   └── widgets.py            # Reusable UI components (Tooltip, etc.)
│
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── validators.py         # Input validation (year, URL, image size)
│   ├── progress.py           # Progress dialog for long operations
│   └── logging_setup.py      # Logging configuration
│
└── tests/                    # (To be added in Phase 6)
    ├── test_metadata_handler.py
    ├── test_chapter_handler.py
    └── test_validators.py
```

## Module Responsibilities

### Config Module
- **constants.py**: Application-wide constants (colors, genres, validation limits)
- **settings.py**: User settings persistence (JSON-based configuration)

### Core Module
- **metadata_handler.py**: Read/write metadata from/to audio files (MP3, M4B, M4A, FLAC)
- **chapter_handler.py**: Chapter embedding and auto-generation (THE CRITICAL BUG FIX)
- **cover_handler.py**: Cover art extraction, loading, and validation
- **undo_manager.py**: Command pattern for undo/redo functionality
- **autosave.py**: Background auto-save with configurable intervals

### UI Module
- **main_window.py**: Main application window and UI orchestration
- **widgets.py**: Reusable UI components (tooltips, progress dialogs, etc.)

### Utils Module
- **validators.py**: Input validation functions
- **progress.py**: Progress dialog implementation
- **logging_setup.py**: Logging configuration (writes to ~/.silo/logs/)

## Key Improvements from Modularization

1. **Separation of Concerns**: Business logic separated from UI
2. **Testability**: Each module can be tested independently
3. **Maintainability**: Easier to locate and fix bugs
4. **Reusability**: Core functions can be used without UI (CLI version possible)
5. **Extensibility**: New features can be added without modifying existing code

## Usage

### Running the Original Version
```bash
python silo.py
```

### Running the Modular Version
```bash
python silo_new.py
```

## Configuration Files

The application uses `~/.silo/` for user data:
- `config.json` - User settings
- `window_state.json` - Window position and size
- `logs/silo_YYYYMMDD.log` - Application logs

## Critical Bug Fix

The **chapter_handler.py** module contains the critical fix for chapter embedding:
- **Before**: Chapters were only saved in memory, never written to files
- **After**: Chapters are actually embedded into M4B/M4A files using mutagen's MP4 chapter support

This was the highest priority bug fix and is now properly isolated in its own module.

## Dependencies

All modules use the same dependencies as the original:
- `tkinter` - GUI framework
- `mutagen` - Audio metadata handling
- `Pillow` - Image processing
- Standard library: `json`, `logging`, `pathlib`, `threading`, etc.

## Migration Notes

The modular version maintains 100% compatibility with the original:
- Same user interface
- Same features
- Same keyboard shortcuts
- Same configuration files
- Same file format support

Users can switch between `silo.py` and `silo_new.py` without any loss of functionality.
