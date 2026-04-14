"""Application constants for Silo audiobook metadata editor."""

# Dark color scheme
COLORS = {
    'bg': '#2b2b2b',           # Main background
    'fg': '#e0e0e0',           # Main foreground/text
    'bg_secondary': '#3c3c3c', # Secondary background (frames, panels)
    'bg_tertiary': '#4a4a4a',  # Tertiary background (entries, listboxes)
    'accent': '#2196F3',       # Accent color (buttons, highlights) - lighter blue
    'accent_hover': '#42A5F5', # Hover state
    'success': '#1976D2',      # Success color - medium blue
    'border': '#555555',       # Border color
    'select_bg': '#1976D2',    # Selection background
    'select_fg': '#ffffff',    # Selection foreground
    'button_secondary': '#0D47A1'  # Dark blue for secondary buttons
}

# Genre options
GENRES = ["Fiction", "Non-Fiction", "Mystery", "Sci-Fi", "Fantasy",
          "Romance", "Biography", "History", "Self-Help", "Other"]

# File extensions supported
SUPPORTED_EXTENSIONS = ['.m4b', '.m4a', '.mp3', '.flac']

# Validation constants
MIN_YEAR = 1000
MAX_YEAR = 9999
MAX_IMAGE_SIZE = 10_000_000  # 10MB

# Auto-save defaults
DEFAULT_AUTO_SAVE_INTERVAL = 300  # 5 minutes in seconds

# Undo/Redo defaults
DEFAULT_UNDO_HISTORY = 50
