#!/usr/bin/env python3
"""
Silo - Audiobook Metadata Editor
Main entry point for the modular version
"""

import sys
import tkinter as tk
import logging

# Setup logging first
from utils.logging_setup import setup_logging
logger = setup_logging()

# Import application components
from config.settings import Settings
from ui.main_window import AudiobookMetadataEditor


def main():
    """Main application entry point."""
    logger.info("Silo starting")

    try:
        # Load settings
        settings = Settings.load()

        # Create main window
        root = tk.Tk()
        app = AudiobookMetadataEditor(root, settings)

        logger.info("Application started successfully")
        root.mainloop()

        logger.info("Application closed")

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
